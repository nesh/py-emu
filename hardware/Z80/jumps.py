class Z80JumpsMixin(object):
    # ======
    # = JR =
    # ======
    def _jr(self, cond, op):
        if not cond: return
        self.T -= 5
        self.abs_T += 5
        self.PC = (self.PC + self.mem.as_signed(op)) & 0xFFFF
    
    def jr(self, adr, op):
        self.PC = (self.PC + self.mem.as_signed(op)) & 0xFFFF
    
    def jr_nz(self, adr, op):
        self._jr(not self.F.z, op)
    def jr_z(self, adr, op):
        self._jr(self.F.z, op)
    
    def jr_nc(self, adr, op):
        self._jr(not self.F.c, op)
    def jr_c(self, adr, op):
        self._jr(self.F.c, op)
    
    # ======
    # = JP =
    # ======
    def _jp(self, adr, op):
        self.PC = op
    
    def _jp(self, cond, op):
        if not cond: return
        self.PC = op
    
    def jp_nz(self, adr, op):
        self._jp(not self.F.z, op)
    def jp_z(self, adr, op):
        self._jp(self.F.z, op)
    
    def jp_nc(self, adr, op):
        self._jp(not self.F.c, op)
    def jp_c(self, adr, op):
        self._jp(self.F.c, op)
    
    # ========
    # = CALL =
    # ========
    def _call(self, cond, op):
        if not cond: return
        self.T -= 7
        self.abs_T += 7
        self.push(self.PC)
        self.PC = op
    
    def call(self, adr, op):
        self.push(self.PC)
        self.PC = op
    
    # =======
    # = RST =
    # =======
    def _rst(self, op):
        self.push(self.PC)
        self.PC = op
    
    def rst00(self, adr, op):
        self._rst(0x0000)
    def rst08(self, adr, op):
        self._rst(0x0008)
    def rst10(self, adr, op):
        self._rst(0x0010)
    def rst18(self, adr, op):
        self._rst(0x0018)
    def rst20(self, adr, op):
        self._rst(0x0020)
    def rst28(self, adr, op):
        self._rst(0x0028)
    def rst30(self, adr, op):
        self._rst(0x0030)
    def rst38(self, adr, op):
        self._rst(0x0038)
    
    
    # ========
    # = RET  =
    # ========
    def _ret(self, cond):
        if not cond: return
        self.T -= 6
        self.abs_T += 6
        self.PC = self.pop()
    
    def ret(self, adr, op):
        self.PC = self.pop()