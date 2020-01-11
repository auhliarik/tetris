import tkinter as tk
from tkinter import font as tkfont


import game

class Program:
    def __init__(self):

        self.window = tk.Tk()
        self.window.title("Tetris")


        #
        self.toolbar = tk.Frame(self.window,
                                height=600,
                                width=400)
        self.toolbar.grid(row=0, column=1)

        # Canvas, where next shape is displayed together with its label
        font = tkfont.Font(family='Helvetica', size=16, weight='bold')
        self.next_shape_label = tk.Label(self.toolbar, text="Next shape:",
                                         font=font)
        self.next_shape_label.grid(row=0)
        self.next_shape_canvas = tk.Canvas(self.toolbar,
                                           width=5*30, height=4*30,
                                           bg='black')
        self.next_shape_canvas.grid(row=1, padx=20, pady=0)


        self.game = game.Game(self, self.window, self.next_shape_canvas)


        font = tkfont.Font(family='Helvetica', size=20, weight='bold')
        self.new_game_button = tk.Button(self.toolbar,
                                         text="New game", font=font,
                                         command=self.ask_if_sure)
        self.new_game_button.grid(row=2, pady=20)


        self.pause_image = tk.PhotoImage(file='pause.png')
        self.play_image = tk.PhotoImage(file='play.png')
        self.pause_button = tk.Button(self.toolbar, width=50, height=50,
                                      image=self.pause_image,
                                      command=self.pause_unpause)
        self.pause_button.grid(row=3, padx=20, pady=20)


        self.game.run()

        self.window.mainloop()


    def pause_unpause(self):
        if not self.game.paused:
            self.game.pause()
            self.game.unbind_keys()
            self.pause_button.config(image=self.play_image)
        else:
            self.game.run()
            self.game.bind_keys()
            self.pause_button.config(image=self.pause_image)

    def new_game(self):
        self.pause_button.config(image=self.pause_image)
        self.game.new_game()

    def ask_if_sure(self):
        """Creates a popup window with a question, whether user is sure to quit
        the game and start again. Afterwards, it acts according to answer."""

        if not self.game.paused:
            self.pause_unpause()

        self.popup = tk.Toplevel(self.window)
        self.popup.title("Warning")

        text = "Are you sure you want to start again?\n"
        text += "All progress will be lost."
        font = tkfont.Font(family='Helvetica', size=14)
        label = tk.Label(self.popup, text=text, font=font)
        label.grid(row=0, columnspan=2, padx=20, pady=10)

        def f_no():
            self.popup.destroy()
            self.pause_unpause()
        button_no = tk.Button(self.popup, text="No", font=font,
                              command=f_no)
        button_no.grid(row=1, column=0)
        def f_yes():
            self.popup.destroy()
            self.new_game()
        button_yes = tk.Button(self.popup, text="Yes", font=font,
                               command=f_yes)
        button_yes.grid(row=1, column=1)

        # Placing popup window somewhat closer to the center
        x = self.window.winfo_x()
        y = self.window.winfo_y()
        self.popup.geometry("+%d+%d" % (x + 70, y + 200))

Program()
