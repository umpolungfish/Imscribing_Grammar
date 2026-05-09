-- ig_primitives.lua
-- Pandoc Lua filter: ensures Imscribing Grammar primitive and subtype glyphs
-- render correctly in XeLaTeX/LuaLaTeX.
--
-- IG notation: each symbol is  PrimitiveBase_{\text{SubtypeGlyph}}
--
--   Primitive bases  Ð Þ Ř ƒ Ç ɢ Ħ  — Latin Ext / IPA, absent from math fonts
--   Subtype glyphs   ß ò ¨ ¯ ý Ť ɐ ˙ ì ð ż Ù ʔ ˝ ˌ Ş ž ÿ Æ Ţ Ñ £ ő ï Å
--                    and others listed in SYMBOL_REFERENCE.md — also non-math
--
-- Strategy (avoids double-wrapping):
--   Pass 1 — replace \text{X} where X is IG-special with \text{{\igfont X}}
--   Pass 2 — targeted gsub for each of the 7 non-standard base chars ONLY;
--             these never appear inside \text{}, so there is no overlap with
--             pass 1's output.
--   Str    — wrap IG-special runs in \igtext{} for text-mode occurrences.
--
-- Required in document header-includes:
--   \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
--   \newcommand{\igtext}[1]{{\igfont #1}}
--
-- Usage:
--   pandoc FILE.md -o FILE.pdf --pdf-engine=xelatex --lua-filter=ig_primitives.lua

-- ── Character classification ─────────────────────────────────────────────────

-- Returns true for codepoints that fall outside standard Unicode math font
-- ranges (Latin Modern Math, STIX Two, etc.) and therefore need \igfont.
local function is_ig_special(cp)
  if cp <= 0x007E then return false end                    -- ASCII: always fine
  if cp >= 0x0300 and cp <= 0x036F then return false end  -- combining diacritics
  if cp >= 0x0370 and cp <= 0x03FF then return false end  -- Greek block: in math fonts
  if cp >= 0x2100 and cp <= 0x22FF then return false end  -- letterlike / math ops
  return true
end

local function str_has_ig(s)
  local ok, result = pcall(function()
    for _, cp in utf8.codes(s) do
      if is_ig_special(cp) then return true end
    end
    return false
  end)
  return ok and result
end

-- The 7 primitive base glyphs that are NOT in standard math fonts.
-- Greek-derived bases (Φ Γ Σ Ω φ̂) are already present in math fonts and
-- need no substitution.
-- Each entry is the raw UTF-8 byte sequence for a targeted gsub.
local PRIMITIVE_BASES = {
  "\xC3\x90",  -- Ð  U+00D0  Dimensionality
  "\xC3\x9E",  -- Þ  U+00DE  Topology
  "\xC5\x98",  -- Ř  U+0158  Relational mode
  "\xC6\x92",  -- ƒ  U+0192  Fidelity
  "\xC3\x87",  -- Ç  U+00C7  Kinetics
  "\xC9\xA2",  -- ɢ  U+0262  Interaction grammar
  "\xC4\xA6",  -- Ħ  U+0126  Temporal depth
}

-- ── Math-mode helpers ────────────────────────────────────────────────────────

-- Pass 1: \text{X} where X contains IG-special chars → \text{{\igfont X}}
-- Keeps \text{} to stay in text mode; \igfont inside selects Noto Serif.
-- {\igfont} alone in math mode does nothing — \newfontfamily is text-mode only.
local function inject_math_text(s)
  return (s:gsub("\\text(%b{})", function(braced)
    local inner = braced:sub(2, -2)
    if str_has_ig(inner) then
      return "\\text{{\\igfont " .. inner .. "}}"
    else
      return "\\text" .. braced
    end
  end))
end

-- Pass 1b: _{X} or ^{X} where X is a bare IG-special glyph (no leading \)
-- Wraps with \text{{\igfont}} to escape math mode before applying Noto Serif.
local function inject_bare_subscripts(s)
  return (s:gsub("([_^])(%b{})", function(marker, braced)
    local inner = braced:sub(2, -2)
    if inner:match("^\\") or inner:match("^%{") then
      return nil  -- already a command or nested group; leave alone
    end
    if str_has_ig(inner) then
      return marker .. "{\\text{{\\igfont " .. inner .. "}}}"
    end
  end))
end

-- Pass 2: wrap each bare primitive base glyph with {\igfont X}.
-- These glyphs never appear inside \text{} in well-formed IG notation, so
-- there is no risk of double-wrapping with pass 1's output.
local function inject_primitive_bases(s)
  for _, base in ipairs(PRIMITIVE_BASES) do
    s = s:gsub(base, "\\text{{\\igfont " .. base .. "}}")
  end
  return s
end

-- ── Text-mode helper ─────────────────────────────────────────────────────────

-- Split a plain string into Inlines, wrapping IG-special runs in \igtext{}.
local function split_into_inlines(s)
  local parts = {}
  local run = {}
  local in_ig = false

  local function flush()
    if #run == 0 then return end
    local chunk = table.concat(run)
    if in_ig then
      table.insert(parts, pandoc.RawInline("latex", "\\igtext{" .. chunk .. "}"))
    else
      table.insert(parts, pandoc.Str(chunk))
    end
    run = {}
  end

  local ok = pcall(function()
    for _, cp in utf8.codes(s) do
      local h = is_ig_special(cp)
      if h ~= in_ig then flush(); in_ig = h end
      table.insert(run, utf8.char(cp))
    end
  end)
  if not ok then return { pandoc.Str(s) } end
  flush()
  return parts
end

-- ── Preamble injection ───────────────────────────────────────────────────────

local IG_PREAMBLE = [[\ifdefined\igfont\else
  \usepackage{fontspec}
  \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
\fi
\providecommand{\igtext}[1]{{\igfont #1}}]]

function Meta(m)
  local raw = pandoc.RawBlock("latex", IG_PREAMBLE)
  if not m["header-includes"] then
    m["header-includes"] = pandoc.MetaList({})
  end
  local hi = m["header-includes"]
  if hi.t == "MetaList" then
    table.insert(hi, pandoc.MetaBlocks({raw}))
  end
  return m
end

-- ── Pandoc filter entry points ────────────────────────────────────────────────

function Math(el)
  if not str_has_ig(el.text) then return nil end
  local s = inject_math_text(el.text)         -- pass 1: \text{X} with IG chars
  s = inject_primitive_bases(s)               -- pass 2: bare base glyphs
  s = inject_bare_subscripts(s)               -- pass 3: _{X} with bare IG glyphs
  if s ~= el.text then
    el.text = s
    return el
  end
end

function Str(el)
  if not str_has_ig(el.text) then return nil end
  local parts = split_into_inlines(el.text)
  if #parts == 1 and parts[1].tag == "Str" then return nil end
  return parts
end
