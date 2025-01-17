from dataclasses import dataclass
from typing import Generator
from itertools import combinations
    
from Row import Row
from Matriu import Matriu

@dataclass
class LinearCode:
    """Representació d'un codi lineal"""
    G: Matriu = None 
    H: Matriu = None
    
    n: int = 0
    k: int = 0
    M: int = 0
    d: int = 0
    
    systematic: bool = False
    
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
        """
        # Primer apliquem reducció
        base = self._rrefReduction(base)
        
        # Guarda quines files s'hauran d'eliminar
        to_remove = [0] * base.shape[0]
        for row1 in range(base.shape[0]):
            # Si la fila és tot 0, cal eliminar-la
            if base[row1] == Row([0]*base.shape[1]):
                if verbose: print(f"Base[{row1}] == 0. Removing. ")
                to_remove[row1] = 1
                continue
            # Comparem la fila actual amb les següents
            for row2 in range(row1+1, base.shape[0]):
                # Si són iguals, cal eliminar-ne una
                if base[row1] == base[row2]:
                    if verbose: print(f"Base[{row1}] == Base[{row2}]. Removing. ")
                    to_remove[row2] = 1

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
        for pivot in range(matrix.shape[0]):
            if pivot >= matrix.shape[1]:
                break
            
            if matrix[pivot][pivot] == 0:
                if verbose: print(f"matrix[{pivot}, {pivot}] == 0")
                # Intercanviar per una fila que tingui un 1 a la columna 'pivot' 
                for row in range(pivot + 1, matrix.shape[0]):
                    if matrix[row][pivot] != 0:
                        if verbose: print(f"matrix[{row}, {pivot}] != 0: matrix[{pivot}, {pivot}] <-> matrix[{row}, {pivot}]")
                        matrix.swap_rows(pivot, row)
                        break
                else:
                    # No hi ha elements amb 1 a la columna
                    continue

            # Fer que tots els elements de la columna excepte pivot siguin 0
            for row in range(matrix.shape[0]):
                if row != pivot and matrix[row][pivot] != 0:
                    if verbose: print(f"matrix[{row}] = matrix[{pivot}] + matrix[{row}]")
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

        H = Gt_i.split(slice(n-k-1, n, 1), slice(k, n+k, 1)) % 2
        print(Gt_i%2)
        return self._calculate_base(H)
    
    @classmethod
    def _calculate_H(self, G: Matriu, verbose: bool = True) -> Matriu:
        """
        Calcula H si la matriu és sistemàtica
        """
        G = self._calculate_base(Matriu(G))
        k, n = G.shape
        # G = (I|A)?
        G_i = G.split(slice(k), slice(k))
        G_a = G.split(slice(k), slice(k, n, 1))
        if G_i != Matriu.eye(k):
            return self._calculate_H_not_systematic(G, verbose)
        H = G_a.transpose().hstack(Matriu.eye((n-k)))
        
        return H
    
    @classmethod                
    def _get_free_variables(self, matrix: Matriu, verbose: bool = True) -> list[int]:
        """
        Una vegada està convertida en RREF, les variables
        lliures són les columnes on cap fila hi té el 1r 1.
        
        Iterar cada fila, buscar el primer 1 que hi tenen i 
        guardar aquesta columna (variable dependent).
        Les lliures seran la resta (totes les columnes - dependents)
        >>> m = LC_Solver(3, [[0, 1, 1], [1, 0, 0]])
        >>> m._get_free_variables(m.base, False)
        [2]
        >>> m = LC_Solver(3, [[0, 1, 1], [1, 0, 0], [0, 0, 1]])
        >>> m._get_free_variables(m.base, False)
        []
        """
        n_eq, n_var = matrix.shape        
        pivot_columns = set()
        
        for row in range(n_eq):
            for col in range(n_var):
                if matrix[row][col] == 1:
                    if verbose: print(f"M[{row},{col}] == 1. Adding to pivot. ({pivot_columns})")
                    pivot_columns.add(col)
                    break       
                     
        all_columns = set(range(n_var))
        free_columns = list(all_columns - pivot_columns)
        return free_columns
    
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
        try:
            lc.H = self._calculate_H(lc.G, verbose)
            lc.d = self._min_hamming_distance(lc.H)
            lc.systematic = True
        except ValueError:
            lc.H = Matriu.zeros(lc.k, lc.n)
            lc.systematic = False
        return lc
    
    def _split_bits_in_blocks(self, bits: list[int], size: int) -> Generator[Matriu, None, None]:
        if len(bits) % size != 0:
            raise ValueError(f"Length of bits ({len(bits)}) and block size ({size}) do not match")
        
        for block in range(0, len(bits), size):
            yield Matriu([bits[block:block+size]])
    
    def parameters(self):
        pass
    
    def codify(self, bits: list[int]):
        if self.lc is None:
            raise ValueError("Code is not defined")
        
        codes = []
        for block in self._split_bits_in_blocks(bits, self.lc.k):
            code = block*self.lc.G % 2
            codes.append("".join(map(str, code[0].elements)))
            
        return "".join(codes)
                    
    def decodify_detect(self, bits: list[int]):
        if self.lc is None:
            raise ValueError("Code is not defined")

        msgs = []
        for block in self._split_bits_in_blocks(bits, self.lc.n):
            sindrom = self.lc.H*block.transpose() % 2
            if sindrom:
                msgs.append("?"*self.lc.k)
                continue
            msgs.append("".join(map(str, sindrom[0].elements)))
        return "".join(msgs)
        
    
    def decodify_correct(self, bits: list[int]):
        pass
    
if __name__=="__main__":
    # M = Matriu([[0, 1, 0, 1, 1, 0],
    #             [1,0,0,0,1,1],
    #             [0,1,1,0,1,1],
    #             [0,0,0,0,1,1]
    #            ])
    
    M = Matriu([[0,1,1,1,0],
                [0,0,1,0,1]
               ])
    
    code = LC_Solver.solve(M)  
    solver = LC_Solver(code)
    print(code.H)
    print()
    print(code.G)
    # print(solver.codify(list(map(int, list("011001011101")))))
    # print(solver.decodify_detect(list(map(int, list("01110001110111010111")))))
    
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