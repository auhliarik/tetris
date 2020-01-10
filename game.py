import tkinter
import random
import time

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

        # Canvas, Where next shape to spawn is shown, should be set before run
        self.next_shape_canvas = next_shape_canvas
        # Main canvas
        self.canvas_height = self.no_rows*self.block_size
        self.canvas_width = self.no_columns*self.block_size
        self.canvas = tkinter.Canvas(window,
                                     height=self.canvas_height,
                                     width=self.canvas_width,
                                     bg='black')
        self.canvas.grid(row=0, column=0)
        shp.Shape.primary_canvas = self.canvas

        self.shape_types = ['I', 'J', 'L', 'S', 'Z', 'O', 'T']
        self.active_shape = shp.Shape(random.choice(self.shape_types))
        self.next_shape_type = random.choice(self.shape_types)
        self.display_next_shape(self.next_shape_type)
        self.shapes_in_canvas = {self.active_shape}

        self.time_step_cycle = None
        self.bind_keys()


    def display_next_shape(self, type):
        i0 = 2
        j0 = 1

        if type == 'I':
            i0 += -0.5
            j0 += -0.5
        elif type == 'O':
            i0 += 0
            j0 += -0.5
        self.next_shape_canvas.delete('all')
        self.next_shape = shp.Shape(type, i0=i0, j0=j0,
                                    canvas=self.next_shape_canvas)

    def run(self):
        self.paused = False
        self.time_step()

    def pause(self):
        self.paused = True
        self.canvas.after_cancel(self.time_step_cycle)

    def new_game(self):
        self.pause()

        for shape in self.shapes_in_canvas:
            shape.delete()
        self.shapes_in_canvas.clear()

        self.time_step_cycle = None

        self.active_shape = shp.Shape(random.choice(self.shape_types))
        self.next_shape_type = random.choice(self.shape_types)
        self.canvas.update()

        self.shapes_in_canvas = {self.active_shape}
        self.points = 0
        time.sleep(0.6)
        self.run()

    def bind_keys(self):
        for key in '<Left>', '<Right>', '<Up>', '<Down>', '<space>':
            self.canvas.bind_all(key, self.key_pressed)

    def unbind_keys(self):
        for key in '<Left>', '<Right>', '<Up>', '<Down>', '<space>':
            self.canvas.unbind_all(key)

    def time_step(self):
        if self.active_shape == None:
            self.erase_full_lines()
            # Spawing new active shape
            self.active_shape = shp.Shape(self.next_shape_type)
            self.shapes_in_canvas.add(self.active_shape)
            # Choosing and displaying new shape in the queue
            self.next_shape_type = random.choice(self.shape_types)
            self.display_next_shape(self.next_shape_type)
            # New active shape starts to fall
            if self.active_shape.can_move('<down>', self.shapes_in_canvas):
                self.active_shape.move('<down>')
                self.time_step_cycle = self.canvas.after(self.delay,
                                                         self.time_step)
                return
            else:
                self.pause()
                print("Game over")

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

        # Detecting full lines
        no_deleted_lines = 0
        for row in range(0, no_rows):
            row_full = True
            shapes_in_row = set()
            for column in range(0, no_columns):
                # Detecting, whether block at (row, column) is occupied
                block_occupied = False
                for shape in self.shapes_in_canvas:
                    if shape.is_at(row, column):
                        block_occupied = True
                        shapes_in_row.add(shape)
                        break
                if not block_occupied:
                    row_full = False
                    break

            # If this row is full two processes occur:
            # 1.) All squares in the line are deleted
            # 2.) Shapes with squares both above and below the deleted line are
            #     separated into two parts, so that they can fall independently
            #     from this moment
            if row_full:
                no_deleted_lines += 1
                # Deleting squares in line
                for column in range(0, no_columns):
                    for shape in shapes_in_row:
                        if shape.is_at(row, column):
                            shape.delete_square_at(row, column)
                # Dividing shapes_in_row into two parts
                for shape in shapes_in_row:
                    part_above = shp.Shape(shape.type, empty=True)
                    self.shapes_in_canvas.add(part_above)
                    for square in list(shape.squares):
                        if square.row > row:
                            shape.remove_square(square)
                            part_above.add_square(square)

        # Deleting all shapes containing no squares
        for shape in list(self.shapes_in_canvas):
            if len(shape.coords) == 0:
                self.shapes_in_canvas.discard(shape)

        # Adding points
        self.points += 100*no_deleted_lines
        if no_deleted_lines != 0:
            print("Points:", self.points)

        # Falling of blocks
        # All shapes try to move down one after another until the situation
        # is not changed after two iterations
        if no_deleted_lines == 0:
            return
        times_unchanged = 0
        while times_unchanged < 2:
            has_changed = False
            for shape in self.shapes_in_canvas:
                if shape.test_and_move('<down>', self.shapes_in_canvas):
                    has_changed = True
            if not has_changed:
                times_unchanged += 1
            else:
                times_unchanged = 0
