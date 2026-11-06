"""Compare synthetic GUI data-selection and trend-plot workloads with a git ref.

Run from the repository root:
    MPLBACKEND=Agg python scripts/benchmark_gui_hotpaths.py --base 15ae917

These measurements exclude application startup, Qt windows, and real datasets.
"""

import argparse
import ast
import gc
import json
import subprocess
import time
import tracemalloc
from pathlib import Path
from statistics import median
from types import SimpleNamespace

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]


def source_at(ref, path):
    if ref is None:
        return (ROOT / path).read_text(encoding='utf-8')
    return subprocess.check_output(['git', 'show', f'{ref}:{path}'], cwd=ROOT, text=True)


def selection_method(ref):
    tree = ast.parse(source_at(ref, 'metax/gui/main_gui.py'))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'MetaXGUI')
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == 'get_table_by_df_type')
    namespace = {'pd': pd}
    exec(compile(ast.Module(body=[method], type_ignores=[]), '<selection>', 'exec'), namespace)
    return namespace[method.name]


def measure(function, repeats, track_memory=True):
    times, peaks = [], []
    for _ in range(repeats):
        gc.collect()
        if track_memory:
            tracemalloc.start()
        start = time.perf_counter()
        result = function()
        times.append(time.perf_counter() - start)
        if track_memory:
            peaks.append(tracemalloc.get_traced_memory()[1] / 1024 ** 2)
            tracemalloc.stop()
        del result
        plt.close('all')
    result = {'median_seconds': round(median(times), 6)}
    if peaks:
        result['median_peak_traced_mib'] = round(median(peaks), 3)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='15ae917')
    parser.add_argument('--rows', type=int, default=100_000)
    parser.add_argument('--samples', type=int, default=60)
    parser.add_argument('--trajectories', type=int, default=600)
    parser.add_argument('--repeats', type=int, default=3)
    args = parser.parse_args()
    rng = np.random.default_rng(42)
    frame = pd.DataFrame(rng.random((args.rows, args.samples)),
                         index=[f'feature_{i}' for i in range(args.rows)])
    frame.index.get_loc(frame.index[0])  # Warm the lookup engine for both paths.
    rows, columns = frame.index[:20].tolist(), frame.columns[:8].tolist()
    gui = SimpleNamespace(tfa=SimpleNamespace(taxa_df=frame))
    before, after = selection_method(args.base), selection_method(None)
    original = lambda: before(gui, 'taxa')[columns].loc[rows]
    optimized = lambda: after(gui, 'taxa', sample_list=columns, selected_items=rows)
    pd.testing.assert_frame_equal(original(), optimized())
    results = {
        'pandas_version': pd.__version__,
        'selection_shape': [args.rows, args.samples],
        'selected_shape': [len(rows), len(columns)],
        'selection_before': measure(original, args.repeats),
        'selection_after': measure(optimized, args.repeats),
    }
    trends = pd.DataFrame(rng.random((args.trajectories, 6)), columns=list('ABCDEF'))
    tfa = SimpleNamespace(BasicStats=SimpleNamespace(get_stats_mean_df_by_group=lambda df: df))
    for label, ref in [('before', args.base), ('after', None)]:
        namespace = {}
        exec(compile(source_at(ref, 'metax/taxafunc_ploter/trends_plot.py'), '<trends>', 'exec'), namespace)
        plotter = namespace['TrendsPlot'](tfa)

        def render():
            np.random.seed(42)
            fig, _ = plotter.plot_trends(trends, 3)
            fig.canvas.draw()

        results[f'trends_{label}'] = measure(render, args.repeats, track_memory=False)
    results['trajectories'] = args.trajectories
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
