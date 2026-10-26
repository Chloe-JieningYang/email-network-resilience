import math
import networkx as nx
import pytest

from src.resilience import resilience_metrics
from src.removal import fixed_order_trials, random_trials


def chain():
    graph = nx.DiGraph()
    graph.add_nodes_from((n, {'department': n}) for n in range(4))
    graph.add_edges_from([(0, 1), (1, 2)])
    return graph


def test_chain_direction_isolate_and_removed_bridge():
    graph = chain()
    baseline = resilience_metrics(graph, graph)
    assert baseline['reachable_cross_pairs'] == 3
    assert baseline['eligible_cross_pairs'] == 12
    assert baseline['survivor_reachability'] == 0.25
    damaged = graph.copy()
    damaged.remove_node(1)
    result = resilience_metrics(graph, damaged)
    assert result['cross_edge_retention'] == 0
    assert result['reachable_cross_pairs'] == 0
    assert result['eligible_cross_pairs'] == 6


def test_disconnected_and_undefined_denominators():
    graph = chain()
    graph.remove_edges_from(list(graph.edges))
    result = resilience_metrics(graph, graph)
    assert result['survivor_reachability'] == 0
    assert math.isnan(result['cross_edge_retention'])
    graph.remove_nodes_from([1, 2, 3])
    assert math.isnan(resilience_metrics(graph, graph)['survivor_reachability'])


def test_paths_can_pass_through_same_department():
    graph = chain()
    graph.nodes[1]['department'] = 0
    result = resilience_metrics(graph, graph)
    assert result['reachable_cross_pairs'] == 2
    assert result['eligible_cross_pairs'] == 10


def test_fixed_budget_baseline_and_no_mutation():
    graph = chain()
    before = graph.copy()
    rows = fixed_order_trials(graph, [1, 0, 2, 3], [0, .25, .5], 'contacts')
    assert [r['removed_count'] for r in rows] == [0, 1, 2]
    assert rows[0]['cross_edge_retention'] == 1
    assert rows[1]['reachable_cross_pairs'] == 0
    assert rows[1]['original_pair_reachability'] == 0
    assert nx.utils.graphs_equal(graph, before)


def test_random_reproducibility_nested_prefix_and_equal_budgets():
    graph = chain()
    rows = random_trials(graph, [0, .25, .5], seeds=[0, 1])
    assert rows == random_trials(graph, [0, .25, .5], seeds=[0, 1])
    assert [r['removed_count'] for r in rows] == [0, 1, 2] * 2
    import random
    for seed in [0, 1]:
        order = sorted(graph)
        random.Random(seed).shuffle(order)
        expected = fixed_order_trials(graph, order, [0, .25, .5], 'random', seed)
        assert rows[seed * 3:seed * 3 + 3] == expected


@pytest.mark.parametrize('order,fractions', [([0], [0]), ([0, 0, 2, 3], [0]), ([0, 1, 2, 3], [-.1]), ([0, 1, 2, 3], [1.1])])
def test_reject_invalid_experiments(order, fractions):
    with pytest.raises(ValueError):
        fixed_order_trials(chain(), order, fractions, 'test')


def test_scc_reachability_matches_employee_path_search():
    from src.resilience import reachable_pair_count
    for seed in range(12):
        graph = nx.gnp_random_graph(12, .18, seed=seed, directed=True)
        nx.set_node_attributes(graph, {n: n % 3 for n in graph}, 'department')
        expected = sum(graph.nodes[u]['department'] != graph.nodes[v]['department']
                       for u in graph for v in nx.descendants(graph, u))
        assert reachable_pair_count(graph) == expected


def test_all_removed_and_fixed_denominator_interpretation():
    graph = chain()
    rows = fixed_order_trials(graph, [3, 0, 1, 2], [0, .25, 1])
    assert rows[1]['survivor_reachability'] == .5  # Removing isolate raises survivor ratio.
    assert rows[1]['original_pair_reachability'] == .25
    assert math.isnan(rows[2]['survivor_reachability'])
    assert rows[2]['original_pair_reachability'] == 0
