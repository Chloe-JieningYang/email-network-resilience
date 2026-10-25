import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from PIL import Image
import pytest

ROOT = Path(__file__).resolve().parents[1]


def run_cli(tmp_path, edges, labels):
    edge_path, label_path = tmp_path / 'edges.txt', tmp_path / 'labels.txt'
    edge_path.write_text(edges)
    label_path.write_text(labels)
    output = tmp_path / 'output'
    result = subprocess.run(
        [sys.executable, '-m', 'src.run_analysis', '--edges', str(edge_path),
         '--labels', str(label_path), '--output-dir', str(output)],
        cwd=tmp_path,
        env={**os.environ, 'PYTHONPATH': str(ROOT)},
        capture_output=True, text=True,
    )
    return result, output, edge_path, label_path


def read_csv(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def test_cli_exports_literal_results_provenance_and_headless_figures(tmp_path):
    result, output, edges, labels = run_cli(
        tmp_path, '0 0\n0 1\n1 2\n', '0 0\n1 1\n2 1\n3 2\n'
    )
    assert result.returncode == 0, result.stderr
    rows = read_csv(output / 'tables' / 'employee_rankings.csv')
    assert [int(r['node_id']) for r in rows] == [0, 1, 2, 3]
    assert [int(r['contact_rank']) for r in rows] == [1, 2, 3, 4]
    assert [int(r['betweenness_rank']) for r in rows] == [2, 1, 3, 4]
    assert float(rows[1]['betweenness']) == pytest.approx(1 / 6)
    dependencies = read_csv(output / 'tables' / 'department_dependence.csv')
    assert dependencies == [{
        'source_department': '0', 'target_department': '1', 'edge_count': '1',
        'top_employee': '0', 'top_employee_edge_count': '1', 'dependence': '1.0',
    }]
    summary = {(r['graph_version'], r['metric']): int(r['value']) for r in read_csv(output / 'tables' / 'network_summary.csv')}
    assert summary['raw', 'edges'] == 3
    assert summary['cleaned', 'edges'] == 2
    assert summary['cleaned', 'isolated_nodes'] == 1
    assert read_csv(output / 'tables' / 'department_sizes.csv')[-1] == {'department': '2', 'employees': '1'}
    assert read_csv(output / 'tables' / 'department_contacts.csv') == [{
        'source_department': '0', 'target_department': '1', 'edge_count': '1',
    }]
    metadata = json.loads((output / 'metadata.json').read_text())
    assert metadata['inputs']['edges']['sha256'] == hashlib.sha256(edges.read_bytes()).hexdigest()
    assert metadata['inputs']['labels']['sha256'] == hashlib.sha256(labels.read_bytes()).hexdigest()
    assert metadata['analysis']['betweenness'] == {'normalized': True, 'weight': None, 'endpoints': False, 'exact': True}
    assert edges.read_text() == '0 0\n0 1\n1 2\n'
    for name in ('department_contacts.png', 'department_dependence.png', 'employee_rankings.png'):
        with Image.open(output / 'figures' / name) as image:
            assert image.width >= 1000 and image.height >= 600
            image.verify()


@pytest.mark.parametrize('labels', ['0 0\n1 1\n', ''])
def test_cli_handles_edgeless_or_empty_inputs_without_inventing_results(tmp_path, labels):
    result, output, _, _ = run_cli(tmp_path, '', labels)
    assert result.returncode == 0, result.stderr
    assert read_csv(output / 'tables' / 'department_dependence.csv') == []
    assert read_csv(output / 'tables' / 'department_contacts.csv') == []
    assert len(read_csv(output / 'tables' / 'employee_rankings.csv')) == len(labels.splitlines())


def test_invalid_dataset_fails_before_creating_results(tmp_path):
    result, output, _, _ = run_cli(tmp_path, '0 9\n', '0 0\n')
    assert result.returncode != 0
    assert 'no department label' in result.stderr
    assert not output.exists()
