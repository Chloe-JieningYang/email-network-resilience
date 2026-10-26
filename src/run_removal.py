"""Run reproducible removal experiments: python -m src.run_removal."""
import argparse
import csv
import hashlib
import json
import platform
from importlib.metadata import version
from pathlib import Path

from .data import RAW_DIR, load_network
from .removal import DEFAULT_FRACTIONS, fixed_order_trials, random_trials
from .run_analysis import ROOT


def load_orders(path, graph):
    with path.open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != len(graph) or {int(r['node_id']) for r in rows} != set(graph):
        raise ValueError('Ranking CSV employees do not match graph')
    orders = {}
    for strategy, field in [('contacts', 'contact_rank'), ('betweenness', 'betweenness_rank')]:
        if sorted(int(r[field]) for r in rows) != list(range(1, len(graph) + 1)):
            raise ValueError(f'Invalid unique ranking: {field}')
        orders[strategy] = [int(r['node_id']) for r in sorted(rows, key=lambda r: int(r[field]))]
    return orders


def plot_comparison(rows, destination):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    metrics = [('cross_edge_retention', 'Cross-department edge retention'),
               ('survivor_reachability', 'Reachability among surviving pairs'),
               ('original_pair_reachability', 'Reachability / original pair count')]
    for ax, (metric, title) in zip(axes, metrics):
        for strategy in ['random', 'contacts', 'betweenness']:
            subset = [r for r in rows if r['strategy'] == strategy]
            xs = sorted({r['actual_removal_fraction'] for r in subset})
            values = [[r[metric] for r in subset if r['actual_removal_fraction'] == x] for x in xs]
            means = np.array([np.mean(v) for v in values])
            x_percent = np.array(xs) * 100
            line, = ax.plot(x_percent, means, marker='o', label=strategy)
            if strategy == 'random':
                std = np.array([np.std(v, ddof=1) if len(v) > 1 else 0 for v in values])
                ax.fill_between(x_percent, np.maximum(0, means - std), np.minimum(1, means + std),
                                color=line.get_color(), alpha=.2, label='random ±1 SD across trials')
        ax.set(title=title, xlabel='Employees removed (%)', ylabel='Fraction', ylim=(0, 1.02))
        ax.grid(alpha=.25)
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=180)
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'results')
    args = parser.parse_args(argv)
    graph = load_network()
    ranking_path = ROOT / 'results/tables/employee_rankings.csv'
    metadata = json.loads((ROOT / 'results/metadata.json').read_text())
    # Fail rather than mixing rankings and graph inputs from different datasets.
    for key, path in [('edges', RAW_DIR / 'email-Eu-core.txt'),
                      ('labels', RAW_DIR / 'email-Eu-core-department-labels.txt')]:
        source = metadata['inputs'][key]
        if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
            raise ValueError('Input checksum differs from ranking provenance; rerun src.run_analysis')
    orders = load_orders(ranking_path, graph)
    print('Running 30 random permutations and two fixed rankings...', flush=True)
    rows = random_trials(graph)
    for strategy, order in orders.items():
        rows.extend(fixed_order_trials(graph, order, strategy=strategy))
    output = args.output_dir
    (output / 'tables').mkdir(parents=True, exist_ok=True)
    with (output / 'tables/removal_trials.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    settings = {
        'fractions': DEFAULT_FRACTIONS, 'seeds': list(range(30)),
        'versions': {'python': platform.python_version(), **{
            name: version(name) for name in ('networkx', 'numpy', 'matplotlib')}},
        'rankings': 'fixed original graph; nested prefixes',
        'ranking_sha256': hashlib.sha256(ranking_path.read_bytes()).hexdigest(),
        'inputs': metadata['inputs'], 'undefined_values': 'NaN',
        'random_band': 'sample standard deviation across trials, not a confidence interval',
    }
    (output / 'removal_metadata.json').write_text(json.dumps(settings, indent=2) + '\n')
    plot_comparison(rows, output / 'figures/removal_comparison.png')
    print(f'Wrote {len(rows)} trials and removal comparison to {output}')


if __name__ == '__main__':
    main()
