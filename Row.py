class Row:
    """
    Class to represent a row of numbers (float or integer)

    Implements basic row operations: addition/subtraction,
    scalar multiplication, modular and boolean operations, etc.
    """

    def __init__(self, elements: list[int | float] = None):
        """
        Initialize a row instance with the given elements. If none are given, the row is empty.

        :param elements: List of integers or floats of a row (opcional).
        >>> r = Row([1, 2, 3])
        >>> r.elements
        [1, 2, 3]
        >>> r = Row()
        >>> r.elements
        []
        """
        self.elements = [] if elements is None else elements

    def __add__(self, other):
        """
        Add two rows, or add a number to each element of a row

        :param other: Another row or number.
        :return: Resulting row after applying the operation.
        >>> r1 = Row([1, 2, 3])
        >>> r2 = Row([4, 5, 6])
        >>> r1 + r2
        [5 7 9]
        >>> r1 + 2
        [3 4 5]
        """
        if isinstance(other, Row):
            if len(self.elements) != len(other.elements):
                raise ValueError("Rows must have the same length")
            return Row([a + b for a, b in zip(self.elements, other.elements)])
        elif isinstance(other, (int, float)):
            return Row([a + other for a in self.elements])
        return NotImplemented

    def __sub__(self, other):
        """
        Add two rows, or add a number to each element of a row

        :param other: Another row or number.
        :return: Resulting row after applying the operation.
        >>> r1 = Row([1, 2, 3])
        >>> r2 = Row([4, 5, 6])
        >>> r1 + r2
        [5 7 9]
        >>> r1 + 2
        [3 4 5]
        """
        if isinstance(other, Row):
            if len(self.elements) != len(other.elements):
                raise ValueError("Rows must have the same length")
            return Row([a - b for a, b in zip(self.elements, other.elements)])
        elif isinstance(other, (int, float)):
            return Row([a - other for a in self.elements])
        return NotImplemented

    def __radd__(self, other):
        """
        Allows right side addition (<element> + Row)
        Needed to use sum(Row)

        :param other: The other operand
        >>> r = Row([1, 2, 3])
        >>> sum([r, r])
        [2 4 6]
        """
        if isinstance(other, Row):
            return self + other
        elif other == 0:
            return self
        return NotImplemented

    def __mul__(self, scalar: int | float) -> 'Row':
        """
        Multiply each element of the row by a number.

        :param scalar: Number to multiply.
        :return: New row after the operation.
        >>> r = Row([1, 2, 3])
        >>> r * 2
        [2 4 6]
        """
        return Row([scalar * element for element in self.elements])

    def __mod__(self, mod: int) -> 'Row':
        """
        Apply the modulus operation to each element of the row.

        :param mod: Modulus value.
        :return: New row after the operation.
        >>> r = Row([10, 15, 20])
        >>> r % 6
        [4 3 2]
        """
        return Row([element % mod for element in self.elements])

    def __getitem__(self, index):
        """
        Allows accessing a specified element, or a slice of the row.

        :param index: Index or slice.
        :return: Element or row obtained
        >>> r = Row([1, 2, 3, 4])
        >>> r[1]
        2
        >>> r[1:3]
        [2 3]
        """
        if isinstance(index, int):
            return self.elements[index]
        if isinstance(index, slice):
            return Row(self.elements[index])

    def __setitem__(self, index, value):
        """
        Assigna a value to a given Row's element

        :param index: Index of the element.
        :param value: New value.
        >>> r = Row([1, 2, 3])
        >>> r[1] = 5
        >>> r
        [1 5 3]
        """
        self.elements[index] = value

    def __len__(self) -> int:
        """
        Obtain the length of the Row

        :return: Length of the row
        >>> r = Row([1, 2, 3])
        >>> len(r)
        3
        """
        return len(self.elements)

    def __str__(self) -> str:
        """
        Representation of the row

        :return: String with the Row's elements.
        >>> r = Row([1, 2, 3])
        >>> str(r)
        '[1 2 3]'
        """
        return f"[{' '.join(map(str, self.elements))}]"

    def __eq__(self, other) -> bool:
        """
        Compare whether two rows are equal.

        :param other: The other row to compare with.
        :return: True if both are equal, False otherwise.
        >>> r1 = Row([1, 2, 3])
        >>> r2 = Row([1, 2, 3])
        >>> r3 = Row([1, 2, 4])
        >>> r1 == r2
        True
        >>> r1 == r3
        False
        """
        if len(self) != len(other):
            return False
        return all([a==b for a, b in zip(self.elements, other.elements)])

    def __bool__(self) -> bool:
        """
        Return whether any element of the Row is different to 0.

        :return: True si any element is non-zero, False otherwise.
        >>> r1 = Row([0, 0, 0])
        >>> bool(r1)
        False
        >>> r2 = Row([1, 0, 0])
        >>> bool(r2)
        True
        """
        return any(e != 0 for e in self.elements)

    def __repr__(self):
        """
        Representation of the row (same as str()).

        >>> r = Row([1, 2, 3])
        >>> repr(r)
        '[1 2 3]'
        """
        return self.__str__()

    def add_element(self, element):
        """
        Add an element or a list of elements to the row.

        :param element: Element, list or Row to be added.
        >>> r = Row([1, 2])
        >>> r.add_element(3)
        [1 2 3]
        >>> r.add_element([4, 5])
        [1 2 3 4 5]
        >>> r.add_element(Row([6]))
        [1 2 3 4 5 6]
        """
        # Si es vol afegir un número (real o enter)
        if isinstance(element, (int, float)):
            self.elements.append(element)
            return self
        # Si es vol afegir una altra Row, s'afegeixen els elements al final
        if isinstance(element, Row):
            self.elements.extend(element.elements)
            return self
        # Si es vol afegir una llista, s'afegeixen els elements al final
        if isinstance(element, list):
            self.elements.extend(element)
            return self
        raise ValueError(f"Element type of Row not valid: {type(element)}")

    def del_element(self, element):
        """
        Delete an element or a list of elements to the row.

        :param element: Element, list or Row to be added.
        >>> r = Row([1, 2])
        >>> r.add_element(3)
        [1 2 3]
        >>> r.add_element([4, 5])
        [1 2 3 4 5]
        >>> r.add_element(Row([6]))
        [1 2 3 4 5 6]
        """
        # Si es vol afegir un número (real o enter)
        if isinstance(element, (int, float)):
            self.elements.append(element)
            return self
        # Si es vol afegir una altra Row, s'afegeixen els elements al final
        if isinstance(element, Row):
            self.elements.extend(element.elements)
            return self
        # Si es vol afegir una llista, s'afegeixen els elements al final
        if isinstance(element, list):
            self.elements.extend(element)
            return self
        raise ValueError(f"Element type of Row not valid: {type(element)}")
