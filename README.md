

## What?
### **A graphical implementation of [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)**
### **using Python 3 and tkinter**
- **Multiplatform**: tested on Windows and Ubuntu (should work on MacOS)
- **Drawing and erasing cells by clicking**
- **Loading and saving grid layouts** (patterns)
- **Step-by-step evolution** and **auto-play with various speeds**
- **Keyboard shortcuts** (for controls)
- **Change board size**
- **Sample patterns included** in *src/layouts/*
- A script to convert *Plaintext* to *csv* for patterns (because I reinvented the wheel instead of using standard formats:))

![Demonstration of the program](./README_Showcase_Animation.webp)

## What not?
- This project is certainly not optimized for performance (especially with larger patterns)
- Grid is not borderless / looping
- Live cells will be wiped out when board size is changed
- History is not saved (no undo)

## Why?
- Cellular automata is cool (complexity rising out of simple rules; initial layout determining "the whole life")
- A project for University of Tartu's course "Tehnoloogia tarbijast loojaks (LTAT.TK.011), G" / spring of 2022
<br>
<br>
---
## Reflection & future: feature requests & bugs?
- I will probably not develop this much further, but it was fun! (almost, I didn't develop deep feelings for tkinter)
- Would be nice: pause game if no cells are to be changed (should restructure to lessen code interdependency, maybe modularize a bit etc, remove dead comments/code)
- Bug: right now it looks like the game is leaking some memory! I suspected that deleting from tkinter canvas doesn't actually free up memory (new id-s)
- Could rewrite: create all canvas cell elements (rectangles) at once, then change their visibility using canvas.itemconfig -- I tried some of that with the help of GitHub Copilot in a separate tinkering file, seemed more performant
