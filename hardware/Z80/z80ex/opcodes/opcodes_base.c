/* autogenerated from ./opcodes_base.dat, do not edit */

/*NOP*/
static void op_0x00(Z80EX_CONTEXT *cpu)
{
	T_WAIT_UNTIL(4);
	return;
}

/*LD BC,@*/
static void op_0x01(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	LD16(BC,temp_word.w);
	T_WAIT_UNTIL(10);
	return;
}

/*LD (BC),A*/
static void op_0x02(Z80EX_CONTEXT *cpu)
{
	LD_A_TO_ADDR_MPTR(temp_byte,A, (BC));
	WRITE_MEM((BC),temp_byte,4);
	T_WAIT_UNTIL(7);
	return;
}

/*INC BC*/
static void op_0x03(Z80EX_CONTEXT *cpu)
{
	INC16(BC);
	T_WAIT_UNTIL(6);
	return;
}

/*INC B*/
static void op_0x04(Z80EX_CONTEXT *cpu)
{
	INC(B);
	T_WAIT_UNTIL(4);
	return;
}

/*DEC B*/
static void op_0x05(Z80EX_CONTEXT *cpu)
{
	DEC(B);
	T_WAIT_UNTIL(4);
	return;
}

/*LD B,#*/
static void op_0x06(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	LD(B,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*RLCA*/
static void op_0x07(Z80EX_CONTEXT *cpu)
{
	RLCA();
	T_WAIT_UNTIL(4);
	return;
}

/*EX AF,AF'*/
static void op_0x08(Z80EX_CONTEXT *cpu)
{
	EX(AF,AF_);
	T_WAIT_UNTIL(4);
	return;
}

/*ADD HL,BC*/
static void op_0x09(Z80EX_CONTEXT *cpu)
{
	ADD16(HL,BC);
	T_WAIT_UNTIL(11);
	return;
}

/*LD A,(BC)*/
static void op_0x0a(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(BC),4);
	LD_A_FROM_ADDR_MPTR(A,temp_byte, (BC));
	T_WAIT_UNTIL(7);
	return;
}

/*DEC BC*/
static void op_0x0b(Z80EX_CONTEXT *cpu)
{
	DEC16(BC);
	T_WAIT_UNTIL(6);
	return;
}

/*INC C*/
static void op_0x0c(Z80EX_CONTEXT *cpu)
{
	INC(C);
	T_WAIT_UNTIL(4);
	return;
}

/*DEC C*/
static void op_0x0d(Z80EX_CONTEXT *cpu)
{
	DEC(C);
	T_WAIT_UNTIL(4);
	return;
}

/*LD C,#*/
static void op_0x0e(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	LD(C,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*RRCA*/
static void op_0x0f(Z80EX_CONTEXT *cpu)
{
	RRCA();
	T_WAIT_UNTIL(4);
	return;
}

/*DJNZ %*/
static void op_0x10(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	temp_byte_s=(temp_byte & 0x80)? -(((~temp_byte) & 0x7f)+1): temp_byte;
	DJNZ(temp_byte_s, /*t:*/ /*t1*/8,/*t2*/13);
	return;
}

/*LD DE,@*/
static void op_0x11(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	LD16(DE,temp_word.w);
	T_WAIT_UNTIL(10);
	return;
}

/*LD (DE),A*/
static void op_0x12(Z80EX_CONTEXT *cpu)
{
	LD_A_TO_ADDR_MPTR(temp_byte,A, (DE));
	WRITE_MEM((DE),temp_byte,4);
	T_WAIT_UNTIL(7);
	return;
}

/*INC DE*/
static void op_0x13(Z80EX_CONTEXT *cpu)
{
	INC16(DE);
	T_WAIT_UNTIL(6);
	return;
}

/*INC D*/
static void op_0x14(Z80EX_CONTEXT *cpu)
{
	INC(D);
	T_WAIT_UNTIL(4);
	return;
}

/*DEC D*/
static void op_0x15(Z80EX_CONTEXT *cpu)
{
	DEC(D);
	T_WAIT_UNTIL(4);
	return;
}

/*LD D,#*/
static void op_0x16(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	LD(D,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*RLA*/
static void op_0x17(Z80EX_CONTEXT *cpu)
{
	RLA();
	T_WAIT_UNTIL(4);
	return;
}

/*JR %*/
static void op_0x18(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	temp_byte_s=(temp_byte & 0x80)? -(((~temp_byte) & 0x7f)+1): temp_byte;
	JR(temp_byte_s);
	T_WAIT_UNTIL(12);
	return;
}

/*ADD HL,DE*/
static void op_0x19(Z80EX_CONTEXT *cpu)
{
	ADD16(HL,DE);
	T_WAIT_UNTIL(11);
	return;
}

/*LD A,(DE)*/
static void op_0x1a(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(DE),4);
	LD_A_FROM_ADDR_MPTR(A,temp_byte, (DE));
	T_WAIT_UNTIL(7);
	return;
}

/*DEC DE*/
static void op_0x1b(Z80EX_CONTEXT *cpu)
{
	DEC16(DE);
	T_WAIT_UNTIL(6);
	return;
}

/*INC E*/
static void op_0x1c(Z80EX_CONTEXT *cpu)
{
	INC(E);
	T_WAIT_UNTIL(4);
	return;
}

/*DEC E*/
static void op_0x1d(Z80EX_CONTEXT *cpu)
{
	DEC(E);
	T_WAIT_UNTIL(4);
	return;
}

/*LD E,#*/
static void op_0x1e(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	LD(E,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*RRA*/
static void op_0x1f(Z80EX_CONTEXT *cpu)
{
	RRA();
	T_WAIT_UNTIL(4);
	return;
}

/*JR NZ,%*/
static void op_0x20(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	temp_byte_s=(temp_byte & 0x80)? -(((~temp_byte) & 0x7f)+1): temp_byte;
	if(!(F & FLAG_Z)) {
	JR(temp_byte_s);
	T_WAIT_UNTIL(12);
	}
	else { T_WAIT_UNTIL(7);}
	return;
}

/*LD HL,@*/
static void op_0x21(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	LD16(HL,temp_word.w);
	T_WAIT_UNTIL(10);
	return;
}

/*LD (@),HL*/
static void op_0x22(Z80EX_CONTEXT *cpu)
{
	temp_addr.b.l=READ_OP();
	temp_addr.b.h=READ_OP();
	LD_RP_TO_ADDR_MPTR_16(temp_word.w,HL, temp_addr.w);
	WRITE_MEM(temp_addr.w,temp_word.b.l,10);
	WRITE_MEM(temp_addr.w+1,temp_word.b.h,13);
	T_WAIT_UNTIL(16);
	return;
}

/*INC HL*/
static void op_0x23(Z80EX_CONTEXT *cpu)
{
	INC16(HL);
	T_WAIT_UNTIL(6);
	return;
}

/*INC H*/
static void op_0x24(Z80EX_CONTEXT *cpu)
{
	INC(H);
	T_WAIT_UNTIL(4);
	return;
}

/*DEC H*/
static void op_0x25(Z80EX_CONTEXT *cpu)
{
	DEC(H);
	T_WAIT_UNTIL(4);
	return;
}

/*LD H,#*/
static void op_0x26(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	LD(H,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*DAA*/
static void op_0x27(Z80EX_CONTEXT *cpu)
{
	DAA();
	T_WAIT_UNTIL(4);
	return;
}

/*JR Z,%*/
static void op_0x28(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	temp_byte_s=(temp_byte & 0x80)? -(((~temp_byte) & 0x7f)+1): temp_byte;
	if(F & FLAG_Z) {
	JR(temp_byte_s);
	T_WAIT_UNTIL(12);
	}
	else { T_WAIT_UNTIL(7);}
	return;
}

/*ADD HL,HL*/
static void op_0x29(Z80EX_CONTEXT *cpu)
{
	ADD16(HL,HL);
	T_WAIT_UNTIL(11);
	return;
}

/*LD HL,(@)*/
static void op_0x2a(Z80EX_CONTEXT *cpu)
{
	temp_addr.b.l=READ_OP();
	temp_addr.b.h=READ_OP();
	READ_MEM(temp_word.b.l,temp_addr.w,10);
	READ_MEM(temp_word.b.h,temp_addr.w+1,13);
	LD_RP_FROM_ADDR_MPTR_16(HL,temp_word.w, temp_addr.w);
	T_WAIT_UNTIL(16);
	return;
}

/*DEC HL*/
static void op_0x2b(Z80EX_CONTEXT *cpu)
{
	DEC16(HL);
	T_WAIT_UNTIL(6);
	return;
}

/*INC L*/
static void op_0x2c(Z80EX_CONTEXT *cpu)
{
	INC(L);
	T_WAIT_UNTIL(4);
	return;
}

/*DEC L*/
static void op_0x2d(Z80EX_CONTEXT *cpu)
{
	DEC(L);
	T_WAIT_UNTIL(4);
	return;
}

/*LD L,#*/
static void op_0x2e(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	LD(L,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*CPL*/
static void op_0x2f(Z80EX_CONTEXT *cpu)
{
	CPL();
	T_WAIT_UNTIL(4);
	return;
}

/*JR NC,%*/
static void op_0x30(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	temp_byte_s=(temp_byte & 0x80)? -(((~temp_byte) & 0x7f)+1): temp_byte;
	if(!(F & FLAG_C)) {
	JR(temp_byte_s);
	T_WAIT_UNTIL(12);
	}
	else { T_WAIT_UNTIL(7);}
	return;
}

/*LD SP,@*/
static void op_0x31(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	LD16(SP,temp_word.w);
	T_WAIT_UNTIL(10);
	return;
}

/*LD (@),A*/
static void op_0x32(Z80EX_CONTEXT *cpu)
{
	temp_addr.b.l=READ_OP();
	temp_addr.b.h=READ_OP();
	LD_A_TO_ADDR_MPTR(temp_byte,A, temp_addr.w);
	WRITE_MEM(temp_addr.w,temp_byte,10);
	T_WAIT_UNTIL(13);
	return;
}

/*INC SP*/
static void op_0x33(Z80EX_CONTEXT *cpu)
{
	INC16(SP);
	T_WAIT_UNTIL(6);
	return;
}

/*INC (HL)*/
static void op_0x34(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	INC(temp_byte);
	WRITE_MEM((HL),temp_byte,8);
	T_WAIT_UNTIL(11);
	return;
}

/*DEC (HL)*/
static void op_0x35(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	DEC(temp_byte);
	WRITE_MEM((HL),temp_byte,8);
	T_WAIT_UNTIL(11);
	return;
}

/*LD (HL),#*/
static void op_0x36(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	LD(temp_byte,temp_byte);
	WRITE_MEM((HL),temp_byte,7);
	T_WAIT_UNTIL(10);
	return;
}

/*SCF*/
static void op_0x37(Z80EX_CONTEXT *cpu)
{
	SCF();
	T_WAIT_UNTIL(4);
	return;
}

/*JR C,%*/
static void op_0x38(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	temp_byte_s=(temp_byte & 0x80)? -(((~temp_byte) & 0x7f)+1): temp_byte;
	if(F & FLAG_C) {
	JR(temp_byte_s);
	T_WAIT_UNTIL(12);
	}
	else { T_WAIT_UNTIL(7);}
	return;
}

/*ADD HL,SP*/
static void op_0x39(Z80EX_CONTEXT *cpu)
{
	ADD16(HL,SP);
	T_WAIT_UNTIL(11);
	return;
}

/*LD A,(@)*/
static void op_0x3a(Z80EX_CONTEXT *cpu)
{
	temp_addr.b.l=READ_OP();
	temp_addr.b.h=READ_OP();
	READ_MEM(temp_byte,temp_addr.w,10);
	LD_A_FROM_ADDR_MPTR(A,temp_byte, temp_addr.w);
	T_WAIT_UNTIL(13);
	return;
}

/*DEC SP*/
static void op_0x3b(Z80EX_CONTEXT *cpu)
{
	DEC16(SP);
	T_WAIT_UNTIL(6);
	return;
}

/*INC A*/
static void op_0x3c(Z80EX_CONTEXT *cpu)
{
	INC(A);
	T_WAIT_UNTIL(4);
	return;
}

/*DEC A*/
static void op_0x3d(Z80EX_CONTEXT *cpu)
{
	DEC(A);
	T_WAIT_UNTIL(4);
	return;
}

/*LD A,#*/
static void op_0x3e(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	LD(A,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*CCF*/
static void op_0x3f(Z80EX_CONTEXT *cpu)
{
	CCF();
	T_WAIT_UNTIL(4);
	return;
}

/*LD B,B*/
static void op_0x40(Z80EX_CONTEXT *cpu)
{
	LD(B,B);
	T_WAIT_UNTIL(4);
	return;
}

/*LD B,C*/
static void op_0x41(Z80EX_CONTEXT *cpu)
{
	LD(B,C);
	T_WAIT_UNTIL(4);
	return;
}

/*LD B,D*/
static void op_0x42(Z80EX_CONTEXT *cpu)
{
	LD(B,D);
	T_WAIT_UNTIL(4);
	return;
}

/*LD B,E*/
static void op_0x43(Z80EX_CONTEXT *cpu)
{
	LD(B,E);
	T_WAIT_UNTIL(4);
	return;
}

/*LD B,H*/
static void op_0x44(Z80EX_CONTEXT *cpu)
{
	LD(B,H);
	T_WAIT_UNTIL(4);
	return;
}

/*LD B,L*/
static void op_0x45(Z80EX_CONTEXT *cpu)
{
	LD(B,L);
	T_WAIT_UNTIL(4);
	return;
}

/*LD B,(HL)*/
static void op_0x46(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	LD(B,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*LD B,A*/
static void op_0x47(Z80EX_CONTEXT *cpu)
{
	LD(B,A);
	T_WAIT_UNTIL(4);
	return;
}

/*LD C,B*/
static void op_0x48(Z80EX_CONTEXT *cpu)
{
	LD(C,B);
	T_WAIT_UNTIL(4);
	return;
}

/*LD C,C*/
static void op_0x49(Z80EX_CONTEXT *cpu)
{
	LD(C,C);
	T_WAIT_UNTIL(4);
	return;
}

/*LD C,D*/
static void op_0x4a(Z80EX_CONTEXT *cpu)
{
	LD(C,D);
	T_WAIT_UNTIL(4);
	return;
}

/*LD C,E*/
static void op_0x4b(Z80EX_CONTEXT *cpu)
{
	LD(C,E);
	T_WAIT_UNTIL(4);
	return;
}

/*LD C,H*/
static void op_0x4c(Z80EX_CONTEXT *cpu)
{
	LD(C,H);
	T_WAIT_UNTIL(4);
	return;
}

/*LD C,L*/
static void op_0x4d(Z80EX_CONTEXT *cpu)
{
	LD(C,L);
	T_WAIT_UNTIL(4);
	return;
}

/*LD C,(HL)*/
static void op_0x4e(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	LD(C,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*LD C,A*/
static void op_0x4f(Z80EX_CONTEXT *cpu)
{
	LD(C,A);
	T_WAIT_UNTIL(4);
	return;
}

/*LD D,B*/
static void op_0x50(Z80EX_CONTEXT *cpu)
{
	LD(D,B);
	T_WAIT_UNTIL(4);
	return;
}

/*LD D,C*/
static void op_0x51(Z80EX_CONTEXT *cpu)
{
	LD(D,C);
	T_WAIT_UNTIL(4);
	return;
}

/*LD D,D*/
static void op_0x52(Z80EX_CONTEXT *cpu)
{
	LD(D,D);
	T_WAIT_UNTIL(4);
	return;
}

/*LD D,E*/
static void op_0x53(Z80EX_CONTEXT *cpu)
{
	LD(D,E);
	T_WAIT_UNTIL(4);
	return;
}

/*LD D,H*/
static void op_0x54(Z80EX_CONTEXT *cpu)
{
	LD(D,H);
	T_WAIT_UNTIL(4);
	return;
}

/*LD D,L*/
static void op_0x55(Z80EX_CONTEXT *cpu)
{
	LD(D,L);
	T_WAIT_UNTIL(4);
	return;
}

/*LD D,(HL)*/
static void op_0x56(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	LD(D,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*LD D,A*/
static void op_0x57(Z80EX_CONTEXT *cpu)
{
	LD(D,A);
	T_WAIT_UNTIL(4);
	return;
}

/*LD E,B*/
static void op_0x58(Z80EX_CONTEXT *cpu)
{
	LD(E,B);
	T_WAIT_UNTIL(4);
	return;
}

/*LD E,C*/
static void op_0x59(Z80EX_CONTEXT *cpu)
{
	LD(E,C);
	T_WAIT_UNTIL(4);
	return;
}

/*LD E,D*/
static void op_0x5a(Z80EX_CONTEXT *cpu)
{
	LD(E,D);
	T_WAIT_UNTIL(4);
	return;
}

/*LD E,E*/
static void op_0x5b(Z80EX_CONTEXT *cpu)
{
	LD(E,E);
	T_WAIT_UNTIL(4);
	return;
}

/*LD E,H*/
static void op_0x5c(Z80EX_CONTEXT *cpu)
{
	LD(E,H);
	T_WAIT_UNTIL(4);
	return;
}

/*LD E,L*/
static void op_0x5d(Z80EX_CONTEXT *cpu)
{
	LD(E,L);
	T_WAIT_UNTIL(4);
	return;
}

/*LD E,(HL)*/
static void op_0x5e(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	LD(E,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*LD E,A*/
static void op_0x5f(Z80EX_CONTEXT *cpu)
{
	LD(E,A);
	T_WAIT_UNTIL(4);
	return;
}

/*LD H,B*/
static void op_0x60(Z80EX_CONTEXT *cpu)
{
	LD(H,B);
	T_WAIT_UNTIL(4);
	return;
}

/*LD H,C*/
static void op_0x61(Z80EX_CONTEXT *cpu)
{
	LD(H,C);
	T_WAIT_UNTIL(4);
	return;
}

/*LD H,D*/
static void op_0x62(Z80EX_CONTEXT *cpu)
{
	LD(H,D);
	T_WAIT_UNTIL(4);
	return;
}

/*LD H,E*/
static void op_0x63(Z80EX_CONTEXT *cpu)
{
	LD(H,E);
	T_WAIT_UNTIL(4);
	return;
}

/*LD H,H*/
static void op_0x64(Z80EX_CONTEXT *cpu)
{
	LD(H,H);
	T_WAIT_UNTIL(4);
	return;
}

/*LD H,L*/
static void op_0x65(Z80EX_CONTEXT *cpu)
{
	LD(H,L);
	T_WAIT_UNTIL(4);
	return;
}

/*LD H,(HL)*/
static void op_0x66(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	LD(H,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*LD H,A*/
static void op_0x67(Z80EX_CONTEXT *cpu)
{
	LD(H,A);
	T_WAIT_UNTIL(4);
	return;
}

/*LD L,B*/
static void op_0x68(Z80EX_CONTEXT *cpu)
{
	LD(L,B);
	T_WAIT_UNTIL(4);
	return;
}

/*LD L,C*/
static void op_0x69(Z80EX_CONTEXT *cpu)
{
	LD(L,C);
	T_WAIT_UNTIL(4);
	return;
}

/*LD L,D*/
static void op_0x6a(Z80EX_CONTEXT *cpu)
{
	LD(L,D);
	T_WAIT_UNTIL(4);
	return;
}

/*LD L,E*/
static void op_0x6b(Z80EX_CONTEXT *cpu)
{
	LD(L,E);
	T_WAIT_UNTIL(4);
	return;
}

/*LD L,H*/
static void op_0x6c(Z80EX_CONTEXT *cpu)
{
	LD(L,H);
	T_WAIT_UNTIL(4);
	return;
}

/*LD L,L*/
static void op_0x6d(Z80EX_CONTEXT *cpu)
{
	LD(L,L);
	T_WAIT_UNTIL(4);
	return;
}

/*LD L,(HL)*/
static void op_0x6e(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	LD(L,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*LD L,A*/
static void op_0x6f(Z80EX_CONTEXT *cpu)
{
	LD(L,A);
	T_WAIT_UNTIL(4);
	return;
}

/*LD (HL),B*/
static void op_0x70(Z80EX_CONTEXT *cpu)
{
	LD(temp_byte,B);
	WRITE_MEM((HL),temp_byte,4);
	T_WAIT_UNTIL(7);
	return;
}

/*LD (HL),C*/
static void op_0x71(Z80EX_CONTEXT *cpu)
{
	LD(temp_byte,C);
	WRITE_MEM((HL),temp_byte,4);
	T_WAIT_UNTIL(7);
	return;
}

/*LD (HL),D*/
static void op_0x72(Z80EX_CONTEXT *cpu)
{
	LD(temp_byte,D);
	WRITE_MEM((HL),temp_byte,4);
	T_WAIT_UNTIL(7);
	return;
}

/*LD (HL),E*/
static void op_0x73(Z80EX_CONTEXT *cpu)
{
	LD(temp_byte,E);
	WRITE_MEM((HL),temp_byte,4);
	T_WAIT_UNTIL(7);
	return;
}

/*LD (HL),H*/
static void op_0x74(Z80EX_CONTEXT *cpu)
{
	LD(temp_byte,H);
	WRITE_MEM((HL),temp_byte,4);
	T_WAIT_UNTIL(7);
	return;
}

/*LD (HL),L*/
static void op_0x75(Z80EX_CONTEXT *cpu)
{
	LD(temp_byte,L);
	WRITE_MEM((HL),temp_byte,4);
	T_WAIT_UNTIL(7);
	return;
}

/*HALT*/
static void op_0x76(Z80EX_CONTEXT *cpu)
{
	HALT();
	T_WAIT_UNTIL(4);
	return;
}

/*LD (HL),A*/
static void op_0x77(Z80EX_CONTEXT *cpu)
{
	LD(temp_byte,A);
	WRITE_MEM((HL),temp_byte,4);
	T_WAIT_UNTIL(7);
	return;
}

/*LD A,B*/
static void op_0x78(Z80EX_CONTEXT *cpu)
{
	LD(A,B);
	T_WAIT_UNTIL(4);
	return;
}

/*LD A,C*/
static void op_0x79(Z80EX_CONTEXT *cpu)
{
	LD(A,C);
	T_WAIT_UNTIL(4);
	return;
}

/*LD A,D*/
static void op_0x7a(Z80EX_CONTEXT *cpu)
{
	LD(A,D);
	T_WAIT_UNTIL(4);
	return;
}

/*LD A,E*/
static void op_0x7b(Z80EX_CONTEXT *cpu)
{
	LD(A,E);
	T_WAIT_UNTIL(4);
	return;
}

/*LD A,H*/
static void op_0x7c(Z80EX_CONTEXT *cpu)
{
	LD(A,H);
	T_WAIT_UNTIL(4);
	return;
}

/*LD A,L*/
static void op_0x7d(Z80EX_CONTEXT *cpu)
{
	LD(A,L);
	T_WAIT_UNTIL(4);
	return;
}

/*LD A,(HL)*/
static void op_0x7e(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	LD(A,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*LD A,A*/
static void op_0x7f(Z80EX_CONTEXT *cpu)
{
	LD(A,A);
	T_WAIT_UNTIL(4);
	return;
}

/*ADD A,B*/
static void op_0x80(Z80EX_CONTEXT *cpu)
{
	ADD(A,B);
	T_WAIT_UNTIL(4);
	return;
}

/*ADD A,C*/
static void op_0x81(Z80EX_CONTEXT *cpu)
{
	ADD(A,C);
	T_WAIT_UNTIL(4);
	return;
}

/*ADD A,D*/
static void op_0x82(Z80EX_CONTEXT *cpu)
{
	ADD(A,D);
	T_WAIT_UNTIL(4);
	return;
}

/*ADD A,E*/
static void op_0x83(Z80EX_CONTEXT *cpu)
{
	ADD(A,E);
	T_WAIT_UNTIL(4);
	return;
}

/*ADD A,H*/
static void op_0x84(Z80EX_CONTEXT *cpu)
{
	ADD(A,H);
	T_WAIT_UNTIL(4);
	return;
}

/*ADD A,L*/
static void op_0x85(Z80EX_CONTEXT *cpu)
{
	ADD(A,L);
	T_WAIT_UNTIL(4);
	return;
}

/*ADD A,(HL)*/
static void op_0x86(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	ADD(A,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*ADD A,A*/
static void op_0x87(Z80EX_CONTEXT *cpu)
{
	ADD(A,A);
	T_WAIT_UNTIL(4);
	return;
}

/*ADC A,B*/
static void op_0x88(Z80EX_CONTEXT *cpu)
{
	ADC(A,B);
	T_WAIT_UNTIL(4);
	return;
}

/*ADC A,C*/
static void op_0x89(Z80EX_CONTEXT *cpu)
{
	ADC(A,C);
	T_WAIT_UNTIL(4);
	return;
}

/*ADC A,D*/
static void op_0x8a(Z80EX_CONTEXT *cpu)
{
	ADC(A,D);
	T_WAIT_UNTIL(4);
	return;
}

/*ADC A,E*/
static void op_0x8b(Z80EX_CONTEXT *cpu)
{
	ADC(A,E);
	T_WAIT_UNTIL(4);
	return;
}

/*ADC A,H*/
static void op_0x8c(Z80EX_CONTEXT *cpu)
{
	ADC(A,H);
	T_WAIT_UNTIL(4);
	return;
}

/*ADC A,L*/
static void op_0x8d(Z80EX_CONTEXT *cpu)
{
	ADC(A,L);
	T_WAIT_UNTIL(4);
	return;
}

/*ADC A,(HL)*/
static void op_0x8e(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	ADC(A,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*ADC A,A*/
static void op_0x8f(Z80EX_CONTEXT *cpu)
{
	ADC(A,A);
	T_WAIT_UNTIL(4);
	return;
}

/*SUB B*/
static void op_0x90(Z80EX_CONTEXT *cpu)
{
	SUB(B);
	T_WAIT_UNTIL(4);
	return;
}

/*SUB C*/
static void op_0x91(Z80EX_CONTEXT *cpu)
{
	SUB(C);
	T_WAIT_UNTIL(4);
	return;
}

/*SUB D*/
static void op_0x92(Z80EX_CONTEXT *cpu)
{
	SUB(D);
	T_WAIT_UNTIL(4);
	return;
}

/*SUB E*/
static void op_0x93(Z80EX_CONTEXT *cpu)
{
	SUB(E);
	T_WAIT_UNTIL(4);
	return;
}

/*SUB H*/
static void op_0x94(Z80EX_CONTEXT *cpu)
{
	SUB(H);
	T_WAIT_UNTIL(4);
	return;
}

/*SUB L*/
static void op_0x95(Z80EX_CONTEXT *cpu)
{
	SUB(L);
	T_WAIT_UNTIL(4);
	return;
}

/*SUB (HL)*/
static void op_0x96(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	SUB(temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*SUB A*/
static void op_0x97(Z80EX_CONTEXT *cpu)
{
	SUB(A);
	T_WAIT_UNTIL(4);
	return;
}

/*SBC A,B*/
static void op_0x98(Z80EX_CONTEXT *cpu)
{
	SBC(A,B);
	T_WAIT_UNTIL(4);
	return;
}

/*SBC A,C*/
static void op_0x99(Z80EX_CONTEXT *cpu)
{
	SBC(A,C);
	T_WAIT_UNTIL(4);
	return;
}

/*SBC A,D*/
static void op_0x9a(Z80EX_CONTEXT *cpu)
{
	SBC(A,D);
	T_WAIT_UNTIL(4);
	return;
}

/*SBC A,E*/
static void op_0x9b(Z80EX_CONTEXT *cpu)
{
	SBC(A,E);
	T_WAIT_UNTIL(4);
	return;
}

/*SBC A,H*/
static void op_0x9c(Z80EX_CONTEXT *cpu)
{
	SBC(A,H);
	T_WAIT_UNTIL(4);
	return;
}

/*SBC A,L*/
static void op_0x9d(Z80EX_CONTEXT *cpu)
{
	SBC(A,L);
	T_WAIT_UNTIL(4);
	return;
}

/*SBC A,(HL)*/
static void op_0x9e(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	SBC(A,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*SBC A,A*/
static void op_0x9f(Z80EX_CONTEXT *cpu)
{
	SBC(A,A);
	T_WAIT_UNTIL(4);
	return;
}

/*AND B*/
static void op_0xa0(Z80EX_CONTEXT *cpu)
{
	AND(B);
	T_WAIT_UNTIL(4);
	return;
}

/*AND C*/
static void op_0xa1(Z80EX_CONTEXT *cpu)
{
	AND(C);
	T_WAIT_UNTIL(4);
	return;
}

/*AND D*/
static void op_0xa2(Z80EX_CONTEXT *cpu)
{
	AND(D);
	T_WAIT_UNTIL(4);
	return;
}

/*AND E*/
static void op_0xa3(Z80EX_CONTEXT *cpu)
{
	AND(E);
	T_WAIT_UNTIL(4);
	return;
}

/*AND H*/
static void op_0xa4(Z80EX_CONTEXT *cpu)
{
	AND(H);
	T_WAIT_UNTIL(4);
	return;
}

/*AND L*/
static void op_0xa5(Z80EX_CONTEXT *cpu)
{
	AND(L);
	T_WAIT_UNTIL(4);
	return;
}

/*AND (HL)*/
static void op_0xa6(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	AND(temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*AND A*/
static void op_0xa7(Z80EX_CONTEXT *cpu)
{
	AND(A);
	T_WAIT_UNTIL(4);
	return;
}

/*XOR B*/
static void op_0xa8(Z80EX_CONTEXT *cpu)
{
	XOR(B);
	T_WAIT_UNTIL(4);
	return;
}

/*XOR C*/
static void op_0xa9(Z80EX_CONTEXT *cpu)
{
	XOR(C);
	T_WAIT_UNTIL(4);
	return;
}

/*XOR D*/
static void op_0xaa(Z80EX_CONTEXT *cpu)
{
	XOR(D);
	T_WAIT_UNTIL(4);
	return;
}

/*XOR E*/
static void op_0xab(Z80EX_CONTEXT *cpu)
{
	XOR(E);
	T_WAIT_UNTIL(4);
	return;
}

/*XOR H*/
static void op_0xac(Z80EX_CONTEXT *cpu)
{
	XOR(H);
	T_WAIT_UNTIL(4);
	return;
}

/*XOR L*/
static void op_0xad(Z80EX_CONTEXT *cpu)
{
	XOR(L);
	T_WAIT_UNTIL(4);
	return;
}

/*XOR (HL)*/
static void op_0xae(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	XOR(temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*XOR A*/
static void op_0xaf(Z80EX_CONTEXT *cpu)
{
	XOR(A);
	T_WAIT_UNTIL(4);
	return;
}

/*OR B*/
static void op_0xb0(Z80EX_CONTEXT *cpu)
{
	OR(B);
	T_WAIT_UNTIL(4);
	return;
}

/*OR C*/
static void op_0xb1(Z80EX_CONTEXT *cpu)
{
	OR(C);
	T_WAIT_UNTIL(4);
	return;
}

/*OR D*/
static void op_0xb2(Z80EX_CONTEXT *cpu)
{
	OR(D);
	T_WAIT_UNTIL(4);
	return;
}

/*OR E*/
static void op_0xb3(Z80EX_CONTEXT *cpu)
{
	OR(E);
	T_WAIT_UNTIL(4);
	return;
}

/*OR H*/
static void op_0xb4(Z80EX_CONTEXT *cpu)
{
	OR(H);
	T_WAIT_UNTIL(4);
	return;
}

/*OR L*/
static void op_0xb5(Z80EX_CONTEXT *cpu)
{
	OR(L);
	T_WAIT_UNTIL(4);
	return;
}

/*OR (HL)*/
static void op_0xb6(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	OR(temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*OR A*/
static void op_0xb7(Z80EX_CONTEXT *cpu)
{
	OR(A);
	T_WAIT_UNTIL(4);
	return;
}

/*CP B*/
static void op_0xb8(Z80EX_CONTEXT *cpu)
{
	CP(B);
	T_WAIT_UNTIL(4);
	return;
}

/*CP C*/
static void op_0xb9(Z80EX_CONTEXT *cpu)
{
	CP(C);
	T_WAIT_UNTIL(4);
	return;
}

/*CP D*/
static void op_0xba(Z80EX_CONTEXT *cpu)
{
	CP(D);
	T_WAIT_UNTIL(4);
	return;
}

/*CP E*/
static void op_0xbb(Z80EX_CONTEXT *cpu)
{
	CP(E);
	T_WAIT_UNTIL(4);
	return;
}

/*CP H*/
static void op_0xbc(Z80EX_CONTEXT *cpu)
{
	CP(H);
	T_WAIT_UNTIL(4);
	return;
}

/*CP L*/
static void op_0xbd(Z80EX_CONTEXT *cpu)
{
	CP(L);
	T_WAIT_UNTIL(4);
	return;
}

/*CP (HL)*/
static void op_0xbe(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_byte,(HL),4);
	CP(temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*CP A*/
static void op_0xbf(Z80EX_CONTEXT *cpu)
{
	CP(A);
	T_WAIT_UNTIL(4);
	return;
}

/*RET NZ*/
static void op_0xc0(Z80EX_CONTEXT *cpu)
{
	if(!(F & FLAG_Z)) {
	RET(/*rd*/5,8);
	T_WAIT_UNTIL(11);
	}
	else { T_WAIT_UNTIL(5);}
	return;
}

/*POP BC*/
static void op_0xc1(Z80EX_CONTEXT *cpu)
{
	POP(BC, /*rd*/4,7);
	T_WAIT_UNTIL(10);
	return;
}

/*JP NZ,@*/
static void op_0xc2(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	if(!(F & FLAG_Z)) {
	JP(temp_word.w);
	T_WAIT_UNTIL(10);
	}
	else { T_WAIT_UNTIL(10);MEMPTR=temp_word.w;}
	return;
}

/*JP @*/
static void op_0xc3(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	JP(temp_word.w);
	T_WAIT_UNTIL(10);
	return;
}

/*CALL NZ,@*/
static void op_0xc4(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	if(!(F & FLAG_Z)) {
	CALL(temp_word.w, /*wr*/11,14);
	T_WAIT_UNTIL(17);
	}
	else { T_WAIT_UNTIL(10);MEMPTR=temp_word.w;}
	return;
}

/*PUSH BC*/
static void op_0xc5(Z80EX_CONTEXT *cpu)
{
	PUSH(BC, /*wr*/5,8);
	T_WAIT_UNTIL(11);
	return;
}

/*ADD A,#*/
static void op_0xc6(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	ADD(A,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*RST 0x00*/
static void op_0xc7(Z80EX_CONTEXT *cpu)
{
	RST(0x00, /*wr*/5,8);
	T_WAIT_UNTIL(11);
	return;
}

/*RET Z*/
static void op_0xc8(Z80EX_CONTEXT *cpu)
{
	if(F & FLAG_Z) {
	RET(/*rd*/5,8);
	T_WAIT_UNTIL(11);
	}
	else { T_WAIT_UNTIL(5);}
	return;
}

/*RET*/
static void op_0xc9(Z80EX_CONTEXT *cpu)
{
	RET(/*rd*/4,7);
	T_WAIT_UNTIL(10);
	return;
}

/*JP Z,@*/
static void op_0xca(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	if(F & FLAG_Z) {
	JP(temp_word.w);
	T_WAIT_UNTIL(10);
	}
	else { T_WAIT_UNTIL(10);MEMPTR=temp_word.w;}
	return;
}

static void op_p_CB(Z80EX_CONTEXT *cpu)
{
	cpu->prefix=0xCB;
	cpu->noint_once=1;
}

/*CALL Z,@*/
static void op_0xcc(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	if(F & FLAG_Z) {
	CALL(temp_word.w, /*wr*/11,14);
	T_WAIT_UNTIL(17);
	}
	else { T_WAIT_UNTIL(10);MEMPTR=temp_word.w;}
	return;
}

/*CALL @*/
static void op_0xcd(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	CALL(temp_word.w, /*wr*/11,14);
	T_WAIT_UNTIL(17);
	return;
}

/*ADC A,#*/
static void op_0xce(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	ADC(A,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*RST 0x08*/
static void op_0xcf(Z80EX_CONTEXT *cpu)
{
	RST(0x08, /*wr*/5,8);
	T_WAIT_UNTIL(11);
	return;
}

/*RET NC*/
static void op_0xd0(Z80EX_CONTEXT *cpu)
{
	if(!(F & FLAG_C)) {
	RET(/*rd*/5,8);
	T_WAIT_UNTIL(11);
	}
	else { T_WAIT_UNTIL(5);}
	return;
}

/*POP DE*/
static void op_0xd1(Z80EX_CONTEXT *cpu)
{
	POP(DE, /*rd*/4,7);
	T_WAIT_UNTIL(10);
	return;
}

/*JP NC,@*/
static void op_0xd2(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	if(!(F & FLAG_C)) {
	JP(temp_word.w);
	T_WAIT_UNTIL(10);
	}
	else { T_WAIT_UNTIL(10);MEMPTR=temp_word.w;}
	return;
}

/*OUT (#),A*/
static void op_0xd3(Z80EX_CONTEXT *cpu)
{
	temp_word.w=(READ_OP() + ( A << 8 ));
	OUT_A(temp_word.w,A, /*wr*/8);
	T_WAIT_UNTIL(11);
	return;
}

/*CALL NC,@*/
static void op_0xd4(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	if(!(F & FLAG_C)) {
	CALL(temp_word.w, /*wr*/11,14);
	T_WAIT_UNTIL(17);
	}
	else { T_WAIT_UNTIL(10);MEMPTR=temp_word.w;}
	return;
}

/*PUSH DE*/
static void op_0xd5(Z80EX_CONTEXT *cpu)
{
	PUSH(DE, /*wr*/5,8);
	T_WAIT_UNTIL(11);
	return;
}

/*SUB #*/
static void op_0xd6(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	SUB(temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*RST 0x10*/
static void op_0xd7(Z80EX_CONTEXT *cpu)
{
	RST(0x10, /*wr*/5,8);
	T_WAIT_UNTIL(11);
	return;
}

/*RET C*/
static void op_0xd8(Z80EX_CONTEXT *cpu)
{
	if(F & FLAG_C) {
	RET(/*rd*/5,8);
	T_WAIT_UNTIL(11);
	}
	else { T_WAIT_UNTIL(5);}
	return;
}

/*EXX*/
static void op_0xd9(Z80EX_CONTEXT *cpu)
{
	EXX();
	T_WAIT_UNTIL(4);
	return;
}

/*JP C,@*/
static void op_0xda(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	if(F & FLAG_C) {
	JP(temp_word.w);
	T_WAIT_UNTIL(10);
	}
	else { T_WAIT_UNTIL(10);MEMPTR=temp_word.w;}
	return;
}

/*IN A,(#)*/
static void op_0xdb(Z80EX_CONTEXT *cpu)
{
	temp_word.w=(READ_OP() + ( A << 8 ));
	IN_A(A,temp_word.w, /*rd*/8);
	T_WAIT_UNTIL(11);
	return;
}

/*CALL C,@*/
static void op_0xdc(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	if(F & FLAG_C) {
	CALL(temp_word.w, /*wr*/11,14);
	T_WAIT_UNTIL(17);
	}
	else { T_WAIT_UNTIL(10);MEMPTR=temp_word.w;}
	return;
}

static void op_p_DD(Z80EX_CONTEXT *cpu)
{
	cpu->prefix=0xDD;
	cpu->noint_once=1;
}

/*SBC A,#*/
static void op_0xde(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	SBC(A,temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*RST 0x18*/
static void op_0xdf(Z80EX_CONTEXT *cpu)
{
	RST(0x18, /*wr*/5,8);
	T_WAIT_UNTIL(11);
	return;
}

/*RET PO*/
static void op_0xe0(Z80EX_CONTEXT *cpu)
{
	if(!(F & FLAG_P)) {
	RET(/*rd*/5,8);
	T_WAIT_UNTIL(11);
	}
	else { T_WAIT_UNTIL(5);}
	return;
}

/*POP HL*/
static void op_0xe1(Z80EX_CONTEXT *cpu)
{
	POP(HL, /*rd*/4,7);
	T_WAIT_UNTIL(10);
	return;
}

/*JP PO,@*/
static void op_0xe2(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	if(!(F & FLAG_P)) {
	JP(temp_word.w);
	T_WAIT_UNTIL(10);
	}
	else { T_WAIT_UNTIL(10);MEMPTR=temp_word.w;}
	return;
}

/*EX (SP),HL*/
static void op_0xe3(Z80EX_CONTEXT *cpu)
{
	READ_MEM(temp_word.b.l,(SP),4);
	READ_MEM(temp_word.b.h,(SP+1),7);
	EX_MPTR(temp_word.w,HL);
	WRITE_MEM((SP),temp_word.b.l,11);
	WRITE_MEM((SP+1),temp_word.b.h,14);
	T_WAIT_UNTIL(19);
	return;
}

/*CALL PO,@*/
static void op_0xe4(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	if(!(F & FLAG_P)) {
	CALL(temp_word.w, /*wr*/11,14);
	T_WAIT_UNTIL(17);
	}
	else { T_WAIT_UNTIL(10);MEMPTR=temp_word.w;}
	return;
}

/*PUSH HL*/
static void op_0xe5(Z80EX_CONTEXT *cpu)
{
	PUSH(HL, /*wr*/5,8);
	T_WAIT_UNTIL(11);
	return;
}

/*AND #*/
static void op_0xe6(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	AND(temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*RST 0x20*/
static void op_0xe7(Z80EX_CONTEXT *cpu)
{
	RST(0x20, /*wr*/5,8);
	T_WAIT_UNTIL(11);
	return;
}

/*RET PE*/
static void op_0xe8(Z80EX_CONTEXT *cpu)
{
	if(F & FLAG_P) {
	RET(/*rd*/5,8);
	T_WAIT_UNTIL(11);
	}
	else { T_WAIT_UNTIL(5);}
	return;
}

/*JP HL*/
static void op_0xe9(Z80EX_CONTEXT *cpu)
{
	JP_NO_MPTR(HL);
	T_WAIT_UNTIL(4);
	return;
}

/*JP PE,@*/
static void op_0xea(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	if(F & FLAG_P) {
	JP(temp_word.w);
	T_WAIT_UNTIL(10);
	}
	else { T_WAIT_UNTIL(10);MEMPTR=temp_word.w;}
	return;
}

/*EX DE,HL*/
static void op_0xeb(Z80EX_CONTEXT *cpu)
{
	EX(DE,HL);
	T_WAIT_UNTIL(4);
	return;
}

/*CALL PE,@*/
static void op_0xec(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	if(F & FLAG_P) {
	CALL(temp_word.w, /*wr*/11,14);
	T_WAIT_UNTIL(17);
	}
	else { T_WAIT_UNTIL(10);MEMPTR=temp_word.w;}
	return;
}

static void op_p_ED(Z80EX_CONTEXT *cpu)
{
	cpu->prefix=0xED;
	cpu->noint_once=1;
}

/*XOR #*/
static void op_0xee(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	XOR(temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*RST 0x28*/
static void op_0xef(Z80EX_CONTEXT *cpu)
{
	RST(0x28, /*wr*/5,8);
	T_WAIT_UNTIL(11);
	return;
}

/*RET P*/
static void op_0xf0(Z80EX_CONTEXT *cpu)
{
	if(!(F & FLAG_S)) {
	RET(/*rd*/5,8);
	T_WAIT_UNTIL(11);
	}
	else { T_WAIT_UNTIL(5);}
	return;
}

/*POP AF*/
static void op_0xf1(Z80EX_CONTEXT *cpu)
{
	POP(AF, /*rd*/4,7);
	T_WAIT_UNTIL(10);
	return;
}

/*JP P,@*/
static void op_0xf2(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	if(!(F & FLAG_S)) {
	JP(temp_word.w);
	T_WAIT_UNTIL(10);
	}
	else { T_WAIT_UNTIL(10);MEMPTR=temp_word.w;}
	return;
}

/*DI*/
static void op_0xf3(Z80EX_CONTEXT *cpu)
{
	DI();
	T_WAIT_UNTIL(4);
	return;
}

/*CALL P,@*/
static void op_0xf4(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	if(!(F & FLAG_S)) {
	CALL(temp_word.w, /*wr*/11,14);
	T_WAIT_UNTIL(17);
	}
	else { T_WAIT_UNTIL(10);MEMPTR=temp_word.w;}
	return;
}

/*PUSH AF*/
static void op_0xf5(Z80EX_CONTEXT *cpu)
{
	PUSH(AF, /*wr*/5,8);
	T_WAIT_UNTIL(11);
	return;
}

/*OR #*/
static void op_0xf6(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	OR(temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*RST 0x30*/
static void op_0xf7(Z80EX_CONTEXT *cpu)
{
	RST(0x30, /*wr*/5,8);
	T_WAIT_UNTIL(11);
	return;
}

/*RET M*/
static void op_0xf8(Z80EX_CONTEXT *cpu)
{
	if(F & FLAG_S) {
	RET(/*rd*/5,8);
	T_WAIT_UNTIL(11);
	}
	else { T_WAIT_UNTIL(5);}
	return;
}

/*LD SP,HL*/
static void op_0xf9(Z80EX_CONTEXT *cpu)
{
	LD16(SP,HL);
	T_WAIT_UNTIL(6);
	return;
}

/*JP M,@*/
static void op_0xfa(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	if(F & FLAG_S) {
	JP(temp_word.w);
	T_WAIT_UNTIL(10);
	}
	else { T_WAIT_UNTIL(10);MEMPTR=temp_word.w;}
	return;
}

/*EI*/
static void op_0xfb(Z80EX_CONTEXT *cpu)
{
	EI();
	T_WAIT_UNTIL(4);
	return;
}

/*CALL M,@*/
static void op_0xfc(Z80EX_CONTEXT *cpu)
{
	temp_word.b.l=READ_OP();
	temp_word.b.h=READ_OP();
	if(F & FLAG_S) {
	CALL(temp_word.w, /*wr*/11,14);
	T_WAIT_UNTIL(17);
	}
	else { T_WAIT_UNTIL(10);MEMPTR=temp_word.w;}
	return;
}

static void op_p_FD(Z80EX_CONTEXT *cpu)
{
	cpu->prefix=0xFD;
	cpu->noint_once=1;
}

/*CP #*/
static void op_0xfe(Z80EX_CONTEXT *cpu)
{
	temp_byte=READ_OP();
	CP(temp_byte);
	T_WAIT_UNTIL(7);
	return;
}

/*RST 0x38*/
static void op_0xff(Z80EX_CONTEXT *cpu)
{
	RST(0x38, /*wr*/5,8);
	T_WAIT_UNTIL(11);
	return;
}



/**/
static z80ex_opcode_fn opcodes_base[0x100] = {
 op_0x00       , op_0x01       , op_0x02       , op_0x03       ,
 op_0x04       , op_0x05       , op_0x06       , op_0x07       ,
 op_0x08       , op_0x09       , op_0x0a       , op_0x0b       ,
 op_0x0c       , op_0x0d       , op_0x0e       , op_0x0f       ,
 op_0x10       , op_0x11       , op_0x12       , op_0x13       ,
 op_0x14       , op_0x15       , op_0x16       , op_0x17       ,
 op_0x18       , op_0x19       , op_0x1a       , op_0x1b       ,
 op_0x1c       , op_0x1d       , op_0x1e       , op_0x1f       ,
 op_0x20       , op_0x21       , op_0x22       , op_0x23       ,
 op_0x24       , op_0x25       , op_0x26       , op_0x27       ,
 op_0x28       , op_0x29       , op_0x2a       , op_0x2b       ,
 op_0x2c       , op_0x2d       , op_0x2e       , op_0x2f       ,
 op_0x30       , op_0x31       , op_0x32       , op_0x33       ,
 op_0x34       , op_0x35       , op_0x36       , op_0x37       ,
 op_0x38       , op_0x39       , op_0x3a       , op_0x3b       ,
 op_0x3c       , op_0x3d       , op_0x3e       , op_0x3f       ,
 op_0x40       , op_0x41       , op_0x42       , op_0x43       ,
 op_0x44       , op_0x45       , op_0x46       , op_0x47       ,
 op_0x48       , op_0x49       , op_0x4a       , op_0x4b       ,
 op_0x4c       , op_0x4d       , op_0x4e       , op_0x4f       ,
 op_0x50       , op_0x51       , op_0x52       , op_0x53       ,
 op_0x54       , op_0x55       , op_0x56       , op_0x57       ,
 op_0x58       , op_0x59       , op_0x5a       , op_0x5b       ,
 op_0x5c       , op_0x5d       , op_0x5e       , op_0x5f       ,
 op_0x60       , op_0x61       , op_0x62       , op_0x63       ,
 op_0x64       , op_0x65       , op_0x66       , op_0x67       ,
 op_0x68       , op_0x69       , op_0x6a       , op_0x6b       ,
 op_0x6c       , op_0x6d       , op_0x6e       , op_0x6f       ,
 op_0x70       , op_0x71       , op_0x72       , op_0x73       ,
 op_0x74       , op_0x75       , op_0x76       , op_0x77       ,
 op_0x78       , op_0x79       , op_0x7a       , op_0x7b       ,
 op_0x7c       , op_0x7d       , op_0x7e       , op_0x7f       ,
 op_0x80       , op_0x81       , op_0x82       , op_0x83       ,
 op_0x84       , op_0x85       , op_0x86       , op_0x87       ,
 op_0x88       , op_0x89       , op_0x8a       , op_0x8b       ,
 op_0x8c       , op_0x8d       , op_0x8e       , op_0x8f       ,
 op_0x90       , op_0x91       , op_0x92       , op_0x93       ,
 op_0x94       , op_0x95       , op_0x96       , op_0x97       ,
 op_0x98       , op_0x99       , op_0x9a       , op_0x9b       ,
 op_0x9c       , op_0x9d       , op_0x9e       , op_0x9f       ,
 op_0xa0       , op_0xa1       , op_0xa2       , op_0xa3       ,
 op_0xa4       , op_0xa5       , op_0xa6       , op_0xa7       ,
 op_0xa8       , op_0xa9       , op_0xaa       , op_0xab       ,
 op_0xac       , op_0xad       , op_0xae       , op_0xaf       ,
 op_0xb0       , op_0xb1       , op_0xb2       , op_0xb3       ,
 op_0xb4       , op_0xb5       , op_0xb6       , op_0xb7       ,
 op_0xb8       , op_0xb9       , op_0xba       , op_0xbb       ,
 op_0xbc       , op_0xbd       , op_0xbe       , op_0xbf       ,
 op_0xc0       , op_0xc1       , op_0xc2       , op_0xc3       ,
 op_0xc4       , op_0xc5       , op_0xc6       , op_0xc7       ,
 op_0xc8       , op_0xc9       , op_0xca       , op_p_CB       ,
 op_0xcc       , op_0xcd       , op_0xce       , op_0xcf       ,
 op_0xd0       , op_0xd1       , op_0xd2       , op_0xd3       ,
 op_0xd4       , op_0xd5       , op_0xd6       , op_0xd7       ,
 op_0xd8       , op_0xd9       , op_0xda       , op_0xdb       ,
 op_0xdc       , op_p_DD       , op_0xde       , op_0xdf       ,
 op_0xe0       , op_0xe1       , op_0xe2       , op_0xe3       ,
 op_0xe4       , op_0xe5       , op_0xe6       , op_0xe7       ,
 op_0xe8       , op_0xe9       , op_0xea       , op_0xeb       ,
 op_0xec       , op_p_ED       , op_0xee       , op_0xef       ,
 op_0xf0       , op_0xf1       , op_0xf2       , op_0xf3       ,
 op_0xf4       , op_0xf5       , op_0xf6       , op_0xf7       ,
 op_0xf8       , op_0xf9       , op_0xfa       , op_0xfb       ,
 op_0xfc       , op_p_FD       , op_0xfe       , op_0xff       
};
