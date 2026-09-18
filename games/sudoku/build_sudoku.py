#!/usr/bin/env python3
"""
Generates a collection of mini/full-Sudoku puzzles and writes them to
puzzles.json, then embeds that into a self-contained games/sudoku.html
(same build pattern as cross-word/build_puzzles.py and
wordweave/build_game.py).

Four variants:
  - 4x4  : 4 rows x 4 cols, digits 1-4, 2x2 boxes. Classic mini sudoku.
  - 6x6  : 6 rows x 6 cols, digits 1-6, 2x3 boxes. Classic 6x6 sudoku.
  - 6x4  : 4 rows x 6 cols ("6 wide x 4 tall"), digits 1-6, 2x3 boxes.
           Rows and boxes are full 1-6 permutations same as any sudoku;
           columns only have 4 cells so they can't contain all 6 digits -
           column uniqueness (no repeat in a column) is still enforced,
           it just can't be "every digit present" for that axis. This is
           the standard way a non-square rectangular sudoku variant is
           defined.
  - 9x9  : the classic full-size sudoku, digits 1-9, 3x3 boxes.

All variants share one constraint rule: a digit may not already appear
elsewhere in the same row, same column, or same box. When rows==cols==
digits (the square 4x4/6x6/9x9 case), "no repeat in column" and "every
digit present in column" are equivalent by pigeonhole, so one rule
covers every case - no special-casing needed in the generator/solver.

Solving/counting uses bitmasks + MRV (minimum-remaining-values) cell
ordering rather than fixed left-to-right cell order - a plain
brute-force solver in fixed order is far too slow to check uniqueness
on a sparse 9x9 board (down to ~20 givens).
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
        self.n_boxes_per_row = cols // box_w
        self.full_mask = (1 << digits) - 1


SPECS = {
    "4x4": Spec("4x4", "4×4", 4, 4, 4, 2, 2),
    "6x6": Spec("6x6", "6×6", 6, 6, 6, 2, 3),
    "6x4": Spec("6x4", "6×4", 4, 6, 6, 2, 3),
    "9x9": Spec("9x9", "9×9", 9, 9, 9, 3, 3),
}


def box_index(r, c, spec):
    return (r // spec.box_h) * spec.n_boxes_per_row + (c // spec.box_w)


class Masks:
    """Tracks which digits are already used per row/col/box as bitmasks."""

    def __init__(self, grid, spec):
        self.spec = spec
        self.row = [0] * spec.rows
        self.col = [0] * spec.cols
        self.box = [0] * (spec.n_boxes_per_row * (spec.rows // spec.box_h))
        for r in range(spec.rows):
            for c in range(spec.cols):
                d = grid[r][c]
                if d:
                    self.place(r, c, d)

    def place(self, r, c, d):
        bit = 1 << (d - 1)
        self.row[r] |= bit
        self.col[c] |= bit
        self.box[box_index(r, c, self.spec)] |= bit

    def remove(self, r, c, d):
        bit = ~(1 << (d - 1))
        self.row[r] &= bit
        self.col[c] &= bit
        self.box[box_index(r, c, self.spec)] &= bit

    def candidates_mask(self, r, c):
        used = self.row[r] | self.col[c] | self.box[box_index(r, c, self.spec)]
        return self.spec.full_mask & ~used


def mask_to_digits(mask, rng=None):
    digits = []
    d = 1
    while mask:
        if mask & 1:
            digits.append(d)
        mask >>= 1
        d += 1
    if rng is not None:
        rng.shuffle(digits)
    return digits


def solve_mrv(grid, spec, masks, empties, rng, count_limit=None, first_only=False):
    """Fills `grid` in place via MRV backtracking.

    - first_only: stop at the first solution found (used for full-grid
      generation) and leave that solution in `grid`.
    - count_limit: count solutions up to this many (used for uniqueness
      checks); grid is restored to all-empty-cells-as-0 afterwards.
    Returns the number of solutions found (1 if first_only and one exists).
    """
    remaining = list(empties)
    found = [0]

    def backtrack():
        if not remaining:
            found[0] += 1
            return first_only or (count_limit is not None and found[0] >= count_limit)

        best_i, best_mask, best_count = -1, 0, None
        for i, (r, c) in enumerate(remaining):
            m = masks.candidates_mask(r, c)
            cnt = bin(m).count("1")
            if cnt == 0:
                return False
            if best_count is None or cnt < best_count:
                best_i, best_mask, best_count = i, m, cnt
                if cnt == 1:
                    break

        r, c = remaining[best_i]
        remaining[best_i], remaining[-1] = remaining[-1], remaining[best_i]
        remaining.pop()

        stop = False
        for d in mask_to_digits(best_mask, rng):
            grid[r][c] = d
            masks.place(r, c, d)
            if backtrack():
                stop = True
                break
            masks.remove(r, c, d)
            grid[r][c] = 0
        if not stop:
            remaining.append((r, c))
            remaining[best_i], remaining[-1] = remaining[-1], remaining[best_i]
        return stop

    backtrack()
    return found[0]


def fill_grid(spec, rng):
    grid = [[0] * spec.cols for _ in range(spec.rows)]
    masks = Masks(grid, spec)
    empties = [(r, c) for r in range(spec.rows) for c in range(spec.cols)]
    ok = solve_mrv(grid, spec, masks, empties, rng, first_only=True)
    assert ok, "failed to generate a full grid"
    return grid


def count_solutions(grid, spec, limit=2):
    masks = Masks(grid, spec)
    empties = [(r, c) for r in range(spec.rows) for c in range(spec.cols) if grid[r][c] == 0]
    rng = random.Random(0)  # order doesn't matter for counting
    return solve_mrv(grid, spec, masks, empties, rng, count_limit=limit)


def make_puzzle(spec, target_givens, rng, max_tries=None):
    solution = fill_grid(spec, rng)
    puzzle = [row[:] for row in solution]
    cells = [(r, c) for r in range(spec.rows) for c in range(spec.cols)]
    rng.shuffle(cells)
    if max_tries is None:
        max_tries = len(cells)

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


def verify_puzzle(entry):
    """Checks a built puzzle entry is internally consistent: givens match
    the solution, the solution is a fully valid grid for its spec, and the
    puzzle (as given) has exactly one solution."""
    spec = SPECS[entry["type"]]
    puzzle = entry["puzzle"]
    solution = entry["solution"]

    for r in range(spec.rows):
        for c in range(spec.cols):
            if puzzle[r][c] != 0 and puzzle[r][c] != solution[r][c]:
                return False, "given cell doesn't match solution"

    masks = Masks([[0] * spec.cols for _ in range(spec.rows)], spec)
    for r in range(spec.rows):
        for c in range(spec.cols):
            d = solution[r][c]
            if d < 1 or d > spec.digits:
                return False, "solution digit out of range"
            bit = 1 << (d - 1)
            if masks.row[r] & bit:
                return False, "row conflict in solution"
            if masks.col[c] & bit:
                return False, "col conflict in solution"
            b = box_index(r, c, spec)
            if masks.box[b] & bit:
                return False, "box conflict in solution"
            masks.place(r, c, d)

    grid = [row[:] for row in puzzle]
    if count_solutions(grid, spec, limit=2) != 1:
        return False, "puzzle does not have a unique solution"

    return True, "ok"


def build_puzzles():
    rng = random.Random(20260915)
    # 4 sizes: 10 puzzles each for 4x4/6x6/6x4, 20 for 9x9 = 50 total.
    # Within a size, difficulty is ramped by shrinking the target
    # given-count across a few puzzles per tier (more givens = easier).
    # Names are "<Size label> <difficulty> N".
    difficulty_plan = {
        "4x4": [
            ("easy", 10), ("easy", 9), ("easy", 8),
            ("medium", 7), ("medium", 6), ("medium", 6), ("medium", 5),
            ("hard", 5), ("hard", 4), ("hard", 4),
        ],
        "6x6": [
            ("easy", 24), ("easy", 22), ("easy", 20),
            ("medium", 19), ("medium", 18), ("medium", 17), ("medium", 16),
            ("hard", 15), ("hard", 14), ("hard", 13),
        ],
        "6x4": [
            ("easy", 17), ("easy", 16), ("easy", 15),
            ("medium", 14), ("medium", 13), ("medium", 13), ("medium", 12),
            ("hard", 11), ("hard", 11), ("hard", 10),
        ],
        "9x9": [
            ("easy", 44), ("easy", 42), ("easy", 40), ("easy", 38), ("easy", 36), ("easy", 34),
            ("medium", 33), ("medium", 32), ("medium", 31), ("medium", 30),
            ("medium", 29), ("medium", 28), ("medium", 27), ("medium", 26),
            ("hard", 25), ("hard", 24), ("hard", 23), ("hard", 22), ("hard", 21), ("hard", 20),
        ],
    }

    plan = []
    for spec_key in ("4x4", "6x6", "6x4", "9x9"):
        counters = {"easy": 0, "medium": 0, "hard": 0}
        label = SPECS[spec_key].label
        for difficulty, target in difficulty_plan[spec_key]:
            counters[difficulty] += 1
            name = f"{label} {difficulty.capitalize()} {counters[difficulty]}"
            plan.append((spec_key, name, difficulty, target))

    puzzles = []
    for i, (spec_key, name, difficulty, target) in enumerate(plan, start=1):
        spec = SPECS[spec_key]
        puzzle, solution, givens = make_puzzle(spec, target, rng)
        entry = {
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
        }
        puzzles.append(entry)
        print(f"[{i:2d}] {spec.label:>4} {difficulty:<6} {name:<14} givens={givens}")

    print("\nVerifying all puzzles...")
    failures = []
    for entry in puzzles:
        ok, reason = verify_puzzle(entry)
        if not ok:
            failures.append((entry["id"], entry["name"], reason))
    if failures:
        for pid, name, reason in failures:
            print(f"  FAIL [{pid}] {name}: {reason}")
        raise SystemExit(f"{len(failures)} puzzle(s) failed verification")
    print(f"All {len(puzzles)} puzzles verified OK (valid grid, matches givens, unique solution).")

    OUT_JSON.write_text(json.dumps(puzzles, indent=None, separators=(",", ":")))
    print(f"\nWrote {len(puzzles)} puzzles to {OUT_JSON}")
    embed_into_html(puzzles)


def embed_into_html(puzzles):
    html_path = SCRIPT_DIR.parent / "sudoku.html"
    text = html_path.read_text()
    payload = json.dumps(puzzles, indent=None, separators=(",", ":"))
    marker_start = "const PUZZLES = "
    start = text.index(marker_start) + len(marker_start)
    end = text.index(";\n", start)
    text = text[:start] + payload + text[end:]
    html_path.write_text(text)
    print(f"Embedded {len(puzzles)} puzzles into {html_path}")


if __name__ == "__main__":
    build_puzzles()
