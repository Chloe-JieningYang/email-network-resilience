# Jiening Yang — Removal Experiments and Resilience Improvement

## Objective

Test whether employees identified by cross-department contact counts or betweenness are structurally important, and later evaluate whether targeted alternative connections improve resilience under an equal edge budget.

This is a proposed work allocation based on the Milestone 0 proposal. The dataset has been downloaded; experiments and results have not yet been implemented.

## Inputs and coordination

- Dataset source: https://snap.stanford.edu/data/email-Eu-core.html
- Raw files: `data/raw/email-Eu-core.txt` and `data/raw/email-Eu-core-department-labels.txt`; the original compressed archives are also retained.
- Download validation found 1,005 employees, 42 departments, 25,571 unique directed edges, and 642 self-loops, with labels for every edge endpoint.
- Consume Yikang Cheng's `src/data.py::load_network()` and `results/tables/employee_rankings.csv`. See `docs/yikang-cheng-work-plan.md` for the complete shared output schemas.
- The shared analysis graph is directed and unweighted, retains all labeled employees, and excludes self-loops. Use integer node IDs and the node attribute `department`.
- Jiening owns removal, reachability, and connection-adding modules. Coordinate any loader or shared dependency changes with Yikang.

## Milestone 1 responsibilities, in execution order

1. **Define and test resilience metrics.** Calculate retained cross-department edges relative to the original cleaned graph, and cross-department employee-pair reachability along directed employee-level paths.
2. **Implement three removal strategies.** Compare random employee removal, descending distinct cross-department contact count, and descending directed betweenness. Use rankings computed once on the original graph for Milestone 1. Break score ties by ascending numeric node ID; adaptive reranking is outside the initial scope.
3. **Run a small reproducible experiment.** Start with removal fractions 0%, 1%, 2%, 5%, and 10%. For N original employees, remove floor(fraction × N) nodes and record the actual count. Use 30 random permutations with documented seeds 0–29; use nested prefixes of each permutation across removal levels. Each targeted strategy is deterministic and needs one run per removal level.
4. **Create preliminary result figures.** Plot the three strategies against actual removal fraction. For random trials, show the mean and a band of plus/minus one standard deviation, labeled as variability across trials. Explain whether direct contact loss also produces loss of indirect reachability. Do not assume the targeted strategies must cause greater fragmentation.
5. **Integrate the milestone story.** Connect Yikang's dependence findings to the removal results, explain limitations, and propose a concrete final-stage connection-adding experiment.

## Metric definitions to keep fixed

- **Cross-department edge retention:** surviving edges whose endpoints have different department labels, divided by the original number of such edges. A zero original denominator is undefined and must be reported explicitly.
- **Surviving-pair reachability:** among ordered pairs of surviving employees in different departments, the fraction for which a directed path exists in the surviving employee graph. Paths may traverse any surviving department. Exclude self-pairs. If there are no eligible pairs, report an undefined value rather than silently returning zero.
- Because the eligible pair set changes after deletion, interpret this metric as connectivity among survivors. If it increases or is hard to interpret, add a secondary metric using the original cross-department pair count as a fixed denominator and counting only surviving reachable pairs in the numerator.
- Report the zero-removal baseline. Do not equate direct edge loss, employee removal, and fragmentation; these measure different effects.
- Do not estimate reachability from the aggregated department graph: aggregation can create apparent paths that do not exist between individual employees.

## Deliverables and acceptance criteria

| Output | Required contents |
| --- | --- |
| `src/resilience.py` | Independently testable edge-retention and directed-reachability functions |
| `src/removal.py` | Fixed-ranking and seeded-random removal experiments |
| `results/tables/removal_trials.csv` | `strategy,seed,removal_fraction,removed_count,surviving_nodes,cross_edges_retained,cross_edge_retention,reachable_cross_pairs,eligible_cross_pairs,survivor_reachability`; leave seed blank for deterministic strategies |
| `results/figures/removal_comparison.png` | A readable two-panel comparison of edge retention and surviving-pair reachability, with baseline and random-trial variability |

Acceptance requires consistent removal budgets, unchanged input graphs after each trial, deterministic seeded results, and hand-checkable tests for a directed chain, a disconnected graph, an isolated employee, a removed bridge, zero removals, and an undefined denominator. Test these behaviors before implementation, then follow red–green–refactor for each increment.

Inspect diffs and run relevant tests before each logical commit, once a Git repository is available. Suggested commit boundaries: (1) resilience metrics and tests; (2) removal strategies and tests; (3) experiment exports and plots. A tiny synthetic graph can unblock implementation while Yikang prepares the real-data rankings.

## Final-stage work after Milestone 1

- Specify how vulnerable ordered department pairs are selected and how actual employee endpoints are chosen; selecting a department pair alone does not define a new employee-level edge.
- Compare targeted additions with random cross-department additions using equal numbers of new directed edges. Reject self-loops, existing edges, and duplicate additions. Document candidate eligibility and sampling seeds.
- Choose endpoints and edges using pre-removal information. Keep the same attack sets across augmented graphs for the main controlled comparison; reranking after augmentation can be a separately labeled sensitivity experiment.
- Evaluate multiple addition budgets and removal levels. Track whether proposed edges remain after endpoint deletion.
- Interpret added edges as hypothetical structural interventions, not evidence that real employees would adopt those communication patterns.

## Proposed checkpoints and writing ownership

- **October 26:** metric definitions, synthetic fixtures, and initial experiment implementation.
- **October 27:** integrate the loader/rankings, run preliminary trials, export plots, and rehearse with Yikang. Profile runtime before expanding the experiment grid.
- **October 28 presentation:** present removal setup, preliminary results, limitations, and final-stage plans.
- **By November 2 report deadline:** draft experimental setup, removal results, short-term plans, and contribution statements; incorporate presentation feedback.
- **After Milestone 1:** implement and evaluate targeted versus random connection additions.

Both members review related work, captions, claims, and the complete report. If time is tight, retain all three removal strategies but reduce the removal grid or number of random trials and disclose that change. Defer connection-adding implementation before dropping validation of the core experiment.
