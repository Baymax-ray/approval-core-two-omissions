"""Independent set-based full-target replay of a constructed original core.

Does not import the constructor, follow its trace, or reuse its gain function.
"""

import argparse
from itertools import combinations
import json
from pathlib import Path

if not __debug__:
    raise SystemExit("Run without Python -O: verification requires active assertions.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance", type=Path)
    parser.add_argument("construction", type=Path)
    args = parser.parse_args()
    data = json.loads(args.instance.read_text(encoding="utf-8"))
    certificate = json.loads(args.construction.read_text(encoding="utf-8"))
    m = data["m"]
    k = m - 2
    assert type(m) is int and m >= 3
    assert type(data.get("k", k)) is int and data.get("k", k) == k
    candidates = set(range(m))
    voters = []
    for row in data["ballots"]:
        encoded, multiplicity = row["mask"], row["multiplicity"]
        assert type(encoded) is int and 0 <= encoded < 2 ** m
        assert type(multiplicity) is int and multiplicity > 0
        approved = {j for j in range(m) if (encoded // (2 ** j)) % 2}
        voters.append((approved, multiplicity))
    n = sum(weight for _, weight in voters)
    assert n > 0
    assert all(type(c) is int for c in certificate["committee"])
    assert type(certificate["committee_mask"]) is int
    assert type(certificate["m"]) is int and certificate["m"] == m
    assert type(certificate["k"]) is int and certificate["k"] == k
    assert type(certificate["n"]) is int and certificate["n"] == n
    committee = set(certificate["committee"])
    assert len(certificate["committee"]) == len(committee) == k
    assert committee <= candidates
    assert sum(2 ** c for c in committee) == certificate["committee_mask"]
    checks = 0
    for size in range(1, k + 1):
        for chosen in combinations(sorted(candidates), size):
            target = set(chosen)
            q = sum(weight for approved, weight in voters
                    if len(approved.intersection(target)) > len(approved.intersection(committee)))
            if k * q >= n * size:
                raise AssertionError({"target": chosen, "q": q, "kq": k * q, "nt": n * size})
            checks += 1
    print("INDEPENDENT_CORE_PASS", json.dumps(
        {"m": m, "k": k, "n": n, "committee": sorted(committee), "targets_checked": checks},
        sort_keys=True))


if __name__ == "__main__":
    main()

