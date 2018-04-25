
# Temporary Install Instructions

Build refactoring is a work in progress, these instructions are used to
checkout and build the current tree.  They will change.


## Initial setup
   * basics
     sudo apt-get install make 
     sudo apt-get install python-pip python-wheel
  * Install scons if not already installed:
    * `pip install SCons`
       Note that on Ubuntu scons will currently only work in a virtualenv.
  * Other dependencies (Ubuntu 17.10)
     sudo -H apt-get update
     sudo -H apt-get install -y git gcc g++ build-essential python-dev zlib1g-dev wget valgrind libbz2-dev libhiredis-dev pkg-config
     sudo -H apt-get install -y libkyototycoon-dev libtokyocabinet-dev libkyotocabinet-dev
     sudo -H apt-get install -y libhdf5-100 libhdf5-cpp-100 libhdf5-dev libhdf5-doc
     sudo -H apt-get install -y gcc-4.8 g++-4.8

     from https://github.com/cloudflare/kyotocabinet
          git clone git@github.com:cloudflare/kyotocabinet.git
          CXX=g++-4.8 ./configure
          make -j 4
          sudo make install
     from https://github.com/cloudflare/kyototycoon
          git clone git@github.com:cloudflare/kyototycoon.git
          CXX=g++-4.8 ./configure
          make -j 4
          sudo make install

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

    
