"""
Training script for Boundary Operator LLM
Structurally optimized for the Imscribing Grammar
"""
import torch
import torch.nn as nn
from pathlib import Path
import json
import time
import argparse
from dataclasses import asdict

# Add parent to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the model
from boundary_operator_LLM.model import BoundaryOperatorLLM, BoundaryConfig


# Which card this run owns comes from IG_DEVICES, the one spelling for device
# selection across every repo here (see framework/ig_devices.py).
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent.parent))
from framework.ig_devices import torch_device as _ig_torch_device

class TrainingConfig:
    """Training configuration with properties."""
    def __init__(self):
        # Data
        self.dataset_path = "./data/structure_corpus.jsonl"
        self.batch_size = 8
        self.gradient_accumulation_steps = 4
        self.max_seq_len = 2048
        
        # Optimization
        self.max_epochs = 100
        self.max_steps = 10000
        self.warmup_steps = 1000
        self.learning_rate = 2e-4
        self.weight_decay = 0.1
        self.beta1 = 0.9
        self.beta2 = 0.95
        
        # Regularization
        self.dropout = 0.1
        self.label_smoothing = 0.1
        
        # Output
        self.output_dir = "./output"
        self.save_every = 500
        self.eval_every = 100
        
        # Precision
        self.mixed_precision = True
        self.device = str(_ig_torch_device())


class StructureDataset:
    """Dataset of structural descriptions for pretraining."""
    def __init__(self, filepath: str, vocab_size: int = 32000, max_seq_len: int = 2048):
        self.filepath = filepath
        self.max_seq_len = max_seq_len
        self.texts = self._load_corpus()
        print(f"Loaded {len(self.texts)} documents")
    
    def _load_corpus(self):
        """Load or generate structural corpus."""
        try:
            with open(self.filepath, 'r') as f:
                texts = [line.strip() for line in f if line.strip()]
            return texts
        except FileNotFoundError:
            # Generate synthetic structural corpus for testing
            print("No corpus found, generating synthetic structural corpus...")
            return self._generate_structural_corpus()
    
    def _generate_structural_corpus(self, n_docs: int = 1000) -> list:
        """Generate synthetic structural descriptions."""
        templates = [
            "The {system} operates at {D} dimensional space with {T} topology and {R} coupling.",
            "Type: {D}={D_val}, {T}={T_val}, {R}={R_val}, {P}={P_val}",
            "The {name} has {dim} dimensions and {layers} layers with {heads} attention heads.",
            "Criticality at {phi} with winding number {omega} and chirality {H}.",
            "The system exhibits {K} kinetics with {Gamma} global interaction.",
        ]
        
        systems = ["neural_net", "transformer", "MoE", "RNN", "attention", "memory", "embedding"]
        D_vals = ["D_omega", "D_infinity", "D_triangle", "D_wedge"]
        T_vals = ["T_net", "T_bowtie", "T_boxtimes", "T_inclusion"]
        R_vals = ["R_sup", "R_cat", "R_dagger", "R_bidirectional"]
        P_vals = ["P_asym", "P_psi", "P_pm", "P_sym", "P_special"]
        
        corpus = []
        for _ in range(n_docs):
            text = f"Structural configuration: "
            text += f"D={D_vals[_ % len(D_vals)]}, "
            text += f"T={T_vals[_ % len(T_vals)]}, "
            text += f"R={R_vals[_ % len(R_vals)]}, "
            text += f"P={P_vals[_ % len(P_vals)]}, "
            text += f"Phi={P_vals[(_+1) % len(P_vals)]}, "
            text += f"H={(_ % 4)}"
            corpus.append(text)
        
        # Save to file
        Path(self.filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, 'w') as f:
            for text in corpus:
                f.write(text + '\n')
        
        print(f"Generated {len(corpus)} synthetic documents")
        return corpus
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        # Simple tokenization for demo
        tokens = [ord(c) % 1000 for c in text]
        # Pad/truncate to max_seq_len
        if len(tokens) < self.max_seq_len:
            tokens += [0] * (self.max_seq_len - len(tokens))
        else:
            tokens = tokens[:self.max_seq_len]
        
        return torch.tensor(tokens[:self.max_seq_len-1]), torch.tensor(tokens[1:])


def train_model(
    model: BoundaryOperatorLLM,
    train_config: TrainingConfig,
    train_dataset: StructureDataset
):
    """Training loop for the boundary operator LLM."""
    device = train_config.device
    
    # Move model to device
    model.to(device)
    
    # Optimizer
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=train_config.learning_rate,
        betas=(train_config.beta1, train_config.beta2),
        weight_decay=train_config.weight_decay
    )
    
    # Scheduler
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer,
        max_lr=train_config.learning_rate,
        total_steps=train_config.max_steps,
        pct_start=0.1
    )
    
    # Mixed precision
    scaler = torch.cuda.amp.GradScaler(enabled=train_config.mixed_precision)
    
    # Training loop
    model.train()
    total_loss = 0
    start_time = time.time()
    
    for step in range(train_config.max_steps):
        # Get batch
        input_ids, labels = next(iter(train_dataset))
        input_ids = input_ids.unsqueeze(0).to(device)
        labels = labels.unsqueeze(0).to(device)
        
        # Forward pass
        optimizer.zero_grad()
        
        with torch.cuda.amp.autocast(enabled=train_config.mixed_precision):
            output = model(input_ids)
            logits = output["logits"].view(-1, model.config.vocab_size)
            loss = torch.nn.functional.cross_entropy(
                logits, labels.view(-1),
                ignore_index=0,
                label_smoothing=train_config.label_smoothing
            )
        
        # Backward pass
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(optimizer)
        scaler.update()
        scheduler.step()
        
        total_loss += loss.item()
        
        if step % 100 == 0:
            avg_loss = total_loss / 100
            elapsed = time.time() - start_time
            print(f"Step {step}: loss={avg_loss:.4f}, lr={scheduler.get_last_lr()[0]:.2e}, time={elapsed:.2f}s")
            total_loss = 0
        
        # Save checkpoint
        if step % train_config.save_every == 0 and step > 0:
            save_checkpoint(model, optimizer, step)
        
        # Evaluation
        if step % train_config.eval_every == 0 and step > 0:
            eval_loss = evaluate(model, train_dataset, device)
            print(f"Step {step}: eval_loss={eval_loss:.4f}")


def save_checkpoint(model, optimizer, step):
    """Save model checkpoint."""
    output_dir = Path("./output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    checkpoint = {
        "step": step,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
    }
    
    # Save on device 0
    torch.save(checkpoint, output_dir / f"checkpoint_step_{step}.pt")
    print(f"Saved checkpoint at step {step}")


def evaluate(model, dataset, device):
    """Evaluate model on dataset."""
    model.eval()
    total_loss = 0
    n_samples = 0
    
    with torch.no_grad():
        for i in range(min(10, len(dataset))):
            input_ids, labels = dataset[i]
            input_ids = input_ids.unsqueeze(0).to(device)
            labels = labels.unsqueeze(0).to(device)
            
            output = model(input_ids)
            logits = output["logits"].view(-1, model.config.vocab_size)
            loss = torch.nn.functional.cross_entropy(
                logits, labels.view(-1),
                ignore_index=0
            )
            total_loss += loss.item()
            n_samples += 1
    
    model.train()
    return total_loss / max(n_samples, 1)


def main():
    parser = argparse.ArgumentParser(description="Train Boundary Operator LLM")
    parser.add_argument("--max_steps", type=int, default=1000)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--output_dir", type=str, default="./output")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Boundary Operator LLM Training")
    print("=" * 60)
    
    # Create config
    train_config = TrainingConfig()
    train_config.max_steps = args.max_steps
    
    # Create model
    model_config = BoundaryConfig()
    print(f"Model config: {json.dumps(asdict(model_config), indent=2)}")
    
    model = BoundaryOperatorLLM(model_config)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total parameters: {total_params:,}")
    
    # Create dataset
    dataset = StructureDataset(train_config.dataset_path)
    
    # Start training
    print("\nStarting training...")
    train_model(model, train_config, dataset)
    
    print("\n✓ Training complete")


if __name__ == "__main__":
    main()
