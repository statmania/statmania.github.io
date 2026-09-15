#!/usr/bin/env python3
"""
Generates a small collection of mini-Sudoku puzzles and writes them to
puzzles.json, then embeds that into a self-contained games/sudoku.html
(same build pattern as cross-word/build_puzzles.py and
wordweave/build_game.py).

Three variants:
  - 4x4  : 4 rows x 4 cols, digits 1-4, 2x2 boxes. Classic mini sudoku.
  - 6x6  : 6 rows x 6 cols, digits 1-6, 2x3 boxes. Classic 6x6 sudoku.
  - 6x4  : 4 rows x 6 cols ("6 wide x 4 tall"), digits 1-6, 2x3 boxes.
           Rows and boxes are full 1-6 permutations same as any sudoku;
           columns only have 4 cells so they can't contain all 6 digits -
           column uniqueness (no repeat in a column) is still enforced,
           it just can't be "every digit present" for that axis. This is
           the standard way a non-square rectangular sudoku variant is
           defined.

All three share one constraint rule: a digit may not already appear
elsewhere in the same row, same column, or same box. When rows==cols==
digits (the square 4x4/6x6 case), "no repeat in column" and "every
digit present in column" are equivalent by pigeonhole, so one rule
covers every case - no special-casing needed in the generator/solver.
"""
import json
import random
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_JSON = SCRIPT_DIR / "puzzles.json"


class Spec:
    def __init__(self, key, label, rows, cols, digits, box_h, box_w):
        self.key = key
        self.label = label
        self.rows = rows
        self.cols = cols
        self.digits = digits
        self.box_h = box_h
        self.box_w = box_w


SPECS = {
    "4x4": Spec("4x4", "4×4", 4, 4, 4, 2, 2),
    "6x6": Spec("6x6", "6×6", 6, 6, 6, 2, 3),
    "6x4": Spec("6x4", "6×4", 4, 6, 6, 2, 3),
}


def box_index(r, c, spec):
    return (r // spec.box_h) * (spec.cols // spec.box_w) + (c // spec.box_w)


def candidates(grid, r, c, spec):
    used = set()
    for cc in range(spec.cols):
        if grid[r][cc]:
            used.add(grid[r][cc])
    for rr in range(spec.rows):
        if grid[rr][c]:
            used.add(grid[rr][c])
    b = box_index(r, c, spec)
    for rr in range(spec.rows):
        for cc in range(spec.cols):
            if box_index(rr, cc, spec) == b and grid[rr][cc]:
                used.add(grid[rr][cc])
    return [d for d in range(1, spec.digits + 1) if d not in used]


def fill_grid(spec, rng):
    grid = [[0] * spec.cols for _ in range(spec.rows)]
    cells = [(r, c) for r in range(spec.rows) for c in range(spec.cols)]

    def backtrack(i):
        if i == len(cells):
            return True
        r, c = cells[i]
        opts = candidates(grid, r, c, spec)
        rng.shuffle(opts)
        for d in opts:
            grid[r][c] = d
            if backtrack(i + 1):
                return True
            grid[r][c] = 0
        return False

    ok = backtrack(0)
    assert ok, "failed to generate a full grid"
    return grid


def count_solutions(grid, spec, limit=2):
    cells = [(r, c) for r in range(spec.rows) for c in range(spec.cols) if grid[r][c] == 0]
    count = 0

    def backtrack(i):
        nonlocal count
        if count >= limit:
            return
        if i == len(cells):
            count += 1
            return
        r, c = cells[i]
        for d in candidates(grid, r, c, spec):
            grid[r][c] = d
            backtrack(i + 1)
            grid[r][c] = 0
            if count >= limit:
                return

    backtrack(0)
    return count


def make_puzzle(spec, target_givens, rng, max_tries=200):
    solution = fill_grid(spec, rng)
    puzzle = [row[:] for row in solution]
    cells = [(r, c) for r in range(spec.rows) for c in range(spec.cols)]
    rng.shuffle(cells)

    givens = spec.rows * spec.cols
    tries = 0
    for (r, c) in cells:
        if givens <= target_givens:
            break
        tries += 1
        if tries > max_tries:
            break
        saved = puzzle[r][c]
        puzzle[r][c] = 0
        test = [row[:] for row in puzzle]
        if count_solutions(test, spec, limit=2) == 1:
            givens -= 1
        else:
            puzzle[r][c] = saved

    return puzzle, solution, givens


def build_puzzles():
    rng = random.Random(20260915)
    plan = [
        # (spec_key, name, difficulty, target_givens)
        ("4x4", "Warm-up",   "easy",   9),
        ("4x4", "Quick One", "easy",   8),
        ("4x4", "Tighter",   "medium", 6),
        ("4x4", "Tightest",  "medium", 5),
        ("6x6", "First Six",   "easy",   22),
        ("6x6", "Six Steady",  "medium", 18),
        ("6x6", "Six Tricky",  "hard",   14),
        ("6x4", "Wide Easy",   "easy",   16),
        ("6x4", "Wide Medium", "medium", 13),
        ("6x4", "Wide Hard",   "hard",   11),
    ]

    puzzles = []
    for i, (spec_key, name, difficulty, target) in enumerate(plan, start=1):
        spec = SPECS[spec_key]
        puzzle, solution, givens = make_puzzle(spec, target, rng)
        puzzles.append({
            "id": i,
            "type": spec.key,
            "label": spec.label,
            "name": name,
            "difficulty": difficulty,
            "rows": spec.rows,
            "cols": spec.cols,
            "digits": spec.digits,
            "boxH": spec.box_h,
            "boxW": spec.box_w,
            "givens": givens,
            "puzzle": puzzle,
            "solution": solution,
        })
        print(f"[{i:2d}] {spec.label:>4} {difficulty:<6} {name:<12} givens={givens}")

    OUT_JSON.write_text(json.dumps(puzzles, indent=None, separators=(",", ":")))
    print(f"\nWrote {len(puzzles)} puzzles to {OUT_JSON}")


if __name__ == "__main__":
    build_puzzles()
