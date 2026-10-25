# Milestone 1 Handoff: Jiening Yang → Yikang Cheng

## Ready to use

Jiening's upstream implementation includes the validated graph loader, baseline statistics, exact employee rankings, department-dependence tables, and three figures. The original raw files are unchanged. Removal and reachability experiments remain Yikang's implementation task.

Setup and reproduce from the repository root:

```bash
source .venv/bin/activate
python -m pytest -q
python -m src.run_analysis
```

See the README for first-time installation. Keep changes to shared dependency files coordinated.

## Load the graph

```python
from src.data import load_network

graph = load_network()
assert graph.is_directed()
assert len(graph) == 1005
assert graph.number_of_edges() == 24929
assert graph.nodes[160]['department'] == 36
```

The function performs no I/O until called and returns a fresh `networkx.DiGraph` on each call. Node IDs and department labels are integers. It preserves all labeled employees, removes self-loops, collapses duplicate edges, and rejects malformed rows, duplicate labels, and unlabeled endpoints. Default input paths resolve relative to the repository, not the caller's working directory.

Optional signature: `load_network(edge_path=None, label_path=None, *, remove_self_loops=True)`. For the Milestone 1 experiments, keep the default cleaning behavior. The `False` setting is only for raw-data statistics.

Keep the baseline graph unchanged: remove employees from a copy for each trial. Do not rebuild the network from surviving edge endpoints, because that would discard labeled isolates.

## Read the employee rankings

`results/tables/employee_rankings.csv` contains:

| Field | Meaning |
| --- | --- |
| `node_id` | Employee ID; parse as integer |
| `department` | Anonymous department ID; parse as integer |
| `cross_department_contacts` | Number of distinct other-department neighbors in the union of incoming and outgoing neighbors |
| `betweenness` | Exact normalized directed betweenness on the full cleaned graph; unweighted; endpoints excluded |
| `contact_rank` | Unique 1-based position for contact-based removal |
| `betweenness_rank` | Unique 1-based position for betweenness-based removal |

Rows are stored in ascending node-ID order, **not removal order**. Sort using the corresponding rank field. Both rankings use descending scores and ascending numeric node IDs for ties; do not sort ties lexicographically as strings.

```python
import csv

with open('results/tables/employee_rankings.csv', newline='') as stream:
    rows = list(csv.DictReader(stream))
contact_order = [int(r['node_id']) for r in sorted(rows, key=lambda r: int(r['contact_rank']))]
betweenness_order = [int(r['node_id']) for r in sorted(rows, key=lambda r: int(r['betweenness_rank']))]
assert contact_order[:3] == [160, 121, 82]
assert betweenness_order[:3] == [160, 86, 5]
```

Use these fixed original-graph rankings for the initial comparison. The betweenness score uses paths between all employee pairs, not only cross-department endpoints.

## Baselines and dependence

- 1,005 employees; 42 departments; 24,929 cleaned directed edges.
- 16,284 cross-department edges and 8,645 internal edges.
- 19 isolated employees; largest weak component: 986 nodes; largest strong component: 803 nodes.
- 1,203 observed ordered department pairs with direct contact.

`department_dependence.csv` uses `source_department,target_department,edge_count,top_employee,top_employee_edge_count,dependence`. The score is the maximum employee edge-incidence count divided by the number of edges for that ordered pair. Employees at both ends are candidates. Ties use the smaller employee ID. Rows are ordered by dependence descending, edge count descending, then source and target IDs ascending. Missing department pairs have no direct edges and are omitted.

For example, department 32 → 14 has 27 edges, all involving employee 971. Removing that employee eliminates those **direct** edges; whether an indirect employee-level path remains is for the removal experiment to establish.

## Experiment contract to preserve

Use the settings in `docs/yikang-cheng-work-plan.md`: removal fractions 0%, 1%, 2%, 5%, 10%, equal integer removal counts across strategies, and random seeds 0–29. Include the zero-removal baseline and measure directed reachability on the employee graph. The changing surviving-pair denominator needs explicit interpretation; direct dependence is not itself a reachability metric.

When integrating, check that the ranking CSV was regenerated from the same graph inputs and settings used by the experiments. Input SHA-256 hashes and analysis settings are recorded in `results/metadata.json`.

## Writing and presentation integration

- Reuse `docs/milestone1-jiening-results.md` for the introduction, related work, network construction, methods, and upstream results. It is source material for the IEEE report, not the assembled submission.
- Reuse `docs/milestone1-jiening-slides.md` for the first three slides and optional preliminary-results material.
- Add the removal findings, variability, challenges, short-term plans, and contribution statement. Both members review the completed deck and report before submission.
