import tkinter as tk
import tkinter.filedialog

from tkinter import font as tkfont

import game

class Program:
    def __init__(self):

        self.window = tk.Tk()
        self.window.title("Tetris")


        #
        self.toolbar = tk.Frame(self.window,
                                height=600,
                                width=500)
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

        # At this point game object can be created
        self.game = game.Game(self, self.window, self.next_shape_canvas)

        # Labels with number of points and number of deleted lines displayed
        font = tkfont.Font(family='Helvetica', size=16, weight='bold')
        self.points_display = tk.Label(self.toolbar,
                                       textvariable=self.game.points_text,
                                       font=font)
        self.points_display.grid(row=2, padx=20, pady=5)
        self.lines_display = tk.Label(self.toolbar,
                                       textvariable=self.game.lines_text,
                                       font=font)
        self.lines_display.grid(row=3, padx=20, pady=5)

        # 'Help' button
        font = tkfont.Font(family='Helvetica', size=18, weight='bold')
        self.help_button = tk.Button(self.toolbar,
                                     text="Help", font=font,
                                     command=self.show_help)
        self.help_button.grid(row=4, pady=5)


        # 'New game' button
        font = tkfont.Font(family='Helvetica', size=18, weight='bold')
        self.new_game_button = tk.Button(self.toolbar,
                                         text="New game", font=font,
                                         command=self.ask_if_sure)
        self.new_game_button.grid(row=5, pady=5)

        # 'Save' button
        font = tkfont.Font(family='Helvetica', size=18, weight='bold')
        self.save_game_button = tk.Button(self.toolbar,
                                          text="Save", font=font,
                                          command=self.save_game)
        self.save_game_button.grid(row=6, pady=5)

        # 'Load' button
        font = tkfont.Font(family='Helvetica', size=18, weight='bold')
        self.load_game_button = tk.Button(self.toolbar,
                                          text="Load", font=font,
                                          command=self.load_game)
        self.load_game_button.grid(row=7, pady=5)

        # 'Pause'/'Play' buton
        self.pause_image = tk.PhotoImage(file='pause.png')
        self.play_image = tk.PhotoImage(file='play.png')
        self.pause_button = tk.Button(self.toolbar, width=100, height=70,
                                      image=self.pause_image,
                                      command=self.pause_unpause)
        self.pause_button.grid(row=8, padx=20, pady=15)

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

    def show_help(self):
        if not self.game.paused:
            was_paused = False
            self.pause_unpause()

        self.popup = tk.Toplevel(self.window)
        self.popup.title("Help")
        self.popup.grab_set()
        self.popup.attributes('-topmost', 'true')

        text = "Controls:\n"
        text += "left/right - shifts shape to the left/right\n"
        text += "down - speeds up falling of the shape\n"
        text += "up - rotates shape by 90 degrees\n"
        text += "space - forces shape to immediately land\n"
        font = tkfont.Font(family='Helvetica', size=14)
        label = tk.Label(self.popup, text=text, font=font)
        label.grid(row=0, padx=10, pady=2)

        def okey():
            self.popup.grab_release()
            self.popup.destroy()
            if not was_paused:
                self.pause_unpause()

        button = tk.Button(self.popup, text="Okey", font=font, command=okey)
        button.grid(row=1, pady=2)

        # Placing popup window somewhat closer to the center
        x = self.window.winfo_x()
        y = self.window.winfo_y()
        self.popup.geometry("+%d+%d" % (x + 70, y + 180))


    def ask_if_sure(self):
        """Creates a popup window with a question, whether user is sure to quit
        the game and start again.
        Afterwards, it acts according to answer."""

        if not self.game.paused:
            self.pause_unpause()

        self.popup = tk.Toplevel(self.window)
        self.popup.title("Warning")
        self.popup.grab_set()
        self.popup.attributes('-topmost', 'true')

        text = "Are you sure you want to start again?\n"
        text += "All progress will be lost."
        font = tkfont.Font(family='Helvetica', size=14)
        label = tk.Label(self.popup, text=text, font=font)
        label.grid(row=0, columnspan=2, padx=20, pady=10)

        def f_no():
            self.popup.grab_release()
            self.popup.destroy()
            self.pause_unpause()
        button_no = tk.Button(self.popup, text="No", font=font,
                              command=f_no)
        button_no.grid(row=1, column=0)
        def f_yes():
            self.popup.grab_release()
            self.popup.destroy()
            self.new_game()
        button_yes = tk.Button(self.popup, text="Yes", font=font,
                               command=f_yes)
        button_yes.grid(row=1, column=1)

        # Placing popup window somewhat closer to the center
        x = self.window.winfo_x()
        y = self.window.winfo_y()
        self.popup.geometry("+%d+%d" % (x + 70, y + 200))

    def new_game(self):
        """Resets the game after user has expressed he/she is sure."""

        self.pause_button.config(image=self.pause_image)
        self.game.new_game()

    def save_game(self):
        if not self.game.paused:
            was_paused = False
            self.pause_unpause()
        else:
            was_paused = True
        filetypes = (("tetris files", "*.tet"),)
        filename = tk.filedialog.asksaveasfilename(initialdir=".",
                                                   title="Select file",
                                                   filetypes=filetypes)
        if filename:
            self.game.save(filename)
        if not was_paused:
            self.pause_unpause()

    def load_game(self):
        if not self.game.paused:
            was_paused = False
            self.pause_unpause()
        else:
            was_paused = True
        filetypes = (("tetris files", "*.tet"),)
        filename = tk.filedialog.askopenfilename(initialdir=".",
                                                 title="Select file",
                                                 filetypes=filetypes)
        if filename:
            self.game.load(filename)
        if not was_paused:
            self.pause_unpause()


Program()
