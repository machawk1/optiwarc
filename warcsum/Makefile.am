bin_PROGRAMS = \
  warcsum \
  warccollres

warcsum_SOURCES = \
  warcsum.c

 man_MANS = \
  warcsum.1 \
  warccollres.1

warccollres_SOURCES = \
  warccollres.c

warccollres_CFLAGS= -I/usr/include/mysql -DBIG_JOINS=1 -fno-strict-aliasing

dist_bin_SCRIPTS = \
  warcsumproc \
  warcsumsplit


