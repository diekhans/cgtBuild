"""
Definitions and functions use for building CGT
"""
import os

# library base names
SONLIB_LIB_NAME = "sonlib"
CUTEST_LIB_NAME = "cutest"
CACTUS_LIB_NAME = "cactus"

# special output paths
TEST_BIN_DIR = "testbin"
BIN_DIR = "bin"

# run directories at root, all output is installed from build directories to here.
RUN_DIR = "#/run"
#RUN_BIN_DIR = os.path.join(RUN_DIR, "bin")
# RUN_LIB_DIR = os.path.join(RUN_DIR, "lib")
# RUN_INCLUDE_DIR = os.path.join(RUN_DIR, "include")

##
# building and linking
##
def buildStaticLibrary(env, libBaseName, srcs):
    """link a static library"""
    env.StaticLibrary(target="lib" + libBaseName, source=srcs)

def getSrcPaths(srcDir, srcFiles):
    """Combine srcDir and srcFiles, If srcDir can be none, if srcFiles
    contains full paths"""
    if srcDir is None:
        return srcFiles
    else:
        return [os.path.join(srcDir, sf) for sf in srcFiles]
    

def linkProg(env, progName, srcFiles):
    """link a program, with specified srcs from srcFiles in srcDir.
    If srcDir can be none, if srcFiles contains full paths"""
    env.Program(target=os.path.join(BIN_DIR, progName), source=srcFiles)


def linkTestProg(env, progName, srcFiles):
    """link a test program, with specified srcs from srcFiles in srcDir.
    If srcDir can be none, if srcFiles contains full paths"""
    env.Program(target=os.path.join(TEST_BIN_DIR, progName), source=srcFiles)


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

def libAddSonLib(env):
    libAdd(env, "#/trees/sonLib/sonlib/include",
           "./lib", SONLIB_LIB_NAME)

def libAddCuTest(env):
    libAdd(env, "#/trees/sonLib/cutest",
           "./lib", CUTEST_LIB_NAME,)
    

