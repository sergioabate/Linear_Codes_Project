class Row:
    """
    Classe per representar una fila (row) de números (reals o enters)

    Implementa funcionalitats bàsiques per operar amb files:
    sumar/restar, multiplicar per un escalar, operacións modulars, booleanes...
    """

    def __init__(self, elements: list[int | float] = None):
        """
        Inicialitza una fila amb els elements donats. Si no s'especifiquen, la fila estarà buida.

        :param elements: Llista d'enters o floats de la fila (opcional).
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
        Suma dues files o suma un número a cada element de la fila.

        :param other: Una altra fila o un número.
        :return: Nova fila resultant de la suma.
        >>> r1 = Row([1, 2, 3])
        >>> r2 = Row([4, 5, 6])
        >>> r1 + r2
        [5 7 9]
        >>> r1 + 2
        [3 4 5]
        """
        if isinstance(other, Row):
            if len(self.elements) != len(other.elements):
                raise ValueError("Les files han de tenir la mateixa longitud per sumar.")
            return Row([a + b for a, b in zip(self.elements, other.elements)])
        elif isinstance(other, (int, float)):
            return Row([a + other for a in self.elements])
        return NotImplemented

    def __radd__(self, other):
        """
        Permet sumar un altre element més una instància de Row. 
        Necessària per utilitzar sum(Row)

        :param other: L'altre operand (pot ser 0 o un número).
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
        Multiplica cada element de la fila per un escalar.

        :param scalar: Escalar (int o float).
        :return: Nova fila resultant.
        >>> r = Row([1, 2, 3])
        >>> r * 2
        [2 4 6]
        """
        return Row([scalar * element for element in self.elements])

    def __mod__(self, mod: int) -> 'Row':
        """
        Aplica l'operador mòdul a cada element de la fila.

        :param mod: Valor del mòdul.
        :return: Nova fila amb els residus.
        >>> r = Row([10, 15, 20])
        >>> r % 6
        [4 3 2]
        """
        return Row([element % mod for element in self.elements])

    def __getitem__(self, index):
        """
        Permet accedir a un element específic o a un subconjunt de la fila (slice).

        :param index: Índex o slice.
        :return: Element o fila obintgut
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
        Assigna un valor a un element específic de la fila.

        :param index: Índex de l'element.
        :param value: Valor a assignar.
        >>> r = Row([1, 2, 3])
        >>> r[1] = 5
        >>> r
        [1 5 3]
        """
        self.elements[index] = value

    def __len__(self):
        """
        Retorna la longitud de la fila.

        :return: Longitud de la fila.
        >>> r = Row([1, 2, 3])
        >>> len(r)
        3
        """
        return len(self.elements)

    def __str__(self):
        """
        Retorna una representació de la fila

        :return: String amb els elements de la fila.
        >>> r = Row([1, 2, 3])
        >>> str(r)
        '[1 2 3]'
        """
        return f"[{' '.join(map(str, self.elements))}]"
    
    def __eq__(self, other) -> bool:
        """
        Compara si dues files són iguals.

        :param other: La fila amb qui comparar.
        :return: True si són iguals, False si no.
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
        Retorna si algun element de la fila és diferent de 0.

        :return: True si algun element no és zero, False si no.
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
        Retorna la representació de la fila (igual a str()).

        >>> r = Row([1, 2, 3])
        >>> repr(r)
        '[1 2 3]'
        """
        return self.__str__()
    
    def add_element(self, element):
        """
        Afegeix un element o una llista d'elements a la fila.

        :param element: Element, llista o fila a afegir.
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
        raise ValueError(f"Tipus d'element de la fila no vàlid: {type(element)}")