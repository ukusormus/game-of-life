from tkinter import Button
from tkinter.font import Font

class MyButton(Button):
    """
    Overloaded tkinter Button that has hover logic baked in
    """
    def __init__(self, bg_color="#000000", hover_color="#000000", click_color="#000000", *args, **kwargs):
        self.bg_color = bg_color
        self.hover_color = hover_color
        
        Button.__init__(self, bg=bg_color, activebackground=click_color,
                        relief="flat", font=Font(size=18), justify="center",
                        *args, **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, e):
        e.widget["background"] = self.hover_color
    
    def on_leave(self, e):
        e.widget["background"] = self.bg_color