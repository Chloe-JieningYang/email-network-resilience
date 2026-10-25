# Jiening Milestone 1 Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task with test-first increments and a final whole-branch review.

**Goal:** Deliver Jiening's validated employee network, rankings, department-dependence analysis, reproducible figures, and English handoff/report material for Milestone 1.

**Architecture:** `src/data.py` loads the labeled directed graph; `src/analysis.py` computes tables without file or plotting side effects. `src/run_analysis.py` exports tables and provenance and calls `src/plots.py` for publication-style static PNG figures. Yikang consumes the loader and ranking CSV; removal experiments remain his responsibility.

**Tech Stack:** Python >=3.12, NetworkX, Matplotlib, NumPy, pytest; project-local virtual environment and pinned dependencies.

**Spec:** `docs/jiening-yang-work-plan.md` (approved through the conversation; user now requests execution).

## Global Constraints

- Keep raw files unchanged. Preserve directed edges and all labeled employees, remove self-loops in the analysis graph, and collapse duplicate edges.
- Contacts are distinct incoming/outgoing neighbors outside the employee's department; reciprocal ties count once.
- Use exact, unweighted, normalized directed betweenness with endpoints excluded; sort scores descending and break ties by ascending integer node ID.
- Dependence is the maximum employee incidence count divided by the number of edges for each ordered department pair. Count candidate employees on both sides; omit pairs with no direct contact.
- Use the agreed CSV schemas. Keep all new documentation and figure text in English.
- No removal or connection-adding implementation, no push, no merge, no external submission.

## Review Focus / documented assumptions

1. Isolated labeled employees must survive loading, even if only a self-loop exists: loader fixture and real-data count test.
2. Missing labels, conflicting/duplicate label rows, malformed rows, and negative IDs must fail explicitly: parameterized loader failure tests.
3. Incoming-only and reciprocal contacts must be counted correctly: hand-derived ranking fixture.
4. Ordered department pairs and employee ties must remain deterministic: reversed-pair dependence fixture and ranking ties.
5. Empty/edgeless graphs and zero contact cells must export without invalid charts or invented dependencies: analysis and CLI integration tests.

## Design review against the proposal and official documentation

- Confirmed SNAP input semantics and original counts on the official dataset page. The 642 self-loops are not cross-employee communication and are removed only from the analysis graph.
- Confirmed NetworkX's directed betweenness normalization and endpoint exclusion in its official documentation; exact computation is appropriate for this graph size.
- The dependence metric is a local direct-edge concentration measure, not proof of global disconnection. Show contact counts, and a separately labeled view with at least five edges.
- Labels are anonymous departments. No claims about employee roles, message volume, causal departure effects, or scale-free structure are justified.
- User requested a new branch in the current checkout. Work on `feat/milestone1-jiening-analysis`; do not introduce a separate worktree.
- All scope and ownership decisions are settled by the existing plans. No user decision blocks implementation.

## Task 1: Validated graph loader and environment

**Files:** `.gitignore`, `requirements.txt`, `pyproject.toml`, `src/__init__.py`, `src/data.py`, `tests/test_data.py`.
**Produces:** `load_network(edge_path=None, label_path=None, *, remove_self_loops=True) -> nx.DiGraph`; zero arguments use repository-relative raw paths regardless of the working directory.

- [x] Write tests for labels, isolates, edge direction, duplicates, loops, custom paths, malformed data and unknown endpoints; verify missing implementation causes failure.
- [x] Implement loader and validation with filename/line diagnostics; verify the real graph has 1,005 nodes, 24,929 cleaned edges, 42 departments, and no loops.
- [x] Run the complete pytest suite and inspect the diff.
- [x] Commit: `feat: add validated directed email-network loader`.

## Task 2: Network statistics, rankings, and dependence

**Files:** `src/analysis.py`, `tests/test_analysis.py`.
**Consumes:** the loader's graph with integer node IDs and integer `department` attributes.
**Produces:** `network_summary(graph, graph_version)`, `department_sizes(graph)`, `department_contacts(graph)`, `employee_rankings(graph)`, `department_dependence(graph)`, each returning CSV-ready lists of dictionaries.

- [ ] Write hand-derived fixture tests for summaries, isolate inclusion, contact deduplication, directed-chain betweenness (=0.5 for the middle of a three-node chain), score ties, ordered department pairs, dependence ties, and empty graphs; observe expected failures.
- [ ] Implement pure computations with deterministic row ordering and exact betweenness.
- [ ] Run the complete suite and inspect the diff.
- [ ] Commit: `feat: compute employee rankings and department dependence`.

## Task 3: Reproducible outputs, figures, and handoff material

**Files:** `src/run_analysis.py`, `src/plots.py`, `tests/test_pipeline.py`, `results/`, `README.md`, `docs/milestone1-jiening-results.md`, `docs/handoff-to-yikang.md`, `docs/milestone1-jiening-slides.md`.
**Consumes:** Task 2 tables. **Produces:** agreed CSVs, department sizes/contact CSVs, input checksums/version metadata, three labeled PNGs, and English interpretation/references.

- [ ] Write a CLI integration test on a tiny custom dataset verifying literal CSV results, output isolation, provenance, and nonempty figures; observe failure before implementation.
- [ ] Implement `python -m src.run_analysis` with optional `--edges`, `--labels`, and `--output-dir` arguments. Use a headless plotting backend; avoid changing the caller's graph.
- [ ] Run the full real-data pipeline; inspect the tables and rendered figures; generate English method/results text and a slide outline from verified outputs.
- [ ] Verify a rerun yields identical tables; run the complete suite, inspect staged changes, and perform a fresh whole-branch review.
- [ ] Commit: `feat: export milestone analysis and handoff materials`.

## Execution record

- Branch created from clean `main` at `7602e00`. No existing code or baseline tests.
- Proceed inline under the user's execution request. Plan and technical review make the existing work allocation concrete without reopening agreed scope.

- Task 1: complete — 13 tests first failed on the unimplemented loader, then passed; raw inputs unchanged. Ruling: Python >=3.12 is required by the installed NetworkX/NumPy versions.
