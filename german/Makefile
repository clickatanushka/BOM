# Convenience wrappers. Everything here is just the scripts with no arguments;
# read scripts/<name>.py --help for the real interface.
PY := .venv/bin/python

.PHONY: help setup doctor markers crops preview split train val test baseline demo synthetic clean-synthetic

help:
	@echo "make setup            create .venv and install dependencies"
	@echo "make doctor           check the environment and show the next step"
	@echo "make markers          generate rig/markers.png to print"
	@echo "make crops            align + crop everything under dataset/raw"
	@echo "make preview          contact sheet of the crops"
	@echo "make split            build train/val/test, grouped by board"
	@echo "make train            fine-tune the classifier"
	@echo "make val              choose thresholds on the validation set"
	@echo "make test             score the test set (run this once)"
	@echo "make baseline         rule-based comparison for the report"
	@echo "make synthetic        generate fake boards to exercise the pipeline"
	@echo "make clean-synthetic  delete the fake boards"

setup:
	uv venv --python 3.12 .venv || python -m venv .venv
	.venv/bin/python -m pip install -q -r requirements.txt

doctor:    ; $(PY) scripts/doctor.py
markers:   ; $(PY) scripts/make_markers.py
crops:     ; $(PY) scripts/align.py
preview:   ; $(PY) scripts/align.py --preview
split:     ; $(PY) scripts/split.py
train:     ; $(PY) scripts/train.py
val:       ; $(PY) scripts/evaluate.py --stage val
test:      ; $(PY) scripts/evaluate.py --stage test
baseline:  ; $(PY) scripts/baseline.py --stage test
synthetic: ; $(PY) scripts/make_synthetic.py --set-roi

clean-synthetic:
	rm -rf dataset/raw/*/*/board_S* dataset/crops/*/*/board_S*
	@echo "synthetic boards removed; re-run make crops and make split"
