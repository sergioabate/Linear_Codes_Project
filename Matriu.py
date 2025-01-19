from Row import Row

class Matriu:
    """
    Class to represent a Matrix composed of instances of the Row class

    It implements the basic operations: addition, subtraction, multiplication,
    and others such as changing rows/columns, transposing, etc.
    """
    def __init__(self, rows):
        """
        Create an instance of a matrix representation

        >>> Matriu([[1, 2, 3], [1, 2, 3]]).shape
        (2, 3)
        >>> Matriu([Row([1, 2, 3]), Row([1, 2, 3])]).shape
        (2, 3)
        """
        # Matriu que representa la instància.
        self.matrix: list[list[int]] = [Row(row) if not isinstance(row, Row) else row for row in rows]
        # Dimensions de la matriu, sent [0] nombre de files, i [1] nombre de columnes
        self.shape: tuple[int, int] = (len(self.matrix), len(self.matrix[0])) if self.matrix else (0, 0)

    def __repr__(self):
        """
        Representation of a matrix in list form

        >>> m = Matriu([[1, 2, 3], [4, 5, 6]])
        >>> repr(m)
        '[[1, 2, 3], [4, 5, 6]]'
        """
        return str([row.elements for row in self.matrix])

    def __add__(self, other: 'Matriu'):
        """
        Addition of two matrices

        :param other: Another matrix.
        :return: resulting matrix after apply the operation
        >>> m1 = Matriu([[1, 2, 3], [1, 2, 3]])
        >>> m2 = Matriu([[1, 2, 3], [1, 2, 3]])
        >>> m1 + m2
        [[2, 4, 6], [2, 4, 6]]
        """
        if self.shape != other.shape:
            raise ValueError("Les matrius han de tenir la mateixa mida per sumar-les")
        return Matriu([r1 + r2 for r1, r2 in zip(self.matrix, other.matrix)])

    def __sub__(self, other: 'Matriu'):
        """
        Substraction of two matrices

        :param other: Another matrix.
        :return: resulting matrix after apply the operation
        >>> m1 = Matriu([[1, 2, 3], [1, 2, 3]])
        >>> m2 = Matriu([[1, 2, 3], [1, 2, 3]])
        >>> m1 - m2
        [[0, 0, 0], [0, 0, 0]]
        """
        if self.shape != other.shape:
            raise ValueError("Les matrius han de tenir la mateixa mida per restar-les")
        return Matriu([r1 - r2 for r1, r2 in zip(self.matrix, other.matrix)])

    def __mul__(self, other: 'Matriu | float | int'):
        """
        Multiplication of two matrices

        :param other: Another matrix.
        :return: resulting matrix after apply the operation
        >>> m1 = Matriu([[1, 2, 3], [1, 2, 3]])
        >>> m2 = Matriu([[1, 2, 3], [1, 2, 3]])
        >>> m1 - m2
        [[0, 0, 0], [0, 0, 0]]
        """
        # Handle scalar multiplication
        if isinstance(other, (float, int)):
            return Matriu([row * other for row in self.matrix])

        # Handle matrix multiplication (dot product)
        if isinstance(other, Matriu):
            if self.shape[1] != other.shape[0]:
                raise ValueError(f"Mides de matrius incompatibles per multiplicació: {self.shape} i {other.shape}")

            # Transpose the other matrix for easier column access
            other_transposed = other.transpose()
            result = []
            for row in self.matrix:
                result_row = [sum(a * b for a, b in zip(row, col)) for col in other_transposed.matrix]
                result.append(Row(result_row))

            return Matriu(result)

    def __mod__(self, mod):
        """
        Apply the module operation to each element of the matrix

        :param mod: The module value to apply.
        :return: resulting matrix after applying the module operation.

        >>> m1 = Matriu([[1, 2, 3], [4, 5, 6]])
        >>> m1 % 2
        [[1, 0, 1], [0, 1, 0]]
        >>> m2 = Matriu([[7, 8, 9], [10, 11, 12]])
        >>> m2 % 3
        [[1, 2, 0], [1, 2, 0]]
        """
        return Matriu([row % mod for row in self.matrix])

    def __getitem__(self, index):
        """
        Access a row of the matrix by its index

        :param index: The index of the row to access.
        :return: The row at the specified index.

        >>> m1 = Matriu([[1, 2, 3], [4, 5, 6]])
        >>> m1[0]
        [1 2 3]
        >>> m1[1]
        [4 5 6]
        """
        return self.matrix[index]

    def __setitem__(self, index, value):
        """
        Set a row of the matrix at the specified index

        :param index: The index of the row to modify.
        :param value: The new value for the row.

        >>> m1 = Matriu([[1, 2, 3], [4, 5, 6]])
        >>> m1[0] = [7, 8, 9]
        >>> m1[0]
        [7, 8, 9]
        >>> m1[1] = [10, 11, 12]
        >>> m1[1]
        [10, 11, 12]
        """
        self.matrix[index] = value

    def __len__(self):
        """
        Return the number of rows in the matrix

        :return: The number of rows in the matrix

        >>> m1 = Matriu([[1, 2, 3], [4, 5, 6]])
        >>> len(m1)
        2
        >>> m2 = Matriu([[7, 8, 9]])
        >>> len(m2)
        1
        """
        return len(self.matrix)

    def __eq__(self, other: 'Matriu'):
        """
        Defines the equality relation between two matrices

        >>> Matriu([[1, 2, 3], [1, 2, 3]]) == Matriu([[1, 2, 3], [1, 2, 3]])
        True
        >>> Matriu([[1, 2, 3], [1, 2, 3]]) == Matriu([[1, 2, 3], [1, 2, 4]])
        False
        >>> Matriu.eye(2) == Matriu.eye(3)
        False
        >>> Matriu.eye(2) == Matriu.eye(2)
        True
        """
        if not isinstance(other, Matriu):
            return False

        if self.shape != other.shape:
            return False

        for row in range(self.shape[0]):
            if self[row] != other[row]:
                return False
        return True

    def __bool__(self) -> bool:
        """
        Return False if all elements in the matrix are 0, True otherwise.

        :return: True if at least one element in the matrix is non-zero, False otherwise.

        >>> m1 = Matriu([[0, 0, 0], [0, 0, 0]])
        >>> bool(m1)
        False
        >>> m2 = Matriu([[0, 0, 0], [0, 1, 0]])
        >>> bool(m2)
        True
        """
        for row in self:
            for element in row:
                if element:
                    return True
        return False

    def __iter__(self):
        """
        Iterate over the rows of the matrix.

        :return: Each row in the matrix.

        >>> m1 = Matriu([[1, 2, 3], [4, 5, 6]])
        >>> list(m1)
        [[1 2 3], [4 5 6]]
        >>> m2 = Matriu([[7, 8, 9]])
        >>> list(m2)
        [[7 8 9]]
        """
        for row in self.matrix:
            yield row

    def __str__(self):
        """
        Return a string representation of the matrix where each row is on a new line.

        :return: String representation of the matrix.
        """
        return "\n".join(str(row) for row in self.matrix)

    def transpose(self) -> 'Matriu':
        """
        Return the transpose of the matrix.

        :return: A new matrix that is the transpose of the current one.

        >>> m1 = Matriu([[1, 2, 3], [4, 5, 6]])
        >>> m1.transpose()
        [[1, 4], [2, 5], [3, 6]]
        >>> m2 = Matriu([[7, 8], [9, 10], [11, 12]])
        >>> m2.transpose()
        [[7, 9, 11], [8, 10, 12]]
        """

        transposed_rows = [[self.matrix[row_idx][col_idx] for row_idx in range(self.shape[0])]
                           for col_idx in range(self.shape[1])]
        return Matriu(transposed_rows)

    def swap_rows(self, row1: int, row2: int):
        """
        Swap two rows in the matrix.

        :param row1: Index of the first row.
        :param row2: Index of the second row.
        :raises IndexError: If row indices are out of bounds.

        >>> m1 = Matriu([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> m1.swap_rows(0, 2)
        >>> m1
        [[7, 8, 9], [4, 5, 6], [1, 2, 3]]
        >>> m2 = Matriu([[10, 20], [30, 40], [50, 60]])
        >>> m2.swap_rows(1, 2)
        >>> m2
        [[10, 20], [50, 60], [30, 40]]
        >>> m3 = Matriu([[1, 2], [3, 4]])
        >>> m3.swap_rows(0, 2)
        Traceback (most recent call last):
            ...
        IndexError: Index de fila fora de límits
        """
        if not (0 <= row1 < self.shape[0]) or not (0 <= row2 < self.shape[0]):
            raise IndexError("Index de fila fora de límits")
        self.matrix[row1], self.matrix[row2] = self.matrix[row2], self.matrix[row1]

    def remove_row(self, row: int) -> 'Matriu':
        """
        Removes a row at the specified position.

        :param row: Index of the row to remove.
        :raises IndexError: If the row index is out of bounds.
        :return: Resulting matrix
        >>> m1 = Matriu([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> m1.remove_row(1)
        [[1, 2, 3], [7, 8, 9]]
        >>> m2 = Matriu([[10, 20], [30, 40], [50, 60]])
        >>> m2.remove_row(0)
        [[30, 40], [50, 60]]
        >>> m3 = Matriu([[1, 2], [3, 4]])
        >>> m3.remove_row(2)
        Traceback (most recent call last):
            ...
        IndexError: Index de fila fora de límits
        """
        if not (0 <= row < self.shape[0]):
            raise IndexError("Index de fila fora de límits")
        self.matrix.pop(row)
        self.shape = (self.shape[0]-1, self.shape[1])
        return self

    def add_row(self, row: Row, pos: int = -1) -> 'Matriu':
        """
        Adds a new row to the matrix at the specified position.
        If no position is provided, the row is added at the end.

        :param row: Row to add.
        :param pos: Position to insert the row. Defaults to -1 (append at the end).
        :raises ValueError: If the row is not of type "Row".
        :raises IndexError: If the position is out of bounds.
        :return: Resulting matrix

        >>> m1 = Matriu([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> m1.add_row(Row([10, 11, 12]))
        [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]

        >>> m2 = Matriu([[1, 2], [3, 4], [5, 6]])
        >>> m2.add_row(Row([7, 8]), pos=1)
        [[1, 2], [7, 8], [3, 4], [5, 6]]
        >>> m3 = Matriu([[1, 2], [3, 4]])
        >>> m3.add_row([5, 6])
        Traceback (most recent call last):
            ...
        ValueError: Invalid row type
        >>> m4 = Matriu([[1, 2], [3, 4], [5, 6]])
        >>> m4.add_row(Row([7, 8]), pos=5)
        Traceback (most recent call last):
            ...
        IndexError: Index de fila fora de límits
        """
        if not isinstance(row, Row):
            raise ValueError("Invalid row type")

        if pos == -1:
            self.matrix.append(row)
            self.shape = (self.shape[0]+1, self.shape[1])
            return self

        if not (0 <= pos < self.shape[0]):
            raise IndexError("Index de fila fora de límits")

        self.matrix.append([])
        for row_pos in range(self.shape[0]-1, pos-1, -1):
            self.matrix[row_pos+1] = self.matrix[row_pos]
        self.matrix[pos] = row
        self.shape = (self.shape[0]+1, self.shape[1])
        return self

    def add_column(self, column: Row) -> 'Matriu':
        """
        Adds a new column to the matrix.

        :param column: Column to add, must be of type "Row".
        :raises ValueError: If the column is not of type "Row" or if the column size is invalid.
        :return: Resulting matrix
        >>> m1 = Matriu([[1, 2], [3, 4], [5, 6]])
        >>> m1.add_column(Row([7, 8, 9]))
        [[1, 2, 7], [3, 4, 8], [5, 6, 9]]
        >>> m2 = Matriu([[1, 2], [3, 4]])
        >>> m2.add_column(Row([5, 6]))
        [[1, 2, 5], [3, 4, 6]]
        >>> m3 = Matriu([[1, 2], [3, 4]])
        >>> m3.add_column(Row([10, 11]))
        [[1, 2, 10], [3, 4, 11]]
        """
        if not isinstance(column, Row):
            raise ValueError("Tipus de columna invàlid. Ha de ser de tipus Row (tot i no ser lògic)")
        if len(column) != self.shape[0]:
            raise ValueError("Mida de columna invàlida")

        for row in range(self.shape[0]):
            self[row].add_element(column[row])
        self.shape = (self.shape[0], self.shape[1]+1)

        return self

    def get_column(self, column: int) -> 'Row':
        """
        Returns a column from the matrix as a `Row` object.

        :param column: The index of the column to retrieve.
        :raises IndexError: If the column index is out of bounds.
        :return: The Row resulting from the corresponding column
        >>> m1 = Matriu([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> m1.get_column(1)
        [2 5 8]
        >>> m2 = Matriu([[1, 2], [3, 4]])
        >>> m2.get_column(0)
        [1 3]
        >>> m3 = Matriu([[1, 2], [3, 4]])
        >>> m3.get_column(3)
        Traceback (most recent call last):
            ...
        IndexError: Index de columna fora de límits
        """
        if not (0 <= column < self.shape[1]):
            raise IndexError("Index de columna fora de límits")

        r = Row()
        for row in self:
            r.add_element(row[column])
        return r

    def get_columns(self, columns: list[int] | tuple[int]) -> list[Row]:
        """
        Returns multiple columns from the matrix as a list of `Row` objects.

        :param columns: A list or tuple containing the indices of the columns to retrieve.
        :raises IndexError: If any column index is out of bounds.
        :return: The Rows list resulting from the corresponding columns
        >>> m1 = Matriu([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> m1.get_columns([0, 2])
        [[1 4 7], [3 6 9]]
        >>> m2 = Matriu([[1, 2], [3, 4], [5, 6]])
        >>> m2.get_columns((0, 1))
        [[1 3 5], [2 4 6]]
        >>> m3 = Matriu([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> m3.get_columns([1, 3])
        Traceback (most recent call last):
            ...
        IndexError: Index de columna fora de límits
        """
        result = []
        for col in columns:
            result.append(self.get_column(col))
        return result

    def get_row(self, row: int) -> 'Row':
        """
        Returns a row from the matrix as a `Row` object.

        :param row: The index of the row to retrieve.
        :raises IndexError: If the row index is out of bounds.
        :return: The Rows resulting
        >>> m1 = Matriu([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> m1.get_row(1)
        [4 5 6]
        >>> m2 = Matriu([[1, 2], [3, 4], [5, 6]])
        >>> m2.get_row(2)
        [5 6]
        >>> m3 = Matriu([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> m3.get_row(3)
        Traceback (most recent call last):
            ...
        IndexError: Index de fila fora de límits
        """
        if not (0 <= row < self.shape[0]):
            raise IndexError("Index de fila fora de límits")

        return self[row]

    def get_rows(self, rows: list[int] | tuple[int]) -> list[Row]:
        """
        Returns multiple rows from the matrix as a list of `Row` objects.

        :param rows: A list or tuple containing the indices of the rows to retrieve.
        :raises IndexError: If any row index is out of bounds.
        :return: A list of corresponding Rows
        >>> m1 = Matriu([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> m1.get_rows([0, 2])
        [[1 2 3], [7 8 9]]
        >>> m2 = Matriu([[1, 2], [3, 4], [5, 6]])
        >>> m2.get_rows((0, 1))
        [[1 2], [3 4]]
        >>> m3 = Matriu([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> m3.get_rows([1, 3])
        Traceback (most recent call last):
            ...
        IndexError: Index de fila fora de límits
        """
        result = []
        for row in rows:
            result.append(self.get_row(row))
        return result

    def hstack(self, other: 'Matriu') -> 'Matriu':
        """
        Horizontally stacks two matrices (i.e., appends columns of the second matrix to the first matrix).

        :param other: Another matrix to stack horizontally with the current one.
        :raises TypeError: If the `other` parameter is not an instance of `Matriu`.
        :raises ValueError: If the number of rows in the matrices are not the same.
        :return: A new matrix resulting from the horizontal stack.
        >>> m1 = Matriu([[1, 2, 3], [4, 5, 6]])
        >>> m2 = Matriu([[7, 8], [9, 10]])
        >>> m1.hstack(m2)
        [[1, 2, 3, 7, 8], [4, 5, 6, 9, 10]]
        >>> m3 = Matriu([[1, 2], [3, 4], [5, 6]])
        >>> m4 = Matriu([[7, 8], [9, 10], [11, 12]])
        >>> m3.hstack(m4)
        [[1, 2, 7, 8], [3, 4, 9, 10], [5, 6, 11, 12]]
        >>> m5 = Matriu([[1, 2, 3], [4, 5, 6]])
        >>> m6 = Matriu([[7, 8]])
        >>> m5.hstack(m6)
        Traceback (most recent call last):
            ...
        ValueError: El nombre de files de les matrius no són iguals
        """
        if not isinstance(other, Matriu):
            raise TypeError("Tipus de matriu invàlida")
        if self.shape[0] != other.shape[0]:
            raise ValueError("El nombre de files de les matrius no són iguals")

        M = Matriu(self.matrix)
        for row in range(self.shape[0]):
            M[row].add_element(other[row])

        M.shape = (M.shape[0], M.shape[1]+other.shape[1])
        return M

    def vstack(self, other: 'Matriu') -> 'Matriu':
        """
        Vertically stacks two matrices (i.e., appends rows of the second matrix to the first matrix).

        :param other: Another matrix to stack vertically with the current one.
        :raises TypeError: If the `other` parameter is not an instance of `Matriu`.
        :raises ValueError: If the number of columns in the matrices are not the same.
        :return: A new matrix resulting from the vertical stack.

        >>> m1 = Matriu([[1, 2, 3], [4, 5, 6]])
        >>> m2 = Matriu([[7, 8, 9], [10, 11, 12]])
        >>> m1.vstack(m2)
        [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]
        >>> m3 = Matriu([[1, 2], [3, 4], [5, 6]])
        >>> m4 = Matriu([[7, 8], [9, 10], [11, 12]])
        >>> m3.vstack(m4)
        [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]]
        >>> m5 = Matriu([[1, 2, 3], [4, 5, 6]])
        >>> m6 = Matriu([[7, 8]])
        >>> m5.vstack(m6)
        Traceback (most recent call last):
            ...
        ValueError: El nombre de columnes de les matrius no són iguals
        """
        if not isinstance(other, Matriu):
            raise TypeError("Tipus de matriu invàlida")
        if self.shape[1] != other.shape[1]:
            raise ValueError("El nombre de columnes de les matrius no són iguals")

        M = Matriu(self.matrix)
        for row in range(self.shape[0]):
            M.add_row(other[row])
        M.shape = (M.shape[0]+other.shape[0], M.shape[1])
        return M

    def split(self, rows: slice, columns: slice) -> 'Matriu':
        """
        Splits the matrix into a submatrix defined by the given row and column slices.

        :param rows: A slice defining the rows to select.
        :param columns: A slice defining the columns to select.
        :return: A new matrix that is a submatrix of the original one.

        >>> m1 = Matriu([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> m1.split(slice(0, 2), slice(0, 2))
        [[1, 2], [4, 5]]
        >>> m2 = Matriu([[10, 11, 12, 13], [14, 15, 16, 17], [18, 19, 20, 21]])
        >>> m2.split(slice(1, 3), slice(2, 4))
        [[16, 17], [20, 21]]
        >>> m3 = Matriu([[1, 2, 3], [4, 5, 6]])
        >>> m3.split(slice(0, 1), slice(1, 2))
        [[2]]
        """
        return Matriu([row[columns] for row in self.matrix[rows]])

    # Classe "estàtica" de Matriu. S'utilitza Matriu.eye(N)
    # per executar-la, sense crear una instància amb Matriu()
    @classmethod
    def eye(self, N: int) -> 'Matriu':
        """
        Creates an identity matrix of size N x N.

        :param N: The size of the identity matrix.
        :return: An identity matrix of size N x N.

        >>> Matriu.eye(3)
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        >>> Matriu.eye(4)
        [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        >>> Matriu.eye(2)
        [[1, 0], [0, 1]]
        """
        return self([[1 if i == j else 0 for j in range(N)] for i in range(N)])

    @classmethod
    def ones(self, N: int, M: int = None) -> 'Matriu':
        """
        Creates a matrix filled with ones of size N x M (default square matrix).

        :param N: The number of rows.
        :param M: The number of columns (optional, defaults to N for a square matrix).
        :return: A matrix of size N x M filled with ones.

        >>> Matriu.ones(3)
        [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
        >>> Matriu.ones(2, 4)
        [[1, 1, 1, 1], [1, 1, 1, 1]]
        >>> Matriu.ones(1, 5)
        [[1, 1, 1, 1, 1]]
        >>> Matriu.ones(4, 2)
        [[1, 1], [1, 1], [1, 1], [1, 1]]
        """
        if M is None:
            M = N
        return self([[1 for j in range(M)] for i in range(N)])

    @classmethod
    def zeros(self, N: int, M: int = None) -> 'Matriu':
        """
        Creates a matrix filled with zeros of size N x M (default square matrix).

        :param N: The number of rows.
        :param M: The number of columns (optional, defaults to N for a square matrix).
        :return: A matrix of size N x M filled with zeros.

        >>> Matriu.zeros(3)
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

        >>> Matriu.zeros(2, 4)
        [[0, 0, 0, 0], [0, 0, 0, 0]]

        >>> Matriu.zeros(1, 5)
        [[0, 0, 0, 0, 0]]

        >>> Matriu.zeros(4, 2)
        [[0, 0], [0, 0], [0, 0], [0, 0]]
        """
        if M is None:
            M = N
        return self([[0 for j in range(M)] for i in range(N)])
