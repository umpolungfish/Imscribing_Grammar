-- ImscribingGrammar/Primitives/Synthon.lean
-- Compatibility shim — re-exports from Imscription.lean.
-- The canonical type is Imscription; this file keeps old import paths working.

import ImscribingGrammar.Primitives.Imscription

namespace ImscribingGrammar.Primitives

abbrev Synthon      := Imscription
abbrev synthonTier  := imscriptionTier

end ImscribingGrammar.Primitives
