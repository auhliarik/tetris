import tkinter
import random
import time

import square as sq
import shape as shp


class Game():
    def __init__(self, program, window, next_shape_canvas):
        # Do not change these constants. Their changing is not possible without
        # a manual change of other parameters - mainly shapes' spawnig position.
        self.program = program
        self.block_size  = sq.Square.a = 30
        self.no_rows     = sq.Square.num_rows = 20
        self.no_columns  = sq.Square.num_columns = 15

        self.delay = 500     # delay between two subsequent movements down [ms]
        self.paused = False
        self.is_game_over = False

        self.deleted_lines = 0                   # Raises level
        self.lines_text = tkinter.StringVar()    # Displayed in lines label
        self.lines_text.set("Deleted lines: 0")
        # Increased by points, affects delay and number of new points
        self.level = 1
        self.points = 0
        self.points_text = tkinter.StringVar()   # Displayed in points label
        self.points_text.set("Points: 0")

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
        self.is_game_over = False
        self.unbind_keys()
        self.pause()

        for shape in self.shapes_in_canvas:
            shape.delete()
        self.shapes_in_canvas.clear()

        self.active_shape = shp.Shape(random.choice(self.shape_types))
        self.next_shape_type = random.choice(self.shape_types)
        self.display_next_shape(self.next_shape_type)
        self.canvas.update()

        self.shapes_in_canvas = {self.active_shape}
        self.reset_points()
        self.time_step_cycle = None
        time.sleep(0.6)

        self.program.pause_button.config(state='normal')
        self.bind_keys()
        self.run()

    def game_over(self):
        self.pause()
        self.unbind_keys()
        self.program.pause_button.config(state='disabled')
        self.is_game_over = True

        self.images = []
        for i in range(8):
            filename = 'game_over_images/game_over_' + str(i) +'.png'
            self.images.append(tkinter.PhotoImage(file=filename))
        x = self.canvas_width // 2
        y = self.canvas_height // 2
        self.game_over_image = self.canvas.create_image(x, y,
                                                        image=self.images[0])
        self.canvas.update()
        self.game_over_change_phase(1)

    def game_over_change_phase(self, i):
        if self.is_game_over:
            self.canvas.itemconfig(self.game_over_image, image=self.images[i % 8])
            self.canvas.after(100, lambda: self.game_over_change_phase(i+1))
            self.canvas.update()
        else:
            self.canvas.delete(self.game_over_image)

    def bind_keys(self):
        for key in '<Left>', '<Right>', '<Up>', '<Down>', '<space>':
            self.canvas.bind_all(key, self.key_pressed)

    def unbind_keys(self):
        for key in '<Left>', '<Right>', '<Up>', '<Down>', '<space>':
            self.canvas.unbind_all(key)

    def time_step(self):
        if self.active_shape == None:
            # Erasing full lines. Keys are unbinded as it seems that pressing
            # a key while erasing lines can cause problems.
            self.unbind_keys()
            self.erase_full_lines()
            self.bind_keys()
            # Spawing new active shape
            self.active_shape = shp.Shape(self.next_shape_type)
            self.shapes_in_canvas.add(self.active_shape)
            # Choosing and displaying the next shape in the queue
            self.next_shape_type = random.choice(self.shape_types)
            self.display_next_shape(self.next_shape_type)
            # New active shape starts to fall
            if not self.active_shape.can_move('<down>', self.shapes_in_canvas):
                self.game_over()
            else:
                self.active_shape.move('<down>')
                self.call_next_time_step()
            return

        if self.active_shape.can_move('<down>', self.shapes_in_canvas):
            self.active_shape.move('<down>')
        else:
            self.active_shape = None
        self.call_next_time_step()

    def call_next_time_step(self):
        """Private method. Safely calles next time step, i.e. deletes another
        call if there is such present, in order to prevent double canvas.after
        cycle, which would increase the game speed."""

        if self.time_step_cycle is not None:
            self.canvas.after_cancel(self.time_step_cycle)
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
            # both due to time flow and pressing '<Down>' key.
            # After falling one block the timer restarts.
            self.canvas.after_cancel(self.time_step_cycle)
            self.active_shape.test_and_move('<down>', self.shapes_in_canvas)
            self.call_next_time_step()
        elif key == 'space':
            # Forces shape to immediately land
            self.canvas.after_cancel(self.time_step_cycle)
            while self.active_shape.can_move('<down>', self.shapes_in_canvas):
                self.active_shape.move('<down>')
            self.active_shape = None
            self.call_next_time_step()
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

        if not no_deleted_lines:
            return

        # Deleting all shapes containing no squares
        for shape in list(self.shapes_in_canvas):
            if len(shape.coords) == 0:
                self.shapes_in_canvas.discard(shape)

        # Add deleted lines, points, update level, etc.
        self.add_points(no_deleted_lines)

        # Falling of blocks
        # All shapes try to move down one after another until the situation
        # is not changed after two iterations
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

    def add_points(self, no_deleted_lines):
        """Updates number of deleted lines, points, level and increases game
        speed if needed."""

        self.deleted_lines += no_deleted_lines
        self.lines_text.set(f"Deleted lines: {self.deleted_lines}")

        factor = {1:40, 2:100, 3:300, 4:1200}
        self.points += factor[no_deleted_lines] * self.level
        self.points_text.set(f"Points: {self.points}")

        if self.deleted_lines % 10 == 0:
            self.level += 1
            self.delay = round(self.delay * 0.8)

    def reset_points(self):
        """Resets points, number of deleted lines, level and game speed.
        Used when game is reset."""

        self.deleted_lines = 0
        self.lines_text.set(f"Deleted lines: {self.deleted_lines}")

        self.points = 0
        self.points_text.set(f"Points: {self.points}")

        self.level = 1
        self.delay = 500

    def save(self, filename):
        with open(filename, 'w') as file:
            # Writing game stats
            file.write(str(self.points) + '\n')
            file.write(str(self.deleted_lines) + '\n')
            file.write(str(self.level) + '\n')
            file.write(str(self.delay) + '\n\n')

            # Writing next shape type
            file.write(self.next_shape_type + '\n\n')

            # Writing active shape info
            if self.active_shape is not None:
                file.write(self.active_shape.type + '\n')
                row, column = self.active_shape.rotation_center
                file.write(str(row) + ' ' + str(column) + '\n')
                for square in self.active_shape.squares:
                    file.write(str(square.row) + ' ' + str(square.column) +'\n')
            else:
                file.write("None" + '\n')
            file.write('\n\n')

            # Writing other shapes info
            for shape in self.shapes_in_canvas - {self.active_shape}:
                file.write(shape.type + '\n')
                for square in shape.squares:
                    file.write(str(square.row) + ' ' + str(square.column) +'\n')
                file.write('\n')

    def load(self, filename):
        # Game paused and keys unbinded by program object
        self.is_game_over = False

        for shape in self.shapes_in_canvas:
            shape.delete()
        self.shapes_in_canvas.clear()

        with open(filename) as file:
            # Loading game stats
            self.points = int(file.readline())
            self.points_text.set(f"Points: {self.points}")

            self.deleted_lines = int(file.readline())
            self.lines_text.set(f"Deleted lines: {self.deleted_lines}")

            self.level = int(file.readline())
            self.delay = int(file.readline())

            # Loading next shape type
            file.readline()
            self.next_shape_type = file.readline().strip()
            self.display_next_shape(self.next_shape_type)
            file.readline()

            # Loading active shape
            type = file.readline().strip()
            self.active_shape = shp.Shape(type, empty=True)
            color = self.active_shape.color

            row, column = file.readline().split()
            row = int(row)
            column = int(column)
            self.active_shape.rotation_center = [row, column]

            line = file.readline().strip()
            while line:
                row, column = line.split()
                row = int(row)
                column = int(column)
                self.active_shape.add_square(sq.Square(self.canvas,
                                                       row, column,
                                                       color))
                line = file.readline().strip()
            self.shapes_in_canvas = {self.active_shape}
            file.readline()

            # Loading other shapes
            while True:
                type = file.readline().strip()
                if not type:    # End of .tet file
                    break
                shape = shp.Shape(type, empty=True)
                color = shape.color
                self.shapes_in_canvas.add(shape)
                line = file.readline().strip()
                while line:
                    row, column = line.split()
                    row = int(row)
                    column = int(column)
                    shape.add_square(sq.Square(self.canvas,
                                               row, column,
                                               color))
                    line = file.readline().strip()

        self.canvas.update()
        self.time_step_cycle = None
        time.sleep(0.6)
