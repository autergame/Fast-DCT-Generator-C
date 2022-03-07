// GENERATED CODE
// FDCT IDCT 8x8

inline void fdct_1d_8x8(float *dst, const float *src,
	int dst_stridea, int dst_strideb, int src_stridea, int src_strideb)
{
	for (int i = 0; i < 8; i++)
	{
		const float x00 = src[0 * src_stridea] + src[7 * src_stridea];
		const float x01 = src[1 * src_stridea] + src[6 * src_stridea];
		const float x02 = src[2 * src_stridea] + src[5 * src_stridea];
		const float x03 = src[3 * src_stridea] + src[4 * src_stridea];
		const float x04 = src[0 * src_stridea] - src[7 * src_stridea];
		const float x05 = src[1 * src_stridea] - src[6 * src_stridea];
		const float x06 = src[2 * src_stridea] - src[5 * src_stridea];
		const float x07 = src[3 * src_stridea] - src[4 * src_stridea];
		const float x08 = x00 + x03;
		const float x09 = x01 + x02;
		const float x0a = x00 - x03;
		const float x0b = x01 - x02;
		const float x0c = 1.38703984532215f * x04 + 0.275899379282943f * x07;
		const float x0d = 1.17587560241936f * x05 + 0.785694958387102f * x06;
		const float x0e = -0.785694958387102f * x05 + 1.17587560241936f * x06;
		const float x0f = 0.275899379282943f * x04 - 1.38703984532215f * x07;
		const float x10 = 0.353553390593274 * (x0c - x0d);
		const float x11 = 0.353553390593274 * (x0e - x0f);
		dst[0 * dst_stridea] = 0.353553390593274 * (x08 + x09);
		dst[1 * dst_stridea] = 0.353553390593274 * (x0c + x0d);
		dst[2 * dst_stridea] = 0.461939766255643f * x0a + 0.191341716182545f * x0b;
		dst[3 * dst_stridea] = 0.707106781186547 * (x10 - x11);
		dst[4 * dst_stridea] = 0.353553390593274 * (x08 - x09);
		dst[5 * dst_stridea] = 0.707106781186547 * (x10 + x11);
		dst[6 * dst_stridea] = 0.191341716182545f * x0a - 0.461939766255643f * x0b;
		dst[7 * dst_stridea] = 0.353553390593274 * (x0e + x0f);
		dst += dst_strideb;
		src += src_strideb;
	}
}

void fdct_8x8(float *dst, const float *src)
{
	float tmp[8 * 8] = { 0.f };
	fdct_1d_8x8(tmp, src, 1, 8, 1, 8);
	fdct_1d_8x8(dst, tmp, 8, 1, 8, 1);
}

inline void idct_1d_8x8(float *dst, const float *src,
	int dst_stridea, int dst_strideb, int src_stridea, int src_strideb)
{
	for (int i = 0; i < 8; i++)
	{
		const float x00 = 1.4142135623731f * src[0 * src_stridea];
		const float x01 = 1.38703984532215f * src[1 * src_stridea] + 0.275899379282943f * src[7 * src_stridea];
		const float x02 = 1.30656296487638f * src[2 * src_stridea] + 0.541196100146197f * src[6 * src_stridea];
		const float x03 = 1.17587560241936f * src[3 * src_stridea] + 0.785694958387102f * src[5 * src_stridea];
		const float x04 = 1.4142135623731f * src[4 * src_stridea];
		const float x05 = -0.785694958387102f * src[3 * src_stridea] + 1.17587560241936f * src[5 * src_stridea];
		const float x06 = 0.541196100146197f * src[2 * src_stridea] - 1.30656296487638f * src[6 * src_stridea];
		const float x07 = -0.275899379282943f * src[1 * src_stridea] + 1.38703984532215f * src[7 * src_stridea];
		const float x09 = x00 + x04;
		const float x0a = x01 + x03;
		const float x0b = 1.4142135623731f * x02;
		const float x0c = x00 - x04;
		const float x0d = x01 - x03;
		const float x0e = 0.353553390593274 * (x09 - x0b);
		const float x0f = 0.353553390593274 * (x0c + x0d);
		const float x10 = 0.353553390593274 * (x0c - x0d);
		const float x11 = 1.4142135623731f * x06;
		const float x12 = x05 + x07;
		const float x13 = x05 - x07;
		const float x14 = 0.353553390593274 * (x11 + x12);
		const float x15 = 0.353553390593274 * (x11 - x12);
		const float x16 = 0.5f * x13;
		const float x08 = -x15;
		dst[0 * dst_stridea] = 0.25f * (x09 + x0b) + 0.353553390593274f * x0a;
		dst[1 * dst_stridea] = 0.707106781186547 * (x0f - x08);
		dst[2 * dst_stridea] = 0.707106781186547 * (x0f + x08);
		dst[3 * dst_stridea] = 0.707106781186547 * (x0e + x16);
		dst[4 * dst_stridea] = 0.707106781186547 * (x0e - x16);
		dst[5 * dst_stridea] = 0.707106781186547 * (x10 - x14);
		dst[6 * dst_stridea] = 0.707106781186547 * (x10 + x14);
		dst[7 * dst_stridea] = 0.25f * (x09 + x0b) - 0.353553390593274f * x0a;
		dst += dst_strideb;
		src += src_strideb;
	}
}

void idct_8x8(float *dst, const float *src)
{
	float tmp[8 * 8] = { 0.f };
	idct_1d_8x8(tmp, src, 1, 8, 1, 8);
	idct_1d_8x8(dst, tmp, 8, 1, 8, 1);
}