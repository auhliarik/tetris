class RowNumberOutOfLimitError(Exception): pass
class ColumnNumberOutOfLimitError(Exception): pass


class Square:
    """Class used to handle individual squares in the active area.
    This class is mainly used by 'Shape' class in module 'shape'."""

    x, y = 0, 0     # Upper left corner of the area, where squares should appear
    a = 30          # Size of squares
    no_rows = 20    # Number of rows for the whole class, does not include
                    # two hidden columns with number -1 and -2, where shapes
                    # spawn
    no_columns = 15 # Number of columns for the whole class
    canvas = None   # Canvas from tkinter module, in which squares are created

    def __init__(self, row, column, color):
        Square.test_row_and_column(row, column)
        self._row = row
        self._column = column
        self._color = color

        # Upper left and lower right corner of the square
        x0 = Square.x + self._column * Square.a
        y0 = Square.y + self._row * Square.a
        x1 = x0 + Square.a
        y1 = y0 + Square.a

        self._tag = Square.canvas.create_rectangle(x0, y0, x1, y1, fill=color)

    def move_to(self, row, column):
        """Safely moves square to another position determined by [row]
        and [column] - checks whether these are valid. Mainly used by
        row and column setters."""

        Square.test_row_and_column(row, column)
        self._row = row
        self._column = column

        # Upper left and lower right corner of the square
        x0 = Square.x + self._column * Square.a
        y0 = Square.y + self._row * Square.a
        x1 = x0 + Square.a
        y1 = y0 + Square.a

        Square.canvas.coords(self._tag, x0, y0, x1, y1)

    def delete(self):
        """Deletes square."""
        Square.canvas.delete(self._tag)

    def __str__(self):
        return "(" + str(self._row) + "," + str(self._column) + ")"

    __repr__ = __str__

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
        Square.canvas.itemconfig(self._tag, fill=color)

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, row):
        self.move_to(row, self._column)

    @property
    def column(self):
        return self._column

    @column.setter
    def column(self, column):
        self.move_to(self._row, column)

    @property
    def coords(self):
        return self._row, self._column

    @staticmethod
    def test_row_and_column(row, column):
        """Testing whether row and column numbers are valid.
        Raises exception if not."""
        no_rows = Square.no_rows
        no_columns = Square.no_columns
        # Negative row number is valid so that shapes could spawn in a hidden area
        if row < -2 :
            message = "Negative row numbers lower than -2 are not valid. "
            message += f"Got {row}"
            raise RowNumberOutOfLimitError(message)
        if row >= no_rows:
            message = f"Column number {row} is over the limit ({no_rows-1})"
            raise RowNumberOutOfLimitError(message)
        if column < 0 :
            message = f"Negative column numbers are not valid. Got {column}"
            raise ColumnNumberOutOfLimitError(message)
        if column >= no_columns:
            message = f"Column number {column} is over the limit ({no_columns-1})"
            raise ColumnNumberOutOfLimitError(message)
