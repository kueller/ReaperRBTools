# venuegen

This script allows you to draw venue events on a MIDI track, and generate the corresponding track events. No more clutter and no more misspelling event names.

## Setup

Create two tracks in your Reaper project: CAMERA and LIGHTING. Add MIDI items to those tracks as you would any other. **Make sure the MIDI items are named CAMERA/LIGHTING.** This is what the script will look for.

![Track Setup](https://i.imgur.com/L7fP7Bv.png)

You only need the names here. Unlike other tracks in the template you do not need a TRACK NAME event. The script will remove it anyways.

Load the appropriate note names from the given text files. Feel free to edit these as you please. Attempts were made to make the names more readable than the RBN documentation.

## Note Placement

This explains how venuegen will parse and interpret your notes in the MIDI tracks. For general information on how to make a venue refer to the [RBN Docs](http://docs.c3universe.com/rbndocs/index.php?title=RBN2_Camera_And_Lights).

### LIGHTING

![LIGHTING track example](https://i.imgur.com/IVPNGGu.png)

Place the proper lighting and post-processing notes based on the note names. For the lighting notes **first**, **prev**, **next**, **BONUSFX**, and **BONUSFX Opt** you can place any length note and a text event will be generated at the start of the note.

For all other lighting notes, the space between the notes will determine the transition time between the effects. If there is no space between the two notes, an event will be placed only at the start of the note as before. If there *is* space between two notes, an event will be added at the end of the first note and the time in between will be the transition. See the examples below.

![Two events with no space](https://i.imgur.com/gbRsFWr.png)

**Example 1:** The **Desat Posterize** event will switch immediately to the **Film Contrast Red** event since there is no space in between the notes.

![Two events with space](https://i.imgur.com/EHZLbCX.png)

**Example 2:** The **Bright** note has space before **Film Contrast Green**, so an extra event is added at the end of **Bright** to cause a cross-fade transition of the two effects within the time of the open space.

### CAMERA

![CAMERA track example](https://i.imgur.com/g9Bnkx5.png)

Most notes in CAMERA only depend on the start note, so the length does not matter. A few directed cuts will rely in note length. Not for "transitions" but to determine the length of the cut. These events are marked with an asterisk.

#### RANDOM

Camera notes have precedence and if a band member is not present for a specific shot the game will default to a low precendence camera cut. To counter this it is common practice to "stack" camera cuts with your own fallback shots (see the docs for more on this).

The CAMERA track gives the option of a RANDOM note. By itself, the random note will choose a random cut from the set of standard camera cuts. If RANDOM is stacked with existing cuts though, it will choose a cut of lower precedence to be a fallback. A full list of the behavior of RANDOM is below.

* RANDOM will choose a random standard camera cut lower than the lowest precedence shot it is stacked with. If the RANDOM note is alone precedence is not a factor.
* The random generated event will be different from the previous and next camera cuts. If there are stacked cuts preceding and following the cut it will be different from all of them. Do not stack every single event to see what happens.
* RANDOM does not check other RANDOM notes. If you put multiple in succession this might result in duplicate events. This is a tougher problem that will be fixed in a later release.
* Directed cuts are not taken into account, due to their unpredictable nature. They are treated as the highest precedence.
* RANDOM will generate a new random event each time. If you like the result it gives you, change that to a static note.


## Running venuegen

Place the script **venuegen.py** into a convenient location, such as the folder where you put the other scripts for CAT. Load it into Reaper from the actions menu under **ReaScript: New/Load...**

Run the script and after you will see the CAMERA and LIGHTING events populated with the proper events. Copy these into VENUE.

You can change and edit the venuegen notes as you please. Each time the script is run it will generate new events and erase the old ones.

When it is time to export remember to mute the CAMERA and LIGHTING tracks. Magma will complain if they are in the output MIDI.

![Muted tracks](https://i.imgur.com/Cwtjhbr.png)
