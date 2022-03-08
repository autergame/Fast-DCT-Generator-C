// GENERATED CODE
// FDCT IDCT %BLOCK_SIZE%x%BLOCK_SIZE%

inline void fdct_1d_%BLOCK_SIZE%x%BLOCK_SIZE%(float *dst, const float *src,
	int dst_stridea, int dst_strideb, int src_stridea, int src_strideb)
{
	for (int i = 0; i < %BLOCK_SIZE%; i++)
	{
%CODE_FDCT%
		dst += dst_strideb;
		src += src_strideb;
	}
}

void fdct_%BLOCK_SIZE%x%BLOCK_SIZE%(float *dst, const float *src)
{
	float* tmp = (float*)calloc(%BLOCK_SIZE% * %BLOCK_SIZE%, 4);
	fdct_1d_%BLOCK_SIZE%x%BLOCK_SIZE%(tmp, src, 1, %BLOCK_SIZE%, 1, %BLOCK_SIZE%);
	fdct_1d_%BLOCK_SIZE%x%BLOCK_SIZE%(dst, tmp, %BLOCK_SIZE%, 1, %BLOCK_SIZE%, 1);
	free(tmp);
}

inline void idct_1d_%BLOCK_SIZE%x%BLOCK_SIZE%(float *dst, const float *src,
	int dst_stridea, int dst_strideb, int src_stridea, int src_strideb)
{
	for (int i = 0; i < %BLOCK_SIZE%; i++)
	{
%CODE_IDCT%
		dst += dst_strideb;
		src += src_strideb;
	}
}

void idct_%BLOCK_SIZE%x%BLOCK_SIZE%(float *dst, const float *src)
{
	float* tmp = (float*)calloc(%BLOCK_SIZE% * %BLOCK_SIZE%, 4);
	idct_1d_%BLOCK_SIZE%x%BLOCK_SIZE%(tmp, src, 1, %BLOCK_SIZE%, 1, %BLOCK_SIZE%);
	idct_1d_%BLOCK_SIZE%x%BLOCK_SIZE%(dst, tmp, %BLOCK_SIZE%, 1, %BLOCK_SIZE%, 1);
	free(tmp);
}