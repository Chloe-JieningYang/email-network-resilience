"""Fixed original-ranking and seeded random employee-removal experiments."""
import math
import random
from .resilience import resilience_metrics

DEFAULT_FRACTIONS = (0, .01, .02, .05, .1)


def fixed_order_trials(graph, order, fractions=DEFAULT_FRACTIONS, strategy='contacts', seed=None):
    order, fractions = list(order), list(fractions)
    if len(order) != len(graph) or set(order) != set(graph):
        raise ValueError('Removal order must contain every employee exactly once')
    if any(not math.isfinite(f) or not 0 <= f <= 1 for f in fractions):
        raise ValueError('Removal fractions must be finite and between zero and one')
    rows = []
    for fraction in fractions:
        count = math.floor(fraction * len(graph))
        surviving = graph.copy()
        surviving.remove_nodes_from(order[:count])
        rows.append({
            'strategy': strategy, 'seed': seed,
            'removal_fraction': fraction,
            'actual_removal_fraction': count / len(graph) if len(graph) else 0,
            'removed_count': count,
            **resilience_metrics(graph, surviving),
        })
    return rows


def random_trials(graph, fractions=DEFAULT_FRACTIONS, seeds=range(30)):
    fractions = tuple(fractions)
    rows = []
    for seed in seeds:
        order = sorted(graph)
        random.Random(seed).shuffle(order)
        rows.extend(fixed_order_trials(graph, order, fractions, 'random', seed))
    return rows
