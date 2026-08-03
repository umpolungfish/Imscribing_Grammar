-- IG_primitives.lua
-- Pandoc Lua filter: fixes Imscribing Grammar primitive character rendering
-- in XeLaTeX output. Mirrors the approach of hebrew_inject.lua.
--
-- Two classes of problem characters:
--   Class A — missing from Latin Modern text font (lmroman):
--     Ħ U+0126, ƒ U+0192, ɢ U+0262, ɐ U+0250, ʔ U+0294,
--     ˌ U+02CC, ˝ U+02DD, ⊙ U+2299
--     → need {\igprimfont char} (Everson Mono)
--
--   Class B — missing from LaTeX math font (lmmi10) but OK in text mode:
--     Ç U+00C7   (⊢ ⊣ > all migrated off Class B)
--     → need \text{char} (Latin Modern Roman has these)
--
-- In math mode:
--   • \text{X} where X contains Class A → \text{...} with selective {\igprimfont} runs
--   • bare Class A char              → \text{{\igprimfont char}}
--   • bare Class B char              → \text{char}
-- In text mode (Str nodes):
--   • Class A chars                  → {\igprimfont char} (run-aware)
--
-- Add to your document YAML header-includes:
--   \newfontfamily\igprimfont{Everson Mono}
--   (Everson Mono covers IPA, the twelve axis letters, and the Shavian block)
--
-- Usage:
--   pandoc FILE.md -o FILE.pdf --pdf-engine=xelatex --lua-filter=IG_primitives.lua

-- ── Auto-inject \igprimfont definition ───────────────────────────────────────
-- Ensures \igprimfont is available even when the document has no YAML header.
-- Uses \@ifundefined so it's safe to include alongside an explicit definition.
local IGPRIMFONT_DEF = [[
\makeatletter
\@ifundefined{igprimfont}{\newfontfamily\igprimfont{Everson Mono}}{}
\makeatother]]

function Meta(m)
  local raw = pandoc.RawBlock("latex", IGPRIMFONT_DEF)
  if m["header-includes"] then
    -- MetaList or MetaBlocks — append
    local hi = m["header-includes"]
    if hi.t == "MetaList" then
      table.insert(hi, pandoc.MetaBlocks({raw}))
    else
      m["header-includes"] = pandoc.MetaList({
        pandoc.MetaBlocks({hi}), pandoc.MetaBlocks({raw})
      })
    end
  else
    m["header-includes"] = pandoc.MetaList({pandoc.MetaBlocks({raw})})
  end
  return m
end

-- ── Character sets ────────────────────────────────────────────────────────────

-- Class A: not in Latin Modern at all — need \igprimfont
local CLASS_A = {
  [0x0126] = true,  -- Ħ  H with stroke         (Ħ primitive)
  [0x0192] = true,  -- ƒ  f with hook            (ƒ primitive)
  [0x0250] = true,  -- ɐ  turned a               (Φ_ɐ subtype)
  [0x0262] = true,  -- ɢ  small capital G        (ɢ primitive)
  [0x0294] = true,  -- ʔ  glottal stop           (Γ_ʔ subtype)
  [0x02CC] = true,  -- ˌ  low vertical line      (ɢ_ˌ subtype)
  [0x02DD] = true,  -- ˝  double acute accent    (ɢ_˝ subtype)
  [0x2299] = true,  -- ⊙  circled dot            (⊙ criticality primitive)
  [0x2297] = true,  -- ⊗  tensor product         (not in lmroman text font)
  -- Greek subtype chars — not in lmroman; Everson Mono has full Greek coverage
  [0x03B2] = true,  -- β  beta                   (Γ_β subtype)
  [0x03B3] = true,  -- γ  gamma                  (Γ_γ subtype)
  [0x03BB] = true,  -- λ  lambda                 (Ç_λ subtype)
  [0x03C5] = true,  -- υ  upsilon                (Φ_υ subtype)
  [0x03C9] = true,  -- ω  omega                  (retired ⊢ subtype)
  -- Canonical alphabet: axis letters that are not text characters in lmroman
  [0x22A2] = true,  -- ⊢  right tack             (⊢ Dimensionality primitive)
  -- > Relational is ASCII; lmroman has it in both modes, no entry needed.
  [0x22A3] = true,  -- ⊣  left tack              (⊣ Topology primitive)
}

-- Shavian block U+10450–U+1047F: the canonical value glyphs. Everson Mono
-- covers them; lmroman does not, so every one is Class A.
for cp = 0x10450, 0x1047F do CLASS_A[cp] = true end

-- Class B: in lmroman (text mode) but NOT in lmmi10 (math mode).
-- Covers IG primitive glyphs + all IG subtype chars (from SYMBOL_REFERENCE.md)
-- that are non-ASCII Latin text characters needing \text{} in math mode.
local CLASS_B = {
  -- IG primitive glyphs
  [0x00C7] = true,  -- Ç  C with cedilla         (Ç primitive)
  -- IG subtype chars (SYMBOL_REFERENCE.md)
  [0x00A3] = true,  -- £  pound sign             (Ħ_£ subtype)
  [0x00C5] = true,  -- Å  A-ring                 (Ω_Å subtype)
  [0x00C6] = true,  -- Æ  AE ligature            (⊙_Æ subtype)
  [0x00D1] = true,  -- Ñ  N with tilde           (Ħ_Ñ subtype)
  [0x00D9] = true,  -- Ù  U grave                (Ç_Ù subtype)
  [0x00E6] = true,  -- æ  ae ligature            (subtype, from \aelig)
  [0x00EC] = true,  -- ì  i grave                (ƒ_ì subtype)
  [0x00EF] = true,  -- ï  i diaeresis            (Σ_ï subtype)
  [0x00F0] = true,  -- ð  eth                    (ƒ_ð subtype)
  [0x00FF] = true,  -- ÿ  y diaeresis            (⊙_ÿ subtype)
  [0x0151] = true,  -- ő  o double-acute         (Σ_ő subtype)
  [0x0162] = true,  -- Ţ  T with cedilla         (⊙_Ţ subtype)
  [0x015E] = true,  -- Ş  S with cedilla         (ɢ_Ş subtype)
  [0x017C] = true,  -- ż  z dot-above            (ƒ_ż subtype)
  [0x017E] = true,  -- ž  z caron                (⊙_ž subtype)
  [0x02D9] = true,  -- ˙  dot-above              (Φ_˙ subtype)
}

local function str_has_class_a(s)
  local ok, result = pcall(function()
    for _, cp in utf8.codes(s) do
      if CLASS_A[cp] then return true end
    end
    return false
  end)
  return ok and result
end

local function str_has_any_problem(s)
  local ok, result = pcall(function()
    for _, cp in utf8.codes(s) do
      if CLASS_A[cp] or CLASS_B[cp] then return true end
    end
    return false
  end)
  return ok and result
end

-- ── Helpers ───────────────────────────────────────────────────────────────────

-- Wrap a string's Class A runs with {\igprimfont ...}
-- (non-A runs stay as plain text)
local function wrap_class_a(s)
  local parts = {}
  local run   = {}
  local in_a  = false

  local function flush()
    if #run == 0 then return end
    local chunk = table.concat(run)
    if in_a then
      table.insert(parts, "{\\igprimfont\\upshape " .. chunk .. "}")
    else
      table.insert(parts, chunk)
    end
    run = {}
  end

  local ok = pcall(function()
    for _, cp in utf8.codes(s) do
      local a = CLASS_A[cp] or false
      if a ~= in_a then flush(); in_a = a end
      table.insert(run, utf8.char(cp))
    end
  end)
  if not ok then return s end
  flush()
  return table.concat(parts)
end

-- ── Unbraced subscript command fixer ─────────────────────────────────────────
-- LaTeX text commands used as unbraced subscripts (_\SS, _\AA, etc.) cause
-- "Missing {" because they expand to multiple tokens.  Replace with Unicode
-- chars in braces so XeLaTeX handles them safely.
-- Map of LaTeX text-mode commands that are invalid in math mode.
-- Pandoc sometimes emits these when converting Unicode chars in math contexts.
local TEXT_CMD_CHARS = {
  SS = "ß", ss = "ß",
  AA = "Å", aa = "å",
  ae = "æ", AE = "Æ", aelig = "æ", AElig = "Æ",
  oe = "œ", OE = "Œ", oelig = "œ", OElig = "Œ",
  dh = "ð",
  NG = "Ŋ", ng = "ŋ",
  L  = "Ł", l  = "ł",
  o  = "ø", O  = "Ø",
  i  = "ı", j  = "ȷ",
}

-- Escape ^ and ~ inside \text{} in math mode.
-- In LaTeX text mode ^ and ~ are accent/tie operators that expect arguments;
-- \textasciicircum and \textasciitilde produce the literal glyphs safely.
local function fix_text_accent_chars(s)
  return (s:gsub("\\text(%s*)(%b{})", function(spaces, braced)
    local inner = braced:sub(2, -2)
    local fixed = inner:gsub("%^", "\\textasciicircum")
                       :gsub("~",  "\\textasciitilde")
    if fixed == inner then return nil end
    return "\\text" .. spaces .. "{" .. fixed .. "}"
  end))
end

-- Replace any \COMMAND inside math with its Unicode char when the command is
-- a known text-mode command (not a math command).  Handles both braced and
-- unbraced positions.  Unknown commands are left untouched.
local function fix_text_cmds_in_math(s)
  return (s:gsub("\\([%a]+)", function(cmd)
    return TEXT_CMD_CHARS[cmd]  -- nil return = keep original
  end))
end

-- Strip spurious backslashes before non-ASCII Unicode chars in CLASS_A/B.
-- Happens when users write e.g. \Ñ in math mode (not a valid LaTeX command).
-- LaTeX commands use ASCII letters only, so \NON_ASCII is always wrong.
local function strip_unicode_backslashes(s)
  local parts = {}
  local i = 1
  while i <= #s do
    if s:byte(i) == 92 then  -- backslash
      local j = i + 1
      if j <= #s and s:byte(j) >= 0x80 then
        local ok, cp = pcall(utf8.codepoint, s, j)
        if ok and (CLASS_A[cp] or CLASS_B[cp]) then
          -- Drop the backslash; include the Unicode char
          local ch = utf8.char(cp)
          table.insert(parts, ch)
          i = j + #ch
        else
          table.insert(parts, "\\")
          i = j
        end
      else
        table.insert(parts, "\\")
        i = j
      end
    else
      local ok, cp = pcall(utf8.codepoint, s, i)
      if ok then
        local ch = utf8.char(cp)
        table.insert(parts, ch)
        i = i + #ch
      else
        table.insert(parts, s:sub(i, i))
        i = i + 1
      end
    end
  end
  return table.concat(parts)
end

-- Fix unbraced subscript commands: _\SS → _{ß}
-- (after fix_text_cmds_in_math this should be rare, but kept as a safety net)
local function fix_unbraced_subcmds(s)
  s = s:gsub("_\\([%a]+)([^%a{])", function(cmd, after)
    local ch = TEXT_CMD_CHARS[cmd]
    if ch then return "_{" .. ch .. "}" .. after end
    return "_{" .. "\\" .. cmd .. "}" .. after
  end)
  s = s:gsub("_\\([%a]+)$", function(cmd)
    local ch = TEXT_CMD_CHARS[cmd]
    if ch then return "_{" .. ch .. "}" end
    return "_{" .. "\\" .. cmd .. "}"
  end)
  return s
end

-- ── Math node processing ──────────────────────────────────────────────────────

-- Pass 1: upgrade \text{X} → \text{wrapped X} when X has Class A chars.
-- Uses wrap_class_a for selective font switches (more precise than whole-block wrapping).
local function fix_text_commands(s)
  return (s:gsub("\\text(%s*)(%b{})", function(spaces, braced)
    local inner = braced:sub(2, -2)
    if str_has_class_a(inner) then
      local wrapped = wrap_class_a(inner)
      return "\\text" .. spaces .. "{" .. wrapped .. "}"
    end
    return "\\text" .. spaces .. braced
  end))
end

-- Pass 1b: fix subscript/superscript args containing a single problem char.
-- fix_bare_chars only processes depth-0 content; _{ß} has ß at depth 1.
-- This pass catches those cases before fix_bare_chars runs.
local function fix_subarg_problem_chars(s)
  return (s:gsub("([_^])(%b{})", function(marker, braced)
    local inner = braced:sub(2, -2)
    local cp = nil
    local count = 0
    pcall(function()
      for _, c in utf8.codes(inner) do count = count + 1; cp = c end
    end)
    if count ~= 1 or not cp then return nil end
    if CLASS_A[cp] then
      return marker .. "{\\text{{\\igprimfont\\upshape " .. utf8.char(cp) .. "}}}"
    elseif CLASS_B[cp] then
      return marker .. "{\\text{" .. utf8.char(cp) .. "}}"
    end
    return nil
  end))
end

-- Pass 2: handle any remaining bare problem chars (not already inside a group).
-- We walk the string char by char. Inside a {…} group we leave things alone.
local function fix_bare_chars(s)
  local parts  = {}
  local depth  = 0   -- brace depth; at depth>0 we are inside an existing group

  local ok = pcall(function()
    local i = 1
    while i <= #s do
      -- try to decode a utf8 char
      local cp = utf8.codepoint(s, i)
      local char = utf8.char(cp)
      local bytes = #char

      if char == "{" then
        depth = depth + 1
        table.insert(parts, char)
      elseif char == "}" then
        depth = math.max(0, depth - 1)
        table.insert(parts, char)
      elseif depth == 0 then
        if CLASS_A[cp] then
          table.insert(parts, "\\text{{\\igprimfont\\upshape " .. char .. "}}")
        elseif CLASS_B[cp] then
          table.insert(parts, "\\text{" .. char .. "}")
        else
          table.insert(parts, char)
        end
      else
        table.insert(parts, char)
      end

      i = i + bytes
    end
  end)

  if not ok then return s end
  return table.concat(parts)
end

function Math(el)
  local s = el.text
  -- Step 1: strip \UNICODECHAR backslashes (\Ñ → Ñ, etc.)
  s = strip_unicode_backslashes(s)
  -- Step 2: brace any unbraced _\CMD subscripts (_\SS → _{ß})
  s = fix_unbraced_subcmds(s)
  -- Step 3: replace remaining \CMD text-mode commands with Unicode chars
  --         e.g. _{\aelig} → _{æ}
  s = fix_text_cmds_in_math(s)
  -- Step 4: escape ^ and ~ inside \text{} (accent operators in text mode)
  s = fix_text_accent_chars(s)
  -- Step 5: font-wrap problem chars
  if str_has_any_problem(s) then
    s = fix_text_commands(s)         -- upgrade existing \text{} wrappers
    s = fix_subarg_problem_chars(s)  -- wrap single-char _{X}/^{X} subscript args
    s = fix_bare_chars(s)            -- wrap bare depth-0 chars
  end
  if s == el.text then return nil end
  el.text = s
  return el
end

-- ── Text node processing ──────────────────────────────────────────────────────

function Str(el)
  if not str_has_class_a(el.text) then return nil end
  local parts = {}
  local run   = {}
  local in_a  = false

  local function flush()
    if #run == 0 then return end
    local chunk = table.concat(run)
    if in_a then
      table.insert(parts, pandoc.RawInline("latex", "{\\igprimfont\\upshape " .. chunk .. "}"))
    else
      table.insert(parts, pandoc.Str(chunk))
    end
    run = {}
  end

  local ok = pcall(function()
    for _, cp in utf8.codes(el.text) do
      local a = CLASS_A[cp] or false
      if a ~= in_a then flush(); in_a = a end
      table.insert(run, utf8.char(cp))
    end
  end)
  if not ok then return nil end
  flush()
  if #parts == 1 and parts[1].tag == "Str" then return nil end
  return parts
end
