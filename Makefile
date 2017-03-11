# calls scons or git


mods = sonLib cactus cPecan hal
#lastz-dist

modDirs = ${mods:%=mods/%}

build:
	scons

# commit if dirty
gitDirs = . ${modDirs}
commit: ${gitDirs:%=%.commit}


%.commit: checkCommitMsg
	(cd $* && if [ "$$(git status --short)" != "" ] ; then  git commit -am '${msg}' ; fi)


checkCommitMsg:
	@if [ "${msg}" = "" ] ; then echo "Error: must specify msg=xxx on commit" >/dev/stderr ;fi

clean:
	rm -rf build output


# backup of .git dirs
savebak:
	savebak cgtBuild .git trees/*/.git
