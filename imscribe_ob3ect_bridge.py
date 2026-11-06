#!/usr/bin/env python3
"""One resident imscriber continues as the operator of the ob3ect pipeline.

Generation, native tuple expansion, ROTAT measurements and artifact construction
share one agent, provider and conversation. MoDoT runs computation only.
"""

from __future__ import annotations
import asyncio
import json
import re
import subprocess
import sys
import os
import uuid
import time
import contextlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.json import JSON

# Ensure project paths
_PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_PROJECT_ROOT))
sys.path.insert(0, str(_PROJECT_ROOT / "imscribing_grammar"))
sys.path.insert(0, str(_PROJECT_ROOT / "imscribing_grammar" / "ob3ect"))
sys.path.insert(0, str(_PROJECT_ROOT / "imscribing_grammar" / "imscrbgrmr"))

# Import the gated imscription generator
try:
    from imscribing_grammar.agents.imscribe_generator_agent import (
        ImscriptionGeneratorAgent,
        ImscriptionGenerationResult,
    )
    from imscribing_grammar.imscrbgrmr.provider_config import build_agent_config
except ImportError:
    try:
        from agents.imscribe_generator_agent import (
            ImscriptionGeneratorAgent,
            ImscriptionGenerationResult,
        )
        from imscrbgrmr.provider_config import build_agent_config
    except ImportError as e:
        print(f"[ERROR] Could not import imscription generator: {e}", file=sys.stderr)
        sys.exit(1)

# Import ob3ect core for artifact loading
from imscribing_grammar.ob3ect.core import Ob3ectArtifact, GLYPH


_OPCODE_NAMES = re.compile(r"\b(?:" + "|".join(map(re.escape, GLYPH)) + r")\b")


def symbolic_output(text):
    """Render opcode spellings with the canonical symbols."""
    return _OPCODE_NAMES.sub(lambda match: GLYPH[match.group()], text)


class SymbolOutput:
    """Apply the same notation to Rich, plain prints, logs and JSON output."""
    def __init__(self, stream):
        self.stream = stream

    def write(self, text):
        self.stream.write(symbolic_output(text))
        return len(text)

    def __getattr__(self, name):
        return getattr(self.stream, name)

# Constants
_ASK_BINARY = Path("/home/mrnob0dy666/imsgct/MoDoT/ask_native/target/x86_64-unknown-linux-gnu/release/ask")  # MoDoT binary
_OB3ECT_DIGITAL = Path.home() / "ob3ect" / "digital"
_PRIM_ORDER = ["\u22a2", "\u22a3", "\u227b", "\u227a", "\u22c8", "\u22a4", "\u2208", "\u220b", "\u2299", "\u22a5", "\u229e", "\u22a1"]

_LOCAL_PROVIDERS = {"local", "llamacpp", "llama-server", "vllm", "ollama",
                    "local-http", "lmstudio", "lm-studio"}
_API_PROVIDERS = {"openrouter", "deepseek", "gemini", "google", "groq",
                  "qwen", "mistral", "anthropic", "kilo", "kilocode"}


def resolve_bridge_route(provider=None, model=None):
    """Read the configured pair; CLI overrides each environment value directly."""
    selected_provider = provider if provider is not None else os.environ.get("IG_PROVIDER", "deepseek")
    selected_model = model if model is not None else os.environ.get("IG_MODEL")
    return selected_provider.lower(), selected_model


def bridge_agent_config(provider, model):
    config = build_agent_config(provider=provider, model=model, max_tokens=8000)
    if model is not None:
        config["model"] = model
    config["_provider_pinned"] = True
    return config


class BridgeDisplay:
    """Show returned model text and native observations with readable formatting."""
    def __init__(self, *, verbose=False, stderr=False):
        self.console = Console(file=SymbolOutput(sys.stderr if stderr else sys.stdout), highlight=False)
        self.verbose = verbose
        self.status = None
        self.phase = ""

    def heading(self, description, provider, model, session_id):
        body = Text(description, style="bold")
        body.append(f"\n{provider} · {model}", style="cyan")
        self.console.print(Panel(body, title="Imscription → Ob3ect", border_style="cyan", expand=False))
        self.detail("Session", session_id)
        self.console.print()

    @contextlib.contextmanager
    def stage(self, number, title):
        self.phase = title
        self.console.print(Text(f"{number}/3  {title}", style="bold cyan"))
        if self.console.is_terminal:
            with self.console.status(title, spinner="dots") as status:
                self.status = status
                try:
                    yield
                finally:
                    self.status = None
        else:
            yield

    def turn(self, number):
        if self.status:
            self.status.update(f"{self.phase} · model turn {number}")
        else:
            self.console.print(f"     Model turn {number}", style="dim")

    def response(self, number, response):
        self.structured(f"Resident turn {number}", response, border="blue")

    def structured(self, title, output, border="cyan"):
        try:
            value = json.loads(output) if isinstance(output, str) else output
        except (ValueError, TypeError):
            value = None
        body = JSON.from_data(value, ensure_ascii=False) if value is not None else Text(str(output), overflow="fold")
        self.console.print(Panel(body, title=title, border_style=border))

    def operation(self, operation, output):
        try:
            record = json.loads(output)
        except (ValueError, TypeError):
            record = None
        if operation == "boundary comparison" and isinstance(record, dict):
            table = Table(title="Boundary comparison", header_style="bold cyan")
            table.add_column("Check")
            table.add_column("Result")
            for key, label in (("period_match", "Orbit period"),
                               ("canonical_word_match", "Canonical word"),
                               ("verdict_match", "Native verdict"),
                               ("invariants_match", "Invariant flags"),
                               ("canonical_readouts_match", "Every rotated readout"),
                               ("execution_match", "Every executed return"),
                               ("complete", "Complete observations"),
                               ("all_passed", "Boundary recovery")):
                passed = record.get(key, False)
                outcome = ({"complete": "Complete", "all_passed": "Recovered"}.get(key, "Match") if passed else
                           "Missing" if key not in record else
                           {"complete": "Incomplete", "all_passed": "Held"}.get(key, "Differs"))
                table.add_row(label, Text(outcome,
                                          style="green" if passed else "yellow"))
            self.console.print(table)
            if not record.get("all_passed"):
                for detail in record.get("details", []):
                    self.detail("Observation", detail)
            return
        if not isinstance(record, dict) or "orbit" not in record:
            self.structured(f"MoDoT · {operation}", output)
            return
        self.console.print()
        self.console.rule(Text(f"MoDoT · {operation}", style="bold cyan"))
        self.structured("Measured word", record["word"])
        self.structured(f"Canonical word · cut {record['canonical_k']}", record["canonical_word"])
        self.detail("Orbit", f"{record['period']} measured cuts · cyclic ancestry {record['verdict']}")
        behavior = Table(title="Rotation behavior", header_style="bold cyan")
        behavior.add_column("Observation")
        behavior.add_column("Across cuts")
        registers = sorted({row["final_register"] for row in record["orbit"]})
        verdicts = sorted({row["verdict"] for row in record["orbit"]})
        behavior.add_row("Landing register", "Constant: " + registers[0] if len(registers) == 1
                         else "Changes: " + ", ".join(registers))
        behavior.add_row("Cyclic ancestry", "Constant: " + verdicts[0] if len(verdicts) == 1
                         else "Changes: " + ", ".join(verdicts))
        self.console.print(behavior)
        execution = record.get("canonical_execution")
        if execution is not None:
            self.detail("Executed return", "complete" if execution["returned"] else "held")
            fixation = f"first ⊡ at step {execution['fixed_at']}" if execution['fixed_at'] is not None else "no ⊡ executed"
            self.detail("Canonical execution", f"{fixation} · "
                        f"{execution['open_frames']} open frames · {execution['executed_reconnections']} executed reconnections · "
                        f"{execution['skipped_fuses']} skipped ∋ · {execution['inert_steps']} inert steps")
            bank = execution["banking"]
            self.detail("Banking", "vacuous" if bank["vacuous"] else "holds" if bank["holds"] else "exposed")
            self.detail("Banking evidence", f"{bank['deposits']} deposits · {bank['live_clears']} live clears")
        # Every observed register and verdict remains visible. The full word
        # and cut identify each rotation without reprinting it at every row.
        orbit = record["orbit"]
        groups = max(1, min(4, self.console.width // 36))
        table = Table(title="All orbit observations", header_style="bold cyan", show_lines=False)
        for _ in range(groups):
            table.add_column("Cut", justify="right")
            table.add_column("Register")
            table.add_column("Ancestry")
            table.add_column("Return")
        for start in range(0, len(orbit), groups):
            cells = []
            for row in orbit[start:start + groups]:
                cut = str(row["k"]) + (" *" if row["k"] == record["canonical_k"] else "")
                cells.extend([cut, row["final_register"], row["verdict"],
                              "complete" if row.get("execution", {}).get("returned") else "held" if "execution" in row else "unmeasured"])
            cells.extend([""] * (groups * 4 - len(cells)))
            table.add_row(*cells)
        table.caption = "* canonical cut; cut k rotates the complete word left by k opcodes"
        self.console.print(table)

    def detail(self, label, value):
        line = Text(f"     {label}  ", style="dim")
        line.append(str(value), style="default")
        self.console.print(line)

    def comparison(self, verification):
        if verification["all_passed"]:
            self.console.print("     Exact word and every rotated readout recovered", style="green")
            return
        for detail in verification["details"]:
            self.console.print(Text(f"     {detail}"))

    def finish(self, result, evidence_path):
        self.console.print()
        table = Table.grid(padding=(0, 2))
        table.add_column(style="dim")
        table.add_column(overflow="fold")
        table.add_row("Tuple", Text(result.imscription_tuple))
        if result.reentry:
            table.add_row("Returned Type", Text(result.reentry.get("current_tuple", "Pending")))
            table.add_row("Re-entry rounds", str(len(result.reentry.get("rounds", []))))
        table.add_row("Bootstrap", f"{len(result.ob3ect_bootstrap_word or '')} opcodes")
        artifact = result.ob3ect_artifact
        if artifact is not None:
            lean_verified = getattr(artifact, "lean_verified", None)
            lean_output = getattr(artifact, "lean_verification_output", "") or ""
            lean_status = ("Elaborated" if lean_verified is True else
                           "Rejected" if lean_verified is False else
                           "Timed out" if "timed out" in lean_output else "Not verified")
            table.add_row("Lean scaffold", lean_status)
        def display_path(path):
            resolved = Path(path).absolute()
            for root, prefix in ((_PROJECT_ROOT, ""), (Path.home(), "~/")):
                try:
                    return prefix + str(resolved.relative_to(root))
                except ValueError:
                    pass
            return str(path)
        table.add_row("Artifact", Text(display_path(result.artifact_path) if result.artifact_path else "Not produced"))
        table.add_row("Evidence", Text(display_path(evidence_path)))
        if result.error:
            table.add_row("Reason", Text(result.error))
        title = (("Re-entry stable" if result.all_passed else "Re-entry held") if result.reentry else
                 ("Boundary recovered" if result.all_passed else "Boundary held"))
        self.console.print(Panel(table, title=title,
                                 border_style="green" if result.all_passed else "yellow"))
        if artifact is not None and getattr(artifact, "lean_verification_output", ""):
            self.structured("Lean scaffold output", artifact.lean_verification_output,
                            border="green" if getattr(artifact, "lean_verified", None) else "yellow")


def retained_message_view(messages, system=""):
    """Reference exact repeated tool returns without removing their events.

    The complete messages and measurements remain in the resident bank. The
    first occurrence supplies the definition; subsequent occurrences retain
    their own operation and index while referring to that identical output.
    """
    import hashlib
    import os
    from imscribing_grammar.resident_state_view import NativeJSONView
    json_view = NativeJSONView(GLYPH.values())
    seen = {}
    assistant_definitions = {}
    assistant_frames = []
    # The API already carries the current system text. Historical task frames
    # may reference exact slices of that same visible text without duplicating it.
    task_frames = [(-1, f"Task frame: {system}\n")] if system else []
    view = []
    for index, message in enumerate(messages):
        content = message["content"]
        if message["role"] == "assistant":
            if content in assistant_definitions:
                original = assistant_definitions[content]
                digest = hashlib.sha256(content.encode()).hexdigest()
                content = f"Retained identical assistant output: message={original}; sha256={digest}"
            else:
                assistant_definitions[content] = index
                matches = []
                for prior_index, prior in assistant_frames:
                    prefix = len(os.path.commonprefix([content, prior]))
                    suffix = len(os.path.commonprefix([content[prefix:][::-1], prior[prefix:][::-1]]))
                    matches.append((prefix + suffix, prior_index, prefix, suffix))
                shared, prior_index, prefix, suffix = max(matches, default=(0, -1, 0, 0))
                if shared >= 512:
                    digest = hashlib.sha256(content.encode()).hexdigest()
                    middle = content[prefix:len(content)-suffix if suffix else None]
                    content = (f"Retained assistant continuation: source_message={prior_index}; "
                               f"prefix_characters={prefix}; suffix_characters={suffix}; sha256={digest}\n{middle}")
                assistant_frames.append((index, message['content']))
        if message["role"] == "user" and content.startswith("MoDoT ") and " returned:\n" in content:
            head, body = content.split(" returned:\n", 1)
            if body in seen:
                original = seen[body]
                digest = hashlib.sha256(body.encode()).hexdigest()
                content = f"{head} returned:\nRetained identical native output: message={original}; sha256={digest}"
            else:
                seen[body] = index
                content = f"{head} returned:\nRetained native output definition: message={index}\n{json_view.encode_body(body)}"
        original_content = message["content"]
        if message["role"] == "user" and original_content.startswith("Task frame: "):
            matches = []
            for prior_index, prior in task_frames:
                prefix = len(os.path.commonprefix([original_content, prior]))
                suffix = len(os.path.commonprefix([original_content[prefix:][::-1], prior[prefix:][::-1]]))
                matches.append((prefix + suffix, prior_index, prefix, suffix))
            shared, prior_index, prefix, suffix = max(matches, default=(0, -1, 0, 0))
            if shared >= 256:
                digest = hashlib.sha256(original_content.encode()).hexdigest()
                middle = original_content[prefix:len(original_content)-suffix if suffix else None]
                definition = '; source_definition=Task frame: + current API system + newline' if prior_index == -1 else ''
                content = (f"Retained task-frame continuation v2: message={index}; source_message={prior_index}; "
                           f"prefix_characters={prefix}; suffix_characters={suffix}; sha256={digest}{definition}\n{middle}")
            else:
                content = f"Retained task-frame definition: message={index}\n{original_content}"
                content = json_view.encode_text(content)
            task_frames.append((index, original_content))
        view.append({**message, "content": content})
    return view


def restore_retained_message_view(messages, system=""):
    """Expand every reference for exact continuation/codec verification."""
    import hashlib
    from imscribing_grammar.resident_state_view import NativeJSONView
    json_view = NativeJSONView()
    restored = []
    assistant_reference = re.compile(r"Retained identical assistant output: message=(\d+); sha256=([0-9a-f]{64})$")
    assistant_delta = re.compile(r"Retained assistant continuation: source_message=(\d+); prefix_characters=(\d+); suffix_characters=(\d+); sha256=([0-9a-f]{64})\n(.*)", re.S)
    definition = re.compile(r"Retained native output definition: message=(\d+)(?:; sha256=([0-9a-f]{64}))?\n(.*)", re.S)
    pattern = re.compile(r"Retained identical native output: message=(\d+); sha256=([0-9a-f]{64})$")
    task_definition = re.compile(r"Retained task-frame definition: message=(\d+)\n(.*)", re.S)
    task_continuation = re.compile(r"Retained task-frame continuation: message=(\d+); prefix_message=(\d+); prefix_characters=(\d+); prefix_sha256=([0-9a-f]{64})\n(.*)", re.S)
    task_delta = re.compile(r"Retained task-frame continuation v2: message=(\d+); source_message=(-?\d+); prefix_characters=(\d+); suffix_characters=(\d+); sha256=([0-9a-f]{64})(?:; source_definition=Task frame: \+ current API system \+ newline)?\n(.*)", re.S)
    for message in messages:
        content = json_view.decode_text(message["content"])
        shared_delta = assistant_delta.fullmatch(content) if message['role'] == 'assistant' else None
        if shared_delta:
            original, prefix, suffix = map(int, shared_delta.group(1, 2, 3))
            if original >= len(restored) or restored[original]['role'] != 'assistant':
                raise ValueError('Assistant delta is outside its retained past')
            source = restored[original]['content']
            content = source[:prefix] + shared_delta[5] + (source[-suffix:] if suffix else '')
            if hashlib.sha256(content.encode()).hexdigest() != shared_delta[4]:
                raise ValueError('Assistant delta changed its source binding')
        shared_assistant = assistant_reference.fullmatch(content) if message["role"] == "assistant" else None
        if shared_assistant:
            original = int(shared_assistant[1])
            if original >= len(restored) or restored[original]["role"] != "assistant":
                raise ValueError("Assistant reference is outside its retained past")
            content = restored[original]["content"]
            if hashlib.sha256(content.encode()).hexdigest() != shared_assistant[2]:
                raise ValueError("Assistant reference changed its source binding")
        delta = task_delta.fullmatch(content)
        if delta:
            index, prior_index, prefix, suffix = map(int, delta.group(1, 2, 3, 4))
            if index != len(restored) or prior_index < -1 or prior_index >= len(restored) or (prior_index == -1 and not system):
                raise ValueError("Task-frame delta is outside the retained past")
            source = f"Task frame: {system}\n" if prior_index == -1 else restored[prior_index]["content"]
            content = source[:prefix] + delta[6] + (source[-suffix:] if suffix else "")
            if hashlib.sha256(content.encode()).hexdigest() != delta[5]:
                raise ValueError("Task-frame delta changed its source binding")
        defined = task_definition.fullmatch(content)
        continued = task_continuation.fullmatch(content)
        if defined:
            if int(defined[1]) != len(restored):
                raise ValueError("Task-frame definition changed its source position")
            content = defined[2]
        elif continued:
            index, prior_index, length = map(int, continued.group(1, 2, 3))
            if index != len(restored) or prior_index >= len(restored):
                raise ValueError("Task-frame continuation is outside the retained past")
            prefix = restored[prior_index]["content"][:length]
            if hashlib.sha256(prefix.encode()).hexdigest() != continued[4]:
                raise ValueError("Task-frame prefix changed its source binding")
            content = prefix + continued[5]
        if message["role"] == "user" and content.startswith("MoDoT ") and " returned:\n" in content:
            head, body = content.split(" returned:\n", 1)
            declared = definition.fullmatch(body)
            if declared:
                decoded_body = json_view.decode_body(declared[3])
                if int(declared[1]) != len(restored) or (declared[2] and hashlib.sha256(decoded_body.encode()).hexdigest() != declared[2]):
                    raise ValueError("Native output definition changed its source binding")
                body = decoded_body
                content = f"{head} returned:\n{body}"
            match = pattern.fullmatch(body)
            if match:
                index = int(match[1])
                if index >= len(restored):
                    raise ValueError("Native output reference is outside the retained past")
                original = restored[index]["content"].split(" returned:\n", 1)[1]
                if hashlib.sha256(original.encode()).hexdigest() != match[2]:
                    raise ValueError("Native output reference changed its source binding")
                content = f"{head} returned:\n{original}"
        restored.append({**message, "content": content})
    return restored


def banked_message_view(messages, system="", recent=2):
    """Expose a continuation while retaining a retrievable, exact history bank."""
    import hashlib
    offset = max(0, len(messages)-recent)
    raw = json.dumps(messages[:offset], ensure_ascii=False)
    boundary = {'offset': offset, 'total_messages': len(messages),
                'bank_sha256': hashlib.sha256(raw.encode()).hexdigest()}
    content = ('Resident history bank boundary: ' + json.dumps(boundary) + '\n'
               'Every original message remains in the same resident bank. Earlier records are held, not deleted. '
               'For exact historical text, respond ONLY with '
               '{"resident_history_read":{"message":0,"offset":0,"length":8192}}. '
               'Message indices address the complete original history; request one page at a time. '
               'The following recent records begin at the boundary offset. References inside those records '
               'use recent-record indices; source_message=-1 refers to the current API system text.')
    return [{'role': 'user', 'content': content}] + retained_message_view(messages[offset:], system)


def restore_banked_message_view(view, bank, system=""):
    import hashlib
    header = view[0]['content'].split('\n', 1)[0]
    boundary = json.loads(header.removeprefix('Resident history bank boundary: '))
    offset = boundary['offset']
    if type(offset) is not int or not 0 <= offset <= len(bank):
        raise ValueError('Resident bank offset is outside its source history')
    raw = json.dumps(bank[:offset], ensure_ascii=False)
    if boundary['total_messages'] != len(bank) or hashlib.sha256(raw.encode()).hexdigest() != boundary['bank_sha256']:
        raise ValueError('Resident bank boundary changed its retained history')
    return bank[:offset] + restore_retained_message_view(view[1:], system)


def resident_context_pages(messages, current, system="", page_bytes=4096):
    """Bound the inference view; exact operands stay addressable in the bank.

    A byte bound reserves room even for non-ASCII glyph tokenization. No
    historical or current operand is deleted or rewritten in its source bank.
    Negative read addresses identify the pending task (-1) and system (-2).
    """
    import hashlib
    def page(text, address):
        data=text.encode('utf-8')
        if len(data)<=2*page_bytes:return text
        first=data[:page_bytes].decode('utf-8',errors='ignore')
        last=data[-page_bytes:].decode('utf-8',errors='ignore')
        return (f'Retained operand: message={address}; utf8_bytes={len(data)}; '
                f'sha256={hashlib.sha256(data).hexdigest()}. '
                'The middle remains in the exact resident bank. Read it with '
                '{"resident_history_read":{"message":'+str(address)+',"offset":0,"length":8192}}. '
                'Read offsets and lengths count original characters.\n'
                'BEGIN ORIGINAL OPERAND\n'+first+'\nHELD MIDDLE\n'+last+'\nEND ORIGINAL OPERAND')
    boundary=banked_message_view(messages,system,recent=0)
    for index in range(max(0,len(messages)-2),len(messages)):
        message=messages[index]
        boundary.append({**message,'content':page(message['content'],index)})
    boundary.append({**current,'content':page(current['content'],-1)})
    return boundary,page(system,-2)


class BridgeSession:
    """Retain the starting agent and its complete inference/tool continuation."""
    def __init__(self, agent, display=None):
        self.agent = agent
        self.session_id = uuid.uuid4().hex
        self.messages = []
        self.operations = []
        self.turn_count = 0
        self.display = display
        self.record_path = None
        self.banked_inference = False
        self.pending_inference = None
        self._ig_chain_name = agent.config.get("provider", "resident")
        self._call = agent.call_llm

        async def remember(*args, **kwargs):
            prompt = kwargs.get("prompt", args[0] if args else "")
            self.turn_count += 1
            if self.display:
                self.display.turn(self.turn_count)
            call_args = list(args)
            call_kwargs = dict(kwargs)
            current_system = kwargs.get('system', '')
            if isinstance(prompt, str) and self.messages and not self.banked_inference:
                history = retained_message_view(self.messages, current_system)
                if restore_retained_message_view(history, current_system) != self.messages:
                    raise ValueError('Resident inference changed its retained history')
                carried_prompt = history + [{"role": "user", "content": prompt}]
                if "prompt" in call_kwargs or not call_args:
                    call_kwargs["prompt"] = carried_prompt
                else:
                    call_args[0] = carried_prompt
            if isinstance(prompt, list) and not self.banked_inference:
                current = {**prompt[-1], "content": f"Task frame: {kwargs.get('system', '')}\n{prompt[-1]['content']}"}
                raw_prompt = prompt[:-1] + [current]
                carried_prompt = retained_message_view(raw_prompt, current_system)
                if restore_retained_message_view(carried_prompt, current_system) != raw_prompt:
                    raise ValueError('Resident inference changed its retained history')
                if (not carried_prompt[-1]["content"].startswith("Retained task-frame continuation v2:")
                        or len(carried_prompt[-1]["content"]) >= len(prompt[-1]["content"])):
                    carried_prompt[-1] = prompt[-1]
                if "prompt" in call_kwargs or not call_args:
                    call_kwargs["prompt"] = carried_prompt
                else:
                    call_args[0] = carried_prompt
            for read_attempt in range(5):
                if self.banked_inference:
                    history = banked_message_view(self.messages, current_system, recent=0)
                    if restore_banked_message_view(history, self.messages, current_system) != self.messages:
                        raise ValueError('Resident bank changed its source history')
                    current_message = prompt[-1] if isinstance(prompt, list) else {'role': 'user', 'content': prompt}
                    self.pending_inference={'message':current_message,'system':current_system}
                    pages,system_page=resident_context_pages(self.messages,current_message,current_system)
                    # The byte bound leaves output capacity within the local
                    # 65,536-token window without relying on chars/token guesses.
                    if len(json.dumps(pages,ensure_ascii=False).encode())+len(system_page.encode())>48000:
                        raise ValueError('Resident paged inference exceeds its input byte budget')
                    self.save()
                    call_kwargs['system']=system_page
                    if 'prompt' in call_kwargs or not call_args:
                        call_kwargs['prompt'] = pages
                    else:
                        call_args[0] = pages
                try:
                    response = await self._call(*call_args, **call_kwargs)
                except Exception as exc:
                    self.operations.append({"operation": "resident inference error", "output": f"{type(exc).__name__}: {exc}"})
                    if any(marker in str(exc).lower() for marker in ('exceed_context_size_error', 'context size', 'context length', 'context window')) and not self.banked_inference:
                        self.banked_inference = True
                        self.operations.append({'operation': 'Resident bank boundary',
                            'output': 'Context capacity reached. Complete history retained in the same resident bank; exact paged readout enabled.'})
                        self.save()
                        continue
                    self.save()
                    raise
                try:
                    request = json.loads(response)
                except (TypeError, ValueError):
                    request = None
                if not isinstance(request, dict) or set(request) != {'resident_history_read'}:
                    break
                source_count = len(self.messages)
                self.messages.append({'role': 'assistant', 'content': response})
                self.operations.append({'operation': 'Resident history request', 'output': response})
                self.save()
                query = request['resident_history_read']
                if not isinstance(query, dict):
                    raise ValueError('Resident history read requires a message and character page')
                index, offset, length = (query.get(k, default) for k, default in [('message', -1), ('offset', 0), ('length', 8192)])
                if any(type(x) is not int for x in [index, offset, length]) or not (-2 <= index < source_count) or (index < 0 and self.pending_inference is None) or offset < 0 or not 1 <= length <= 8192:
                    raise ValueError('Resident history read is outside its retained bank or page bound')
                original = (self.pending_inference['message'] if index == -1 else {'role':'system','content':self.pending_inference['system']} if index == -2 else self.messages[index])
                self.tool_return('Resident history read', json.dumps({'message': index, 'role': original['role'],
                    'offset': offset, 'total_characters': len(original['content']),
                    'text': original['content'][offset:offset+length]}, ensure_ascii=False))
                self.turn_count += 1
                if self.display:
                    self.display.turn(self.turn_count)
            else:
                raise RuntimeError('Resident inference held after its bounded history readout; full bank retained')
            if self.display:
                self.display.response(self.turn_count, response)
            message = prompt[-1] if isinstance(prompt, list) else {"role": "user", "content": prompt}
            system = kwargs.get("system", "")
            self.messages.extend([
                {"role": "user", "content": f"Task frame: {system}\n{message['content']}"},
                {"role": "assistant", "content": response},
            ])
            self.save()
            return response
        agent.call_llm = remember

    def __getattr__(self, name):
        return getattr(self.agent.provider, name)

    def progress(self, message):
        if self.display:
            if self.display.status:
                self.display.status.update(message)
            else:
                self.display.detail("Design", message)

    async def query(self, prompt, **kwargs):
        # auto_design's provider surface re-enters the original agent. It does
        # not allocate a provider or start ask's independent inference loop.
        system = kwargs.pop("system", "")
        max_tokens = kwargs.pop("max_tokens", self.agent.config.get("max_tokens", 8000))
        if max_tokens is None and self.agent.config.get("provider") == "anthropic":
            # This API requires an integer output budget on every request.
            max_tokens = self.agent.config.get("max_tokens") or 8000
        supported = {k: v for k, v in kwargs.items() if k in {"temperature", "reasoning_off"}}
        return await self.agent.call_llm(
            prompt=self.messages + [{"role": "user", "content": prompt}],
            system=system, max_tokens=max_tokens, max_retries=0, **supported,
        )

    def tool_return(self, operation, output):
        self.operations.append({"operation": operation, "output": output})
        if self.display:
            self.display.operation(operation, output)
        # Keep the full measured orbit in the bank. Its boundary and landing
        # map carry the return into inference without repeating every rotated
        # glyph word in the model's context.
        observed = output
        try:
            record = json.loads(output)
            if isinstance(record, dict) and "orbit" in record:
                observed = json.dumps({k: v for k, v in record.items() if k != "orbit"}, ensure_ascii=False)
        except (TypeError, ValueError):
            pass
        self.messages.append({"role": "user", "content": f"MoDoT {operation} returned:\n{observed}"})
        self.save()

    def save(self):
        if self.record_path:
            self.record_path.write_text(json.dumps({
                "session_id": self.session_id, "agent_id": self.agent.agent_id,
                "provider": self.agent.config.get("provider"),
                "model": getattr(self.agent.provider, "model", None),
                "messages": self.messages, "operations": self.operations,
                "reentry": getattr(self, "reentry_state", None),
                "banked_inference": self.banked_inference,
                "pending_inference": self.pending_inference,
            }, ensure_ascii=False, indent=2))


def _native(args):
    result = subprocess.run([str(_ASK_BINARY), *args], capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise RuntimeError(f"MoDoT {' '.join(args[:2])}: {result.stderr or result.stdout}")
    return result.stdout

@dataclass
class BridgeResult:
    description: str
    imscription_name: str = ""
    imscription_tuple: str = ""
    imscription_word: str = ""
    session_id: str = ""
    artifact_path: Optional[str] = None
    operations: List[Dict[str, Any]] = field(default_factory=list)
    ob3ect_artifact: Optional[object] = None
    ob3ect_bootstrap_word: Optional[str] = None
    orbit_verification: Dict[str, Any] = field(default_factory=dict)
    reentry: Optional[Dict[str, Any]] = None
    all_passed: bool = False
    error: Optional[str] = None

def nest_native_word(expanded: str) -> Dict[str, Any]:
    nesting = json.loads(_native(["--imasm", "nest", expanded]))
    positions = nesting["retained_positions"]
    if (len(positions) != len(set(positions))
            or "".join(expanded[index] for index in positions) != nesting["word"]
            or "".join(c for c in expanded if c not in "⊢⊣∈∋")
               != "".join(c for c in nesting["word"] if c not in "⊢⊣∈∋")):
        raise ValueError("Native nesting did not retain the ordered work and source positions")
    return nesting


def nest_design_sequence(sequence, *, nesting_return=None):
    from imscribing_grammar.ob3ect.auto import _CORE_GLYPH, _parse_opcode
    expanded = "".join(_CORE_GLYPH[_parse_opcode(step)] for step in sequence)
    # A designer's one-source graph may contain genuine nested or open arms.
    # Boundary dissolution applies to expanded component programs, rather than
    # deleting the branches from an ordinary one-frame design.
    if expanded.count("⊢") <= 1:
        return sequence
    nesting = nest_native_word(expanded)
    nesting["expanded_sequence"] = sequence
    if nesting_return:
        nesting_return(nesting)
    return [sequence[position] for position in nesting["retained_positions"]]


def run_tuple_cycle(tuple_str: str, *, source_return=None, nesting_return=None) -> str:
    """Expand through the native type programs and their return leg."""
    output = _native(["--imasm", "cycle", f"tuple={tuple_str}"])
    match = re.search(r"^word:\s*([⊢⊣≻≺⋈⊙∈∋⊤⊥⊞⊡]+)\s*$", output, re.M)
    if not match or "LOST:" in output or "return leg —" in output:
        raise ValueError(f"Native tuple cycle did not close its return: {output}")
    if source_return:
        source_return(output)
    expanded = match.group(1)
    nesting = nest_native_word(expanded)
    if nesting_return:
        nesting_return(nesting)
    return nesting["word"]


def run_imasm_cycle(word: str) -> Dict[str, Any]:
    """Read every rotation from MoDoT's native word instrument."""
    output = _native(["--rotat", word])
    header = re.search(r"^word\s*:\s*(\S+)\s+period\s+(\d+)", output, re.M)
    rows = re.findall(r"^\s*(\d+)\s+(\S+)\s+([NTFB])\s+([⊢⊣≻≺⋈⊙∈∋⊤⊥⊞⊡]+)\s*$", output, re.M)
    if not header or int(header.group(2)) != len(rows) or not rows:
        raise ValueError(f"Incomplete native ROTAT audit: {output}")
    orbit = [{"k": int(k), "final_register": reg, "verdict": verdict, "word": w}
             for k, reg, verdict, w in rows]
    if [r["k"] for r in orbit] != list(range(len(orbit))):
        raise ValueError("Native ROTAT audit has missing or duplicated cuts")
    execution_rows = re.findall(r"^execution (\d+) (\{[^\n]+\})$", output, re.M)
    banking_rows = re.findall(r"^banking (\d+) (\{[^\n]+\})$", output, re.M)
    executions = {int(k): json.loads(raw) for k, raw in execution_rows}
    banking = {int(k): json.loads(raw) for k, raw in banking_rows}
    if (len(execution_rows) != len(orbit) or len(banking_rows) != len(orbit)
            or set(executions) != set(range(len(orbit))) or set(banking) != set(executions)):
        raise ValueError("Native ROTAT audit lacks complete execution/banking evidence; rebuild the MoDoT ask instrument")
    for row in orbit:
        execution = executions[row["k"]]
        if execution["final_register"] != row["final_register"]:
            raise ValueError("Native execution and ROTAT register disagree")
        execution["banking"] = banking[row["k"]]
        row["execution"] = execution
    bounded = [r for r in orbit if r["word"].startswith("⊢") and r["word"].endswith("⊣")]
    canonical = min(bounded or orbit, key=lambda r: r["word"])
    k = canonical["k"]
    aligned = orbit[k:] + orbit[:k]
    return {"word": word, "period": len(orbit), "canonical_k": k,
            "canonical_word": canonical["word"], "verdict": canonical["verdict"],
            "invariants": {key: all(r[key] == orbit[0][key] for r in orbit)
                           for key in ("final_register", "verdict")},
            "orbit": orbit,
            "canonical_readouts": [(r["final_register"], r["verdict"]) for r in aligned],
            "canonical_execution": canonical["execution"],
            "canonical_executions": [r["execution"] for r in aligned],
            "execution_returned": canonical["execution"]["returned"],
            "verdict_scope": "cyclic ancestry; execution and banking are measured separately"}

def parse_imscription_tuple(imscription_result: ImscriptionGenerationResult) -> str:
    return imscription_result.imscription.to_notation()

def parse_tuple_to_dict(tuple_str: str) -> Dict[str, str]:
    clean = tuple_str.strip()
    if clean.startswith("\u27e8") and clean.endswith("\u27e9"):
        clean = clean[1:-1]
    
    glyphs = list(clean)
    
    if len(glyphs) != 12:
        raise ValueError(f"Tuple must have 12 glyphs, got {len(glyphs)}")
    
    return dict(zip(_PRIM_ORDER, glyphs))


def navigator_logical_expressions(tuple_str: str, name: str = "current assignment") -> dict:
    """Read both native formula decompositions for the exact current tuple."""
    from imscribing_grammar.navigators import cl8nk_navigator, cl9nk_navigator

    catalog = Path.home() / ".imscrbgrmr" / "catalog.json"
    coordinates = cl9nk_navigator.parse_tuple_arg(tuple_str)
    if coordinates is None:
        raise ValueError("Navigator expressions require a valid twelve-coordinate tuple")
    result = {"tuple": tuple_str, "catalog": str(catalog), "navigators": {}}
    for label, navigator in (("CL8NK", cl8nk_navigator), ("CL9NK", cl9nk_navigator)):
        path = navigator._find_catalog_path()
        if path is None or Path(path).resolve() != catalog.resolve():
            raise ValueError(f"{label} must read the main catalog: {catalog}")
        navigator.load_catalog(force=True)
        formula = navigator.generate_formula(coordinates["tuple"], system_name=name)
        if formula.get("status") == "error":
            raise ValueError(f"{label}: {formula['message']}")
        decomposition = formula["formula_decomposition"]
        if any(part["proximity"] == "unknown" for part in decomposition["per_primitive_fragments"]):
            raise ValueError(f"{label} returned an unknown logical fragment for {tuple_str}")
        result["navigators"][label] = {
            "system": formula["system"], "tuple": formula["tuple"],
            "reference": formula["reference"],
            "formula_decomposition": decomposition,
        }
    return result

def verify_orbit_consistency(audit_a, audit_b):
    required = ("period", "canonical_word", "verdict", "invariants", "canonical_readouts")
    complete = all(a.get(key) is not None for a in (audit_a, audit_b) for key in required)
    complete = complete and all(a.get("period", 0) > 0 and
                               len(a.get("canonical_readouts", [])) == a["period"]
                               for a in (audit_a, audit_b))
    matches = {f"{key}_match": complete and audit_a[key] == audit_b[key] for key in required}
    if "canonical_executions" in audit_a or "canonical_executions" in audit_b:
        matches["execution_match"] = (complete and
            len(audit_a.get("canonical_executions", [])) == audit_a["period"] and
            len(audit_b.get("canonical_executions", [])) == audit_b["period"] and
            audit_a["canonical_executions"] == audit_b["canonical_executions"])
    details = []
    if not complete:
        details.append("Incomplete native audit; every rotated cut is required")
    else:
        if not matches["period_match"]:
            details.append(f"Orbit period: expected {audit_a['period']} cuts, received {audit_b['period']}")
        if not matches["canonical_word_match"]:
            details.append(f"Canonical word differs: {len(audit_a['canonical_word'])} retained opcodes, {len(audit_b['canonical_word'])} returned")
        if not matches["verdict_match"]:
            details.append(f"Native ROTAT verdict: expected {audit_a['verdict']}, received {audit_b['verdict']}")
        if not matches["invariants_match"]:
            details.append(f"Orbit invariants: expected {audit_a['invariants']}, received {audit_b['invariants']}")
        if not matches["canonical_readouts_match"]:
            details.append("Rotated register readouts differ from the retained boundary")
        if not matches.get("execution_match", True):
            details.append("Executed frame returns or banking evidence differ from the retained boundary")
    return {**matches, "complete": complete, "all_passed": complete and all(matches.values()),
            "details": details}


def persist_resident_artifact(artifact, *, session, description, name, artifact_dir=None):
    from imscribing_grammar.ob3ect.auto import _write_diagrams
    directory = Path(artifact_dir or _OB3ECT_DIGITAL)
    slug = re.sub(r"[^a-z0-9]+", "_", (name or description).lower()).strip("_")[:96] or "ob3ect"
    # Bind this run to its exact artifact; never load a different recent design.
    attempt = sum(op["operation"] == "artifact persisted" for op in session.operations)
    target = directory / f"{slug}_{session.session_id[:8]}_{attempt}"
    target.mkdir(parents=True, exist_ok=False)
    artifact.save(target / f"{target.name}_ob3ect.json")
    _write_diagrams(artifact, target, target.name)
    session.artifact_path = str(target / f"{target.name}_ob3ect.json")
    session.record_path = target / "bridge_session.json"
    session.tool_return("artifact persisted", session.artifact_path)

async def generate_imscription(
    description: str,
    name: Optional[str],
    provider: str,
    model: Optional[str],
    delta_g: Optional[float],
    guided: bool,
    axiom_guided: bool,
    temperature: Optional[float],
    agent=None,
) -> ImscriptionGenerationResult:
    if agent is None:
        provider, model = resolve_bridge_route(provider, model)
        agent_config = bridge_agent_config(provider, model)
        agent_class = ImscriptionGeneratorAgent
        if axiom_guided:
            from imscribing_grammar.agents.axiom_guided_generator import AxiomGuidedGeneratorAgent
            agent_class = AxiomGuidedGeneratorAgent
        agent = agent_class(agent_config)
    
    if axiom_guided:
        from imscribing_grammar.agents.axiom_guided_generator import AxiomGuidedGeneratorAgent
        if not isinstance(agent, AxiomGuidedGeneratorAgent):
            raise ValueError("Axiom-guided continuation requires its starting agent")
        result = await agent.generate_validated_imscription(
            description, name=name, auto_register=False, temperature=temperature
        )
    elif guided:
        result = await agent.generate_guided(
            description, name=name, auto_register=False, temperature=temperature
        )
    else:
        result = await agent.generate_from_description(
            description, name=name, auto_register=False, temperature=temperature
        )
    
    if delta_g is not None:
        result.imscription.delta_g = delta_g
    
    return result

async def run_bridge(
    description: str,
    name: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    delta_g: Optional[float] = None,
    guided: bool = True,
    axiom_guided: bool = False,
    temperature: Optional[float] = None,
    domain_type: Optional[str] = None,
    context: Optional[str] = None,
    artifact_dir: Optional[Path] = None,
    display: Optional[BridgeDisplay] = None,
    reentry_rounds: int = 3,
    resume_session: Optional[Path] = None,
    execution_feedback: Optional[str] = None,
) -> BridgeResult:
    
    result = BridgeResult(description=description, imscription_name=name or "")
    
    display = display or BridgeDisplay()
    try:
        provider, model = resolve_bridge_route(provider, model)
        agent_config = bridge_agent_config(provider, model)
        agent_class = ImscriptionGeneratorAgent
        if axiom_guided:
            from imscribing_grammar.agents.axiom_guided_generator import AxiomGuidedGeneratorAgent
            agent_class = AxiomGuidedGeneratorAgent
        session = BridgeSession(agent_class(agent_config), display)
        session_bank = Path(artifact_dir or _OB3ECT_DIGITAL) / "resident_sessions"
        session_bank.mkdir(parents=True, exist_ok=True)
        restored = None
        if resume_session is not None:
            if not guided or axiom_guided:
                raise ValueError("Resident checkpoint restore currently requires the guided native gate")
            restored = json.loads(Path(resume_session).read_text())
            if restored["provider"] != agent_config.get("provider"):
                raise ValueError("Resident continuation must keep its source provider")
            if restored.get("model") != getattr(session.agent.provider, "model", None):
                raise ValueError("Resident continuation must keep its source model")
            if restored["agent_id"] != session.agent.agent_id or restored["reentry"]["subject"] != description:
                raise ValueError("Resident continuation belongs to another agent or subject")
            session.session_id = restored["session_id"]
            session.messages = restored["messages"]
            session.banked_inference = bool(restored.get('banked_inference', False))
            session.operations = restored["operations"]
            session.turn_count = sum(m["role"] == "assistant" for m in session.messages)
            session.reentry_state = restored["reentry"]
            session.record_path = Path(resume_session)
        else:
            session.record_path = session_bank / f"{session.session_id}.json"
        result.session_id = session.session_id
        result.operations = session.operations
        selected_model = (getattr(session.agent.provider, "model", None) or
                          getattr(session.agent.provider, "model_path", None) or agent_config.get("model"))
        display.heading(description, provider, selected_model, session.session_id)
        started = time.monotonic()
        with display.stage(1, "Restore retained imscription" if restored else "Generate imscription"):
            if restored:
                from imscribing_grammar.imscrbgrmr.models import Imscription
                from imscribing_grammar.agents.imscribe_generator_agent import validate_structural
                last = restored["reentry"]["rounds"][-1]
                entry = Imscription.from_dict({"name": name, "description": description,
                                              **parse_tuple_to_dict(restored["reentry"]["current_tuple"])})
                failures = validate_structural(entry)
                if (last["returned_grounding"] == "full") != (not failures):
                    raise ValueError("Restored Type no longer agrees with its native grounding receipt")
                imscription_result = ImscriptionGenerationResult(imscription=entry,
                    confidence=1.0, reasoning=last["returned_reasoning"],
                    grounding_status=last["returned_grounding"], failed_primitives=failures,
                    metadata={"restored_guided_gate": str(resume_session)})
                result.reentry = restored["reentry"]
                result.imscription_word = restored["reentry"]["rounds"][0]["type_word"]
                result.ob3ect_bootstrap_word = restored["reentry"]["continuation"]["previous_imasm_word"]
                persisted = [op["output"] for op in session.operations if op["operation"] == "artifact persisted"]
                if persisted:
                    result.artifact_path = session.artifact_path = persisted[-1]
                display.detail("Restored", f"{session.turn_count} model turns and {len(session.operations)} native returns")
            else:
                imscription_result = await generate_imscription(
                    description=description, name=name, provider=provider, model=model,
                    delta_g=delta_g, guided=guided, axiom_guided=axiom_guided,
                    temperature=temperature, agent=session.agent)
        if execution_feedback:
            session.tool_return("Executing folding return", execution_feedback)
        result.imscription_name = imscription_result.imscription.name
        result.imscription_tuple = parse_imscription_tuple(imscription_result)
        display.detail(result.imscription_name, result.imscription_tuple)
        display.detail("Generation", f"{session.turn_count} model turns · {time.monotonic() - started:.1f}s")
        
        from imscribing_grammar.ob3ect.auto import auto_design_reentrant

        def expand_types(tuple_text):
            return run_tuple_cycle(tuple_text, source_return=lambda output:
                                   session.tool_return("Expanded Lean Type sources", output),
                                   nesting_return=lambda record: session.tool_return(
                                       "Type nesting", json.dumps(record, ensure_ascii=False)))

        async def return_to_types(subject):
            return await generate_imscription(
                subject, result.imscription_name, provider, model, delta_g,
                guided, axiom_guided, temperature, agent=session.agent)

        def retain_artifact(artifact):
            persist_resident_artifact(artifact, session=session, description=description,
                                      name=result.imscription_name, artifact_dir=artifact_dir)
            # A later inference failure must return the last completed round.
            result.ob3ect_artifact = artifact
            result.artifact_path = session.artifact_path
            result.ob3ect_bootstrap_word = artifact.glyph_word
            result.reentry = artifact.reentry
            result.imscription_word = result.reentry["rounds"][0]["type_word"]

        with display.stage(2, "Re-enter Types and IMASM through auto.py"):
            artifact = await auto_design_reentrant(
                description, resident=session, gate_result=imscription_result,
                expand_types=expand_types, observe_word=run_imasm_cycle,
                return_to_types=return_to_types, name=result.imscription_name,
                domain_type=domain_type, context=context, max_rounds=reentry_rounds,
                on_artifact=retain_artifact,
                sequence_transform=lambda steps: nest_design_sequence(
                    steps, nesting_return=lambda record: session.tool_return(
                        "IMASM nesting", json.dumps(record, ensure_ascii=False))),
                logical_expressions=lambda tuple_text: navigator_logical_expressions(
                    tuple_text, result.imscription_name),
                resume_state=restored["reentry"] if restored else None)
        with display.stage(3, "Retain the coupled return"):
            result.ob3ect_artifact = artifact
            result.artifact_path = session.artifact_path
            result.ob3ect_bootstrap_word = artifact.glyph_word
            result.reentry = artifact.reentry
            result.imscription_word = result.reentry["rounds"][0]["type_word"]
            last = result.reentry["rounds"][-1]
            result.orbit_verification = {
                "type_facet": last["returned_type_observation"],
                "imasm_facet": last["imasm_observation"],
                "relation": verify_orbit_consistency(last["returned_type_observation"], last["imasm_observation"]),
                "requires_word_identity": False,
            }
            result.all_passed = result.reentry["status"] == "stable"
            if not result.all_passed:
                result.error = "Re-entry is held with its returned Type assignment, IMASM state and continuation"
            display.detail("Re-entry", result.reentry["status"])
            session.save()

    except Exception as e:
        result.error = str(e)
        if "session" in locals():
            result.reentry = getattr(session, "reentry_state", None)
            session.save()
        display.detail("Error", str(e))
        if display.verbose:
            display.console.print_exception(show_locals=False)
    
    return result

def _main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Bridge imscription generation with ob3ect artifact production",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 imscribe_ob3ect_bridge.py "carboxylic acid dimer" --provider deepseek --delta-g -52.0
  python3 imscribe_ob3ect_bridge.py "Kitaev chain" --provider groq --guided
  python3 imscribe_ob3ect_bridge.py "the muon" --provider openrouter --axiom-guided
        """
    )
    
    parser.add_argument("description", help="Natural language description of the entity")
    parser.add_argument("--name", "-n", help="Optional name for the imscription")
    parser.add_argument("--provider", "-p", default=None,
                        choices=sorted(_LOCAL_PROVIDERS | _API_PROVIDERS),
                        help="LLM provider (overrides inherited provider selection)")
    parser.add_argument("--model", "-m", default=None, help="Model ID (defaults to IG_MODEL)")
    parser.add_argument("--delta-g", type=float, help="Thermodynamic free energy (kJ/mol)")
    parser.add_argument("--guided", action="store_true", default=True, help="Guided generation (default)")
    parser.add_argument("--no-guided", dest="guided", action="store_false", help="Single-shot generation")
    parser.add_argument("--axiom-guided", action="store_true", help="Validate against 5 composition axioms")
    parser.add_argument("--temperature", "-t", type=float, help="Sampling temperature")
    parser.add_argument("--domain-type", choices=["computational", "biological", "alchemical", "mathematical"],
                        help="Domain hint for ob3ect generation")
    parser.add_argument("--context", type=Path, help="Path to context file/directory")
    parser.add_argument("--artifact-dir", type=Path, help="Artifact output directory")
    parser.add_argument("--output", "-o", type=Path, help="Output JSON file for bridge result")
    parser.add_argument("--reentry-rounds", type=int, default=3, help="Retained Type/IMASM rounds before returning a held continuation")
    parser.add_argument("--resume-session", type=Path, help="Continue the same resident from its retained native checkpoint")
    parser.add_argument("--execution-feedback", type=Path, help="Return an executing carrier observation into this resident")
    parser.add_argument("--verbose", action="store_true", help="Include exception tracebacks")
    parser.add_argument("--json", action="store_true", help="Print complete JSON to stdout; progress goes to stderr")
    
    args = parser.parse_args()
    
    context_text = None
    if args.context:
        if args.context.is_file():
            context_text = args.context.read_text(encoding="utf-8")
        elif args.context.is_dir():
            files = sorted(args.context.rglob("*"))
            chunks = []
            for f in files:
                if f.is_file() and f.suffix.lower() in {".md", ".txt", ".lean", ".py", ".tex", ".json"}:
                    try:
                        chunks.append(f"=== {f.name} ===\n{f.read_text(encoding='utf-8')}")
                    except Exception:
                        pass
            context_text = "\n\n".join(chunks)
    
    display = BridgeDisplay(verbose=args.verbose, stderr=args.json)
    result = asyncio.run(run_bridge(
        description=args.description,
        name=args.name,
        provider=args.provider,
        model=args.model,
        delta_g=args.delta_g,
        guided=args.guided,
        axiom_guided=args.axiom_guided,
        temperature=args.temperature,
        domain_type=args.domain_type,
        context=context_text,
        artifact_dir=args.artifact_dir,
        display=display,
        reentry_rounds=args.reentry_rounds,
        resume_session=args.resume_session,
        execution_feedback=args.execution_feedback.read_text() if args.execution_feedback else None,
    ))
    
    output_data = {
        "description": result.description,
        "session_id": result.session_id,
        "artifact_path": result.artifact_path,
        "operations": result.operations,
        "imscription_name": result.imscription_name,
        "imscription_tuple": result.imscription_tuple,
        "imscription_word": result.imscription_word,
        "ob3ect_bootstrap_word": result.ob3ect_bootstrap_word,
        "orbit_verification": result.orbit_verification,
        "reentry": result.reentry,
        "all_passed": result.all_passed,
        "error": result.error,
    }
    
    output_path = args.output
    if output_path is None:
        if result.artifact_path:
            output_path = Path(result.artifact_path).parent / "bridge_result.json"
        else:
            output_path = _PROJECT_ROOT / "measurements" / "bridge_resident_reentry_20261024" / f"{result.session_id or uuid.uuid4().hex}_result.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output_data, indent=2, ensure_ascii=False))
    if args.json:
        print(json.dumps(output_data, indent=2, ensure_ascii=False))
    else:
        display.finish(result, output_path)
    sys.exit(0 if result.all_passed else 1)

def main():
    with contextlib.redirect_stdout(SymbolOutput(sys.stdout)), \
         contextlib.redirect_stderr(SymbolOutput(sys.stderr)):
        _main()


if __name__ == "__main__":
    main()
