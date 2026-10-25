# Yikang Cheng — Data, Department Dependence, and Employee Rankings

## Objective

Prepare a reproducible network analysis that identifies which ordered department pairs depend on a small number of employees. Supply the validated graph and rankings needed by Jiening Yang's removal experiments.

This is a proposed work allocation based on the Milestone 0 proposal. Task lists below describe planned work, not completed analysis.

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
3. **Measure department dependence.** For each ordered department pair A → B with at least one direct edge, calculate the fraction of those edges incident to its most involved employee. Count employees on both sides of the pair. Report edge counts alongside dependence scores; a pair with one edge must not be interpreted as strong evidence of large-scale vulnerability.
4. **Rank employees.** Calculate distinct cross-department contacts using the union of incoming and outgoing neighbors outside the employee's department. Also calculate unweighted, normalized directed betweenness on the full cleaned employee graph. Sort descending by score and break ties by ascending numeric node ID.
5. **Prepare interpretable figures.** Create a directed department-contact heatmap, a table of highly dependent department pairs, and a comparison of the two employee rankings. Show the unfiltered dependence results and a clearly labeled sensitivity view restricted to pairs with at least five edges; five is an initial analysis choice, not a dataset property.

## Shared interface and handoff to Jiening

Use project-root-relative paths. The proposed shared outputs are:

| Output | Required contents |
| --- | --- |
| `src/data.py` | `load_network()`: return the cleaned directed graph with integer node IDs and an integer `department` attribute on every node; no import-time execution |
| `results/tables/network_summary.csv` | `metric,value,graph_version` |
| `results/tables/department_dependence.csv` | `source_department,target_department,edge_count,top_employee,top_employee_edge_count,dependence` |
| `results/tables/employee_rankings.csv` | `node_id,department,cross_department_contacts,betweenness,contact_rank,betweenness_rank` |
| `results/figures/` | Labeled figures with captions explaining directionality, filters, and metric definitions |

Coordinate changes to `src/data.py` and shared dependency configuration before editing them. Yikang owns the loader; Jiening owns experiment modules. No department-level path should substitute for an employee-level path in reachability calculations.

## Acceptance criteria and verification

- The cleaned graph matches the expected counts and retains all labeled nodes.
- Every dependence score lies in [0, 1], with no rows for department pairs lacking direct contact.
- Small hand-checkable fixtures cover incoming/outgoing contact deduplication, self-loops, isolated nodes, pair direction, tied rankings, and a single-employee bridge.
- Betweenness is computed on directed employee paths; contact counts do not count reciprocal contacts twice.
- Generated tables and figures can be reproduced with documented commands from the project root.

For implementation, first create meaningful failing tests for each increment, then implement the smallest passing change. Inspect the diff and run relevant tests before each logical commit, once a Git repository is available. Suggested commit boundaries: (1) loader and validation tests; (2) dependence and ranking calculations with tests; (3) analysis exports and figures.

## Proposed checkpoints and writing ownership

- **October 26:** validated loader and agreed metric definitions; hand the loader to Jiening as soon as it works.
- **October 27:** ranking CSV, dependence table, and initial figures ready for integration and rehearsal.
- **October 28 presentation:** present the motivation, dataset, network construction, and dependence/ranking findings.
- **By November 2 report deadline:** draft the dataset, approach, and dependence/ranking results sections; jointly review related work, limitations, and all numerical claims.
- **After Milestone 1:** check robustness of dependence rankings to edge-count thresholds and support the interpretation of connection-adding experiments.

Both members review the final slides and report. If time is tight, prioritize the validated graph, dependence table, and rankings before additional visualizations.
