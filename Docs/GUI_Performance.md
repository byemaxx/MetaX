# GUI performance changes

This change targets desktop responsiveness and resource lifetime while keeping
the analysis algorithms and session payload structure intact.

- Table, plot, and HTML dialogs are deleted on close and removed from their
  registries. Destruction callbacks use weak references.
- Task callbacks are connected before startup and delivered on the GUI thread
  after native thread exit. Inputs and results are released after callbacks;
  executor deletion waits until nested callback event loops have returned.
- OTF loading, session loading/saving, lazy table materialization, table sorting,
  single-table exports, and trend clustering use worker threads. Modal progress
  dialogs keep painting and event processing active while preventing user edits.
  Session operations reject running or pending analysis workers.
- Session saves use a temporary file in the destination directory and atomic
  replacement. A failed write leaves the previous session intact.
- Cooperative shutdown requests cancellation and polls for task/callback cleanup
  instead of waiting synchronously in the GUI thread. A `**kwargs` parameter alone
  no longer advertises cancellation support.
- GUI output uses bounded thread-safe buffers and 100 ms refresh intervals. Both
  line and character limits prevent unbounded text-widget growth, including logs
  without newlines. Existing application file logging is unchanged.
- Basic and trend plot selections filter rows and columns before copying data.
  Trend trajectories use a `LineCollection` per cluster; all trajectories and the
  existing cluster means are retained. Single-cluster plots are also supported.

## Validation

133 tests passed on Linux, Python 3.12, pandas 2.3.3, and PyQt5 5.15.11:

```sh
QT_QPA_PLATFORM=offscreen QTWEBENGINE_DISABLE_SANDBOX=1 python -m pytest \
  tests/test_gui_responsiveness.py tests/test_gui_memory_optimizations.py \
  tests/test_function_executor.py tests/test_gui_startup.py \
  tests/test_gui_launcher.py tests/test_mgnify_sources.py \
  tests/test_peptide_annotator_layout.py tests/test_auto_report_dialog.py \
  tests/test_complex_plots.py tests/test_basic_plot.py \
  tests/test_workflow_recorder.py -q
```

The new responsiveness and memory tests are included in the existing GUI/full
GitHub Actions job. Native Windows/macOS interaction has not been manually tested.

An initial run with pandas 3.1.1 exposed an UpSetPlot failure in
`test_basic_plot.py::test_plot_upset`. The same failure was reproduced in a clean
checkout of the original `15ae917` commit. No dependency constraints or unrelated
UpSetPlot code were changed here.

## Synthetic benchmarks

Measured against `15ae917`, with three repeats and one BLAS/OpenMP thread:

| Workload | Before | After |
| --- | ---: | ---: |
| Select 20 rows × 8 columns from a 100,000 × 60 table | 0.0220 s | 0.00168 s |
| Peak traced allocation during that selection, excluding the source table | 51.887 MiB | 0.021 MiB |
| Cluster and render 600 trajectories in three clusters | 5.03 s | 0.205 s |

Times are medians. These are isolated synthetic workloads, not end-to-end GUI
speedups or total process memory measurements. Reproduce from the repository root:

```sh
MPLBACKEND=Agg OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python scripts/benchmark_gui_hotpaths.py --base 15ae917
```

## Remaining work

General heatmap/PCA/network plotting, batch exports, and large combobox search
still have synchronous work. Table views retain their current 100-row pagination;
this change does not introduce a virtual table model or asynchronous search.
Matplotlib/Qt canvas operations stay on the GUI thread. CPU work holding Python's
GIL can still delay Python callbacks even when it runs in a worker thread.
