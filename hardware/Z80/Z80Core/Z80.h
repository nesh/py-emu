/** Z80: portable Z80 emulator *******************************/
/**                                                         **/
/**                           Z80.h                         **/
/**                                                         **/
/** This file contains declarations relevant to emulation   **/
/** of Z80 CPU.                                             **/
/**                                                         **/
/** Copyright (C) Marat Fayzullin 1994-2007                 **/
/**     You are not allowed to distribute this software     **/
/**     commercially. Please, notify me, if you make any    **/   
/**     changes to this file.                               **/
/*************************************************************/
#ifndef Z80_H
#define Z80_H

#ifdef __cplusplus
extern "C" {
#endif

                               /* Compilation options:       */
/* #define DEBUG */            /* Compile debugging version  */
/* #define LSB_FIRST */        /* Compile for low-endian CPU */
/* #define MSB_FIRST */        /* Compile for hi-endian CPU  */

                               /* LoopZ80() may return:      */
#define INT_RST00   0x00C7     /* RST 00h                    */
#define INT_RST08   0x00CF     /* RST 08h                    */
#define INT_RST10   0x00D7     /* RST 10h                    */
#define INT_RST18   0x00DF     /* RST 18h                    */
#define INT_RST20   0x00E7     /* RST 20h                    */
#define INT_RST28   0x00EF     /* RST 28h                    */
#define INT_RST30   0x00F7     /* RST 30h                    */
#define INT_RST38   0x00FF     /* RST 38h                    */
#define INT_IRQ     INT_RST38  /* Default IRQ opcode is FFh  */
#define INT_NMI     0xFFFD     /* Non-maskable interrupt     */
#define INT_NONE    0xFFFF     /* No interrupt required      */
#define INT_QUIT    0xFFFE     /* Exit the emulation         */

                               /* Bits in Z80 F register:    */
#define S_FLAG      0x80       /* 1: Result negative         */
#define Z_FLAG      0x40       /* 1: Result is zero          */
#define H_FLAG      0x10       /* 1: Halfcarry/Halfborrow    */
#define P_FLAG      0x04       /* 1: Result is even          */
#define V_FLAG      0x04       /* 1: Overflow occured        */
#define N_FLAG      0x02       /* 1: Subtraction occured     */
#define C_FLAG      0x01       /* 1: Carry/Borrow occured    */
#define Y_FLAG      0x20       // 5
#define X_FLAG      0x08       // 3

                               /* Bits in IFF flip-flops:    */
#define IFF_1       0x01       /* IFF1 flip-flop             */
#define IFF_IM1     0x02       /* 1: IM1 mode                */
#define IFF_IM2     0x04       /* 1: IM2 mode                */
#define IFF_2       0x08       /* IFF2 flip-flop             */
#define IFF_EI      0x20       /* 1: EI pending              */
#define IFF_HALT    0x80       /* 1: CPU HALTed              */

/** Simple Datatypes *****************************************/
/** NOTICE: sizeof(byte)=1 and sizeof(word)=2               **/
/*************************************************************/
#ifndef BYTE_TYPE_DEFINED
#define BYTE_TYPE_DEFINED
typedef unsigned char byte;
#endif
#ifndef WORD_TYPE_DEFINED
#define WORD_TYPE_DEFINED
typedef unsigned short word;
#endif
typedef signed char offset;

/** Structured Datatypes *************************************/
/** NOTICE: #define LSB_FIRST for machines where least      **/
/**         signifcant byte goes first.                     **/
/*************************************************************/
typedef union
{
#ifdef LSB_FIRST
  struct { byte l,h; } B;
#else
  struct { byte h,l; } B;
#endif
  word W;
} pair;

typedef struct Z80_state
{
    pair AF,BC,DE,HL,IX,IY,PC,SP;       /* Main registers      */
    pair AF1,BC1,DE1,HL1;               /* Shadow registers    */
    byte IFF,I;                         /* Interrupt registers */
    byte R;                             /* Refresh register    */

    int IPeriod, ICount; /* Set IPeriod to number of CPU cycles */
                         /* between calls to LoopZ80()          */
    int ITotal;
    int IBackup;        /* Private, don't touch                */
    word IRequest;      /* Set to address of pending IRQ       */
    byte IAutoReset;    /* Set to 1 to autom. reset IRequest   */
    byte TrapBadOps;    /* Set to 1 to warn of illegal opcodes */
    word Trap;          /* Set Trap to address to trace from   */
  
    /** RdZ80()/WrZ80() ******************************************/
    /** These functions are called when access to RAM occurs.   **/
    /** They allow to control memory access.                    **/
    /************************************ TO BE WRITTEN BY USER **/
    void (*write)(word Addr, byte Value);
    byte (*read)(word Addr);
    byte (*read_op)(word Addr);

    /** InZ80()/OutZ80() *****************************************/
    /** Z80 emulation calls these functions to read/write from  **/
    /** I/O ports. There can be 65536 I/O ports, but only first **/
    /** 256 are usually used.                                   **/
    /************************************ TO BE WRITTEN BY USER **/
    void (*io_write)(word Port, byte Value);
    byte (*io_read)(word Port);

    /** PatchZ80() ***********************************************/
    /** Z80 emulation calls this function when it encounters a  **/
    /** special patch command (ED FE) provided for user needs.  **/
    /** For example, it can be called to emulate BIOS calls,    **/
    /** such as disk and tape access. Replace it with an empty  **/
    /** macro for no patching.                                  **/
    /************************************ TO BE WRITTEN BY USER **/
    void (*patch)(void *R);

    /** JumpZ80() ************************************************/
    /** Z80 emulation calls this function when it executes a    **/
    /** JP, JR, CALL, RST, or RET. You can use JumpZ80() to     **/
    /** trap these opcodes and switch memory layout.            **/
    /************************************ TO BE WRITTEN BY USER **/
    void (*jump)(word PC);
} Z80;

/** ResetZ80() ***********************************************/
/** This function can be used to reset the registers before **/
/** starting execution with RunZ80(). It sets registers to  **/
/** their initial values.                                   **/
/*************************************************************/
void ResetZ80(register Z80 *R);

/** ExecZ80() ************************************************/
/** This function will execute given number of Z80 cycles.  **/
/** It will then return the number of cycles left, possibly **/
/** negative, and current register values in R.             **/
/*************************************************************/
// ExecZ80 return values
# define EXECZ80_OK 0
# define EXECZ80_UNKNOWN_OP -1
int ExecZ80(register Z80 *R,register int RunCycles);

/** IntZ80() *************************************************/
/** This function will generate interrupt of given vector.  **/
/*************************************************************/
void IntZ80(register Z80 *R,register word Vector);

#ifdef __cplusplus
}
#endif
#endif /* Z80_H */
