// GENERATED CODE
// FDCT IDCT %BLOCK_SIZE%x%BLOCK_SIZE%

inline void fdct_1d_%BLOCK_SIZE%x%BLOCK_SIZE%(const float* src, float *out, int stridea, int strideb)
{
%VARS_FDCT%

	for (int i = 0; i < %BLOCK_SIZE%; i++)
	{
%CODE_FDCT%

		out += strideb;
		src += strideb;
	}
}

void fdct_%BLOCK_SIZE%x%BLOCK_SIZE%(const float* src, float *out)
{
	float* tmp = (float*)calloc(%BLOCK_SIZE% * %BLOCK_SIZE%, sizeof(float));
	fdct_1d_%BLOCK_SIZE%x%BLOCK_SIZE%(src, tmp, 1, %BLOCK_SIZE%);
	fdct_1d_%BLOCK_SIZE%x%BLOCK_SIZE%(tmp, out, %BLOCK_SIZE%, 1);
	free(tmp);
}

inline void idct_1d_%BLOCK_SIZE%x%BLOCK_SIZE%(const float* src, float *out, int stridea, int strideb)
{
%VARS_IDCT%

	for (int i = 0; i < %BLOCK_SIZE%; i++)
	{
%CODE_IDCT%

		out += strideb;
		src += strideb;
	}
}

void idct_%BLOCK_SIZE%x%BLOCK_SIZE%(const float* src, float *out)
{
	float* tmp = (float*)calloc(%BLOCK_SIZE% * %BLOCK_SIZE%, sizeof(float));
	idct_1d_%BLOCK_SIZE%x%BLOCK_SIZE%(src, tmp, 1, %BLOCK_SIZE%);
	idct_1d_%BLOCK_SIZE%x%BLOCK_SIZE%(tmp, out, %BLOCK_SIZE%, 1);
	free(tmp);
}