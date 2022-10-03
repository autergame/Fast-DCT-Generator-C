import re
import sympy as sp
from collections import Counter

import plonka


def get_code(n, fn):
    plonka.call_num = 0
    nlen = len('%x' % n)
    x = sp.Matrix([sp.Symbol('s_%0*X' % (nlen, i)) for i in range(n)])
    y = sp.Matrix([sp.Symbol('out[%*d * stridea]' % (len(str(n)), i))
                  for i in range(n)])
    code = []
    plonka.tfm_run(fn, y, x, code)
    outcode = []
    aliases = {}
    for (dst, src) in code:
        dst = str(dst)

        # print(src)

        # yeah well...
        src = str(src).replace('1.0*', '')
        src = str(src).replace('*1.0', '')

        applied = False
        # a*s_x +- a*s_y -> a * (x +- y)
        m = re.match(
            r'([0-9.-]+)\*(s_[0-9A-F]+) ([+-]) ([0-9.-]+)\*(s_[0-9A-F]+)', src)
        if m:
            cst1, var1, sign, cst2, var2 = m.groups()
            if cst1 == cst2:
                src = '%.6ff * (%s %s %s)' % (float(cst1), var1, sign, var2)
                applied = True

        # a*s_x +- b*s_y -> a * s_x +- b * s_y
        if applied == False:
            m = re.match(
                r'([0-9.-]+)\*(s_[0-9A-F]+) ([+-]) ([0-9.-]+)\*(s_[0-9A-F]+)', src)
            if m:
                cst1, var1, sign, cst2, var2 = m.groups()
                src = '%.6ff * %s %s %.6ff * %s' % (
                    float(cst1), var1, sign, float(cst2), var2)
                applied = True

        # a*s_x -> a * s_x
        if applied == False:
            m = re.match(r'([0-9.-]+)\*(s_[0-9A-F]+)', src)
            if m:
                cst1, var1 = m.groups()
                src = '%.6ff * %s' % (float(cst1), var1)
                applied = True

        # a*x +- a*y -> a * (x +- y)
        if applied == False:
            m = re.match(
                r'([0-9.-]+)\*(x[0-9a-f]+_[0-9a-f]+x) ([+-]) ([0-9.-]+)\*(x[0-9a-f]+_[0-9a-f]+x)', src)
            if m:
                cst1, var1, sign, cst2, var2 = m.groups()
                if cst1 == cst2:
                    src = '%.6ff * (%s %s %s)' % (float(cst1),
                                                  var1, sign, var2)
                    applied = True

        # a*x +- b*z +- a*y -> a * (x +- y) +- b * z
        if applied == False:
            m = re.match(
                r'([0-9.-]+)\*(x[0-9a-f]+_[0-9a-f]+x) ([+-]) ([0-9.-]+)\*(x[0-9a-f]+_[0-9a-f]+x) ([+-]) ([0-9.-]+)\*(x[0-9a-f]+_[0-9a-f]+x)', src)
            if m:
                cst1, var1, sign2, cst3, var3, sign, cst2, var2 = m.groups()
                if cst1 == cst2:
                    src = '%.6ff * (%s %s %s) %s %.6ff * %s' % (float(cst1),
                                                                var1, sign, var2, sign2, float(cst3), var3)
                    applied = True

        # a*x +- b*y -> a * x +- b * y
        if applied == False:
            m = re.match(
                r'([0-9.-]+)\*(x[0-9a-f]+_[0-9a-f]+x) ([+-]) ([0-9.-]+)\*(x[0-9a-f]+_[0-9a-f]+x)', src)
            if m:
                cst1, var1, sign, cst2, var2 = m.groups()
                src = '%.6ff * %s %s %.6ff * %s' % (
                    float(cst1), var1, sign, float(cst2), var2)
                applied = True

        # a*x -> a * x
        if applied == False:
            m = re.match(r'([0-9.-]+)\*(x[0-9a-f]+_[0-9a-f]+x)', src)
            if m:
                cst1, var1 = m.groups()
                src = '%.6ff * %s' % (float(cst1), var1)

        # print('%s\n' % src)

        line = '%s = %s;' % (dst, src)
        if '[' not in dst:
            line = 'const float ' + line

        # drop no-op lines such as "const float a = b;" with aliases
        if re.match(r'^const float x[0-9a-f]+_[0-9a-f]+x = x[0-9a-f]+_[0-9a-f]+x;$', line):
            aliases[dst] = aliases.get(src, src)
            continue

        # apply any aliases
        for var, rep in aliases.items():
            line = line.replace(var, rep)

        line = '\t\t' + line
        outcode.append(line)
    ret = '\n'.join(outcode)

    # look for simple indirections (one assignement, one use)
    var_histogram = Counter(re.findall(r'x[0-9a-f]+_[0-9a-f]+x', ret))
    simple_vars = [key for key, val in var_histogram.items() if val == 2]

    # when the use of this variable is as simple as a = b, replace with the
    # original value
    for var in simple_vars:
        outcode2 = []
        for line in outcode:
            if ' = %s;' % var in line:
                for line2 in outcode:
                    if var in line2:
                        data = line2.split('=')[1]
                        break
                dst, src = line.split('=')
                line = dst + '=' + data
            outcode2.append(line)
        outcode = outcode2
    ret = '\n'.join(outcode)

    # now that the indirection is removed, remove the original assignment which
    # is now unused
    var_histogram = Counter(re.findall(r'x[0-9a-f]+_[0-9a-f]+x', ret))
    orphan_vars = [key for key, val in var_histogram.items() if val == 1]
    for orphan in orphan_vars:
        outcode = [line for line in outcode if orphan not in line]
    ret = '\n'.join(outcode)

    slen = len(str(n))
    srcvars = []
    for i in range(n):
        srcvars.append(
            '\t\tconst float s_%0*X = src[%*d * stridea];' % (nlen, i, slen, i))
    ret = '\n'.join(srcvars) + '\n\n' + ret

    # symbol indexing and renaming
    varsfrom = sorted(set(re.findall(r'x[0-9a-f]+_[0-9a-f]+x', ret)))
    nb_var = len(varsfrom)
    varsto = ['x_%0*X' % (len('%x' % nb_var), x) for x in range(nb_var)]
    for var_from, var_to in zip(varsfrom, varsto):
        ret = ret.replace(var_from, var_to)

    numbers = re.findall(r'[^x_]([0-9.-]+)f', ret)
    nlist = list(set(numbers))

    maxvarsize = len(str('%x' % len(nlist)))

    nvlist = []
    nvindex = 0
    for num in nlist:
        nvlist.append([num, 'v_%0*X' % (maxvarsize, nvindex)])
        nvindex += 1

    floatmaxsize = 0
    for numvar in nvlist:
        floatlen = len(numvar[0])
        if floatlen > floatmaxsize:
            floatmaxsize = floatlen

    varnumbers = []
    for numvar in nvlist:
        ret = ret.replace(numvar[0] + 'f', numvar[1])
        varnumbers.append('\tstatic const float %s = %*.6ff;' %
                          (numvar[1], floatmaxsize, float(numvar[0])))

    if varnumbers != []:
        varnumbersret = '\n'.join(varnumbers)

    fro = re.search(r'(;)(\n\t\t)(out\[[0 ]+ \* stridea\])', ret)
    if fro:
        c, ntt, out = fro.groups()
        ret = ret.replace(c + ntt + out, c + '\n' + ntt + out)

    return ret, varnumbersret


def write_dct_code(n, template):
    print('Generating %d' % n)
    print('\tGenerating fast DCT')
    fdct, fvars = get_code(n, 'cosII')
    print('\tGenerating fast IDCT')
    idct, ivars = get_code(n, 'cosIII')
    templatestr = template
    templatestr = templatestr.replace('%BLOCK_SIZE%', str(n))
    templatestr = templatestr.replace('%VARS_FDCT%', fvars)
    templatestr = templatestr.replace('%CODE_FDCT%', fdct)
    templatestr = templatestr.replace('%VARS_IDCT%', ivars)
    templatestr = templatestr.replace('%CODE_IDCT%', idct)
    open('../generated_dct/dct%d.h' % n, 'w').write(templatestr)


if __name__ == '__main__':
    template = open('template.h').read()
    for i in range(1, 10):
        write_dct_code(1 << i, template)
