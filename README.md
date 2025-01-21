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
The LinearCode class represents a linear code with all its parameters as attributes. This class allows to perform all the functions for which these codes exist in the world of coding theory.

The attributes it has correspond to the parameters of the code:
* `G`: its generator matrix, which is an instance of the `Matrix` class
* `H`: its control matrix, which is also an instance of the `Matrix` class
* `n`: the block length, which is represented as an `int`
* `k`: the message length (`int`)
* `M`: the code dimension (`int`)
* `d`: the minimum distance (`int`)
* `code_elements`: corresponds to all elements of the linear code. These are stored in a `dict` variable, where the key is the encoded message, and the value is the original message

This class incorporates methods to implement the basic functions of Linear Codes, such as calculating the parameters of a linear code, encoding a message, decoding for error detection, and decoding for error correction.

Apart from these methods (explained in detail below), there is an auxiliary method, which allows us to divide a sequence of bits (e.g. a message to be encoded) into blocks of the desired length.

<details>
  <summary><b>_split_bits_in_blocks(bits, size)</b></summary>
 Returns instances of Matriu corresponding to the blocks of the bit sequence.

 ```python
code = LinearCode(G=Matriu.eye(3), H=Matriu.eye(3), n=3, k=2, M=5, d=3)
list(code._split_bits_in_blocks([1, 0, 1, 1, 0, 0], 3))
>>> [[[1, 0, 1]], [[1, 0, 0]]]
 ```
</details>

Thanks to this method we can encode/decode messages according to the message size (`k`) and the code dimension (`M`).

### Computing all the elements of the code
From the generator matrix G and the measurement of the original messages, all the elements of a linear code can be obtained. To do this, the generator matrix must be multiplied by all possible messages.

The number of possible messages corresponds to `2^k`, taking into account that we are in `F2^n`, and that the messages have measure `k`.

Therefore, the first thing to do is to identify all possible messages. Once identified, they are associated with the encoded message by multiplying the message by the generator matrix G.

This implementation has been done as a method of the class.

<details>
  <summary><b>LinearCode.get_code_elements()</b></summary>
 In order to get all the elements of the code, all possible messages are first generated. Starting from the parameter `k`, the necessary binary combinations to be generated are known.  For this, we have used the `itertools` library, which allows us to generate the messages quickly.

 Then, each of the generated messages must be associated with the corresponding encoding. For this purpose, we have used a dictionary, which allows us to associate two elements with a `key-value` relationship, so that the elements of the linear code can be easily accessed.

 Therefore, each element is calculated by multiplying each message by the matrix G (converting the message to a `Matrix` instance to be able to do the operation), and using these as a key, the original message is associated to them as a value in the dictionary.

 The reason for this assignment of the key and the value is that this method is mainly used for decoding, so the key is required to be the element of the code to be able to access the original message, and thus, decode.

 This method only calculates the code elements in case the instance itself does not contain them. Otherwise they are not recalculated.

```python
m1 = Matriu([[0,1,1,1,0,0],[0,1,1,0,1,1]])
m2 = Matriu([[0,1,0,1,1,0], [1,0,0,0,1,1], [0,1,1,0,1,1], [0,0,0,0,1,1]])
lincode = LinearCode()
lincode.G = m1
lincode.H = m2
lincode.parameters()
>>> .
    .
    .
elements = lincode.get_code_elements()
print(elements)
>>> {'[0 0 0 0 0 0]': (0, 0), '[0 1 1 0 1 1]': (0, 1), '[0 1 1 1 0 0]': (1, 0), '[0 0 0 1 1 1]': (1, 1)}
```
</details>

### Calculating the code parameters
In order to calculate the code parameters, the generator matrix G or the control matrix H must be known. If neither is available, the calculation is not possible.

The parameters that can be derived from these matrices are `n`, `k`, `M`, and `d`. Given that the dimension of the matrix G is `k x n`, and that the dimension of H is `(n-k) x n`, the first two parameters can be derived.

In the case of `M`, it can be calculated from the parameter `k`, since it results in `2^k`.

In the case of `d`, it can be calculated in several ways:
* By checking the ratio between the different columns of the matrix H (more details in **Calculating the minimum Hamming Distance (d)**).
* By finding the minimum weight (bits to 1) between the elements of the code.

In this case, the first option has been chosen, as it is a faster way to calculate the parameter.

Once `d` has been calculated, the last two parameters can be obtained: the `error detection capability` and `error correction capability`. For the first one, it is obtained by `d - 1`, and for the second one by `(d - 1) / 2` truncating in case there are decimals.

To calculate all the parameters, the following method has been used:

<details>
  <summary><b>LinearCode.parameters()</b></summary>
 It calculates the parameters as explained above, and prints them on the screen. In addition, it assigns them to the corresponding attributes of the instance.

 ```python
 code = LinearCode(G=Matriu.eye(3), H=Matriu.eye(3), n=3, k=2, M=5, d=3)
 code.parameters()
 >>> Linear Code Parameters:
     - Code Length (n): 3
     - Code Dimension (k): 3
     - Code Size (M): 8
     - Delta (d): 3
     - Error Detection: 2
     - Error Correction: 1
 ```
</details>

### Codifying messages
To encode a message, it must be split into blocks of size `k`, and multiply each one by the generator matrix G of the linear code. In this way, the encoded message is obtained.

For this, the following method is used:

<details>
  <summary><b>LinearCode.codify(bits)</b></summary>
 From a `list` or `string` of bits corresponding to the message, it is splitted into blocks of size `k` with the `_split_bits_in_blocks()` method, and each of them is multiplied by the matrix G. Then, the encoded blocks are concatenated in a `string` which is returned.

The `_split_bits_in_blocks()` method is used to split the message into blocks.

```python
m1 = Matriu([[0,1,1,1,0,0],[0,1,1,0,1,1]])
m2 = Matriu([[0,1,0,1,1,0], [1,0,0,0,1,1], [0,1,1,0,1,1], [0,0,0,0,1,1]])
lincode = LinearCode()
lincode.G = m1
lincode.H = m2
lincode.parameters()
>>> .
    .
    .
print(lincode.codify("10100111101001"))
>>> 011100011100011011000111011100011100011011
```
</details>

### Decoding messages and detecting/correcting errors
The opposite operation to the previous one is to decode the messages. Also, in this process, errors can be detected and corrected.

To decode, the coded message must be divided into blocks of size `n`. Once split, possible errors must be detected. To do so, the syndrome is calculated, as explained in the introduction: each block is multiplied by the control matrix H.

In case the syndrome results in 0, each block is decoded looking for its equivalent original message block.

If not, it means that an error has been detected. In order to correct it, the syndromes table must be calculated beforehand.

This table calculates the leading errors with a weight less than or equal to the `corrective capacity` for each possible syndrome. Then, when an error is found, it is searched to which leader corresponds to the obtained syndrome, and then the leader is subtracted from the block to be decoded.

Two methods have been developed in this section: one for decoding and detecting errors, and the other for decoding and correcting errors.

<details>
  <summary><b>LinearCode.decodify_detect(bits)</b></summary>
 From a `list` or `string` of bits corresponding to the encoded message, the message is split into blocks of size `n` with the **_split_bits_in_blocks()** method, and the syndrome is calculated for each of them. In case there are no errors, the block is decoded from the dictionary of code elements, and the block is concatenated into the resulting `string`.

 In case of errors, the `?` character is concatenated `?` `k` times.

 ```python
m1 = Matriu([[0,1,1,1,0,0],[0,1,1,0,1,1]])
m2 = Matriu([[0,1,0,1,1,0], [1,0,0,0,1,1], [0,1,1,0,1,1], [0,0,0,0,1,1]])
lincode = LinearCode()
lincode.G = m1
lincode.H = m2
lincode.parameters()
>>> .
    .
    .
print(lincode.decodify_detect("011011000010010011011110111100000000010000"))
>>> 01????????00??
```
</details>

<details>
  <summary><b>LinearCode.decodify_correct(bits)</b></summary>
 From a `list` or `string` of bits corresponding to the encoded message, is performed practically the same as in the previous method, but in this case, the table of syndromes is calculated beforehand.

 To do so, a similar procedure is followed as for obtaining the elements of the code. The possible leaders of weight less or equal to the `corrective capacity` are generated with the `itertools` library, and each one is multiplied by the control matrix H. Then, the table is stored in a dictionary, where the key is the syndrome, and the value is the leader.

In addition, unlike the previous method, if an error is detected, the syndrome is looked up in the syndromes table and the corresponding leader is subtracted from the block to be decoded.

 ```python
m1 = Matriu([[0,1,1,1,0,0],[0,1,1,0,1,1]])
m2 = Matriu([[0,1,0,1,1,0], [1,0,0,0,1,1], [0,1,1,0,1,1], [0,0,0,0,1,1]])
lincode = LinearCode()
lincode.G = m1
lincode.H = m2
lincode.parameters()
>>> .
    .
    .
print(lincode.decodify_detect("011011000010010011011110111100000000010000"))
>>> 01000110100000
```
</details>

### LC_Solver
It represents a Linear Code calculator, which, starting from an instance of Matrix, can its base, its control matrix, and from these, all the parameters of the linear code.

This class has only one attribute: a linear code, which corresponds to an instance of LinearCode.

The methods included in the class are detailed below.

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
The minimum Hamming distance (`d`) corresponds to the minimum number of bits by which two elements of a linear code differ.

It can be calculated from the control matrix `H`, a procedure which has been implemented as a method of this class.

This procedure consists of observing the relationship between the different columns that make up the control matrix `H`. The value of the minimum Hamming distance can be any of the following:
* `d = 1`: if there is any column where all elements are 0.
* In case there is no null column, the combination of columns whose result is 0 is searched. In this case, `d` will be equal to the number of columns necessary for the result to be 0.
* In case there is no combination resulting in 0, `d` will be equal to the number of columns of the matrix `H` plus 1.

To implement this mechanism, a method has been designed to calculate the distance from the control matrix.

<details>
    <summary><b>LCSolver._min_Hamming_distance(Matrix)</b></summary>

  Given an instance of `Matrix` corresponding to the control matrix `H`, the minimum distance is returned as an `int`.

  The procedure is as follows:
  1. The number of columns of the `H` matrix is identified from the `shape` attribute of the `Matrix` instance.
  2. Loop the number of times corresponding to the number of columns in the matrix to find out how many columns are being added at any given time.
  3. Inside the first loop, a second loop is made in which a list is generated with all the combinations of columns from 0 to the number of columns that are grouped at this moment (depending on where the first loop goes). To make the combinations we use the ìtertools` library, specifically, the `combinations()` function. When we get this list of tuples, they are obtained from the `get_columns()` method of `Matrix` and added together.

  If a sum results in 0, the bulces are stopped and the index through which the first loop goes (corresponding to the number of columns that have been added to obtain 0) is returned. Otherwise, the total number of columns of the matrix plus 1 is returned.

   ```python
   H = Matriu([[1, 0, 1, 1], [0, 1, 1, 0]])
   LC_Solver._min_hamming_distance(H)
   >>> 2
   H = Matriu([[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]])
   LC_Solver._min_hamming_distance(H)
   4
   ```
</details>

#### Solving a Hamming Code

This class also incorporates a method to find a Hamming code. These codes have a `t` parameter, with which it is possible to calculate all their parameters, including the generator and control matrices.

In the case of the parameters, they are calculated as follows:
* `n = 2^t - 1`.
* M = 2^n`.
* `k = n - t` * `M = 2^n` * `k = n - t`

In the case of the control matrix `H`, it consists of a `(n - k) x n` matrix, where the columans correspond to all binary combinations of `t` bits, except the null combination.

In the case of the generator matrix `G`, it can be calculated from `H` in the same way as `G` is calculated from `H` in a linear code. This is because it uses the property of **dual codes**, where the `G` of one code is the `H` of the other. If we interpret the H that has been previously calculated as the `G` of the dual, we can calculate the `H` of this `G`, and we get the `G` of the Hamming code.

This implementation is found as part of a method of the `LCSolver` class. It is implemented as a class method; therefore, creating an instance of the class is not needed.

<details>
    <summary><b>LCSolver.Hamming(t)</b></summary>

  Given the parameter t, all parameters and matrices of the Hamming code are computed, and added to the returned code instance.

  To calculate the parameters, it is done in exactly the same way as explained above.

  In the case of `H`, an instance of `Matrix` is created, in which the binary numbers from 1 to t are generated and added as columns.

  In the case of `G`, it is calculated with the **calculate_H(H)** method, using the code duality property.
  > Two codes are said to be dual if one's generator matrix corresponds to the other's control matrix, and viceversa: `G1 = H2, G2 = H1`

  An example to obtain a Hamming code is shown below:

   ```python
   lc = LC_Solver.Hamming(2)
   lc.n
   >>> 3
   lc.M
   >>> 8
   lc.k
   >>> 1
   lc.d
   >>> 3
   lc.G
   >>> [[1, 1, 1]]
   lc.H
   >>> [[1, 1, 0], [1, 0, 1]]
   ```
</details>

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
