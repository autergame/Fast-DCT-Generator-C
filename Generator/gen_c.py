import sys, re
import numpy as np
import sympy as sp
from math import sqrt
from collections import Counter

import plonka

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
		raise sp.ShapeError("Dimensions incorrect for legacy_dot: %s, %s" % (a.shape, b.shape))

def dotx(y, matrix, x, code):
	calc = legacy_dot(sp.Matrix(matrix), sp.Matrix(x))
	if not (isinstance(calc, list) or isinstance(calc, sp.Matrix)):
		calc = [calc]
	for ij in zip(y, calc):
		code.append(ij)
	return y

call_num = 0

def next_syms(x):
	n = len(x)
	global call_num
	prefix = 'x%x_' % call_num
	call_num += 1
	return sp.Matrix([sp.Symbol('%s%xx' % (prefix, i)) for i in range(n)])

def tfm_run(name, y, x, code, scale_factor=None):
	neq2_mat, n_delay, b, v1_tfm, v2_tfm, hvec_size_add, modified_matrix = plonka.tfm_props[name]
	n_orig = len(x)
	n = n_orig + n_delay
	n1 = n // 2
	if scale_factor is None:
		scale_factor = 1./sqrt(n>>modified_matrix)
	if n == 2:
		return dotx(y, scale_factor * neq2_mat, x, code)
	elif n >= 4:
		u = dotx(next_syms(x), plonka.sqrt2 * plonka.twiddle_m(n, b, modified_matrix), x, code)
		vsyms = next_syms(u)
		v1 = tfm_run(v1_tfm, vsyms[:n1+hvec_size_add], u[:n1+hvec_size_add], code, scale_factor)
		v2 = tfm_run(v2_tfm, vsyms[n1+hvec_size_add:], u[n1+hvec_size_add:], code, scale_factor)
		v = np.hstack((v1, v2))
		w = plonka.add_m(n, b, modified_matrix).dot(v)
		return dotx(y, plonka.permute_m(n_orig).T, w, code)
	assert False

def get_code(n, fn):
	global call_num
	call_num = 0
	x = sp.Matrix([sp.Symbol('src[%*d * stridea]' % (len(str(n)), i)) for i in range(n)])
	y = sp.Matrix([sp.Symbol('dst[%*d * stridea]' % (len(str(n)), i)) for i in range(n)])
	code = []
	tfm_run(fn, y, x, code)
	outcode = []
	aliases = {}
	for (dst, src) in code:
		dst = str(dst)

		print(src)

		# yeah well...
		src = str(src).replace('1.0*','')
		src = str(src).replace('*1.0','')

		applied = False
		# a*src[x * stridea] +- a*src[y * stridea] -> a * (x +- y)
		m = re.match(r'([0-9.-]+)\*(src\[[0-9 ]+ \* stridea\]) ([+-]) ([0-9.-]+)\*(src\[[0-9 ]+ \* stridea\])', src)
		if m:
			cst1, var1, sign, cst2, var2 = m.groups()
			if cst1 == cst2:
				src = '%.6ff * (%s %s %s)' % (float(cst1), var1, sign, var2)
				applied = True


		# a*src[x * stridea] +- b*src[y * stridea] -> a * src[x * stridea] +- b * src[y * stridea] 
		if applied == False:
			m = re.match(r'([0-9.-]+)\*(src\[[0-9 ]+ \* stridea\]) ([+-]) ([0-9.-]+)\*(src\[[0-9 ]+ \* stridea\])', src)
			if m:
				cst1, var1, sign, cst2, var2 = m.groups()
				src = '%.6ff * %s %s %.6ff * %s' % (float(cst1), var1, sign, float(cst2), var2)
				applied = True

		# a*src[x * stridea] -> a * src[x * stridea] 
		if applied == False:
			m = re.match(r'([0-9.-]+)\*(src\[[0-9 ]+ \* stridea\])', src)
			if m:
				cst1, var1 = m.groups()
				src = '%.6ff * %s' % (float(cst1), var1)
				applied = True
		
		# a*x +- a*y -> a * (x +- y)
		if applied == False:
			m = re.match(r'([0-9.-]+)\*(x[0-9a-f]+_[0-9a-f]+x) ([+-]) ([0-9.-]+)\*(x[0-9a-f]+_[0-9a-f]+x)', src)
			if m:
				cst1, var1, sign, cst2, var2 = m.groups()
				if cst1 == cst2:
					src = '%.6ff * (%s %s %s)' % (float(cst1), var1, sign, var2)
					applied = True

		# a*x +- b*z +- a*y -> a * (x +- y) +- b * z
		if applied == False:
			m = re.match(r'([0-9.-]+)\*(x[0-9a-f]+_[0-9a-f]+x) ([+-]) ([0-9.-]+)\*(x[0-9a-f]+_[0-9a-f]+x) ([+-]) ([0-9.-]+)\*(x[0-9a-f]+_[0-9a-f]+x)', src)
			if m:
				cst1, var1, sign2, cst3, var3, sign, cst2, var2 = m.groups()
				if cst1 == cst2:
					src = '%.6ff * (%s %s %s) %s %.6ff * %s' % (float(cst1), var1, sign, var2, sign2, float(cst3), var3)
					applied = True

		# a*x +- b*y -> a * x +- b * y 
		if applied == False:
			m = re.match(r'([0-9.-]+)\*(x[0-9a-f]+_[0-9a-f]+x) ([+-]) ([0-9.-]+)\*(x[0-9a-f]+_[0-9a-f]+x)', src)
			if m:
				cst1, var1, sign, cst2, var2 = m.groups()
				src = '%.6ff * %s %s %.6ff * %s' % (float(cst1), var1, sign, float(cst2), var2)
				applied = True

		# a*x -> a * x
		if applied == False:
			m = re.match(r'([0-9.-]+)\*(x[0-9a-f]+_[0-9a-f]+x)', src)
			if m:
				cst1, var1 = m.groups()
				src = '%.6ff * %s' % (float(cst1), var1)

		print('%s\n' % src)

		line = '%s = %s;' % (dst, src)
		if '[' not in dst:
			line = 'const float ' + line

		# drop no-op lines such as "const float a = b;" with aliases
		if re.match(r'^const float x[0-9a-f]+_[0-9a-f]+x = x[0-9a-f]+_[0-9a-f]+x;$', line):
			#outcode.append(indent + '//' + line)
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
		varnumbers.append('\tstatic const float %s = %*.6ff;' % (numvar[1], floatmaxsize, float(numvar[0])))

	varnumbersret = '\n'.join(varnumbers)

	return ret, varnumbersret

def write_dct_code(n, outsrcfile):
	outsrc = outsrcfile.replace('%BLOCK_SIZE%', str(n))
	fdct, fvars = get_code(n, 'cosII')
	idct, ivars = get_code(n, 'cosIII')
	outsrc = outsrc.replace('%VARS_FDCT%', fvars)
	outsrc = outsrc.replace('%CODE_FDCT%', fdct)
	outsrc = outsrc.replace('%VARS_IDCT%', ivars)
	outsrc = outsrc.replace('%CODE_IDCT%', idct)
	open('../Fast-DCT-Generator/generated_dct/dct%d.h' % n, 'w').write(outsrc)
	open('../Fast-DCT-Generator/refs/fdct%d' % n, 'w').write(fdct)
	open('../Fast-DCT-Generator/refs/idct%d' % n, 'w').write(idct)

if __name__ == '__main__':
	outsrcfile = open('../Fast-DCT-Generator/template.h').read()
	write_dct_code(2, outsrcfile)
	write_dct_code(4, outsrcfile)
	write_dct_code(8, outsrcfile)
	write_dct_code(16, outsrcfile)
	write_dct_code(32, outsrcfile)
	write_dct_code(64, outsrcfile)
	write_dct_code(128, outsrcfile)
	write_dct_code(256, outsrcfile)
	write_dct_code(512, outsrcfile)