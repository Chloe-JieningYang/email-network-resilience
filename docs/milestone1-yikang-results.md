# Milestone 1: Yikang's Removal Experiments

## Experimental setup

We removed 0, 10, 20, 50, and 100 employees from the cleaned directed graph of
1,005 employees. These correspond to flooring the requested removal fractions
of 0%, 1%, 2%, 5%, and 10%. Each strategy uses identical integer budgets.
Contact-based and betweenness-based removal follow the existing original-graph
rankings, with no adaptive reranking. Random removal uses 30 permutations,
with seeds 0–29 and nested prefixes across removal levels. Every trial starts
from an unchanged copy of the baseline graph.

We report retained cross-department edges divided by the original 16,284 edges.
We also count ordered, different-department employee pairs connected by a
surviving directed path, including paths through any surviving department.
We divide this count both by eligible surviving pairs and by the original
961,932 cross-department pairs. The latter separates survivor selection from
the loss of reachable employees. Undefined ratios are NaN, not zero.
Reachability is computed exactly using employee-level strongly connected
components and their condensation DAG; department aggregation is not used
for paths. The baseline has 755,692 reachable cross-department ordered pairs,
for a reachability ratio of 78.56%.

## Preliminary results

At 100 removed employees (9.95% of the original workforce):

| Strategy | Cross-department edge retention | Survivor reachability | Reachable pairs / original pair count |
| --- | ---: | ---: | ---: |
| Random, mean of 30 trials | 81.54% | 77.22% | 62.61% |
| Contact ranking | 23.91% | 67.51% | 54.52% |
| Betweenness ranking | 28.51% | 65.14% | 52.74% |

Both targeted strategies damage these measures more than the average random
trial at this budget. Contact-ranked removal loses more direct cross-department
edges, while betweenness-ranked removal leaves lower directed reachability.
This supports treating direct contacts and path-based brokerage as distinct
views of importance. Many indirect paths remain even when direct edge
retention falls sharply; edge loss should not be described as equivalent to
fragmentation. Random bands in the figure show ±1 sample standard deviation
across trials, not confidence intervals or a significance test.

## Validation and limitations

Tests cover a directed chain, disconnection, isolates, bridge removal,
zero and full removal, undefined denominators, deterministic seeds, nested
removal prefixes, equal budgets, unchanged input graphs, and invalid rankings.
SCC-based counts are cross-checked against employee-level path traversal on
12 small random directed graphs. A full-data pipeline test checks CSV exports,
baselines, budgets, and figure generation.

These are static structural deletion experiments, not predictions of real
employee departures or communication volume. Rankings are fixed on the original
graph. We have not evaluated adaptive reranking, edge additions, or statistical
significance. Final-stage work can compare targeted and random connection
additions under equal budgets.

## Reproduction

Run `python -m src.run_removal` from the project root after installing the
project dependencies. The exact package versions used for this run, input
hashes, ranking hash, seeds, and settings are recorded in
`results/removal_metadata.json`. This local run used an existing Python
environment rather than the pinned upstream environment; the actual versions
are recorded instead of assuming the pins were installed.

Outputs: `results/tables/removal_trials.csv` (160 rows),
`results/figures/removal_comparison.png`, and `results/removal_metadata.json`.
