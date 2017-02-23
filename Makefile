ROOT = .

include ${ROOT}/rules/defs.mk
SUBDIRS = mods/sonLib

include ${ROOT}/rules/rules.mk

# backup of .git dirs
savebak:
	savebak cgtBuild .git mods/*/.git
