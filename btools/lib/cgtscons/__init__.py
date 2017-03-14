"""
Definitions and functions use for building CGT
"""
from __future__ import print_function
import os
from SCons.Script import Copy, Chmod

##
# Notes:
#  - str() is called on directory and file names to allow them to be either strings
#    or Scons Node objects.
##



# module names
SONLIB_MOD_NAME = "sonLib"
CPECAN_MOD_NAME = "cPecan"
CACTUS_MOD_NAME = "cactus"


# library base names
SONLIB_LIB_NAME = "sonlib"
CUTEST_LIB_NAME = "cutest"
CPECAN_LIB_NAME = "cpecan"
CACTUS_LIB_NAME = "cactus"
STCAF_LIB_NAME  = "stcaf"
BLAST_LIB_NAME  = "blast"

##
# Access to module files
##
def _moduleGet(env, mod, fname=None):
    """get an module directory or file in that directory, which should be relative to top
    of build directory"""
    p = os.path.join("#/mods", mod)
    if fname is None:
        return p
    else:
        return os.path.join(p, str(fname))


##
#  access to build directories
##
def _buildGet(env, mod, dirname, fname):
    """get an build directory or file in that directory.  Only the basename of fname
    is used, which might be a scons Node"""
    p = os.path.join("#/build", mod, dirname)
    if fname is None:
        return p
    else:
        return os.path.join(p, os.path.basename(str(fname)))

def buildLibDir(env, mod, fname=None):
    """get lib output directory or file in that directory"""
    return _buildGet(env, mod, ".", fname)

##
# access to output directories is via function to allow for configuration
# using env in the future
##

def _outputGet(env, dirname, fname):
    """get an output directory or file in that directory.  Only the basename of fname
    is used, which might be a scons Node"""
    p = os.path.join("#/output", dirname)
    if fname is None:
        return p
    else:
        return os.path.join(p, os.path.basename(str(fname)))

def outputBinDir(env, fname=None):
    """get bin output directory or file in that directory"""
    return _outputGet(env, "bin", fname)

def outputTestBinDir(env, fname=None):
    """get testbin output directory or file in that directory"""
    return _outputGet(env, "testbin", fname)

def outputLibDir(env, fname=None):
    """get lib output directory or file in that directory"""
    return _outputGet(env, "lib", fname)

##
# Building and linking
##

def libFileName(libbase):
    "tack `lib' on the front of the library base name"
    return "lib" + libbase + ".a"


def buildStaticLibrary(env, libBaseName, srcPaths):
    """link a static library"""
    bl = env.StaticLibrary(libFileName(libBaseName), srcPaths)


def getSrcPaths(srcDir, srcFiles):
    """Combine srcDir and srcFiles, If srcDir can be none, if srcFiles
    contains full paths"""
    if srcDir is None:
        return srcFiles
    else:
        return [os.path.join(srcDir, sf) for sf in srcFiles]
    

def globSrcPaths(env, srcDir, globPat, excludes=[]):
    """glob for all files in srcDir matching globPat, excluding excludes
    in srcDir"""
    excludePaths = [os.path.join(srcDir, f) for f in excludes]
    return env.Glob(os.path.join(srcDir, globPat),
                    exclude=excludePaths)
    
def linkProg(env, prog, srcs):
    """link a program, with specified C or C++ sources files.
    The program name is derived from the first C or C++ file, unless specified"""
    if prog is None:
        prog = os.path.splitext(os.path.basename(srcs[0]))[0]
    bp = env.Program(prog, srcs)
    op = env.Install(outputBinDir(env), bp)
    env.Default(op)

def linkProgDir(env, prog, srcDir, srcs):
    """link a program with srcs in srcDir..  The program name is derived from
    the first C or C++ file, if none"""
    linkProg(env, prog,
             [os.path.join(srcDir, s) for s in srcs])

def linkTest(env, prog, srcs):
    """link a test program, with specified C or C++ sources files.
    The program name is derived from the first C or C++ file, unless specified"""
    if prog is None:
        prog = os.path.splitext(os.path.basename(srcs[0]))[0]
    bp = env.Program(prog, srcs)
    op = env.Install(outputTestBinDir(env), bp)
    env.Default(op)

def linkTestDir(env, prog, srcDir, srcs):
    """link a test program with srcs in srcDir..  The program name is derived from
    the first C or C++ file, if none"""
    linkTest(env, prog,
             [os.path.join(srcDir, s) for s in srcs])


##
# make a symbolic link
##
def mkRelSymLink(target, source, env):
    "construct relative symbolic link"
    targetAbs = os.path.abspath(str(target[0]))
    sourceAbs = os.path.abspath(str(source[0]))
    commonPre = os.path.commonprefix((targetAbs, sourceAbs))
    sourceTail = sourceAbs[len(commonPre):]
    # count directories up from target
    numDirs = sourceTail.count("/")
    sourceRel = os.path.join(*((numDirs * ['..']) + [sourceTail]))
    if os.path.exists(targetAbs):
        os.unlink(targetAbs)
    os.symlink(sourceRel, targetAbs)

def envRelSymlink(env, source, target):
    """build a symbolic link, doesn't work with variant directory"""
    env.Command(target, source, mkRelSymLink)


##
# python code
##
def installPyProgs(env, srcDir, srcs):
    """Copy python programs to the install directory and make executable, read-only"""
    for src in srcs:
        op = env.Command(outputBinDir(env, src), os.path.join(srcDir, src),
                         [Copy('$TARGET', '$SOURCE'),
                          Chmod('$TARGET', "ugo-w,ugo+rw")])
        env.Default(op)


def installPyTest(env, srcDir, srcs):
    """Copy a python test programs to the install directory and make executable, read-only"""
    for src in srcs:
        op = env.Command(outputTestBinDir(env, src), os.path.join(srcDir, src),
                         [Copy('$TARGET', '$SOURCE'),
                          Chmod('$TARGET', "ugo-w,ugo+rw")])
        env.Default(op)


###
# create library dependencies
###
    
libExternalPrefixes = ["/hive/groups/recon/local",   # hgwdev
                       "/opt/local",   # OS/X MacPorts
                       "/usr/local",   # FreeBSD, Brew, etc
                       "/usr"]   # Ubuntu, etc

def libAdd(env, inclDirs, libDir, libBases, libDepends=None, libDefine=None):
    """add the paths to include and ibrary to the environments,
   inclDirs and libBases can be a list or a string"""
    # allow LIBS to be duplicate if needed, since linking is ordered
    if isinstance(inclDirs, str):
        inclDirs = [inclDirs]
    if isinstance(libBases, str):
        libBases = [libBases]
    env.AppendUnique(CPPPATH=inclDirs)
    env.Append(LIBS=libBases)
    env.AppendUnique(LIBPATH=[libDir])
    if libDepends is not None:
        env.Append(LIBS=libDepends)
    if libDefine is not None:
        env.Append(CPPDEFINES=[libDefine])

def libFindPrefix(inclFile, prefixes):
    "search for the prefix for a library based on a include file"
    for prefix in prefixes:
        if os.path.exists(os.path.join(prefix, "include", inclFile)):
            return prefix
    raise Exception("can't find header {} on prefixes: {}".format(inclFile, prefixes))

def libFindAdd(env, inclFile, libBases, prefixes, libDepends=None, libDefine=None,
               useRPath=False):
    """search for library and add to the environments, libBases can be a list or string"""
    prefix = libFindPrefix(inclFile, prefixes)
    libAdd(env,
           os.path.join(prefix, "include"),
           os.path.join(prefix, "lib"),
           libBases, libDepends=libDepends, libDefine=libDefine)
    if useRPath:
        env.AppendUnique(RPATH=[os.path.join(prefix, "lib")])

def libAddKyotoDatabase(env):
    libFindAdd(env, "tcbdb.h",
               ["tokyocabinet", "kyototycoon", "kyotocabinet"],
               libExternalPrefixes,
               libDefine="HAVE_TOKYO_CABINET=1",
               libDepends=["z", "bz2", "pthread", "m", "-lstdc++"],
               useRPath=True)

def libAddMod(env, mod, inclDirs, libBase, libDepends=None, libDefine=None):
    """add include and libraries in the variant build directory.  Include dirs maybe a string,
    list or list of Nodes."""
    if isinstance(inclDirs, str):
        inclDirs = [inclDirs]
    libAdd(env,
           [_moduleGet(env, mod, i) for i in inclDirs],
           os.path.join(buildLibDir(env, mod)),
           [libBase], libDepends=libDepends, libDefine=libDefine)

def libAddSonLib(env):
    incDirs = ("sonLib/include", "cutest",
               "matchingAndOrdering/include", "pinchesAndCacti/include",
               "threeEdgeConnected/include")
    libAddMod(env, SONLIB_MOD_NAME, incDirs, SONLIB_LIB_NAME)

def libAddCuTest(env):
    libAddMod(env, SONLIB_MOD_NAME, "cutest", CUTEST_LIB_NAME)
    
def libAddCPecan(env):
    libAddMod(env, CPECAN_MOD_NAME, "include", CPECAN_LIB_NAME)

def libAddCactus(env):
    libAddMod(env, CACTUS_MOD_NAME, "caf/include", STCAF_LIB_NAME)
    libAddMod(env, CACTUS_MOD_NAME, "blast/include", BLAST_LIB_NAME)
    libAddMod(env, CACTUS_MOD_NAME, "api/include", CACTUS_LIB_NAME)
