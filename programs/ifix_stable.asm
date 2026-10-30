; ifix_stable.asm — IFIX stability demonstration (Theorem 3, Case B)
;
; Shows that IFIX-T cannot collapse the loop via FFUSE.
; Key: T ∨ B = B  (B is top of the information order)
;
; At every cycle end:
;   r0 = B  (via T∨B = B in FFUSE)
;   r1 = B  (from FSPLIT, not subsequently IFIX'd)
;   r2 = T  [FIXED]  (IFIX fires last on r2)
;
; Load and run:
;   :load programs/ifix_stable.asm
;   :run 20

.loop:
    ENGAGR  %r0             ; seed B on root
    FSPLIT  %r0  %r1  %r2   ; δ: all three → B
    IFIX    %r2             ; r2 → T  (Case B: enters FFUSE at T)
    FFUSE   %r1  %r2  %r0   ; μ: B ∨ T = B  →  r0 stays B
    EMIT    %r0             ; always B
    EMIT    %r2             ; always T [FIXED]
    JMP     .loop
