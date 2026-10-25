from pathlib import Path

import networkx as nx
import pytest

from src.data import load_network


def write_inputs(tmp_path, edges, labels):
    edge_path = tmp_path / 'edges.txt'
    label_path = tmp_path / 'labels.txt'
    edge_path.write_text(edges)
    label_path.write_text(labels)
    return edge_path, label_path


def test_loader_keeps_direction_and_labeled_isolates_and_cleans_edges(tmp_path):
    paths = write_inputs(tmp_path, '# comment\n1 2\n1 2\n2 2\n', '1 0\n2 1\n3 1\n')
    graph = load_network(*paths)
    assert set(graph) == {1, 2, 3}
    assert set(graph.edges) == {(1, 2)}
    assert dict(graph.nodes(data='department')) == {1: 0, 2: 1, 3: 1}
    assert graph.is_directed()
    assert set(nx.isolates(graph)) == {3}


def test_raw_mode_retains_self_loops(tmp_path):
    paths = write_inputs(tmp_path, '1 1\n1 2\n', '1 0\n2 1\n')
    assert set(load_network(*paths, remove_self_loops=False).edges) == {(1, 1), (1, 2)}


@pytest.mark.parametrize('edges,labels', [
    ('1 2\n', '1 0\n'),             # unlabeled endpoint
    ('1 2\n', '1 0\n2 1\n1 0\n'), # duplicate label
    ('1 2\n', '1 0\n1 1\n2 1\n'), # conflicting label
    ('1 2 3\n', '1 0\n2 1\n'),
    ('one 2\n', '1 0\n2 1\n'),
    ('-1 2\n', '1 0\n2 1\n'),
    ('1 2\n', '1 -1\n2 1\n'),
    ('1 2\n', '1 0 extra\n2 1\n'),
])
def test_invalid_input_fails_with_file_and_line(tmp_path, edges, labels):
    paths = write_inputs(tmp_path, edges, labels)
    with pytest.raises(ValueError, match=r'(edges|labels)\.txt:\d+'):
        load_network(*paths)


def test_missing_file_is_not_silently_treated_as_empty(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_network(tmp_path / 'missing', tmp_path / 'missing-labels')


def test_default_paths_work_outside_repository_and_returns_fresh_graph(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    first = load_network()
    assert (len(first), first.number_of_edges()) == (1005, 24929)
    assert len({d for _, d in first.nodes(data='department')}) == 42
    assert nx.number_of_selfloops(first) == 0
    first.remove_node(0)
    assert len(load_network()) == 1005


def test_empty_edge_file_preserves_labels(tmp_path):
    paths = write_inputs(tmp_path, '', '0 0\n1 1\n')
    graph = load_network(*paths)
    assert set(graph) == {0, 1}
    assert graph.number_of_edges() == 0
