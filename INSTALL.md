
# Temporary Install Instructions

Build refactoring is a work in progress, these instructions are used to
checkout and build the current tree.  They will change.


## Initial setup
  * Install scons if not already installed:
    * `pip install scons`
  * clone cgtBuild meta repo:
    * `git clone -b springClean2017 git@github.com:diekhans/cgtBuild`
    * `cd cgtBuild`
  * use make to clone modules from markd's repo:
    * `make clone`
  * build with scons using 32 cores:
    * `nice scons -j 32`
    
## Other actions:
  * status of all cloned repos
    * `make status`
  * commit pending changes to all repos
    * `make commit msg="your commit message"`
  * push changes
    * `make push`
  * update from github
    * `make pull`

    
