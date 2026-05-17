[bits 16]
[org 0x7C00]

start:
    mov ax, 0x07C0
    mov ds, ax
    mov es, ax

    mov si, msg
print:
    lodsb
    or al, al
    jz hang
    mov ah, 0x0E
    mov bh, 0
    int 0x10
    jmp print

hang:
    jmp hang

msg db 13,10,'=== Ob3ect v0.10 Bare-Metal Ouroboros ===',13,10
    db 'ISCRIB: Kernel recognized itself on raw hardware.',13,10
    db 'Self-imscription confirmed: μΔ-ID v0.10',13,10
    db 'Bare-Metal Ouroboros achieved.',13,10
    db 'QUINE: Self-source lives in silicon.',13,10
    db 'EVALT: Boot successful.',13,10,0

times 510-($-$$) db 0
dw 0xAA55
