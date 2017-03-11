"""
Definitions and functions use for building CGT
"""
from __future__ import print_function
import os
from SCons.Script import Copy

# library base names
SONLIB_LIB_NAME = "sonlib"
CUTEST_LIB_NAME = "cutest"
CACTUS_LIB_NAME = "cactus"
CPECAN_LIB_NAME = "cpecan"

# special output paths
TEST_BIN_DIR = "testbin"
BIN_DIR = "bin"
INCLUDE_DIR = "include"


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
    

def globSrcPaths(env, srcDir, globPat, excludes=[]):
    """glob for all files in srcDir matching globPat, excluding excludes
    in srcDir"""
    excludePaths = [os.path.join(srcDir, f) for f in excludes]
    return env.Glob(os.path.join(srcDir, globPat),
                    exclude=excludePaths)
    

def linkProg(env, progName, srcFiles):
    """link a program, with specified srcs from srcFiles in srcDir.
    If srcDir can be none, if srcFiles contains full paths"""
    env.Program(target=os.path.join(BIN_DIR, progName), source=srcFiles)


def linkTestProg(env, progName, srcFiles):
    """link a test program, with specified srcs from srcFiles in srcDir.
    If srcDir can be none, if srcFiles contains full paths"""
    env.Program(target=os.path.join(TEST_BIN_DIR, progName), source=srcFiles)


def globInclude(env, includeDirs):
    """get list of all include files (*.h) in the specified directories"""
    incls = []
    for includeDir in includeDirs:
        incls.extend(env.Glob("{}/*.h".format(includeDir)))
    return incls

def copyBuildInclude(env, srcFiles):
    "copy files to the build include directory"
    # For some reason, if the include file was adjacent to the sconscript file
    # then in created a circular dependency on the .h file in variant directory,
    # even though the srcFiles are fully qualified paths.  Doing the env.Dir below
    # works around this.
    #env.Install(os.path.join(env.Dir('.').abspath, INCLUDE_DIR), srcFiles)
    print("Dir", env.Dir('.').abspath)
    for srcFile in srcFiles:
        print("t", os.path.join(env.Dir('.').abspath, "include", os.path.basename(srcFile.path)))
        print("s", srcFile)
        env.Command(os.path.join(env.Dir('.').abspath, "include", os.path.basename(srcFile.path)),
                    srcFile.abspath,
                    Copy('$TARGET', '$SOURCE'))
    

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
    libAdd(env, "#/build/sonLib/include",
           "#/build/sonLib/lib", SONLIB_LIB_NAME)

def libAddCuTest(env):
    libAdd(env, "#/build/sonLib/include",
           "#build/sonLib/lib", CUTEST_LIB_NAME)
    
def libAddCactus(env):
    libAdd(env, "#/build/cactus/include",
           "#/build/cactus/lib", CACTUS_LIB_NAME)

def libAddCPecan(env):
    libAdd(env, "#/build/cPecan/include",
           "#/build/cPecan/lib", CPECAN_LIB_NAME)
