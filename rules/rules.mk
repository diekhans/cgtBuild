##
# target variables
##
PROGBASES = ${CPROGS:%=${%}_PROGBASES} ${CXXPROGS:%=${%}_PROGBASES}
LIBOBJS = ${LIBBASES:%=${OBJDIR}/%.o}
OJBS = ${PROGBASES:%=${OBJDIR}/%.o}
DEPENDS = ${LIBBASES:%=.%.depend} ${PROGBASES:%=%.depend}

PROGS = ${PROGBASES:%=${BINDIR}/%}
TESTPROGS = ${PROGBASES:%=${TESTBINDIR}/%}

all:: build

##
# build targets
##
build:: ${LIBOBJS} ${OBJS} ${PROGS}
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

# While compiling the .o's is straight forward, linking the programs is not
# because of not being able to generate the right dependencies.  So we link
# by recursion
build:: ${CPROGS:%=%.linkCProg} ${CXXPROGS:%=%.linkCXXProg}

%.linkCProg: ${OBJS}
	${MAKE} linkProg PROGDIR=${BINDIR} CPROG=$*

ifneq (${CPROG},)
# recursive call
linkProg: ${PROGDIR}/${CPROG}
${PROGDIR}/${CPROG}: $(for f,$(${CPROG}_PROGBASES),${OBJDIR}/$f.o) ${PROG_LIBFILES}
	@mkdir -p $(dir $@)
	${CC} ${CFLAGS} -o $@ $^ ${LIBS}
endif

%.linkCXXProg: ${OBJS}
	${MAKE} linkProg PROGDIR=${BINDIR} CXXPROG=$*

ifneq (${CXXPROG},)
# recursive call
linkProg: ${PROGDIR}/${CXXPROG}
${PROGDIR}/${CXXPROG}: $(for f,$(${CXXPROG}_PROGBASES),${OBJDIR}/$f.o) ${PROG_LIBFILES}
	@mkdir -p $(dir $@)
	${CXX} ${CXXFLAGS} -o $@ $^ ${LIBS}
endif




##
# clean targets
## 
clean::
	rm -f ${LIBFILE} ${LIBOBJS} ${LIBFILE}.lock

clean:: ${SUBDIRS:%=%.clean}
%.clean:
	${MAKE} -C $* clean



# don't fail on missing dependencies, they are generated the first time the .o
# is compiled
ifneq (${DEPENDS},)
-include ${DEPENDS}
endif
