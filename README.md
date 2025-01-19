# Linear Codes in Action

## Introduction
Linear codes are an essential part of error-correcting codes, designed to ensure reliable data transmission and storage. Nowadays, they are widely used in computers and telecomunication systems.

They operate over the binary field _F2_ where all operations are performed modulo 2. The goal of these codes is to encode messages into codewords that not only carry the information, but also allow the detection and correction of errors introduced during transmission.

Linear codes are defined by four main parameters: the block length (_N_), the message length (_k_), the code dimension (_M_), and the minimum distance (_d_). The **block length _N_** is the length of each codeword, which includes both the original message bits and additional redundant bits added for error detection and correction. The message length _k_ refers to the number of bits in the original message, the data to encode. This two last paramaters are related by the **code rate**, which expresses the proportion of bits which actually carry the data compared to the total amount of bits: `k/N`. 

The **code dimension _M_**, given by `2^k`, represents the total number of possible codewords that the code can generate. 

The **minimum distance _d_**, which is the smallest Hamming distance between any two codewords: how many bit changes have to be done to one codeword to get another codeword. It determines the error-detection and correcting capabilities of the code, as the lower the distance, the fewer the bit errors it supports. A code with a minimum distance _d_ can detect up to `d−1` errors and correct up to `⌊(d−1)/2⌋` errors.

The structure of linear codes is defined using two key matrices: the **generator matrix (_G_)** and the **control matrix (_H_)**. The generator matrix _G_ is used for encoding. It has dimensions `k×N`, and its role is to map each k-bit message to a unique N-bit codeword. This is achieved by multiplying the message vector by G, which is a base for the code, using modulo 2 arithmetic. Thus, given a message `m`, we can encode it to `c` as follows: `c = m · G`.

The **control matrix** _H_ is crucial for detecting errors. This matrix has dimensions `(N−k)×N` and satisfies a property that ensures every valid codeword c satisfies `H⋅c^T=0` (where `c^T` is the transpose of `c`). This means that valid codewords are orthogonal to the rows of _H_, and any contradiction from this property indicates an error.

To detect and correct errors, linear codes use the **syndrome function**. When a vector _y_ is received, it might contain errors, so the syndrome is calculated as `s=H⋅y^T`. If `s=0`, the received vector is a valid codeword, as it has previously been seen that every valid codeword satisfies said property. However, if `s≠0`, it means errors are present. Furthermore, this syndrome can then be used to correct errors: each syndrome can be related to a class (as we are working over the finite field of `F2^n`), which contain a leader (that is the value with the least weight, the one with "the least amount of one's"). This leader can be user to correct the codeword, as follows: we receive a codeword with errors `y`, with syndrome `s` and whose leader is `z`, and want to compute the original codeword `y`; then `y = y + z` (or `y = y - z`, which is the same as we are working in `F2`). The syndrome should also appear in a precomputed table of all the possible syndromes for the valid codewords; when correcting, if the obtaind syndrome is not found on this precomputed table, it means the code has more errors than the maximum errors the code can correct. Therefore, this codeword cannot be corrected.  

There also exist more concrete families of linear codes, such as **Hamming Codes**. This codes characterise themselves to be able to correct all single error bits, while being efficient (code-rate speaking, as they use as little redundancy as possible). These codes are defined by `Ham2(t)`, where _t_ is used to compute the parameters _N_ and _k_ of the code, where `N = 2^t - 1` and `k = N - t`. Furthermore, these codes have, by definition, a minimum distance of `d = 3`.

Another important characteristic of these type of codes is its control matrix, where its columns are all the numbers `i = 1, ..., 2^t-1` codified in binary. Therefore, for `Ham2(3)` we have the following control matrix:
```
    [0 0 0 1 1 1 1]
H = [0 1 1 0 0 1 1]
    [1 0 1 0 1 0 1]
```

## Program Structure
The code is structured in three main files:
* `Row.py:` contains a class definition of a matrix's row. Methods for row operations are included in it, such as addition (and subtraction), scalar multiplication or row transformations. 
* `Matrix.py:` contains a class definition of a matrix. It internally makes use of `Row` instances to represent a matrix. Methods for matrix operations are included in it, such as matrix addition and multiplication, scalar multiplication, transposation and matrix transformations.
* `LinearCode.py:` constains a class definition of a linear code, with all its previsouly seen parameters. It includes methods to codify and decodify using a linear code, as well as to detect and correct errors. Another class, `LC_Solver` is included in this file, which is used to solve a given matrix and obtain a `LinearCode`. Further explanation can be found below.

The implementation of most methods as been done using what is known a **_Python's Magic Methods_**. They are used to define or override the behavior of standard Python operations for custom objects. For example, they enable overloading operators like +, -, and *, as well as defining behavior for comparisons, indexing, and string representations.

### Row
Represents a row of a matrix. It implements basic arithmetic row operations, as well as boolean operations and row transformations (add/delete entries). It has been implemented to represent a row over the reals field; therefore, characteristics seen of linear codes over the F2 field do not apply in this class. For example `Row([1, 0]) != Row([3, 2])`.

It is the foundation for the `Matrix` class. A usage example for all characteristic of the class can be found below:
```python
from Row import Row

# Create rows
r1 = Row([1, 2, 3])
r2 = Row([4, 5, 6])

# Addition
print(r1 + r2) 
>>> [5 7 9]
print(r1 + 2) 
>>> [3 4 5]

# Scalar multiplication
print(r1 * 2)   
>>> [2 4 6]

# Modulus
print(r1 % 2)   
>>> [1 0 1]

# Boolean operations
print(bool(Row([0, 0, 0])))  
>>> False
print(bool(Row([0, 1, 0])))  
>>> True

# Equality
print(Row([0, 1]) == Row([0, 1]))
>>> True
print(Row([1, 1]) == Row([0, 1]))
>>> False

# Access and modify elements
print(r1[1])    
>>> 2
r1[1] = 10
print(r1)       
>>> [1 10 3]

# Add elements
r1.add_element(4)
print(r1)       
>>> [1 10 3 4]
r1.add_element([5, 6])
print(r1)       
>>> [1 10 3 4 5 6]

# Slicing
print(r1[1:4])  
>>> [10 3 4]
```

### Matrix
Represents a matrix. It implements basic arithmetic matrix operations, as well as boolean operations and row transformations (add/delete rows). It has been implemented to represent a matrix over the reals field; therefore, characteristics seen of linear codes over the F2 field do not apply in this class, as previously seen in `Row`.

It has two attributes: 
* `Matrix.matrix:` a list of `Row` instances representing the matrix
* `Matrix.shape:` the dimensions of the matrix, represented as a tuple. `Matrix.shape[0]` is the number of rows, whereas  `Matrix.shape[1]` is the number of columns.

Apart from the _magic methods_, it also implements other methods to allow for more complex operations:
<details>
  <summary><b>Matrix.transpose()</b></summary>
 Transposes the matrix. Returns a new `Matrix`, where the rows and columns have been swaped.

 ```python 
 m = Matrix([[1, 2], [3, 4]])
 print(m.transpose())
 >>> [1 3] 
     [2 4]
 ```
</details>

<details>
  <summary><b>Matrix.swap_rows(index1, index2)</b></summary>
 Given two indeces, representing the row at that position, swaps both rows. The operation is inplace, modifying the inner rows of the matrix instance. 

 ```python 
 m = Matrix([[1, 2], [3, 4]])
 m.swap_rows(0, 1)
 print(m)
 >>> [3 4] 
     [1 2]
 ```
</details>

<!-- > **Matrix.transpose()**
> Transposes the matrix. Returns a new `Matrix`, where the rows and columns have been swaped.
> ```python 
> m = Matrix([[1, 2], [3, 4]])
> print(m.transpose())
> >>> [1 3] 
>     [2 4]
> ```

> **Matrix.swap_rows(index1, index2)**
> Given two indeces, representing the row at that position, swaps both rows. The operation is inplace, modifying the inner rows of the matrix instance. 
> ```python 
> m = Matrix([[1, 2], [3, 4]])
> m.swap_rows(0, 1)
> print(m)
> >>> [3 4] 
>     [1 2]
> ``` -->

### LinearCode
### LC_Solver
#### Calculating a base of a matrix (G)
Being able to obtain a base for a given matrix is a key operation in linear codes. As it has previsouly been said, a generator matrix is a base for all the codewords. Therefore, calculating the base should be the first operation performed. It is a private method of `LC_Solver`, **LC_Solver._calculate_base(Matrix)**.

To do so, the matrix is first reduced into **RREF**, where for each row, its first element is at the right-most from all the rows above it. Furthermore, all the other elements in that column must also be zero. The idea is to try to have the identity matrix further to the left as possible. As a quick example:
```
[0 1 1 0 1] -> [1 0 1 1 0]
[1 1 0 1 1] -> [0 1 1 0 1]
```
<details>
  <summary><b>Matrix._rrefReduction(Matrix)</b></summary>
  
To achieve that, we iterate each row `n = 0, ..., Matrix.shape[0]`, checking the row element also at position `n`:
1. If element at `Matrix[n][n]` is equal to zero, we try to find a furtherdown row, `i`, whose `n`th element `Matrix[i][n]` is different to 0, so that both rows can be swapped.
2. If no row has the `n`th element different to zero, we continue with the next `n`
3. If `Matrix[n][n]` is different to zero, or we swapped it with another row, this row is added to all the other rows `i = 0, ..., Matrix.shape[0]; i != n`, making the `n`th element of each row be 0 (except the current row).
</details>

Once the matrix is in RREF, we have two option: either the row is null (all elements are zero), or it is equal to another row. Therefore, to obtain the base, we simply need to delete all the null rows, as well as delete all the rows that are equal except for one. 

Finally, the matrix's RREF is computed again, as due to the row deletions this form could have been lost

Once the matrix is forms a base, it corresponds to the **generating matrix G**.

#### Calculating a control matrix (H)
For a given matrix, we can compute its control matrix. Before compute the control matrix, though, the given matrix must form a base, so that it is a generating matrix G. The previously seen functions allow us to do that.

Once we have a generating matrix, we have two options to compute the control matrix:
1. Perform elemental row operations to G, so that it can be written in the form `G = (I | A)`, where I is the indentity matrix of dimensions `K·K`. We can then compute H, using `H = (A^T | I)`. It requires G to be systematic.
2. Find all the equations that satisfy: `(λ1...λk) · G = x1...Xn`, where `x1...Xn` is an element of the finite field `F2^n`. 

It can be seen how the most generic solution is to use approach number 2, as it does not only allow to compute the control matrix for systematic G matrices, but for every G matrix. It is true, tough, that it is computationally more expensive, as more matrix transformations are required.

The implementation is done using both approaches: we first try to write the generating matrix in its systematic form and, if possible, compute H directly; otherwise, the second approach is performed.

<details>
  <summary><b>Matrix.calculate_H(Matrix)</b></summary>

Given a Matrix, which corresponds to the generating matrix, it first computes its base. This is to make sure all rows are linearly independent. In this step it is also attempted to write `G = (I | A)`, so that the H matrix can easily be computed. If it is not the following approach is used:

  <details>
    <summary><b>Matrix._calculate_H_not_systematic(Matrix)</b></summary>
  
  The generating matrix is transposed, and the identity matrix of size `NxN` is added to its right side, resulting in `G^t | I`. 
  Elemental row operations are performed to this new matrix until its first `k` rows are in RREF: the first element of each row is at the left-most side, and all the other values in this column must be 0.

  Finally, the control matrix H can be obtained taking the last `n-k` rows and the last `n` columns of this rows.

  </details>
</details>



#### Calculating the minimum Hamming Distance (d)

#### Solving a linear code
A main method is given, **LC_Solver.solve(Matrix)**. This method allows to solve a given matrix, obtaining its linear code.

The main characteristics of this method is that any matrix can be provided, and it needn't be in the correct "generating matrix format" (that is, being a base or linearly independant matrix). This allows user to, for example, provide all the codewords from a linear code, and obtain their generating and control matrices.

This method returns an instance of `LinearCode`, with all its attributes defined, making it quick and easy to obtain a linear code to codify and decodify with.

The implementation of this method relies on all the previously seen functions of the `LC_Solver` class

### Testing
<!-- s'han utilitzat doctests en les funcions per verificar les funcionalitats -->

## Usage 

## Examples
<!-- Un exemple de LC_Solver.solve() amb una matriu que representi una G amb format correcte -->
<!-- Un exemple de LC_Solver.solve() amb una matriu que tingui els elements d'un codi -->
<!-- Exemple de codificació -->
<!-- Exemple de descodificació i detecció -->
<!-- Exemple de descodificació i correció -->
<!-- Exemple de descodificació i correció amb més errors dels que pot corregir -->