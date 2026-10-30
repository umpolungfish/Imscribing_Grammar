; frob_loop.asm — Frobenius loop (from the paper)
;
; The fundamental infinite loop: three instructions, circular.
; Loop invariant: μ ∘ δ = id  →  B-state self-sustains forever.
; Paradox growth: P(n) = 4n exactly after n cycles.
;
; Load and run:
;   :load programs/frob_loop.asm
;   :run

.loop:
    ENGAGR  %r0             ; seed: force B on root
    FSPLIT  %r0  %r1  %r2   ; δ: co-multiply → two B-children
    FFUSE   %r1  %r2  %r0   ; μ: recombine → root stays B
    JMP     .loop
