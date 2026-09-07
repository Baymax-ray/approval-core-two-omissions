"""Independent exact replay of the supplied 99-voter repeated-support example.

This finite diagnostic is not a proof of the general repeated-support lemma.
The program uses sets and Fraction; it does not import the constructor.
"""

import argparse
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path

if not __debug__:
    raise SystemExit("Run without Python -O: verification requires active assertions.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance", type=Path)
    args = parser.parse_args()
    data = json.loads(args.instance.read_text(encoding="utf-8"))
    assert type(data["m"]) is int and data["m"] == 11
    assert type(data["k"]) is int and data["k"] == 9
    m, k = data["m"], data["k"]
    candidates = frozenset(range(m))
    profile = []
    encoded_rows = []
    for row in data["ballots"]:
        mask, count = row["mask"], row["multiplicity"]
        assert type(mask) is int and 0 <= mask < 2 ** m
        assert type(count) is int and count > 0
        ballot = frozenset(c for c in candidates if (mask // 2 ** c) % 2)
        profile.append((ballot, count))
        encoded_rows.append((mask, count))
    assert sorted(encoded_rows) == [(29, 27), (30, 27), (35, 1), (2016, 44)]
    n = sum(count for _, count in profile)
    assert n == 99

    def score(committee):
        return sum((count * sum((Fraction(1, j)
                    for j in range(1, len(ballot & committee) + 1)), Fraction(0))
                    for ballot, count in profile), Fraction(0))

    def gains(committee, target):
        return {j for j, (ballot, _) in enumerate(profile)
                if len(ballot & target) > len(ballot & committee)}

    def weight(indices):
        return sum(profile[j][1] for j in indices)

    anchor = frozenset(range(2, 11))
    fixed = frozenset(range(5))
    committees = [frozenset(w) for w in combinations(sorted(candidates), k)]
    assert len(committees) == 55
    gaps = [score(anchor) - score(w) for w in committees if w != anchor]
    assert min(gaps) > 0
    deleted = gains(anchor, fixed)
    q0 = weight(deleted)
    assert q0 == 55 and k * q0 == n * len(fixed)

    residual_candidates = candidates - fixed
    residual_k = k - len(fixed)
    residual_n = n - q0
    assert (residual_k, residual_n) == (4, 44)
    targets = [frozenset(t) for size in range(1, k + 1)
               for t in combinations(sorted(candidates), size)]
    assert len(targets) == 2035
    repeat_checks = positive_repeat = lifts = 0
    for chosen in combinations(sorted(residual_candidates), residual_k):
        residual_core = frozenset(chosen)
        for size in range(1, residual_k + 1):
            for chosen_target in combinations(sorted(residual_candidates), size):
                target = frozenset(chosen_target)
                q = weight(gains(residual_core, target) - deleted)
                assert (residual_k + 1) * q <= residual_n * size
                assert residual_k * q < residual_n * size
        lifted = fixed | residual_core
        assert len(lifted) == k
        for target in targets:
            strict_gainers = gains(lifted, target)
            q = weight(strict_gainers)
            r = weight(deleted & strict_gainers)
            s = len(fixed & target)
            assert (k + 1) * r <= n * s
            assert k * q < n * len(target)
            assert (k + 1) * q <= n * len(target)
            repeat_checks += 1
            positive_repeat += int(r > 0)
        lifts += 1
    assert (lifts, repeat_checks, positive_repeat) == (15, 30525, 1235)

    # A specific second strict improvement. It is deliberately not affordable.
    lifted = fixed | frozenset({6, 7, 8, 9})
    target = frozenset({0, 1, 5})
    repeated = deleted & gains(lifted, target)
    assert weight(repeated) == 1 and len(fixed & target) == 2
    ballot = profile[next(iter(repeated))][0]
    assert (len(ballot & anchor), len(ballot & fixed),
            len(ballot & lifted), len(ballot & target)) == (1, 2, 2, 3)
    assert weight(gains(lifted, target)) == 1
    print("REPEATED_SUPPORT_PASS", json.dumps({
        "m": m, "k": k, "n": n, "pav_committees_checked": len(committees),
        "unique_pav_mask": sum(2 ** c for c in anchor),
        "pav_gap": str(min(gaps)), "initial_strict_gainers": q0,
        "residual_cores_lifted": lifts, "repeat_bound_checks": repeat_checks,
        "positive_repeat_cases": positive_repeat,
        "explicit_repeat_witness": {"committee": sorted(lifted),
                                    "target": sorted(target), "r": 1, "s": 2}
    }, sort_keys=True))


if __name__ == "__main__":
    main()
