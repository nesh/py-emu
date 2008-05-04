/** Z80: portable Z80 emulator *******************************/
/**                                                         **/
/**                         CodesXCB.h                      **/
/**                                                         **/
/** This file contains implementation for FD/DD-CB tables   **/
/** of Z80 commands. It is included from Z80.c.             **/
/**                                                         **/
/** Copyright (C) Marat Fayzullin 1994-2007                 **/
/**     You are not allowed to distribute this software     **/
/**     commercially. Please, notify me, if you make any    **/
/**     changes to this file.                               **/
/*************************************************************/

case RLC_xHL: I=RdZ80(J.W);M_RLC(I);WrZ80(J.W,I);break;
case RRC_xHL: I=RdZ80(J.W);M_RRC(I);WrZ80(J.W,I);break;
case RL_xHL:  I=RdZ80(J.W);M_RL(I);WrZ80(J.W,I);break;
case RR_xHL:  I=RdZ80(J.W);M_RR(I);WrZ80(J.W,I);break;
case SLA_xHL: I=RdZ80(J.W);M_SLA(I);WrZ80(J.W,I);break;
case SRA_xHL: I=RdZ80(J.W);M_SRA(I);WrZ80(J.W,I);break;
case SLL_xHL: I=RdZ80(J.W);M_SLL(I);WrZ80(J.W,I);break;
case SRL_xHL: I=RdZ80(J.W);M_SRL(I);WrZ80(J.W,I);break;

case BIT0_B: case BIT0_C: case BIT0_D: case BIT0_E:
case BIT0_H: case BIT0_L: case BIT0_A:
case BIT0_xHL: I=RdZ80(J.W);M_BIT(0,I);break;
case BIT1_B: case BIT1_C: case BIT1_D: case BIT1_E:
case BIT1_H: case BIT1_L: case BIT1_A:
case BIT1_xHL: I=RdZ80(J.W);M_BIT(1,I);break;
case BIT2_B: case BIT2_C: case BIT2_D: case BIT2_E:
case BIT2_H: case BIT2_L: case BIT2_A:
case BIT2_xHL: I=RdZ80(J.W);M_BIT(2,I);break;
case BIT3_B: case BIT3_C: case BIT3_D: case BIT3_E:
case BIT3_H: case BIT3_L: case BIT3_A:
case BIT3_xHL: I=RdZ80(J.W);M_BIT(3,I);break;
case BIT4_B: case BIT4_C: case BIT4_D: case BIT4_E:
case BIT4_H: case BIT4_L: case BIT4_A:
case BIT4_xHL: I=RdZ80(J.W);M_BIT(4,I);break;
case BIT5_B: case BIT5_C: case BIT5_D: case BIT5_E:
case BIT5_H: case BIT5_L: case BIT5_A:
case BIT5_xHL: I=RdZ80(J.W);M_BIT(5,I);break;
case BIT6_B: case BIT6_C: case BIT6_D: case BIT6_E:
case BIT6_H: case BIT6_L: case BIT6_A:
case BIT6_xHL: I=RdZ80(J.W);M_BIT(6,I);break;
case BIT7_B: case BIT7_C: case BIT7_D: case BIT7_E:
case BIT7_H: case BIT7_L: case BIT7_A:
case BIT7_xHL: I=RdZ80(J.W);M_BIT(7,I);break;

case RES0_xHL: I=RdZ80(J.W);M_RES(0,I);WrZ80(J.W,I);break;
case RES1_xHL: I=RdZ80(J.W);M_RES(1,I);WrZ80(J.W,I);break;   
case RES2_xHL: I=RdZ80(J.W);M_RES(2,I);WrZ80(J.W,I);break;   
case RES3_xHL: I=RdZ80(J.W);M_RES(3,I);WrZ80(J.W,I);break;   
case RES4_xHL: I=RdZ80(J.W);M_RES(4,I);WrZ80(J.W,I);break;   
case RES5_xHL: I=RdZ80(J.W);M_RES(5,I);WrZ80(J.W,I);break;   
case RES6_xHL: I=RdZ80(J.W);M_RES(6,I);WrZ80(J.W,I);break;   
case RES7_xHL: I=RdZ80(J.W);M_RES(7,I);WrZ80(J.W,I);break;   

case SET0_xHL: I=RdZ80(J.W);M_SET(0,I);WrZ80(J.W,I);break;   
case SET1_xHL: I=RdZ80(J.W);M_SET(1,I);WrZ80(J.W,I);break; 
case SET2_xHL: I=RdZ80(J.W);M_SET(2,I);WrZ80(J.W,I);break; 
case SET3_xHL: I=RdZ80(J.W);M_SET(3,I);WrZ80(J.W,I);break; 
case SET4_xHL: I=RdZ80(J.W);M_SET(4,I);WrZ80(J.W,I);break; 
case SET5_xHL: I=RdZ80(J.W);M_SET(5,I);WrZ80(J.W,I);break; 
case SET6_xHL: I=RdZ80(J.W);M_SET(6,I);WrZ80(J.W,I);break; 
case SET7_xHL: I=RdZ80(J.W);M_SET(7,I);WrZ80(J.W,I);break; 

// =========
// = UNDOC =
// =========
#define M_RLC_X(reg) \
    reg=RdZ80(J.W); \
    M_RLC(reg); \
    WrZ80(J.W, reg)
case RLC_B: M_RLC_X(R->BC.B.h); break;
case RLC_C: M_RLC_X(R->BC.B.l); break;
case RLC_D: M_RLC_X(R->DE.B.h); break;
case RLC_E: M_RLC_X(R->DE.B.l); break;
case RLC_H: M_RLC_X(R->HL.B.h); break;
case RLC_L: M_RLC_X(R->HL.B.l); break;
case RLC_A: M_RLC_X(R->AF.B.h); break;

#define M_RRC_X(reg) \
    reg=RdZ80(J.W); \
    M_RRC(reg); \
    WrZ80(J.W, reg)
case RRC_B: M_RRC_X(R->BC.B.h); break;
case RRC_C: M_RRC_X(R->BC.B.l); break;
case RRC_D: M_RRC_X(R->DE.B.h); break;
case RRC_E: M_RRC_X(R->DE.B.l); break;
case RRC_H: M_RRC_X(R->HL.B.h); break;
case RRC_L: M_RRC_X(R->HL.B.l); break;
case RRC_A: M_RRC_X(R->AF.B.h); break;

#define M_RL_X(reg) \
    reg=RdZ80(J.W); \
    M_RL(reg); \
    WrZ80(J.W, reg)
case RL_B: M_RL_X(R->BC.B.h); break;
case RL_C: M_RL_X(R->BC.B.l); break;
case RL_D: M_RL_X(R->DE.B.h); break;
case RL_E: M_RL_X(R->DE.B.l); break;
case RL_H: M_RL_X(R->HL.B.h); break;
case RL_L: M_RL_X(R->HL.B.l); break;
case RL_A: M_RL_X(R->AF.B.h); break;

#define M_RR_X(reg) \
    reg=RdZ80(J.W); \
    M_RR(reg); \
    WrZ80(J.W, reg)
case RR_B: M_RR_X(R->BC.B.h); break;
case RR_C: M_RR_X(R->BC.B.l); break;
case RR_D: M_RR_X(R->DE.B.h); break;
case RR_E: M_RR_X(R->DE.B.l); break;
case RR_H: M_RR_X(R->HL.B.h); break;
case RR_L: M_RR_X(R->HL.B.l); break;
case RR_A: M_RR_X(R->AF.B.h); break;

#define M_SLA_X(reg) \
    reg=RdZ80(J.W); \
    M_SLA(reg); \
    WrZ80(J.W, reg)
case SLA_B: M_SLA_X(R->BC.B.h); break;
case SLA_C: M_SLA_X(R->BC.B.l); break;
case SLA_D: M_SLA_X(R->DE.B.h); break;
case SLA_E: M_SLA_X(R->DE.B.l); break;
case SLA_H: M_SLA_X(R->HL.B.h); break;
case SLA_L: M_SLA_X(R->HL.B.l); break;
case SLA_A: M_SLA_X(R->AF.B.h); break;

#define M_SRA_X(reg) \
    reg=RdZ80(J.W); \
    M_SRA(reg); \
    WrZ80(J.W, reg)
case SRA_B: M_SRA_X(R->BC.B.h); break;
case SRA_C: M_SRA_X(R->BC.B.l); break;
case SRA_D: M_SRA_X(R->DE.B.h); break;
case SRA_E: M_SRA_X(R->DE.B.l); break;
case SRA_H: M_SRA_X(R->HL.B.h); break;
case SRA_L: M_SRA_X(R->HL.B.l); break;
case SRA_A: M_SRA_X(R->AF.B.h); break;

#define M_SLL_X(reg) \
    reg=RdZ80(J.W); \
    M_SLL(reg); \
    WrZ80(J.W, reg)
case SLL_B: M_SLL_X(R->BC.B.h); break;
case SLL_C: M_SLL_X(R->BC.B.l); break;
case SLL_D: M_SLL_X(R->DE.B.h); break;
case SLL_E: M_SLL_X(R->DE.B.l); break;
case SLL_H: M_SLL_X(R->HL.B.h); break;
case SLL_L: M_SLL_X(R->HL.B.l); break;
case SLL_A: M_SLL_X(R->AF.B.h); break;

#define M_SRL_X(reg) \
    reg=RdZ80(J.W); \
    M_SRL(reg); \
    WrZ80(J.W, reg)
case SRL_B: M_SRL_X(R->BC.B.h); break;
case SRL_C: M_SRL_X(R->BC.B.l); break;
case SRL_D: M_SRL_X(R->DE.B.h); break;
case SRL_E: M_SRL_X(R->DE.B.l); break;
case SRL_H: M_SRL_X(R->HL.B.h); break;
case SRL_L: M_SRL_X(R->HL.B.l); break;
case SRL_A: M_SRL_X(R->AF.B.h); break;

#define RES_X(reg, bit) \
    reg = RdZ80(J.W); \
    M_RES(bit, reg); \
    WrZ80(J.W, reg)
case RES0_B: RES_X(R->BC.B.h, 0); break;
case RES0_C: RES_X(R->BC.B.l, 0); break;
case RES0_D: RES_X(R->DE.B.h, 0); break;
case RES0_E: RES_X(R->DE.B.l, 0); break;
case RES0_H: RES_X(R->HL.B.h, 0); break;
case RES0_L: RES_X(R->HL.B.l, 0); break;
case RES0_A: RES_X(R->AF.B.h, 0); break;

case RES1_B: RES_X(R->BC.B.h, 1); break;
case RES1_C: RES_X(R->BC.B.l, 1); break;
case RES1_D: RES_X(R->DE.B.h, 1); break;
case RES1_E: RES_X(R->DE.B.l, 1); break;
case RES1_H: RES_X(R->HL.B.h, 1); break;
case RES1_L: RES_X(R->HL.B.l, 1); break;
case RES1_A: RES_X(R->AF.B.h, 1); break;

case RES2_B: RES_X(R->BC.B.h, 2); break;
case RES2_C: RES_X(R->BC.B.l, 2); break;
case RES2_D: RES_X(R->DE.B.h, 2); break;
case RES2_E: RES_X(R->DE.B.l, 2); break;
case RES2_H: RES_X(R->HL.B.h, 2); break;
case RES2_L: RES_X(R->HL.B.l, 2); break;
case RES2_A: RES_X(R->AF.B.h, 2); break;

case RES3_B: RES_X(R->BC.B.h, 3); break;
case RES3_C: RES_X(R->BC.B.l, 3); break;
case RES3_D: RES_X(R->DE.B.h, 3); break;
case RES3_E: RES_X(R->DE.B.l, 3); break;
case RES3_H: RES_X(R->HL.B.h, 3); break;
case RES3_L: RES_X(R->HL.B.l, 3); break;
case RES3_A: RES_X(R->AF.B.h, 3); break;

case RES4_B: RES_X(R->BC.B.h, 4); break;
case RES4_C: RES_X(R->BC.B.l, 4); break;
case RES4_D: RES_X(R->DE.B.h, 4); break;
case RES4_E: RES_X(R->DE.B.l, 4); break;
case RES4_H: RES_X(R->HL.B.h, 4); break;
case RES4_L: RES_X(R->HL.B.l, 4); break;
case RES4_A: RES_X(R->AF.B.h, 4); break;

case RES5_B: RES_X(R->BC.B.h, 5); break;
case RES5_C: RES_X(R->BC.B.l, 5); break;
case RES5_D: RES_X(R->DE.B.h, 5); break;
case RES5_E: RES_X(R->DE.B.l, 5); break;
case RES5_H: RES_X(R->HL.B.h, 5); break;
case RES5_L: RES_X(R->HL.B.l, 5); break;
case RES5_A: RES_X(R->AF.B.h, 5); break;

case RES6_B: RES_X(R->BC.B.h, 6); break;
case RES6_C: RES_X(R->BC.B.l, 6); break;
case RES6_D: RES_X(R->DE.B.h, 6); break;
case RES6_E: RES_X(R->DE.B.l, 6); break;
case RES6_H: RES_X(R->HL.B.h, 6); break;
case RES6_L: RES_X(R->HL.B.l, 6); break;
case RES6_A: RES_X(R->AF.B.h, 6); break;

case RES7_B: RES_X(R->BC.B.h, 7); break;
case RES7_C: RES_X(R->BC.B.l, 7); break;
case RES7_D: RES_X(R->DE.B.h, 7); break;
case RES7_E: RES_X(R->DE.B.l, 7); break;
case RES7_H: RES_X(R->HL.B.h, 7); break;
case RES7_L: RES_X(R->HL.B.l, 7); break;
case RES7_A: RES_X(R->AF.B.h, 7); break;

#define SET_X(reg, bit) \
    reg = RdZ80(J.W); \
    M_SET(bit, reg); \
    WrZ80(J.W, reg)
case SET0_B: SET_X(R->BC.B.h, 0); break;
case SET0_C: SET_X(R->BC.B.l, 0); break;
case SET0_D: SET_X(R->DE.B.h, 0); break;
case SET0_E: SET_X(R->DE.B.l, 0); break;
case SET0_H: SET_X(R->HL.B.h, 0); break;
case SET0_L: SET_X(R->HL.B.l, 0); break;
case SET0_A: SET_X(R->AF.B.h, 0); break;

case SET1_B: SET_X(R->BC.B.h, 1); break;
case SET1_C: SET_X(R->BC.B.l, 1); break;
case SET1_D: SET_X(R->DE.B.h, 1); break;
case SET1_E: SET_X(R->DE.B.l, 1); break;
case SET1_H: SET_X(R->HL.B.h, 1); break;
case SET1_L: SET_X(R->HL.B.l, 1); break;
case SET1_A: SET_X(R->AF.B.h, 1); break;

case SET2_B: SET_X(R->BC.B.h, 2); break;
case SET2_C: SET_X(R->BC.B.l, 2); break;
case SET2_D: SET_X(R->DE.B.h, 2); break;
case SET2_E: SET_X(R->DE.B.l, 2); break;
case SET2_H: SET_X(R->HL.B.h, 2); break;
case SET2_L: SET_X(R->HL.B.l, 2); break;
case SET2_A: SET_X(R->AF.B.h, 2); break;

case SET3_B: SET_X(R->BC.B.h, 3); break;
case SET3_C: SET_X(R->BC.B.l, 3); break;
case SET3_D: SET_X(R->DE.B.h, 3); break;
case SET3_E: SET_X(R->DE.B.l, 3); break;
case SET3_H: SET_X(R->HL.B.h, 3); break;
case SET3_L: SET_X(R->HL.B.l, 3); break;
case SET3_A: SET_X(R->AF.B.h, 3); break;

case SET4_B: SET_X(R->BC.B.h, 4); break;
case SET4_C: SET_X(R->BC.B.l, 4); break;
case SET4_D: SET_X(R->DE.B.h, 4); break;
case SET4_E: SET_X(R->DE.B.l, 4); break;
case SET4_H: SET_X(R->HL.B.h, 4); break;
case SET4_L: SET_X(R->HL.B.l, 4); break;
case SET4_A: SET_X(R->AF.B.h, 4); break;

case SET5_B: SET_X(R->BC.B.h, 5); break;
case SET5_C: SET_X(R->BC.B.l, 5); break;
case SET5_D: SET_X(R->DE.B.h, 5); break;
case SET5_E: SET_X(R->DE.B.l, 5); break;
case SET5_H: SET_X(R->HL.B.h, 5); break;
case SET5_L: SET_X(R->HL.B.l, 5); break;
case SET5_A: SET_X(R->AF.B.h, 5); break;

case SET6_B: SET_X(R->BC.B.h, 6); break;
case SET6_C: SET_X(R->BC.B.l, 6); break;
case SET6_D: SET_X(R->DE.B.h, 6); break;
case SET6_E: SET_X(R->DE.B.l, 6); break;
case SET6_H: SET_X(R->HL.B.h, 6); break;
case SET6_L: SET_X(R->HL.B.l, 6); break;
case SET6_A: SET_X(R->AF.B.h, 6); break;

case SET7_B: SET_X(R->BC.B.h, 7); break;
case SET7_C: SET_X(R->BC.B.l, 7); break;
case SET7_D: SET_X(R->DE.B.h, 7); break;
case SET7_E: SET_X(R->DE.B.l, 7); break;
case SET7_H: SET_X(R->HL.B.h, 7); break;
case SET7_L: SET_X(R->HL.B.l, 7); break;
case SET7_A: SET_X(R->AF.B.h, 7); break;
