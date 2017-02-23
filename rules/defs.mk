###
# Global configuration file for all makefiles.
#
# The variables in this file can be overridden in a file name config.local.mk
# exist in the ROOT directory.  Such a file should not be checked into the tree
#
# This should be sourced by setting the make variable ROOT to a relative path
# to the top of the tree and then including this file.
#
#    ROOT = ..
#    include ${ROOT}/rules/defs.mk
#    <local variable definitions>
#    ...
#    include ${ROOT}/rules/rules.mk
#    <local rules definitions>
#
# The following variables are defined to determine the targets of particular
# makefile:
#
#  LIBBASES - base name of objects to add to library (no directory or suffix).
#  LIB - Library that will contain objects from this build, in LIBDIR
#  SUBDIRS - subdirectories for recursive make
#  CPROGS = C programs to build
#  CXXPROGS = C+ programs to build
#  TESTCPROGS = test C programs to build
#  TESTCXXPROGS = test C++ programs to build
#  progName_PROGBASES = basename of non-library objects to link for $progName
#  PROG_LIBFILES = librarys file to add for all programs
#
# often useful to add (+=) to these variables are defs.mk is included
#   CFLAGS_INCL
#
# This requires GNU make.
###

MACHTYPE = $(shell uname -m)
SYS = $(shell uname -s)

BINDIR = ${ROOT}/bin
OBJDIR = ${ROOT}/objs
LIBDIR = ${ROOT}/lib
TESTBINDIR = ${ROOT}/testbin


##
# C/C++ compiler and language standard options
##
ifeq (${CC},cc)
    centos6_gcc = /opt/rh/devtoolset-3/root/usr/bin/gcc
    ifeq ($(SYS),Darwin)
        CC = clang -std=c99 
    else ifneq ($(wildcard ${centos6_gcc}),)
        CC = ${centos6_gcc} -std=c99
    else
        CC = gcc -std=c99
    endif

endif

ifeq (${CXX},c++)
    ifeq ($(SYS),Darwin)
        CXX = clang++
    else
        CXXX = g++ -std=gnu++11
    endif
endif

##
# Warning options.  Set WERROR=no to disable -Werror.
##
CFLAGS_WARN = -Wall --pedantic -Wno-error=unused-result
CXXFLAGS_WARN =  -Wall -Wno-error=unused-result --pedantic
ifneq (${WERROR},no)
    CFLAGS_WARN += -Werror
    CXXFLAGS_WARN += -Werror
endif


# Optimization flags.  The choice of optimization level is controled by the OPT variable.
# The following values are recognized:
#   opt - optimize
#   dbg = debug
#   dbg2 = added more debugging options to check memory, etc
#   prof = profling
ifeq (${OPT},)
    OPT = opt
endif

ifeq (${OPT},opt)
   CFLAGS_opt = -O3 -g -funroll-loops -DNDEBUG 
   CXXFLAGS_opt = -O3 -g -funroll-loops -DNDEBUG
else ifeq (${OPT},dbg)
   CFLAGS_dbg = -Wall -O0 -g -fno-inline -UNDEBUG -Wno-error=unused-result
   CCCFLAGS_dbg = -Wall -g -O0 -fno-inline -UNDEBUG
else ifeq (${OPT},dbg2)
   CFLAGS_dbg2 = -g -O1 -fno-inline -fno-omit-frame-pointer -fsanitize=address
   CXXFLAGS_dbg2 = -g -O1 -fno-inline -fno-omit-frame-pointer -fsanitize=address
else ifeq (${OPT},prof)
    CFLAGS_prof = -pg -O3 -g
    CXXFLAGS_prof = -pg -O3 -g
else
    $(error Unknown value for OPT: ${OPT})
endif


##
# assemble full set of flags
##
CFLAGS_VAR = CFLAGS_${OPT}
CXXFLAGS_VAR = CXXFLAGS_${OPT}

CFLAGS = ${${CFLAGS_VAR}} ${CFLAGS_WARN} ${CFLAGS_INCL}
CXXFLAGS = ${${CXXFLAGS_VAR}} ${CXXFLAGS_WARN} ${CXXFLAGS_INCL}



##
# programs and directories
##
addLib = ${ROOT}/btools/bin/addLib

sonlib_incldir = ${ROOT}/mods/sonLib/c/sonlib/inc
sonlib_lib = ${LIBDIR}/sonlib.a

cutest_incl = ${ROOT}/mods/sonLib/c/cutest
cutest_lib = ${LIBDIR}/cutest.a

# location of Tokyo cabinet
ifndef tokyoCabinetLib
ifneq ($(wildcard /hive/groups/recon/local/include/tcbdb.h),)
    # hgwdev hive install
    tcPrefix = /hive/groups/recon/local
    tokyoCabinetIncl = -I${tcPrefix}/include
    tokyoCabinetLib = -L${tcPrefix}/lib -Wl,-rpath,${tcPrefix}/lib -ltokyocabinet -lz -lbz2 -lpthread -lm
else ifneq ($(wildcard /opt/local/include/tcbdb.h),)
    # OS/X with TC installed from MacPorts
    tcPrefix = /opt/local
    tokyoCabinetIncl = -I${tcPrefix}/include -DHAVE_TOKYO_CABINET=1
    tokyoCabinetLib = -L${tcPrefix}/lib -Wl,-rpath,${tcPrefix}/lib -ltokyocabinet -lz -lbz2 -lpthread -lm
else ifneq ($(wildcard /usr/local/include/tcbdb.h),)
    # /usr/local install (FreeBSD, etc)
    tcPrefix = /usr/local
    tokyoCabinetIncl = -I${tcPrefix}/include -DHAVE_TOKYO_CABINET=1
    tokyoCabinetLib = -L${tcPrefix}/lib -Wl,-rpath,${tcPrefix}/lib -ltokyocabinet -lz -lbz2 -lpthread -lm
else ifneq ($(wildcard /usr/include/tcbdb.h),)
    # /usr install (Ubuntu, and probably most Debain-based systems)
    tcPrefix = /usr
    tokyoCabinetIncl = -I${tcPrefix}/include -DHAVE_TOKYO_CABINET=1
    tokyoCabinetLib = -L${tcPrefix}/lib -Wl,-rpath,${tcPrefix}/lib -ltokyocabinet -lz -lbz2 -lpthread -lm
endif
endif

# location of Kyoto Tycoon
ifndef kyotoTycoonLib
ifneq ($(wildcard /hive/groups/recon/local/include/ktcommon.h),)
    # hgwdev hive install
    ttPrefix = /hive/groups/recon/local
    kyotoTycoonIncl = -I${ttPrefix}/include -DHAVE_KYOTO_TYCOON=1
    kyotoTycoonLib = -L${ttPrefix}/lib -Wl,-rpath,${ttPrefix}/lib -lkyototycoon -lkyotocabinet -lz -lbz2 -lpthread -lm -lstdc++
else ifneq ($(wildcard /opt/local/include/ktcommon.h),)
    # OS/X with TC installed from MacPorts
    ttPrefix = /opt/local
    kyotoTycoonIncl = -I${ttPrefix}/include -DHAVE_KYOTO_TYCOON=1 
    kyotoTycoonLib = -L${ttPrefix}/lib -Wl,-rpath,${ttPrefix}/lib -lkyototycoon -lkyotocabinet -lz -lbz2 -lpthread -lm -lstdc++ 
else ifneq ($(wildcard /usr/local/include/ktcommon.h),)
    # /usr/local install (FreeBSD, etc)
    ttPrefix = /usr/local
    kyotoTycoonIncl = -I${ttPrefix}/include -DHAVE_KYOTO_TYCOON=1 
    kyotoTycoonLib = -L${ttPrefix}/lib -Wl,-rpath,${ttPrefix}/lib -lkyototycoon -lkyotocabinet -lz -lbz2 -lpthread -lm -lstdc++
else ifneq ($(wildcard /usr/include/ktcommon.h),)
   # /usr install (Ubuntu)
   ttPrefix = /usr
   kyotoTycoonIncl = -I${ttPrefix}/include -DHAVE_KYOTO_TYCOON=1 
   kyotoTycoonLib = -L${ttPrefix}/lib -Wl,-rpath,${ttPrefix}/lib -lkyototycoon -lkyotocabinet -lz -lbz2 -lpthread -lm -lstdc++
endif
endif
