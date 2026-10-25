"""Headless figures for the preliminary department and employee analysis."""

import os
from pathlib import Path

# Keep Matplotlib's writable font cache inside the project by default.
os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parents[1] / '.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

from .analysis import Row


def _save(fig, path: Path) -> None:
    fig.savefig(path, dpi=180, facecolor='white')
    plt.close(fig)


def plot_analysis(
    sizes: list[Row], contacts: list[Row], dependence: list[Row],
    rankings: list[Row], output_dir: Path,
) -> None:
    """Save three figures; zero/empty data is explicitly labeled, not imputed."""
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    departments = [row['department'] for row in sizes]
    index = {dept: i for i, dept in enumerate(departments)}
    matrix = np.zeros((len(departments), len(departments)))
    for row in contacts:
        matrix[index[row['source_department']], index[row['target_department']]] = row['edge_count']
    fig, ax = plt.subplots(figsize=(10, 8), layout='constrained')
    if contacts:
        image = ax.imshow(
            np.ma.masked_equal(matrix, 0), cmap='viridis',
            norm=LogNorm(vmin=1, vmax=max(2, matrix.max())), interpolation='nearest',
        )
        ax.set_facecolor('#eeeeee')
        fig.colorbar(image, ax=ax, label='Directed employee edges (log color scale)', shrink=0.8)
        step = 1 if len(departments) <= 15 else 2
        ticks = list(range(0, len(departments), step))
        ax.set_xticks(ticks, [str(departments[i]) for i in ticks], fontsize=8)
        ax.set_yticks(ticks, [str(departments[i]) for i in ticks], fontsize=8)
    else:
        ax.text(0.5, 0.5, 'No cross-department edges', ha='center', va='center', transform=ax.transAxes)
    ax.set(xlabel='Receiving department', ylabel='Sending department',
           title='Direct cross-department contacts\nGray cells: no cross-department edges; internal edges excluded')
    _save(fig, output_dir / 'department_contacts.png')

    selected = [row for row in dependence if row['edge_count'] >= 5][:10]
    fig, ax = plt.subplots(figsize=(10, 6), layout='constrained')
    if selected:
        positions = np.arange(len(selected))
        values = [row['dependence'] for row in selected]
        ax.barh(positions, values, color='#287f8e')
        ax.set_yticks(positions, [
            f"{r['source_department']} → {r['target_department']}   (edges={r['edge_count']})"
            for r in selected
        ])
        for i, row in enumerate(selected):
            ax.text(0.98, i, f"employee {row['top_employee']}: {row['top_employee_edge_count']}/{row['edge_count']}",
                    ha='right', va='center', fontsize=9,
                    bbox={'facecolor': 'white', 'alpha': 0.85, 'edgecolor': 'none', 'pad': 2})
        ax.invert_yaxis()
    else:
        ax.text(0.5, 0.5, 'No department pairs with at least 5 edges', ha='center', va='center', transform=ax.transAxes)
    ax.set(xlim=(0, 1.02), xlabel='Fraction of pair edges involving its top employee',
           title='Highest single-employee dependence\nOrdered department pairs with at least 5 direct edges')
    _save(fig, output_dir / 'department_dependence.png')

    fig, ax = plt.subplots(figsize=(9, 6), layout='constrained')
    if rankings:
        ax.scatter(
            [r['cross_department_contacts'] for r in rankings],
            [r['betweenness'] for r in rankings],
            s=20, alpha=0.5, color='#287f8e', edgecolors='none',
        )
        # Annotate only a few employees to keep the plot readable.
        top = sorted(rankings, key=lambda r: r['betweenness_rank'])[:3]
        for offset, row in enumerate(top):
            ax.annotate(str(row['node_id']),
                        (row['cross_department_contacts'], row['betweenness']),
                        xytext=(6, 8 + offset * 4), textcoords='offset points', fontsize=9)
    else:
        ax.text(0.5, 0.5, 'No employees', ha='center', va='center', transform=ax.transAxes)
    ax.set(xlabel='Distinct cross-department contacts (incoming ∪ outgoing)',
           ylabel='Normalized directed betweenness',
           title='Direct contacts versus structural brokerage\nExact betweenness on employee paths; endpoints excluded')
    ax.grid(alpha=0.2)
    _save(fig, output_dir / 'employee_rankings.png')
