import csv
import pytest
from src.run_removal import load_orders, main


def test_real_pipeline_exports_baselines_and_equal_budgets(tmp_path):
    main(['--output-dir', str(tmp_path)])
    with (tmp_path / 'tables/removal_trials.csv').open() as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 160
    baseline = [r for r in rows if r['removed_count'] == '0']
    assert len(baseline) == 32
    assert len({r['reachable_cross_pairs'] for r in baseline}) == 1
    assert {r['cross_edge_retention'] for r in baseline} == {'1.0'}
    assert {int(r['removed_count']) for r in rows} == {0, 10, 20, 50, 100}
    assert (tmp_path / 'figures/removal_comparison.png').stat().st_size > 1000
    assert (tmp_path / 'removal_metadata.json').exists()


def test_invalid_ranking_positions_rejected(tmp_path):
    import networkx as nx
    graph = nx.DiGraph()
    graph.add_nodes_from([0, 1])
    path = tmp_path / 'rankings.csv'
    path.write_text('node_id,contact_rank,betweenness_rank\n0,1,1\n1,1,2\n')
    with pytest.raises(ValueError, match='unique ranking'):
        load_orders(path, graph)
