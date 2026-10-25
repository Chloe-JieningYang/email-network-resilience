# Milestone 1 Work Plan — Yikang Cheng

## Objective

For Milestone 1, run preliminary employee-removal experiments to test whether employees identified by cross-department contact counts or betweenness are structurally important. Integrate the results with Jiening Yang's dependence analysis into the presentation and report.

This Milestone 1 work allocation swaps the member roles originally listed in the Milestone 0 proposal: Jiening owns data and rankings; Yikang owns removal experiments. The dataset has been downloaded; experiments and results have not yet been implemented.

## Work order — receive Jiening's outputs and run experiments

Jiening starts with data loading, validation, and employee rankings, then hands those outputs to Yikang. Yikang does not need to wait idly: use Python and NetworkX to develop metric and removal tests on small directed graphs with integer node IDs and a `department` attribute. Keep experiment functions independent of file loading by accepting a graph and an explicitly supplied removal order.

1. While Jiening prepares the data, write hand-checkable failing tests and implement edge retention, directed reachability, seeded random removal, and fixed-order removal. Use manually specified rankings only as synthetic test inputs.
2. Receive Jiening's validated `src/data.py::load_network()` and run the real-data baseline and random-removal trials.
3. Receive `results/tables/employee_rankings.csv` and run contact-based and betweenness-based removal with identical budgets.
4. Export the trial table, generate the comparison plots, and integrate Jiening's dependence findings into the presentation and report.

Only the real-data runs depend on Jiening's handoffs. Synthetic figures must not appear as empirical results in the milestone submission. See `docs/jiening-yang-work-plan.md` for the upstream responsibilities and shared output schemas.

## Milestone 1 scope and submission targets

- **Presentation: October 28, 2026.** Deliver a six-minute team presentation with approximately 6–7 slides. Both members must speak; target approximately three minutes each.
- **Report: November 2, 2026, 11:59 p.m. local time.** Deliver a 2–4-page IEEE conference-format report, two columns, 10 or 11 pt, single spaced, including all figures and references. Keep the abstract within 75 words.
- **Research target:** compare random, contact-based, and betweenness-based removal on the same cleaned network using a small reproducible experiment. Explain what the results support and what remains untested.
- **Scope boundary:** connection-adding implementation and evaluation, adaptive reranking, and a broad parameter study are outside this work allocation. Mention a possible equal-budget targeted-versus-random addition experiment only as future work in the milestone submission.

## Inputs and coordination

- Dataset source: https://snap.stanford.edu/data/email-Eu-core.html
- Raw files: `data/raw/email-Eu-core.txt` and `data/raw/email-Eu-core-department-labels.txt`; the original compressed archives are also retained.
- Download validation found 1,005 employees, 42 departments, 25,571 unique directed edges, and 642 self-loops, with labels for every edge endpoint.
- Consume Jiening Yang's `src/data.py::load_network()` and `results/tables/employee_rankings.csv`. See `docs/jiening-yang-work-plan.md` for the complete shared output schemas.
- The shared analysis graph is directed and unweighted, retains all labeled employees, and excludes self-loops. Use integer node IDs and the node attribute `department`.
- Yikang owns removal and reachability modules, experiment integration, and submission assembly. Coordinate any loader or shared dependency changes with Jiening.

## Milestone 1 responsibilities, in execution order

1. **Define and test resilience metrics.** Calculate retained cross-department edges relative to the original cleaned graph, and cross-department employee-pair reachability along directed employee-level paths.
2. **Implement three removal strategies.** First test seeded random removal and fixed-order removal using synthetic graphs and supplied rankings. After the real rankings arrive, compare random employee removal, descending distinct cross-department contact count, and descending directed betweenness. Use rankings computed once on the original graph for Milestone 1. Break score ties by ascending numeric node ID; adaptive reranking is outside the initial scope.
3. **Run a small reproducible experiment.** Start with removal fractions 0%, 1%, 2%, 5%, and 10%. For N original employees, remove floor(fraction × N) nodes and record the actual count. Use 30 random permutations with documented seeds 0–29; use nested prefixes of each permutation across removal levels. Each targeted strategy is deterministic and needs one run per removal level.
4. **Create preliminary result figures.** Plot the three strategies against actual removal fraction. For random trials, show the mean and a band of plus/minus one standard deviation, labeled as variability across trials. Explain whether direct contact loss also produces loss of indirect reachability. Do not assume the targeted strategies must cause greater fragmentation.
5. **Integrate the milestone story.** Connect Jiening's dependence findings to the removal results, explain limitations, and write a short future-work paragraph and proposed final-project timeline. This is a planning deliverable; do not implement connection additions for Milestone 1.

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

Inspect diffs and run relevant tests before each logical commit, once a Git repository is available. Suggested commit boundaries: (1) resilience metrics and tests; (2) removal strategies and tests; (3) experiment exports and plots. A tiny synthetic graph can unblock implementation while Jiening prepares the real-data rankings.

## Proposed checkpoints and writing ownership

- **Start immediately, before the data handoff:** metric tests, synthetic fixtures, removal implementation, export/plotting pipeline, and experimental-setup draft.
- **October 26:** validate metrics and removal behavior on synthetic graphs; integrate the real loader if available and start baseline/random-removal trials.
- **October 27:** integrate the loader/rankings, run preliminary trials, export plots, and rehearse with Jiening. Profile runtime before expanding the experiment grid.
- **October 28 presentation:** present removal setup, preliminary results, limitations, and final-stage plans.
- **By November 2 report deadline:** draft experimental setup, removal results, short-term plans, and contribution statements; incorporate presentation feedback.

## Presentation and report ownership

- **Slides 4–6:** assemble the preliminary-results slides using both members' outputs; own the removal setup/results, challenges, timeline, division of labor, and conclusion. Prepare a compact references slide if using seven slides. Coordinate with Jiening to keep the total speaking time within six minutes.
- **Report:** lead the experimental setup, removal results, limitations, conclusion, short-term plans, and contribution statement. Assemble both members' sections in the IEEE template and draft the abstract for joint review.
- **Related work:** contribute sources on removal experiments and resilience; review the section led by Jiening.
- **Submission:** check page and abstract limits, figures, references, and consistency between slides and report. Incorporate presentation feedback, obtain both members' review, and submit the report as a group submission on Gradescope.

If time is tight, retain all three removal strategies but reduce the removal grid or number of random trials and disclose that change. Prioritize validated metrics and interpretable preliminary results over additional experiments. Completion means the experiments and their limitations are documented in the Milestone 1 presentation and report.
