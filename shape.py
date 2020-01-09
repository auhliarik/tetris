import square as sq
from square import RowNumberOutOfLimitError, ColumnNumberOutOfLimitError

class UnknownShapeTypeError(Exception): pass
class UnknownMovementDirectionErrror(Exception): pass


class Shape():
    """Class used to handle individual shapes in a game. See its methods for
    more information."""
    primary_canvas = None

    def __init__(self, type, i0=-1 , j0=6, canvas=None):
        self._type = type    # One of 'I', 'J', 'L', 'S', 'Z', 'O', 'T'
        if canvas is None:
            self._canvas = Shape.primary_canvas
        else:
            self._canvas = canvas

        # Individual shape types with important information about them
        # 'squares_coords' are spawning coordinates of shapes, dependent of
        # (i0, j0) - left lower corner of an 2x4 box, where they spawn.
        if self._type == 'I':
            squares_coords = [(i0,j0), (i0,j0+1), (i0,j0+2), (i0,j0+3)]
            rotation_center = [i0, j0+2]
            color = 'cyan'
        elif self._type == 'J':
            squares_coords = [(i0-1,j0), (i0,j0), (i0,j0+1), (i0,j0+2)]
            rotation_center = [i0, j0+1]
            color = 'blue'
        elif self._type == 'L':
            squares_coords = [(i0,j0), (i0,j0+1), (i0,j0+2), (i0-1,j0+2)]
            rotation_center = [i0, j0+1]
            color = 'orange'
        elif self._type == 'S':
            squares_coords = [(i0,j0), (i0,j0+1), (i0-1,j0+1), (i0-1,j0+2)]
            rotation_center = [i0-1, j0+1]
            color = 'green'
        elif self._type == 'Z':
            squares_coords = [(i0-1,j0), (i0-1,j0+1), (i0,j0+1), (i0,j0+2)]
            rotation_center = [i0-1, j0+1]
            color = 'red'
        elif self._type == 'O':
            squares_coords = [(i0,j0+1), (i0-1,j0+1), (i0,j0+2), (i0-1,j0+2)]
            rotation_center = [i0-1, j0+1]
            color = 'yellow'
        elif self._type == 'T':
            squares_coords = [(i0,j0), (i0,j0+1), (i0-1,j0+1), (i0,j0+2)]
            rotation_center = [i0, j0+1]
            color = 'magenta'
        else:
            message = f"Shape type '{self._type}' unknown."
            raise UnknownShapeTypeError(message)

        self._rotation_center = rotation_center # Needed only until shape locks
        self._squares = set()
        for i, j in squares_coords:
            self._squares.add(sq.Square(self._canvas, i, j, color))

    def is_at(self, row, column):
        """Returns boolean, whether one of the shape's squares is at postition
        ([row], [column]) or not."""

        for square in self._squares:
            if square.coords == (row, column):
                return True
        return False

    def can_move(self, where, all_shapes):
        """Does a check, wheter movement in a direction [where] is possible or
        not. Returns False in case of another object in the way or row/column
        number out of limit. Takes list of all shapes in the game as an
        argument."""

        if where == '<down>':
            row_dif = 1
            column_dif = 0
        elif where == '<left>':
            row_dif = 0
            column_dif = -1
        elif where == '<right>':
            row_dif = 0
            column_dif = 1
        else:
            message = f"Unknown movement direction {where}."
            raise UnknownMovementDirectionErrror(message)

        # Calling can_move_to function checks whether there is another shape
        # in the direction of movement and row and column numbers are valid.
        new_positions = Shape.shift_positions(self.coords, row_dif, column_dif)
        return self.can_move_to(new_positions, all_shapes)

    def move(self, where):
        """Moves a shape one block without checking if it is possible, i.e.
        without a check whether there is something in the direction of the move
        or whether new row and column numbers are valid."""

        if where == '<down>':
            row_diff = 1
            column_diff = 0
        elif where == '<left>':
            row_diff = 0
            column_diff = -1
        elif where == '<right>':
            row_diff = 0
            column_diff = 1
        else:
            message = f"Unknown movement direction {where}."
            raise UnknownMovementDirectionErrror(message)

        for square in self._squares:
            if row_diff != 0:
                square.row += row_diff
            if column_diff != 0:
                square.column += column_diff

        self._rotation_center[0] += row_diff
        self._rotation_center[1] += column_diff
        self._canvas.update()

    def test_and_move(self, where, all_shapes):
        """Combines 'can_move' and 'move' methods - firstly checks if the move
        is possible and if yes the move is performed."""


        if self.can_move(where, all_shapes):
            self.move(where)
            return True
        else:
            return False

    def test_and_rotate(self, all_shapes):
        """Tests, whether rotating a shape is possible and rotates it, if it is.
        Returns 'True', when rotation was successful and 'False' otherwise."""
        rc = self._rotation_center

        # New positions, which shape should occupy after rotation
        new_positions = []
        if self._type == 'I':
            # In-game rotation of 'I' shape is not a rotation in a ususal sense,
            # it is rather a change of vertical and horizontal position.
            # See Nintendo Rotation System for more information.
            i, j = rc
            if self.is_at(i, j-1):  # Shape in horizontal position
                new_positions.append((i-2,j))
                new_positions.append((i-1,j))
                new_positions.append((i,j))
                new_positions.append((i+1,j))
            else:
                new_positions.append((i,j-2))
                new_positions.append((i,j-1))
                new_positions.append((i,j))
                new_positions.append((i,j+1))
        elif self._type == 'O':
            # Rotating 'O' shape does not change anything.
            return True
        else:
            # Other shapes rotate in a 3x3 box
            positions = []
            for square in self._squares:
                positions.append(tuple(square.coords))
            new_positions = Shape.rotate_positions(positions, rc)

        # Checks if there is another shape in the direction of movement and if
        # row and column number are valid. In case one of the conditions is not
        # satisfied, wall kick is tried: rotation is tried after moving
        # the shape one block left/right.
        if not self.can_move_to(new_positions, all_shapes):
            new_positions = Shape.shift_positions(new_positions, 0, -1)
            self._rotation_center[1] += -1
            if not self.can_move_to(new_positions, all_shapes):
                new_positions = Shape.shift_positions(new_positions, 0, 2)
                self._rotation_center[1] += 2
                if not self.can_move_to(new_positions, all_shapes):
                    # As 'I' shape has different rotation system, in case of
                    # the wall on the left, moving 2 block to the right has to
                    # be tried as well.
                    if self._type == 'I':
                        new_positions = Shape.shift_positions(new_positions,
                                                              0, 1)
                        self._rotation_center[1] += 1
                        if not self.can_move_to(new_positions, all_shapes):
                            return False
                    else:
                        return False

        for i, square in enumerate(self._squares):
            square.move_to(*new_positions[i])
        self._canvas.update()
        return True

    def can_move_to(self, new_positions, all_shapes):
        if len(all_shapes) > 0:
            for row, column in new_positions:
                for shape in all_shapes - {self}:
                    if shape.is_at(row, column):
                        return False
                try:
                    sq.Square.test_row_and_column(row, column)
                except (RowNumberOutOfLimitError, ColumnNumberOutOfLimitError):
                    return False
        return True

    def delete_square_at(self, row, column):
        """Deletes square of a shape which is at position ([row], [column])."""

        for square in self._squares:
            if square.coords == (row, column):
                square.delete()
                self._squares.discard(square)
                break

    def __str__(self):
        res = self._type + ":\n"
        for square in self._squares:
            res += str(square) + '\n'
        return res

    __repr__ = __str__

    @property
    def squares(self):
        return self._squares

    @property
    def coords(self):
        coordinates = []
        for shape in self._squares:
            coordinates.append(tuple(shape.coords))
        return coordinates

    @staticmethod
    def shift_positions(positions, d_row, d_column):
        """Shifts all the positions - ([row], [column]) in the list 'positions'
        to ([row] + [d_row], [column] + [d_column]) """

        new_positions = []
        for row, column in positions:
            new_positions.append((row + d_row, column + d_column))
        return new_positions

    @staticmethod
    def rotate_positions(positions, center):
        """Rotates list of positions - (row, column) around a 'center' by 90
        degrees."""

        row = center[0]
        column = center[1]
        new_positions = []

        for i in -1, 0, 1:
            for j in -1, 0, 1:
                if (row + i, column + j) in positions:
                    new_positions.append((row + j, column - i))
        return new_positions
