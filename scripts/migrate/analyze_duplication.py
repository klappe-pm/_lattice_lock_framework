#!/usr/bin/env python3
"""Analyzes YAML configuration files for duplication opportunities."""

import argparse
import yaml
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field


@dataclass
class DuplicationReport:
    common_fields: Dict[str, int] = field(default_factory=dict)
    common_values: Dict[str, Dict[Any, int]] = field(default_factory=dict)
    suggested_base_fields: List[str] = field(default_factory=list)
    line_savings_estimate: int = 0
    file_count: int = 0


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def load_yaml_files(directory: Path) -> List[Tuple[Path, Dict]]:
    configs = []
    for yaml_file in directory.glob("**/*.yaml"):
        try:
            with open(yaml_file, 'r') as f:
                content = yaml.safe_load(f)
                if content:
                    configs.append((yaml_file, content))
        except Exception as e:
            print(f"Warning: Could not parse {yaml_file}: {e}")
    return configs


def analyze_configs(configs: List[Tuple[Path, Dict]], threshold: float = 0.5) -> DuplicationReport:
    report = DuplicationReport()
    report.file_count = len(configs)
    
    if not configs:
        return report
    
    flattened = [(path, flatten_dict(content)) for path, content in configs]
    field_counts: Counter = Counter()
    value_counts: Dict[str, Counter] = defaultdict(Counter)
    
    for path, flat in flattened:
        for key, value in flat.items():
            field_counts[key] += 1
            try:
                value_counts[key][value] += 1
            except TypeError:
                pass
    
    min_count = int(len(configs) * threshold)
    
    for field, count in field_counts.items():
        if count >= min_count:
            report.common_fields[field] = count
            if field in value_counts:
                for value, val_count in value_counts[field].items():
                    if val_count >= min_count:
                        if field not in report.common_values:
                            report.common_values[field] = {}
                        report.common_values[field][value] = val_count
    
    for field, values in report.common_values.items():
        for value, count in values.items():
            if count >= min_count:
                report.suggested_base_fields.append(f"{field}={value}")
    
    report.line_savings_estimate = len(report.suggested_base_fields) * (len(configs) - 1)
    return report


def print_report(report: DuplicationReport):
    print("\n" + "=" * 60)
    print("CONFIGURATION DUPLICATION ANALYSIS REPORT")
    print("=" * 60)
    print(f"\nFiles analyzed: {report.file_count}")
    
    print("\n--- Common Fields (appear in >50% of files) ---")
    for field, count in sorted(report.common_fields.items(), key=lambda x: -x[1]):
        pct = (count / report.file_count) * 100
        print(f"  {field}: {count} files ({pct:.0f}%)")
    
    print("\n--- Suggested Base Template Fields ---")
    if report.suggested_base_fields:
        for suggestion in report.suggested_base_fields[:20]:
            print(f"  - {suggestion}")
    else:
        print("  No common identical values found.")
    
    print(f"\n--- Estimated Line Savings: ~{report.line_savings_estimate} lines ---")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Analyze YAML configs for duplication")
    parser.add_argument("directory", type=Path, help="Directory containing YAML files")
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()
    
    if not args.directory.exists():
        print(f"Error: Directory {args.directory} does not exist.")
        return
    
    configs = load_yaml_files(args.directory)
    if not configs:
        print(f"No YAML files found in {args.directory}")
        return
    
    report = analyze_configs(configs, args.threshold)
    print_report(report)


if __name__ == "__main__":
    main()
