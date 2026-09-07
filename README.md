# Hare core with two omissions

Every finite approval election with `m >= 3` candidates and `k = m - 2`
seats has an ordinary deterministic Hare-core committee. The theorem allows
arbitrary approval sets and voter multiplicities, overlapping deviations,
and blocking at exact Hare-quota equality.

The proof is analytic. An overlap bound for repeated strict gainers supports
a core-preserving contraction and induction. The result is uniform in `m`;
it is not a claim for unrestricted `(m,k)` or for weak Nash certificates.
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

The verifier uses Python sets and does not import the constructor or rely on
its trace. It verifies the final committee, its stated `m`, `k`, `n` and mask,
but does not certify the individual optimization decisions in the trace.
All quota tests use exact integer multiplication. The constructor evaluates
PAV with exact rational arithmetic. Both programs explicitly reject Python
optimization (`-O` or `-OO`) because their checks require active assertions.
They are exhaustive reference implementations, not efficient algorithms.
Neither program nor the example is a premise of the universal proof.

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
