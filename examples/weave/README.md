# Synthetic pete-job walkthrough

> **Stand-in only: not Pete's H2 TwistTumbler.** `pete-job.obj` and the job
> recipe are deterministic synthetic fixtures. They are not matched to his
> Grasshopper G-code and do not establish a PotterBot print.

The pattern is canonical version-1 Clayline JSON: a sine weave at 3 mm
amplitude and 18 mm wavelength, 0.5 cycle of twist per layer, ridge-boost
extrusion, three bottom layers, chained seam, z-blend, and a level rim. The
shell recipe repeats those artist settings explicitly so the complete CLI
surface is visible and auditable.

From the repository root after installing Clayline, run:

```console
bash examples/weave/pete-job.sh demo-out/weave-pete-job
```

The recipe writes G-code, an offline 3D preview, and a JSON report from one
immutable result, then lints the exact G-code bytes. The synthetic form is
deliberately aggressive and currently reports an `overhang` warning. Lint may
still pass because that geometric warning is not a malformed-G-code error.
Inspect it before treating the file as a starting point for any machine work.

## Named synthetic job fixtures

The remaining family-C jobs reuse the same openly labeled synthetic mesh. Each
pattern is canonical, versioned JSON and freezes the visual distinction the PRD
names:

| Job | Pattern | Physical intent |
|---|---|---|
| `ribs-job` | [`ribs-job.pattern.json`](ribs-job.pattern.json) | 2.5 mm sine, twist 0: ribs align vertically on straight walls |
| `spiral-job` | [`spiral-job.pattern.json`](spiral-job.pattern.json) | 2.5 mm sine, twist 0.1: peaks advance gradually per layer |
| `flat-job` | [`flat-job.pattern.json`](flat-job.pattern.json) | zero-amplitude flat wave: clean vase pipeline with the scope off |

They are software fixtures, not machine recipes. Use `clayline weave` with the
shared `pete-job.obj`, the selected pattern, and reviewed printer settings; do
not inherit the provisional 2 mm / 5 mm synthetic values as real tumbler advice.
