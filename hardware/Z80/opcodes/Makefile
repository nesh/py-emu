.PHONY: clean

PY := genop.py _opcodes.py 
DAT := opcodes_base.dat opcodes_cb.dat opcodes_ddfd.dat opcodes_ddfdcb.dat opcodes_ed.dat

all:  ${PY} ${DAT}
	./genop.py
	nosetests ../../../tests/test_z80.py

clean:
	rm -f opcodes_base.py
	rm -f opcodes_cb.py
	rm -f opcodes_dd.py
	rm -f opcodes_ddcb.py
	rm -f opcodes_ed.py
	rm -f opcodes_fd.py
	rm -f opcodes_fdcb.py