"""
Run the whole ShopKart project, module by module, in course order.

Every lesson script is run as its own program (exactly as you would run it on camera), and
the summary at the end shows which ones passed.

    python run_all.py              # every module, charts saved but no chart windows
    python run_all.py 6 7          # only Modules 6 and 7
    python run_all.py --fresh      # run in an empty outputs folder (proves nothing depends on old files)
    python run_all.py --verbose    # also print each script's own output
"""

import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def natural_key(path):
    """lesson_4_9 before lesson_4_10."""
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", path.name)]


def scripts_for(module_folder):
    """The runnable scripts of one module, in the order the videos use them."""
    setup = sorted(module_folder.glob("check_setup.py"))
    lessons = sorted(module_folder.glob("lesson_*.py"), key=natural_key)
    practice = sorted(module_folder.glob("practice*.py"), key=natural_key)
    return setup + lessons + practice


def module_folders(only=None):
    folders = sorted(p for p in ROOT.glob("module_*") if p.is_dir())
    if only:
        folders = [f for f in folders if int(f.name.split("_")[1]) in only]
    return folders


def run_script(script, env, verbose):
    start = time.time()
    result = subprocess.run([sys.executable, str(script)], cwd=ROOT, env=env,
                            capture_output=True, text=True, stdin=subprocess.DEVNULL)
    seconds = time.time() - start
    if verbose:
        print(result.stdout)
    problems = result.returncode != 0 or "Traceback" in result.stderr or "Warning" in result.stderr
    if problems:
        print(result.stdout[-3000:])
        print(result.stderr[-3000:])
    return (not problems), seconds


def main(argv):
    only = {int(a) for a in argv if a.isdigit()}
    verbose = "--verbose" in argv
    env = dict(os.environ, MPLBACKEND="Agg", PYTHONWARNINGS="default")
    if "--fresh" in argv:
        env["SHOPKART_OUTPUTS"] = tempfile.mkdtemp(prefix="shopkart_outputs_")
        print("Fresh outputs folder:", env["SHOPKART_OUTPUTS"])

    results = []
    for folder in module_folders(only):
        scripts = scripts_for(folder)
        if not scripts:
            continue
        print(f"\n=== {folder.name} ({len(scripts)} scripts) ===")
        for script in scripts:
            ok, seconds = run_script(script, env, verbose)
            results.append((folder.name, script.name, ok, seconds))
            print(f"  {'PASS' if ok else 'FAIL'}  {script.name:<45} {seconds:5.1f}s")

    passed = sum(ok for *_, ok, _ in results)
    print("\n" + "=" * 70)
    print(f"{passed}/{len(results)} scripts passed")
    for module, name, ok, _ in results:
        if not ok:
            print(f"  FAILED: {module}/{name}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
