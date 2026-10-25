"""Pure analyses on the loader's directed graph with department attributes.

Functions return deterministic, CSV-ready rows and do not mutate the graph.
Contact and dependence analyses concern direct cross-department edges;
betweenness instead uses directed paths through the entire employee network.
"""

from collections import Counter, defaultdict

import networkx as nx

Row = dict[str, int | float | str]


def network_summary(graph: nx.DiGraph, graph_version: str) -> list[Row]:
    """Count employees, edges, departments, and directed/weak connectivity."""
    departments = nx.get_node_attributes(graph, 'department')
    internal = sum(departments[u] == departments[v] for u, v in graph.edges)
    weak_sizes = [len(c) for c in nx.weakly_connected_components(graph)]
    strong_sizes = [len(c) for c in nx.strongly_connected_components(graph)]
    values = {
        'nodes': len(graph),
        'edges': graph.number_of_edges(),
        'departments': len(set(departments.values())),
        'self_loops': nx.number_of_selfloops(graph),
        'internal_edges': internal,
        'cross_department_edges': graph.number_of_edges() - internal,
        'isolated_nodes': nx.number_of_isolates(graph),
        'weak_components': len(weak_sizes),
        'strong_components': len(strong_sizes),
        'largest_weak_component_nodes': max(weak_sizes, default=0),
        'largest_strong_component_nodes': max(strong_sizes, default=0),
    }
    return [
        {'metric': metric, 'value': value, 'graph_version': graph_version}
        for metric, value in values.items()
    ]


def department_sizes(graph: nx.DiGraph) -> list[Row]:
    """Include every labeled department, even if its employees are isolated."""
    counts = Counter(graph.nodes[node]['department'] for node in graph)
    return [{'department': dept, 'employees': counts[dept]} for dept in sorted(counts)]


def _cross_edges(graph: nx.DiGraph):
    for source, target in graph.edges:
        a = graph.nodes[source]['department']
        b = graph.nodes[target]['department']
        if a != b:
            yield a, b, source, target


def department_contacts(graph: nx.DiGraph) -> list[Row]:
    """Count distinct directed employee edges for observed ordered dept pairs."""
    counts = Counter((a, b) for a, b, _, _ in _cross_edges(graph))
    return [
        {'source_department': a, 'target_department': b, 'edge_count': counts[a, b]}
        for a, b in sorted(counts)
    ]


def employee_rankings(graph: nx.DiGraph) -> list[Row]:
    """Return exact directed betweenness and distinct external-neighbor ranks.

    Ranks are unique 1-based removal positions: descending score, then
    ascending node ID. Reciprocal email contacts count as one neighbor.
    """
    contacts = {
        node: sum(
            graph.nodes[neighbor]['department'] != graph.nodes[node]['department']
            for neighbor in set(graph.predecessors(node)) | set(graph.successors(node))
        )
        for node in graph
    }
    between = nx.betweenness_centrality(graph, normalized=True, weight=None, endpoints=False)
    contact_rank = {
        node: rank for rank, node in enumerate(
            sorted(graph, key=lambda node: (-contacts[node], node)), 1
        )
    }
    betweenness_rank = {
        node: rank for rank, node in enumerate(
            sorted(graph, key=lambda node: (-between[node], node)), 1
        )
    }
    return [
        {
            'node_id': node,
            'department': graph.nodes[node]['department'],
            'cross_department_contacts': contacts[node],
            'betweenness': between[node],
            'contact_rank': contact_rank[node],
            'betweenness_rank': betweenness_rank[node],
        }
        for node in sorted(graph)
    ]


def department_dependence(graph: nx.DiGraph) -> list[Row]:
    """Maximum single-employee share of direct edges for each ordered dept pair.

    Both sending and receiving employees are candidates. Tied employees use
    the smallest node ID. Scores concern direct ties, not global reachability.
    """
    edge_counts = Counter()
    employee_counts = defaultdict(Counter)
    for a, b, source, target in _cross_edges(graph):
        edge_counts[a, b] += 1
        employee_counts[a, b].update((source, target))
    rows = []
    for (a, b), count in edge_counts.items():
        incidences = employee_counts[a, b]
        top = min(incidences, key=lambda node: (-incidences[node], node))
        rows.append({
            'source_department': a, 'target_department': b,
            'edge_count': count, 'top_employee': top,
            'top_employee_edge_count': incidences[top],
            'dependence': incidences[top] / count,
        })
    return sorted(rows, key=lambda r: (
        -r['dependence'], -r['edge_count'], r['source_department'], r['target_department']
    ))
