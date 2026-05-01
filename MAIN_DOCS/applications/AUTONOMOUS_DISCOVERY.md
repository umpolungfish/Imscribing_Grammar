# Autonomous Synthon Discovery Agent

## Overview

The `AutonomousSynthonDiscoveryAgent` is a self-directed agent that continuously:
1. **Proposes** novel synthons based on chemical space exploration
2. **Validates** against existing catalog and literature
3. **Registers** valid synthons to the global catalog
4. **Repeats** until configured limits are reached

## Quick Start

### CLI Usage

```bash
# Run 10 discovery cycles (default)
imscribe agents discover

# Run 50 cycles or 2 hours
imscribe agents discover --cycles 50 --duration 120

# Focus on specific chemistry
imscribe agents discover --focus "hydrogen bonding" --cycles 20

# Use different provider
imscribe agents discover --provider qwen --cycles 100

# Lower confidence threshold for more discoveries
imscribe agents discover --confidence 0.6 --cycles 30
```

### Python API

```python
import asyncio
from agents.autonomous_synthon_discovery_agent import (
    AutonomousSynthonDiscoveryAgent,
    AutonomousRunConfig,
    run_autonomous_discovery,
)
from imscrbgrmr.provider_config import build_agent_config

# Method 1: Convenience function
results = await run_autonomous_discovery(
    max_cycles=50,
    max_minutes=60,
    provider="anthropic",
    focus="catalysis",
)

# Method 2: Full control
config = build_agent_config(provider="anthropic", model=None)
agent = AutonomousSynthonDiscoveryAgent(config)

run_config = AutonomousRunConfig(
    max_cycles=100,
    max_duration_minutes=120,
    min_confidence_threshold=0.7,
    target_domains=["molecular", "supramolecular"],
    focus_areas=["halogen bonding", "chalcogen bonding"],
    save_interval=10,
)

results = await agent.run_autonomous(run_config)
```

## Configuration Options

### AutonomousRunConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_cycles` | int | 100 | Maximum number of discovery cycles |
| `max_duration_minutes` | float | 60.0 | Maximum runtime in minutes |
| `min_confidence_threshold` | float | 0.7 | Minimum confidence for registration |
| `target_domains` | List[str] | All domains | Domains to explore |
| `focus_areas` | Optional[List[str]] | None | Specific chemistry focus |
| `save_interval` | int | 10 | Save progress every N cycles |
| `output_dir` | Optional[Path] | None | Output directory for results |

### CLI Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--provider` | `-p` | Config default | LLM provider |
| `--model` | `-m` | Provider default | Model name |
| `--cycles` | `-c` | 10 | Maximum cycles |
| `--duration` | `-d` | 30.0 | Duration (minutes) |
| `--confidence` | `-f` | 0.7 | Min confidence |
| `--focus` | | None | Focus area |
| `--output` | `-o` | None | Output directory |

## Discovery Cycle

Each cycle performs these steps:

### 1. Proposal
- Generates novel chemical system description
- Avoids existing catalog entries
- Explores underexplored chemical space

### 2. Duplicate Detection
- Checks name against catalog
- Checks description similarity
- Prevents redundant entries

### 3. Literature Validation
- Searches for known systems
- Identifies potential conflicts
- Validates chemical reasonableness

### 4. Synthon Generation
- Maps to seven primitives
- Assigns confidence score
- Provides reasoning

### 5. Registration
- Adds to global catalog if valid
- Persists to disk
- Logs discovery

## Output Files

The agent saves progress to `output_dir` (default: `./discovery_output/`):

### Discovery History
```json
// discovery_history_20260313_143022_cycle_10.json
[
  {
    "cycle_number": 1,
    "timestamp": "2026-03-13T14:30:22.123456",
    "proposed_name": "pyridine_carboxylic_acid_cocrystal",
    "proposed_description": "...",
    "validation_result": "valid_novel",
    "synthon": {...},
    "confidence": 0.85,
    "reasoning": "...",
    "literature_references": [...]
  }
]
```

### Statistics
```json
// discovery_stats_20260313_143022_cycle_10.json
{
  "stats": {
    "cycles_completed": 10,
    "synthons_proposed": 10,
    "synthons_validated": 7,
    "synthons_registered": 7,
    "duplicates_detected": 2,
    "literature_conflicts": 1,
    "errors": 0
  },
  "catalog_size": 45
}
```

### Catalog Export
```json
// catalog_20260313_143022_cycle_10.json
{
  "name": "global_synthonicon",
  "synthons": [...]
}
```

## Validation Results

| Result | Description | Icon |
|--------|-------------|------|
| `valid_novel` | Successfully registered | ✓ |
| `duplicate_exists` | Already in catalog | ⊗ |
| `invalid_chemistry` | Chemically invalid | ✗ |
| `literature_conflict` | Conflicts with literature | ⚠ |
| `low_confidence` | Below confidence threshold | ? |

## Example Session

```bash
$ imscribe agents discover --cycles 5 --focus "halogen bonding"

======================================================================
AUTONOMOUS SYNTHON DISCOVERY AGENT
======================================================================
Configuration:
  Max cycles: 5
  Max duration: 30.0 minutes
  Min confidence: 0.7
  Target domains: ['molecular', 'supramolecular', 'temporal']
  Focus areas: ['halogen bonding']
  Output directory: /home/user/discovery_output
======================================================================

==================================================
CYCLE 1/5
==================================================

[✓] valid_novel
    Name: iodoperfluorobenzene_pyridine_cocrystal
    Notation: ⟨D_wedge; T_bowtie; R_superset; P_directional; F_hbar; G_beth; Gamma_otimes⟩
    Confidence: 85%
    Literature: 2 references found

==================================================
CYCLE 2/5
==================================================

[⊗] duplicate_exists
    Name: carboxylic_acid_dimer
    Reason: Duplicate of existing synthon: carboxylic_acid_dimer

...

======================================================================
DISCOVERY RUN COMPLETE
======================================================================
Duration: 3.2 minutes
Cycles completed: 5
Synthons proposed: 5
Synthons validated: 3
Synthons registered: 3
Duplicates detected: 1
Literature conflicts: 1
Errors: 0
Success rate: 60.0%

Catalog now contains 48 synthons
======================================================================
```

## Advanced Usage

### Focused Discovery Campaigns

```python
# Campaign 1: Non-covalent interactions
await run_autonomous_discovery(
    focus="halogen bonding",
    max_cycles=50,
)

# Campaign 2: Catalytic systems
await run_autonomous_discovery(
    focus="organocatalysis",
    target_domains=["temporal"],
    max_cycles=30,
)

# Campaign 3: Supramolecular assemblies
await run_autonomous_discovery(
    focus="metal-organic frameworks",
    target_domains=["supramolecular"],
    max_cycles=100,
)
```

### Custom Validation

Extend the agent to add custom validation:

```python
class CustomDiscoveryAgent(AutonomousSynthonDiscoveryAgent):
    async def _validate_literature(self, description: str):
        # Add custom validation logic
        result = await super()._validate_literature(description)
        
        # Add additional checks
        if "toxic" in description.lower():
            result["conflict"] = True
            result["reason"] = "Contains toxic functional groups"
        
        return result
    
    async def _check_duplicate(self, name, description):
        # Add similarity-based duplicate detection
        # using molecular fingerprints, etc.
        pass
```

### Integration with External Databases

```python
async def _validate_literature(self, description: str):
    # Search PubChem
    pubchem_results = await self.search_pubchem(description)
    
    # Search Cambridge Structural Database
    csd_results = await self.search_csd(description)
    
    # Combine results
    if pubchem_results or csd_results:
        return {
            "found": True,
            "conflict": False,
            "references": pubchem_results + csd_results,
        }
    
    return {"found": False, "conflict": False}
```

## Best Practices

1. **Start Small**: Run 10-20 cycles first to validate setup
2. **Monitor Progress**: Check output files during long runs
3. **Adjust Confidence**: Lower threshold if too many rejections
4. **Focus Areas**: Use focus for targeted discovery
5. **Save Frequently**: Set `save_interval` appropriately for long runs

## Troubleshooting

### Agent Not Registering Synthons

Check confidence threshold:
```bash
imscribe agents discover --confidence 0.6 --cycles 10
```

### Too Many Duplicates

The catalog may be comprehensive in that region. Try:
```bash
imscribe agents discover --focus "exotic chemistry" --cycles 20
```

### API Rate Limits

Add delays between cycles by modifying the agent:
```python
async def _run_discovery_cycle(self, cycle_number, config):
    await asyncio.sleep(2)  # 2 second delay
    return await super()._run_discovery_cycle(cycle_number, config)
```

## Performance

Typical performance (depends on LLM provider):
- **Cycle time**: 10-30 seconds per cycle
- **Success rate**: 40-70% (valid novel synthons)
- **Catalog growth**: ~5-15 synthons per 20 cycles

## Future Enhancements

Potential improvements:
- Multi-agent collaboration (proposal + validation agents)
- Active learning from rejected proposals
- Integration with computational chemistry tools
- Automated DFT validation
- Real-time literature search via APIs
