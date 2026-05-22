; probe.asm — interactive belief probe
;
; Reads a belief value (N / T / F / B) from the user and routes it
; through a different Frobenius path depending on what was supplied.
; Shows how each of the four Belnap values interacts with FSPLIT/FFUSE/IFIX.
;
; Load and run:
;   :load programs/probe.asm
;   :run

.start:
    READ    %r0             ; ask user for a belief

    JB      %r0  .path_b   ; B → Frobenius round-trip (μ∘δ = id)
    JT      %r0  .path_t   ; T → IFIX stability (T absorbed by B via FFUSE)
    JN      %r0  .path_n   ; N → engagement (N promoted to B)
    JMP     .path_f         ; F → forced join with B

.path_b:
    ; B: paradox round-trip — FSPLIT then FFUSE = identity
    FSPLIT  %r0  %r1  %r2
    FFUSE   %r1  %r2  %r0
    EMIT    %r0             ; B: μ∘δ preserves paradox
    JMP     .cleanup

.path_t:
    ; T: IFIX holds T, but FFUSE with B absorbs it
    IFIX    %r0
    ENGAGR  %r1             ; reference B
    FFUSE   %r0  %r1  %r2   ; T ∨ B = B
    EMIT    %r0             ; T [FIXED]
    EMIT    %r2             ; B  (T was absorbed)
    JMP     .cleanup

.path_n:
    ; N: engagement promotes Neither to Both
    ENGAGR  %r0
    EMIT    %r0             ; B  (N → B via ENGAGR)
    JMP     .cleanup

.path_f:
    ; F: join with B to show F is absorbed
    ENGAGR  %r1             ; reference B
    FFUSE   %r0  %r1  %r2   ; F ∨ B = B
    EMIT    %r0             ; F  (original)
    EMIT    %r2             ; B  (F absorbed into B)

.cleanup:
    CLEAR   %r0
    CLEAR   %r1
    CLEAR   %r2
    JMP     .start
