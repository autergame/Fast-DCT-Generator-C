#define _USE_MATH_DEFINES
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <conio.h>
#include <Windows.h>

#include "generated_dct\dct2.h"
#include "generated_dct\dct4.h"
#include "generated_dct\dct8.h"
#include "generated_dct\dct16.h"
#include "generated_dct\dct32.h"
#include "generated_dct\dct64.h"
#include "generated_dct\dct128.h"
#include "generated_dct\dct256.h"
#include "generated_dct\dct512.h"


void DCT_function(const float* src, float* dst,
	const float* DCTTable, const float* alphaTable, int block_size, float block)
{
	for (int v = 0; v < block_size; v++)
	{
		for (int u = 0; u < block_size; u++)
		{
			float sum = 0.0f;
			for (int y = 0; y < block_size; y++)
			{
				for (int x = 0; x < block_size; x++)
				{
					float xu = DCTTable[x * block_size + u];
					float yv = DCTTable[y * block_size + v];

					int index = y * block_size + x;
					sum += src[index] * xu * yv;
				}
			}

			int index = v * block_size + u;
			dst[index] = alphaTable[index] * sum * block;
		}
	}
}

void inverse_DCT_function(const float* src, float* dst,
	const float* DCTTable, const float* alphaTable, int block_size, float block)
{
	for (int y = 0; y < block_size; y++)
	{
		for (int x = 0; x < block_size; x++)
		{
			float sum = 0.f;
			for (int v = 0; v < block_size; v++)
			{
				for (int u = 0; u < block_size; u++)
				{
					float xu = DCTTable[x * block_size + u];
					float yv = DCTTable[y * block_size + v];

					int index = v * block_size + u;
					sum += alphaTable[index] * src[index] * xu * yv;
				}
			}

			int index = y * block_size + x;
			dst[index] = sum * block;
		}
	}
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

void check_output(const char* name, const float* src, const float* ref, const float* out,
	int block_size, int block_size_full, FILE* file, char* strout, int size)
{
	float diffsum = 0;
	float diffpercentagesum = 0;

	float srcmax = 0, refmax = 0, outmax = 0;
	for (int i = 0; i < block_size_full; i++)
	{
		float srcabs = fabsf(src[i]);
		if (srcabs > srcmax)
			srcmax = srcabs;

		float refabs = fabsf(ref[i]);
		if (refabs > refmax)
			refmax = refabs;

		float outabs = fabsf(out[i]);
		if (outabs > outmax)
			outmax = outabs;
	}

	int srcdigits = (int)log10f(srcmax) + 9;
	int refdigits = (int)log10f(refmax) + 9;
	int outdigits = (int)log10f(outmax) + 9;

	int indexdigits = (int)log10(block_size_full) + 1;

	for (int i = 0; i < block_size_full; i++)
	{
		float diff = fabsf(ref[i] - out[i]);
		float average = (fabsf(ref[i]) + fabsf(out[i])) / 2.f;
		float diffpercentage = fabsf(diff / average) * 100.f;

		printffprintf(strout, size, file,
			"%s %dx%d index: %*d  src: %*.6f ref: %*.6f out: %*.6f  diff: %.6f %.6f%%%%\n",
			name, block_size, block_size,
			indexdigits, i, srcdigits, src[i], refdigits, ref[i], outdigits, out[i], diff, diffpercentage);

		diffsum += diff;
		diffpercentagesum += diffpercentage;
	}
	
	printffprintf(strout, size, file,
		"%s accumulated diff: %.6f %.6f%%%%\n\n",
		name, diffsum / block_size_full, diffpercentagesum / block_size_full);
}

typedef void (*function_dct)(const float*, float*);

function_dct functions_fdct[] = {
	&fdct_2x2,
	&fdct_4x4,
	&fdct_8x8,
	&fdct_16x16,
	&fdct_32x32,
	&fdct_64x64,
	&fdct_128x128,
	&fdct_256x256,
	&fdct_512x512
};

function_dct functions_idct[] = {
	&idct_2x2,
	&idct_4x4,
	&idct_8x8,
	&idct_16x16,
	&idct_32x32,
	&idct_64x64,
	&idct_128x128,
	&idct_256x256,
	&idct_512x512
};

void start_time_func(LARGE_INTEGER *start_time, LARGE_INTEGER *frequency)
{
	QueryPerformanceFrequency(frequency);
	QueryPerformanceCounter(start_time);
}

double stop_time_func(LARGE_INTEGER start_time, LARGE_INTEGER frequency)
{
	LARGE_INTEGER end_time;
	QueryPerformanceCounter(&end_time);
	return ((double)((end_time.QuadPart - start_time.QuadPart) * 1000000) / (double)frequency.QuadPart) / 1000.0;
}

int main()
{
	double elapsed = 0.0;
	LARGE_INTEGER start_time, frequency;

	FILE* file = NULL;
	fopen_s(&file, "output.txt", "w");

	char strout[256] = { '\0' };
	float* DCTTable, *alphaTable;
	float* ref_fdct, *ref_idct, *out_fdct, *out_idct, *dct_src;
	float sqrt1_2 = 1.f / sqrtf(2.f);

	int dctarraysize = sizeof(functions_fdct) / sizeof(function_dct);
	int dctarraysizeblocksize = 1 << dctarraysize;

	float* dct_src_max = (float*)calloc(dctarraysizeblocksize * dctarraysizeblocksize, sizeof(float));
	for (int i = 0; i < dctarraysizeblocksize * dctarraysizeblocksize; i++)
		dct_src_max[i] = (float)(rand() % 255) + 1.f;

	for (int index = 0; index < dctarraysize; index++)
	{
		int block_size = 1 << (index + 1);
		int block_size_full = block_size * block_size;
		float block = 2.f / (float)block_size;

		dct_src = (float*)calloc(block_size_full, sizeof(float));
		for (int y = 0; y < block_size; y++)
		{
			for (int x = 0; x < block_size; x++)
			{
				dct_src[y * block_size + x] = dct_src_max[y * dctarraysizeblocksize + x];
			}
		}

		DCTTable = (float*)calloc(block_size_full, sizeof(float));
		alphaTable = (float*)calloc(block_size_full, sizeof(float));

		start_time_func(&start_time, &frequency);
		for (int y = 0; y < block_size; y++)
		{
			for (int x = 0; x < block_size; x++)
			{
				DCTTable[y * block_size + x] = cosf((2.f * y + 1.f) * x * 3.141592f / (2.f * block_size));
			}
		}
		for (int y = 0; y < block_size; y++)
		{
			for (int x = 0; x < block_size; x++)
			{
				alphaTable[y * block_size + x] = (y == 0 ? sqrt1_2 : 1.f) * (x == 0 ? sqrt1_2 : 1.f);
			}
		}
		double dctalphatableelapsed = stop_time_func(start_time, frequency);

		ref_fdct = (float*)calloc(block_size_full, sizeof(float));
		ref_idct = (float*)calloc(block_size_full, sizeof(float));
		out_fdct = (float*)calloc(block_size_full, sizeof(float));
		out_idct = (float*)calloc(block_size_full, sizeof(float));

		printf("Generating FDCT\n");

		start_time_func(&start_time, &frequency);
		DCT_function(dct_src, ref_fdct, DCTTable, alphaTable, block_size, block);
		double fdctelapsedref = stop_time_func(start_time, frequency);

		start_time_func(&start_time, &frequency);
		functions_fdct[index](dct_src, out_fdct);
		double fdctelapsedout = stop_time_func(start_time, frequency);

		printf("Generating IDCT\n");

		start_time_func(&start_time, &frequency);
		inverse_DCT_function(ref_fdct, ref_idct, DCTTable, alphaTable, block_size, block);
		double idctelapsedref = stop_time_func(start_time, frequency);

		start_time_func(&start_time, &frequency);
		functions_idct[index](out_fdct, out_idct);
		double idctelapsedout = stop_time_func(start_time, frequency);

		printf("Finished\n\n");

		printffprintf(strout, sizeof(strout), file, "FDCT %dx%d\n", block_size, block_size);
		printffprintf(strout, sizeof(strout), file, "FDCT ref table time: %.6f ms\n", dctalphatableelapsed);
		printffprintf(strout, sizeof(strout), file, "FDCT ref total time: %.6f ms\n", fdctelapsedref);
		printffprintf(strout, sizeof(strout), file, "FDCT out total time: %.6f ms\n\n", fdctelapsedout);

		check_output("FDCT", dct_src, ref_fdct, out_fdct, block_size, block_size_full, file, strout, sizeof(strout));

		printffprintf(strout, sizeof(strout), file, "IDCT %dx%d\n", block_size, block_size);
		printffprintf(strout, sizeof(strout), file, "IDCT ref table time: %.6f ms\n", dctalphatableelapsed);
		printffprintf(strout, sizeof(strout), file, "IDCT ref total time: %.6f ms\n", idctelapsedref);
		printffprintf(strout, sizeof(strout), file, "IDCT out total time: %.6f ms\n\n", idctelapsedout);

		check_output("IDCT", ref_fdct, ref_idct, out_idct, block_size, block_size_full, file, strout, sizeof(strout));

		printffprintf(strout, sizeof(strout), file, "\n");

		free(DCTTable);
		free(alphaTable);

		free(ref_fdct);
		free(ref_idct);
		free(out_fdct);
		free(out_idct);

		free(dct_src);
	}

	free(dct_src_max);

	fclose(file);

	printf("Press any key to exit.\n");

	_getch();

	return 0;
}