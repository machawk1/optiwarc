#ifndef __GZMULTI_H__
#define __GZMULTI_H__

#include <stdio.h>
#include <zlib.h>
#include <string.h>
#include <assert.h>
#include <time.h>

#define CHUNK_FIRST 0
#define CHUNK_MIDDLE 1
#define CHUNK_LAST 2
#define CHUNK_FIRST_LAST 3

extern int gzmInflateInit (z_stream *z);
inflateMember (z_stream *z, FILE *fp, unsigned int max_in, unsigned int
max_out, void (*procMember) (z_stream*, int, void*), void* userPointer);
//extern int inflateMember (z_stream *z, FILE *fp, unsigned int max_in);
//extern int throw_stream (FILE*, z_stream);

#endif  /* __GZMULTI_H__ */
