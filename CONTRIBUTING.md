# Contributing to Clayline

Clayline controls physical paste-printing hardware. Contributions are welcome,
but reproducibility, warning honesty, and machine evidence take priority over a
clean-looking demo.

## Development setup

Use Python 3.11 or newer and install all development and UI dependencies from the
repository root:

```console
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev,ui]'
make check
```

The emission core is part of Clayline. A fresh install resolves only the declared
package-index dependencies; the test suite and runtime must remain offline.

`make check` is the required local gate. It runs Ruff linting, Ruff formatting
checks, the complete pytest suite, and the fixture inventory validator. Run the
whole command before proposing a change, not only the focused test you added.

## Keep one real pipeline

The Python API, CLI, and local web UI are shells over the same ingest, plan, stack,
emit, preview, report, and lint path. Preview must consume the exact prepared
emission trace used to write G-code. Do not create display-only geometry, hardcode
demo data, or add a control that is not wired end to end.

Every public function should be typed. Internal units are millimetres, mm/s, and
mm³. Runtime code must not call the network or emit telemetry.

## Fixtures and reproducibility

Clayline keeps three complementary fixture groups:

- tile fixtures derived from the three reference photos;
- adversarial SVGs covering real Illustrator/Inkscape exports, transforms, units,
  degenerate geometry, open paths, crossings, tight turns, and stress cases;
- job fixtures covering calibrated/drape Z and sequential multi-page output.

Do not replace a real or quirky fixture with a cleaner synthetic substitute.
Synthetic tests are useful only in addition to the real fixture families. If a
change alters geometry, warnings, stacking, G-code, or a report, test both the
small isolated contract and the relevant production fixture.

Golden output must be generated with reproducible mode enabled. Update it only
through the production pipeline, inspect the diff, lint every changed G-code file,
and document why the behavior changed. Never suppress a warning or round away a
difference merely to make a golden pass.

## Evidence discipline

Milestone claims require a bundle under `docs/verification/M<n>/` as defined in
the handoff:

- complete `make check` output from a clean clone and fresh environment;
- real plan/preview artifacts where required;
- lint reports and the actual G-code where required;
- a `STATUS.md` that distinguishes software verification, independent
  verification, hardware calibration, and physical acceptance.

Screenshots must come from the running artifact. Generated output must identify
the exact parameters and profile. Open images and HTML previews yourself; a
worker's summary is not visual verification. Keep warnings and limitations in the
evidence even when they make the result look unfinished.

## Never guess hardware facts

A bundled profile may be marked `verified = true` only when its values trace to
machine documentation or a successful supplied file. Record that source. Unknown
nozzles, bounds, speeds, start/end blocks, cartridge dimensions, extrusion modes,
and pause behavior stay unknown.

Generic profiles must remain visibly unverified. A software lint PASS is not a
physical safety or print-quality result. Do not claim calibration, a PotterBot
print, or acceptance without the corresponding machine-side evidence.

## Pull request checklist

Before handing off a change:

1. Keep the diff scoped; preserve unrelated work already in the tree.
2. Add focused tests and exercise the relevant real fixture family.
3. Run `make check` from the supported environment.
4. Generate deterministic artifacts with `--reproducible` where applicable.
5. Lint changed G-code independently and inspect visual artifacts.
6. Update the relevant status/evidence without overstating the gate.
7. Recheck CLI help, Python signatures, and UI disabled-state hints if an
   interface changed.

## License and contributor agreement

Clayline is distributed under the GNU General Public License, version 3 (see
[LICENSE](LICENSE)). Copyright in the project is held by Pete Katz.

By submitting a contribution (a pull request, patch, fixture, document, or any
other material) you agree that:

1. you wrote it, or otherwise have the right to submit it under these terms;
2. you license it to the project under GPL-3.0; and
3. you additionally grant Pete Katz a perpetual, worldwide, non-exclusive,
   royalty-free licence to use, reproduce, modify, sublicense, and distribute
   your contribution under any licence, including proprietary and commercial
   licences, as part of Clayline or works derived from it.

You keep your copyright; this is a licence grant, not an assignment. It keeps
Clayline free under the GPL while leaving the maintainer able to offer it under
other terms later. Record your agreement by adding a
`Signed-off-by: Your Name <email>` line to each commit (`git commit -s`).

Keep dependencies GPL-compatible or permissively licensed. Do not copy code from
Cura, CuraEngine, or other slicers. Implement behavior from documented
requirements and understanding, and preserve attribution for compatible upstream
work.
