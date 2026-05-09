"""
Append final 2 navigators: langlands_program and representation_theory
"""

CODE_TO_APPEND_3 = '''

# =============================================================================
# Langlands Program Navigator
# =============================================================================

_LANGLANDS_GRAMMAR = (
    "D_omega  T_openo  R_downstep  P_doublebarpipe  F_hardsign  K_schwa  "
    "G_revapostrophe  Gamma_broad  Phi_ctyogh  H_invscripta  n:m  Omega_dzlig"
)


@nav_group.group("langlands_program")
def langlands_program_group():
    """Langlands program navigator — Galois/automorphic correspondence, L-functions.

    \b
    Structural type:
      D_omega T_openo R_downstep P_doublebarpipe F_hardsign K_schwa
      G_revapostrophe Gamma_broad Phi_ctyogh H_invscripta n:m Omega_dzlig

    \b
    Key structural facts:
      D_omega / T_openo → imscriptive: Galois reps ↔ automorphic forms
      R_downstep        → adjoint functoriality: base change, lift, descent
      Gamma_broad     → broad correspondence: global-to-global
      Phi_ctyogh           → self-modeling: Langlands duality
      H_invscripta           → eternal: infinite descent, infinite extensions

    \b
    Examples:
      imscribe nav langlands_program describe
      imscribe nav langlands_program probe
      imscribe nav langlands_program l_function
    """


@langlands_program_group.command("describe")
def langlands_program_describe():
    """Grammar derivation and automorphic-Galois bridge."""
    console.print()
    console.print(Panel(
        "[bold cyan]Langlands Program Navigator[/bold cyan]\\n\\n"
        f"[bold]Tuple:[/bold]  {_LANGLANDS_GRAMMAR}\\n\\n"
        "[bold]Tier:[/bold]  O_∞  (Galois↔automorphic bridge)\\n\\n"
        "[bold]Architecture mandates:[/bold]\\n"
        "  D_omega / T_openo → imscriptive: all number fields, groups, representations\\n"
        "  R_downstep        → adjoint functoriality: base change, lift, descent\\n"
        "  P_doublebarpipe        → Frobenius: uncertainty between global/local\\n"
        "  F_hardsign          → preserves L-function identities, functional equations\\n"
        "  K_schwa          → slow exploration through moduli of automorphic reps\\n"
        "  G_revapostrophe         → arbitrary number fields, reductive groups\\n"
        "  Gamma_broad     → broad correspondence: not sequential, global-to-global\\n"
        "  Phi_ctyogh           → self-modeling: Langlands duality as self-duality of L-group\\n"
        "  H_invscripta           → eternal: infinite descent, infinite extensions\\n"
        "  Omega_dzlig         → integer winding: motivic weight, conductor, L-function order\\n\\n"
        "[bold]Key methods:[/bold]\\n"
        "  find_galois_match                match Galois rep with automorphic form\\n"
        "  find_automorphic_match           match automorphic form with Galois rep\\n"
        "  compute_l_function               L(s, π) values for automorphic rep\\n"
        "  verify_functoriality             check functorial lift between groups\\n"
        "  compute_base_change              base change to larger field\\n"
        "  compute_local_factors            local L-factors at primes\\n"
        "  verify_tamagawa_number           Tamagawa number = 1\\n"
        "  find_endoscopic_transfer         endoscopic transfer between groups",
        title="Langlands Program Navigator", expand=False,
    ))
    console.print()


@langlands_program_group.command("probe")
def langlands_program_probe():
    """Run full Langlands program analysis (invokes langlands_program_navigator.py)."""
    cmd = ["uv", "run", str(_PROJECT_ROOT / "langlands_program_navigator.py")]
    console.print(f"\\n  [dim]Running:[/dim] {' '.join(cmd)}\\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@langlands_program_group.command("l_function")
@click.argument("automorphic_rep")
@click.argument("s_value")
def langlands_l_function(automorphic_rep: str, s_value: float):
    """Compute L-function value for an automorphic representation.

    \b
    Example:
      imscribe nav langlands_program l_function "GL2_newform" 1.5
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "langlands_program_navigator.py"),
           "l_function", automorphic_rep, str(s_value)]
    console.print(f"\\n  [dim]Running:[/dim] {' '.join(cmd)}\\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


# =============================================================================
# Representation Theory Navigator
# =============================================================================

_REPTHEORY_GRAMMAR = (
    "D_omega  T_commatailz  R_ctz  P_doublebarpipe  F_hardsign  K_schwa  "
    "G_revapostrophe  Gamma_seq  Phi_ctyogh  H_turntwo  n:m  Omega_dzlig"
)


@nav_group.group("representation_theory")
def representation_theory_group():
    """Representation theory navigator — characters, tensor decompositions, Lie theory.

    \b
    Structural type:
      D_omega T_commatailz R_ctz P_doublebarpipe F_hardsign K_schwa
      G_revapostrophe Gamma_seq Phi_ctyogh H_turntwo n:m Omega_dzlig

    \b
    Key structural facts:
      D_omega / T_commatailz → imscriptive: all groups, algebras, representations
      R_ctz                 → categorical: induction↔restriction, tensor product
      Phi_ctyogh                 → self-modeling: group algebra = representation category
      H_turntwo                    → two-step: tensor with dual, Clebsch-Gordan
      Omega_dzlig               → integer winding: dimension, weight lattice index

    \b
    Examples:
      imscribe nav representation_theory describe
      imscribe nav representation_theory probe
      imscribe nav representation_theory character
    """


@representation_theory_group.command("describe")
def representation_theory_describe():
    """Grammar derivation and character table architecture."""
    console.print()
    console.print(Panel(
        "[bold cyan]Representation Theory Navigator[/bold cyan]\\n\\n"
        f"[bold]Tuple:[/bold]  {_REPTHEORY_GRAMMAR}\\n\\n"
        "[bold]Tier:[/bold]  O_∞  (character table → representation category)\\n\\n"
        "[bold]Architecture mandates:[/bold]\\n"
        "  D_omega / T_commatailz → imscriptive: all groups, algebras, representations\\n"
        "  R_ctz               → categorical relations: functors, induction, restriction\\n"
        "  P_doublebarpipe            → Frobenius: uncertainty in positive characteristic\\n"
        "  F_hardsign              → preserves character orthogonality, Schur orthogonality\\n"
        "  K_schwa              → slow traversal through moduli of representations\\n"
        "  G_revapostrophe             → arbitrary groups: finite, Lie, algebraic, quantum\\n"
        "  Gamma_seq           → sequential: weight lattice, tensor decomposition\\n"
        "  Phi_ctyogh               → self-modeling: group algebra = representation category\\n"
        "  H_turntwo                  → two-step: representation ⊗ its dual, Clebsch-Gordan\\n"
        "  Omega_dzlig             → integer winding: dimension, weight lattice index\\n\\n"
        "[bold]Key methods:[/bold]\\n"
        "  compute_character            χ(g) = trace(ρ(g)) for group element g\\n"
        "  decompose_tensor             decompose R_A ⊗ R_B into irreducibles\\n"
        "  induce_character             induce character from subgroup to group\\n"
        "  restrict_character           restrict character from group to subgroup\\n"
        "  compute_dimensions           dimension formula for reps\\n"
        "  find_irreducibles            list all irreducible representations\\n"
        "  verify_shur_orthogonality    check character orthogonality relations\\n"
        "  compute_clebsch_gordan       CG coefficients for tensor product\\n"
        "  match_representations        match reps across different realizations",
        title="Representation Theory Navigator", expand=False,
    ))
    console.print()


@representation_theory_group.command("probe")
def representation_theory_probe():
    """Run full representation theory analysis (invokes representation_theory_navigator.py)."""
    cmd = ["uv", "run", str(_PROJECT_ROOT / "representation_theory_navigator.py")]
    console.print(f"\\n  [dim]Running:[/dim] {' '.join(cmd)}\\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@representation_theory_group.command("character")
@click.argument("group")
@click.argument("representation")
@click.argument("element")
def representation_theory_character(group: str, representation: str, element: str):
    """Compute character table entry χ(g).

    \b
    Example:
      imscribe nav representation_theory character "S3" "standard" "(12)"
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "representation_theory_navigator.py"),
           "character", group, representation, element]
    console.print(f"\\n  [dim]Running:[/dim] {' '.join(cmd)}\\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


@representation_theory_group.command("tensor_decompose")
@click.argument("group")
@click.argument("rep_a")
@click.argument("rep_b")
def representation_theory_tensor(group: str, rep_a: str, rep_b: str):
    """Decompose tensor product of two representations.

    \b
    Example:
      imscribe nav representation_theory tensor_decompose "SU3" "fundamental" "fundamental"
    """
    cmd = ["uv", "run", str(_PROJECT_ROOT / "representation_theory_navigator.py"),
           "tensor_decompose", group, rep_a, rep_b]
    console.print(f"\\n  [dim]Running:[/dim] {' '.join(cmd)}\\n")
    subprocess.run(cmd, cwd=str(_PROJECT_ROOT))


# End of additions
'''

with open('/home/mrnob0dy666/imscrbgrmrP/imscrbgrmr/navigator_commands.py', 'a') as f:
    f.write(CODE_TO_APPEND_3)
print("Langlands and representation theory navigators added - ALL 6 NAVIGATORS COMPLETE")
