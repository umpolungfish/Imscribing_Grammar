"""
Catalog Cleanup Utility — Adversarial validation and cleanup of recorded synthons.

This module scans the synthon catalog, validates each entry against mechanistic
axioms, and flags or removes invalid assignments.

Usage:
    python -m imscrbgrmr.catalog_cleanup --review
    python -m imscrbgrmr.catalog_cleanup --remove-invalid
"""

import argparse
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any

from imscrbgrmr import global_catalog, Synthon
from imscrbgrmr.adversarial_grounding import validate_full_synthon


def validate_catalog_entry(
    name: str,
    synthon: Synthon,
    description: str = "",
) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate a single catalog entry against adversarial axioms.
    
    Args:
        name: Synthon name
        synthon: Synthon object
        description: Optional description for context
    
    Returns:
        Tuple of (is_valid, validation_details)
    """
    synthon_data = synthon.to_dict()
    
    # Extract description from metadata if available
    if not description and synthon.description:
        description = synthon.description
    
    # If no description, use name as hint
    if not description:
        description = name.replace("_", " ")
    
    results = validate_full_synthon(synthon_data, description)
    
    violations = [
        (prim, res) for prim, res in results.items()
        if not res.is_valid
    ]
    
    details = {
        "name": name,
        "notation": synthon.to_notation(),
        "violations": violations,
        "num_violations": len(violations),
        "is_valid": len(violations) == 0,
        "suggested_alternatives": {
            prim: res.alternative_value for prim, res in violations
            if res.alternative_value
        },
    }
    
    return len(violations) == 0, details


def scan_catalog() -> Tuple[List[Synthon], List[Dict[str, Any]]]:
    """
    Scan entire catalog for axiom violations.
    
    Returns:
        Tuple of (valid_synthons, invalid_details)
    """
    valid = []
    invalid_details = []
    
    for name, synthon in global_catalog._synthons.items():
        is_valid, details = validate_catalog_entry(name, synthon)
        
        if is_valid:
            valid.append(synthon)
        else:
            invalid_details.append(details)
    
    return valid, invalid_details


def review_catalog() -> None:
    """Print a review of catalog validity."""
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    valid, invalid = scan_catalog()
    
    console.print(f"\n[bold]Catalog Review[/bold]")
    console.print(f"Total synthons: {len(valid) + len(invalid)}")
    console.print(f"Valid: {len(valid)}")
    console.print(f"Invalid: {len(invalid)}")
    
    if invalid:
        console.print(f"\n[bold red]Invalid Entries:[/bold red]")
        
        table = Table(title="Axiom Violations")
        table.add_column("Name", style="cyan")
        table.add_column("Notation", style="magenta")
        table.add_column("Violations", style="red")
        table.add_column("Suggested Fixes", style="green")
        
        for details in invalid:
            violations_str = ", ".join([
                f"{prim}: {res.assigned_value} ({res.axiom_violated})"
                for prim, res in details["violations"]
            ])
            
            fixes_str = ", ".join([
                f"{prim}→{alt}"
                for prim, alt in details["suggested_alternatives"].items()
            ])
            
            table.add_row(
                details["name"],
                details["notation"],
                violations_str,
                fixes_str if fixes_str else "Manual review required",
            )
        
        console.print(table)
    else:
        console.print(f"\n[green]✓ All catalog entries pass adversarial validation[/green]")


def remove_invalid_entries(dry_run: bool = True) -> int:
    """
    Remove invalid entries from catalog.
    
    Args:
        dry_run: If True, only report what would be removed
    
    Returns:
        Number of entries removed (or would be removed)
    """
    _, invalid = scan_catalog()
    
    if not invalid:
        return 0
    
    removed = 0
    for details in invalid:
        name = details["name"]
        
        if dry_run:
            print(f"Would remove: {name} ({details['notation']})")
            print(f"  Violations: {details['num_violations']}")
            for prim, res in details["violations"]:
                print(f"    - {prim}: {res.assigned_value} → {res.alternative_value}")
                print(f"      Reason: {res.reason}")
        else:
            if name in global_catalog._synthons:
                del global_catalog._synthons[name]
                removed += 1
                print(f"Removed: {name}")
    
    return removed


def save_invalid_report(output_path: str) -> None:
    """Save invalid entries to a JSON report."""
    _, invalid = scan_catalog()
    
    report = {
        "total_invalid": len(invalid),
        "entries": invalid,
    }
    
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Saved report to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Catalog cleanup utility for adversarial axiom validation"
    )
    parser.add_argument(
        "--review",
        action="store_true",
        help="Review catalog for axiom violations",
    )
    parser.add_argument(
        "--remove-invalid",
        action="store_true",
        help="Remove invalid entries from catalog",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be removed without actually removing (default: True)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Actually remove invalid entries (overrides --dry-run)",
    )
    parser.add_argument(
        "--save-report",
        type=str,
        metavar="PATH",
        help="Save invalid entries report to JSON file",
    )
    
    args = parser.parse_args()
    
    if args.review:
        review_catalog()
    elif args.remove_invalid:
        dry_run = not args.force
        count = remove_invalid_entries(dry_run=dry_run)
        if dry_run:
            print(f"\n{count} entries would be removed. Use --force to actually remove.")
        else:
            print(f"\n{count} entries removed from catalog.")
            # Save catalog after removal
            global_catalog.save()
            print("Catalog saved.")
    elif args.save_report:
        save_invalid_report(args.save_report)
    else:
        # Default: show review
        review_catalog()


if __name__ == "__main__":
    main()
