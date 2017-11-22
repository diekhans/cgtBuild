# calls scons or git

# git@github.com:lastz/lastz.git 1.04.00

mods = sonLib cactus cPecan hal

modDirs = ${mods:%=mods/%}
gitDirs = . ${modDirs}

.PHONY: build clone commit status push clean savebak

build:
	scons

# initial clone of mods
clone: ${mods:%=%.clone}
%.clone:
	@mkdir -p mods
	(cd mods && if [ ! -e $* ] ; then git clone -b springClean2017 git@github.com:diekhans/$*  ; fi)

# commit if dirty
commit: ${gitDirs:%=%.commit}
%.commit: checkCommitMsg
	(cd $* && if [ "$$(git status --short --untracked-files=no)" != "" ] ; then  git commit -am '${msg}' ; fi)

checkCommitMsg:
	@if [ "${msg}" = "" ] ; then echo "Error: must specify msg=xxx on commit" >/dev/stderr && exit 1 ;fi

# status
status: ${gitDirs:%=%.status}
%.status:
	@echo "======= $* ======"
	(cd $* && git status)

# push
push: ${gitDirs:%=%.push}
%.push:
	(cd $* && git push)

# pull
pull: ${gitDirs:%=%.push}
%.pull:
	(cd $* && git pull)

clean:
	rm -rf build output


# backup of .git dirs
savebak:
	savebak cgtBuild .git trees/*/.git
