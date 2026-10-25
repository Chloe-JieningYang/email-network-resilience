# Milestone 1: Jiening's Methods and Preliminary Results

This English draft covers Jiening Yang's completed upstream analysis. It is material for the team report; the removal experiments, integrated abstract, conclusion, and final IEEE layout still require the downstream contribution and joint review. All numerical findings below come from the committed `results/tables/` outputs.

## Introduction and motivation

Cross-department communication may depend on a small number of employees even when an institution has many email relationships overall. We ask which ordered department pairs have the most concentrated direct contacts and whether employees with many cross-department neighbors also occupy important positions on directed network paths. The preliminary analysis identifies candidate dependencies and supplies two employee rankings for subsequent removal experiments. It describes structural relationships rather than communication volume or the causal effects of actual employee departures.

## Related work and positioning

Yin et al. study local clustering with higher-order motifs, including direction-sensitive network structure [2]. Their work is cited by the dataset provider. Our project uses the supplied department labels rather than inferring communities, and focuses on dependence between known groups.

Brandes provides an efficient algorithm for shortest-path betweenness centrality [3]. We use the exact directed implementation in NetworkX [5], contrasting path-based brokerage with a simpler count of distinct cross-department contacts. The two scores capture different structural properties.

Albert, Jeong, and Barabasi compare random failures and targeted attacks in complex networks [4]. Their results motivate a controlled removal comparison; they do not establish that this particular email network is scale free or predict its resilience. Our contribution is to combine labeled department-pair dependence with employee-level rankings and the planned removal analysis.

## Dataset and network construction

We use SNAP's email-Eu-core data [1]. A directed edge u → v indicates that employee u sent employee v at least one email. The dataset includes only internal contacts and assigns each employee to one of 42 anonymous departments. No email counts or timestamps are used.

The original files contain 1,005 labeled employees and 25,571 unique directed edges. We remove 642 self-loops from the analysis graph while retaining every labeled employee. The resulting unweighted directed network has 24,929 edges, including 16,284 cross-department edges (65.3%) and 8,645 internal edges. Nineteen employees become isolated after self-loop removal. The largest weakly and strongly connected components contain 986 and 803 employees, respectively. Department sizes range from 1 to 109 employees.

Input validation rejects missing endpoint labels, duplicate label assignments, malformed records, and negative identifiers. Duplicate directed edges would collapse into one relationship; none occur in the supplied edge list. Raw files remain unchanged, and the raw and cleaned statistics are exported separately.

## Methods

### Direct department-pair dependence

For distinct departments A and B, let E_AB be the set of directed employee edges from A to B. For each employee v in either department, let c_AB(v) count edges in E_AB incident to v. For pairs with at least one edge, define:

`D_AB = max_v c_AB(v) / |E_AB|`.

This score lies between zero and one and is directional: A → B is analyzed separately from B → A. A score of one means all observed direct edges for the pair involve a single employee. It does not establish that all indirect paths depend on that employee. Tied employees are represented by the smallest numeric node ID.

We report the edge count next to each score because sparse pairs can have high dependence mechanically. The main table retains every observed pair; the figure separately shows pairs with at least five edges. This threshold is a descriptive analysis choice. Results at thresholds of one, five, and ten edges are compared below.

### Employee rankings

Cross-department contact count is the number of distinct neighbors outside an employee's department, combining incoming and outgoing neighbors. A reciprocal relationship counts once. Directed betweenness sums the fractions of shortest employee-level paths passing through a node, excludes source/target endpoints, and is normalized by `(N - 1)(N - 2)` for this directed graph [5]. Paths use the entire employee network, including internal edges; betweenness is not restricted to cross-department endpoint pairs. We compute it exactly, without sampled source nodes.

For both metrics, employees are ordered by descending score with ascending numeric node ID breaking ties. Exported ranks are unique 1-based removal positions, not statistical average ranks.

## Preliminary results

### Direct dependence is heterogeneous and sensitive to edge support

There are 1,203 ordered department pairs with at least one direct contact, out of 42 × 41 = 1,722 possible cross-department directions. The median pair dependence is 0.50. Of these pairs, 308 have dependence equal to one.

| Minimum edges per ordered pair | Observed pairs retained | Pairs with dependence = 1 | Median dependence |
| --- | ---: | ---: | ---: |
| 1 | 1,203 | 308 | 0.500 |
| 5 | 673 | 13 | 0.400 |
| 10 | 450 | 1 | 0.364 |

The reduction in fully dependent pairs after excluding sparse contacts shows why edge support must accompany concentration scores. Nevertheless, concentration is not limited to single-edge pairs: all 27 edges from department 32 to department 14 involve employee 971. This pair remains fully dependent even at the ten-edge threshold. For department 24 → 36, employee 163 is involved in 14 of 15 edges (dependence 0.933).

These are candidate direct-contact vulnerabilities. Their consequences for indirect reachability remain untested in this upstream analysis.

### Direct contacts and path-based brokerage overlap but differ

Employee 160 (department 36) ranks first under both measures, with 334 distinct cross-department contacts and normalized directed betweenness of approximately 0.07212. The next two contact-ranked employees are 121 and 82; the next two betweenness-ranked employees are 86 and 5.

The two top-ten employee sets overlap in eight employees. Employees 377 and 129 rank ninth and tenth in betweenness but only 42nd and 39th in cross-department contacts. This descriptive mismatch motivates testing the removal strategies separately. It does not yet show which strategy causes more damage.

## Figure captions

1. **Department-contact heatmap** (`results/figures/department_contacts.png`): rows are sending departments and columns are receiving departments. Color shows the number of directed employee edges on a logarithmic scale. Gray cells have no cross-department edge; internal edges on the diagonal are excluded. The figure is an aggregation for visualization, not the graph used for path calculations.
2. **Highest department-pair dependence** (`results/figures/department_dependence.png`): ten highest-ranked pairs among those with at least five direct edges. Labels show edge support and the representative top employee's incidence count. Thirteen eligible pairs have dependence one, so the ten shown are a deterministic subset, ordered by edge count and then department IDs; they are not uniquely the only vulnerable pairs.
3. **Contacts versus brokerage** (`results/figures/employee_rankings.png`): each point is an employee; the horizontal axis counts distinct cross-department neighbors and the vertical axis gives exact normalized directed betweenness. The three employees with highest betweenness are labeled.

## Limitations and next steps

The analysis concerns a static, anonymous contact graph. It cannot measure communication volume, distinguish collaboration from administrative email, identify employee roles, or estimate behavioral adaptation after a departure. High direct dependence does not imply loss of indirect paths, and a large connected component can coexist with vulnerable local relationships. Score ties and arbitrary edge-support thresholds require transparent reporting.

Yikang's next milestone task is to compare random, contact-ranked, and betweenness-ranked employee removal under equal budgets, including trial variability and employee-level directed reachability. Connection additions are described only as future work for the final project and have not been implemented here.

## Contribution statement for this part

Jiening Yang implemented data validation and graph construction, descriptive statistics, exact employee rankings, directed department-pair dependence, figure generation, and reproducibility metadata. Jiening also prepared these upstream methods/results, related-work notes, slide notes, and the handoff interface. This statement does not attribute unfinished removal experiments to either member as completed work.

## References

[1] Stanford Network Analysis Project, "email-Eu-core network." https://snap.stanford.edu/data/email-Eu-core.html (accessed October 25, 2026).

[2] H. Yin, A. R. Benson, J. Leskovec, and D. F. Gleich, "Local Higher-Order Graph Clustering," KDD, pp. 555–564, 2017. https://doi.org/10.1145/3097983.3098069. Author-hosted paper: https://cs.stanford.edu/~jure/pubs/mappr-kdd17.pdf.

[3] U. Brandes, "A Faster Algorithm for Betweenness Centrality," Journal of Mathematical Sociology, vol. 25, no. 2, pp. 163–177, 2001. https://doi.org/10.1080/0022250X.2001.9990249. Paper: https://pdodds.w3.uvm.edu/research/papers/others/2001/brandes2001a.pdf.

[4] R. Albert, H. Jeong, and A.-L. Barabasi, "Error and attack tolerance of complex networks," Nature, vol. 406, pp. 378–382, 2000. https://doi.org/10.1038/35019019. Author preprint: https://arxiv.org/abs/cond-mat/0008064.

[5] NetworkX, "betweenness_centrality," documentation. https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.betweenness_centrality.html (accessed October 25, 2026).
