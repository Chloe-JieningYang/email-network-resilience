import networkx as nx
import pytest

from src.analysis import (
    department_contacts, department_dependence, department_sizes,
    employee_rankings, network_summary,
)


def graph_with_labels(labels, edges):
    graph = nx.DiGraph()
    graph.add_nodes_from((node, {'department': department}) for node, department in labels)
    graph.add_edges_from(edges)
    return graph


def test_summary_counts_direction_components_and_isolates():
    graph = graph_with_labels([(0, 0), (1, 0), (2, 1), (3, 2)], [(0, 1), (1, 2), (2, 1)])
    rows = network_summary(graph, 'cleaned')
    values = {r['metric']: r['value'] for r in rows}
    assert values == {
        'nodes': 4, 'edges': 3, 'departments': 3, 'self_loops': 0,
        'internal_edges': 1, 'cross_department_edges': 2, 'isolated_nodes': 1,
        'weak_components': 2, 'strong_components': 3,
        'largest_weak_component_nodes': 3, 'largest_strong_component_nodes': 2,
    }
    assert {r['graph_version'] for r in rows} == {'cleaned'}
    assert department_sizes(graph) == [
        {'department': 0, 'employees': 2}, {'department': 1, 'employees': 1},
        {'department': 2, 'employees': 1},
    ]
    assert department_contacts(graph) == [
        {'source_department': 0, 'target_department': 1, 'edge_count': 1},
        {'source_department': 1, 'target_department': 0, 'edge_count': 1},
    ]


def test_contacts_include_incoming_and_deduplicate_reciprocal_neighbors():
    graph = graph_with_labels(
        [(4, 2), (3, 0), (2, 1), (1, 0), (0, 0)],
        [(0, 2), (2, 0), (1, 2), (0, 1)],
    )
    before = graph.copy()
    rows = employee_rankings(graph)
    assert [r['node_id'] for r in rows] == [0, 1, 2, 3, 4]
    assert [r['cross_department_contacts'] for r in rows] == [1, 1, 2, 0, 0]
    assert [r['contact_rank'] for r in rows] == [2, 3, 1, 4, 5]
    assert nx.utils.graphs_equal(graph, before)


def test_directed_betweenness_excludes_endpoints_and_normalizes():
    graph = graph_with_labels([(0, 0), (1, 1), (2, 2)], [(0, 1), (1, 2)])
    rows = employee_rankings(graph)
    assert [r['betweenness'] for r in rows] == pytest.approx([0, 0.5, 0])
    assert [r['betweenness_rank'] for r in rows] == [2, 1, 3]


def test_dependence_counts_both_sides_and_preserves_pair_direction():
    graph = graph_with_labels(
        [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2)],
        [(0, 2), (0, 3), (1, 2), (2, 1), (0, 1)],
    )
    rows = department_dependence(graph)
    by_pair = {(r['source_department'], r['target_department']): r for r in rows}
    assert set(by_pair) == {(0, 1), (1, 0)}
    assert by_pair[0, 1] == {
        'source_department': 0, 'target_department': 1, 'edge_count': 3,
        'top_employee': 0, 'top_employee_edge_count': 2, 'dependence': 2 / 3,
    }
    assert by_pair[1, 0] == {
        'source_department': 1, 'target_department': 0, 'edge_count': 1,
        'top_employee': 1, 'top_employee_edge_count': 1, 'dependence': 1.0,
    }


def test_dependence_can_select_an_employee_in_the_receiving_department():
    graph = graph_with_labels([(0, 0), (1, 0), (2, 1)], [(0, 2), (1, 2)])
    assert department_dependence(graph)[0]['top_employee'] == 2
    assert department_dependence(graph)[0]['dependence'] == 1


def test_dependence_output_has_stable_priority_order():
    graph = graph_with_labels(
        [(0, 0), (1, 1), (2, 2), (3, 2)], [(0, 1), (0, 2), (0, 3)]
    )
    assert [(r['source_department'], r['target_department']) for r in department_dependence(graph)] == [(0, 2), (0, 1)]


@pytest.mark.parametrize('labels', [[], [(0, 0)], [(0, 0), (1, 1)]])
def test_edgeless_graphs_do_not_invent_contacts_or_dependencies(labels):
    graph = graph_with_labels(labels, [])
    assert department_contacts(graph) == []
    assert department_dependence(graph) == []
    rows = employee_rankings(graph)
    assert all(r['betweenness'] == 0 and r['cross_department_contacts'] == 0 for r in rows)
    summary = {r['metric']: r['value'] for r in network_summary(graph, 'cleaned')}
    assert summary['nodes'] == len(labels)
    assert summary['isolated_nodes'] == len(labels)
    assert summary['largest_weak_component_nodes'] == (1 if labels else 0)
