# Pro to LH

![Pro to LH GUI](https://i.imgur.com/hl0zPqp.png)

This script translates the left-hand positions in the Pro Guitar or Pro Bass track to the left-hand animations in the standard Guitar/Bass tracks.

## Usage

Place the script **pro_to_lh.py** into a convenient location, such as the folder where you put the other scripts for CAT. Load it into Reaper from the actions menu under **ReaScript: New/Load...**

Use the hastily made GUI to select which instrument to apply the translation to. Specific behavior is listed below.

* The script reads from **PART REAL_GUITAR** or **PART REAL_BASS**, not the 22 fret versions.
* Make sure your MIDI item for those tracks are named exactly as the track. This is what the script looks for.
* The left-hand animation positions are based on Orange Harrison's approximations from the [RBN Docs](http://docs.c3universe.com/rbndocs/index.php?title=Guitar_and_Bass_Authoring#Left_Hand_Animations).
* Any positions higher than fret 12 are floored to fret 12 on the animations.
* Slides and chord events are not handled. Consider this a starting point rather than complete automation.