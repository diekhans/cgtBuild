# Description of source trees and build of Comparative Genomics Toolkit.

## Overview

The cgtBuild repo is a meta-repo that builds CGT component repositories.  It
may also be used to build some dependencies as needed.  The build process is
implemented using [scons](http://scons.org/).


## Directories

Overall structure of this repo is
  * `sconstruct` - scons main program that builds the Comparative Genomics Toolkit.
  * `btools/` -tools for managing and building the Comparative Genomics Toolkit.
    * `bin/mgit` - tool for running git over multiple module or dependency repos.
    * `lib/cgtscons` - Python packages with CGT-specific definitions and
      functions used by scons build process.
  * `mods/` - component git repos are checked out into this directory.
  * `deps/` - external source dependency repos are checked out into this
      directory.  These are used when an dependency needs patching, as special
      version, or needs to be built because it's not readily available in some
      environments.
  * `build/` - variant directory for intermediate build output.
    
Each module under `mods` attempts to follow the same general structure,
although there maybe some variation due to differing needs or history.
  * `sconscript` - scons sconscript build program for this tree.
  * *submod1/* - Each sub-module within a tree lives in it's own directory, recommend sub-directory
    structure is:
    * `include/` - Include files for a library that is used outside of the module.
    * `src/` - source files for compiled programs and library objects.
    * `bin/` - interpreted programs (scripts)
	* `tests/` - tests
    * `lib/py/cgt/` - python packages, which should all be part of the package `cgt`
    * `doc/` - documentation

If a repo only contains one sub-module, then the *submod/* directory maybe omitted.


## Scons build

The python-based build tool [scons](http://scons.org/) is used to build the
CGT modules and needed dependencies.  Scons simplifies maybe build tasks, such
as computing dependencies and build and linking libraries.  Since it is programmed in 
a Turning-complete language, special task are easy to add.  However, scons does
have a bit usage pattern around how a build is organized.  If one goes too much
against it's patterns, it can lead to odd black-box behavior.

Scons uses a variant directory to separate out the build of each module.  By
default, the entire source tree is duplicated to the variant directory and
built in place.  The CGT doesn't use this approach, to allow for easy editing.
Instead, source files used in place, with the output (object and libraries)
going to the variant (`build/`) directory.

Python functions in the `cgtscons` package are used to set the
include and library paths in `sconscript` files.  Include files are 
not copied to the variant directory and are included from the module file.






