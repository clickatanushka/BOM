#!/usr/bin/env python
"""Choose the decision thresholds, then measure the gate honestly.

    python scripts/evaluate.py --stage val     # choose thresholds, tune freely
    python scripts/evaluate.py --stage test    # run ONCE, this is the reported number

The validation stage picks the FAIL threshold as the largest value that still
catches every reversed part, minus a safety margin. That is the opposite of the
lenient "FAIL if wrong >= 80%" in the original deck: a high cut lets reversed
parts through, and a reversed part reaching the customer is the one outcome the
project exists to prevent.

The test stage applies the frozen thresholds and writes the report. Every extra
look at the test set after tuning weakens it, so the run is counted and warned
about in results/logs/test_runs.json.
"""
import argparse
import csv
import json
import shutil
from datetime import datetime

import cv2
import numpy as np

import _boot  # noqa: F401
from polarity import config as C
from polarity import data
from polarity import model as M

BATCH = 64


def score_stage(cfg, classifier, stage):
    """Run the model over one split. Returns (paths, truth 0/1, P(wrong))."""
    root = C.split_dir(cfg) / stage
    paths, truth = [], []
    for index, label in enumerate(data.LABELS):
        found = data.list_images(root / label)
        paths.extend(found)
        truth.extend([index] * len(found))
    if not paths:
        raise SystemExit(f"no images in {root} — run scripts/split.py first")

    scores = []
    for start in range(0, len(paths), BATCH):
        crops = [cv2.imread(str(p)) for p in paths[start:start + BATCH]]
        scores.append(classifier.p_wrong(crops))
    return paths, np.array(truth), np.concatenate(scores)


def sweep(truth, scores):
    """False PASS and false FAIL at every candidate FAIL threshold."""
    rows = []
    for t in np.unique(np.round(np.concatenate([scores, [0.0, 1.0]]), 4)):
        predicted_fail = scores >= t
        rows.append({
            "threshold": float(t),
            "false_pass": int(((truth == 1) & ~predicted_fail).sum()),
            "false_fail": int(((truth == 0) & predicted_fail).sum()),
        })
    return rows


def choose_thresholds(cfg, truth, scores):
    """FAIL below the weakest wrong image; CHECK at a percentile of the correct ones."""
    wrong_scores = scores[truth == 1]
    correct_scores = scores[truth == 0]
    if not len(wrong_scores):
        raise SystemExit("validation set has no wrong images — the split is unusable")

    weakest_wrong = float(wrong_scores.min())
    strongest_correct = float(correct_scores.max()) if len(correct_scores) else 0.0

    if weakest_wrong > strongest_correct:
        # The classes separate. Put the threshold in the middle of the gap: it is
        # then equally far from letting a reversed part through and from stopping
        # a good board, so neither lighting drift nor a new board vendor pushes
        # the gate over an edge immediately. Never sit closer than the safety
        # margin to the weakest reversed part.
        midpoint = (strongest_correct + weakest_wrong) / 2
        fail_threshold = round(max(0.02, min(midpoint, weakest_wrong - cfg["safety_margin"])), 4)
    else:
        # The classes overlap, so some error is unavoidable. Zero false PASS wins:
        # sit below the weakest reversed part and accept the false FAILs.
        fail_threshold = round(max(0.02, weakest_wrong - cfg["safety_margin"]), 4)

    check_threshold = float(np.percentile(correct_scores, cfg["check_percentile"])) \
        if len(correct_scores) else fail_threshold / 2
    check_threshold = round(min(check_threshold, fail_threshold * 0.9), 4)
    check_threshold = max(check_threshold, 0.005)

    return {
        "fail_threshold": fail_threshold,
        "check_threshold": check_threshold,
        "weakest_wrong_score": round(weakest_wrong, 4),
        "strongest_correct_score": round(strongest_correct, 4),
        "separation": round(weakest_wrong - strongest_correct, 4),
        "safety_margin": cfg["safety_margin"],
        "check_percentile": cfg["check_percentile"],
        "chosen_on": "validation set",
        "chosen_at": datetime.now().isoformat(timespec="seconds"),
        "component": cfg["component"],
    }


def tally(truth, decisions):
    d = {
        "n": len(truth),
        "n_correct": int((truth == 0).sum()),
        "n_wrong": int((truth == 1).sum()),
        "false_pass": int(((truth == 1) & (decisions == M.PASS)).sum()),
        "wrong_to_check": int(((truth == 1) & (decisions == M.CHECK)).sum()),
        "wrong_to_fail": int(((truth == 1) & (decisions == M.FAIL)).sum()),
        "false_fail": int(((truth == 0) & (decisions == M.FAIL)).sum()),
        "correct_to_check": int(((truth == 0) & (decisions == M.CHECK)).sum()),
        "correct_to_pass": int(((truth == 0) & (decisions == M.PASS)).sum()),
    }
    d["false_fail_rate"] = d["false_fail"] / max(d["n_correct"], 1)
    d["escape_rate"] = d["false_pass"] / max(d["n_wrong"], 1)
    return d


def plots(cfg, stage, truth, scores, thresholds, out_dir):
    """Score histogram with the thresholds drawn on it: the one picture that
    shows whether the two classes actually separate."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    fig, ax = plt.subplots(figsize=(9, 4.5))
    bins = np.linspace(0, 1, 41)
    ax.hist(scores[truth == 0], bins=bins, alpha=0.75, label="correct boards", color="#2e7d32")
    ax.hist(scores[truth == 1], bins=bins, alpha=0.75, label="wrong boards", color="#c62828")
    ax.axvline(thresholds["check_threshold"], color="#ef6c00", ls="--",
               label=f"CHECK >= {thresholds['check_threshold']}")
    ax.axvline(thresholds["fail_threshold"], color="#1565c0", ls="-",
               label=f"FAIL >= {thresholds['fail_threshold']}")
    ax.set_xlabel("P(wrong) from the model")
    ax.set_ylabel("images")
    ax.set_title(f"{cfg['component']} — {stage} set score separation")
    ax.legend()
    fig.tight_layout()
    path = out_dir / f"{cfg['component']}_{stage}_scores.png"
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def write_report(cfg, stage, stats, thresholds, sweep_rows, checkpoint, failed_dir,
                 plot_path, csv_path, synthetic=False):
    gate = cfg["gate"]
    passed = (stats["false_pass"] <= gate["max_false_pass"]
              and stats["false_fail_rate"] <= gate["max_false_fail_rate"])
    verdict = "GO" if passed else "NO-GO"

    # The most permissive cut that still catches every reversed part: this is the
    # ceiling the chosen threshold has to stay under.
    zero_escape = [r for r in sweep_rows if r["false_pass"] == 0]
    ceiling = max(zero_escape, key=lambda r: r["threshold"]) if zero_escape else None

    lines = [
        f"# Polarity gate report — {cfg['component']} — {stage} set",
        "",
    ]
    if synthetic:
        lines += [
            "> **SYNTHETIC DATA — NOT EVIDENCE.**",
            "> Some or all of these images were generated by `scripts/make_synthetic.py`, "
            "not photographed from real hardware. The numbers below show that the "
            "pipeline runs end to end. They say nothing about whether the gate works on "
            "real boards, and must not be used to support a Go decision.",
            "",
        ]
    lines += [
        f"Generated {datetime.now().isoformat(timespec='seconds')}  ",
        f"Model `{checkpoint.arch}` sha256 `{checkpoint.sha}`  ",
        f"Seed {cfg['seed']}  ",
        f"Thresholds chosen on the {thresholds['chosen_on']} at {thresholds['chosen_at']}",
        "",
        "## Result",
        "",
        f"**{verdict}**",
        "",
        "| Metric | Value | Target |",
        "|---|---|---|",
        f"| Total images | {stats['n']} | ~200 |",
        f"| Correct boards | {stats['n_correct']} | |",
        f"| Wrong boards | {stats['n_wrong']} | |",
        f"| **False PASS** (reversed part called good) | **{stats['false_pass']}** | "
        f"{gate['max_false_pass']} |",
        f"| False FAIL (good board stopped) | {stats['false_fail']} "
        f"({stats['false_fail_rate']*100:.1f}%) | <= {gate['max_false_fail_rate']*100:.0f}% |",
        f"| Wrong sent to CHECK | {stats['wrong_to_check']} | caught, operator confirms |",
        f"| Correct sent to CHECK | {stats['correct_to_check']} | operator load |",
        f"| Wrong correctly failed | {stats['wrong_to_fail']} | |",
        f"| Correct correctly passed | {stats['correct_to_pass']} | |",
        "",
        "## Decision rule",
        "",
        f"- `P(wrong) >= {thresholds['fail_threshold']}` -> **FAIL**",
        f"- `P(wrong) >= {thresholds['check_threshold']}` -> **CHECK** (operator looks)",
        "- otherwise -> **PASS**",
        "",
        f"Weakest wrong image scored {thresholds['weakest_wrong_score']}; "
        f"strongest correct image scored {thresholds['strongest_correct_score']}; "
        f"separation {thresholds['separation']:+.4f}.",
        "",
    ]

    if ceiling:
        separated = thresholds["separation"] > 0
        rule = ("placed in the middle of the gap between the two classes, so it is equally "
                "far from letting a reversed part through and from stopping a good board"
                if separated else
                f"placed {thresholds['safety_margin']} below the weakest reversed part, "
                "because the classes overlap and zero false PASS takes priority")
        lines += [
            "## Threshold headroom",
            "",
            f"On this data every FAIL threshold up to `{ceiling['threshold']:.4f}` still "
            f"catches every reversed part; at that ceiling {ceiling['false_fail']} good "
            f"board(s) would be stopped. The gate runs at `{thresholds['fail_threshold']}`, "
            f"{rule}.",
            "",
        ]

    if stats["false_pass"] > 0:
        lines += [
            "## Escapes",
            "",
            f"{stats['false_pass']} reversed part(s) were called PASS. The gate does not hold. "
            "More epochs will not fix this; more varied reversed boards will. Look at the "
            "escaped images before shooting more data.",
            "",
        ]

    lines += [
        "## Evidence",
        "",
        f"- Per-image predictions: `{csv_path.relative_to(C.ROOT)}`",
        f"- Images not cleanly called (a miss, or routed to CHECK): "
        f"`{failed_dir.relative_to(C.ROOT) if failed_dir.exists() else 'none — every decision was clean'}`",
    ]
    if plot_path:
        lines.append(f"- Score separation plot: `{plot_path.relative_to(C.ROOT)}`")
    lines += [
        f"- Board assignment: `dataset/split/{cfg['component']}/SPLIT_MANIFEST.txt`",
        "",
        "## Reproducing this",
        "",
        "```bash",
        "python scripts/split.py        # same seed, same boards per split",
        "python scripts/train.py",
        f"python scripts/evaluate.py --stage {stage}",
        "```",
        "",
    ]
    return "\n".join(lines), verdict


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_config_arg(ap)
    ap.add_argument("--stage", choices=["val", "test"], required=True)
    ap.add_argument("--keep-thresholds", action="store_true",
                    help="on --stage val, measure with the existing thresholds "
                         "instead of choosing new ones")
    args = ap.parse_args()

    cfg = C.load(args.config)
    classifier = M.Classifier(C.model_path(cfg))
    threshold_path = C.threshold_path(cfg)

    paths, truth, scores = score_stage(cfg, classifier, args.stage)
    print(f"scored {len(paths)} {args.stage} images "
          f"({(truth == 0).sum()} correct, {(truth == 1).sum()} wrong)")

    if args.stage == "val" and not args.keep_thresholds:
        thresholds = choose_thresholds(cfg, truth, scores)
        threshold_path.write_text(json.dumps(thresholds, indent=2))
        cfg["fail_threshold"] = thresholds["fail_threshold"]
        cfg["check_threshold"] = thresholds["check_threshold"]
        C.save(cfg)
        print(f"chose FAIL >= {thresholds['fail_threshold']}   "
              f"CHECK >= {thresholds['check_threshold']}")
        print(f"  weakest wrong {thresholds['weakest_wrong_score']}   "
              f"strongest correct {thresholds['strongest_correct_score']}   "
              f"separation {thresholds['separation']:+.4f}")
        if thresholds["separation"] <= 0:
            print("  ! the classes overlap. Zero false PASS is only possible by "
                  "failing many good boards. Collect more varied reversed boards.")
    else:
        if not threshold_path.exists():
            raise SystemExit("thresholds not chosen yet — run --stage val first")
        thresholds = json.loads(threshold_path.read_text())
        print(f"using frozen thresholds FAIL >= {thresholds['fail_threshold']}   "
              f"CHECK >= {thresholds['check_threshold']}")

    decisions = np.array([M.decide(float(s), thresholds["fail_threshold"],
                                   thresholds["check_threshold"]) for s in scores])
    stats = tally(truth, decisions)
    sweep_rows = sweep(truth, scores)

    # ---- Evidence ----------------------------------------------------------
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reports = C.results_dir() / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    failed_dir = C.results_dir() / "failed" / f"{cfg['component']}_{args.stage}_{stamp}"

    csv_path = reports / f"{cfg['component']}_{args.stage}_predictions.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["image", "board", "truth", "p_wrong", "decision", "correct_call"])
        for path, t, s, d in zip(paths, truth, scores, decisions):
            label = data.LABELS[t]
            good_call = (label == "wrong" and d in (M.FAIL, M.CHECK)) or \
                        (label == "correct" and d in (M.PASS, M.CHECK))
            strict = (label == "wrong" and d == M.FAIL) or (label == "correct" and d == M.PASS)
            writer.writerow([path.name, data.board_id_of(path), label,
                             f"{s:.4f}", d, strict])
            if not strict:
                failed_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, failed_dir / f"{label}_{d}_p{s:.3f}_{path.name}")
            _ = good_call

    synthetic = any(data.board_id_of(p).startswith("S") for p in paths)
    plot_path = plots(cfg, args.stage, truth, scores, thresholds, reports)
    report_text, verdict = write_report(cfg, args.stage, stats, thresholds, sweep_rows,
                                        classifier, failed_dir, plot_path, csv_path,
                                        synthetic)
    report_path = reports / f"{cfg['component']}_{args.stage}_report.md"
    report_path.write_text(report_text)

    # ---- Test-set discipline ----------------------------------------------
    if args.stage == "test":
        ledger_path = C.results_dir() / "logs" / "test_runs.json"
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else []
        ledger.append({"at": datetime.now().isoformat(timespec="seconds"),
                       "component": cfg["component"], "model_sha": classifier.sha,
                       "false_pass": stats["false_pass"], "false_fail": stats["false_fail"],
                       "verdict": verdict})
        ledger_path.write_text(json.dumps(ledger, indent=2))
        runs = sum(1 for e in ledger if e["component"] == cfg["component"])
        if runs > 1:
            print(f"\n  ! the {cfg['component']} test set has now been scored {runs} times.")
            print("    Each look after tuning makes the number less honest. Report the "
                  "first run, or collect fresh boards for a new test set.")

    print("\n" + "=" * 60)
    if synthetic:
        print("  SYNTHETIC DATA — pipeline check only, not evidence for a decision")
    print(f"  false PASS {stats['false_pass']}   "
          f"false FAIL {stats['false_fail']} ({stats['false_fail_rate']*100:.1f}%)   "
          f"CHECK {stats['correct_to_check'] + stats['wrong_to_check']}")
    print(f"  gate verdict: {verdict}")
    print("=" * 60)
    print(f"report  {report_path}")
    if plot_path:
        print(f"plot    {plot_path}")
    if failed_dir.exists():
        print(f"review  {failed_dir}   (misses and CHECK-band images)")
    print("next:", "python scripts/evaluate.py --stage test" if args.stage == "val"
          else "python scripts/hmi.py --source <phone stream url>")


if __name__ == "__main__":
    main()
