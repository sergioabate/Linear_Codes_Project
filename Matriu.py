from Row import Row

class Matriu:
    def __init__(self, rows):
        """
        Crea una instància de Matriu
        
        >>> Matriu([[1, 2, 3], [1, 2, 3]]).shape
        (2, 3)
        >>> Matriu([Row([1, 2, 3]), Row([1, 2, 3])]).shape
        (2, 3)
        """
        self.matrix = [Row(row) if not isinstance(row, Row) else row for row in rows]
        self.shape = (len(self.matrix), len(self.matrix[0])) if self.matrix else (0, 0)

    def __add__(self, other: 'Matriu'):
        if self.shape != other.shape:
            raise ValueError("Matrices must have the same shape to add.")
        return Matriu([r1 + r2 for r1, r2 in zip(self.matrix, other.matrix)])

    def __mul__(self, other: 'Matriu | float | int'):
        # Handle scalar multiplication
        if isinstance(other, (float, int)):
            return Matriu([row * other for row in self.matrix])

        # Handle matrix multiplication (dot product)
        if isinstance(other, Matriu):
            if self.shape[1] != other.shape[0]:
                raise ValueError(f"Incompatible shapes for matrix multiplication: {self.shape} and {other.shape}")
            
            # Transpose the other matrix for easier column access
            other_transposed = other.transpose()
            result = []
            for row in self.matrix:
                result_row = [sum(a * b for a, b in zip(row, col)) for col in other_transposed.matrix]
                result.append(Row(result_row))
                
            return Matriu(result)
            
    def __mod__(self, mod):
        return Matriu([row % mod for row in self.matrix])
    
    def __getitem__(self, index):
        return self.matrix[index]

    def __setitem__(self, index, value):
        self.matrix[index] = value

    def __len__(self):
        return len(self.matrix)

    def __eq__(self, other: 'Matriu'):
        """
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
        for row in self:
            for element in row:
                if element:
                    return True
        return False

    def __iter__(self):
        for row in self.matrix:
            yield row

    def __str__(self):
        return "\n".join(str(row) for row in self.matrix)

    def transpose(self):
        transposed_rows = [[self.matrix[row_idx][col_idx] for row_idx in range(self.shape[0])]
                           for col_idx in range(self.shape[1])]
        return Matriu(transposed_rows)

    def swap_rows(self, row1: int, row2: int):
        if not (0 <= row1 < self.shape[0]) or not (0 <= row2 < self.shape[0]):
            raise IndexError("Row index out of bounds.")
        self.matrix[row1], self.matrix[row2] = self.matrix[row2], self.matrix[row1]

    def remove_row(self, row: int) -> 'Matriu':
        """
        Elimina una fila a la posició especificada
        L'eliminiació és `inplace`, es modifica la instància
        """
        if not (0 <= row < self.shape[0]):
            raise IndexError("Row index out of bounds.")
        self.matrix.pop(row)
        self.shape = (self.shape[0]-1, self.shape[1])
        return self

    def add_row(self, row: Row, pos: int = -1) -> 'Matriu':
        """
        Afegeix una fila a la posició especificada,
        al final si no.
        En cas d'especificar posició, les files amb índex > pos
        es desplaçaran cap avall.
        L'afegiment és `inplace`, es modifica la instància
        """
        if not isinstance(row, Row):
            raise ValueError("Invalid row type")
        
        if pos == -1:
            self.matrix.append(row)
            self.shape = (self.shape[0]+1, self.shape[1])
            return self
        
        if not (0 <= pos < self.shape[0]):
            raise IndexError("Row index out of bounds.")
        
        self.matrix.append([])
        for row_pos in range(self.shape[0]-1, pos-1, -1):
            self.matrix[row_pos+1] = self.matrix[row_pos]
        self.matrix[pos] = row
        self.shape = (self.shape[0]+1, self.shape[1])
        return self
    
    def add_column(self, column: Row) -> 'Matriu':
        if not isinstance(column, Row):
            raise ValueError("Invalid column type (should be Row despite making no sense)")
        if len(column) != self.shape[0]:
            raise ValueError("Invalid length of column")
        
        for row in range(self.shape[0]):
            self[row].add_element(column[row])
        self.shape = (self.shape[0], self.shape[1]+1)
        
        return self
    
    def get_column(self, column: int) -> 'Row':
        if not (0 <= column < self.shape[1]):
            raise IndexError("Column index out of bounds.")
        
        r = Row()
        for row in self:
            r.add_element(row[column])
        return r
    
    def get_columns(self, columns: list[int] | tuple[int]) -> list[Row]:
        result = []
        for col in columns:
            result.append(self.get_column(col))
        return result
    
    def get_row(self, row: int) -> 'Row':
        if not (0 <= row < self.shape[1]):
            raise IndexError("Row index out of bounds.")
        
        return self[row]
    
    def get_rows(self, rows: list[int] | tuple[int]) -> list[Row]:
        result = []
        for row in rows:
            result.append(self.get_row(row))
        return result
        
    def hstack(self, other: 'Matriu') -> 'Matriu':
        """
        Ajunta horitzontalment la matriu `self` amb `other`.
        Resultant amb M = (self | other).
        Ambdues han de tenir el mateix nombre de files
        """
        if not isinstance(other, Matriu):
            raise TypeError("Invalid matrix type")
        if self.shape[0] != other.shape[0]:
            raise ValueError("Number of rows of matrices do not match")
        
        M = Matriu(self.matrix)
        for row in range(self.shape[0]):
            M[row].add_element(other[row])
            
        M.shape = (M.shape[0], M.shape[1]+other.shape[1])
        return M
    
    def vstack(self, other: 'Matriu') -> 'Matriu':
        """
        Ajunta horitzontalment la matriu `self` amb `other`.
        Resultant amb M = (self).
                          (----)
                          (other)  
        Ambdues han de tenir el mateix nombre de columnes
        """
        if not isinstance(other, Matriu):
            raise TypeError("Invalid matrix type")
        if self.shape[1] != other.shape[1]:
            raise ValueError("Number of columns of matrices do not match")
        
        M = Matriu(self.matrix)
        for row in range(self.shape[0]):
            M.add_row(other[row])
        M.shape = (M.shape[0]+other.shape[0], M.shape[1])
        return M

    def split(self, rows: slice, columns: slice) -> 'Matriu':
        return Matriu([row[columns] for row in self.matrix[rows]])

    # Classe "estàtica" de Matriu. S'utilitza Matriu.eye(N) 
    # per executar-la, sense crear una instància amb Matriu()
    @classmethod
    def eye(self, N: int) -> 'Matriu':
        return self([[1 if i == j else 0 for j in range(N)] for i in range(N)])
    
    @classmethod
    def ones(self, N: int, M: int = None) -> 'Matriu':
        if M is None:
            M = N
        return self([[1 for j in range(M)] for i in range(N)])
    
    @classmethod
    def zeros(self, N: int, M: int = None) -> 'Matriu':
        if M is None:
            M = N
        return self([[0 for j in range(M)] for i in range(N)])