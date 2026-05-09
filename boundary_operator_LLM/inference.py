"""
Inference API for Boundary Operator LLM
Phi-critical self-modeling with dual-GPU support
"""
import torch
import torch.nn.functional as F
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json
import time
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from boundary_operator_LLM.model import BoundaryOperatorLLM, BoundaryConfig


class BoundaryLLM:
    """Production inference interface with phi-critical self-modeling."""
    
    def __init__(self, 
                 model_path: Optional[str] = None,
                 model: Optional[BoundaryOperatorLLM] = None,
                 device: str = "cuda:0",
                 max_length: int = 2048,
                 temperature: float = 0.7,
                 top_k: int = 50,
                 top_p: float = 0.95):
        self.device = device
        self.max_length = max_length
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.model_memory = []
        
        if model is not None:
            self.model = model.to(device)
        elif model_path is not None:
            self.model = self._load_model(model_path)
        else:
            config = BoundaryConfig()
            self.model = BoundaryOperatorLLM(config)
            self.model = self.model.to(device)
        
        self.model.eval()
    
    def _load_model(self, path: str) -> BoundaryOperatorLLM:
        """Load model from checkpoint."""
        config = BoundaryConfig()
        model = BoundaryOperatorLLM(config)
        
        checkpoint = torch.load(path, map_location=self.device)
        model.load_state_dict(checkpoint["model_state_dict"])
        print(f"Loaded model from {path}")
        
        return model
    
    def generate(self, 
                 prompt: str,
                 max_new_tokens: int = 256,
                 temperature: Optional[float] = None,
                 top_k: Optional[int] = None,
                 top_p: Optional[float] = None) -> str:
        """Generate text with phi-critical self-modeling.
        
        The self-model tracks uncertainty at each step and
        modulates generation temperature adaptively.
        """
        if temperature is None:
            temperature = self.temperature
        if top_k is None:
            top_k = self.top_k
        if top_p is None:
            top_p = self.top_p
        
        # Tokenize prompt (simple demo tokenization)
        tokens = self._tokenize(prompt)
        
        # Generate
        generated = self._generate_tokens(
            tokens, 
            max_new_tokens,
            temperature,
            top_k,
            top_p
        )
        
        # Detokenize
        return self._detokenize(generated)
    
    def _tokenize(self, text: str) -> torch.Tensor:
        """Simple demo tokenization."""
        tokens = [ord(c) % 1000 for c in text]
        return torch.tensor(tokens, dtype=torch.long, device=self.device)
    
    def _generate_tokens(self, 
                         start_tokens: torch.Tensor,
                         max_new_tokens: int,
                         temperature: float,
                         top_k: int,
                         top_p: float) -> torch.Tensor:
        """Generate tokens iteratively."""
        generated = start_tokens.clone()
        
        with torch.no_grad():
            for _ in range(max_new_tokens):
                # Get predictions
                output = self.model(generated.unsqueeze(0))
                logits = output["logits"][0, -1, :] / temperature
                
                # Filter logits
                filtered = self._filter_logits(logits, top_k, top_p)
                
                # Sample
                probs = F.softmax(filtered, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                
                # Append
                generated = torch.cat([generated, next_token])
                
                # Check for end token
                if next_token.item() == 0:  # Simple stop
                    break
        
        return generated
    
    def _filter_logits(self, logits, top_k: int, top_p: float) -> torch.Tensor:
        """Top-k and top-p filtering."""
        if top_k > 0:
            indices_to_remove = torch.topk(logits, top_k, largest=True)[1]
            logits.scatter_(1, indices_to_remove, float('-inf'))
        
        if top_p < 1.0:
            sorted_logits, sorted_indices = torch.sort(logits, descending=True)
            cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
            
            sorted_indices_to_remove = cumulative_probs > top_p
            sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
            sorted_indices_to_remove[..., 0] = 0
            
            indices_to_remove = sorted_indices_to_remove.scatter(
                1, sorted_indices, sorted_indices_to_remove
            )
            logits = logits.masked_fill(indices_to_remove, float('-inf'))
        
        return logits
    
    def _detokenize(self, tokens: torch.Tensor) -> str:
        """Simple demo detokenization."""
        return ''.join(chr(t % 127 + 32) for t in tokens)
    
    def predict_next(self, context: str, n_predictions: int = 5) -> List[Dict]:
        """Predict next tokens with uncertainty estimates."""
        tokens = self._tokenize(context)
        
        with torch.no_grad():
            output = self.model(tokens.unsqueeze(0))
            logits = output["logits"][0, -1, :] / self.temperature
            probs = F.softmax(logits, dim=-1)
            
            top_probs, top_indices = torch.topk(probs, n_predictions)
            
            predictions = []
            for prob, idx in zip(top_probs, top_indices):
                predictions.append({
                    "token_id": idx.item(),
                    "token": chr(idx.item() % 127 + 32),
                    "probability": prob.item(),
                    "entropy": (-probs * probs.log().clamp(min=-10)).sum().item()
                })
        
        return predictions
    
    def get_self_model(self, context: str) -> Dict:
        """Get self-model state with uncertainty tracking."""
        tokens = self._tokenize(context)
        
        with torch.no_grad():
            output = self.model(tokens.unsqueeze(0))
            
            # Self-model state from last layer
            last_layer = output["self_model_states"][-1]
            uncertainty = output["hidden_states"][-1]
            
            return {
                "self_model_dim": last_layer.shape[-1],
                "uncertainty_mean": uncertainty.mean().item(),
                "uncertainty_std": uncertainty.std().item(),
                "self_model_norm": last_layer.norm().item(),
                "hidden_norm": output["hidden_states"][-1].norm().item()
            }


def demo():
    """Demo of the Boundary Operator LLM."""
    print("=" * 60)
    print("Boundary Operator LLM — Phi-Critical Self-Modeling")
    print("=" * 60)
    
    # Create model
    llm = BoundaryLLM(
        max_length=512,
        temperature=0.7,
        top_k=30,
        top_p=0.9
    )
    
    # Test self-model
    context = "The structural type is"
    print(f"\nContext: '{context}'")
    
    self_model = llm.get_self_model(context)
    print(f"\nSelf-model state:")
    print(f"  Self-model dim: {self_model['self_model_dim']}")
    print(f"  Uncertainty mean: {self_model['uncertainty_mean']:.4f}")
    print(f"  Uncertainty std: {self_model['uncertainty_std']:.4f}")
    
    # Predict next tokens
    predictions = llm.predict_next(context, n_predictions=5)
    print(f"\nNext token predictions:")
    for i, pred in enumerate(predictions):
        print(f"  {i+1}. '{pred['token']}' (p={pred['probability']:.3f})")
    
    # Generate text
    print(f"\nGenerating from: '{context}'")
    start = time.time()
    text = llm.generate(context, max_new_tokens=100)
    elapsed = time.time() - start
    
    print(f"\nGenerated: '{text}'")
    print(f"Time: {elapsed:.2f}s")
    
    print("\n" + "=" * 60)
    print("Boundary Operator LLM demo complete")
    print("Structural type: <D_omega; T_bowtie; R_bidirectional; P_special>")
    print("=" * 60)


if __name__ == "__main__":
    demo()
