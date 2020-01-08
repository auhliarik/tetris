import tkinter
import random

import square as sq
import shape as shp


class Game():
    def __init__(self, window, next_shape_canvas):
        # Do not change these constants. Their changing is not possible without
        # a manual change of other parameters - mainly shapes' spawnig position.
        self.block_size  = sq.Square.a = 30
        self.no_rows     = sq.Square.num_rows = 20
        self.no_columns  = sq.Square.num_columns = 15
        self.delay = 500     # delay, between two subsequent movements down [ms]

        self.real_gravity = False
        self.paused = False
        self.points = 0

        # Canvas, Where next shape to spawn is shown
        self.next_shape_canvas = next_shape_canvas
        # Main canvas
        self.canvas_height = self.no_rows*self.block_size
        self.canvas_width = self.no_columns*self.block_size
        self.canvas = tkinter.Canvas(window,
                                     height=self.canvas_height,
                                     width=self.canvas_width,
                                     bg='black')
        self.canvas.grid(row=0, column=0)
        sq.Square.canvas = self.canvas

        self.shape_types = ['I', 'J', 'L', 'S', 'Z', 'O', 'T']
        self.active_shape = shp.Shape(random.choice(self.shape_types))
        self.shapes_in_canvas = {self.active_shape}

        self.time_step_cycle = None

        # Binding keys
        for key in '<Left>', '<Right>', '<Up>', '<Down>', '<space>':
            self.canvas.bind_all(key, self.key_pressed)


    def run(self):
        self.time_step()


    def time_step(self):
        if self.active_shape == None:
            self.erase_full_lines()
            # Create random shape
            self.active_shape = shp.Shape(random.choice(self.shape_types))
            self.shapes_in_canvas.add(self.active_shape)
            if self.active_shape.can_move('<down>', self.shapes_in_canvas):
                self.active_shape.move('<down>')
                self.canvas.after(500)
            else:
                self.paused = True
                print("Game over")

        if not self.paused:
            if self.active_shape.can_move('<down>', self.shapes_in_canvas):
                self.active_shape.move('<down>')
            else:
                self.active_shape = None

            self.time_step_cycle = self.canvas.after(self.delay, self.time_step)


    def key_pressed(self, event):
        key = event.keysym
        if self.active_shape == None:
            pass
        elif key == 'Left':
            self.active_shape.test_and_move('<left>', self.shapes_in_canvas)
        elif key == 'Right':
            self.active_shape.test_and_move('<right>', self.shapes_in_canvas)
        elif key == 'Up':
            # Rotates a shape
            self.active_shape.test_and_rotate(self.shapes_in_canvas)
        elif key == 'Down':
            # Forces a shape to fall one block immediately
            # self.time_step timer is cancelled, so that shape does not fall
            # both due to time flow  and pressing '<Down>' key.
            # After falling one block the timer restarts.
            self.canvas.after_cancel(self.time_step_cycle)
            self.active_shape.test_and_move('<down>', self.shapes_in_canvas)
            self.time_step_cycle = self.canvas.after(self.delay, self.time_step)
        elif key == 'space':
            # Forces shape to immediately land
            self.canvas.after_cancel(self.time_step_cycle)
            while self.active_shape.can_move('<down>', self.shapes_in_canvas):
                self.active_shape.move('<down>')
            self.active_shape = None
            self.time_step_cycle = self.canvas.after(self.delay, self.time_step)
        else:
            print(key)

    def erase_full_lines(self):
        """
        """
        no_rows = self.no_rows
        no_columns = self.no_columns
        no_deleted_lines = 0

        for row in range(0, no_rows):
            row_full = True
            shapes_in_row = set()
            for column in range(0, no_columns):
                block_occupied = False
                for shape in self.shapes_in_canvas:
                    if shape.is_at(row, column):
                        block_occupied = True
                        shapes_in_row.add(shape)
                        break
                if not block_occupied:
                    row_full = False
                    break

            if row_full:
                # Deletes line
                no_deleted_lines += 1
                for column in range(0, no_columns):
                    for shape in shapes_in_row:
                        if shape.is_at(row, column):
                            shape.delete_square_at(row, column)
            if not self.real_gravity:
                for i in range(no_deleted_lines):
                    for shape in self.shapes_in_canvas:
                        shape.test_and_move('<down>', self.shapes_in_canvas)
            else:
                pass

    # def save(self, filename):
    #     shapes = {}
    #     for shape in self.shapes_in_canvas:
    #         shape_data = {"type": shape.}
