from reaper_python import *
import sys
import base64

sys.argv=["Main"]
import Tkinter

LH_POS = 108        # Position note for Pro G/B
MAXLEN = 1048567

# Range for left-hand animations
LH_START = 40
LH_END   = 59

MIDI_ON = 0x90
MIDI_OFF = 0x80

TICKS = 480

LH_TO_FRET = {
        1: 40,
        2: 43,
        3: 45,
        4: 47,
        5: 49,
        6: 50,
        7: 52,
        8: 53,
        9: 55,
        10: 56,
        11: 57,
        12: 58
}

class MIDINote:

    def __init__(self, rpos, apos, status, note, velocity):
        self.rpos = rpos
        self.apos = apos
        self.status = status
        self.note = note
        self.velocity = velocity

    def __repr__(self):
        return "E %d %x %x %x" % (self.rpos, self.status, self.note, self.velocity)

class MIDIEvent:

    def __init__(self, rpos, apos, status, encText):
        self.rpos = rpos
        self.apos = apos
        self.status = status
        self.encText = encText
        self.text = base64.b64decode(str(encText))[2:]

    def __repr__(self):
        s = "<X %d %x\n%s\n>" % (self.rpos, self.status, self.encText)
        return s

        
class MIDITrackData:

    def __init__(self, chunk, midi_start, midi_end, notes):
        self.chunk = chunk
        self.midi_start = midi_start
        self.midi_end = midi_end
        self.notes = notes

    def __repr__(self):
        tok = self.chunk.split('\n')
        text = '\n'.join(tok[0:self.midi_start]) + '\n'

        for note in self.notes:
            text = text + str(note) + '\n'

        text = text + '\n'.join(tok[self.midi_end:])
        return text

def get_item(title):
    item_names = {}
    for i in range(RPR_CountMediaItems(0)):
        m = RPR_GetMediaItem(0, i)
        mt = RPR_GetMediaItemTake(m, 0)
        name = RPR_GetSetMediaItemTakeInfo_String(mt, "P_NAME", "", 0)[3]
        if len(name) > 0: 
            item_names[name.lower().strip()] = m

    if title in item_names:
        return item_names[title]

    return None

def get_midi_data(item):
    notes_array = []
    notes_pos = 0

    start_midi = 0
    end_midi = 0

    chunk = RPR_GetSetItemState(item, "", MAXLEN)[2].strip()
    vars_array = chunk.split('\n')

    i = 0
    while i < len(vars_array):
        note = ""
        if vars_array[i].startswith("E ") or vars_array[i].startswith("e "):
            if start_midi == 0: start_midi = i
            note = vars_array[i].split(" ")
            if len(note) >= 5:
                decval = int(note[3], 16) # MIDI note value
                notes_pos = notes_pos + int(note[1]) # Ticks since last note
                status = int(note[2], 16)
                velocity = int(note[4], 16)
                n = MIDINote(int(note[1]), notes_pos, status, decval, velocity) 
                notes_array.append(n)
        elif vars_array[i].startswith("<X") or vars_array[i].startswith("<x"):
            if start_midi == 0: start_midi = i
            note = vars_array[i].split(" ")
            if len(note) >= 2:
                notes_pos = notes_pos + int(note[1])
                encText = vars_array[i+1]
                status = int(note[2])
                e = MIDIEvent(int(note[1]), notes_pos, status, encText)
                notes_array.append(e)
                i = i + 2
        else:
            if start_midi != 0 and end_midi == 0: end_midi = i

        i = i + 1

    data = MIDITrackData(chunk, start_midi, end_midi, notes_array)

    return data

def write_midi_data(item, data):
    RPR_GetSetItemState(item, str(data), MAXLEN)

def recalculate_positions(MIDIdata):
    if len(MIDIdata.notes) < 2: return

    MIDIdata.notes[0].rpos = MIDIdata.notes[0].apos

    i = 1
    for i in range(len(MIDIdata.notes)):
        note = MIDIdata.notes[i]
        prev = MIDIdata.notes[i-1]

        # Ignore the note on/note off events
        if note.status != 0xb0 and prev.status != 0xb0:
            note.rpos = note.apos - prev.apos

# Filter to only keep notes for hand positions
def filter_pro_positions(MIDIdata):
    new_notes = []

    for note in MIDIdata.notes:
        if isinstance(note, MIDINote):
            if note.status == MIDI_ON and note.note == LH_POS:
                new_notes.append(note)

    MIDIdata.notes = new_notes
    return MIDIdata

# Filter out notes within the left-hand animation range
def filter_std_positions(MIDIdata):
    new_notes = []

    for note in MIDIdata.notes:
        if isinstance(note, MIDINote):
            if note.note < LH_START or note.note > LH_END:
                new_notes.append(note)
        else:
            new_notes.append(note)

    MIDIdata.notes = new_notes
    recalculate_positions(MIDIdata)
    return MIDIdata

# Merge notes of MIDIdata_2 into MIDIdata_1
def merge_notes(MIDIdata_1, MIDIdata_2):
    MIDIdata_1.notes += MIDIdata_2.notes
    MIDIdata_1.notes.sort(key=lambda x: x.apos)
    recalculate_positions(MIDIdata_1)

    return MIDIdata_1

def pro_to_lh(form, inst):
    pro_name = "part real_" + inst.lower()
    pro_item = get_item(pro_name)
    
    std_name = "part " + inst.lower()
    std_item = get_item(std_name)

    if pro_item is None:
        RPR_MB("Could not find a \"PART REAL_GUITAR\" MIDI item.", "Pro to LH", 0)
        form.destroy()
        return
    if std_item is None:
        RPR_MB("Could not find a \"PART GUITAR MIDI\" item.", "Pro to LH", 0)
        form.destroy()
        return

    pro_midi = filter_pro_positions(get_midi_data(pro_item))
    std_midi = filter_std_positions(get_midi_data(std_item))

    # Add MIDI notes that translate the Pro G/B positions
    # to animation ones.
    # Add a note on and off, as 32nd notes.
    lh_notes = []
    for note in pro_midi.notes:
        if (note.velocity - 100) < 1: pitch = 1
        elif (note.velocity - 100) > 12: pitch = 12
        else: pitch = LH_TO_FRET[note.velocity - 100]

        lh_notes.append(MIDINote(0, note.apos, MIDI_ON, pitch, 96))
        lh_notes.append(MIDINote(0, note.apos + TICKS//8, MIDI_OFF, pitch, 0))

    pro_midi.notes = lh_notes
    merge_notes(std_midi, pro_midi)

    write_midi_data(std_item, std_midi)

    form.destroy()

def main():
    form = Tkinter.Tk()
    form.wm_title("Pro to LH")
    form.minsize(height=70, width=170)

    frame_sel = Tkinter.Frame(form)
    frame_sel.pack(side=Tkinter.LEFT, fill="both", padx=10)

    opts = ("Guitar", "Bass")
    tkvar = Tkinter.StringVar(form)
    tkvar.set("Guitar")

    inst_sel = Tkinter.OptionMenu(frame_sel, tkvar, *opts)
    inst_sel.pack(side=Tkinter.LEFT)

    frame_btn = Tkinter.Frame(form)
    frame_btn.pack(side=Tkinter.RIGHT, fill="both", padx=10)

    button = Tkinter.Button(frame_btn, text="Apply", 
            command=lambda: pro_to_lh(form, tkvar.get()))
    button.pack(side=Tkinter.RIGHT)

    form.mainloop()

if __name__ == "__main__":
    main()
