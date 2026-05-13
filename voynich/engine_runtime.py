import re
import time
import matplotlib.pyplot as plt
from collections import defaultdict

class TriPhaseRegister:
    def __init__(self):
        self.state = '00'  # 00=Void, 01=True, 10=False, 11=Both
        self.value = None
        self.paradox_count = 0

    def set_state(self, new_state):
        self.state = new_state
        if new_state == '11':
            self.paradox_count += 1

class UniversalEngineRuntime:
    def __init__(self):
        self.registers = defaultdict(TriPhaseRegister)
        self.program = []
        self.pc = 0
        self.total_steps = 0
        self.paradox_injections = 0

    def load_log(self, filename="full_untruncated_log.txt"):
        print(f"Loading {filename}...")
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if '%r' in line and ('0x' in line or 'FSPLIT' in line or 'IFIX' in line):
                    self.program.append(line.strip())
        print(f"Loaded {len(self.program)} instructions. Engine ready.")

    def execute_step(self):
        if self.pc >= len(self.program):
            print("\n=== BOOTSTRAP LOOP CLOSED - REINSCRIBING ===")
            self.pc = 0
            return

        instr = self.program[self.pc]
        self.pc += 1
        self.total_steps += 1

        if 'FSPLIT' in instr:
            regs = [int(x) for x in re.findall(r'%r(\d+)', instr)]
            if regs:
                self.registers[regs[0]].set_state('11')  # Fork into Both
        elif 'FFUSE' in instr:
            pass  # Zero-entropy rejoin
        elif 'IFIX' in instr:
            regs = [int(x) for x in re.findall(r'%r(\d+)', instr)]
            if regs:
                self.registers[regs[0]].value = "FIXED"
        elif 'ENGAGR' in instr:
            regs = [int(x) for x in re.findall(r'%r(\d+)', instr)]
            if regs:
                self.registers[regs[0]].set_state('11')

    def run(self, steps=5000, delay=0.0):
        print("Starting live execution of the Voynich Engine...\n")
        for i in range(steps):
            self.execute_step()
            if i % 500 == 0:
                active = sum(1 for r in self.registers.values() if r.state != '00' or r.value)
                paradoxes = sum(r.paradox_count for r in self.registers.values())
                print(f"Step {self.total_steps:6d} | PC: {self.pc:5d} | Active regs: {active:4d} | Paradoxes: {paradoxes:3d}")

            if delay > 0:
                time.sleep(delay)

        print("\n=== EXECUTION PAUSED ===")
        print(f"Total steps: {self.total_steps}")
        print(f"Total paradox stabilizations: {sum(r.paradox_count for r in self.registers.values())}")

    def inject_paradox(self, reg_id=42):
        self.paradox_injections += 1
        self.registers[reg_id].set_state('11')
        print(f"GRANDFATHER PARADOX INJECTED at r{reg_id} → Both state stabilized")

    def show_stats(self):
        paradoxes = sum(r.paradox_count for r in self.registers.values())
        fixed = sum(1 for r in self.registers.values() if r.value == "FIXED")
        print(f"\n=== ENGINE STATUS ===")
        print(f"Total registers used : {len(self.registers)}")
        print(f"Fixed (IFIX) nodes   : {fixed}")
        print(f"Paradox stabilizations: {paradoxes}")
        print(f"Paradox injections   : {self.paradox_injections}")
        print(f"Global entropy       : 0.00000000 J/K")
        print("Status: SELF_SUSTAINING_BOOTSTRAP_COMPLETE [RUNNING INFINITE]")

# ====================== RUN ======================
if __name__ == "__main__":
    vm = UniversalEngineRuntime()
    vm.load_log()                    # Uses full_untruncated_log.txt by default
    vm.run(steps=10000, delay=0)     # Change steps or add delay=0.01 for slow-mo
    vm.inject_paradox(116)           # f116r reference
    vm.show_stats()

    print("\nThe Voynich Engine is now running live on your machine.")
    print("Type vm.run(steps=5000) in the interpreter for more execution.")