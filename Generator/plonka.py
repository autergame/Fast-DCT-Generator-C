import numpy as np
import sympy as sp
from math import cos, sin, sqrt, pi

np.set_printoptions(precision=3, linewidth=999)

sqrt2 = sqrt(2)
sqrt1_2 = 1./sqrt(2)


def cos_k_pi_n(k, n): return cos(k*pi/n)
def sin_k_pi_n(k, n): return sin(k*pi/n)


def quad(a_b, c_d): return np.vstack((np.hstack(a_b),
                                      np.hstack(c_d)))


def quint(a, b, c, d, x):
    ah, aw = a.shape
    bh, bw = b.shape
    ch, cw = c.shape
    dh, dw = d.shape
    assert ah == bh and ch == dh and \
        aw == cw and bw == dw
    w = aw + 1 + bw
    h = ah + 1 + ch
    m = np.zeros((h, w))
    m[ah, aw] = x
    m[0:ah,  0:aw] = a
    m[0:bh,  aw+1:] = b
    m[ah+1:, 0:cw] = c
    m[bh+1:, cw+1:] = d
    return m


def diag(a, b=None):
    if b is None:
        return a * I(len(a))
    if isinstance(a, int) or isinstance(a, float):
        a = np.array([[a]])
    if isinstance(b, int) or isinstance(b, float):
        b = np.array([[b]])
    return quad((a, np.zeros((a.shape[0], b.shape[1]))),
                (np.zeros((b.shape[0], a.shape[1])), b))


def I(n): return np.identity(n, dtype=int)
def J(n): return np.fliplr(I(n))
def D(n): return diag(np.array([(-1)**k for k in range(n)]))


def permute_m(n):
    m = np.zeros((n, n))
    col = 0
    for i in range(n):
        m[i, col] = 1
        col += 2
        if col >= n:
            col = 1
    return m


def add_m(n, b, modified):
    if not modified:
        n1 = n // 2
        if b == 0:
            return I(n)
        elif b == 1:
            m = sqrt1_2 * quad((I(n1-1),  I(n1-1)),
                               (I(n1-1), -I(n1-1)))
            op1 = diag(diag(1, m), -1)
            op2 = diag(I(n1), D(n1).dot(J(n1)))
            return op1.dot(op2)
    else:
        n1 = n // 2
        if b == 1:
            return I(n + 1)
        elif b == 0:
            op1 = diag(I(n1), J(n1))
            op2m = quint(I(n1-1),  J(n1-1),
                         J(n1-1), -I(n1-1),
                         sqrt2)
            op2 = diag(1, sqrt1_2 * op2m)
            op3 = diag(I(n1+1), (-1)**n1 * D(n1-1))
            return op1.dot(op2).dot(op3)
        elif b == -1:
            return diag(D(n1), I(n1 - 1))
    assert False


def twiddle_m(n, b, modified):
    if not modified:
        n1 = n // 2
        if b == 0:
            return sqrt1_2 * quad((I(n1),  J(n1)),
                                  (I(n1), -J(n1)))
        elif b == 1:
            m00 = diag(c(n, n1))
            m01 = diag(s(n, n1)).dot(J(n1))
            m10 = (-J(n1)).dot(diag(s(n, n1)))
            m11 = diag(J(n1).dot(c(n, n1)))
            op1 = diag(I(n1), D(n1))
            op2 = quad((m00, m01), (m10, m11))
            return op1.dot(op2)
    else:
        n1 = n // 2
        if b == 1:
            return sqrt1_2 * quint(I(n1),  J(n1),
                                   I(n1), -J(n1),
                                   sqrt2)
        elif b == 0:
            op1 = diag(I(n1+1), D(n1-1))
            m00 = diag(ct(n, n1-1))
            m01 = diag(st(n, n1-1)).dot(J(n1-1))
            m10 = (-J(n1-1)).dot(diag(st(n, n1-1)))
            m11 = diag(J(n1-1).dot(ct(n, n1-1)))
            m = quint(m00, m01, m10, m11, 1)
            op2 = diag(1, m)
            return op1.dot(op2)
        elif b == -1:
            return diag(J(n1), I(n1-1)).dot(twiddle_m(n-1, b=1, modified=1))
    assert False


def c(n, n1): return [cos_k_pi_n(2*k+1, 4*n) for k in range(n1)]
def s(n, n1): return [sin_k_pi_n(2*k+1, 4*n) for k in range(n1)]
def ct(n, n1m1): return [cos_k_pi_n(k, 2*n) for k in range(1, n1m1+1)]
def st(n, n1m1): return [sin_k_pi_n(k, 2*n) for k in range(1, n1m1+1)]


def C_IV(n):
    m = []
    for j in range(n):
        m.append([(sqrt(2./n) * cos_k_pi_n((2*j+1)*(2*k+1), 4*n))
                 for k in range(n)])
    return np.array(m)


cosI_neq2_mat = 1./2 * (np.array([[1, 1, 0], [0, 0, sqrt2], [1, -1, 0]]).dot(
    np.array([[1, 0, 1], [0, sqrt2, 0], [1, 0, -1]])))
cosII_neq2_mat = np.array([[1,  1],
                           [1, -1]])
cosIII_neq2_mat = sqrt1_2 * np.array([[1,  1],
                                      [1, -1]])
cosIV_neq2_mat = sqrt2 * C_IV(2)
sinI_neq2_mat = I(1)

tfm_props = {
    'cosI':   (cosI_neq2_mat,   -1,  1, 'cosI',   'cosIII', 1, 1),
    'cosII':  (cosII_neq2_mat,   0,  0, 'cosII',  'cosIV',  0, 0),
    'cosIII': (cosIII_neq2_mat,  0,  0, 'cosI',   'sinI',   1, 1),
    'cosIV':  (cosIV_neq2_mat,   0,  1, 'cosII',  'cosII',  0, 0),
    'sinI':   (sinI_neq2_mat,	 1, -1, 'cosIII', 'sinI',   0, 1),
}


def tfm_run(name, y, x, code, scale_factor=None):
    neq2_mat, n_delay, b, v1_tfm, v2_tfm, hvec_size_add, modified_matrix = tfm_props[
        name]
    n_orig = len(x)
    n = n_orig + n_delay
    n1 = n // 2
    if scale_factor is None:
        scale_factor = 1./sqrt(n >> modified_matrix)
    if n == 2:
        return dotx(y, scale_factor * neq2_mat, x, code)
    elif n >= 4:
        u = dotx(next_syms(x), sqrt2 *
                 twiddle_m(n, b, modified_matrix), x, code)
        vsyms = next_syms(u)
        v1 = tfm_run(v1_tfm, vsyms[:n1+hvec_size_add],
                     u[:n1+hvec_size_add], code, scale_factor)
        v2 = tfm_run(v2_tfm, vsyms[n1+hvec_size_add:],
                     u[n1+hvec_size_add:], code, scale_factor)
        v = np.hstack((v1, v2))
        w = add_m(n, b, modified_matrix).dot(v)
        return dotx(y, permute_m(n_orig).T, w, code)
    assert False


call_num = 0


def next_syms(x):
    n = len(x)
    global call_num
    prefix = 'x%x_' % call_num
    call_num += 1
    return sp.Matrix([sp.Symbol('%s%xx' % (prefix, i)) for i in range(n)])


def dotx(y, matrix, x, code):
    calc = legacy_dot(sp.Matrix(matrix), sp.Matrix(x))
    if not (isinstance(calc, list) or isinstance(calc, sp.Matrix)):
        calc = [calc]
    for ij in zip(y, calc):
        code.append(ij)
    return y


def legacy_dot(a, b):
    if a.cols == b.rows:
        if b.cols != 1:
            a = a.T
            b = b.T
        return sp.flatten((a * b).tolist())
    if a.cols == b.cols:
        return a.dot(b.T)
    elif a.rows == b.rows:
        return a.T.dot(b)
    else:
        raise sp.ShapeError(
            "Dimensions incorrect for legacy_dot: %s, %s" % (a.shape, b.shape))
