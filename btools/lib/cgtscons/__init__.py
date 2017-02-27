import os

# library base names
SONLIB_LIB_NAME = "sonlib"
CUTEST_LIB_NAME = "cutest"

# special output paths
TEST_BIN_DIR = "testbin"


###
# Code to deal with putting everything in the build directory scons gives very
# poor control over location of some output files. VariantDir doesn't give the
# layout we want for object files
# Setting LIBPREFIX="lib/" handles libraries, but need to build the explictly
# from objects in different directory, not source.
###
def _objectPathBuild(env, libOrProgName, srcFile):
    "build a object from a source file"
    # might be an FS object, so conver to string
    objPath = os.path.join("objs", libOrProgName,
                           os.path.splitext(os.path.basename(str(srcFile)))[0] + ".o")
    return  env.StaticObject(target=objPath, source=srcFile)

def objectPathsBuild(env, libOrProgName, srcFiles):
    """explictly build objects paths so they end up in
    VariantDir/objs/libOrProgName"""
    return [_objectPathBuild(env, libOrProgName, srcFile) for srcFile in srcFiles]


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
    os.symlink(sourceRel, targetAbs)

def envRelSymlink(env, source, target):
    env.Command(target, source, mkRelSymLink)
