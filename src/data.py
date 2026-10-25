"""Load labeled directed email networks without import-time I/O."""

from collections.abc import Iterator
from pathlib import Path

import networkx as nx

RAW_DIR = Path(__file__).resolve().parents[1] / 'data' / 'raw'


def _integer_pairs(path: Path) -> Iterator[tuple[int, int, int]]:
    """Yield (line number, first value, second value), validating input rows."""
    with path.open(encoding='utf-8') as stream:
        for line_number, line in enumerate(stream, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            fields = line.split()
            try:
                if len(fields) != 2:
                    raise ValueError
                first, second = map(int, fields)
                if first < 0 or second < 0:
                    raise ValueError
            except ValueError:
                raise ValueError(
                    f'{path}:{line_number}: expected two nonnegative integers'
                ) from None
            yield line_number, first, second


def load_network(
    edge_path: str | Path | None = None,
    label_path: str | Path | None = None,
    *,
    remove_self_loops: bool = True,
) -> nx.DiGraph:
    """Return a fresh unweighted DiGraph with integer `department` attributes.

    Defaults resolve relative to the repository, not the current directory.
    All labeled employees are retained, including isolates. Duplicate edges
    collapse naturally; duplicate label rows and unlabeled endpoints fail.
    Set remove_self_loops=False only when inspecting the original network.
    """
    edge_path = Path(edge_path) if edge_path is not None else RAW_DIR / 'email-Eu-core.txt'
    label_path = (
        Path(label_path) if label_path is not None
        else RAW_DIR / 'email-Eu-core-department-labels.txt'
    )
    graph = nx.DiGraph()
    for line_number, node, department in _integer_pairs(label_path):
        if node in graph:
            raise ValueError(f'{label_path}:{line_number}: duplicate label for node {node}')
        graph.add_node(node, department=department)
    for line_number, source, target in _integer_pairs(edge_path):
        if source not in graph or target not in graph:
            raise ValueError(f'{edge_path}:{line_number}: edge endpoint has no department label')
        if source != target or not remove_self_loops:
            graph.add_edge(source, target)
    return graph
