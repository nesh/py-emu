SRC = Z80.c
DEP = Z80.h Codes.h CodesCB.h CodesED.h CodesXCB.h CodesXX.h Tables.h
OUT = ../z80_core.so
# -------------------------------------------------
.PHONY: all clean distclean

all:  $(OUT)

# TODO autodetect endianess
Z80.o: $(SRC) $(DEP)
	gcc -c -shared -fPIC -O3 -fomit-frame-pointer -Wall -DEXECZ80 -DLSB_FIRST Z80.c
	
$(OUT): Z80.o
	libtool -dynamic -o $(OUT) z80.o

clean:
	rm -f *.o
	rm -f $(OUT)