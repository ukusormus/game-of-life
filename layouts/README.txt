Layout files are csv files. The header (first line) will indicate board size and the rest of the file will have coordinates of alive cells.

-------
board width,board height
first live cell x,first live cell y
second live cell x,second live cell y
...
n-th live cell x,n-th live cell y
--------

Use plaintext_to_csv.py to convert Plaintext pattern file to csv. You can find some patterns from here: https://conwaylife.com/wiki/Category:Patterns

Usage: python plaintext_to_csv.py [patter.cells]