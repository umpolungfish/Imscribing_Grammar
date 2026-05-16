/-
  Manuscript_ZFCt.lean  —  ZFCt formalization of three undeciphered writing systems
  Generated from manuscript_zfct.json  (Voynich 227, Rohonc 33, Linear A 53)
-/
import ImscribingGrammar.Primitives.Imscription
open ImscribingGrammar.Primitives
set_option pp.all false
namespace Manuscript_ZFCt

namespace Voynich

  /-- 83 entries (e.g. f100v, f101v), tier .O_2 -/
  def type1 : Imscription :=
    { dim := Dimensionality.D_omega, top := Topology.T_openo, rel := Relational.R_lyoghlig, pol := Polarity.P_aolig, fid := Fidelity.F_beltl, kin := KineticChar.K_teshlig, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_invscripta, stoi := Stoichiometry.S_doublebaresh, prot := Protection.Omega_dzlig }

  def type1_zfct : String :=
    "LCard a ∧ holo x a  ∧\n    ⊙bound a f ∧ Refl a f ∧ holo x a  ∧\n    lr⇔ x y ∧ Θ x y ∧ ¬ Θ y x  ∧\n    ∃ y( y ∈ x ∧ ¬ y = x)  ∧\n    cls x  ∧\n    fixpt f  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    ∧  ∧\n    fixpt f  ∧\n    wind f x ∧ ¬ wind f σ x  ∧\n    bij f x x  ∧\n    ℤwind f x ∧ wind f x"

  theorem type1_tier : imscriptionTier type1 = .O_2 := by
    native_decide

  /-- 74 entries (e.g. f100r, f101r), tier .O_2 -/
  def type2_sym_F : Imscription :=
    { dim := Dimensionality.D_omega, top := Topology.T_openo, rel := Relational.R_lyoghlig, pol := Polarity.P_pipevar, fid := Fidelity.F_beltl, kin := KineticChar.K_teshlig, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_invscripta, stoi := Stoichiometry.S_doublebaresh, prot := Protection.Omega_dzlig }

  def type2_sym_F_zfct : String :=
    "LCard a ∧ holo x a  ∧\n    ⊙bound a f ∧ Refl a f ∧ holo x a  ∧\n    lr⇔ x y ∧ Θ x y ∧ ¬ Θ y x  ∧\n    ℤ₂ f ∧ ∃ f( bij f x x ∧ ∀ y( f( f y) = y))  ∧\n    cls x  ∧\n    fixpt f  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    ∧  ∧\n    fixpt f  ∧\n    wind f x ∧ ¬ wind f σ x  ∧\n    bij f x x  ∧\n    ℤwind f x ∧ wind f x"

  theorem type2_sym_F_tier : imscriptionTier type2_sym_F = .O_2 := by
    native_decide

  /-- 19 entries (e.g. f102r1, f116r), tier .O_2 -/
  def type3_sym_all : Imscription :=
    { dim := Dimensionality.D_omega, top := Topology.T_openo, rel := Relational.R_lyoghlig, pol := Polarity.P_subdoublearrow, fid := Fidelity.F_beltl, kin := KineticChar.K_teshlig, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_invscripta, stoi := Stoichiometry.S_doublebaresh, prot := Protection.Omega_dzlig }

  def type3_sym_all_zfct : String :=
    "LCard a ∧ holo x a  ∧\n    ⊙bound a f ∧ Refl a f ∧ holo x a  ∧\n    lr⇔ x y ∧ Θ x y ∧ ¬ Θ y x  ∧\n    ∀ f( bij f x x → ∀ y( y ∈ x ↔ f y ∈ x))  ∧\n    cls x  ∧\n    fixpt f  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    ∧  ∧\n    fixpt f  ∧\n    wind f x ∧ ¬ wind f σ x  ∧\n    bij f x x  ∧\n    ℤwind f x ∧ wind f x"

  theorem type3_sym_all_tier : imscriptionTier type3_sym_all = .O_2 := by
    native_decide

  /-- 18 entries (e.g. f11r, f11v), tier .O_2 -/
  def type4_sym_F_broad : Imscription :=
    { dim := Dimensionality.D_omega, top := Topology.T_openo, rel := Relational.R_lyoghlig, pol := Polarity.P_pipevar, fid := Fidelity.F_beltl, kin := KineticChar.K_teshlig, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_broad, crit := Criticality.Phi_ctyogh, chir := Chirality.H_invscripta, stoi := Stoichiometry.S_doublebaresh, prot := Protection.Omega_dzlig }

  def type4_sym_F_broad_zfct : String :=
    "LCard a ∧ holo x a  ∧\n    ⊙bound a f ∧ Refl a f ∧ holo x a  ∧\n    lr⇔ x y ∧ Θ x y ∧ ¬ Θ y x  ∧\n    ℤ₂ f ∧ ∃ f( bij f x x ∧ ∀ y( f( f y) = y))  ∧\n    cls x  ∧\n    fixpt f  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    ∀ y( f y)  ∧\n    fixpt f  ∧\n    wind f x ∧ ¬ wind f σ x  ∧\n    bij f x x  ∧\n    ℤwind f x ∧ wind f x"

  theorem type4_sym_F_broad_tier : imscriptionTier type4_sym_F_broad = .O_2 := by
    native_decide

  /-- 17 entries (e.g. f13r, f16v), tier .O_2 -/
  def type5_broad : Imscription :=
    { dim := Dimensionality.D_omega, top := Topology.T_openo, rel := Relational.R_lyoghlig, pol := Polarity.P_aolig, fid := Fidelity.F_beltl, kin := KineticChar.K_teshlig, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_broad, crit := Criticality.Phi_ctyogh, chir := Chirality.H_invscripta, stoi := Stoichiometry.S_doublebaresh, prot := Protection.Omega_dzlig }

  def type5_broad_zfct : String :=
    "LCard a ∧ holo x a  ∧\n    ⊙bound a f ∧ Refl a f ∧ holo x a  ∧\n    lr⇔ x y ∧ Θ x y ∧ ¬ Θ y x  ∧\n    ∃ y( y ∈ x ∧ ¬ y = x)  ∧\n    cls x  ∧\n    fixpt f  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    ∀ y( f y)  ∧\n    fixpt f  ∧\n    wind f x ∧ ¬ wind f σ x  ∧\n    bij f x x  ∧\n    ℤwind f x ∧ wind f x"

  theorem type5_broad_tier : imscriptionTier type5_broad = .O_2 := by
    native_decide

  /-- 6 entries (e.g. f103r, f103v), tier .O_inf -/
  def type6_sym_cl_cross : Imscription :=
    { dim := Dimensionality.D_omega, top := Topology.T_bullseye, rel := Relational.R_lyoghlig, pol := Polarity.P_doublebarpipe, fid := Fidelity.F_beltl, kin := KineticChar.K_teshlig, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_invscripta, stoi := Stoichiometry.S_doublebaresh, prot := Protection.Omega_dzlig }

  def type6_sym_cl_cross_zfct : String :=
    "LCard a ∧ holo x a  ∧\n    ∀ z( z ∈ x ↔ repl f z)  ∧\n    lr⇔ x y ∧ Θ x y ∧ ¬ Θ y x  ∧\n    Frob f g  ∧\n    cls x  ∧\n    fixpt f  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    ∧  ∧\n    fixpt f  ∧\n    wind f x ∧ ¬ wind f σ x  ∧\n    bij f x x  ∧\n    ℤwind f x ∧ wind f x"

  theorem type6_sym_cl_cross_tier : imscriptionTier type6_sym_cl_cross = .O_inf := by
    native_decide

  /-- 4 entries (e.g. f66r, f84r), tier .O_2 -/
  def type7_sym_all_cross : Imscription :=
    { dim := Dimensionality.D_omega, top := Topology.T_bullseye, rel := Relational.R_lyoghlig, pol := Polarity.P_subdoublearrow, fid := Fidelity.F_beltl, kin := KineticChar.K_teshlig, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_invscripta, stoi := Stoichiometry.S_doublebaresh, prot := Protection.Omega_dzlig }

  def type7_sym_all_cross_zfct : String :=
    "LCard a ∧ holo x a  ∧\n    ∀ z( z ∈ x ↔ repl f z)  ∧\n    lr⇔ x y ∧ Θ x y ∧ ¬ Θ y x  ∧\n    ∀ f( bij f x x → ∀ y( y ∈ x ↔ f y ∈ x))  ∧\n    cls x  ∧\n    fixpt f  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    ∧  ∧\n    fixpt f  ∧\n    wind f x ∧ ¬ wind f σ x  ∧\n    bij f x x  ∧\n    ℤwind f x ∧ wind f x"

  theorem type7_sym_all_cross_tier : imscriptionTier type7_sym_all_cross = .O_2 := by
    native_decide

  /-- 3 entries (e.g. f75r, f79v), tier .O_inf -/
  def type8_sym_cl : Imscription :=
    { dim := Dimensionality.D_omega, top := Topology.T_openo, rel := Relational.R_lyoghlig, pol := Polarity.P_doublebarpipe, fid := Fidelity.F_beltl, kin := KineticChar.K_teshlig, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_invscripta, stoi := Stoichiometry.S_doublebaresh, prot := Protection.Omega_dzlig }

  def type8_sym_cl_zfct : String :=
    "LCard a ∧ holo x a  ∧\n    ⊙bound a f ∧ Refl a f ∧ holo x a  ∧\n    lr⇔ x y ∧ Θ x y ∧ ¬ Θ y x  ∧\n    Frob f g  ∧\n    cls x  ∧\n    fixpt f  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    ∧  ∧\n    fixpt f  ∧\n    wind f x ∧ ¬ wind f σ x  ∧\n    bij f x x  ∧\n    ℤwind f x ∧ wind f x"

  theorem type8_sym_cl_tier : imscriptionTier type8_sym_cl = .O_inf := by
    native_decide

  /-- 1 entries (e.g. f116v), tier .O_2 -/
  def type9_broad_memless : Imscription :=
    { dim := Dimensionality.D_omega, top := Topology.T_openo, rel := Relational.R_lyoghlig, pol := Polarity.P_aolig, fid := Fidelity.F_beltl, kin := KineticChar.K_teshlig, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_broad, crit := Criticality.Phi_ctyogh, chir := Chirality.H_closeomega, stoi := Stoichiometry.S_doublebaresh, prot := Protection.Omega_dzlig }

  def type9_broad_memless_zfct : String :=
    "LCard a ∧ holo x a  ∧\n    ⊙bound a f ∧ Refl a f ∧ holo x a  ∧\n    lr⇔ x y ∧ Θ x y ∧ ¬ Θ y x  ∧\n    ∃ y( y ∈ x ∧ ¬ y = x)  ∧\n    cls x  ∧\n    fixpt f  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    ∀ y( f y)  ∧\n    fixpt f  ∧\n    x = x  ∧\n    bij f x x  ∧\n    ℤwind f x ∧ wind f x"

  theorem type9_broad_memless_tier : imscriptionTier type9_broad_memless = .O_2 := by
    native_decide

  /-- 1 entries (e.g. f46r), tier .O_inf -/
  def type10_sym_cl_broad_cross : Imscription :=
    { dim := Dimensionality.D_omega, top := Topology.T_bullseye, rel := Relational.R_lyoghlig, pol := Polarity.P_doublebarpipe, fid := Fidelity.F_beltl, kin := KineticChar.K_teshlig, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_broad, crit := Criticality.Phi_ctyogh, chir := Chirality.H_invscripta, stoi := Stoichiometry.S_doublebaresh, prot := Protection.Omega_dzlig }

  def type10_sym_cl_broad_cross_zfct : String :=
    "LCard a ∧ holo x a  ∧\n    ∀ z( z ∈ x ↔ repl f z)  ∧\n    lr⇔ x y ∧ Θ x y ∧ ¬ Θ y x  ∧\n    Frob f g  ∧\n    cls x  ∧\n    fixpt f  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    ∀ y( f y)  ∧\n    fixpt f  ∧\n    wind f x ∧ ¬ wind f σ x  ∧\n    bij f x x  ∧\n    ℤwind f x ∧ wind f x"

  theorem type10_sym_cl_broad_cross_tier : imscriptionTier type10_sym_cl_broad_cross = .O_inf := by
    native_decide

  /-- 1 entries (e.g. f65r), tier .O_2 -/
  def type11_memless : Imscription :=
    { dim := Dimensionality.D_omega, top := Topology.T_openo, rel := Relational.R_lyoghlig, pol := Polarity.P_aolig, fid := Fidelity.F_beltl, kin := KineticChar.K_teshlig, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_closeomega, stoi := Stoichiometry.S_doublebaresh, prot := Protection.Omega_dzlig }

  def type11_memless_zfct : String :=
    "LCard a ∧ holo x a  ∧\n    ⊙bound a f ∧ Refl a f ∧ holo x a  ∧\n    lr⇔ x y ∧ Θ x y ∧ ¬ Θ y x  ∧\n    ∃ x ¬ x = x  ∧\n    cls x  ∧\n    fixpt f  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    ∧  ∧\n    fixpt f  ∧\n    x = x  ∧\n    bij f x x  ∧\n    ℤwind f x ∧ wind f x"

  theorem type11_memless_tier : imscriptionTier type11_memless = .O_2 := by
    native_decide

end Voynich

namespace Rohonc

  /-- 13 entries (e.g. p1, p10), tier .O_2 -/
  def type1_sym_F_cross : Imscription :=
    { dim := Dimensionality.D_turnthree, top := Topology.T_bullseye, rel := Relational.R_downstep, pol := Polarity.P_pipevar, fid := Fidelity.F_beltl, kin := KineticChar.K_schwa, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_toneletterstem, stoi := Stoichiometry.S_ltailm, prot := Protection.Omega_dzlig }

  def type1_sym_F_cross_zfct : String :=
    "∃ a( Ord a ∧ x ∈ rank a)  ∧\n    ∀ z( z ∈ x ↔ repl f z)  ∧\n    repl f x ∧ ∀ y( y ∈ repl f x → bij f x y)  ∧\n    ℤ₂ f ∧ ∃ f( bij f x x ∧ ∀ y( f( f y) = y))  ∧\n    cls x  ∧\n    ∀ y( y ⊆ x → ∃ z( z ∈ x ∧ y ⊆ z))  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    seq! f g ∧ ⟨→⟩ f g τ ∧ ¬ ⟨→⟩ g f τ  ∧\n    fixpt f  ∧\n    ∃ y( y ∈ x ∧ ¬ x ∈ y)  ∧\n    ∃ f( func f ∧ ¬ bij f x x)  ∧\n    ℤwind f x ∧ wind f x"

  theorem type1_sym_F_cross_tier : imscriptionTier type1_sym_F_cross = .O_2 := by
    native_decide

  /-- 11 entries (e.g. p11, p13), tier .O_2 -/
  def type2_broad_cross : Imscription :=
    { dim := Dimensionality.D_turnthree, top := Topology.T_bullseye, rel := Relational.R_downstep, pol := Polarity.P_aolig, fid := Fidelity.F_beltl, kin := KineticChar.K_schwa, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_broad, crit := Criticality.Phi_ctyogh, chir := Chirality.H_toneletterstem, stoi := Stoichiometry.S_ltailm, prot := Protection.Omega_dzlig }

  def type2_broad_cross_zfct : String :=
    "∃ a( Ord a ∧ x ∈ rank a)  ∧\n    ∀ z( z ∈ x ↔ repl f z)  ∧\n    repl f x ∧ ∀ y( y ∈ repl f x → bij f x y)  ∧\n    ∃ y( y ∈ x ∧ ¬ y = x)  ∧\n    cls x  ∧\n    ∀ y( y ⊆ x → ∃ z( z ∈ x ∧ y ⊆ z))  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    ∀ y( f y)  ∧\n    fixpt f  ∧\n    ∃ y( y ∈ x ∧ ¬ x ∈ y)  ∧\n    ∃ f( func f ∧ ¬ bij f x x)  ∧\n    ℤwind f x ∧ wind f x"

  theorem type2_broad_cross_tier : imscriptionTier type2_broad_cross = .O_2 := by
    native_decide

  /-- 4 entries (e.g. p301, p350), tier .O_2 -/
  def type3_cross : Imscription :=
    { dim := Dimensionality.D_turnthree, top := Topology.T_bullseye, rel := Relational.R_downstep, pol := Polarity.P_aolig, fid := Fidelity.F_beltl, kin := KineticChar.K_schwa, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_toneletterstem, stoi := Stoichiometry.S_ltailm, prot := Protection.Omega_dzlig }

  def type3_cross_zfct : String :=
    "∃ a( Ord a ∧ x ∈ rank a)  ∧\n    ∀ z( z ∈ x ↔ repl f z)  ∧\n    repl f x ∧ ∀ y( y ∈ repl f x → bij f x y)  ∧\n    ∃ y( y ∈ x ∧ ¬ y = x)  ∧\n    cls x  ∧\n    ∀ y( y ⊆ x → ∃ z( z ∈ x ∧ y ⊆ z))  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    seq! f g ∧ ⟨→⟩ f g τ ∧ ¬ ⟨→⟩ g f τ  ∧\n    fixpt f  ∧\n    ∃ y( y ∈ x ∧ ¬ x ∈ y)  ∧\n    ∃ f( func f ∧ ¬ bij f x x)  ∧\n    ℤwind f x ∧ wind f x"

  theorem type3_cross_tier : imscriptionTier type3_cross = .O_2 := by
    native_decide

  /-- 3 entries (e.g. p151, p200), tier .O_2 -/
  def type4_incl : Imscription :=
    { dim := Dimensionality.D_turnthree, top := Topology.T_invscr, rel := Relational.R_downstep, pol := Polarity.P_aolig, fid := Fidelity.F_beltl, kin := KineticChar.K_schwa, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_toneletterstem, stoi := Stoichiometry.S_ltailm, prot := Protection.Omega_dzlig }

  def type4_incl_zfct : String :=
    "∃ a( Ord a ∧ x ∈ rank a)  ∧\n    sep f x  ∧\n    repl f x ∧ ∀ y( y ∈ repl f x → bij f x y)  ∧\n    ∃ y( y ∈ x ∧ ¬ y = x)  ∧\n    cls x  ∧\n    ∀ y( y ⊆ x → ∃ z( z ∈ x ∧ y ⊆ z))  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    seq! f g ∧ ⟨→⟩ f g τ ∧ ¬ ⟨→⟩ g f τ  ∧\n    fixpt f  ∧\n    ∃ y( y ∈ x ∧ ¬ x ∈ y)  ∧\n    ∃ f( func f ∧ ¬ bij f x x)  ∧\n    ℤwind f x ∧ wind f x"

  theorem type4_incl_tier : imscriptionTier type4_incl = .O_2 := by
    native_decide

  /-- 1 entries (e.g. p300), tier .O_2 -/
  def type5_broad_incl : Imscription :=
    { dim := Dimensionality.D_turnthree, top := Topology.T_invscr, rel := Relational.R_downstep, pol := Polarity.P_aolig, fid := Fidelity.F_beltl, kin := KineticChar.K_schwa, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_broad, crit := Criticality.Phi_ctyogh, chir := Chirality.H_toneletterstem, stoi := Stoichiometry.S_ltailm, prot := Protection.Omega_dzlig }

  def type5_broad_incl_zfct : String :=
    "∃ a( Ord a ∧ x ∈ rank a)  ∧\n    sep f x  ∧\n    repl f x ∧ ∀ y( y ∈ repl f x → bij f x y)  ∧\n    ∃ y( y ∈ x ∧ ¬ y = x)  ∧\n    cls x  ∧\n    ∀ y( y ⊆ x → ∃ z( z ∈ x ∧ y ⊆ z))  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    ∀ y( f y)  ∧\n    fixpt f  ∧\n    ∃ y( y ∈ x ∧ ¬ x ∈ y)  ∧\n    ∃ f( func f ∧ ¬ bij f x x)  ∧\n    ℤwind f x ∧ wind f x"

  theorem type5_broad_incl_tier : imscriptionTier type5_broad_incl = .O_2 := by
    native_decide

  /-- 1 entries (e.g. p51), tier .O_2 -/
  def type6_sym_all_cross : Imscription :=
    { dim := Dimensionality.D_turnthree, top := Topology.T_bullseye, rel := Relational.R_downstep, pol := Polarity.P_subdoublearrow, fid := Fidelity.F_beltl, kin := KineticChar.K_schwa, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_toneletterstem, stoi := Stoichiometry.S_ltailm, prot := Protection.Omega_dzlig }

  def type6_sym_all_cross_zfct : String :=
    "∃ a( Ord a ∧ x ∈ rank a)  ∧\n    ∀ z( z ∈ x ↔ repl f z)  ∧\n    repl f x ∧ ∀ y( y ∈ repl f x → bij f x y)  ∧\n    ∀ f( bij f x x → ∀ y( y ∈ x ↔ f y ∈ x))  ∧\n    cls x  ∧\n    ∀ y( y ⊆ x → ∃ z( z ∈ x ∧ y ⊆ z))  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    seq! f g ∧ ⟨→⟩ f g τ ∧ ¬ ⟨→⟩ g f τ  ∧\n    fixpt f  ∧\n    ∃ y( y ∈ x ∧ ¬ x ∈ y)  ∧\n    ∃ f( func f ∧ ¬ bij f x x)  ∧\n    ℤwind f x ∧ wind f x"

  theorem type6_sym_all_cross_tier : imscriptionTier type6_sym_all_cross = .O_2 := by
    native_decide

end Rohonc

namespace LinearA

  /-- 34 entries (e.g. t120, t121), tier .O_2 -/
  def type1_cross : Imscription :=
    { dim := Dimensionality.D_turnthree, top := Topology.T_bullseye, rel := Relational.R_downstep, pol := Polarity.P_aolig, fid := Fidelity.F_hardsign, kin := KineticChar.K_frtailgamma, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_toneletterstem, stoi := Stoichiometry.S_ltailm, prot := Protection.Omega_dzlig }

  def type1_cross_zfct : String :=
    "∃ a( Ord a ∧ x ∈ rank a)  ∧\n    ∀ z( z ∈ x ↔ repl f z)  ∧\n    repl f x ∧ ∀ y( y ∈ repl f x → bij f x y)  ∧\n    ∃ y( y ∈ x ∧ ¬ y = x)  ∧\n    cls x  ∧\n    ∃ y ∃ z( y ∈ x ∧ z ∈ x ∧ y ⊆ z)  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    seq! f g ∧ ⟨→⟩ f g τ ∧ ¬ ⟨→⟩ g f τ  ∧\n    fixpt f  ∧\n    ∃ y( y ∈ x ∧ ¬ x ∈ y)  ∧\n    ∃ f( func f ∧ ¬ bij f x x)  ∧\n    ℤwind f x ∧ wind f x"

  theorem type1_cross_tier : imscriptionTier type1_cross = .O_2 := by
    native_decide

  /-- 17 entries (e.g. t10, t11), tier .O_2 -/
  def type2_broad_cross : Imscription :=
    { dim := Dimensionality.D_turnthree, top := Topology.T_bullseye, rel := Relational.R_downstep, pol := Polarity.P_aolig, fid := Fidelity.F_hardsign, kin := KineticChar.K_frtailgamma, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_broad, crit := Criticality.Phi_ctyogh, chir := Chirality.H_toneletterstem, stoi := Stoichiometry.S_ltailm, prot := Protection.Omega_dzlig }

  def type2_broad_cross_zfct : String :=
    "∃ a( Ord a ∧ x ∈ rank a)  ∧\n    ∀ z( z ∈ x ↔ repl f z)  ∧\n    repl f x ∧ ∀ y( y ∈ repl f x → bij f x y)  ∧\n    ∃ y( y ∈ x ∧ ¬ y = x)  ∧\n    cls x  ∧\n    ∃ y ∃ z( y ∈ x ∧ z ∈ x ∧ y ⊆ z)  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    ∀ y( f y)  ∧\n    fixpt f  ∧\n    ∃ y( y ∈ x ∧ ¬ x ∈ y)  ∧\n    ∃ f( func f ∧ ¬ bij f x x)  ∧\n    ℤwind f x ∧ wind f x"

  theorem type2_broad_cross_tier : imscriptionTier type2_broad_cross = .O_2 := by
    native_decide

  /-- 2 entries (e.g. t1, t2), tier .O_2 -/
  def type3_sym_F_cross : Imscription :=
    { dim := Dimensionality.D_turnthree, top := Topology.T_bullseye, rel := Relational.R_downstep, pol := Polarity.P_pipevar, fid := Fidelity.F_hardsign, kin := KineticChar.K_frtailgamma, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_toneletterstem, stoi := Stoichiometry.S_ltailm, prot := Protection.Omega_dzlig }

  def type3_sym_F_cross_zfct : String :=
    "∃ a( Ord a ∧ x ∈ rank a)  ∧\n    ∀ z( z ∈ x ↔ repl f z)  ∧\n    repl f x ∧ ∀ y( y ∈ repl f x → bij f x y)  ∧\n    ℤ₂ f ∧ ∃ f( bij f x x ∧ ∀ y( f( f y) = y))  ∧\n    cls x  ∧\n    ∃ y ∃ z( y ∈ x ∧ z ∈ x ∧ y ⊆ z)  ∧\n    ∀ a ∃ y( Card a → Card y ∧ a ⊆ y ∧ y ∈ x)  ∧\n    seq! f g ∧ ⟨→⟩ f g τ ∧ ¬ ⟨→⟩ g f τ  ∧\n    fixpt f  ∧\n    ∃ y( y ∈ x ∧ ¬ x ∈ y)  ∧\n    ∃ f( func f ∧ ¬ bij f x x)  ∧\n    ℤwind f x ∧ wind f x"

  theorem type3_sym_F_cross_tier : imscriptionTier type3_sym_F_cross = .O_2 := by
    native_decide

end LinearA

namespace CorpusComparison

  def voynich_main : Imscription :=
    { dim := Dimensionality.D_omega, top := Topology.T_openo, rel := Relational.R_lyoghlig, pol := Polarity.P_aolig, fid := Fidelity.F_beltl, kin := KineticChar.K_teshlig, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_invscripta, stoi := Stoichiometry.S_doublebaresh, prot := Protection.Omega_dzlig }
  theorem voynich_main_tier : imscriptionTier voynich_main = .O_2 := by native_decide

  def rohonc_main : Imscription :=
    { dim := Dimensionality.D_turnthree, top := Topology.T_bullseye, rel := Relational.R_downstep, pol := Polarity.P_pipevar, fid := Fidelity.F_beltl, kin := KineticChar.K_schwa, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_toneletterstem, stoi := Stoichiometry.S_ltailm, prot := Protection.Omega_dzlig }
  theorem rohonc_main_tier : imscriptionTier rohonc_main = .O_2 := by native_decide

  def linearA_main : Imscription :=
    { dim := Dimensionality.D_turnthree, top := Topology.T_bullseye, rel := Relational.R_downstep, pol := Polarity.P_aolig, fid := Fidelity.F_hardsign, kin := KineticChar.K_frtailgamma, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_toneletterstem, stoi := Stoichiometry.S_ltailm, prot := Protection.Omega_dzlig }
  theorem linearA_main_tier : imscriptionTier linearA_main = .O_2 := by native_decide

  theorem voynich_rohonc_dist : primitiveMismatches voynich_main rohonc_main = 7 := by native_decide
  theorem rohonc_linearA_dist : primitiveMismatches rohonc_main linearA_main = 3 := by native_decide
  theorem voynich_linearA_dist : primitiveMismatches voynich_main linearA_main = 7 := by native_decide

  def voynich_frob_cross_seq : Imscription :=
    { dim := Dimensionality.D_omega, top := Topology.T_bullseye, rel := Relational.R_lyoghlig, pol := Polarity.P_doublebarpipe, fid := Fidelity.F_beltl, kin := KineticChar.K_teshlig, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_invscripta, stoi := Stoichiometry.S_doublebaresh, prot := Protection.Omega_dzlig }
  theorem voynich_frob_cross_seq_tier : imscriptionTier voynich_frob_cross_seq = .O_inf := by native_decide

  def voynich_frob_cross_broad : Imscription :=
    { dim := Dimensionality.D_omega, top := Topology.T_bullseye, rel := Relational.R_lyoghlig, pol := Polarity.P_doublebarpipe, fid := Fidelity.F_beltl, kin := KineticChar.K_teshlig, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_broad, crit := Criticality.Phi_ctyogh, chir := Chirality.H_invscripta, stoi := Stoichiometry.S_doublebaresh, prot := Protection.Omega_dzlig }
  theorem voynich_frob_cross_broad_tier : imscriptionTier voynich_frob_cross_broad = .O_inf := by native_decide

  def voynich_frob_open_seq : Imscription :=
    { dim := Dimensionality.D_omega, top := Topology.T_openo, rel := Relational.R_lyoghlig, pol := Polarity.P_doublebarpipe, fid := Fidelity.F_beltl, kin := KineticChar.K_teshlig, gran := Granularity.G_revapostrophe, gram := Grammar.Gamma_seq, crit := Criticality.Phi_ctyogh, chir := Chirality.H_invscripta, stoi := Stoichiometry.S_doublebaresh, prot := Protection.Omega_dzlig }
  theorem voynich_frob_open_seq_tier : imscriptionTier voynich_frob_open_seq = .O_inf := by native_decide

end CorpusComparison
end Manuscript_ZFCt