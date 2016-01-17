#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.69])
AC_INIT([gzmulti], [0.1], [archive@bibalex.org])
AM_INIT_AUTOMAKE
LT_INIT
AC_CONFIG_SRCDIR([lib/gzmulti.h])
#AC_CONFIG_HEADERS([config.h])

# Checks for programs.
AC_PROG_CC

# Checks for libraries.
# FIXME: Replace `main' with a function in `-lz':
AC_CHECK_LIB([z], [main])

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.

AC_CONFIG_FILES([Makefile
                 lib/Makefile])
AC_OUTPUT
