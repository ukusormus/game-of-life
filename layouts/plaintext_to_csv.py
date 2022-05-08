"""
For converting Plaintext files (https://conwaylife.com/wiki/Plaintext) to csv files to use patterns from conwaylife.com's wiki more easily.

(storing patterns in csv because who looks up conventions before starting to code his very own GOL? :))
"""

import csv
import argparse
import os.path

parser = argparse.ArgumentParser()

parser.add_argument("input_filename", help="input file (Plaintext)")

args = parser.parse_args()

print("\n" * 3)
print("-" * 50)

print(f"Checking if input file ({args.input_filename}) exists...")
if not os.path.isfile(args.input_filename):
    print("! No input file found.")
    exit()


#### SETTINGS
    
padding = 10  # to make room for patterns to evolve outside of initial conditions
fixed_size_board = 0  # change this to non-0 pos value if you want a board of fixed size

# If you need to shift patterns around a bit (e.g. for spaceships), change these values to non zero
cell_shift_x = 38  # pos for right-shift, neg for left-shift
cell_shift_y = 50  # pos for down-shift, neg for up-shift

#### /SETTINGS

rows = padding
cols = padding

alive_cells_count = 0
coords_to_write = []

print("File exists, reading...")
with open(args.input_filename, "r") as file:
    
    for line in file.readlines():
        #print(line)
        
        if line.startswith("!"):  # comments
            continue
        
        curr_col_nr = padding
        
        for char in line:
            if char == "O":  # alive cell
                alive_cells_count += 1
                coords_to_write.append((curr_col_nr + cell_shift_x, rows + cell_shift_y))
            
            curr_col_nr += 1
            cols = max(curr_col_nr, cols)  # keep track of the furthest col
        
        rows += 1  # every row that is not a comment is a row

print("Reading input file done.")

print()
print(f"- Board size: {cols}x{rows}.")
print(f"- Alive cells count: {alive_cells_count}")
print(f"- List of coordinates: {coords_to_write}")
print()


out_filename = os.path.splitext(args.input_filename)[0] + ".csv"  # replace current file extension with csv
print(f"Writing output file ({out_filename}) ...")

with open(out_filename, "w", newline="") as file:  # newline="" removes blank lines between csv rows
        csvwriter = csv.writer(file)
        
        # fixed size board or padding (look up in the SETTINGS section)
        if fixed_size_board > 0:
            rows = fixed_size_board
        else:
            rows = max(rows, cols) + padding - 1
        
        # write board size (rows,cols)
        # make the board a square
        csvwriter.writerow([rows, rows])
        
        # write live cells' coordinates
        csvwriter.writerows(coords_to_write)

print("Ready.")
print("-" * 50)
print("\n" * 3)