# SMT Wrong-Polarity AI Gate — Phase 1 Plan (Phone + Laptop)

> This is the plan. The system described here is now built in this folder.
> See [CONTEXT.md](CONTEXT.md) for how it works and where the work stands,
> and [README.md](README.md) for the commands.

## 1. What this project is

**Domain.** SMT (Surface Mount Technology) is how modern PCBs are assembled:
solder paste is printed on the bare board, a pick-and-place machine drops
components onto the paste, a reflow oven melts the paste. Afterwards AOI
(Automated Optical Inspection) cameras check the board, then electrical test.

**The problem.** Polarized parts (diodes, LEDs, electrolytic / tantalum
capacitors, ICs) only work one way round. Their orientation mark is tiny: a
~1 mm painted band on a diode, a stripe on a tantalum cap, a dot on an IC.
When a reel is loaded wrong or a feeder is mis-programmed, every board in the
batch has the part reversed. Rule-based AOI (template matching, colour
histograms, programmed part by part, in use since the 1990s) is brittle to
lighting and vendor marking differences, and it sits after reflow, so the fix
means desoldering. Deep-learning AOI (CNN classifiers on labelled crops,
industry adoption ~2016–2018) handles this kind of subtle appearance check far
better. That is what the deck means by "AI is the classifier, OpenCV only
prepares the image."

**The proposal.** Add an AI gate after placement and before AOI (ideally before
reflow, while the part still sits in wet paste and the fix is a tweezers job).
Phase 1 (this plan) proves the detection works using only a phone and a laptop.
Phase 2 (industrial camera + PLC controller + HMI operator screen) is funded
only if Phase 1 passes the gate in section 2.

**Our hardware.** iPhone 17 (camera), Arch Linux laptop with i5-12450H and
16 GB RAM (no NVIDIA driver installed, so CPU training, which is fine for a
small classifier), Wi-Fi between the two.

## 2. Definition of done (Go / No-Go gate)

Deliverables: (a) trained model file, (b) validation report, (c) live laptop
demo screen.

| Metric | Target | Meaning |
|---|---|---|
| False PASS | **0** | A reversed part the AI called correct. This is a quality escape. Non-negotiable. |
| False FAIL | ≤ 3 per 100 | A correct part flagged. Operator rechecks. Cheap. |
| Test set | ~200 unseen images, ~half correct, ~half wrong | Never used for training or threshold tuning. |
| Repeatability | Same numbers on rerun | Fixed seed, saved model, logged threshold. |
| Evidence | Every failed image saved with timestamp | Goes in the report. |

**Correction to the deck.** The deck says "FAIL if Wrong ≥ 80%". That is the
lenient direction. To get zero false PASS the system must fail *easily*: the
FAIL threshold on P(wrong) is chosen on the validation set as the largest
value that still catches every wrong image, minus a safety margin. Expect
something like 0.3–0.5, not 0.8. Add a third output, **CHECK**, for the
uncertain band so a human looks instead of the system guessing.

## 3. Rules that keep the result honest

1. **Split by board, never by image.** One board photographed 50 times and
   split randomly puts near-duplicates in train and test. Accuracy becomes fake.
2. **Wrong examples must be real.** Get scrap/rework boards with the part
   physically placed backwards. Do NOT create "wrong" images by rotating a
   correct crop 180°; that rotates the silkscreen and pads too, and the model
   learns the silkscreen instead of the part.
3. **No flips in augmentation.** A horizontal or vertical flip changes polarity.
   Allowed: brightness, contrast, mild blur, ±5° rotation, small shifts.
4. **Threshold chosen on val, applied to test exactly once.** No retuning after
   seeing test numbers.
5. **Same rig every time.** Fixed phone position, locked exposure/focus, fixed
   board position, one stable light. Variation is added deliberately, not by
   accident.

## 4. Rig (zero purchase)

- Phone clamp on a tripod / copy stand / stack of books, camera pointing
  straight down, ~15–20 cm above the board.
- A stiff card with **four printed ArUco markers** at the corners and the
  board outline taped in the middle. ArUco gives OpenCV a rock-solid
  homography for alignment; much more reliable than finding board edges.
- One desk lamp diffused with paper. No flash. No window light.
- iPhone: Settings → Camera → Formats → **Most Compatible** (JPEG, not HEIC).
  In the Camera app **long-press the board to lock AE/AF** before each session.
- Photo transfer to Arch: **LocalSend** (App Store + AUR) over Wi-Fi. USB via
  libimobiledevice/ifuse works too but breaks across iOS versions.
- Live demo stream: an iOS app that publishes **MJPEG or RTSP over Wi-Fi**
  (e.g. "IP Camera Lite"); OpenCV opens the URL directly, no driver.
  Alternative: Iriun Webcam (has a Linux client that creates a /dev/video).

## 5. Data plan

- **Component.** One designator on one board where reversal has actually
  happened. Diode (D12) or tantalum cap (C17) with a clear band is the easiest
  first win. LED7 is harder (marking is subtle).
- **Boards.** ≥ 5 boards per class. Correct boards are easy. Wrong boards must
  come from the factory (rework/scrap). **Ask for them on day 1 — long pole.**
- **Images.** 200–500 per class. From a fixed rig this is fast: shoot bursts,
  and between bursts nudge the lamp, shift the board a few mm in its outline,
  tilt the card slightly, swap boards, add dust/fingerprints.
- **Naming.** `D12_correct_b01_0001.jpg` (component_label_board_index). Keep a
  CSV log: time, label, board id, lighting note.
- **Folders.**
  ```
  dataset/raw/D12/{correct,wrong}/board_XX/*.jpg      originals
  dataset/crops/D12/{correct,wrong}/board_XX/*.jpg    aligned 224 px ROI crops
  dataset/split/D12/{train,val,test}/{correct,wrong}/ 70 / 15 / 15 by board
  ```

## 6. Pipeline (what to build, in order)

```
phone photo → align (ArUco → homography → canonical top-down view)
            → crop fixed ROI → 224×224 → reject blurry (Laplacian variance)
            → split by board → train classifier → threshold sweep on val
            → run once on test → report → live HMI
```

| Script | Job |
|---|---|
| `make_markers.py` | Generate the 4 ArUco markers to print. |
| `ingest.py` | Rename incoming phone photos, log board/label/session to CSV. |
| `align.py` | Detect 4 markers, warp to canonical size, crop ROI (set once with `--pick`), blur reject, log rejects. |
| `split.py` | train/val/test grouped by board; print boards + images per split. |
| `train.py` | timm ResNet18 or MobileNetV3-small, ImageNet weights, 2-class head, polarity-safe augmentation, early stop, fixed seed. |
| `evaluate.py` | `--stage val`: sweep thresholds, choose FAIL/CHECK, save `threshold.json`. `--stage test`: run once, write report.md + confusion matrix + failed images with timestamps. |
| `baseline.py` | Rule-based OpenCV (left-half vs right-half brightness). Works on easy images, breaks on hard ones. Its numbers sit next to the AI's in the report = the argument for Phase 2. |
| `hmi.py` | Open the phone stream, align + classify every frame, show crop with box and a big PASS / CHECK / FAIL panel, log every decision. |

**Environment.**
```bash
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install torch torchvision timm opencv-contrib-python numpy pyyaml scikit-learn matplotlib pillow
```
(`opencv-contrib-python` is needed for the ArUco module. Python 3.12 pinned
because torch wheels for 3.14 lag.)

## 7. Day-by-day

| Day | Work | Depends on |
|---|---|---|
| 1 | Print markers, build rig, capture standard, shoot 100 correct photos, ingest, set ROI, check crops look sharp and centred | Phone stand, one board |
| 2 | Shoot wrong boards the same way, align + crop everything, split by board, check counts | **Reversed boards from factory** |
| 3 | Train, first confusion matrix, threshold sweep on val, run baseline | Day 2 |
| 4 | Add boards/variation where the model is weakest (look at failed images), retrain, freeze threshold, run test **once**, write report | Day 3 |
| 5 | Live HMI on the phone stream, dry run in front of the team, go / no-go decision | Day 4 |

If day 3 shows false PASS > 0 at every threshold, the fix is more wrong-board
variety, not more epochs.

## 8. Report contents (what goes to the decision meeting)

- Table from section 2 with actual numbers, val and test separately.
- Confusion matrix, chosen thresholds, model file hash, seed.
- Folder of misclassified images with timestamps.
- Baseline vs AI comparison.
- Photos of the rig and the capture standard so anyone can repeat it.
- Recommendation: Go (start industrial camera + PLC/HMI) or No-Go (what data is missing).
