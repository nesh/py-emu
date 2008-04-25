from tables import *
from tools import as_signed

class Z80_8BitLoad(object):
    # ============
    # = LD r, r' =
    # ============
    def ld_a_a(self):
        pass
    
    def ld_a_b(self):
        self.A = self.B
    
    def ld_a_c(self):
        self.A = self.C
    
    def ld_a_d(self):
        self.A = self.D

    def ld_a_e(self):
        self.A = self.E

    def ld_a_h(self):
        self.A = self.H

    def ld_a_l(self):
        self.A = self.L

    def ld_b_a(self):
        self.B = self.A

    def ld_b_b(self):
        pass

    def ld_b_c(self):
        self.B = self.C

    def ld_b_d(self):
        self.B = self.D

    def ld_b_e(self):
        self.B = self.E

    def ld_b_h(self):
        self.B = self.H

    def ld_b_l(self):
        self.B = self.L

    def ld_c_a(self):
        self.C = self.A

    def ld_c_b(self):
        self.C = self.B

    def ld_c_c(self):
        pass

    def ld_c_d(self):
        self.C = self.D

    def ld_c_e(self):
        self.C = self.E

    def ld_c_h(self):
        self.C = self.H

    def ld_c_l(self):
        self.C = self.L

    def ld_d_a(self):
        self.D = self.A

    def ld_d_b(self):
        self.D = self.B

    def ld_d_c(self):
        self.D = self.C

    def ld_d_d(self):
        pass

    def ld_d_e(self):
        self.D = self.E

    def ld_d_h(self):
        self.D = self.H

    def ld_d_l(self):
        self.D = self.L

    def ld_e_a(self):
        self.E = self.A

    def ld_e_b(self):
        self.E = self.B

    def ld_e_c(self):
        self.E = self.C

    def ld_e_d(self):
        self.E = self.D

    def ld_e_e(self):
        pass

    def ld_e_h(self):
        self.E = self.H

    def ld_e_l(self):
        self.E = self.L

    def ld_h_a(self):
        self.H = self.A

    def ld_h_b(self):
        self.H = self.B

    def ld_h_c(self):
        self.H = self.C

    def ld_h_d(self):
        self.H = self.D

    def ld_h_e(self):
        self.H = self.E

    def ld_h_h(self):
        pass

    def ld_h_l(self):
        self.H = self.L

    def ld_l_a(self):
        self.L = self.A

    def ld_l_b(self):
        self.L = self.B

    def ld_l_c(self):
        self.L = self.C

    def ld_l_d(self):
        self.L = self.D

    def ld_l_e(self):
        self.L = self.E

    def ld_l_h(self):
        self.L = self.H

    def ld_l_l(self):
        pass
    
    # ===========
    # = LD r, n =
    # ===========
    def ld_a_n(self):
        self.A = self.read_op()
    
    def ld_b_n(self):
        self.B = self.read_op()

    def ld_c_n(self):
        self.C = self.read_op()

    def ld_d_n(self):
        self.D = self.read_op()

    def ld_e_n(self):
        self.E = self.read_op()

    def ld_h_n(self):
        self.H = self.read_op()

    def ld_l_n(self):
        self.L = self.read_op()

    # ==============
    # = LD r, (HL) =
    # ==============
    def ld_a_hl(self):
        self.A = self.read(self.HL)
    
    def ld_b_hl(self):
        self.B = self.read(self.HL)
    
    def ld_c_hl(self):
        self.C = self.read(self.HL)
    
    def ld_d_hl(self):
        self.D = self.read(self.HL)
    
    def ld_e_hl(self):
        self.E = self.read(self.HL)
    
    def ld_h_hl(self):
        self.H = self.read(self.HL)
    
    def ld_l_hl(self):
        self.L = self.read(self.HL)
    
    # ================
    # = LD r, (IX+d) =
    # ================
    def ld_a_ixd(self, reg):
        off = as_signed(self.read_op())
        self.A = self.read(getattr(self, reg) + off)

    def ld_b_ixd(self, reg):
        off = as_signed(self.read_op())
        self.B = self.read(getattr(self, reg) + off)

    def ld_c_ixd(self, reg):
        off = as_signed(self.read_op())
        self.C = self.read(getattr(self, reg) + off)

    def ld_d_ixd(self, reg):
        off = as_signed(self.read_op())
        self.D = self.read(getattr(self, reg) + off)

    def ld_e_ixd(self, reg):
        off = as_signed(self.read_op())
        self.E = self.read(getattr(self, reg) + off)

    def ld_h_ixd(self, reg):
        off = as_signed(self.read_op())
        self.H = self.read(getattr(self, reg) + off)

    def ld_l_ixd(self, reg):
        off = as_signed(self.read_op())
        self.L = self.read(getattr(self, reg) + off)

    # ==============
    # = LD (HL), r =
    # ==============
    def ld_hl_a(self):
        self.write(self.HL, self.A)
    
    def ld_hl_b(self):
        self.write(self.HL, self.B)

    def ld_hl_c(self):
        self.write(self.HL, self.C)

    def ld_hl_d(self):
        self.write(self.HL, self.D)

    def ld_hl_e(self):
        self.write(self.HL, self.E)

    def ld_hl_h(self):
        self.write(self.HL, self.H)

    def ld_hl_l(self):
        self.write(self.HL, self.L)

    # ===================
    # = LD (I(XY)+d), r =
    # ===================
    def ld_ixd_a(self, reg):
        off = as_signed(self.read_op())
        self.write(getattr(self, reg) + off, self.A)

    def ld_ixd_b(self, reg):
        off = as_signed(self.read_op())
        self.write(getattr(self, reg) + off, self.B)

    def ld_ixd_c(self, reg):
        off = as_signed(self.read_op())
        self.write(getattr(self, reg) + off, self.C)

    def ld_ixd_d(self, reg):
        off = as_signed(self.read_op())
        self.write(getattr(self, reg) + off, self.D)

    def ld_ixd_e(self, reg):
        off = as_signed(self.read_op())
        self.write(getattr(self, reg) + off, self.E)

    def ld_ixd_h(self, reg):
        off = as_signed(self.read_op())
        self.write(getattr(self, reg) + off, self.H)

    def ld_ixd_l(self, reg):
        off = as_signed(self.read_op())
        self.write(getattr(self, reg) + off, self.L)

    # ==============
    # = LD (HL), n =
    # ==============
    def ld_hl_n(self):
        self.write(self.HL, self.read_op())
    
    # ===================
    # = LD (I(XY)+d), n =
    # ===================
    def ld_ixd_n(self, reg):
        off = as_signed(self.read_op())
        self.write(getattr(self, reg) + off, self.read_op())
    
    # ==============
    # = LD A, (RP) =
    # ==============
    def ld_a_bc(self):
        self.A = self.read(self.BC)
    
    def ld_a_de(self):
        self.A = self.read(self.DE)

    def ld_a_nn(self):
        self.A = self.read(self.read_op16())
    
    # ==============
    # = LD (RP), A =
    # ==============
    def ld_bc_a(self):
        self.write(self.BC, self.A)
    
    def ld_de_a(self):
        self.write(self.DE, self.A)
    
    def ld_nn_a(self):
        self.write(self.read_op16(), self.A)
    
    # ========
    # = misc =
    # ========
    def ld_a_i(self):
        """R->AF.B.l=(R->AF.B.l&C_FLAG)|(R->IFF&IFF_2? P_FLAG:0)|ZSTable[R->AF.B.h];"""
        self.A = self.I
        self.F.c = False
        self.F.byte = (V_FLAG if self.IFF2 else 0) | ZS_TABLE[self.A]

    def ld_a_r(self):
        """R->AF.B.l=(R->AF.B.l&C_FLAG)|(R->IFF&IFF_2? P_FLAG:0)|ZSTable[R->AF.B.h];"""
        self.A = self.R
        self.F.c = False
        self.F.byte = (V_FLAG if self.IFF2 else 0) | ZS_TABLE[self.A]
        
    def ld_i_a(self):
        self.I = self.A
    
    def ld_r_a(self):
        self.R = self.A
    
    # ==================
    # = populate table =
    # ==================
    def _create_8b_load(self):
        # ============
        # = LD r, r' =
        # ============
        # A
        self._op[LD_A_A] = self.ld_a_a
        self._op[LD_A_B] = self.ld_a_b
        self._op[LD_A_C] = self.ld_a_c
        self._op[LD_A_D] = self.ld_a_d
        self._op[LD_A_E] = self.ld_a_e
        self._op[LD_A_H] = self.ld_a_h
        self._op[LD_A_L] = self.ld_a_l
        # B
        self._op[LD_B_A] = self.ld_b_a
        self._op[LD_B_B] = self.ld_b_b
        self._op[LD_B_C] = self.ld_b_c
        self._op[LD_B_D] = self.ld_b_d
        self._op[LD_B_E] = self.ld_b_e
        self._op[LD_B_H] = self.ld_b_h
        self._op[LD_B_L] = self.ld_b_l
        # C
        self._op[LD_C_A] = self.ld_c_a
        self._op[LD_C_B] = self.ld_c_b
        self._op[LD_C_C] = self.ld_c_c
        self._op[LD_C_D] = self.ld_c_d
        self._op[LD_C_E] = self.ld_c_e
        self._op[LD_C_H] = self.ld_c_h
        self._op[LD_C_L] = self.ld_c_l
        # D
        self._op[LD_D_A] = self.ld_d_a
        self._op[LD_D_B] = self.ld_d_b
        self._op[LD_D_C] = self.ld_d_c
        self._op[LD_D_D] = self.ld_d_d
        self._op[LD_D_E] = self.ld_d_e
        self._op[LD_D_H] = self.ld_d_h
        self._op[LD_D_L] = self.ld_d_l
        # E
        self._op[LD_E_A] = self.ld_e_a
        self._op[LD_E_B] = self.ld_e_b
        self._op[LD_E_C] = self.ld_e_c
        self._op[LD_E_D] = self.ld_e_d
        self._op[LD_E_E] = self.ld_e_e
        self._op[LD_E_H] = self.ld_e_h
        self._op[LD_E_L] = self.ld_e_l
        # H
        self._op[LD_H_A] = self.ld_h_a
        self._op[LD_H_B] = self.ld_h_b
        self._op[LD_H_C] = self.ld_h_c
        self._op[LD_H_D] = self.ld_h_d
        self._op[LD_H_E] = self.ld_h_e
        self._op[LD_H_H] = self.ld_h_h
        self._op[LD_H_L] = self.ld_h_l
        # L
        self._op[LD_L_A] = self.ld_l_a
        self._op[LD_L_B] = self.ld_l_b
        self._op[LD_L_C] = self.ld_l_c
        self._op[LD_L_D] = self.ld_l_d
        self._op[LD_L_E] = self.ld_l_e
        self._op[LD_L_H] = self.ld_l_h
        self._op[LD_L_L] = self.ld_l_l
        # ============
        # = LD r, n =
        # ============
        self._op[LD_A_BYTE] = self.ld_a_n
        self._op[LD_B_BYTE] = self.ld_b_n
        self._op[LD_C_BYTE] = self.ld_c_n
        self._op[LD_D_BYTE] = self.ld_d_n
        self._op[LD_E_BYTE] = self.ld_e_n
        self._op[LD_H_BYTE] = self.ld_h_n
        self._op[LD_L_BYTE] = self.ld_l_n
        # ============
        # = LD r, (HL) =
        # ============
        self._op[LD_A_xHL] = self.ld_a_hl
        self._op[LD_B_xHL] = self.ld_b_hl
        self._op[LD_C_xHL] = self.ld_c_hl
        self._op[LD_D_xHL] = self.ld_d_hl
        self._op[LD_E_xHL] = self.ld_e_hl
        self._op[LD_H_xHL] = self.ld_h_hl
        self._op[LD_L_xHL] = self.ld_l_hl
        # ===================
        # = LD r, (I(XY)+d) =
        # ===================
        self._xx_op[LD_A_xHL] = self.ld_a_ixd
        self._xx_op[LD_B_xHL] = self.ld_b_ixd
        self._xx_op[LD_C_xHL] = self.ld_c_ixd
        self._xx_op[LD_D_xHL] = self.ld_d_ixd
        self._xx_op[LD_E_xHL] = self.ld_e_ixd
        self._xx_op[LD_H_xHL] = self.ld_h_ixd
        self._xx_op[LD_L_xHL] = self.ld_l_ixd
        # ==============
        # = LD (HL), r =
        # ==============
        self._op[LD_xHL_A] = self.ld_hl_a
        self._op[LD_xHL_B] = self.ld_hl_b
        self._op[LD_xHL_C] = self.ld_hl_c
        self._op[LD_xHL_D] = self.ld_hl_d
        self._op[LD_xHL_E] = self.ld_hl_e
        self._op[LD_xHL_H] = self.ld_hl_h
        self._op[LD_xHL_L] = self.ld_hl_l
        # ===================
        # = LD (I(XY)+d), r =
        # ===================
        self._xx_op[LD_xHL_A] = self.ld_ixd_a
        self._xx_op[LD_xHL_B] = self.ld_ixd_b
        self._xx_op[LD_xHL_C] = self.ld_ixd_c
        self._xx_op[LD_xHL_D] = self.ld_ixd_d
        self._xx_op[LD_xHL_E] = self.ld_ixd_e
        self._xx_op[LD_xHL_H] = self.ld_ixd_h
        self._xx_op[LD_xHL_L] = self.ld_ixd_l
        # ==============
        # = LD (HL), n =
        # ==============
        self._op[LD_xHL_BYTE] = self.ld_hl_n
        # ===================
        # = LD (I(XY)+d), n =
        # ===================
        self._xx_op[LD_xHL_BYTE] = self.ld_ixd_n
        # ==============
        # = LD A, (RP) =
        # ==============
        self._op[LD_A_xBC] = self.ld_a_bc
        self._op[LD_A_xDE] = self.ld_a_de
        self._op[LD_A_xWORD] = self.ld_a_nn
        # ==============
        # = LD (RP), A =
        # ==============
        self._op[LD_xBC_A] = self.ld_bc_a
        self._op[LD_xDE_A] = self.ld_de_a
        self._op[LD_xWORD_A] = self.ld_nn_a
        # ========
        # = misc =
        # ========
        self._ed_op[LD_I_A] = self.ld_i_a
        self._ed_op[LD_R_A] = self.ld_r_a
        self._ed_op[LD_A_I] = self.ld_a_i
        self._ed_op[LD_A_R] = self.ld_a_r
        