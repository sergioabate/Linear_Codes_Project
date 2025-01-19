from dataclasses import dataclass
from typing import Generator
from itertools import combinations

from Row import Row
from Matriu import Matriu

import itertools

"""
Representació d'un codi lineal, amb les seves propietats possibles:
"""
@dataclass
class LinearCode:
    """Representació d'un codi lineal"""
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
        Genera tots els elements del codi en un diccionari.
        És útil per decodificar en blocs.

        Ho guarda d'aquesta manera:

        decoded         | coded
        '[0 0 0 0 0 0]'   (0, 0)
        ...
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
        if len(bits) % size != 0:
            raise ValueError(f"Length of bits ({len(bits)}) and block size ({size}) do not match")

        for block in range(0, len(bits), size):
            yield Matriu([bits[block:block+size]])

    def parameters(self):
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
            f"  - Code Length (n): {self.n}\n"
            f"  - Code Dimension (k): {self.k}\n"
            f"  - Code Size (M): {self.M}\n"
            f"  - Delta (d): {self.d}\n"
            f"  - Error Detection: {e_detection}\n"
            f"  - Error Correction: {e_correction}")


    def codify(self, bits: list[int] | str):
        if isinstance(bits, str):
            bits = list(map(int, bits))
        codes = []
        for block in self._split_bits_in_blocks(bits, self.k):
            code = block*self.G % 2
            codes.append("".join(map(str, code[0].elements)))

        return "".join(codes)

    def decodify_detect(self, bits: list[int] | str):
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
        if isinstance(bits, str):
            bits = list(map(int, bits))
            
        msgs = []
        correct_capacity = int((self.d - 1) / 2)

        # calcul de la taula de sindromes per corregir
        liders_e = (list(error) for error in itertools.product([0, 1], repeat=self.n) if 0 < sum(error) <= correct_capacity) # erros menors que cap. corr
        taula_sindromes = {}
        for lider_e in liders_e: # calcula taula de síndormes
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

"""
Representa una calculadora de codis lineals.
Cal proporcionar-li una instància de `LinearCode`, que representa
el codi lineal a resolder
"""
class LC_Solver():
    def __init__(self, lc: LinearCode = None):
        self.lc = lc

    @classmethod
    def _calculate_base(self, base: Matriu, verbose = True) -> Matriu:
        """
        Donada una matriu, calcula la seva base.
        Pot verificar que una base sigui correcte (files LI)
        o a partir d'una matriu que representa els elements d'un codi
        calcular-ne la seva base.

        Comprova si la base és vàlida (files LI).
        Aplica reducció de gauss, comprova quines files són
        nul·les i les elimina.

        Aquesta operació fa que totes les files siguin linealment independents,
        que cap d'elles depengui d'una altra, o combinació d'aquestes.
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
        Donada una matriu, calcula la seva forma RREF (Reduced Row Echelon Form).
        Això significa que per totes les files d'una matriu, el primer element d'una fila
        es troba més a la dreta que totes les files superiors
        Ex:
            [0 1 1 0 1]  ->  [1 1 0 1 1]
            [1 1 0 1 1]  ->  [0 1 1 0 1]

        S'itera cada fila `n`, verificant si l'element `n` d'aquesta fila és 1;
            si no ho és, es busca si alguna fila té un 1 a la posició `n`, i s'intercanvien;
            si ho és, es fa que la resta de files tinguin un 0 a aquesta posició
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
        Procediment semblant a RREF:
        Transposem G, i hi concatenem la identitat de n x n (eye(n))
        Ens quedem amb (Gt|I). Apliquem transformacions elementals
        per tal que les primeres k files de Gt estiguin esglaonades,
        i la resta de files de Gt siguin 0. Les transformacions
        s'apliquen també a la part de I.
        Les últimes n-k files de la matriu I es corresponen a H.
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
        Calcula la matriu de control, H, indiferentment de si és
        o no sistemàtica.
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
        Es genera la H = (A|I) per després poder generar G.
        Primer es genera el dual, G' = H = (A|I) -> H' = (I|A) = G,
        i s'obté el codi de Hamming a partir d'aquest
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
        Calcula el codi lineal resultant del `LC_Solver`
        que conté els elements d'un codi o una base d'aquest.
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
