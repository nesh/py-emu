/** Z80: portable Z80 emulator *******************************/
/**                                                         **/
/**                         CodesED.h                       **/
/**                                                         **/
/** This file contains implementation for the ED table of   **/
/** Z80 commands. It is included from Z80.c.                **/
/**                                                         **/
/** Copyright (C) Marat Fayzullin 1994-2007                 **/
/**     You are not allowed to distribute this software     **/
/**     commercially. Please, notify me, if you make any    **/
/**     changes to this file.                               **/
/*************************************************************/

/** This is a special patch for emulating BIOS calls: ********/
case DB_FE:     PatchZ80(R);break;
/*************************************************************/

case ADC_HL_BC: M_ADCW(BC);break;
case ADC_HL_DE: M_ADCW(DE);break;
case ADC_HL_HL: M_ADCW(HL);break;
case ADC_HL_SP: M_ADCW(SP);break;

case SBC_HL_BC: M_SBCW(BC);break;
case SBC_HL_DE: M_SBCW(DE);break;
case SBC_HL_HL: M_SBCW(HL);break;
case SBC_HL_SP: M_SBCW(SP);break;

case LD_xWORDe_HL:
  J.B.l=OpZ80(R->PC.W++);
  J.B.h=OpZ80(R->PC.W++);
  WrZ80(J.W++,R->HL.B.l);
  WrZ80(J.W,R->HL.B.h);
  break;
case LD_xWORDe_DE:
  J.B.l=OpZ80(R->PC.W++);
  J.B.h=OpZ80(R->PC.W++);
  WrZ80(J.W++,R->DE.B.l);
  WrZ80(J.W,R->DE.B.h);
  break;
case LD_xWORDe_BC:
  J.B.l=OpZ80(R->PC.W++);
  J.B.h=OpZ80(R->PC.W++);
  WrZ80(J.W++,R->BC.B.l);
  WrZ80(J.W,R->BC.B.h);
  break;
case LD_xWORDe_SP:
  J.B.l=OpZ80(R->PC.W++);
  J.B.h=OpZ80(R->PC.W++);
  WrZ80(J.W++,R->SP.B.l);
  WrZ80(J.W,R->SP.B.h);
  break;

case LD_HL_xWORDe:
  J.B.l=OpZ80(R->PC.W++);
  J.B.h=OpZ80(R->PC.W++);
  R->HL.B.l=RdZ80(J.W++);
  R->HL.B.h=RdZ80(J.W);
  break;
case LD_DE_xWORDe:
  J.B.l=OpZ80(R->PC.W++);
  J.B.h=OpZ80(R->PC.W++);
  R->DE.B.l=RdZ80(J.W++);
  R->DE.B.h=RdZ80(J.W);
  break;
case LD_BC_xWORDe:
  J.B.l=OpZ80(R->PC.W++);
  J.B.h=OpZ80(R->PC.W++);
  R->BC.B.l=RdZ80(J.W++);
  R->BC.B.h=RdZ80(J.W);
  break;
case LD_SP_xWORDe:
  J.B.l=OpZ80(R->PC.W++);
  J.B.h=OpZ80(R->PC.W++);
  R->SP.B.l=RdZ80(J.W++);
  R->SP.B.h=RdZ80(J.W);
  break;

case RRD:
    I = RdZ80(R->HL.W);
    J.B.l = (I >> 4) | (A << 4);
    WrZ80(R->HL.W, J.B.l);
    A = (I & 0x0F) | (A & 0xF0);
    F = PZSTable[A] | (F & C_FLAG) | FLAGS_XY(A);
    break;
  
case RLD:
    I = RdZ80(R->HL.W);
    J.B.l = (I << 4) | (A & 0x0F);
    WrZ80(R->HL.W, J.B.l);
    A = (I >> 4) | (A & 0xF0);
    F = PZSTable[A] | (F & C_FLAG) | FLAGS_XY(A);
    break;

case LD_A_I:
  A = R->I;
  F = (F & C_FLAG)
              | (R->IFF & IFF_2 ? P_FLAG : 0)
              | ZSTable[A]
              | FLAGS_XY(A);
  break;

case LD_A_R:
  A = R->R;
  F = (F & C_FLAG)
              | (R->IFF & IFF_2 ? P_FLAG:0)
              | ZSTable[A]
              | FLAGS_XY(A);
  break;

case LD_I_A: R->I = A; break;
case LD_R_A: SET_R(A); break;

case 0x4E:
case 0x66:
case 0x6E:
case IM_0:
    R->IFF &= ~(IFF_IM1 | IFF_IM2);
    break;

case 0x76:
case IM_1:
    R->IFF = (R->IFF & ~IFF_IM2) | IFF_IM1;
    break;

case 0x7E:
case IM_2:
    R->IFF = (R->IFF & ~IFF_IM1) | IFF_IM2;
    break;

case 0x55:
case 0x5D:
case 0x65:
case 0x6D:
case 0x75:
case 0x7D:
case RETI:
case RETN:
    if(R->IFF & IFF_2)
        R->IFF |= IFF_1;
    else
        R->IFF &= ~IFF_1;
    M_RET;
    break;

case 0x4C:
case 0x54:
case 0x5C:
case 0x64:
case 0x6C:
case 0x74:
case 0x7C:
case NEG:
    I = A;
    A = 0;
    M_SUB(I);
    break;

case IN_B_xC:  M_IN(R->BC.B.h);break;
case IN_C_xC:  M_IN(R->BC.B.l);break;
case IN_D_xC:  M_IN(R->DE.B.h);break;
case IN_E_xC:  M_IN(R->DE.B.l);break;
case IN_H_xC:  M_IN(R->HL.B.h);break;
case IN_L_xC:  M_IN(R->HL.B.l);break;
case IN_A_xC:  M_IN(A);break;
case IN_F_xC:  M_IN(J.B.l);break;

case OUT_xC_B: OutZ80(R->BC.W,R->BC.B.h);break;
case OUT_xC_C: OutZ80(R->BC.W,R->BC.B.l);break;
case OUT_xC_D: OutZ80(R->BC.W,R->DE.B.h);break;
case OUT_xC_E: OutZ80(R->BC.W,R->DE.B.l);break;
case OUT_xC_H: OutZ80(R->BC.W,R->HL.B.h);break;
case OUT_xC_L: OutZ80(R->BC.W,R->HL.B.l);break;
case OUT_xC_A: OutZ80(R->BC.W,A);break;
// OUT (C), 0
case 0x71: OutZ80(R->BC.W, 0); break;

case INI:
    n = InZ80(R->BC.W);
    WrZ80(R->HL.W++, n);
    --R->BC.B.h;
    F =
        (n & (1 << 7) ? N_FLAG : 0)
        | ZSTable[R->BC.B.h] | FLAGS_XY(R->BC.B.h);
    // F = N_FLAG | (R->BC.B.h ? 0 : Z_FLAG) | FLAGS_XY(R->BC.B.h);
    break;

case INIR:
  do
  {
    WrZ80(R->HL.W++,InZ80(R->BC.W));
    --R->BC.B.h;CYCLES_ADD(21);
  }
  while(R->BC.B.h&&(R->ICount>0));
  if(R->BC.B.h) { F=N_FLAG;R->PC.W-=2; }
  else { F=Z_FLAG|N_FLAG;CYCLES_SUB(5); }
  break;

case IND:
  WrZ80(R->HL.W--,InZ80(R->BC.W));
  --R->BC.B.h;
  F=N_FLAG|(R->BC.B.h? 0:Z_FLAG);
  break;

case INDR:
  do
  {
    WrZ80(R->HL.W--,InZ80(R->BC.W));
    --R->BC.B.h;CYCLES_ADD(21);
  }
  while(R->BC.B.h&&(R->ICount>0));
  if(R->BC.B.h) { F=N_FLAG;R->PC.W-=2; }
  else { F=Z_FLAG|N_FLAG;CYCLES_SUB(5); }
  break;

case OUTI:
    --R->BC.B.h;
    I = RdZ80(R->HL.W++);
    OutZ80(R->BC.W, I);
    F = N_FLAG | (R->BC.B.h ? 0 : Z_FLAG)
                | (R->HL.B.l + I > 255 ? (C_FLAG | H_FLAG) : 0);
    break;

case OTIR:
  do
  {
    --R->BC.B.h;
    I=RdZ80(R->HL.W++);
    OutZ80(R->BC.W,I);
    CYCLES_ADD(21);
  }
  while(R->BC.B.h&&(R->ICount>0));
  if(R->BC.B.h)
  {
    F=N_FLAG|(R->HL.B.l+I>255? (C_FLAG|H_FLAG):0);
    R->PC.W-=2;
  }
  else
  {
    F=Z_FLAG|N_FLAG|(R->HL.B.l+I>255? (C_FLAG|H_FLAG):0);
    CYCLES_SUB(5);
  }
  break;

case OUTD:
  --R->BC.B.h;
  I=RdZ80(R->HL.W--);
  OutZ80(R->BC.W,I);
  F=N_FLAG|(R->BC.B.h? 0:Z_FLAG)|(R->HL.B.l+I>255? (C_FLAG|H_FLAG):0);
  break;

case OTDR:
  do
  {
    --R->BC.B.h;
    I=RdZ80(R->HL.W--);
    OutZ80(R->BC.W,I);
    CYCLES_ADD(21);
  }
  while(R->BC.B.h&&(R->ICount>0));
  if(R->BC.B.h)
  {
    F=N_FLAG|(R->HL.B.l+I>255? (C_FLAG|H_FLAG):0);
    R->PC.W-=2;
  }
  else
  {
    F=Z_FLAG|N_FLAG|(R->HL.B.l+I>255? (C_FLAG|H_FLAG):0);
    CYCLES_SUB(5);
  }
  break;

#define M_LDI { \
    register word io = RdZ80(R->HL.W); \
    WrZ80(R->DE.W, io); \
    F &= S_FLAG | Z_FLAG | C_FLAG; \
    if ((A + io) & 0x02) F |= Y_FLAG; \
    if ((A + io) & 0x08) F |= X_FLAG; \
    R->HL.W++; R->DE.W++; R->BC.W--; \
    if (R->BC.W) F |= V_FLAG; \
}

case LDI: M_LDI; break;

case LDIR:
    M_LDI;
    if(R->BC.W) {
        R->PC.W -= 2;
    } else {
        CYCLES_SUB(5);
    }
    break;

// case LDIR:
//   do
//   {
//     WrZ80(R->DE.W++,RdZ80(R->HL.W++));
//     --R->BC.W;CYCLES_ADD(21);
//   }
//   while(R->BC.W&&(R->ICount>0));
//   F&=~(N_FLAG|H_FLAG|P_FLAG);
//   if(R->BC.W) { F|=N_FLAG;R->PC.W-=2; }
//   else CYCLES_SUB(5);
//   break;

case LDD:
  WrZ80(R->DE.W--,RdZ80(R->HL.W--));
  --R->BC.W;
  F=(F&~(N_FLAG|H_FLAG|P_FLAG))|(R->BC.W? P_FLAG:0);
  break;

case LDDR:
  do
  {
    WrZ80(R->DE.W--,RdZ80(R->HL.W--));
    --R->BC.W;CYCLES_ADD(21);
  }
  while(R->BC.W&&(R->ICount>0));
  F&=~(N_FLAG|H_FLAG|P_FLAG);
  if(R->BC.W) { F|=N_FLAG;R->PC.W-=2; }
  else CYCLES_SUB(5);
  break;

case CPI:
    I = RdZ80(R->HL.W++);
    J.B.l = A - I;
    --R->BC.W;
    F =
        N_FLAG | (F & C_FLAG) | ZSTable[J.B.l]
        | ((A ^ I ^ J.B.l) & H_FLAG) | (R->BC.W ? P_FLAG : 0);
    n = A - I - (F & H_FLAG ? 1 : 0);
    F |= (n & (1 << 1) ? Y_FLAG : 0)
                 | (n & (1 << 3) ? X_FLAG : 0);
    break;

case CPIR:
  do
  {
    I=RdZ80(R->HL.W++);
    J.B.l=A-I;
    --R->BC.W;CYCLES_ADD(21);
  }  
  while(R->BC.W&&J.B.l&&(R->ICount>0));
  F =
    N_FLAG|(F&C_FLAG)|ZSTable[J.B.l]|
    ((A^I^J.B.l)&H_FLAG)|(R->BC.W? P_FLAG:0);
  if(R->BC.W&&J.B.l) R->PC.W-=2; else CYCLES_SUB(5);
  break;  

case CPD:
  I=RdZ80(R->HL.W--);
  J.B.l=A-I;
  --R->BC.W;
  F =
    N_FLAG|(F&C_FLAG)|ZSTable[J.B.l]|
    ((A^I^J.B.l)&H_FLAG)|(R->BC.W? P_FLAG:0);
  break;

case CPDR:
  do
  {
    I=RdZ80(R->HL.W--);
    J.B.l=A-I;
    --R->BC.W;CYCLES_ADD(21);
  }
  while(R->BC.W&&J.B.l);
  F =
    N_FLAG|(F&C_FLAG)|ZSTable[J.B.l]|
    ((A^I^J.B.l)&H_FLAG)|(R->BC.W? P_FLAG:0);
  if(R->BC.W&&J.B.l) R->PC.W-=2; else CYCLES_SUB(5);
  break;
