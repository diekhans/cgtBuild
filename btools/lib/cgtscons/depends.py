"""
Functions to handled adding library dependencies.
"""
import os

libExternalPrefixes = ["/hive/groups/recon/local",   # hgwdev
                       "/opt/local",   # OS/X MacPorts
                       "/usr/local",   # FreeBSD, Brew, etc
                       "/usr"]   # Ubuntu, etc


def libFindPrefix(inclFile, prefixes):
    "search for the prefix for a library based on a include file"
    for prefix in prefixes:
        if os.path.exists(os.path.join(prefix, "include", inclFile)):
            return prefix
    raise Exception("can't find header {} on prefixes: {}".format(inclFile, prefixes))
    

def libAdd(env, inclFile, libBase, prefixes, libDepends = None, libDefine=None):
    "search for library and add to the environments"
    prefix = libFindPrefix(inclFile, prefixes)
    env.Append(CPPPATH = [os.path.join(prefix, "include")])
    env.Append(LIBS = [libBase], LIBPATH = [os.path.join(prefix, "lib")])
    if libDepends is not None:
        env.Append(LIBS = libDepends)
    if libDefine is not None:
        env.Append(CPPDEFINES = [libDefine])


def libAddKyotoDatabase(env):
    libAdd(env, "ktcommon.h", "kyototycoon", libExternalPrefixes,
           libDepends=["z", "bz2", "pthread", "m", "-lstdc++"],
           libDefine="HAVE_TOKYO_CABINET=1")
    libAdd(env, "tcbdb.h", "tokyocabinet", libExternalPrefixes,
           libDepends=["z", "bz2", "pthread", "m"],
           libDefine="HAVE_TOKYO_CABINET=1")


__all__ = (libAddKyotoDatabase.__name__, )
