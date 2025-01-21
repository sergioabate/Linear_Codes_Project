# Linear Codes in Action

- [Linear Codes in Action](#linear-codes-in-action)
  * [Introduction](#introduction)
  * [Program Structure](#program-structure)
    + [Row](#row)
    + [Matrix](#matrix)
    + [LinearCode](#linearcode)
      - [Computing all the elements of the code](#computing-all-the-elements-of-the-code)
      - [Calculating the code parameters](#calculating-the-code-parameters)
      - [Codifying messages](#codifying-messages)
      - [Decoding messages and detecting/correcting errors](#decoding-messages-and-detecting-correcting-errors)
    + [LC_Solver](#lc-solver)
      - [Calculating a base of a matrix (G)](#calculating-a-base-of-a-matrix--g-)
      - [Calculating a control matrix (H)](#calculating-a-control-matrix--h-)
      - [Calculating the minimum Hamming Distance (d)](#calculating-the-minimum-hamming-distance--d-)
      - [Solving a Hamming Code](#solving-a-hamming-code)
      - [Solving a linear code](#solving-a-linear-code)
    + [Testing](#testing)
  * [Examples](#examples)
    + [Example 1: computing the canonical and control matrices from three generators](#example-1--computing-the-canonical-and-control-matrices-from-three-generators)
    + [Example 2: computing the parameters of a linear code](#example-2--computing-the-parameters-of-a-linear-code)
    + [Example 3: codifying a message](#example-3--codifying-a-message)
    + [Example 4: detecting errors plus decodifying](#example-4--detecting-errors-plus-decodifying)
    + [Example 5: correcting errors plus decodifying](#example-5--correcting-errors-plus-decodifying)


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
<details>
  <summary><b>Row examples: </b></summary>
  <p>

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
  </p>
</details>

### Matrix
Represents a matrix. It implements basic arithmetic matrix operations, as well as boolean operations and row transformations (add/delete rows). It has been implemented to represent a matrix over the reals field; therefore, characteristics seen of linear codes over the F2 field do not apply in this class, as previously seen in `Row`.

It has two attributes:
* `Matrix.matrix:` a list of `Row` instances representing the matrix
* `Matrix.shape:` the dimensions of the matrix, represented as a tuple. `Matrix.shape[0]` is the number of rows, whereas  `Matrix.shape[1]` is the number of columns.

An example of using the most common methods (adding, subtracting, multiplying, adding elements, etc.) is as follows:

<details>
  <summary><b>Matrix examples: </b></summary>
  <p>

```python
from Matrix import Matrix

# Create matrix
m1 = Matriu([[1, 2, 3], [1, 2, 3]])
m2 = Matriu([[1, 2, 3], [1, 2, 3]])

# Addition
print(m1 + m2)
>>> [[2 4 6], [2 4 6]]

# Substraction
print(m1 - m2)
>>> [[0 0 0], [0 0 0]]

# Multiplication
print(m1 * m2)
>>> [6 12 18]
    [6 12 18]

# Modulus
print(m1 % 2)
>>> [1 0 1]

# Get item
print(m1[0])
>>> [1 2 3]

# Set item
m1[0] = [7, 8, 9]
print(m1[0])
>>> [7 8 9]

# Length
print(len(m1))
>>> 2

# Equality
print(Matrix([[1, 2, 3], [1, 2, 3]]) == Matrix([[1, 2, 3], [1, 2, 3]]))
>>> True
print(Matrix([[1, 2, 3], [1, 2, 3]]) == Matrix([[1, 2, 3], [1, 2, 1]]))
>>> False

# Bool
m1 = [[0, 0, 0], [0, 0, 0]]
bool(m1)
>>> False
m2 = [[2, 0, 0], [0, 0, 0]]
bool(m1)
>>> True

# Access and modify elements
print(r1[1])
>>> 2
r1[1] = 10
print(r1)
>>> [1 10 3]
```
  </p>
</details>

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

<details>
  <summary><b>Matrix.remove_row(row)</b></summary>
 Given a row index, removes it from the matrix. It returns a new matrix, with the given row removed.

 ```python
m1 = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
m1.remove_row(1)
>>> [[1, 2, 3], [7, 8, 9]]
m2 = Matrix([[10, 20], [30, 40], [50, 60]])
m2.remove_row(0)
>>> [[30, 40], [50, 60]]
m3 = Matrix([[1, 2], [3, 4]])
m3.remove_row(2)
>>> Traceback (most recent call last):
>>> ...
>>> IndexError: Row index out of bounds
 ```
</details>

<details>
  <summary><b>Matrix.add_row(row, pos)</b></summary>
 Given a row, and a position, returns a new matrix with the given row added at the given position.
 If no position is given, it is appended to the end.

 ```python
m1 = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
m1.add_row(Row([10, 11, 12]))
>>> [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]
m2 = Matrix([[1, 2], [3, 4], [5, 6]])
m2.add_row(Row([7, 8]), pos=1)
>>> [[1, 2], [7, 8], [3, 4], [5, 6]]
m3 = Matrix([[1, 2], [3, 4]])
m3.add_row([5, 6])
>>> Traceback (most recent call last):
>>>     ...
>>> ValueError: Invalid row type
 ```
</details>

<details>
  <summary><b>Matrix.add_column(column)</b></summary>
 Given a column, it returns a new matrix with it added to the end. Despite it being a column, a `Row` instance is expected.

 ```python
m1 = Matrix([[1, 2], [3, 4], [5, 6]])
m1.add_column(Row([7, 8, 9]))
>>> [[1, 2, 7], [3, 4, 8], [5, 6, 9]]
m2 = Matrix([[1, 2], [3, 4]])
m2.add_column(Row([5, 6]))
>>> [[1, 2, 5], [3, 4, 6]]
 ```
</details>

<details>
  <summary><b>Matrix.get_column(column)</b></summary>
 Given a column index, returns a `Row` instance with its elements being the column's values.

 ```python
m1 = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
m1.get_column(1)
>>> [2 5 8]
m2 = Matrix([[1, 2], [3, 4]])
m2.get_column(0)
>>>[1 3]
 ```
</details>

<details>
  <summary><b>Matrix.get_columns(columns)</b></summary>
 Given an iterable (list, tuple) of columns index, returns a list of `Row` instances with each row's elements being the column's values.

 ```python
m1 = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
m1.get_columns([0, 2])
>>> [[1 4 7], [3 6 9]]
m2 = Matrix([[1, 2], [3, 4], [5, 6]])
m2.get_columns((0, 1))
>>> [[1 3 5], [2 4 6]]
 ```
</details>

<details>
  <summary><b>Matrix.get_row(row)</b></summary>
 Given a row index, returns a `Row` instance of the matrix's row.

 ```python
m1 = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
m1.get_row(1)
>>> [4 5 6]
m2 = Matrix([[1, 2], [3, 4], [5, 6]])
m2.get_row(2)
>>> [5 6]
 ```
</details>

<details>
  <summary><b>Matrix.get_rows(rows)</b></summary>
 Given an iterable (list, tuple) of row indexes, returns a list of `Row` instances corresponding to the Matrix's rows

 ```python
m1 = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
m1.get_rows([0, 2])
>>> [[1 2 3], [7 8 9]]
m2 = Matrix([[1, 2], [3, 4], [5, 6]])
m2.get_rows((0, 1))
>>> [[1 2], [3 4]]
 ```
</details>

<details>
  <summary><b>Matrix.hstack(matrix)</b></summary>
    Horizontally stacks another matrix to the current matrix (i.e., appends columns of the second matrix to the self matrix).

 ```python
m1 = Matrix([[1, 2, 3], [4, 5, 6]])
m2 = Matrix([[7, 8], [9, 10]])
m1.hstack(m2)
>>> [[1, 2, 3, 7, 8], [4, 5, 6, 9, 10]]
m3 = Matrix([[1, 2], [3, 4], [5, 6]])
m4 = Matrix([[7, 8], [9, 10], [11, 12]])
m3.hstack(m4)
>>> [[1, 2, 7, 8], [3, 4, 9, 10], [5, 6, 11, 12]]
 ```
</details>

<details>
  <summary><b>Matrix.vstack(matrix)</b></summary>
    Vertically stacks another matrix to the current matrix (i.e., appends rows of the second matrix to the self matrix).

 ```python
m1 = Matrix([[1, 2, 3], [4, 5, 6]])
m2 = Matrix([[7, 8, 9], [10, 11, 12]])
m1.vstack(m2)
>>> [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]
m3 = Matrix([[1, 2], [3, 4], [5, 6]])
m4 = Matrix([[7, 8], [9, 10], [11, 12]])
m3.vstack(m4)
>>> [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]]
 ```
</details>

<details>
  <summary><b>Matrix.split(rows, columns)</b></summary>
    Splits the matrix into a submatrix defined by the given row and column slices.

 ```python
m1 = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
m1.split(slice(0, 2), slice(0, 2))
>>> [[1, 2], [4, 5]]
m2 = Matrix([[10, 11, 12, 13], [14, 15, 16, 17], [18, 19, 20, 21]])
m2.split(slice(1, 3), slice(2, 4))
>>> [[16, 17], [20, 21]]
 ```
</details>

These last methods are specially useful (and used) by the `LC_Solver` class to calculate the control matrix of a given matrix. Furthermore, they can also be useful to perform other matrix operations.

There are also 3 class methods (that is, no `Matrix` instance is needed to run them) considered to be _Helper Methods_:

<details>
  <summary><b>Matrix.eye(N)</b></summary>
      Creates an identity matrix of size N x N.

 ```python
Matrix.eye(3)
>>> [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
Matrix.eye(4)
>>> [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
Matrix.eye(2)
>>> [[1, 0], [0, 1]]
 ```
</details>

<details>
  <summary><b>Matrix.ones(N, M)</b></summary>
    Creates a matrix filled with ones of size N x M. If no `M` parameter is given, it defaults to a square matrix.

 ```python
Matrix.ones(3)
>>> [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
Matrix.ones(2, 4)
>>> [[1, 1, 1, 1], [1, 1, 1, 1]]
Matrix.ones(1, 5)
>>> [[1, 1, 1, 1, 1]]
Matrix.ones(4, 2)
>>> [[1, 1], [1, 1], [1, 1], [1, 1]]
 ```
</details>

<details>
  <summary><b>Matrix.zeros(N, M)</b></summary>
    Creates a matrix filled with zeros of size N x M. If no `M` parameter is given, it defaults to a square matrix.

 ```python
Matrix.zeros(3)
>>> [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
Matrix.zeros(2, 4)
>>> [[0, 0, 0, 0], [0, 0, 0, 0]]
Matrix.zeros(1, 5)
>>> [[0, 0, 0, 0, 0]]
Matrix.zeros(4, 2)
>>> [[0, 0], [0, 0], [0, 0], [0, 0]]
 ```
</details>

Again, these methods are useful to calculate the control matrix (specially when `G = (I | A)`, as it requries the identity matrix to be appended). They are also helpful to verify if two given G and H matrices are valid, as they must verify `G · H^t == 0`.

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
  <summary><b>LinearCode._split_bits_in_blocks(bits, size)</b></summary>
 Returns instances of `Matrix` corresponding to the blocks of the bit sequence.

 ```python
code = LinearCode(G=Matrix.eye(3), H=Matrix.eye(3), n=3, k=2, M=5, d=3)
list(code._split_bits_in_blocks([1, 0, 1, 1, 0, 0], 3))
>>> [[[1, 0, 1]], [[1, 0, 0]]]
 ```
</details>

Thanks to this method we can encode/decode messages according to the message size (`k`) and the code dimension (`M`).



#### Computing all the elements of the code
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
m1 = Matrix([[0,1,1,1,0,0],[0,1,1,0,1,1]])
m2 = Matrix([[0,1,0,1,1,0], [1,0,0,0,1,1], [0,1,1,0,1,1], [0,0,0,0,1,1]])
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

#### Calculating the code parameters
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
 code = LinearCode(G=Matrix.eye(3), H=Matrix.eye(3), n=3, k=2, M=5, d=3)
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

#### Codifying messages
To encode a message, it must be split into blocks of size `k`, and multiply each one by the generator matrix G of the linear code. In this way, the encoded message is obtained.

For this, the following method is used:

<details>
  <summary><b>LinearCode.codify(bits)</b></summary>
 From a `list` or `string` of bits corresponding to the message, it is splitted into blocks of size `k` with the `_split_bits_in_blocks()` method, and each of them is multiplied by the matrix G. Then, the encoded blocks are concatenated in a `string` which is returned.

The `_split_bits_in_blocks()` method is used to split the message into blocks.

```python
m1 = Matrix([[0,1,1,1,0,0],[0,1,1,0,1,1]])
m2 = Matrix([[0,1,0,1,1,0], [1,0,0,0,1,1], [0,1,1,0,1,1], [0,0,0,0,1,1]])
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

#### Decoding messages and detecting/correcting errors
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
m1 = Matrix([[0,1,1,1,0,0],[0,1,1,0,1,1]])
m2 = Matrix([[0,1,0,1,1,0], [1,0,0,0,1,1], [0,1,1,0,1,1], [0,0,0,0,1,1]])
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
m1 = Matrix([[0,1,1,1,0,0],[0,1,1,0,1,1]])
m2 = Matrix([[0,1,0,1,1,0], [1,0,0,0,1,1], [0,1,1,0,1,1], [0,0,0,0,1,1]])
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
Being able to obtain a base for a given matrix is a key operation in linear codes. As it has previsouly been said, a generator matrix is a base for all the codewords. Therefore, calculating the base should be the first operation performed. It is a public method of `LC_Solver`, **LC_Solver.calculate_base(Matrix)**. It is made public to allow users to calculate any matrix into its canonical form and, if possible, in its systematic form.

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
    <summary><b>LC_Solver._min_Hamming_distance(Matrix)</b></summary>

  Given an instance of `Matrix` corresponding to the control matrix `H`, the minimum distance is returned as an `int`.

  The procedure is as follows:
  1. The number of columns of the `H` matrix is identified from the `shape` attribute of the `Matrix` instance.
  2. Loop the number of times corresponding to the number of columns in the matrix to find out how many columns are being added at any given time.
  3. Inside the first loop, a second loop is made in which a list is generated with all the combinations of columns from 0 to the number of columns that are grouped at this moment (depending on where the first loop goes). To make the combinations we use the `itertools` library, specifically, the `combinations()` function. When we get this list of tuples, they are obtained from the `get_columns()` method of `Matrix` and added together.

  If a sum results in 0, the bulces are stopped and the index through which the first loop goes (corresponding to the number of columns that have been added to obtain 0) is returned. Otherwise, the total number of columns of the matrix plus 1 is returned.

  <p>

   ```python
   H = Matrix([[1, 0, 1, 1], [0, 1, 1, 0]])
   LC_Solver._min_hamming_distance(H)
   >>> 2
   H = Matrix([[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]])
   LC_Solver._min_hamming_distance(H)
   4
   ```
  </p>
</details>

#### Solving a Hamming Code

This class also incorporates a method to find a Hamming code. These codes have a `t` parameter, with which it is possible to calculate all their parameters, including the generator and control matrices.

In the case of the parameters, they are calculated as follows:
* `n = 2^t - 1`.
* `M = 2^n`.
* `k = n - t` * `M = 2^n` * `k = n - t`

In the case of the control matrix `H`, it consists of a `(n - k) x n` matrix, where the columans correspond to all binary combinations of `t` bits, except the null combination.

In the case of the generator matrix `G`, it can be calculated from `H` in the same way as `G` is calculated from `H` in a linear code. This is because it uses the property of **dual codes**, where the `G` of one code is the `H` of the other. If we interpret the H that has been previously calculated as the `G` of the dual, we can calculate the `H` of this `G`, and we get the `G` of the Hamming code.

This implementation is found as part of a method of the `LC_Solver` class. It is implemented as a class method; therefore, creating an instance of the class is not needed.

<details>
    <summary><b>LC_Solver.Hamming(t)</b></summary>

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
To ensure the correct functionality of all classes and their methods, tests have been implemented using Python's doctest module. This module allows tests to be written directly within the method's docstring, making the tests part of the documentation itself.

This approach makes testing more intuitive and user-friendly, as the examples serve a dual purpose: they showcase the method's usage while simultaneously verifying its behavior. By viewing the documentation, users can easily understand the method's functionality and see example inputs and outputs in one place.

Most of the examples seen in this documentation have been directly extracted from the implemented tests.

The correct functioning of all methods can be verified running:
```shell
python3 -m doctest Row.py Matrix.py LinearCode.py
```

## Examples
This section shows some examples of implementation to demonstrate how this works.

### Example 1: computing the canonical and control matrices from three generators
<!-- Un exemple de LC_Solver.solve() amb una matriu que representi una G amb format correcte -->
From the following generators, the generator and control matrices will be obtained.
```
v1 = [0 0 1 0 1]
v2 = [1 0 0 1 0]
v3 = [1 1 1 0 1]
```

```python
vectors = Matrix([
                [0,0,1,0,1],
                [1,0,0,1,0],
                [1,1,1,0,1]
               ])
solver = LC_Solver()
lincode = solver.solve(vectors)
print(lincode.G)
>>> [1 0 0 1 0]
    [0 1 0 1 0]
    [0 0 1 0 1]
print(lincode.H)
>>> [1 1 0 1 0]
>>> [0 0 1 0 1]
```

### Example 2: computing the parameters of a linear code
In this example, an instance of Linear Code is created, in which only its canonical generator matrix G is specified, and all parameters will be obtained from it.

The generator matrix is the following:
```
G = [1 0 0 1 0 1]
    [0 1 0 1 0 1]
    [0 0 1 0 0 1]
```

```python
G = Matrix([
            [1, 0, 0, 1, 0, 1],
            [0, 1, 0, 1, 0, 1],
            [0, 0, 1, 0, 0, 1]
            ])
solver = LC_Solver()
lincode = solver.solve(G)
print(lincode.G)
>>> [1 0 0 1 0 1]
    [0 1 0 1 0 1]
    [0 0 1 0 0 1]
lincode.parameters()
>>> Linear Code Parameters:
    - Code Length (n): 6
    - Code Dimension (k): 3
    - Code Size (M): 8
    - Delta (d): 2
    - Error Detection: 1
    - Error Correction: 0
```

### Example 3: codifying a message
In this example we will start with a generator matrix G, with which we will find all other parameters of the code and encode a message.

The generator matrix is the following:
```
G = [1 0 0 1 1 0 1]
    [0 1 0 0 1 0 1]
    [0 0 1 1 0 0 0]
```

The message to be coded is as follows: `100110100100111011011`.

```python
G = Matrix([
            [1, 0, 0, 1, 1, 0, 1],
            [0, 1, 0, 0, 1, 0, 1],
            [0, 0, 1, 1, 0, 0, 0]
            ])
solver = LC_Solver()
lincode = solver.solve(G)
print(lincode.G)
>>> [1 0 0 1 1 0 1]
    [0 1 0 0 1 0 1]
    [0 0 1 1 0 0 0]
print(lincode.codify("100110100100111011011"))
>>> 1001101110100010011011001101111000001111010111101
```

### Example 4: detecting errors plus decodifying
In this example, a generator matrix G will be used to find all other parameters of the code and decode a message, detecting possible errors.

The generator matrix is the following:
```
G = [1 0 0 0 1 1 0]
    [0 1 0 0 1 0 1]
    [0 0 1 0 0 1 1]
    [0 0 0 1 1 1 1]
```

The message to be decoded is as follows: `10110100101011`.

```python
G = Matrix([
            [1, 0, 0, 0, 1, 1, 0],
            [0, 1, 0, 0, 1, 0, 1],
            [0, 0, 1, 0, 0, 1, 1],
            [0, 0, 0, 1, 1, 1, 1]
            ])
solver = LC_Solver()
lincode = solver.solve(G)
print(lincode.G)
>>> [1 0 0 0 1 1 0]
    [0 1 0 0 1 0 1]
    [0 0 1 0 0 1 1]
    [0 0 0 1 1 1 1]
print(lincode.decodify_detect("10110100101011"))
>>> 1011????
```

### Example 5: correcting errors plus decodifying
In this example, the same generator matrix G as before will be used to find all other parameters of the code and decode a message, correcting possible errors.

The generator matrix is the following:
```
G = [1 0 0 0 1 1 0]
    [0 1 0 0 1 0 1]
    [0 0 1 0 0 1 1]
    [0 0 0 1 1 1 1]
```

The message to be decoded is as follows: `10110100101011`.

```python
G = Matrix([
            [1, 0, 0, 0, 1, 1, 0],
            [0, 1, 0, 0, 1, 0, 1],
            [0, 0, 1, 0, 0, 1, 1],
            [0, 0, 0, 1, 1, 1, 1]
            ])
solver = LC_Solver()
lincode = solver.solve(G)
print(lincode.G)
>>> [1 0 0 0 1 1 0]
    [0 1 0 0 1 0 1]
    [0 0 1 0 0 1 1]
    [0 0 0 1 1 1 1]
print(lincode.decodify_correct("10110100101011"))
>>> 10110101
```

### Example 6: using a Hamming Code
In this example a Hamming Code is obtained using the helper functions defined in `LC_Solver`.

```python
ham_code = LC_Solver.Hamming(3)
print(ham_code.H)
>>> [1 1 1 1 0 0 0]
    [1 1 0 0 1 1 0]
    [1 0 1 0 1 0 1]
```

The control matrix can also be written in systematic form, using `LC_Solver.calculate_base()`:
```python
H_syst = LC_Solver.calculate_base(ham_code.H)
print(H_syst)
>>> [1 0 0 1 0 1 1]
    [0 1 0 1 1 0 1]
    [0 0 1 1 1 1 0]
```
