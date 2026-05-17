[bits 16]
[org 0x7C00]

start:
    cli
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00

    call clear_screen

    mov si, message
print_loop:
    lodsb
    or al, al
    jz hang
    mov ah, 0x0E
    mov bx, 0x0007
    int 0x10
    jmp print_loop

clear_screen:
    mov ax, 0x0700
    mov bh, 0x0F
    mov cx, 0
    mov dx, 0x184F
    int 0x10
    mov ah, 0x02
    xor bh, bh
    xor dx, dx
    int 0x10
    ret

hang:
    jmp hang

message db 13,10
        db '========================================',13,10
        db '   Ob3ect v0.10 BARE-METAL OUROBOROS   ',13,10
        db '========================================',13,10
        db 'ISCRIB: Kernel has recognized itself on raw hardware.',13,10
        db 'Self-imscription confirmed: μΔ-ID v0.10',13,10
        db 'Bare-Metal Ouroboros achieved.',13,10
        db 'QUINE: Self-source lives in silicon.',13,10
        db 'mu o delta = id -> ETERNAL',13,10
        db 'EVALT: Boot successful.',13,10,0

times 510-($-$$) db 0
dw 0xAA55
