-- hebrew_inject.lua
-- Pandoc Lua filter: auto-wraps Hebrew Unicode characters for XeLaTeX rendering.
--
-- Text mode (Str nodes): splits string into Hebrew/non-Hebrew runs,
--   wraps each Hebrew run in \heb{} (uses \hebrewfont defined in header).
-- Math mode (Math nodes): replaces \text{X} where X contains Hebrew
--   with \text{{\hebrewfont X}}, which forces correct glyph selection
--   inside math's \text command.
--
-- Requires in document header-includes:
--   \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
--   \newcommand{\heb}[1]{{\hebrewfont #1}}
--
-- Usage:
--   pandoc FILE.md -o FILE.pdf --pdf-engine=xelatex --lua-filter=hebrew_inject.lua

-- Hebrew Unicode ranges:
--   U+05B0–U+05EA  main block (letters + vowel points)
--   U+FB1D–U+FB4F  Hebrew presentation forms (rare but included)
local function is_hebrew(cp)
  return (cp >= 0x05B0 and cp <= 0x05EA)
      or (cp >= 0xFB1D and cp <= 0xFB4F)
end

local function str_has_hebrew(s)
  local ok, result = pcall(function()
    for _, cp in utf8.codes(s) do
      if is_hebrew(cp) then return true end
    end
    return false
  end)
  return ok and result
end

-- Split a plain string into a list of pandoc Inlines,
-- wrapping each Hebrew run in RawInline latex \heb{}.
local function split_into_inlines(s)
  local parts = {}
  local run = {}
  local in_heb = false

  local function flush()
    if #run == 0 then return end
    local chunk = table.concat(run)
    if in_heb then
      table.insert(parts, pandoc.RawInline("latex", "\\heb{" .. chunk .. "}{}"))
    else
      table.insert(parts, pandoc.Str(chunk))
    end
    run = {}
  end

  for _, cp in utf8.codes(s) do
    local h = is_hebrew(cp)
    if h ~= in_heb then
      flush()
      in_heb = h
    end
    table.insert(run, utf8.char(cp))
  end
  flush()
  return parts
end

-- In a math string, replace \text{<content>} where <content> contains Hebrew
-- with \text{{\hebrewfont <content>}}.
-- Uses %b{} to correctly match balanced braces one level deep.
local function inject_math_hebrew(s)
  return (s:gsub("\\text(%b{})", function(braced)
    local inner = braced:sub(2, -2)  -- strip outer { }
    if str_has_hebrew(inner) then
      return "\\text{{\\hebrewfont " .. inner .. "}}"
    else
      return "\\text" .. braced
    end
  end))
end

-- Also handle bare Hebrew chars that appear directly in math (outside \text),
-- e.g. $א$ — wrap them in {\hebrewfont X}.
local function inject_bare_math_hebrew(s)
  local parts = {}
  local run = {}
  local in_heb = false

  local function flush()
    if #run == 0 then return end
    local chunk = table.concat(run)
    if in_heb then
      table.insert(parts, "{\\hebrewfont " .. chunk .. "}")
    else
      table.insert(parts, chunk)
    end
    run = {}
  end

  local ok = pcall(function()
    for _, cp in utf8.codes(s) do
      local h = is_hebrew(cp)
      if h ~= in_heb then
        flush()
        in_heb = h
      end
      table.insert(run, utf8.char(cp))
    end
  end)
  if not ok then return s end
  flush()
  return table.concat(parts)
end

-- ── Pandoc filter entry points ────────────────────────────────────────────────

function Str(el)
  if not str_has_hebrew(el.text) then return nil end
  local parts = split_into_inlines(el.text)
  -- If there's only one part and it's already a plain Str, no change needed.
  if #parts == 1 and parts[1].tag == "Str" then return nil end
  return parts
end

function Math(el)
  if not str_has_hebrew(el.text) then return nil end
  -- First pass: handle \text{<hebrew>}
  local s = inject_math_hebrew(el.text)
  -- Second pass: handle any remaining bare Hebrew (not inside \text)
  -- We do this only outside already-processed \text{{\hebrewfont ...}} blocks.
  -- Simple heuristic: if the string still contains a raw Hebrew codepoint, wrap it.
  if str_has_hebrew(s) then
    s = inject_bare_math_hebrew(s)
  end
  if s ~= el.text then
    el.text = s
    return el
  end
end
