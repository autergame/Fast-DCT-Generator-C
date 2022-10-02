# Fast-DCT-Generator-C
Python based Fast DCT (FDCT) and Fast Inverse DCT (FIDCT) generator for several dimensions to C and C++

## Help From:
* https://github.com/ubitux/dct

## From ubitux

```
Experiment: trying to implement a generic fast DCT II/III based on "Fast and
numerically stable algorithms for discrete cosine transforms" from Gerlind
Plonka & Manfred Tasche (DOI: 10.1016/j.laa.2004.07.015).

• plonka.py contains the litteral implementation of the algorithms (recursive
  form) presented in the paper.
• gen_c.py generates the unrolled C code to compute forward and inverse
  2D DCTs (DCT-II and DCT-III, scaled, floating point) for several dimensions
  (4x4, 8x8, 16x16, ...) using the maths in plonka.py. The 1D DCTs can be
  extracted from that code as well.

Running ``make'' will test the mathematics in plonka.py (test-plonka-*),
generates the C (including tests) for a few DCT (in dct*.c), compile them, and
run them as a test.
```
