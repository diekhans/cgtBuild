"""
Functions to handled adding library dependencies.
"""
import os
from cgtscons import SONLIB_LIB_NAME, CUTEST_LIB_NAME

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
    libAdd(env, "#/mods/sonLib/c/sonlib/include",
           "./lib", SONLIB_LIB_NAME)

def libAddCuTest(env):
    libAdd(env, "#/mods/sonLib/c/cutest",
           "./lib", CUTEST_LIB_NAME,)
    
__all__ = (libAddKyotoDatabase.__name__, )
