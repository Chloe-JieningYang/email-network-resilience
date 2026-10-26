"""Directed employee-level resilience, with explicit denominator conventions."""
from collections import Counter
import math
import networkx as nx


def cross_edge_count(graph):
    return sum(graph.nodes[u]['department'] != graph.nodes[v]['department']
               for u, v in graph.edges)


def eligible_pair_count(graph):
    counts = Counter(nx.get_node_attributes(graph, 'department').values())
    return len(graph) ** 2 - sum(count ** 2 for count in counts.values())


def reachable_pair_count(graph):
    """Count ordered cross-department pairs using exact SCC condensation.

    Each SCC is internally mutually reachable. Descendants in the condensation
    DAG represent exactly the other reachable employees, without inventing
    paths through department aggregation. Department counters exclude pairs
    whose endpoint departments match. This avoids repeated employee-level BFS.
    """
    dag = nx.condensation(graph)
    counts = {c: Counter(graph.nodes[n]['department'] for n in dag.nodes[c]['members'])
              for c in dag}
    descendants = {}
    total = 0
    for component in reversed(list(nx.topological_sort(dag))):
        reachable = set()
        for child in dag.successors(component):
            reachable.add(child)
            reachable.update(descendants[child])
        descendants[component] = reachable
        targets = counts[component].copy()
        for other in reachable:
            targets.update(counts[other])
        target_size = sum(targets.values())
        total += sum(count * (target_size - targets[dept])
                     for dept, count in counts[component].items())
    return total


def resilience_metrics(original, surviving):
    """Surviving must be an induced deletion subgraph of original."""
    original_edges = cross_edge_count(original)
    original_pairs = eligible_pair_count(original)
    retained = cross_edge_count(surviving)
    eligible = eligible_pair_count(surviving)
    reachable = reachable_pair_count(surviving)
    return {
        'surviving_nodes': len(surviving),
        'cross_edges_retained': retained,
        'cross_edge_retention': retained / original_edges if original_edges else math.nan,
        'reachable_cross_pairs': reachable,
        'eligible_cross_pairs': eligible,
        'survivor_reachability': reachable / eligible if eligible else math.nan,
        'original_pair_reachability': reachable / original_pairs if original_pairs else math.nan,
    }
