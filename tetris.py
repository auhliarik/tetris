import tkinter as tk

import game

class Program:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Tetris")

        self.game = game.Game(self.window, None)

        self.toolbar = tk.Frame(self.window,
                                height=self.game.canvas_height,
                                width=150)
        self.toolbar.grid(row=0, column=1)



        self.game.run()

        self.window.mainloop()


    def close_menu(self):
        self.menu.destroy()
        self.window.lift()
        self.window.grab_set()
        self.window.focus_force()



Program()
