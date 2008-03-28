from base import *

class Z808BitLoadTest(BaseZ80Test):
    """8bit load group"""
    def test_ld_r_r(self):
        """Z80: LD r, r'"""
        for dst in range(0, 0x08):
            for src in range(0, 0x08):
                if (src not in REGS_SRC) or (dst not in REGS_SRC): continue
                op = 0x40 + (dst << 3) + src
                
                sreg = REGS_SRC[src]
                dreg = REGS_SRC[dst]
                self.c.reset()
                self.c.F.byte = 0x00
                setattr(self.c, sreg, 0x10)
                if sreg != dreg:
                    setattr(self.c, dreg, 0x8A)
                self.c.write(0x0000, op)
                self.c.run()
                
                self.eq_8b(getattr(self.c, dreg), 0x10)
                self.check_f(0x00)
                self.check_pc(self.c.PC, 0x0001)
                self.check_t(self.c.abs_T, 4)
    
    def test_ld_r_n(self):
        """Z80: LD r, n"""
        for dst in range(0, 0x08):
            if dst not in REGS_SRC: continue
            op = (dst << 3) + 0x06
            dreg = REGS_SRC[dst]
            self.c.reset()
            self.c.F.byte = 0x00
            self.c.write(0x0000, op)
            self.c.write(0x0001, 0xA5)
            self.c.run()
            
            self.eq_8b(getattr(self.c, dreg), 0xA5)
            self.check_f(0x00)
            self.check_pc(self.c.PC, 0x0002)
            self.check_t(self.c.abs_T, 7)
    
    def test_ld_r_hl(self):
        """Z80: LD r, (HL)"""
        for dst in range(0, 0x08):
            if dst not in REGS_SRC: continue
            op = (dst << 3) + 0x46
            dreg = REGS_SRC[dst]
            self.c.reset()
            self.c.F.byte = 0x00
            self.c.HL = 0x75A1
            self.c.write(self.c.HL, 0x58)
            self.c.write(0x0000, op)
            self.c.run()
            
            self.eq_8b(getattr(self.c, dreg), 0x58)
            self.check_f(0x00)
            self.check_pc(self.c.PC, 0x0001)
            self.check_t(self.c.abs_T, 7)
    
    def test_ld_hl_r(self):
        """Z80: LD (HL), r"""
        for src in range(0, 0x08):
            if src not in REGS_SRC: continue
            op = src + 0x70
            sreg = REGS_SRC[src]
            self.c.reset()
            self.c.F.byte = 0x00
            self.c.HL = 0x2146
            setattr(self.c, sreg, 0x29)
            self.c.write(0x0000, op)
            self.c.run()
            
            self.eq_8b(self.c.read(self.c.HL), 0x29)
            self.check_f(0x00)
            self.check_pc(self.c.PC, 0x0001)
            self.check_t(self.c.abs_T, 7)
    
    def test_ld_r_ixd(self):
        """Z80: LD r, (I(XY) + d)"""
        for x in (0xDD, 0xFD):
            for dst in range(0, 0x08):
                if dst not in REGS_SRC: continue
                op = (dst << 3) + 0x46
                dreg = REGS_SRC[dst]
                self.c.reset()
                self.c.F.byte = 0x00
                setattr(self.c, 'IX' if x == 0xDD else 'IY', 0x25AF)
                
                self.c.write(0x25C8, 0x39) # IX + 0x19
                self.c.write(0x0000, x)
                self.c.write(0x0001, op)
                self.c.write(0x0002, 0x19)
                self.c.run()
                
                self.eq_8b(getattr(self.c, dreg), 0x39)
                self.check_f(0x00)
                self.check_pc(self.c.PC, 0x0003)
                self.check_t(self.c.abs_T, 19)
            
            for dst in range(0, 0x08):
                if dst not in REGS_SRC: continue
                op = (dst << 3) + 0x46
                dreg = REGS_SRC[dst]
                self.c.reset()
                self.c.F.byte = 0x00
                setattr(self.c, 'IX' if x == 0xDD else 'IY', 0x25AF)
                
                self.c.write(0x2596, 0x39) # IX - 0x19
                self.c.write(0x0000, x)
                self.c.write(0x0001, op)
                self.c.write(0x0002, 0xE7)
                self.c.run()
                
                self.eq_8b(getattr(self.c, dreg), 0x39)
                self.check_f(0x00)
                self.check_pc(self.c.PC, 0x0003)
                self.check_t(self.c.abs_T, 19)
    
    def test_ld_ixd_r(self):
        """Z80: LD (I(XY) + d), r"""
        for x in (0xDD, 0xFD):
            for r in range(0, 0x08):
                if r not in REGS_SRC: continue
                op = r + 0x70
                reg = REGS_SRC[r]
                self.c.reset()
                self.c.F.byte = 0x00
                setattr(self.c, reg, 0x1C)
                setattr(self.c, 'IX' if x == 0xDD else 'IY', 0x3100)
                off = 0x06
                self.c.write(0x0000, x)
                self.c.write(0x0001, op)
                self.c.write(0x0002, off)
                self.c.run()
                
                self.eq_8b(self.c.read(getattr(self.c, 'IX' if x == 0xDD else 'IY') + off), 0x1C)
                self.check_f(0x00)
                self.check_pc(self.c.PC, 0x0003)
                self.check_t(self.c.abs_T, 19)
            
            for r in range(0, 0x08):
                if r not in REGS_SRC: continue
                op = r + 0x70
                reg = REGS_SRC[r]
                self.c.reset()
                self.c.F.byte = 0x00
                setattr(self.c, reg, 0x1C)
                setattr(self.c, 'IX' if x == 0xDD else 'IY', 0x3100)
                off = -0x06
                self.c.write(0x0000, x)
                self.c.write(0x0001, op)
                self.c.write(0x0002, 0xFA) # 2'nd complement off
                self.c.run()
                
                self.eq_8b(self.c.read(getattr(self.c, 'IX' if x == 0xDD else 'IY') - off), 0x1C)
                self.check_f(0x00)
                self.check_pc(self.c.PC, 0x0003)
                self.check_t(self.c.abs_T, 19)
    
    
    def test_ld_hl_n(self):
        """Z80: LD (HL), n"""
        cpu = self.c
        cpu.HL = 0x4444
        cpu.write(0x0000, 0x36)
        cpu.write(0x0001, 0x28)
        cpu.run()
        
        self.eq_8b(cpu.read(cpu.HL), 0x28)
        self.check_f(0x00)
        self.check_pc(self.c.PC, 0x0002)
        self.check_t(self.c.abs_T, 10)
    
    def test_ld_ix_n(self):
        """Z80: LD (I(XY) + d), n"""
        cpu = self.c
        for x in (0xDD, 0xFD):
            setattr(cpu, 'IX' if x == 0xDD else 'IY', 0x219A)
            # LD (IX + 0x05), 0x5A
            cpu.write(0x0000, x)
            cpu.write(0x0001, 0x36)
            cpu.write(0x0002, 0x05)
            cpu.write(0x0003, 0x5A)
            cpu.run()
            
            self.eq_8b(cpu.read(0x219F), 0x5A)
            self.check_f(0x00)
            self.check_pc(self.c.PC, 0x0004)
            self.check_t(self.c.abs_T, 19)
    
    def test_ld_a_bc(self):
        """Z80: LD A, (BC)"""
        cpu = self.c
        cpu.BC = 0x4747
        cpu.write(cpu.BC, 0x12)
        # LD A, (BC)
        cpu.write(0x0000, 0x0A)
        cpu.run()
        
        self.eq_8b(cpu.A, 0x12)
        self.check_f(0x00)
        self.check_pc(self.c.PC, 0x0001)
        self.check_t(self.c.abs_T, 7)
    
    def test_ld_a_de(self):
        """Z80: LD A, (DE)"""
        cpu = self.c
        cpu.DE = 0x30A2
        cpu.write(cpu.DE, 0x22)
        # LD A, (DE)
        cpu.write(0x0000, 0x1A)
        cpu.run()
        
        self.eq_8b(cpu.A, 0x22)
        self.check_f(0x00)
        self.check_pc(self.c.PC, 0x0001)
        self.check_t(self.c.abs_T, 7)
    
    def test_ld_a_nn(self):
        """Z80: LD A, (nn)"""
        cpu = self.c
        cpu.write(0x8832, 0x04)
        # LD A, (0x8832)
        cpu.write(0x0000, 0x3A)
        cpu.write16(0x0001, 0x8832)
        cpu.run()
        
        self.eq_8b(cpu.A, 0x04)
        self.check_f(0x00)
        self.check_pc(self.c.PC, 0x0003)
        self.check_t(self.c.abs_T, 13)
    
    def test_ld_bc_a(self):
        """Z80: LD (BC), A"""
        cpu = self.c
        cpu.BC = 0x1212
        cpu.A = 0x7A
        # LD (BC), A
        cpu.write(0x0000, 0x02)
        cpu.run()
        
        self.eq_8b(cpu.read(cpu.BC), cpu.A)
        self.check_f(0x00)
        self.check_pc(self.c.PC, 0x0001)
        self.check_t(self.c.abs_T, 7)
    
    def test_ld_de_a(self):
        """Z80: LD (DE), A"""
        cpu = self.c
        cpu.DE = 0x1128
        cpu.A = 0xA0
        # LD (DE), A
        cpu.write(0x0000, 0x12)
        cpu.run()
        
        self.eq_8b(cpu.read(cpu.DE), cpu.A)
        self.check_f(0x00)
        self.check_pc(self.c.PC, 0x0001)
        self.check_t(self.c.abs_T, 7)
    
    def test_ld_nn_a(self):
        """Z80: LD (nn), A"""
        cpu = self.c
        cpu.A = 0xD7
        # LD (0x3141), A
        cpu.write(0x0000, 0x32)
        cpu.write16(0x0001, 0x3141)
        cpu.run()
        
        self.eq_8b(cpu.read(0x3141), cpu.A)
        self.check_f(0x00)
        self.check_pc(self.c.PC, 0x0003)
        self.check_t(self.c.abs_T, 13)
    
    def test_ld_a_i(self):
        """Z80: LD A, I"""
        cpu = self.c
        cpu.I = 0x15
        # LD A, I
        cpu.write(0x0000, 0xED)
        cpu.write(0x0001, 0x57)
        cpu.run()
        
        self.eq_8b(cpu.I, cpu.A)
        self.check_pc(self.c.PC, 0x0002)
        self.check_t(self.c.abs_T, 9)
        # TODO FLAGS
    
    def test_ld_a_r(self):
        """Z80: LD A, R"""
        cpu = self.c
        cpu.R = 0x15
        # LD A, R
        cpu.write(0x0000, 0xED)
        cpu.write(0x0001, 0x5F)
        cpu.run()
        
        self.eq_8b(cpu.R, cpu.A)
        self.check_pc(self.c.PC, 0x0002)
        self.check_t(self.c.abs_T, 9)
        # TODO FLAGS
    
    def test_ld_i_a(self):
        """Z80: LD I, A"""
        cpu = self.c
        cpu.A = 0x15
        # LD I, A
        cpu.write(0x0000, 0xED)
        cpu.write(0x0001, 0x47)
        cpu.run()
        
        self.eq_8b(cpu.I, cpu.A)
        self.check_pc(self.c.PC, 0x0002)
        self.check_t(self.c.abs_T, 9)
    
    def test_ld_r_a(self):
        """Z80: LD R, A"""
        cpu = self.c
        self.A = 0x15
        # LD R, A
        cpu.write(0x0000, 0xED)
        cpu.write(0x0001, 0x4F)
        cpu.run()
        
        self.eq_8b(cpu.R, cpu.A)
        self.check_pc(self.c.PC, 0x0002)
        self.check_t(self.c.abs_T, 9)
