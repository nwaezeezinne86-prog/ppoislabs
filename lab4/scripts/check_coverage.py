#!/usr/bin/env python3
"""Runs gcov (JSON mode) on a coverage build directory and fails if project line coverage is below a threshold.

Usage: check_coverage.py <coverage-dir> <min-percent>

Only files under include/ and src/ are counted (tests and system headers are ignored). A line of a template or an
inline function counts as covered when any instantiation executed it.
"""
import glob
import json
import os
import subprocess
import sys

PROJECT_DIRS = ("include/", "src/")


def collect(directory):
    """Returns {source file: {line number: executed?}} for project files."""
    coverage = {}
    for notes in sorted(glob.glob(os.path.join(directory, "*.gcno"))):
        run = subprocess.run(["gcov", "--json-format", "--stdout", notes], cwd=directory,
                             capture_output=True, text=True, check=True)
        for document in run.stdout.splitlines():
            for source in json.loads(document)["files"]:
                name = source["file"]
                if not name.startswith(PROJECT_DIRS):
                    continue
                lines = coverage.setdefault(name, {})
                for entry in source["lines"]:
                    number = entry["line_number"]
                    lines[number] = lines.get(number, False) or entry["count"] > 0
    return coverage


def main():
    directory, threshold = sys.argv[1], float(sys.argv[2])
    coverage = collect(directory)
    if not coverage:
        print("No coverage data found")
        return 1
    executed_sum = total_sum = 0
    for name, lines in sorted(coverage.items()):
        executed, total = sum(lines.values()), len(lines)
        if total == 0:
            continue
        executed_sum += executed
        total_sum += total
        print(f"{name}: {executed}/{total} lines ({100.0 * executed / total:.1f}%)")
    percent = 100.0 * executed_sum / total_sum
    print(f"TOTAL: {executed_sum}/{total_sum} lines ({percent:.1f}%), required {threshold:.0f}%")
    return 0 if percent >= threshold else 1


if __name__ == "__main__":
    sys.exit(main())
