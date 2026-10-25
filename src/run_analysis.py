"""Export Jiening's Milestone 1 analysis: python -m src.run_analysis."""

import argparse
import csv
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform

import networkx as nx

from .analysis import (
    department_contacts, department_dependence, department_sizes,
    employee_rankings, network_summary,
)
from .data import RAW_DIR, load_network

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    'network_summary': ['metric', 'value', 'graph_version'],
    'department_sizes': ['department', 'employees'],
    'department_contacts': ['source_department', 'target_department', 'edge_count'],
    'employee_rankings': ['node_id', 'department', 'cross_department_contacts', 'betweenness', 'contact_rank', 'betweenness_rank'],
    'department_dependence': ['source_department', 'target_department', 'edge_count', 'top_employee', 'top_employee_edge_count', 'dependence'],
}


def _provenance(path: Path) -> dict:
    resolved = path.resolve()
    return {
        'path': str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--edges', type=Path, default=RAW_DIR / 'email-Eu-core.txt')
    parser.add_argument('--labels', type=Path, default=RAW_DIR / 'email-Eu-core-department-labels.txt')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'results')
    args = parser.parse_args(argv)
    # Validate inputs before creating any output artifacts.
    raw = load_network(args.edges, args.labels, remove_self_loops=False)
    graph = raw.copy()
    graph.remove_edges_from(list(nx.selfloop_edges(graph)))
    print(f'Computing exact directed betweenness for {len(graph)} employees...', flush=True)
    tables = {
        'network_summary': network_summary(raw, 'raw') + network_summary(graph, 'cleaned'),
        'department_sizes': department_sizes(graph),
        'department_contacts': department_contacts(graph),
        'employee_rankings': employee_rankings(graph),
        'department_dependence': department_dependence(graph),
    }
    metadata = {
        'inputs': {'edges': _provenance(args.edges), 'labels': _provenance(args.labels)},
        'versions': {'python': platform.python_version(), **{
            name: version(name) for name in ('networkx', 'numpy', 'matplotlib')
        }},
        'analysis': {
            'directed': True, 'weighted': False, 'self_loops_removed': nx.number_of_selfloops(raw),
            'all_labeled_nodes_retained': True,
            'betweenness': {'normalized': True, 'weight': None, 'endpoints': False, 'exact': True},
            'contacts': 'union of incoming and outgoing neighbors in other departments',
            'ranking_tie_break': 'ascending integer node ID; ranks are unique 1-based positions',
            'dependence': 'max employee incidence count / edge count for each ordered department pair',
            'dependence_tie_break': 'ascending integer node ID',
            'dependence_figure_min_edges': 5,
        },
    }
    output = args.output_dir
    table_dir = output / 'tables'
    table_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in tables.items():
        with (table_dir / f'{name}.csv').open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=SCHEMAS[name])
            writer.writeheader()
            writer.writerows(rows)
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    from .plots import plot_analysis
    plot_analysis(tables['department_sizes'], tables['department_contacts'],
                  tables['department_dependence'], tables['employee_rankings'], output / 'figures')
    print(f'Wrote 5 tables, 3 figures, and metadata to {output.resolve()}')


if __name__ == '__main__':
    main()
