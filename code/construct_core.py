"""Exact exhaustive construction of a Hare or Droop core with two omissions.

No numerical solver, floating quota, or inherited research code is used.
This diagnostic implementation is not a premise of the analytic theorem.
"""

import argparse
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path

if not __debug__:
    raise SystemExit("Run without Python -O: verification requires active assertions.")


def subsets(candidates, size):
    for selected in combinations(candidates, size):
        yield sum(1 << c for c in selected)


def target_masks(candidates, k):
    for size in range(1, k + 1):
        yield from subsets(candidates, size)


def gainers(profile, committee, target):
    return [(ballot, count) for ballot, count in profile
            if (ballot & target).bit_count() > (ballot & committee).bit_count()]


def first_blocker(profile, candidates, k, committee, droop=False):
    n = sum(count for _, count in profile)
    for target in target_masks(candidates, k):
        q = sum(count for _, count in gainers(profile, committee, target))
        blocked = ((k + 1) * q > n * target.bit_count() if droop
                   else k * q >= n * target.bit_count())
        if blocked:
            return target, q
    return None


def construct(profile, candidates, trace, droop=False):
    k = len(candidates) - 2
    n = sum(count for _, count in profile)
    assert k >= (0 if droop else 1) and n > 0
    harmonic = [Fraction(0)]
    for j in range(1, k + 1):
        harmonic.append(harmonic[-1] + Fraction(1, j))

    def pav(committee):
        return sum((count * harmonic[(ballot & committee).bit_count()]
                    for ballot, count in profile), Fraction(0))

    committee = max(subsets(candidates, k), key=pav)
    blocker = first_blocker(profile, candidates, k, committee, droop)
    record = {"n": n, "k": k, "candidates": list(candidates),
              "pav_committee": committee, "pav_value": str(pav(committee))}
    trace.append(record)
    if blocker is None:
        record.update({"status": "CORE_LEAF", "returned_committee": committee})
        return committee

    target, q = blocker
    dropped = gainers(profile, committee, target)
    residual = [(ballot, count) for ballot, count in profile
                if (ballot & target).bit_count() <= (ballot & committee).bit_count()]
    remaining_candidates = tuple(c for c in candidates if not target & (1 << c))
    residual_mask = sum(1 << c for c in remaining_candidates)
    residual = [(ballot & residual_mask, count) for ballot, count in residual]
    next_k = k - target.bit_count()
    next_n = n - q
    assert (0 if droop else 1) <= next_k < k and next_n > 0
    if droop:
        assert (k + 1) * q > n * target.bit_count()
        assert (k + 1) * next_n < n * (next_k + 1)
    else:
        assert k * q >= n * target.bit_count()
        assert k * next_n <= n * next_k
    record.update({"status": "CONTRACTION", "target": target,
                   "strict_gainer_count": q, "dropped_types": dropped,
                   "residual_n": next_n, "residual_k": next_k})
    child = construct(residual, remaining_candidates, trace, droop)
    answer = target | child
    assert answer.bit_count() == k
    assert first_blocker(profile, candidates, k, answer, droop) is None
    record["returned_committee"] = answer
    return answer


def validate_instance(instance):
    m = instance["m"]
    assert isinstance(m, int) and not isinstance(m, bool) and m >= 3
    assert type(instance.get("k", m - 2)) is int and instance.get("k", m - 2) == m - 2
    profile = []
    for row in instance["ballots"]:
        ballot, count = row["mask"], row["multiplicity"]
        assert isinstance(ballot, int) and not isinstance(ballot, bool)
        assert isinstance(count, int) and not isinstance(count, bool)
        assert 0 <= ballot < (1 << m) and count > 0
        profile.append((ballot, count))
    assert profile
    return m, profile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instance", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--droop", action="store_true",
                        help="Use strict Droop blocking: (k+1)*q > n*|T|.")
    args = parser.parse_args()
    instance = json.loads(args.instance.read_text(encoding="utf-8"))
    m, profile = validate_instance(instance)
    trace = []
    committee = construct(profile, tuple(range(m)), trace, args.droop)
    status = "EXACT_CONSTRUCTED_DROOP_CORE" if args.droop else "EXACT_CONSTRUCTED_CORE"
    result = {"status": status, "m": m, "k": m - 2,
              "n": sum(count for _, count in profile), "committee_mask": committee,
              "committee": [c for c in range(m) if committee & (1 << c)], "trace": trace}
    serialized = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")


if __name__ == "__main__":
    main()
