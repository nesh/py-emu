from base import *

class Z8016BitLoadTest(BaseZ80Test):
    """ 16bit load"""
    
    def test_ld_dd_nn(self):
        """Z80: LD rp, nn"""
        cpu = self.c
        for rp in range(0, 4):
            cpu.reset()
            cpu.write(0, (rp << 4) + 1)
            cpu.write16(1, 0x5000)
            cpu.run()
            
            self.eq_16b(getattr(cpu, RP[rp]), 0x5000)
            self.check_f(0x00)
            self.check_pc(self.c.PC, 0x0003)
            self.check_t(self.c.abs_T, 10)

    def test_ld_idx_nn(self):
        """Z80: LD I(XY), nn"""
        cpu = self.c
        for x in (0xDD, 0xFD):
            for rp in range(0, 4):
                rp = 'IX' if x == 0xDD else 'IY'
                cpu.reset()
                cpu.write(0, x)
                cpu.write(1, 0x21)
                cpu.write16(2, 0x5000)
                cpu.run()
            
                self.eq_16b(getattr(cpu, rp), 0x5000)
                self.check_f(0x00)
                self.check_pc(self.c.PC, 0x0004)
                self.check_t(self.c.abs_T, 14)

    def test_ld_hl_nn(self):
        """Z80: LD HL, (nn)"""
        cpu = self.c

        adr = 0x4545
        val = 0xA137
        
        cpu.reset()
        cpu.write16(adr, val)
        cpu.write(0, 0x2A)
        cpu.write16(1, adr)
        cpu.run()
        
        self.eq_16b(cpu.HL, val)
        self.check_f(0x00)
        self.check_pc(self.c.PC, 0x0003)
        self.check_t(self.c.abs_T, 16)

    def test_ld_dd_xnn(self):
        """Z80: LD rp, (nn)"""
        cpu = self.c
        adr = 0x2130
        val = 0x7865

        for rp in range(0, 4):
            cpu.reset()
            cpu.write(0, 0xED)
            cpu.write(1, (rp << 4) | 0x4B)
            cpu.write16(2, adr)
            cpu.run()
        
            self.eq_16b(getattr(cpu, RP[rp]), val)
            self.check_f(0x00)
            self.check_pc(self.c.PC, 0x0005)
            self.check_t(self.c.abs_T, 20)

    def test_ld_idx_nn(self):
        """Z80: LD HL, (nn)"""
        cpu = self.c

        adr = 0x6666
        val = 0xDA92
        
        for x in (0xDD, 0xFD):
            rp = 'IX' if x == 0xDD else 'IY'
            cpu.reset()
            cpu.write16(adr, val)
            cpu.write(0, x)
            cpu.write(1, 0x2A)
            cpu.write16(2, adr)
            cpu.run()
        
            self.eq_16b(getattr(cpu, rp), val)
            self.check_f(0x00)
            self.check_pc(self.c.PC, 0x0005)
            self.check_t(self.c.abs_T, 20)
