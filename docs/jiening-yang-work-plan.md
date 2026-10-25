# Milestone 1 Work Plan — Jiening Yang

## Objective

For Milestone 1, prepare a reproducible preliminary analysis that identifies which ordered department pairs depend on a small number of employees. Supply the validated graph and rankings needed by Yikang Cheng's initial removal experiments, and explain the dataset and approach in the presentation and report.

This Milestone 1 work allocation swaps the member roles originally listed in the Milestone 0 proposal: Jiening owns data and rankings; Yikang owns removal experiments. Task lists below describe planned work, not completed analysis.

## Start here — prepare the handoff to Yikang

Jiening owns the upstream work and starts directly from the downloaded dataset. Yikang owns the downstream removal experiments and can develop metric tests on synthetic graphs in parallel. Deliver two separate handoffs:

1. **Validated loader first:** provide `src/data.py::load_network()` as soon as graph validation passes, together with the command to run its tests. Yikang can then run the real-data baseline and random-removal trials.
2. **Employee rankings second:** provide `results/tables/employee_rankings.csv` with the agreed fields, ranking definitions, and tie-breaking rule. Yikang can then run the two targeted-removal strategies.

Do not wait for department-dependence figures or report prose before handing over the loader and rankings. After these handoffs, continue the dependence analysis, figures, related work, and corresponding report sections while Yikang runs experiments. See `docs/yikang-cheng-work-plan.md` for his downstream tasks.

## Milestone 1 scope and submission targets

- **Presentation: October 28, 2026.** Deliver a six-minute team presentation with approximately 6–7 slides. Both members must speak; target approximately three minutes each.
- **Report: November 2, 2026, 11:59 p.m. local time.** Deliver a 2–4-page IEEE conference-format report, two columns, 10 or 11 pt, single spaced, including all figures and references. Keep the abstract within 75 words.
- **Research target:** establish the network, quantify department dependence, compare employee rankings, and provide an initial three-strategy removal experiment. Preliminary results may show either vulnerability or robustness; no outcome is assumed.
- **Scope boundary:** implementing connection-adding strategies, adaptive reranking, and a broad parameter study is outside this work allocation. The milestone only needs a short description of proposed next steps for the final project.

## Dataset already downloaded

- Official source: https://snap.stanford.edu/data/email-Eu-core.html
- Directed email edges: `data/raw/email-Eu-core.txt` and its original `.gz` archive.
- Department labels: `data/raw/email-Eu-core-department-labels.txt` and its original `.gz` archive.
- Download validation: 1,005 labeled employees, 42 departments, 25,571 unique directed edges, and 642 self-loops. Every edge endpoint has a department label.
- Edge archive SHA-256: `4b47acdb80197b085fe63c819c357ae488131ee904ed93d1b219a68b0f9e245f`.
- Label archive SHA-256: `e5abe5b4581a480032a63adcf2576c161785f45692642c6ebb0b1276f0f33669`.

Preserve these raw files. The data records whether an email relationship exists, not message counts, timestamps, or communication volume. Include the dataset citation supplied on the official source page in the report.

## Milestone 1 responsibilities, in execution order

1. **Implement and validate the graph loader.** Use Python and NetworkX as the proposed implementation stack. Load all labeled employees, including isolated nodes, into an unweighted directed graph. Attach department IDs as node attributes. Remove self-loops only in the analysis graph and collapse any duplicate directed edges. The expected cleaned graph has 1,005 nodes and 24,929 edges.
2. **Produce descriptive statistics.** Report department sizes, internal versus cross-department edges, isolated nodes, and weakly/strongly connected component sizes. State whether each statistic uses the raw or cleaned graph.
3. **Rank employees and hand off the CSV.** Calculate distinct cross-department contacts using the union of incoming and outgoing neighbors outside the employee's department. Also calculate unweighted, normalized directed betweenness on the full cleaned employee graph. Sort descending by score and break ties by ascending numeric node ID. Deliver the rankings to Yikang immediately after validation.
4. **Measure department dependence.** For each ordered department pair A → B with at least one direct edge, calculate the fraction of those edges incident to its most involved employee. Count employees on both sides of the pair. Report edge counts alongside dependence scores; a pair with one edge must not be interpreted as strong evidence of large-scale vulnerability.
5. **Prepare interpretable figures.** Create a directed department-contact heatmap, a table of highly dependent department pairs, and a comparison of the two employee rankings. Show edge counts alongside dependence. If time allows, add a clearly labeled sensitivity view restricted to pairs with at least five edges; five is an initial analysis choice, not a dataset property.
6. **Lead related-work preparation.** Read and cite relevant sources on the dataset, bridging/centrality, and network robustness. Explain how the project relates to those sources; distinguish completed findings from hypotheses. Yikang reviews the citations and contributes sources related to removal experiments.

## Shared interface and handoff to Yikang

Use project-root-relative paths. The proposed shared outputs are:

| Output | Required contents |
| --- | --- |
| `src/data.py` | `load_network()`: return the cleaned directed graph with integer node IDs and an integer `department` attribute on every node; no import-time execution |
| `results/tables/network_summary.csv` | `metric,value,graph_version` |
| `results/tables/department_dependence.csv` | `source_department,target_department,edge_count,top_employee,top_employee_edge_count,dependence` |
| `results/tables/employee_rankings.csv` | `node_id,department,cross_department_contacts,betweenness,contact_rank,betweenness_rank` |
| `results/figures/` | Labeled figures with captions explaining directionality, filters, and metric definitions |

Coordinate changes to `src/data.py` and shared dependency configuration before editing them. Jiening owns the loader; Yikang owns experiment modules. No department-level path should substitute for an employee-level path in reachability calculations.

## Acceptance criteria and verification

- The cleaned graph matches the expected counts and retains all labeled nodes.
- Every dependence score lies in [0, 1], with no rows for department pairs lacking direct contact.
- Small hand-checkable fixtures cover incoming/outgoing contact deduplication, self-loops, isolated nodes, pair direction, tied rankings, and a single-employee bridge.
- Betweenness is computed on directed employee paths; contact counts do not count reciprocal contacts twice.
- Generated tables and figures can be reproduced with documented commands from the project root.
- The report includes related work, explicit modeling assumptions, preliminary findings, limitations, and an accurate contribution statement.

For implementation, first create meaningful failing tests for each increment, then implement the smallest passing change. Inspect the diff and run relevant tests before each logical commit, once a Git repository is available. Suggested commit boundaries: (1) loader and validation tests; (2) dependence and ranking calculations with tests; (3) analysis exports and figures.

## Proposed checkpoints and writing ownership

- **October 26:** validated loader and agreed metric definitions; hand the loader to Yikang as soon as it works.
- **October 27:** ranking CSV, dependence table, and initial figures ready for integration and rehearsal.
- **October 28 presentation:** present the motivation, dataset, network construction, and dependence/ranking findings.
- **By November 2 report deadline:** draft the dataset, approach, and dependence/ranking results sections; jointly review related work, limitations, and all numerical claims.

## Presentation and report ownership

- **Slides 1–3:** own the title/overview, motivation and related work, and data/network construction. Supply the dependence and ranking results for the preliminary-results slides assembled by Yikang. Rehearse the speaking handoff together.
- **Report:** lead the introduction, previous work, dataset, network construction, dependence/ranking methods, and corresponding preliminary findings.
- **Joint review:** verify the abstract, interpretation, references, contribution statement, and all reported numbers. Yikang assembles the report and submission files; both members approve the submission.

If time is tight, prioritize the validated graph, dependence table, rankings, and clear method explanations before additional visualizations. Completion means these outputs are integrated into the Milestone 1 presentation and report, not merely generated as standalone analysis files.
