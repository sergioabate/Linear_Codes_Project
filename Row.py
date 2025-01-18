class Row:
    def __init__(self, elements: list[int | float] = None):
        self.elements = [] if elements is None else elements

    def __add__(self, other):
        # Row + Row
        if isinstance(other, Row):
            if len(self.elements) != len(other.elements):
                raise ValueError("Rows must have the same length to add.")
            return Row([a + b for a, b in zip(self.elements, other.elements)])
        # Row + numero
        elif isinstance(other, (int, float)):
            return Row([a + other for a in self.elements])
        # Una altra cosa
        return NotImplemented

    def __radd__(self, other): # això per quan fas <algo> + Row. Cal implementar per poder fer sum()
        # This method is called when the other operand is not a Row instance
        if isinstance(other, Row):
            return self + other  # Fer servir __add__
        elif other == 0:  # zero inicial a sum()
            return self
        return NotImplemented

    def __mul__(self, scalar: int | float) -> 'Row':
        return Row([scalar * element for element in self.elements])

    def __mod__(self, mod: int) -> 'Row':
        return Row([element % mod for element in self.elements])

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.elements[index]
        if isinstance(index, slice):
            return Row(self.elements[index])

    def __setitem__(self, index, value):
        self.elements[index] = value

    def __len__(self):
        return len(self.elements)

    def __str__(self):
        return f"[{' '.join(map(str, self.elements))}]"
    
    def __eq__(self, other) -> bool:
        """
        >>> r1=Row([1, 2, 3])
        >>> r2=Row([1, 2, 3])
        >>> r3=Row([1, 2, 4])
        >>> r4=Row([1, 2, 3, 4])
        >>> r1==r2
        True
        >>> r1==r3
        False
        >>> r1==r4
        False
        """
        if len(self) != len(other): 
            return False
        return all([a==b for a, b in zip(self.elements, other.elements)])
    
    def __bool__(self) -> bool:
        return any(e != 0 for e in self.elements)
    
    def __repr__(self):
        return self.__str__()
    
    def add_element(self, element):
        if isinstance(element, (int, float)):
            self.elements.append(element)
            return self
        if isinstance(element, Row):
            self.elements.extend(element.elements)
            return self
        if isinstance(element, list):
            self.elements.extend(element)
            return self
        raise ValueError(f"Invalid row element type {type(element)}")
