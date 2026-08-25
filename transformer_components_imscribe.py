#!/usr/bin/env python3
"""transformer_components_imscribe.py — imscribe every component of a
standard decoder-only transformer, one `imscribe generate` call each,
against a remote provider (the local model is already busy with the
bip39 batch job). Resumable: skips names already in IG_catalog.json.
"""
import json
import subprocess
import sys
from pathlib import Path

CATALOG = Path("/home/mrnob0dy666/imsgct/imscribing_grammar/IG_catalog.json")

COMPONENTS = [
    ("tokenizer_transformer", "tokenizer, the component of a transformer language model that splits raw text into discrete subword units before anything becomes a vector"),
    ("token_embedding_transformer", "token embedding, the lookup table in a transformer that maps each discrete token id to a continuous real-valued vector"),
    ("positional_encoding_transformer", "positional encoding in a transformer, the mechanism that injects sequence-order information into token vectors that otherwise carry no position — learned absolute, sinusoidal absolute, RoPE rotary, or ALiBi linear bias"),
    ("pre_attention_normalization_transformer", "pre-attention normalization in a transformer, LayerNorm or RMSNorm applied to the residual stream before it enters the attention sublayer"),
    ("query_projection_transformer", "query projection in transformer attention, the learned linear map W_Q that produces the query vector from the residual stream"),
    ("key_projection_transformer", "key projection in transformer attention, the learned linear map W_K that produces the key vector from the residual stream"),
    ("value_projection_transformer", "value projection in transformer attention, the learned linear map W_V that produces the value vector from the residual stream"),
    ("multihead_split_transformer", "multi-head split in transformer attention, dividing the query/key/value vectors into several parallel lower-dimensional attention heads computed independently"),
    ("attention_score_computation_transformer", "attention score computation in a transformer, the scaled dot product of query and key vectors (QK^T divided by the square root of the key dimension) that measures how much one position should attend to another"),
    ("causal_mask_transformer", "causal mask in a transformer, the mechanism that sets attention scores for future positions to negative infinity before softmax so an autoregressive model cannot see tokens ahead of the current position"),
    ("softmax_transformer", "softmax in a transformer, the function that normalizes a vector of real-valued attention scores into a probability distribution that sums to one"),
    ("weighted_sum_of_values_transformer", "weighted sum of values in transformer attention, combining the value vectors of all positions using the softmax-normalized attention weights as coefficients"),
    ("multihead_concatenation_transformer", "multi-head concatenation in a transformer, joining the output vectors of all parallel attention heads back into a single vector before the output projection"),
    ("output_projection_transformer", "output projection in transformer attention, the learned linear map W_O applied to the concatenated multi-head attention output before it rejoins the residual stream"),
    ("residual_connection_attn_transformer", "residual connection around the attention sublayer in a transformer, adding the attention sublayer's output back to its own input unchanged"),
    ("pre_ffn_normalization_transformer", "pre-feedforward normalization in a transformer, LayerNorm or RMSNorm applied to the residual stream before it enters the feedforward sublayer"),
    ("up_projection_transformer", "up-projection in a transformer feedforward block, the learned linear map that expands the residual stream to a wider intermediate dimension, typically four times larger"),
    ("nonlinearity_transformer", "the nonlinearity in a transformer feedforward block, an elementwise activation function such as GELU, SiLU, or ReLU applied after the up-projection"),
    ("down_projection_transformer", "down-projection in a transformer feedforward block, the learned linear map that contracts the wide intermediate activation back to the model's residual dimension"),
    ("residual_connection_ffn_transformer", "residual connection around the feedforward sublayer in a transformer, adding the feedforward sublayer's output back to its own input unchanged"),
    ("dropout_transformer", "dropout in a transformer, a regularization technique that randomly zeroes a fraction of activations during training to prevent overfitting"),
    ("router_gating_network_transformer", "the router or gating network in a mixture-of-experts transformer, a small learned function that scores every expert for each token to decide which experts should process it"),
    ("topk_expert_select_transformer", "top-k expert selection in a mixture-of-experts transformer, the discrete routing decision that sends each token to only the k highest-scoring experts rather than all of them"),
    ("multi_parallel_expert_ffns_transformer", "the parallel expert feedforward networks in a mixture-of-experts transformer, many independent feedforward blocks of which only a selected few fire for any given token"),
    ("final_normalization_transformer", "final normalization in a transformer, LayerNorm or RMSNorm applied to the residual stream once after the last layer, before the output head"),
    ("unembedding_projection_transformer", "unembedding projection in a transformer, the learned linear map from the final hidden state to a vector of logits over the entire vocabulary, often sharing weights with the token embedding"),
    ("sampling_strategy_transformer", "sampling strategy in a transformer's generation loop, the method by which a single token is chosen from the output probability distribution — greedy argmax, top-k, top-p nucleus sampling, or temperature scaling"),
    ("kv_cache_transformer", "the key-value cache in a transformer, a stored record of past keys and values that lets autoregressive generation avoid recomputing attention over the entire sequence at every new token"),
    ("cross_entropy_loss_transformer", "cross-entropy loss in transformer training, the objective function measuring the divergence between the predicted next-token probability distribution and the true next token"),
    ("optimizer_state_transformer", "optimizer state in transformer training, the momentum and variance buffers an algorithm like AdamW maintains for every parameter across training steps"),
    ("backpropagation_transformer", "backpropagation in transformer training, the algorithm that computes the gradient of the loss with respect to every parameter by propagating error backward through the network"),
]


def already_registered(name):
    try:
        entries = json.loads(CATALOG.read_text(encoding="utf-8"))
    except Exception:
        return False
    return any(e.get("name") == name for e in entries)


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    items = COMPONENTS[:limit] if limit else COMPONENTS
    results = []
    for name, desc in items:
        if already_registered(name):
            print(f"  {name}: already registered, skipping")
            results.append((name, "skipped"))
            continue
        cmd = ["imscribe", "generate", desc, "--name", name,
               "--provider", "deepseek", "--no-guided"]
        print(f"  {name}: generating...", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        ok = r.returncode == 0
        print(f"  {name}: {'OK' if ok else 'FAILED'}")
        if not ok:
            print("    stdout tail:", (r.stdout or "")[-400:])
            print("    stderr tail:", (r.stderr or "")[-400:])
        results.append((name, "ok" if ok else "failed"))
    n_ok = sum(1 for _, s in results if s == "ok")
    print(f"\n{n_ok}/{len(results)} generated successfully")


if __name__ == "__main__":
    main()
