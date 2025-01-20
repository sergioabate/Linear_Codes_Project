from dataclasses import dataclass
from typing import Generator
from itertools import combinations

from Row import Row
from Matriu import Matriu

import itertools

@dataclass
class LinearCode:
    """
    Class to represent a Linear Code, consisting of the
    generator matrix G, the control matrix H, and the code parameters.

    It implements methods to get all code elements, split messages into blocks,
    compress parameters, encode, decode and detect errors, and decode and correct errors.
    """
    G: Matriu = None
    H: Matriu = None

    n: int = None
    k: int = None
    M: int = None
    d: int = None

    # Només es generaran si són necessaris (decodificar)
    code_elements: dict[str:str] = None

    def get_code_elements(self) -> dict[str,str]:
        """
        Generates and returns a dictionary corresponding to the code elements (codewords) of the linear code.

        The code elements are calculated using the generator matrix G and
        the possible message blocks. The first time the method is called,
        it computes the code elements and stores them for later use.

        He stores them like this:
        decoded         | coded
        '[0 0 0 0 0 0]'   (0, 0)

        :return: A dictionary where the keys are the code elements (as strings)
                and the values are the corresponding message blocks.

        >>> m1 = Matriu([[0,1,1,1,0,0],[0,1,1,0,1,1]])
        >>> m2 = Matriu([[0,1,0,1,1,0], [1,0,0,0,1,1], [0,1,1,0,1,1], [0,0,0,0,1,1]])
        >>> lincode = LinearCode()
        >>> lincode.G = m1
        >>> lincode.H = m2
        >>> lincode.n = 6
        >>> lincode.k = 2
        >>> lincode.M = 4
        >>> lincode.d = 3
        >>> elements = lincode.get_code_elements()
        >>> print(elements)
        {'[0 0 0 0 0 0]': (0, 0), '[0 1 1 0 1 1]': (0, 1), '[0 1 1 1 0 0]': (1, 0), '[0 0 0 1 1 1]': (1, 1)}
        """
        # Generem els codis únicament la primera vegada
        if self.code_elements is not None:
            return self.code_elements

        blocs = list(itertools.product([0, 1], repeat = self.k))
        elements = {}

        for bloc in blocs:
            bloc_matrix = Matriu([list(bloc)])
            code_element = bloc_matrix * self.G % 2
            elements[str(code_element)] = bloc

        self.code_elements = elements

        return elements

    def _split_bits_in_blocks(self, bits: list[int], size: int) -> Generator[Matriu, None, None]:
        """
        Splits a list of bits into blocks of a specified size.

        This method raises a ValueError if the length of the bits is not divisible by the block size.

        :param bits: List of bits to be split into blocks.
        :param size: The size of each block.
        :return: A generator that yields Matriu instances, each containing a block of bits.

        >>> code = LinearCode(G=Matriu.eye(3), H=Matriu.eye(3), n=3, k=2, M=5, d=3)
        >>> list(code._split_bits_in_blocks([1, 0, 1, 1, 0, 0], 3))
        [[[1, 0, 1]], [[1, 0, 0]]]
        >>> list(code._split_bits_in_blocks([1, 0, 1], 2))
        Traceback (most recent call last):
            ...
        ValueError: Length of bits (3) and block size (2) do not match
        """
        if len(bits) % size != 0:
            raise ValueError(f"Length of bits ({len(bits)}) and block size ({size}) do not match")

        for block in range(0, len(bits), size):
            yield Matriu([bits[block:block+size]])

    def parameters(self):
        """
        Prints the parameters of the Linear Code based on the generator matrix G,
        the control matrix H, and other parameters.

        >>> code = LinearCode(G=Matriu.eye(3), H=Matriu.eye(3), n=3, k=2, M=5, d=3)
        >>> code.parameters()
        Linear Code Parameters:
        - Code Length (n): 3
        - Code Dimension (k): 3
        - Code Size (M): 8
        - Delta (d): 3
        - Error Detection: 2
        - Error Correction: 1
        """
        if self.G is None or self.H is None:
            raise ValueError("Either G or H matrix have not been defined")

        # Maybe the LinearCode was not obtained through LC_Solver,
        # but instead created with lc = LinearCode(), lc.G = ... lc.H = ...
        if self.d is None:
            self.d = LC_Solver._min_hamming_distance(self.H)

        self.k, self.n = self.G.shape
        self.M = 2**self.k

        e_detection = self.d - 1
        e_correction = int((self.d - 1)/2)

        print("Linear Code Parameters:\n"
            f"- Code Length (n): {self.n}\n"
            f"- Code Dimension (k): {self.k}\n"
            f"- Code Size (M): {self.M}\n"
            f"- Delta (d): {self.d}\n"
            f"- Error Detection: {e_detection}\n"
            f"- Error Correction: {e_correction}")


    def codify(self, bits: list[int] | str):
        """
        Encodes a list of bits (or a bit string) into a linear code using the generator matrix G.

        The bits are split into blocks of size k, then each block is multiplied by the generator matrix
        G modulo 2, and the resulting encoded blocks are concatenated into the final encoded string.

        :param bits: A list of bits or a string of bits to encode.
        :return: A string representing the encoded bits.

        >>> m1 = Matriu([[0,1,1,1,0,0],[0,1,1,0,1,1]])
        >>> m2 = Matriu([[0,1,0,1,1,0], [1,0,0,0,1,1], [0,1,1,0,1,1], [0,0,0,0,1,1]])
        >>> lincode = LinearCode()
        >>> lincode.G = m1
        >>> lincode.H = m2
        >>> lincode.n = 6
        >>> lincode.k = 2
        >>> lincode.M = 4
        >>> lincode.d = 3
        >>> print(lincode.codify("10100111101001"))
        011100011100011011000111011100011100011011
        """
        if isinstance(bits, str):
            bits = list(map(int, bits))
        codes = []
        for block in self._split_bits_in_blocks(bits, self.k):
            code = block*self.G % 2
            codes.append("".join(map(str, code[0].elements)))

        return "".join(codes)

    def decodify_detect(self, bits: list[int] | str):
        """
        Decodes a list of bits (or a bit string) into the original message while detecting errors.

        The bits are split into blocks of size n, and for each block, the syndrome is calculated
        using the control matrix H. If the syndrome is non-zero, the block is marked as erroneous
        with '?' symbols. Otherwise, the corresponding original message is retrieved.

        :param bits: A list of bits or a string of bits to decode.
        :return: A string representing the decoded message, with '?' for erroneous blocks.

        >>> m1 = Matriu([[0,1,1,1,0,0],[0,1,1,0,1,1]])
        >>> m2 = Matriu([[0,1,0,1,1,0], [1,0,0,0,1,1], [0,1,1,0,1,1], [0,0,0,0,1,1]])
        >>> lincode = LinearCode()
        >>> lincode.G = m1
        >>> lincode.H = m2
        >>> lincode.n = 6
        >>> lincode.k = 2
        >>> lincode.M = 4
        >>> lincode.d = 3
        >>> print(lincode.decodify_detect("011011000000011011011100011100000000000000"))
        01000110100000
        """

        if isinstance(bits, str):
            bits = list(map(int, bits))
        msgs = []
        for block in self._split_bits_in_blocks(bits, self.n):
            sindrom = self.H*block.transpose() % 2
            if sindrom:
                msgs.append("?"*self.k)
            else:
                msgs.append("".join(map(str, self.get_code_elements()[str(block)])))

        return "".join(msgs)

    def decodify_correct(self, bits: list[int] | str):
        """
        Decodes a list of bits (or a bit string) into the original message, correcting errors within the code's capacity.

        This method splits the bits into blocks of size n. For each block, the syndrome is calculated using the control
        matrix H. If the syndrome indicates an error, it uses a precomputed syndrome table to correct it. Blocks with
        errors exceeding the code's capacity are marked with '?'.

        :param bits: A list of bits or a string of bits to decode.
        :return: A string representing the decoded message, with '?' for uncorrectable blocks.

        >>> m1 = Matriu([[0,1,1,1,0,0],[0,1,1,0,1,1]])
        >>> m2 = Matriu([[0,1,0,1,1,0], [1,0,0,0,1,1], [0,1,1,0,1,1], [0,0,0,0,1,1]])
        >>> lincode = LinearCode()
        >>> lincode.G = m1
        >>> lincode.H = m2
        >>> lincode.n = 6
        >>> lincode.k = 2
        >>> lincode.M = 4
        >>> lincode.d = 3
        >>> print(lincode.decodify_correct("011011000010010011011110111100000000010000"))
        01000110100000
        """
        if isinstance(bits, str):
            bits = list(map(int, bits))

        msgs = []
        correct_capacity = int((self.d - 1) / 2)

        # calcul de la taula de sindromes per corregir
        liders_e = (list(error) for error in itertools.product([0, 1], repeat=self.n) if 0 < sum(error) <= correct_capacity) # erros menors que cap. corr
        taula_sindromes = {}
        for lider_e in liders_e: # calcula taula de síndromes
            lider_e_matrix = Matriu([list(lider_e)])
            sindr = self.H * lider_e_matrix.transpose() % 2
            taula_sindromes[str(sindr)] = lider_e_matrix

        for block in self._split_bits_in_blocks(bits, self.n):
            sindrom = self.H*block.transpose() % 2
            if sindrom:
                error = taula_sindromes.get(str(sindrom))
                if error is None:
                    print(f"Warning! Block {block} has more errors than the linear code's correct capabilites")
                    msgs.append("?"*self.k)
                else:
                    correct = (block - error) % 2
                    msgs.append("".join(map(str, self.get_code_elements()[str(correct)])))
            else:
                msgs.append("".join(map(str, self.get_code_elements()[str(block)])))

        return "".join(msgs)

class LC_Solver():
    """
    Represents a linear code calculator. It must be provided with an instance of "LinearCode",
    which represents the linear code to be solved.

    Attributes:
        lc (LinearCode): An instance of the LinearCode class.

    Example:
    >>> lc = LinearCode(G=Matriu.eye(3), H=Matriu.eye(3), n=3, k=2, M=5, d=3)
    >>> solver = LC_Solver(lc)
    >>> solver.lc.n
    3
    """

    def __init__(self, lc: LinearCode = None):
        """
        Initializes the LC_Solver with a LinearCode instance.

        :param lc: An instance of LinearCode, optional.
        """
        self.lc = lc

    @classmethod
    def _calculate_base(self, base: Matriu, verbose = True) -> Matriu:
        """
        Given a matrix, calculate its basis.
        You can check that a basis is correct (LI rows).
        or from a matrix representing the elements of a code
        calculate its basis.

        Check if the basis is valid (LI rows).
        It applies Gaussian reduction, checks which rows are
        null and eliminates them.

        This operation makes all rows linearly independent,
        so that none of them depends on any other.

        :param base: The matrix to calculate the base for.
        :param verbose: If True, prints the steps during the calculation.
        :return: The reduced base matrix.
        """
        # Primer apliquem reducció. Fa que les files que quedin puguin ser
        # únicament iguals o zero.
        base = self._rrefReduction(base)

        # Guarda quines files s'hauran d'eliminar
        to_remove = [0] * base.shape[0]

        # Iterem totes les files
        for row1 in range(base.shape[0]):
            # Si la fila és tot 0, cal eliminar-la
            if base[row1] == Row([0]*base.shape[1]):
                if verbose: print(f"Base[{row1}] == 0. Removing. ")
                to_remove[row1] = 1 # guardem que la fila a index `row1` s'ha d'eliminar
                continue
            # Comparem la fila actual amb les següents
            for row2 in range(row1+1, base.shape[0]):
                # Si són iguals, cal eliminar-ne una
                if base[row1] == base[row2]:
                    if verbose: print(f"Base[{row1}] == Base[{row2}]. Removing. ")
                    to_remove[row2] = 1 # guardem que la fila a index `row2` s'ha d'eliminar

        # Eliminem del final al principi perquè sinó
        # en eliminar es mouen tots els index
        for i in range(len(to_remove)-1, -1, -1):
            if to_remove[i]:
                base.remove_row(i)

        # Apliquem reducció de nou (en eliminar files, potser n'han quedat
        # d'iguals o no està en forma RREF)
        # self.base = self._rrefReduction(base)
        return self._rrefReduction(base)

    @classmethod
    def _rrefReduction(self, matrix: Matriu, verbose = True):
        """
        Given a matrix, calculate its RREF (Reduced Row Echelon From) form.
        This means that for all rows in a matrix, the first element of a row
        is further to the right than all the rows above it.
        Ex:
            [0 1 1 0 1]  ->  [1 1 0 1 1]
            [1 1 0 1 1]  ->  [0 1 1 0 1]

        Each row "n" is iterated, checking if the element ‘n’ of this row is 1:
            if it is not, look for whether any row has a 1 at position ‘n’, and swap them;
            if it is, the rest of the rows are made to have a 0 in this position.

        :param matrix: The matrix to be reduced.
        :param verbose: If True, prints the steps during the reduction.
        :return: The reduced matrix.

        >>> matrix = Matriu([[1, 1, 0], [1, 0, 1], [0, 1, 1]])
        >>> result = LC_Solver._rrefReduction(matrix, verbose=False)
        >>> result.matrix
        [[1 0 1], [0 1 1], [0 0 0]]
        """
        for pivot in range(matrix.shape[0]):
            if pivot >= matrix.shape[1]:
                break

            if verbose: print(f"Utilitzant pivot = {pivot}")

            if matrix[pivot][pivot] == 0:
                if verbose: print(f"\tmatrix[{pivot}, {pivot}] == 0")
                # Intercanviar per una fila que tingui un 1 a la columna 'pivot'
                for row in range(pivot + 1, matrix.shape[0]):
                    if matrix[row][pivot] != 0:
                        if verbose: print(f"\t\tmatrix[{row}, {pivot}] != 0: matrix[{pivot}, {pivot}] <-> matrix[{row}, {pivot}]")
                        matrix.swap_rows(pivot, row)
                        break
                else:
                    # No hi ha elements amb 1 a la columna
                    if verbose: print(f"\telements a col[{pivot}] ja són 0; continuant")
                    continue

            # Fer que tots els elements de la columna excepte pivot siguin 0
            for row in range(matrix.shape[0]):
                if row != pivot and matrix[row][pivot] != 0:
                    if verbose: print(f"\tmatrix[{row}] = matrix[{pivot}] + matrix[{row}]")
                    # Sumem la fila pivot a la fila on volem eliminar l'element de la columna
                    matrix[row] = matrix[row] + matrix[pivot]

        return matrix % 2

    @classmethod
    def _calculate_H_not_systematic(self, G: Matriu, verbose: bool = True) -> Matriu:
        """
        Procedure similar to RREF:
        We transpose G, is concatenated with the identity of n x n (eye(n)).
        We are left with (Gt|I). We apply elementary transformations
        so that the first k rows of Gt are staggered,
        and the remaining rows of Gt are 0. The transformations
        are also applied to part I.
        The last n-k rows of matrix I correspond to H.

        :param G: The generator matrix.
        :param verbose: If True, prints the steps during the calculation.
        :return: The calculated parity-check matrix H.

        >>> G = Matriu([[1, 0, 1, 1], [0, 1, 1, 0]])
        >>> H = LC_Solver._calculate_H_not_systematic(G, verbose=False)
        Utilitzant pivot = 0
            matrix[2] = matrix[0] + matrix[2]
            matrix[3] = matrix[0] + matrix[3]
        Utilitzant pivot = 1
            matrix[2] = matrix[1] + matrix[2]
        Utilitzant pivot = 2
        Utilitzant pivot = 3
        Utilitzant pivot = 0
        Utilitzant pivot = 1
        Utilitzant pivot = 2
        Utilitzant pivot = 3

        >>> H.matrix
        [[1 1 1 0], [1 0 0 1]]
        """
        k, n = G.shape

        Gt = G.transpose()
        Gt_i = Gt.hstack(Matriu.eye(Gt.shape[0]))
        for pivot in range(k):
            if Gt_i[pivot][pivot] == 0:
                if verbose: print(f"matrix[{pivot}, {pivot}] == 0")
                # Intercanviar per una fila que tingui un 1 a la columna 'pivot'
                for row in range(pivot + 1, Gt_i.shape[0]):
                    if Gt_i[row][pivot] != 0:
                        if verbose: print(f"matrix[{row}, {pivot}] != 0: matrix[{pivot}, {pivot}] <-> matrix[{row}, {pivot}]")
                        Gt_i.swap_rows(pivot, row)
                        break
                else:
                    # No hi ha elements amb 1 a la columna
                    continue

            # Fer que tots els elements de la columna excepte pivot siguin 0
            for row in range(Gt_i.shape[0]):
                if row != pivot and Gt_i[row][pivot] != 0:
                    if verbose: print(f"matrix[{row}] = matrix[{pivot}] + matrix[{row}]")
                    # Sumem la fila pivot a la fila on volem eliminar l'element de la columna
                    Gt_i[row] = Gt_i[row] + Gt_i[pivot]

        H = Gt_i.split(slice(n-k-2, n, 1), slice(k, n+k, 1)) % 2
        # H = Gt_i.split(slice(n-k-1, n, 1), slice(k, n+k, 1)) % 2
        return self._calculate_base(H)

    @classmethod
    def _calculate_H(self, G: Matriu, verbose: bool = True) -> Matriu:
        """
        Computes control matrix H, regardless of whether the
        generator matrix G is in systematic form.

        :param G: The generator matrix.
        :param verbose: If True, prints the intermediate steps.
        :return: The calculated parity-check matrix H.

        >>> G = Matriu([[1, 0, 1, 1], [0, 1, 1, 0]])
        >>> H = LC_Solver._calculate_H(G, verbose=False)
        Utilitzant pivot = 0
        Utilitzant pivot = 1
        Utilitzant pivot = 0
        Utilitzant pivot = 1
        G matrix:
        [1 0 1 1]
        [0 1 1 0]

        >>> H.matrix
        [[1 1 1 0], [1 0 0 1]]
        """
        G = self._calculate_base(Matriu(G))
        print("G matrix:")
        print(G)
        k, n = G.shape
        # G = (I|A)?
        G_i = G.split(slice(k), slice(k))
        G_a = G.split(slice(k), slice(k, n, 1))
        if G_i != Matriu.eye(k):
            return self._calculate_H_not_systematic(G, verbose)
        H = G_a.transpose().hstack(Matriu.eye((n-k)))

        return H

    @classmethod
    def _min_hamming_distance(self, G: Matriu) -> int:
        """
        Computes the minimum Hamming distance of a linear code from its generator matrix G.

        The minimum Hamming distance is the smallest number of columns in G whose sum (mod 2)
        results in the zero vector.

        :param G: Generator matrix of the linear code.
        :return: Minimum Hamming distance.

        >>> G = Matriu([[1, 0, 1, 1], [0, 1, 1, 0]])
        >>> LC_Solver._min_hamming_distance(G)
        2
        >>> G = Matriu([[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]])
        >>> LC_Solver._min_hamming_distance(G)
        3
        """
        n_cols = G.shape[1]  # Number of columns in G

        # Iterate over subset sizes (1 to n_cols)
        for mida_comb in range(1, n_cols + 1):
            # Genera les possibles combinacions amb el nombre de columnes que va augmentant fins a `n`
            for cols in combinations(range(n_cols), mida_comb):
                # Suma les columnes de la combinació mòdul 2
                col_sum = sum(G.get_columns(cols)) % 2

                # Si la suma és 0, el nombre de columnes és el
                # nombre d'elements en la combinació
                if not col_sum:
                    return mida_comb  # Minimum Hamming distance found

        # Per si totes són independents
        return n_cols + 1

    @classmethod
    def Hamming(self, t: int) -> LinearCode:
        """
        H = (A|I) is generated so that G can be generated later.
        First the dual is generated, G‘ = H = (A|I) -> H’ = (I|A) = G,
        and the Haming code is obtained from it.

        :param t: The Hamming parameter (defines the number of parity bits).
        :return: A LinearCode object representing the Hamming code.
        """
        lc = LinearCode()
        lc.n = 2**t-1
        lc.M = 2**lc.n
        lc.k = lc.n-t

        lc.d = 3 # per definició

        lc.H = Matriu([[] for _ in range(lc.n-lc.k)])

        # Afegim les N columnes amb [1, N] valors binaris a cada col
        for col in range(lc.n, 0, -1):
            column = list(map(int, list(bin(col).replace("0b", "").zfill(lc.n-lc.k))))
            lc.H.add_column(Row(column))

        # Calculem G, considerant que és el dual
        lc.G = self._calculate_H(lc.H, True)

        return lc


    @classmethod
    def solve(self, matrix: Matriu, verbose = True) -> LinearCode:
        """
        Computes the resulting linear code from the `LC_Solver`,
        which contains the elements of a code or a basis of it.

        This method calculates the generator matrix G, the parity-check matrix H, and the minimum Hamming distance of the code.

        :param matrix: The input matrix used to calculate the code elements or basis.
        :param verbose: If True, prints the process.
        :return: A LinearCode object containing the code parameters and matrices.

        >>> lc_solver = LC_Solver()
        >>> matrix = Matriu([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        >>> lc = lc_solver.solve(matrix)
        Utilitzant pivot = 0
        Utilitzant pivot = 1
        Utilitzant pivot = 2
        Utilitzant pivot = 0
        Utilitzant pivot = 1
        Utilitzant pivot = 2
        Utilitzant pivot = 0
        Utilitzant pivot = 1
        Utilitzant pivot = 2
        Utilitzant pivot = 0
        Utilitzant pivot = 1
        Utilitzant pivot = 2
        G matrix:
        [1 0 0]
        [0 1 0]
        [0 0 1]

        >>> lc.G.shape
        (3, 3)
        >>> lc.H.shape
        (0, 0)
        >>> lc.d
        1
        >>> lc.k
        3
        >>> lc.n
        3
        """
        lc = LinearCode()

        lc.G = self._calculate_base(matrix)
        lc.k, lc.n = lc.G.shape
        lc.M = 2**lc.k
        lc.H = self._calculate_H(lc.G, verbose)
        lc.d = self._min_hamming_distance(lc.H)
        return lc

if __name__=="__main__":
    lincode = LinearCode()
    lincode.G = Matriu([
                [0,1,1,1,0,0],
                [0,1,1,0,1,1]
               ])
    lincode.H = Matriu([
                [0,1,0,1,1,0],
                [1,0,0,0,1,1],
                [0,1,1,0,1,1],
                [0,0,0,0,1,1]
               ])

    #lincode = LC_Solver.solve(M)
    #solver = LC_Solver(lincode)
    print(lincode.H)
    print()
    print(lincode.G)
    print()
    #print(lincode.G*lincode.H.transpose() % 2)
    #print(LC_Solver._rrefReduction(M))
    lincode.parameters()
    #solver2 = LC_Solver();
    #solver2.parameters(lincode)

    print(lincode.get_code_elements())
    print()
    print(lincode.codify("10100111101001"))
    print()
    print(lincode.decodify_detect("011011000000011011011100011100000000000000"))
    print()
    print(lincode.decodify_detect("011011000010010011011110111100000000010000"))
    print()
    print(lincode.decodify_correct("011011000010010011011110111100000000010000"))



    # print(code.G.split(slice(code.k), slice(2, 3, 1)))
    # print(LC_Solver._calculate_base(M))
    # print(LC_Solver._min_hamming_distance(M))

    # code = LC_Solver.solve(M)
    # solver = LC_Solver(code)
    # print(solver.codify(list(map(int, list("10100111101001")))))

    # print(Matriu([[], [], []]).add_column(Row([1, 1, 1])))

    # ham3 = LC_Solver.Hamming(5)
    # print(ham3.H)
    # print()
    # print(ham3.G)

    # print(ham3.G*(ham3.H.transpose()) % 2)
