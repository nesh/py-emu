.PHONY: clean test

PY := genop.py _opcodes.py 
DAT := opcodes_base.dat opcodes_cb.dat opcodes_ddfd.dat opcodes_ddfdcb.dat opcodes_ed.dat
GEN := opcodes_base.py opcodes_cb.py opcodes_dd.py opcodes_ddcb.py opcodes_ed.py opcodes_fd.py opcodes_fdcb.py

all: code test

code: ${GEN} ${PY}

%.py: %.dat
	@./genop.py

test:
	@nosetests ../../../tests/test_z80.py

clean:
	@echo "cleaning..."
	@rm -f opcodes_base.py
	@rm -f opcodes_cb.py
	@rm -f opcodes_dd.py
	@rm -f opcodes_ddcb.py
	@rm -f opcodes_ed.py
	@rm -f opcodes_fd.py
	@rm -f opcodes_fdcb.py
	@find . -name "*.pyc" -exec rm -f {} \;
	@find . -name "*.pyo" -exec rm -f {} \;
