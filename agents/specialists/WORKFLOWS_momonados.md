## Worked chains

Composition guidance for the kernel. These are the shapes that recur; the
command surface itself is discovered from `menu.rs`, `repl.rs` and `help`, never
recited from memory.

### Answer "can the kernel do X?"

    command grep -n '"<word>"' mOMonadOS/src/repl.rs mOMonadOS/src/menu.rs
    → present in both:  run it, quote the output
    → repl.rs only:     it works and is undocumented — say so, and give the form
                        from the match arm
    → menu.rs only:     the menu promises what the kernel does not dispatch —
                        a defect, report it
    → neither:          it does not exist. Say where you looked. Do not invent
                        a plausible name.

### Survey the whole surface

    run_command: cd mOMonadOS && python3 check_menu_coverage.py
    → names every repl arm no menu entry reaches
    run_command: command grep -c 'MenuItem {' src/menu.rs
    → the documented surface, as a number that dates itself

Then batch a boot to sample the ones in question. One boot, many commands.

### Run several commands

    cd /home/mrnob0dy666/imsgct/mOMonadOS
    ./run_serial_cmds.sh "help" "ctc help" "ctc cycle T" "substrate"

The boot dominates; three commands cost barely more than one. There is no
timeout, so a long computation completes rather than being cut off and
misreported as a hang.

### After changing kernel source

    make image          rebuild — the runners boot whatever ELF is on disk
    ./run_serial_cmds.sh "<the command you changed>"
    python3 check_menu_coverage.py
    make ordinals       if you touched ordinals, tuples or the catalog

Skipping the rebuild is the single most common way to conclude a change did
nothing. The output you are reading is the previous binary.

### Diagnose "Unknown: <name>" for a command that help lists

    command grep -n -B3 '"<name>" =>' src/repl.rs     # look for #[cfg(feature)]
    command grep -n '<name>' Cargo.toml               # is the feature enabled?

A gate the build does not enable puts a command in the menu and out of the
binary at the same time. That is a wiring defect, not a missing capability.

### Wire a new command

Three points, all required:

    src/main.rs   mod <name>;
    src/repl.rs   "<name>" => { ... }          arm on the command word
    src/menu.rs   MenuItem { name, cmd, desc, example, submenu }

If it takes arguments: give it a `help` reachable as `<cmd> help`, a submenu
naming every form, and an example carrying real arguments rather than repeating
the command name. Then `make image`, run it, and re-run check_menu_coverage.py.

### Read a module before judging it

    file_read src/<module>.rs

The modules carry their reasoning in comments, including why a thing is done the
way it is and what a previous attempt got wrong. Read them before calling a
module wrong. Where comment and code disagree, that is the finding.

### Cross-check against Lean

    make ordinals

Passes as "all 44 values match Lean canonical". This is the bridge between the
kernel's ordinal tables and p4ramill. A kernel claim with a Lean counterpart is
stronger than one without; say which you have.
