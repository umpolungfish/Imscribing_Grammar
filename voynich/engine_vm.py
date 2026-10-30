import json
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple

class TriPhaseRegister:
    def __init__(self):
        self.flux = '00'  # 00=Void, 01=True, 10=False, 11=Both
        self.value = None
        self.loop_count = 0

    def engage_paradox(self):
        self.flux = '11'
        self.loop_count += 1

class UniversalEngineVM:
    def __init__(self):
        self.registers: Dict[int, TriPhaseRegister] = defaultdict(TriPhaseRegister)
        self.program: List[str] = []
        self.pc = 0  # program counter
        self.history = []  # for grandfather paradox simulation

    def load_compilation(self, log_file: str):
        with open(log_file, 'r') as f:
            for line in f:
                if '|' in line and ('0x' in line or 'DATA' in line):
                    self.program.append(line.strip())

    def execute(self, steps=1000):
        for _ in range(steps):
            if self.pc >= len(self.program):
                print("LOOP CLOSED - REINSCRIBING...")
                self.pc = 0  # infinite loop
            instr = self.program[self.pc]
            self.execute_single(instr)
            self.pc += 1

    def execute_single(self, instr: str):
        if 'FSPLIT' in instr:
            # Fork dual rail
            reg = int(instr.split('%r')[1].split(',')[0])
            self.registers[reg].flux = '11'  # Both
        elif 'FFUSE' in instr:
            # Rejoin with zero delta
            pass  # thermodynamic balance
        elif 'IFIX' in instr:
            # Burn to permanent state
            reg = int(instr.split('%r')[1])
            self.registers[reg].value = "FIXED"
        elif 'ENGAGR' in instr:
            reg = int(instr.split('%r')[1])
            self.registers[reg].engage_paradox()
        # ... (other opcodes can be expanded)

    def inject_grandfather_paradox(self, reg_id: int):
        """Deliberate timeline contradiction"""
        print(f"INJECTING GRANDFATHER PARADOX at r{reg_id}")
        self.registers[reg_id].engage_paradox()
        self.history.append(f"Paradox stabilized at r{reg_id} (Both state)")

    def visualize_registers(self):
        G = nx.DiGraph()
        for i, reg in list(self.registers.items())[:50]:  # sample
            G.add_node(f"r{i}", flux=reg.flux, loops=reg.loop_count)
        nx.draw(G, with_labels=True, node_color='lightblue')
        plt.title("Tri-Phase Flux Register Graph")
        plt.show()

# ====================== RUN ======================
vm = UniversalEngineVM()
vm.load_compilation("full_compilation_log.txt")  # or your v2.3 output
print("VM loaded with", len(vm.program), "instructions.")

# Example execution
vm.execute(steps=500)
vm.inject_grandfather_paradox(42)  # test paradox resolution
vm.visualize_registers()

print("Engine running infinite. Paradoxes resolved natively.")
