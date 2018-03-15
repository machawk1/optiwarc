#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.69])
AC_INIT([warcsum], [0.1], [archive@bibalex.org])
AM_INIT_AUTOMAKE
AC_CONFIG_SRCDIR([warcsum.c])
#AC_CONFIG_HEADERS([config.h])

# Checks for programs.
AC_PROG_CC
AM_PROG_CC_C_O

# Checks for libraries.
AC_CHECK_LIB([gzmulti], [gzmInflateInit])
AC_CHECK_LIB([crypto], [MD5_Init])
AC_CHECK_LIB([curl], [curl_version])
AC_CHECK_LIB([dl], [dlopen])
AC_CHECK_LIB([m], [logf])
AC_CHECK_LIB([mysqlclient], [mysql_close])
AC_CHECK_LIB([pthread], [pthread_mutex_init])
AC_CHECK_LIB([rt], [sched_yield])
AC_CHECK_LIB([config], [config_destroy])
AC_CHECK_LIB([z], [inflateReset2])

# Checks for header files.
AC_CHECK_HEADERS([stdlib.h string.h unistd.h])

# Checks for typedefs, structures, and compiler characteristics.
AC_CHECK_HEADER_STDBOOL
AC_TYPE_SIZE_T

# Checks for library functions.
AC_FUNC_MALLOC
AC_FUNC_REALLOC

AC_CONFIG_FILES([Makefile])
AC_OUTPUT
