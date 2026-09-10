# Project context — SMT wrong-polarity AI gate

The single file to read when picking this project back up, or when handing it to
someone else. It carries what the code cannot say for itself: why each decision
was made, what state the work is in, and what happens next.

Companions: **[PLAN.md](PLAN.md)** for the domain and the schedule,
**[README.md](README.md)** for commands, **[rig/CAPTURE_STANDARD.md](rig/CAPTURE_STANDARD.md)**
for the photography rules.

Last updated: 11 September 2026.

---

## 1. What this is

Surface-mount assembly places components onto solder paste, then reflows them.
Polarized parts (diodes, LEDs, electrolytic and tantalum capacitors, ICs) only
work one way round, and their orientation mark is about a millimetre wide. When
a reel is loaded backwards, every board in the batch is wrong the same way.
Rule-based optical inspection is brittle to lighting and to vendor marking
differences, and it runs after reflow, when fixing a part means desoldering it.

This project adds an inspection gate earlier, and uses a trained classifier
rather than hand-written rules. Phase 1, the whole of this repository, proves
the detection works with a phone and a laptop and no purchases. Phase 2, an
industrial camera wired to a PLC and an operator HMI, is only funded if Phase 1
passes its gate.

**Hardware in use:** iPhone 17 for capture, Arch Linux laptop (i5-12450H, 16 GB,
CPU only, no NVIDIA driver installed) for everything else, Wi-Fi between them.
CPU training is not a constraint at this model size: around 19 seconds per epoch
on 342 images.

## 2. Definition of done

Deliverables are a trained model, a validation report, and a live laptop demo.

| Metric | Target | Why |
|---|---|---|
| False PASS | **0** | A reversed part called good. This is a quality escape and the reason the project exists. |
| False FAIL | ≤ 3 per 100 | A good board stopped. Costs an operator recheck. Cheap. |
| Test set | ~200 unseen images | Never used for training or threshold tuning. |
| Repeatability | Same numbers on rerun | Fixed seed, saved model, logged thresholds. |
| Evidence | Every miss saved with a timestamp | Goes into the report. |

## 3. Architecture

```
phone photo
   │
   ├─ polarity/align.py     find 4 ArUco markers → homography → canonical 1600×1200 view
   │                        → crop the fixed ROI → resize to 224×224
   ├─ polarity/quality.py   reject blurry or badly exposed crops
   │
   ├─ polarity/model.py     ResNet18, 2 classes, outputs P(wrong)
   │
   └─ decision              P ≥ fail → FAIL · P ≥ check → CHECK · else PASS
```

`polarity/pipeline.py` is the single function that runs alignment, cropping and
the quality gates. Both the dataset builder and the live demo call it, so what
the model was trained on and what it sees on the line cannot drift apart.

### Modules

| File | Responsibility |
|---|---|
| `polarity/config.py` | Load/save `config.yaml`, derive every path from the component name. |
| `polarity/align.py` | Marker detection, perspective flattening, ROI crop. |
| `polarity/quality.py` | Sharpness (Laplacian variance) and exposure gates. |
| `polarity/pipeline.py` | The one photo → crop path, returning a `FrameResult`. |
| `polarity/model.py` | Model construction, checkpoint loading, `decide()`, threshold loading. |
| `polarity/data.py` | Dataset walking, board-level grouping, file naming. |

### Scripts

| Script | When to run it | What it does |
|---|---|---|
| `doctor.py` | Any time you are unsure | Checks libraries, display, config, data counts, and prints the exact next command. |
| `make_markers.py` | Once, at the start | Writes `rig/markers.png` to print for the fixture. |
| `make_synthetic.py` | Before real boards exist | Generates fake fixture photos to exercise the pipeline. |
| `ingest.py` | After every photo session | Renames photos into `dataset/raw/`, logs board and session to CSV. |
| `align.py --pick` | Once, after the first photos | Interactive ROI selection, saved to the config. |
| `align.py` | After every ingest | Aligns and crops everything, logs rejects with reasons. |
| `align.py --preview` | After cropping | Contact sheet, to check framing before shooting more. |
| `split.py` | Before training | train/val/test grouped by board, with a manifest. |
| `train.py` | After splitting | Fine-tunes the classifier, early stopping, saves the checkpoint. |
| `evaluate.py --stage val` | After training | Chooses the thresholds, writes the validation report. |
| `evaluate.py --stage test` | Once, at the end | Applies frozen thresholds, writes the report that goes to the meeting. |
| `baseline.py` | Before the meeting | Rule-based comparison: does this need AI at all? |
| `hmi.py` | The demo | Live phone stream to a PASS / CHECK / FAIL operator screen. |

## 4. Design decisions and why

**ArUco fixture instead of board-edge detection.** Four printed markers give an
exact homography from any phone angle to one canonical view, so the ROI is a
fixed rectangle and small changes in phone height or tilt between sessions are
absorbed. Edge detection on a green board under a desk lamp is far less reliable.
If fewer than four markers are found the frame is rejected rather than guessed.

**The FAIL threshold is chosen on data, not fixed at 80%.** The original deck
proposed "FAIL if P(wrong) ≥ 80%". That is the lenient direction and it lets
reversed parts through. Instead `evaluate.py --stage val` finds the weakest score
the model gives any genuinely reversed image and the strongest it gives any good
one, then:

- if the classes separate, the threshold goes in the **middle of the gap**, so it
  is equally far from an escape and from a false rejection, and never closer than
  `safety_margin` to the weakest reversed part;
- if they overlap, it goes below the weakest reversed part, accepting false FAILs,
  because zero escapes wins.

**A third state, CHECK.** Between the two thresholds the system says "I am not
sure, look at it" instead of guessing. The band starts at the 99th percentile of
scores on good validation boards, so roughly one good board in a hundred gets a
human look. An honest "I cannot tell" is worth more on a production line than a
confident coin flip.

**Split by board, never by image.** Fifty photos of one board are near-duplicates.
Splitting them at random puts copies of training images into the test set and the
accuracy becomes fiction. Whole boards therefore live in exactly one split, which
is why at least five physical boards per class are needed. `split.py` refuses to
run with fewer than three and writes `SPLIT_MANIFEST.txt` recording the assignment.

**No flips in augmentation.** A horizontal flip, a vertical flip or a 180 degree
rotation turns a correctly placed part into a reversed one without changing the
label. Training on those teaches the model that a reversed part is fine.
Augmentation is limited to brightness, contrast, saturation, hue, mild blur, ±5°
rotation, and small shifts and scale.

**Wrong examples must be real hardware.** Faking a reversed part by rotating a
correct crop also rotates the silkscreen and the pads, so the model learns the
silkscreen instead of the component. Getting genuinely reversed boards from the
factory is the slowest item in the plan and should be requested on day one.

**Quality gates run before the model, in both training and inference.** A blurred
or blown-out crop gets "I cannot see it", not a guess. Because the same gate ran
when the dataset was built, the model never sees an input class at inference time
that it never saw in training.

**Class weighting favours over-rejecting.** The loss weights the `wrong` class by
the class imbalance times `wrong_class_weight` (1.5). Missing a reversed part
costs more than stopping a good board.

**The test set is treated as spendable.** Each `--stage test` run is appended to
`results/logs/test_runs.json` and the script warns from the second run onward.
Tuning after looking at the test numbers is how honest projects end up reporting
fiction.

**A rule-based baseline ships alongside the model.** `baseline.py` fits a
brightness-asymmetry rule on train and validation and applies it to test. It
answers the obvious question from the decision meeting: if the simple rule
matches the model, the AI phase is not justified for this component.

**Synthetic boards for pipeline rehearsal.** Reversed boards gate the schedule, so
`make_synthetic.py` renders fixture photos with a dark component body and a bright
band on the right (correct) or left (reversed), with the silkscreen mark in the
same place in both classes so the model cannot cheat. Any report containing
synthetic boards is stamped **SYNTHETIC DATA — NOT EVIDENCE**.

## 5. Current state

**Built and verified end to end on synthetic data (11 September 2026).**

| Stage | Result |
|---|---|
| 480 synthetic photos, 8 boards per class | generated |
| Fixture alignment | 480/480 found all four markers |
| Quality gate | 23 rejected as too soft, 457 crops kept |
| Split by board | 342 train / 59 val / 56 test, no board in two splits |
| Training, 8 epochs, CPU | ~19 s/epoch, val accuracy 1.000 |
| Score separation on validation | weakest reversed 0.953, strongest good 0.180, gap +0.774 |
| Thresholds | FAIL ≥ 0.567, CHECK ≥ 0.166 |
| Test set | false PASS 0, false FAIL 0 |
| Live screen | flattened board, ROI boxed, model input thumbnail, verdict panel |

That proves the plumbing. It says nothing about real boards: the synthetic band
is a clean bright rectangle, while a real cathode band is a millimetre of paint
under a desk lamp.

**Not done yet:** everything involving real hardware. No fixture has been built,
no real photograph has been taken, and no reversed boards have been obtained.

## 6. What to do next

1. **Ask the factory for reversed boards today.** Scrap or rework boards with the
   part physically placed backwards, at least five distinct boards. Nothing real
   can be measured without them and they take the longest to arrive.
2. Pick the component. A diode or tantalum capacitor with a clear band is the
   easiest first win; an LED is harder because the marking is subtle. Set it in
   `config.yaml` under `component`.
3. `python scripts/make_markers.py`, print at 100%, build the fixture card.
4. Delete the synthetic data: `make clean-synthetic`.
5. Shoot 100 photos of good boards, ingest, `align.py --pick`, `align.py`,
   then look at `align.py --preview` before shooting more.
6. Continue through the plan in [PLAN.md](PLAN.md) section 7.

## 7. Gotchas

- **`opencv-contrib-python`, not `opencv-python`.** The plain package has no
  `cv2.aruco` and the whole alignment step disappears.
- **Python 3.12 in the venv.** The system Python here is 3.14 and torch wheels
  lag behind it. `uv venv --python 3.12` is what the setup uses.
- **HEIC photos.** Set the iPhone to Most Compatible or the loader silently skips
  them. `doctor.py` will show raw photos present but zero crops.
- **`--cropped` for replaying crop folders.** `hmi.py` expects full fixture photos.
  Pointing it at `dataset/crops/...` gives "fixture not found" on every frame
  unless `--cropped` is passed.
- **Printing markers at anything other than 100% scale** changes their size and
  detection gets unreliable. Turn off "fit to page".
- **`results/logs/test_runs.json` was reset** after the synthetic rehearsal, so
  the counter starts clean for real data.
- **The home directory is a git repository** (`/home/anushka` tracks BOM.git).
  Run `git rev-parse --show-toplevel` before staging anything here, or files from
  the wrong project get committed.

## 8. Session log

**11 September 2026 — system built.**

- Wrote the plan first ([PLAN.md](PLAN.md)) covering the domain, the gate, the
  honesty rules, the rig, and a day-by-day schedule.
- Built the package and eight scripts in this folder. An earlier throwaway
  scaffold at `~/polarity` was used as a reference and is now superseded; it can
  be deleted.
- Verified the environment: OpenCV 5.0.0 with ArUco, torch 2.14 on CPU, timm
  1.0.29, pretrained weights downloadable, GUI windows available.
- Built the synthetic generator when it became clear the pipeline could not
  otherwise be tested before real boards arrive.
- Fixed four defects found by running the thing rather than reading it:
  numpy scalars rejected as OpenCV colours; the simulated card filled the frame
  so camera tilt pushed markers out of shot and 66% of photos failed alignment;
  the FAIL threshold sat at the top of the class gap instead of the middle; and
  the board id was lost once files were copied flat into the split, which broke
  both the report's board column and the synthetic-data detection.
- Ran the full chain end to end and confirmed the numbers in section 5.
