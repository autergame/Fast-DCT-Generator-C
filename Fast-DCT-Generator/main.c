#define _USE_MATH_DEFINES
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <conio.h>

#include "generated\dct2.h"
#include "generated\dct4.h"
#include "generated\dct8.h"
#include "generated\dct16.h"
#include "generated\dct32.h"
#include "generated\dct64.h"
#include "generated\dct128.h"

void dct_1d_ref(float* dst, const float* src, int stridea, int strideb, const float* matrix, int block_size)
{
	for (int x = 0; x < block_size; x++)
	{
		for (int j = 0; j < block_size; j++)
		{
			float sum = 0.;
			for (int i = 0; i < block_size; i++)
				sum += matrix[j * block_size + i] * src[i * stridea];
			dst[j * stridea] = sum;
		}
		dst += strideb;
		src += strideb;
	}
}

void fdct_ref(float* dst, const float* src, const float* dct_matrix, int block_size)
{
	float* tmp = (float*)calloc(block_size * block_size, sizeof(float));
	dct_1d_ref(tmp, src, 1, block_size, dct_matrix, block_size);
	dct_1d_ref(dst, tmp, block_size, 1, dct_matrix, block_size);
	free(tmp);
}

void idct_ref(float* dst, const float* src, const float* dct_trp_matrix, int block_size)
{
	float* tmp = (float*)calloc(block_size * block_size, sizeof(float));
	dct_1d_ref(tmp, src, 1, block_size, dct_trp_matrix, block_size);
	dct_1d_ref(dst, tmp, block_size, 1, dct_trp_matrix, block_size);
	free(tmp);
}

void printffprintf(char* strout, int size, FILE* file, const char* format, ...)
{
	va_list _ArgList;
	__crt_va_start(_ArgList, format);
	_vsprintf_s_l(strout, size, format, NULL, _ArgList);
	__crt_va_end(_ArgList);
	printf(strout);
	fprintf(file, strout);
}

void check_output(const char* name, const float* ref, const float* out, int block_size, FILE* file, char* strout, int size)
{
	for (int i = 0; i < block_size * block_size; i++)
	{
		float diff = fabsf(ref[i] - out[i]);
		printffprintf(strout, size, file, "%s %dx%d  index: %5d  ref: %12.6f out: %12.6f diff: %8.6f\n",
			name, block_size, block_size, i, ref[i], out[i], diff);
	}
}

typedef void (*function_dct)(float*, const float*);

function_dct functions_fdct[7] = {
	&fdct_2x2,
	&fdct_4x4,
	&fdct_8x8,
	&fdct_16x16,
	&fdct_32x32,
	&fdct_64x64,
	&fdct_128x128,
};

function_dct functions_idct[7] = {
	&idct_2x2,
	&idct_4x4,
	&idct_8x8,
	&idct_16x16,
	&idct_32x32,
	&idct_64x64,
	&idct_128x128,
};

int main()
{
	FILE* file;
	fopen_s(&file, "output.txt", "w");

	char strout[256] = { '\0' };
	float* dct_matrix, *dct_trp_matrix, *ref_fdct, *ref_idct, *out_fdct, *out_idct, *dct_src;

	for (int index = 0; index < 7; index++)
	{
		int block_size = 1 << (index + 1);
		int block_size_full = block_size * block_size;

		dct_matrix = (float*)calloc(block_size_full, sizeof(float));
		dct_trp_matrix = (float*)calloc(block_size_full, sizeof(float));

		for (int i = 0; i < block_size; i++)
		{
			for (int j = 0; j < block_size; j++)
			{
				if (i == 0)
					dct_matrix[i * block_size + j] = 1 / sqrt(block_size);
				else
					dct_matrix[i * block_size + j] = sqrt(2.0 / block_size) * cos(((2 * j + 1) * i * M_PI) / (2 * block_size));
			}
		}

		for (int i = 0; i < block_size; i++)
		{
			for (int j = 0; j < block_size; j++)
			{
				dct_trp_matrix[i * block_size + j] = dct_matrix[j * block_size + i];
			}
		}

		ref_fdct = (float*)calloc(block_size_full, sizeof(float));
		ref_idct = (float*)calloc(block_size_full, sizeof(float));
		out_fdct = (float*)calloc(block_size_full, sizeof(float));
		out_idct = (float*)calloc(block_size_full, sizeof(float));

		dct_src = (float*)calloc(block_size_full, sizeof(float));
		for (int i = 0; i < block_size_full; i++)
			dct_src[i] = rand() % 256;

		printffprintf(strout, sizeof(strout), file, "FDCT IDCT %dx%d\n\n", block_size, block_size);

		fdct_ref(ref_fdct, dct_src, dct_matrix, block_size);
		functions_fdct[index](out_fdct, dct_src);
		check_output("FDCT", ref_fdct, out_fdct, block_size, file, strout, sizeof(strout));

		printffprintf(strout, sizeof(strout), file, "\n");

		idct_ref(ref_idct, ref_fdct, dct_trp_matrix, block_size);
		functions_idct[index](out_idct, out_fdct);
		check_output("IDCT", ref_idct, out_idct, block_size, file, strout, sizeof(strout));

		printffprintf(strout, sizeof(strout), file, "\n\n");

		free(dct_matrix);
		free(dct_trp_matrix);

		free(ref_fdct);
		free(ref_idct);
		free(out_fdct);
		free(out_idct);

		free(dct_src);
	}

	fclose(file);

	_getch();

	return 0;
}