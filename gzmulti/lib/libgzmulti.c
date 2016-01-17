#include "gzmulti.h"

/*
 * This library is an offshoot of the initial gzmulti tool
 * implementation. The idea is to build an easy-to-use wrapper API for
 * working with multi-member GZIP files.
 *
 * In addition to using the initial gzmulti source code as reference,
 * consult the zlib manual:
 *
 * http://www.zlib.net/manual.html
 */

/* Initialize next_in, avail_in, zalloc, afree, and opaque z_stream
 * fields, then call inflateInit2 with windowBits = 31 [(default is 15)
 * + (16 for gzip header)].
 */
int
gzmInflateInit (z_stream *z)
{
  /* Internal state alloc/free. */
  z->zalloc = Z_NULL;
  z->zfree = Z_NULL;
  z->opaque = Z_NULL;

  /* Initialize  z variables */
  z->avail_in = 0;
  z->next_in = Z_NULL;

  /* Status returned by zlib functions. */
  int err;

  err = inflateInit2 (z, 31);

  if (err != Z_OK)
    {
      printf ("inflateInit error %d\n", err);
      return Z_ERRNO;
    }
  return err;
}

/*
 * Inflate one member then stop. It reads the input with max_in size and
 * output the decompressed data in max_out size. The callback function
 * pointer, procMember, will process the output data (decompressed
 * data). One of the easiest implementation of procMember (implemented
 * by caller) is to write the decompressed data to file.
 */
int
inflateMember (z_stream *z, FILE *fp, unsigned int max_in, unsigned int max_out, void (*procMember) (z_stream*, int, void*), void* userPointer)
//inflateMember (z_stream *z, FILE *fp, unsigned int max_in)

{
  /* Status returned by zlib functions. */
  int err;

  /* next_out and next_in  hold pointer to head of z->next_out and
   * z->next_in char arrays, respectively.
   */
  unsigned char* next_out = z->next_out;
  unsigned char* next_in = z->next_in;


  /* chunk initialization as CHUNK_FIRST */
  int chunk = CHUNK_FIRST;

  /* inflating the stream by reading fragments from input file, then
   * decompressing it till end of stream or end of file (err =
   * Z_STREAM_END).
   */
  do
    {
      z->next_in = next_in;
      /* avail_in = number of bytes read in z->next_in. */
      z->avail_in = fread (z->next_in, 1, max_in, fp);

      if (ferror (fp))
        {
          (void) inflateEnd (z);
          return Z_ERRNO;
        }
      if (z->avail_in == 0)
        {
          break;
        }
      do
        {
          /* bytes available (z->avail_out) at the beginning = max_out. */
          z->avail_out = max_out;
          /* run inflate() on input untill output buffer not full. That makes
           * inflate() continue working on the remaining, avail_in, till
           * z->avail_out!=0 which means that (there is a remaining free space
           * of next_out (z->avail_in=0)). That means the max_in bytes have
           * been read from file and finished decompression (free space in
           * z->next_out is an evidence). we need to read another block.
           */

          err = inflate (z, Z_NO_FLUSH);

          assert (err != Z_STREAM_ERROR);
          //printf ("current_position:%ld\t\terr:%d\tavail_in:%d\tavail_out:%d\tmsg:%s\n", ftell (fp), err, z->avail_in, z->avail_out, z->msg);
          switch (err)
            {
            case Z_NEED_DICT:
              err = Z_DATA_ERROR;
              return err;
            case Z_DATA_ERROR:
              return err;
            case Z_MEM_ERROR:
              (void) inflateEnd (z);
              return err;
            }
          z->next_out = next_out;
          /* When reached to the end of stream, Z_STREAM_END, we set chunk to
           * CHUNK_FIRST_LAST or CHUNK_LAST */
          if (z->avail_out != 0 && err == Z_STREAM_END)
            {
              if (chunk == CHUNK_FIRST)
                {
                  chunk = CHUNK_FIRST_LAST;
                }
              else if (chunk == CHUNK_MIDDLE)
                {
                  chunk = CHUNK_LAST;
                }
            }
          /* callback function, procMember. */
          procMember (z, chunk, userPointer);
          /* set chunk value as a middle chunk, CHUNK_MIDDLE */
          chunk = CHUNK_MIDDLE;
        }
      while (z->avail_out == 0 && err != Z_STREAM_END);
    }
  while (err != Z_STREAM_END);

  /* Return to the head of the next stream by moving f_read pointer back
   * by -1 * zstr.avail_in from the current position, SEEK_CUR.
   */
  fseek (fp, -1 * (int) z->avail_in, SEEK_CUR);
  //  printf ("current_position:%ld\t\terr:%d\tavail_in:%d\tavail_out:%d\tmsg:%s\n\n", ftell (fp), err, z->avail_in, z->avail_out, z->msg);
  z->next_in = next_in;
  z->next_out = next_out;
  return err;
}