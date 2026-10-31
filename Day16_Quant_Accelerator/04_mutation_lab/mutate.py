"""
mutate.py: a tiny mutation tester (no install beyond pytest). It answers one question:
"If someone (me, tomorrow you, a tired 2 a.m. you) changes ONE token in engine.py, do your tests notice?"

    python mutate.py ../03_bug_hunt/engine.py ../03_bug_hunt/test_engine.py            # all mutants
    python mutate.py ENGINE TESTS --lines 120-200 --max 40                             # a slice

A mutant is "killed" if at least one test fails. "Survived" = a blind spot in your suite (or an equivalent mutant
that changes nothing observable: decide which, and write it down). Score = killed / total.
Industrial tools: mutmut, cosmic-ray (see RESOURCES). This one is 80 lines so you can read every line.
"""
import argparse, re, shutil, subprocess, sys, tempfile, os, time

OPS = [  # (name, regex, replacement) — classic mutation operators (Jia & Harman 2011, sec. II)
    ("+ -> -",   r"(?<=[\w\)\] ])\+(?=[ \w\(])", "-"),
    ("- -> +",   r"(?<=[\w\)\] ]) - (?=[\w\(])", " + "),
    ("* -> /",   r"(?<=[\w\)\] ]) \* (?=[\w\(])", " / "),
    ("/ -> *",   r"(?<=[\w\)\] ]) / (?=[\w\(])", " * "),
    ("> -> >=",  r" > ", " >= "),
    ("< -> <=",  r" < ", " <= "),
    (">= -> >",  r" >= ", " > "),
    ("<= -> <",  r" <= ", " < "),
    ("== -> !=", r" == ", " != "),
    ("min->max", r"\bmin\(", "max("),
    ("max->min", r"\bmax\(", "min("),
    ("i+1->i+2", r"self\.i \+ 1", "self.i + 2"),
    ("[:-1]->[:]", r"\.iloc\[:-1\]", ".iloc[:]"),
    ("floor->ceil", r"math\.floor", "math.ceil"),
    ("buy<->sell", r'"buy" if', '"sell" if'),
]

def mutants(lines, lo, hi):
    in_doc = False
    for n, line in enumerate(lines, 1):
        s = line.strip()
        if s.count('"""') == 1: in_doc = not in_doc; continue
        if in_doc or not (lo <= n <= hi) or s.startswith("#") or not s: continue
        code, _, _ = line.partition("#")
        for name, pat, rep in OPS:
            for m in re.finditer(pat, code):
                new = code[:m.start()] + rep + code[m.end():]          # literal swap of the matched token
                if new.rstrip() == code.rstrip(): continue                 # no-op mutant: skip
                yield n, name, line, new.rstrip() + "\n"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("engine"); ap.add_argument("tests")
    ap.add_argument("--lines", default="1-100000"); ap.add_argument("--max", type=int, default=10**6)
    a = ap.parse_args(); lo, hi = map(int, a.lines.split("-"))
    src = open(a.engine).read().splitlines(keepends=True)
    work = tempfile.mkdtemp(); d = os.path.dirname(os.path.abspath(a.engine))
    for f in os.listdir(d):
        if f.endswith(".py"): shutil.copy(os.path.join(d, f), work)
    shutil.copy(a.tests, work)
    base = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", os.path.basename(a.tests)],
                          cwd=work, capture_output=True, text=True)
    if base.returncode != 0: sys.exit("Your suite fails on the UNMUTATED engine. Fix that first.\n" + base.stdout[-800:])
    killed, survived, t0 = 0, [], time.time()
    ms = list(mutants(src, lo, hi))[: a.max]
    for k, (n, name, old, new) in enumerate(ms, 1):
        mut = src.copy(); mut[n - 1] = new
        open(os.path.join(work, os.path.basename(a.engine)), "w").writelines(mut)
        try:
            r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                                os.path.basename(a.tests)], cwd=work, capture_output=True, text=True, timeout=120)
            dead = r.returncode != 0
        except subprocess.TimeoutExpired:
            dead = True  # infinite loop counts as caught
        killed += dead
        if not dead: survived.append((n, name, old.strip(), new.strip()))
        print(f"[{k}/{len(ms)}] line {n:4d} {name:12s} {'killed' if dead else 'SURVIVED'}", flush=True)
    print(f"\nMutation score: {killed}/{len(ms)} = {killed/len(ms):.0%}  ({time.time()-t0:.0f}s)")
    print("\nSurvivors (blind spots or equivalent mutants; triage each):")
    for n, name, o, new in survived: print(f"  line {n}: {name}\n      was: {o}\n      now: {new}")

if __name__ == "__main__":
    main()
