# SMT Wrong-Polarity AI Detection Gate — Phase 1

Prove that a phone photo plus a small trained classifier can tell a correctly
placed polarized component from a reversed one, with **zero reversed parts
called good** on boards the model has never seen.

Phone camera → fixture alignment → component crop → classifier → PASS / CHECK / FAIL.

- **[PLAN.md](PLAN.md)** — the domain, why this matters, the day-by-day plan.
- **[CONTEXT.md](CONTEXT.md)** — how the system is built, every design decision, current state.
- **[rig/CAPTURE_STANDARD.md](rig/CAPTURE_STANDARD.md)** — print this and tape it next to the rig.

## Setup

```bash
cd ~/german
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install -r requirements.txt
python scripts/doctor.py            # checks the environment, tells you the next step
```

`scripts/doctor.py` is the thing to run whenever you are unsure what to do next.
It reports what data exists, whether the model is trained, and prints the exact
next command.

## The workflow

```bash
python scripts/make_markers.py                     # print rig/markers.png, build the fixture
python scripts/ingest.py --src ~/Downloads/ls --label correct --board 01
python scripts/align.py --pick                     # drag a box around the component, once
python scripts/align.py                            # crop every photo
python scripts/align.py --preview                  # eyeball the crops before shooting more
python scripts/split.py                            # train/val/test, grouped by board
python scripts/train.py                            # fine-tune the classifier
python scripts/evaluate.py --stage val             # choose the thresholds
python scripts/evaluate.py --stage test            # score the test set, ONCE
python scripts/baseline.py --stage test            # rule-based comparison for the report
python scripts/hmi.py --source http://<phone-ip>:8080/video    # live demo
```

`make help` lists the same steps as shortcuts.

## Try it before you have any boards

The reversed boards have to come from the factory and that is the slowest item
in the plan. Synthetic boards let you rehearse the whole chain today:

```bash
python scripts/make_synthetic.py --boards 8 --per-board 30 --set-roi
python scripts/align.py && python scripts/split.py && python scripts/train.py
python scripts/evaluate.py --stage val && python scripts/evaluate.py --stage test
```

Synthetic boards are named `board_S*`, and any report that includes them is
stamped **SYNTHETIC DATA — NOT EVIDENCE**. Delete them before collecting the
real dataset: `make clean-synthetic`.

## Layout

```
config.yaml              one component per config; copy it for C17, LED7, ...
polarity/                the reusable pieces
  config.py              load and save the config, derived paths
  align.py               ArUco fixture detection, perspective flattening, ROI crop
  quality.py             blur and exposure gates
  pipeline.py            photo -> aligned -> cropped -> quality-checked
  model.py               build/load the classifier, the PASS/CHECK/FAIL rule
  data.py                dataset walking, board-level grouping
scripts/                 everything runnable, each with --help
rig/                     printable markers and the capture standard
dataset/raw/             original phone photos, by component/label/board
dataset/crops/           aligned 224 px crops, same structure
dataset/split/           train/val/test, whole boards never split
models/                  <component>_best.pt, _threshold.json, _train_meta.json
results/reports/         report.md, predictions.csv, score plots
results/failed/          every image not cleanly called, timestamped
results/logs/            ingest, alignment rejects, HMI decisions, test-run ledger
```

## The three rules that keep the numbers honest

1. **Whole boards live in one split.** Fifty photos of one board split at random
   put near-duplicates of training images into the test set, and the accuracy
   becomes fiction.
2. **No flips, ever.** A horizontal flip turns a correct part into a reversed one
   without changing the label. Augmentation is photometric plus small jitter only.
3. **Thresholds are chosen on validation and applied to test once.** Every extra
   look at the test set is counted in `results/logs/test_runs.json` and warned about.
