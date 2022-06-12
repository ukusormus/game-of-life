
Author: Uku Sõrmus (GitHub: ukusormus)

WHAT:
- Conway's Game of Life graphical implementation with Python and tkinter
- Supports going step by step and auto-play with various speeds
- Supports loading and saving grid layouts (patterns)
- Supports changing grid size
- Keyboard shortcuts (for controls)
- Some sample patterns in ./layouts
- A script to convert Plaintext to csv (look into ./layouts/plaintext_to_csv.py)

WHAT NOT:
- This project is certainly not optimized for performance (especially with larger patterns)
- Grid is not borderless / looping
- Live cells will be wiped out when board size is changed
- No history is saved

WHY:
- Cellular automata is cool (complexity rising out of simple rules; initial layout determining "the whole life")
- A project for University of Tartu's course "Tehnoloogia tarbijast loojaks (LTAT.TK.011), G" / spring of 2022

...

Future? Feature requests? Bugs?
- I will probably not develop this much further, but it was fun! (almost, I didn't develop deep feelings for tkinter)
- Would be nice: pause game if no cells are to be changed (should restructure the code interdependency, modularize a bit more)
- Bug: right now it looks like the game is leaking some memory! I suspected that deleting from tkinter canvas doesn't actually free up memory (new id-s),
  but debugging without game playing shows that list objects get added? Not sure, may be something with Thonny IDE, or ...
- Maybe rewrite: create all canvas cell elements (rectangles) at once, then change their properties (visibility or color)

...
Read more about Conway's Game of Life: https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life
