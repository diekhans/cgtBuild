##
# target variables
##
LIBOBJS = ${LIBBASES:%=${OBJDIR}/%.o}
DEPENDS = ${LIBBASES:%=.%.depend}

all:: build

##
# build targets
##
build:: ${LIBOBJS}
ifneq (${LIBFILE},)
build:: ${LIBFILE}(${LIBOBJS})
endif
build:: ${SUBDIRS:%=%.build}
%.build:
	${MAKE} -C $* build


${OBJDIR}/%.o: %.c
	@mkdir -p $(dir $@)
	${CC} ${CFLAGS} -c -MM -MT $@ $< > .$*.depend
	${CC} ${CFLAGS} -c -o $@ $<

(%.o): %.o
	@mkdir -p $(dir $@)
	${addLib} $@ $*.o

##
# clean targets
## 
clean::
	rm -f ${LIBFILE} ${LIBOBJS}

clean:: ${SUBDIRS:%.clean}
%_clean:
	${MAKE} -C $* clean



# don't fail on missing dependencies, they are generated the first time the .o
# is compiled
ifneq (${DEPENDS},)
-include ${DEPENDS}
endif
