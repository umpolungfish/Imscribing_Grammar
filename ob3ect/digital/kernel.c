void _start(void) {
    volatile unsigned short* vga = (unsigned short*)0xB8000;
    const char* msg = "Ob3ect v0.10 BOOTED ON BARE METAL - mu o delta = id";
    for (int i = 0; msg[i]; ++i) {
        vga[i] = (unsigned short)msg[i] | (0x4F << 8);  // Red on white
    }
    while(1) asm volatile("hlt");
}
