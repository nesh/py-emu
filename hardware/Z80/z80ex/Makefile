# Z80ex Makefile
# (for GNU make)
#
#################################################################

# currently this will only work on Mac OSX!!!!!
# TODO configure!

CC := gcc -ansi -pedantic -Wall -pipe -O3 -I. -I./include
LINKER := gcc

#little/big endian, choose one:
ENDIANNESS := WORDS_LITTLE_ENDIAN
#ENDIANNESS := WORDS_BIG_ENDIAN


#################################################################

PROJ := z80ex
EMU := libz80ex
DASM := libz80ex_dasm
VERSION := 0.15
VER_STR :=
API_V := 0.${VERSION}

c_files:= z80ex.c z80ex_dasm.c

%.lo : %.c
	glibtool --mode=compile ${CC} -D$(ENDIANNESS) -c -o $@ $<	

.PHONY : all clean distclean

all:: shared

z80ex.lo: include/z80ex.h include/z80ex_common.h daa_table.c typedefs.h macros.h opcodes/opcodes_base.c\
opcodes/opcodes_dd.c opcodes/opcodes_fd.c opcodes/opcodes_cb.c\
opcodes/opcodes_ed.c opcodes/opcodes_ddcb.c opcodes/opcodes_fdcb.c

z80ex_dasm.lo: include/z80ex_dasm.h include/z80ex_common.h opcodes/opcodes_dasm.c

clean:
	rm -f *.o
	rm -f *.lo
	rm -rf .libs

distclean: clean
	rm -rf lib

# shared: z80ex.o z80ex_dasm.o
# 	${LINKER} --shared -Wl,-soname,${EMU}.so.${API_V} -o ./lib/${EMU}.so.${API_V}.${VERSION} z80ex.o	
# 	${LINKER} --shared -Wl,-soname,${DASM}.so.${API_V} -o ./lib/${DASM}.so.${API_V}.${VERSION} z80ex_dasm.o

# OSX ONLY
shared: z80ex.lo z80ex_dasm.lo
	@mkdir -p lib
	libtool -dynamic -lc -compatibility_version ${API_V} -current_version ${API_V} -o ./lib/${EMU}.so z80ex.lo
	libtool -dynamic -lc -compatibility_version ${API_V} -current_version ${API_V} -o ./lib/${DASM}.so z80ex.lo


#EOF