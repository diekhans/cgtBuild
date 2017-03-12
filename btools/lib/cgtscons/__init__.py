"""
Definitions and functions use for building CGT
"""
from __future__ import print_function
import os

# library base names
SONLIB_LIB_NAME = "sonlib"
CUTEST_LIB_NAME = "cutest"
CACTUS_LIB_NAME = "cactus"
CPECAN_LIB_NAME = "cpecan"

# access to output directories is via function to allow for configuration
# using env in the future

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

def outputIncludeDir(env, fname=None):
    """get include output directory or file in that directory"""
    return _outputGet(env, "include", fname)

def libFileName(libbase):
    "tack `lib' on the front of the library base name"
    return "lib" + libbase + ".a"

##
# Building and linking, with results in output directory.
# this also copies includes to output.
##

def addOutputIncludeAlias(env, outInclude):
    """an alias is create for all output includes, and only add the
    alias to the defaults targets.  This prevents and up to date message
    for each include. """
    env.Default(env.Alias("outputIncludes", outInclude))

def globInclude(env, includeDirs):
    """get list of all include files (*.h) in the specified directories"""
    inclFiles = []
    for includeDir in includeDirs:
        inclFiles.extend(env.Glob("{}/*.h".format(includeDir)))
    return inclFiles

def makeIncludesDepends(env, includeFiles):
    "copy files to the run include directory"
    # create dependencies so files are installed as needed and then insist they
    # are installed
    for incl in includeFiles:
        env.Depends(outputIncludeDir(env, incl), incl)
        oi = env.Install(outputIncludeDir(env), incl)
        addOutputIncludeAlias(env, oi)

def buildStaticLibrary(env, libBaseName, srcs):
    """link a static library"""
    bl = env.StaticLibrary(libFileName(libBaseName), srcs)
    ol = env.Install(outputLibDir(env), bl)
    env.Depends(ol, bl)
    env.Default(ol)

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
    

def linkProg(env, progName, srcFiles):
    """link a program, with specified srcs from srcFiles in srcDir.
    If srcDir can be none, if srcFiles contains full paths"""
    bp = env.Program(progName, srcFiles)
    op = env.Install(outputBinDir(env), bp)
    env.Default(op)


def linkTestProg(env, progName, srcFiles):
    """link a test program, with specified srcs from srcFiles in srcDir.
    If srcDir can be none, if srcFiles contains full paths"""
    bp = env.Program(progName, srcFiles)
    op = env.Install(outputTestBinDir(env), bp)
    env.Default(op)

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


###
# library dependencies
###
    
libExternalPrefixes = ["/hive/groups/recon/local",   # hgwdev
                       "/opt/local",   # OS/X MacPorts
                       "/usr/local",   # FreeBSD, Brew, etc
                       "/usr"]   # Ubuntu, etc

def libAdd(env, inclDir, libDir, libBases, libDepends=None, libDefine=None):
    """add the paths to include and ibrary to the environments,
    libBases can be a list or a string"""
    # allow LIBS to be duplicate if needed, since linking is ordered
    env.AppendUnique(CPPPATH=[inclDir])
    if isinstance(libBases, str):
        libBases = [libBases]
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

def libAddVariant(env, mod, libBases, libDepends=None, libDefine=None):
    "add include and libraries in the variant build directory"
    libAdd(env,
           os.path.join(outputIncludeDir(env)),
           os.path.join(outputLibDir(env)),
           libBases, libDepends=libDepends, libDefine=libDefine)

def libAddSonLib(env):
    libAddVariant(env, "sonLib", SONLIB_LIB_NAME)

def libAddCuTest(env):
    libAddVariant(env, "sonLib", CUTEST_LIB_NAME)
    
def libAddCactus(env):
    libAddVariant(env, "cactus", CACTUS_LIB_NAME)

def libAddCPecan(env):
    libAddVariant(env, "cPecan", CPECAN_LIB_NAME)
