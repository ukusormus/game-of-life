# public packages
import tkinter as tk
import tkinter.filedialog as tk_filedialog
from copy import deepcopy
from time import sleep
from threading import Thread
from math import log
import csv

# --- debugging mem leak --
# from pympler import summary, muppy
# 
# def debug_mem():
#     while True:
#         all_objects = muppy.get_objects()
#         summary.print_(summary.summarize(all_objects))
#         sleep(5)
# 
# Thread(target=debug_mem).start()
# ------------------------

# internal packages
from custom_hover_button import MyButton
from timer import Timer  # for timing code execution

t = Timer()

# find & replace "#print" with "print" for more info

def init_root():
    ## General
    root = tk.Tk()
    root.title("Game of Life")
    
    # TODO: add a fancy icon
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
    
    ## Handle window exit button
    def destroy_and_exit():
        root.destroy()
        raise SystemExit
    root.protocol("WM_DELETE_WINDOW", destroy_and_exit)
    
    ## Window
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    window_width = int(screen_width / 1.4)
    window_height = int(screen_height / 1.5)

    # Sets window to the center of screen
    window_x = int(screen_width / 2 - window_width / 2)
    window_y = int(screen_height / 2 - window_height / 2)

    root.geometry(
        f"{window_width}x{window_height}+{window_x}+{window_y}")
    
    # Make window size static
    root.resizable(False, False)
    
    # Window will always be at least minsize
    # root.minsize(window_width, window_height)
    
    ## Layout & styling: root has two columns, one row
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)
    
    root.configure(bg="#858585")
    
    return root


class Controls:
    """
    Right side of the window: controlling what happens on the board
    """
    def __init__(self, master, game):
        self.master = master
        self.game = game
        
        self.width = int(master.winfo_width() / 2.2)
        
        self.height = int(master.winfo_height() / 2.4)
        
        self.colors = {
            #"controls_bg": "#545454",
            "blue_button": "#01BAEF",
            "blue_button_hover": "#5BC3EB",
            "blue_button_click": "#FFFBFE"
        }
        
        
        ## Setup frame
        frame_padding = 20
        self.frame = tk.Frame(self.master, width=self.width, height=self.height, padx=frame_padding, pady=frame_padding)
        self.frame.grid(column=1, row=0)
        
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=4)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=1)
        
        self.frame.grid_propagate(0)  # forces frame to be certain size
        
        ## Setup buttons and controls
        button_padding = 10
        
        # | Column 0: |
        
        # - Evolve button (one generation forward)
        self.forward_button = self.forward_button()
        self.master.bind("e", lambda _: self.forward_button.invoke())
        self.forward_button.grid(column=0, row=0, sticky="NEWS", padx=button_padding, pady=button_padding)
        
        # - Play button
        self.play_button = self.play_button()
        self.master.bind("p", lambda _: self.play_button.invoke())
        self.play_button.grid(column=0, row=1, sticky="NEWS", padx=button_padding, pady=button_padding)
        
        self.playing = False
        self.min_play_speed = 1
        self.max_play_speed = 20
        # play_speed changes seconds of sleep (see self.play_thread())
        # used as a tk variable in play_speed_slider 
        self.play_speed = tk.IntVar(value=self.min_play_speed)
        
        # - Play speed slider
        self.play_speed_slider = self.speed_slider()
        self.play_speed_slider["label"] = f"Simulation speed ({self.min_play_speed}-{self.max_play_speed})"
        self.play_speed_slider.grid(column=0, row=2, sticky="EWS", padx=button_padding, pady=button_padding)
        # Keyboard support - clamping speed to min and max speed is handled by tkinter scale widget (from_ and to) :)
        self.master.bind("<Left>", lambda _: self.play_speed_slider.set(self.play_speed_slider.get() - 1))
        self.master.bind("<Right>", lambda _: self.play_speed_slider.set(self.play_speed_slider.get() + 1))
        # Bind left click to right click on slider to change value according to where you click, not increment (decrement) by one
        self.play_speed_slider.bind("<Button-1>",
                                    lambda e: self.play_speed_slider.event_generate("<Button-3>", x=e.x, y=e.y))
        
        hints_padding = 10
        self.slider_hint_right = tk.Label(master=self.frame, text="(→)")
        self.slider_hint_right.grid(column=0, row=3, sticky="SE", padx=hints_padding)
        self.slider_hint_left = tk.Label(master=self.frame, text="(←)")
        self.slider_hint_left.grid(column=0, row=3, sticky="SW", padx=hints_padding)        
        
        # | Column 1: |
        
        # - Reset board
        self.reset_button = self.reset_button()
        self.master.bind("r", lambda _: self.reset_button.invoke())
        self.reset_button.grid(column=1, row=0, sticky="NEWS", padx=button_padding, pady=button_padding)
        
        # - Load board
        self.default_layouts_folder = "./layouts"
        
        self.load_layout = self.load_layout()
        self.master.bind("l", lambda _: self.load_layout.invoke())
        self.load_layout.grid(column=1, row=1, sticky="NEWS", padx=button_padding, pady=button_padding)
        
        # - Save board
        self.save_layout = self.save_layout()
        self.master.bind("s", lambda _: self.save_layout.invoke())
        self.save_layout.grid(column=1, row=2, sticky="NEWS", padx=button_padding, pady=button_padding)
        
        # - Board width and height / a square
        self.board_min_size = 1
        self.board_max_size = 100
        
        self.board_size_box = self.board_size_box()
        box_padding = 15
        self.board_size_box.grid(column=1, row=3, columnspan=1, sticky="SE", padx=box_padding)

        self.board_size_label = tk.Label(master=self.frame, text=f"Board size ({self.board_min_size}-{self.board_max_size})")
        self.board_size_label.grid(column=1, row=3, sticky="SW", padx=button_padding)

    
    def forward_button(self):
        return MyButton(master=self.frame, text=">> Evolve once (E)",
                      bg_color=self.colors.get("blue_button"),
                      hover_color=self.colors.get("blue_button_hover"),
                      click_color=self.colors.get("blue_button_click"),
                      command=lambda: self.game.evolve())

    def reset_button(self):
        def reset():
            self.game.clear_grid()
            
            if self.playing:  # stop evolution & playing if board is reset
                self.play_button.invoke()
        
        return MyButton(master=self.frame, text="Reset board (R)",
                      bg_color=self.colors.get("blue_button"),
                      hover_color=self.colors.get("blue_button_hover"),
                      click_color=self.colors.get("blue_button_click"),
                      command=lambda: reset())
    
    def speed_slider(self):
        return tk.Scale(master=self.frame, from_=self.min_play_speed, to=self.max_play_speed,
                        orient=tk.HORIZONTAL, length=self.width / 2.5, width=self.height / 20, sliderlength=self.width / 22, 
                        troughcolor=self.colors.get("blue_button_hover"),
                        borderwidth=0,
                        variable=self.play_speed)  # this variable is changed when scale is moved
    
    def play_button(self):        
        def play_action():  # called on play button click
            self.playing = not self.playing
            
            if self.playing:
                #print("Starting playing.")
                
                Thread(target=self.play_thread).start()
                
                self.play_button["text"] = ">> Pause (P)"
            else:
                #print("Pausing playing.")
                
                self.play_button["text"] = ">> Play (P)"
        
        
        return MyButton(master=self.frame, text=">> Play (P)",
                      bg_color=self.colors.get("blue_button"),
                      hover_color=self.colors.get("blue_button_hover"),
                      click_color=self.colors.get("blue_button_click"),
                      command=lambda: play_action())
    
    def play_thread(self):  # started from play_action as a Thread
        while self.playing:
            #print("playing...")
            
            self.game.evolve()
            
            # sleep time formula between generations: a log curve
            # if play_speed is between 1 and 20, then sleep_time is between 1 and 0.002 (sec)
            sleep_time = log(self.play_speed.get(), 0.047) + 1
            
            sleep(sleep_time)
    
    def load_layout(self):
        def load_layout_action():
            if self.playing:  # stop evolution & playing if new layout is beginning to be loaded
                self.play_button.invoke()
            
            #print("Loading new board, opening file dialog...")
            filename = tk_filedialog.askopenfilename(title="Load a new Game of Life board layout",
                                                 initialdir=self.default_layouts_folder, filetypes=[("Comma-separated values file", "*.csv")])

            if filename == "":  # load dialog closed
                return

            with open(filename, "r") as file:
                #print(f"{filename} opened. Reading...")
                
                csvreader = csv.reader(file)
                
                # layout file's first row should be board size (rows,cols)
                board_rows, board_columns = next(csvreader)
                self.game.change_grid_size(int(board_rows), int(board_columns))
                
                self.board_size_box.delete(0, tk.END)
                self.board_size_box.insert(0, f"{board_rows}")
                #print(f"Rows: {board_rows}, cols: {board_columns}")
                
                # every other row is live cell coordinates
                for row in csvreader:
                    self.game.create_cell(int(row[0]), int(row[1]))
            
            #print("New board loaded.")
            #print()
            
        return MyButton(master=self.frame, text="Load board (L)",
                      bg_color=self.colors.get("blue_button"),
                      hover_color=self.colors.get("blue_button_hover"),
                      click_color=self.colors.get("blue_button_click"),
                      command=lambda: load_layout_action())
    
    def save_layout(self):
        def save_layout_action():
            if self.playing:  # stop evolution & playing if current layout is beginning to be saved
                self.play_button.invoke()            
            
            #print("Saving current board...")
            filename = tk_filedialog.asksaveasfilename(title="Save your Game of Life current board layout",
                                                       initialdir=self.default_layouts_folder, defaultextension=".csv",
                                                       filetypes=[("Comma-separated values file", "*.csv")])
            
            if filename == "":  # save dialog closed
                return
            
            with open(filename, "w", newline="") as file:  # newline="" removes blank lines between csv rows
                #print(f"{filename} opened. Saving...")
                
                csvwriter = csv.writer(file)
                
                # write board size (rows,cols)
                csvwriter.writerow([self.game.cell_rows, self.game.cell_columns])
                
                # write live cells' coordinates
                data = [[x, y] for (x, y) in self.game.cell_objects.keys()]
                #print(data)
                csvwriter.writerows(data)
                
            #print("New board saved.")
            #print()
        
        return MyButton(master=self.frame, text="Save board (S)",
                      bg_color=self.colors.get("blue_button"),
                      hover_color=self.colors.get("blue_button_hover"),
                      click_color=self.colors.get("blue_button_click"),
                      command=lambda: save_layout_action())
    
    def board_size_box(self):
        def validate_board_size(i):
            # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/entry-validation.html
            #print("Validating if input board size is integer...")
            #print()
            
            if i == "":  # allows backspace / empty input
                # We allow this, but don't change the actual board size
                return True
            
            if not str.isdigit(i):
                return False
            
            i = int(i)
            
            if i < self.board_min_size:
                return False
            
            if i > self.board_max_size:
                return False
            
            # Change board size
            self.game.change_grid_size(i, i)
            
            return True
        
        vcmd = (self.frame.register(validate_board_size))
        
        entry = tk.Entry(master=self.frame, textvariable=tk.StringVar(self.frame, value=f"{self.game.cell_rows}"),
                        exportselection=0, # disable auto-copy to clipboard
                        validate="key", validatecommand=(vcmd, "%P"))  # %P returns "the value that the text will have if the change is allowed"
        
        return entry 


class Game:
    """
    Left side of the window: the game itself, including cell logic
    """
    def __init__(self, master):
        self.master = master
        
        self.colors = {
            "canvas_bg": "#545454",
            "gridline": "#707070",
            "cell_fill": "#EFEA5A",
            "cell_outline": "#858585"
        }
        
        ## Canvas
        self.width = int(master.winfo_width() / 2.2)
        self.height = self.width
        self.padding = 20
        
        self.canvas = tk.Canvas(self.master, bg=self.colors.get("canvas_bg"),
                                width=self.width, height=self.width,
                                highlightthickness=0, borderwidth=0)
        
        # To delete and add cells on left mouse click
        self.canvas.bind("<Button-1>", self.canvas_clicked)
        
        self.canvas.grid(column=0, row=0, sticky="W", padx=self.padding, pady=self.padding)
        
        ## Cells
        self.cell_rows = 20
        self.cell_columns = 20
        
        self.cell_width = self.width / self.cell_rows
        self.cell_height = self.height / self.cell_columns
        self.cell_border_width = 1

        # cell_objects' keys are coordinates as tuples: (cell_row, cell_col), e.g. (5, 2)
        # cell_objects' values are object IDs as ints: id, e.g. 3
        self.cell_objects = dict()
        
        #self.cell_objects2 = [[0 for _ in range(self.cell_rows)] for _ in range(self.cell_columns)]
        
        
        ## Gridlines
        self.draw_gridlines()
        
        
    def draw_gridlines(self):
        # Vertical
        for x in range(self.cell_rows):
            self.canvas.create_line(x * self.cell_width, 0, x * self.cell_width, self.height,
                                    fill=self.colors.get("gridline"), width=self.cell_border_width, tag="gridline")
        # Horizontal
        for y in range(self.cell_columns):
            self.canvas.create_line(0, y * self.cell_height, self.width, y * self.cell_height,
                                    fill=self.colors.get("gridline"), width=self.cell_border_width, tag="gridline")
    
    def change_grid_size(self, new_rows, new_columns, new_width=None, new_height=None):
        #print(f"Changing board size to {new_rows}x{new_columns}...")
        #print()
        self.cell_rows = new_rows
        self.cell_columns = new_columns
        
        if new_width != None and new_height != None:
            self.width = new_width
            self.height = new_height
        
        
        self.cell_width = self.width / self.cell_rows
        self.cell_height = self.height / self.cell_columns
        
        self.canvas.delete("gridline")
        self.draw_gridlines()
        self.draw_whole_grid()
    
#     def is_cell_alive(self, x, y): ### for cell_objects2
#         try:
#             if self.cell_objects2[x][y] != 0:
#                 return True
#         except IndexError:
#             pass
#         
#         return False
    
    def create_cell(self, x, y):
        cell_x0 = x * self.cell_width
        cell_y0 = y * self.cell_height
        cell_x1 = cell_x0 + self.cell_width
        cell_y1 = cell_y0 + self.cell_height
        
        # cell is tkinter object-ID (int)
        cell_id = self.canvas.create_rectangle(cell_x0, cell_y0, cell_x1, cell_y1,
                                               width=self.cell_border_width, fill=self.colors.get("cell_fill"), tag="cell")
        
        self.cell_objects[(x, y)] = cell_id
        #self.cell_objects2[x][y] = cell_id
        
        
        #print(f"New cell (id: {cell_id}) created.")
        #print()
    
    def remove_cell(self, x, y):
        cell_id = self.cell_objects.pop((x, y))
        
#         cell_id = self.cell_objects2[x][y] 
#         self.cell_objects2[x][y] = 0
        
        self.canvas.delete(cell_id)
        
        #print(f"Cell (id: {cell_id}) deleted.")
        #print()
    
    def canvas_clicked(self, e):
        #print("Canvas clicked.")
        
        # Column and row number
        x = int(e.x // self.cell_width)
        y = int(e.y // self.cell_height)
       
        if (x, y) not in self.cell_objects:
        #if not self.is_cell_alive(x, y):
            #print("└ No cell, creating one...")
            self.create_cell(x, y)
        else:
            #print("└ Cell, deleting it...")
            self.remove_cell(x, y)
            
        #print()
    
    def clear_grid(self):
        #print("Clearing grid...")
        
        self.canvas.delete("cell")
        
        self.cell_objects.clear()
        #self.cell_objects2 = [[0 for _ in range(self.cell_rows)] for _ in range(self.cell_columns)]
        
        #print("Grid cleared.")
        #print()
    
    def draw_whole_grid(self):
        # Clear whole canvas
        self.clear_grid()
        
        # Draw live cells
        for (x, y) in self.cell_objects:
            self.create_cell(x, y)
#         for x in range(self.cell_rows):
#             for y in range(self.cell_columns):
#                 if self.is_cell_alive(x, y):
#                     self.create_cell(x, y)
    
    def alive_neighbours_count(self, x, y):
        # Excludes itself
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                
                if (x + i, y + j) in self.cell_objects:
                #if self.is_cell_alive(x + i, y + j):
                    count += 1
        
        return count
    
    def evolve(self):
        #print("Evolving...")
        
        cell_objects_copy = deepcopy(self.cell_objects)
        
        # brute force
        # We don't need to check cells that aren't neighbours of alive cells!? etc
        cells_to_create = []
        
        # ~ 1.4 secs... w cell_objects (dict) / but i used self.width, not self.cell_rows !!!
        # 0.0011 secs w cell_objects (dict)
        # 0.0015 secs w cell_objects2 (2D list)
        # TODO: times are for smaller board, test out performance on bigger boards w more cells
        t.start()
        for x in range(self.cell_rows):
            for y in range(self.cell_columns):
                alive_neighbours = self.alive_neighbours_count(x, y)
                if alive_neighbours == 3 or (alive_neighbours == 2 and (x, y) in cell_objects_copy):
                # if alive_neighbours == 3 or (alive_neighbours == 2 and self.is_cell_alive(x, y)):
                    cells_to_create.append((x, y))
        
        # 0.0001 sec
        self.clear_grid()
        
        if cells_to_create:        
            # 0.0004 sec
            [self.create_cell(x, y) for (x, y) in cells_to_create]
        else:
            # No cells to create, can pause game
            # TODO
            pass
            
            
        t.stop()
        #print("Evolved.")
        #print("--------")
        #print()


def main():
    root = init_root()
    root.update()  # makes root geometry info like winfo_width available to use for Game canvas and Controls frame
    
    game_window = Game(root)
    
    control_window = Controls(root, game_window)
    
    root.mainloop()


if __name__ == "__main__":
    main()