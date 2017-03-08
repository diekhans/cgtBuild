import os

# library base names
SONLIB_LIB_NAME = "sonlib"
CUTEST_LIB_NAME = "cutest"
CACTUS_LIB_NAME = "cactus"

# special output paths
TEST_BIN_DIR = "testbin"

# run directories at root, all output is installed from build directories to here.
RUN_DIR = "#/run"
# RUN_BIN_DIR = os.path.join(RUN_DIR, "bin")
# RUN_LIB_DIR = os.path.join(RUN_DIR, "lib")
# RUN_INCLUDE_DIR = os.path.join(RUN_DIR, "include")

##
# building and linking
##
def buildStaticLibrary(env, libBaseName, srcs):
    """link a static library"""
    env.StaticLibrary(target="lib" + libBaseName, source=srcs)

def linkTestProg(env, progName, srcDir, srcFiles):
    """link a test program, with specified srcs from srcFiles in srcDir.
    If srcDir can be none, if srcFiles contains full paths"""
    if srcDir is not None:
        srcPaths = [os.path.join(srcDir, sf) for sf in srcFiles]
    else:
        srcPaths = srcFiles
    env.Program(target=os.path.join(TEST_BIN_DIR, progName),
                source=srcPaths)


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
