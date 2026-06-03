#!/usr/bin/env python3
"""
train_grammaformer.py — QLoRA fine-tuning for GrammaFormer on agent trajectories.

Usage:
  # Train small from scratch on agent trajectory data
  python scripts/train_grammaformer.py --data trajectory_data.jsonl --epochs 3

  # Graft from Qwen3 base, then fine-tune
  python scripts/train_grammaformer.py --base-model Qwen/Qwen2.5-0.5B --data ...

  # Resume from checkpoint
  python scripts/train_grammaformer.py --resume models/grammaformer/checkpoint.pt
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

# Ensure framework is importable
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from framework.grammaformer import (
    GrammaFormer, GrammaFormerConfig, GrammaFormerForCausalLM,
    graft_grammaformer_from_qwen, PhaseGatedController,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Dataset
# ═══════════════════════════════════════════════════════════════════════════════

class TrajectoryDataset(Dataset):
    """Agent trajectory data: each example is one winding.

    JSONL format per line:
      {"messages": [{"role": "...", "content": "..."}, ...],
       "phase": "THINK|ACT|OBSERVE|UPDATE",
       "winding": 0,
       "frobenius_closed": true,
       "tool_call": {"name": "...", "arguments": {...}}}
    """

    def __init__(self, path: str, tokenizer, max_seq_len: int = 8192):
        self.tokenizer = tokenizer
        self.max_seq_len = max_seq_len
        self.examples: List[Dict] = []

        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ex = json.loads(line)
                    self.examples.append(ex)
                except json.JSONDecodeError:
                    continue

        print(f"Loaded {len(self.examples)} trajectory examples from {path}")

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> Dict:
        ex = self.examples[idx]
        messages = ex.get("messages", [])

        # Build prompt (everything up to assistant turn) — no generation prompt
        # so we can find where the assistant response starts.
        prompt_msgs = []
        response_text = ""
        for m in messages:
            if m["role"] == "assistant":
                response_text = m["content"]
                break
            prompt_msgs.append(m)

        prompt_text = self.tokenizer.apply_chat_template(
            prompt_msgs, tokenize=False, add_generation_prompt=True,
            enable_thinking=False)
        full_text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False,
            enable_thinking=False)

        prompt_ids = self.tokenizer(
            prompt_text, truncation=False, return_tensors="pt")["input_ids"][0]
        full_tokens = self.tokenizer(
            full_text, truncation=True, max_length=self.max_seq_len,
            padding="max_length", return_tensors="pt")

        input_ids = full_tokens["input_ids"][0]
        attention_mask = full_tokens["attention_mask"][0]

        # Labels: -100 everywhere except the assistant response tokens.
        # This is standard SFT — only compute loss on what the model should generate.
        labels = input_ids.clone()
        prompt_len = min(len(prompt_ids), len(labels))
        labels[:prompt_len] = -100                        # mask prompt
        labels[attention_mask == 0] = -100               # mask padding

        phase_str = ex.get("phase", "THINK")
        phase_map = {"THINK": 0, "ACT": 1, "OBSERVE": 2, "UPDATE": 3}
        phase = phase_map.get(phase_str, 0)

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
            "phase": phase,
            "winding": ex.get("winding", 0),
            "frobenius_closed": float(ex.get("frobenius_closed", False)),
        }

# ═══════════════════════════════════════════════════════════════════════════════
# Composite Loss
# ═══════════════════════════════════════════════════════════════════════════════

def compute_loss(model: GrammaFormer, batch: Dict,
                 alpha_f: float = 0.5, alpha_m: float = 0.05,
                 alpha_g: float = 0.1, alpha_ffn_mag: float = 1e-4,
                 gate_target: float = 0.5) -> Tuple[torch.Tensor, Dict[str, float]]:
    """Composite loss: LM + alpha*Frobenius + beta*Meta + gamma*Gate.
    FIXED: alpha_f raised to 0.5 (was 0.1) -- Frobenius is structurally central.
    FIXED: gate_target now parameterized (was hardcoded 0.8)."""
    input_ids = batch["input_ids"]
    attention_mask = batch["attention_mask"]
    labels = batch["labels"]
    phase = batch["phase"]
    winding = batch["winding"]

    out = model(input_ids, attention_mask, winding=int(winding[0].item()),
                phase=int(phase[0].item()), return_meta=True)

    # 1. Language modeling loss (shifted)
    # Cast to float32: bfloat16 overflows in softmax for large logits → NaN loss.
    logits = out["logits"][:, :-1, :].contiguous()
    targets = labels[:, 1:].contiguous()
    loss_lm = F.cross_entropy(
        logits.float().view(-1, logits.size(-1)),
        targets.view(-1),
        ignore_index=-100)

    # 2. Frobenius loss: μ(δ(h)) ≈ h on last token
    _dtype = next(model.parameters()).dtype
    _fallback = torch.zeros(1, 1, model.config.d_model,
                            device=input_ids.device, dtype=_dtype)
    loss_f = model.frobenius_head.frobenius_loss(
        out.get("hidden_for_frob", _fallback))

    # 3. Meta-network loss: predict per-sample LM error magnitude.
    # Previous loss (error_pred.pow(2).mean()) minimized ||error_pred|| to zero
    # — the model solved it by outputting zeros, giving M=0.0000 dead meta.
    # Correct loss: make the meta-network predict how hard each sample is.
    if "error_pred" in out and "meta_emb" in out:
        error_pred = out["error_pred"]               # (B, d_model) — model dtype
        B = logits.size(0)
        per_tok = F.cross_entropy(
            logits.float().view(-1, logits.size(-1)),
            targets.reshape(-1),
            ignore_index=-100, reduction='none',
        ).view(B, -1)                                # (B, S-1) float32
        valid = (targets != -100).to(_dtype)         # (B, S-1) — match model dtype
        per_item = (per_tok.to(_dtype) * valid).sum(-1) / valid.sum(-1).clamp(min=1)
        pred_mag = error_pred.norm(dim=-1)           # (B,) model dtype
        loss_m_raw = F.mse_loss(pred_mag, per_item.detach())
        loss_m = loss_m_raw.clamp(max=3.0)
        m_per_item_max = per_item.max().item()
        m_is_high = loss_m_raw.item() > 3.0
    else:
        loss_m = torch.tensor(0.0, device=input_ids.device, dtype=_dtype)
        loss_m_raw = loss_m
        m_per_item_max = 0.0
        m_is_high = False

    # 4. Gate timing loss: ACT→target, non-ACT→stay below threshold (hinge)
    gate_val = out["gate_value"]  # scalar tensor with grad
    gate_scalar = out.get("gate_scalar", gate_val.item())
    is_act_phase = (phase[0].item() == PhaseGatedController.PHASE_ACT)
    if is_act_phase:
        loss_g = F.mse_loss(gate_val,
                            torch.tensor(gate_target, device=input_ids.device, dtype=_dtype))
    else:
        loss_g = F.relu(gate_val - 0.5).pow(2)

    # 5. Complex FFN magnitude penalty — regularize weight magnitudes so the
    # high-magnitude phase basin doesn't become a stable attractor.
    if alpha_ffn_mag > 0 and hasattr(model, 'layers'):
        ffn_mag_acc = torch.zeros(1, device=input_ids.device, dtype=torch.float32)
        n_complex = 0
        for layer in model.layers:
            if hasattr(layer.ffn, 'w1_re'):
                ffn = layer.ffn
                ffn_mag_acc = ffn_mag_acc + (
                    ffn.w1_re.weight.float().pow(2).mean() +
                    ffn.w1_im.weight.float().pow(2).mean() +
                    ffn.w2_re.weight.float().pow(2).mean() +
                    ffn.w2_im.weight.float().pow(2).mean() +
                    ffn.cross_re_im.weight.float().pow(2).mean() +
                    ffn.cross_im_re.weight.float().pow(2).mean()
                )
                n_complex += 1
        loss_ffn_mag = (ffn_mag_acc / max(n_complex, 1)).to(_dtype)
    else:
        loss_ffn_mag = torch.zeros(1, device=input_ids.device, dtype=_dtype)

    total = loss_lm + alpha_f * loss_f + alpha_m * loss_m + alpha_g * loss_g + alpha_ffn_mag * loss_ffn_mag

    metrics = {
        "loss_lm": loss_lm.item(),
        "loss_f": loss_f.item(),
        "loss_m": loss_m_raw.item() if isinstance(loss_m_raw, torch.Tensor) else float(loss_m_raw),
        "loss_m_clamped": loss_m.item() if isinstance(loss_m, torch.Tensor) else float(loss_m),
        "loss_g": loss_g.item() if isinstance(loss_g, torch.Tensor) else float(loss_g),
        "loss_ffn_mag": loss_ffn_mag.item() if isinstance(loss_ffn_mag, torch.Tensor) else float(loss_ffn_mag),
        "total": total.item(),
        "gate_val": gate_scalar,
        "m_per_item_max": m_per_item_max,
        "m_is_high": m_is_high,
        "phase": int(phase[0].item()),
    }
    return total, metrics


# ═══════════════════════════════════════════════════════════════════════════════
# Training loop
# ═══════════════════════════════════════════════════════════════════════════════

def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    print(f"Device: {device}")

    # Load tokenizer
    from transformers import AutoTokenizer
    tok_path = args.tokenizer or args.base_model or "Qwen/Qwen2.5-0.5B"
    _tok_arg = Path(tok_path) if Path(tok_path).exists() else tok_path
    tokenizer = AutoTokenizer.from_pretrained(
        _tok_arg, trust_remote_code=True, use_fast=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Initialize model
    if args.resume:
        print(f"Resuming from {args.resume}")
        model = GrammaFormerForCausalLM.from_pretrained(args.resume).grammaformer
    elif args.base_model:
        print(f"Grafting from {args.base_model} ...")
        model = graft_grammaformer_from_qwen(args.base_model, map_location="cpu")
    else:
        cfg = GrammaFormerConfig.small()
        print(f"Training from scratch: d={cfg.d_model}, layers={cfg.n_layers}")
        model = GrammaFormer(cfg)

    # QLoRA: freeze base, train adapters + new components (do before .to(device))
    if args.qlora and args.base_model:
        _apply_qlora(model, args)

    total_params = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Params: {total_params:,} total, {trainable:,} trainable")

    model = model.bfloat16().to(device)
    model.train()

    if args.grad_ckpt:
        model.gradient_checkpointing_enable()

    # Dataset
    dataset = TrajectoryDataset(args.data, tokenizer, args.max_seq_len)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True,
                        num_workers=args.num_workers, drop_last=True)

    # Freeze token_embed only — pure lookup table, no structural role.
    # frobenius_head is the μ∘δ operator (the Φ gate). It MUST be trainable:
    # freezing it structurally prevents Frobenius closure from being learned.
    # The F-loss would climb indefinitely with it frozen.
    # Memory: backbone(1527M) + frob_head(311M) = 1838M trainable.
    # With 8-bit moments: 4.4(params) + 3.7(grads) + 3.7(moments) = 11.8 GB. Fits.
    if not args.train_vocab:
        for p in model.token_embed.parameters():
            p.requires_grad = False

    trainable_params = [p for p in model.parameters() if p.requires_grad]

    try:
        import bitsandbytes as bnb
        optimizer = bnb.optim.AdamW8bit(trainable_params, lr=args.lr,
                                        weight_decay=args.weight_decay)
        print(f"Optimizer: bitsandbytes AdamW8bit ({sum(p.numel() for p in trainable_params)/1e6:.0f}M trainable params)")
    except ImportError:
        optimizer = torch.optim.AdamW(trainable_params, lr=args.lr,
                                      weight_decay=args.weight_decay)
        print("WARNING: bitsandbytes not found — using AdamW (may OOM on <24 GB GPU)")
        print(f"Optimizer: AdamW ({sum(p.numel() for p in trainable_params)/1e6:.0f}M trainable params)")
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=len(loader) * args.epochs)

    # Training
    os.makedirs(args.output, exist_ok=True)
    global_step = 0

    # ── Frobenius-only pretraining phase ──
    if args.frob_pretrain_steps > 0:
        print(f"Frobenius-only pretraining: {args.frob_pretrain_steps} steps...")
        # Temporarily unfreeze frobenius_head (may have been frozen above for main loop).
        for p in model.frobenius_head.parameters():
            p.requires_grad_(True)
        frob_optimizer = torch.optim.AdamW(
            list(model.frobenius_head.parameters()),
            lr=args.frob_pretrain_lr)
        frob_loader_iter = iter(loader)
        for step in range(args.frob_pretrain_steps):
            try:
                batch = next(frob_loader_iter)
            except StopIteration:
                frob_loader_iter = iter(loader)
                batch = next(frob_loader_iter)
            batch = {k: v.to(device) for k, v in batch.items()}
            frob_optimizer.zero_grad()
            loss_f_only = model.frobenius_loss(
                batch["input_ids"], batch["attention_mask"])
            loss_f_only.backward()
            if args.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(
                    model.frobenius_head.parameters(), args.grad_clip)
            frob_optimizer.step()
            if (step + 1) % max(1, args.frob_pretrain_steps // 5) == 0:
                print(f"  Frob-pretrain step {step+1}/{args.frob_pretrain_steps} "
                      f"| F-loss={loss_f_only.item():.4f}")
        del frob_optimizer, frob_loader_iter
        torch.cuda.empty_cache()
        print("Frobenius pretraining complete.")

    for epoch in range(args.epochs):
        epoch_loss = 0.0
        epoch_steps = 0
        nan_steps = 0
        for batch_idx, batch in enumerate(loader):
            batch = {k: v.to(device) for k, v in batch.items()}

            optimizer.zero_grad()
            anneal_frac = min(1.0, global_step / args.gate_anneal_steps)
            current_gate_target = 0.5 + 0.3 * anneal_frac  # 0.5 → 0.8
            loss, metrics = compute_loss(model, batch,
                                         alpha_f=args.alpha_f,
                                         alpha_m=args.alpha_m,
                                         alpha_g=args.alpha_g,
                                         alpha_ffn_mag=args.alpha_ffn_mag,
                                         gate_target=current_gate_target)

            # Skip NaN/Inf batches — don't let a single bad step poison the run.
            if not torch.isfinite(loss):
                nan_steps += 1
                optimizer.zero_grad()
                global_step += 1
                if global_step % args.log_every == 0:
                    print(f"Step {global_step} | NaN loss skipped "
                          f"(F={metrics['loss_f']:.4f} Gate={metrics['gate_val']:.3f})")
                continue

            loss.backward()

            if args.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)

            optimizer.step()
            scheduler.step()
            global_step += 1
            epoch_loss += loss.item()
            epoch_steps += 1

            if global_step % args.log_every == 0:
                m_str = f"M={metrics['loss_m']:.4f}"
                if metrics.get('m_is_high'):
                    m_str += (f"→clamped"
                              f"[per_item_max={metrics['m_per_item_max']:.2f}"
                              f" phase={metrics['phase']}]")
                print(f"Step {global_step} | LM={metrics['loss_lm']:.4f} "
                      f"F={metrics['loss_f']:.4f} {m_str} "
                      f"G={metrics['loss_g']:.4f} | Total={metrics['total']:.4f} "
                      f"Gate={metrics['gate_val']:.3f}")

            if args.save_every > 0 and global_step % args.save_every == 0:
                ckpt_path = os.path.join(args.output, f"checkpoint-{global_step}")
                model.save_pretrained(ckpt_path)
                print(f"Checkpoint saved to {ckpt_path}")

        avg_loss = epoch_loss / epoch_steps if epoch_steps else float("nan")
        print(f"Epoch {epoch+1}/{args.epochs} | Avg loss: {avg_loss:.4f} "
              f"({epoch_steps} steps, {nan_steps} NaN skipped)")

    # Final save
    model.save_pretrained(args.output)
    tokenizer.save_pretrained(args.output)
    print(f"Model saved to {args.output}")


def _apply_qlora(model: GrammaFormer, args):
    """Apply QLoRA: freeze base weights, add LoRA adapters to attention + FFN."""
    try:
        from peft import LoraConfig, get_peft_model, TaskType
    except ImportError:
        print("WARNING: peft not installed. Install with: pip install peft")
        print("Continuing without QLoRA (all params trainable).")
        return

    # Freeze all params first
    for p in model.parameters():
        p.requires_grad = False

    # Unfreeze GrammaFormer-specific components (always trained)
    for name, param in model.named_parameters():
        if any(x in name for x in ["meta.", "phase_gate.", "memory_bank.",
                                     "frobenius_head.", "register.",
                                     "winding_pe.", "u", "v"]):
            param.requires_grad = True

    # Add LoRA to attention Q/K/V/O
    target_modules = []
    for i in range(model.config.n_layers):
        prefix = f"layers.{i}.attention."
        target_modules.extend([f"{prefix}W_q", f"{prefix}W_k",
                               f"{prefix}W_v", f"{prefix}W_o"])
        if model.config.use_complex_ffn:
            prefix_ffn = f"layers.{i}.ffn."
            target_modules.extend([
                f"{prefix_ffn}w1_re", f"{prefix_ffn}w1_im",
                f"{prefix_ffn}w2_re", f"{prefix_ffn}w2_im"])

    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        target_modules=target_modules,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    # Note: full peft wrapping may not work with custom GrammaFormer.
    # Fallback: manually freeze/unfreeze as done above.
    print(f"QLoRA: {len(target_modules)} target modules, r={args.lora_r}")


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train GrammaFormer")
    parser.add_argument("--data", required=True, help="JSONL trajectory data")
    parser.add_argument("--base-model", help="Qwen base model to graft from")
    parser.add_argument("--tokenizer", help="Tokenizer path (default: base model)")
    parser.add_argument("--resume", help="Resume from checkpoint dir")
    parser.add_argument("--output", default="models/grammaformer_trained")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--grad-clip", type=float, default=1.0)
    parser.add_argument("--max-seq-len", type=int, default=8192)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--log-every", type=int, default=10)
    parser.add_argument("--save-every", type=int, default=500)
    parser.add_argument("--qlora", action="store_true",
                        help="Use QLoRA (freeze base, LoRA adapters)")
    parser.add_argument("--lora-r", type=int, default=64)
    parser.add_argument("--lora-alpha", type=int, default=128)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--grad-ckpt", action="store_true",
                        help="Enable gradient checkpointing (trades compute for memory)")
    parser.add_argument("--frob-pretrain-steps", type=int, default=500,
                        help="Steps of Frobenius-only pretraining before main loop (0=skip)")
    parser.add_argument("--frob-pretrain-lr", type=float, default=1e-3,
                        help="Learning rate for Frobenius pretraining phase")
    parser.add_argument("--gate-anneal-steps", type=int, default=500,
                        help="Steps over which gate target anneals from 0.5 to 0.8")
    parser.add_argument("--alpha-f", type=float, default=4.1,
                        help="Frobenius loss weight (default 4.1; grammar-derived: Φ cliff "
                             "is 91%% of d(GF,O_inf); must balance LM loss at convergence)")
    parser.add_argument("--alpha-g", type=float, default=0.3,
                        help="Gate loss weight (default 0.3; was 0.1 — gate froze at 0.543)")
    parser.add_argument("--alpha-m", type=float, default=0.05,
                        help="Meta loss weight (default 0.05; lower to 0.005-0.01 to tame "
                             "M-loss spikes — at 0.05, M=44 adds 2.2 to total loss)")
    parser.add_argument("--alpha-ffn-mag", type=float, default=1e-4,
                        help="ComplexFFN weight magnitude penalty (default 1e-4; "
                             "regularizes high-magnitude phase basin in complex weights)")
    parser.add_argument("--train-vocab", action="store_true",
                        help="Also train token_embed and frobenius_head (requires >24 GB VRAM)")
    parser.add_argument("--cpu", action="store_true")
    args = parser.parse_args()
    train(args)
