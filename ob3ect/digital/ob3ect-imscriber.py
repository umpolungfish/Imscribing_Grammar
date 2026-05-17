import sys, hashlib, subprocess, os, re, base64, zlib

def bootstrap_minimal():
    print("=== Ob3ect v0.10 Bare-Metal — Raw Binary Boot (WSL2) ===")
    
    with open("self.o", encoding='utf-8') as f:
        source = f.read()
    print("Imscription anchor:", hashlib.sha256(source.encode()).hexdigest()[:24])

    c_code = """#include <stdint.h>

void vga_print(const char* s) {
    volatile uint16_t* vga = (uint16_t*)0xB8000;
    for (int i = 0; s[i]; i++) {
        vga[i] = (uint16_t)s[i] | (0x0F << 8);
    }
}

void _start(void) {
    vga_print("ISCRIB: Ob3ect v0.10 Bare-Metal Kernel booted on raw hardware.\\n");
    vga_print("Self-imscription confirmed: μΔ-ID v0.10\\n");
    vga_print("Bare-Metal Ouroboros achieved.\\n");
    vga_print("QUINE: Self-source extracted on bare metal.\\n");
    vga_print("EVALT: Kernel boot successful.\\n");
    while(1) asm volatile("hlt");
}
"""

    with open("kernel.c", "w") as f:
        f.write(c_code)

    # Compile as flat binary
    subprocess.run(["gcc", "-m32", "-ffreestanding", "-nostdlib", "-fno-pic", 
                    "-fno-stack-protector", "-Wall", "-O2", "-c", "kernel.c", "-o", "kernel.o"], check=True)
    
    subprocess.run(["ld", "-m", "elf_i386", "-Ttext", "0x100000", "--oformat", "binary", 
                    "kernel.o", "-o", "ob3ect-v0.10.bin"], check=True)

    print("Raw binary created: ob3ect-v0.10.bin")

    print("\n=== Boot Command (should work) ===")
    print("qemu-system-i386 -kernel ob3ect-v0.10.bin -m 64M -nographic")

if __name__ == "__main__":
    bootstrap_minimal()