## Worked chains

Composition guidance for the closure cluster. The exact argument forms come from
`<cmd> help` in the running kernel, never from memory.

### Classify a pairing before spending anything on it

    ./run_serial_cmds.sh "nesting <map> <x>"

Reads three things in one shot: the first gap, the ratio q = r₂/r₁, and what the
nest actually did. Three outcomes:

    q = 0        the point IS the answer — one-shot, cost nothing
    q < 1        being drawn in — arrives on a finite budget
    q ≥ 1        gap held or growing — never arrives, at any budget

The two-step reading is the whole point. One gap of 1.00 and one of 1.73 look
different and behave identically; both sit at q = 1 and neither ever settles.
Magnitude tells you nothing about arrival.

### Close something the rule says cannot close

    ./run_serial_cmds.sh "ctc <action> <T|F|N|B>"

Possession is tested first, then the basin, then imposition. Read the price:

    width 1      a value held outright — nothing was manufactured
    width 2-3    closure bought by giving up precision
    width 4      the whole logic smeared — closure achieved, nothing learned

`ctc not T` is the case worth understanding: negation HAS fixed points at N and
B, but from T they sit behind a 2-cycle with no slope down to either. The old
three-way rule called that "never". It closes at price 1, and the report prints
the unreachable fixed points beside the answer so a made closure cannot pass for
a held one.

### Survey what already closes without being asked

    ./run_serial_cmds.sh "oneshots"

Ten constructions, each calling the kernel's own engine — the period finder calls
the real order-finding engine, the Belnap one the real negation, the factoring
one the same order engine as the first. That discipline is why they agree with
the rest of the kernel; a local reimplementation would drift.

### Measure an operator set, then check it reconstructs

    ./run_serial_cmds.sh "ovm <name>" "ovm cycle <name> <sx> <sy> <sz>"

The report gives eigenvalues, frame, overlap, equiangularity, positivity and
completeness. The cycle is μ∘δ = id in measurement clothing: measure a state,
reconstruct it, compare. Reconstruction returning the input is informational
completeness on that state — a fixed point of the measure-then-rebuild map.

`ovm belnap` gives the B = XZ fiducial, which is where this cluster meets the
rest: the fiducial is stationary under the symmetry it is nested in, which is why
period finding here is one-shot rather than iterative.

### Batch, always

    ./run_serial_cmds.sh "ovm sic-povm" "ovm frame sic-povm" "ovm duals sic-povm"

The QEMU boot dominates every short command. Three questions cost barely more
than one, and there is no timeout, so a long computation completes rather than
being cut off and misreported as a hang.

### After changing any of the four modules

    make image
    ./run_serial_cmds.sh "<the command you changed> help" "<the command>"

The runners boot whatever ELF is on disk. Reading the previous binary is the
usual reason a change looks like it did nothing.

### Reporting

Every closure gets its class and its price. "It closed" is half an answer:
one-shot, iterated at N steps, never, or manufactured at width W. A report that
does not say which of the four is not reporting a measurement.
