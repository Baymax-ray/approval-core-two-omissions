# Droop core with two omissions

Every finite approval election with `m >= 3` candidates and `k = m - 2`
seats has a deterministic Droop-core committee, and hence an ordinary
deterministic Hare-core committee. The theorem allows
arbitrary approval sets and voter multiplicities, overlapping deviations,
and blocking at exact Hare-quota equality.
The one-outsider bound also covers zero or one omission, giving Droop-core
existence whenever `m-k <= 2` and `1 <= k <= m`.
Hare blocking means `k*q >= n*|T|`; Droop blocking means
`(k+1)*q > n*|T|`. Equality blocks only under the Hare convention.

The proof is analytic. An overlap bound for repeated strict gainers supports
a core-preserving contraction and induction. The code implements this
construction, independently checks its outputs, and reproduces the examples;
it is not a premise of the proof. The result is uniform in `m`;
it is not a claim for unrestricted `(m,k)`.
"Two omissions" means two unselected candidates, not at-most-two disapprovals
on each ballot.

## Read the result

- [Manuscript PDF](paper/main.pdf)
- [Self-contained LaTeX source](paper/main.tex)
- Repository: [Baymax-ray/approval-core-two-omissions](https://github.com/Baymax-ray/approval-core-two-omissions)

Author: Jiarui Fang, Boston University. The manuscript includes a concise
disclosure of GPT-6 Astra use in the mathematical work, code and writing.
The author retains responsibility for the submitted content.

## Exact construction and independent verification

Use Python 3.10 or later. There are no third-party Python dependencies.
Run from this directory:

```text
python -B code/construct_core.py examples/election.json
python -B code/verify_core.py examples/election.json examples/core.json
```

The constructor prints a core committee and a recursive trace. To save a
fresh result without replacing the supplied example:

```text
python -B code/construct_core.py examples/election.json --output result.json
python -B code/verify_core.py examples/election.json result.json
```

The supplied election has `m=11`, `k=9`, `n=18`. Its unique PAV maximizer is
blocked at equality, `9*10 = 18*5`. The contraction leaves eight voters and
four seats on six candidates. The returned original committee has mask 511.
Independent verification checks all 2035 original nonempty targets of size
at most nine and prints `INDEPENDENT_CORE_PASS`.

For the stronger Droop criterion, use `--droop` explicitly in both commands:

```text
python -B code/construct_core.py examples/election.json --droop --output droop-result.json
python -B code/verify_core.py examples/election.json droop-result.json --droop
```

The second command prints `INDEPENDENT_DROOP_CORE_PASS`. The verifier's
command-line option selects the quota; it does not infer stability from a
certificate's status or trace. The default Hare output is unchanged.
The Droop constructor permits the auxiliary zero-seat residual instance
used in the proof; top-level inputs still require `m >= 3` and `k = m-2`.

The verifier uses Python sets and does not import the constructor or rely on
its trace. It verifies the final committee, its stated `m`, `k`, `n` and mask,
but does not certify the individual optimization decisions in the trace.
All quota tests use exact integer multiplication. The constructor evaluates
PAV with exact rational arithmetic. All three programs explicitly reject Python
optimization (`-O` or `-OO`) because their checks require active assertions.
They are exhaustive reference implementations, not efficient algorithms.
At a call with `m` candidates, PAV optimization compares `m*(m-1)/2`
committees, while a full blocking test examines `2**m-m-2` targets.
None of these finite checks is a premise of the analytic existence proofs.

### An example separating Hare and Droop

[examples/droop_distinction.json](examples/droop_distinction.json) relabels
[Peters, Example 6.1](https://arxiv.org/html/2501.18304v2#S6.Thmtheorem1).
It has `m=8`, `k=6`, `n=24`, with `B={0,1}`, `X={2,3}` and `Y={4,5,6,7}`.
Seven voters approve `X union {0}`, seven approve `X union {1}`, and ten
approve `Y`. The unique global PAV committee is `W0=X union Y` (mask 252).
It is Hare core but is Droop-blocked by `F=B union X` (mask 15):
`6*14 = 84 < 24*4 = 96 < 7*14 = 98`.

```text
python -B code/construct_core.py examples/droop_distinction.json --output distinction-hare.json
python -B code/verify_core.py examples/droop_distinction.json distinction-hare.json
python -B code/construct_core.py examples/droop_distinction.json --droop --output distinction-droop.json
python -B code/verify_core.py examples/droop_distinction.json distinction-droop.json --droop
```

The Hare result retains mask 252. The Droop construction fixes `F`, leaving
ten voters, four candidates and two seats, and returns mask 63 (`F union {4,5}`).
Each independent verification checks all 246 original targets under its
selected quota. Section 6.1 also gives a direct all-target Hare-stability
argument, rather than inferring stability from a single failed deviation.

### A nonzero repeated-support example

[examples/repeated_support.json](examples/repeated_support.json) has `m=11`,
`k=9`, `n=99`. Write `B={0,1}`, `X={2,3,4}`, `Y={5,6,7,8,9,10}` and `y1=5`.

| Approval set | Multiplicity | Mask |
|---|---:|---:|
| `X` together with candidate `0` | 27 | 29 |
| `X` together with candidate `1` | 27 | 30 |
| `Y` | 44 | 2016 |
| `B` together with `y1` | 1 | 35 |

The unique global PAV maximizer is `W0=X union Y` (mask 2044).
The target `F=B union X` has 55 strict gainers and blocks at Hare equality:
`9*55 = 99*5`. The residual election consists of 44 voters who all approve
`Y`, with four seats. All 15 four-element subsets of `Y` are residual cores.

The last voter strictly improves from utility 1 at `W0` to 2 at `F`.
For example, choose the residual committee `{6,7,8,9}`. The later target
`T={0,1,5}` gives that voter utility 3, so `r=1` and `s=|F intersect T|=2`.
This target is **not affordable** (`9*1 < 99*3`, also `10*1 < 99*3` under
Droop). It demonstrates that the repeated-support lemma covers later
targets regardless of affordability.

```text
python -B code/verify_repeated_support.py examples/repeated_support.json
```

This independent set-based checker compares all 55 PAV committees, verifies
all 15 residual cores and their lifts under both quota conventions, and
checks the overlap bound on all `15*2035 = 30525` completion-target pairs.
Exactly 1235 pairs have positive repeated support. It prints
`REPEATED_SUPPORT_PASS` and an exact summary. The profile was suggested in
pre-submission feedback; this checker independently recomputes its claims.

## Input format

`m` is an integer at least three. Optional `k` must be the integer `m-2`.
Candidates are numbered `0,...,m-1`. Each row of `ballots` has an integer
`mask` and a positive integer `multiplicity`. Bit `j` is one exactly when
candidate `j` is approved. Mask zero represents empty approvals. Repeated
rows are permitted. Boolean and floating-point substitutes for these integer
fields are rejected. `candidate_labels` is optional descriptive metadata.
See [examples/election.json](examples/election.json) for a complete instance.

At each contraction the constructor creates a separate ordinary residual
election. The manuscript proves the quota-transfer inequality; it does not
silently use a residual quota for an original blocking test. Every lifted
committee is checked against its parent electorate, and the independent
verifier always uses the original input electorate and quota.

## Build the manuscript

From `paper/`, run:

```text
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The source includes its bibliography and needs no external source files.
Standard LaTeX packages are sufficient. Exact code checks were run with
CPython 3.10.16, and the PDF was built with TeX Live 2026.

## Integrity and rights

`SHA256SUMS` records the distributed source, example and PDF identities.
It is an integrity inventory, not evidence of mathematical correctness.
Generated build files and user-created results are not part of that inventory.

The manuscript in `paper/` is copyright 2026 Jiarui Fang, all rights reserved.
Code and accompanying non-manuscript material use the [MIT license](code/LICENSE).
See [LICENSE](LICENSE) for the exact scope. No manuscript reuse license is
granted by the code license.
