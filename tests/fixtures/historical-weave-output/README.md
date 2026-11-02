# Immutable historical output

These gzip files contain the original emitted G-code, including its original
release and printer-profile stamps. They are test inputs, not current print
recommendations. No production default, historical acceptance artifact or
original hash was changed.

| Files | Exact original source used for recovery | Existing oracle |
| --- | --- | --- |
| `m11/*.gcode.gz` | `086a62a85f4716a1290842a5d507755a1e8bd6f5` (2026-08-02), original `test_m11_emission._result` | `tests/golden/weave/m11-gcode.sha256.json` |
| `m12/*.gcode.gz` | `1d5f46bd41c643a2265e40e7d2f7a4359258743b` (2026-08-03), original `test_m12_goldens._gcode` | `tests/golden/weave/m12-gcode.sha256.json` |
| `zellige-settle-off-two-pass.gcode.gz` | `f58ec426a78b62bb0642a0f8f4720fc9c3598304` (2026-08-02), original `_request(0.0, 12.0, settle=False)` | `SETTLE_OFF_GCODE_SHA256[2]`, `tests/test_zellige_clearance_convergence.py` |

Every uncompressed artifact was verified against its existing SHA-256 before
being added; `gzip.compress(..., mtime=0)` makes the packaging deterministic.
Tests read these self-contained artifacts and the explicit frozen v1.3.0
profile, so a public source snapshot needs no historical Git checkout or
private fixture to audit them. The injected-plow test now starts with its
exact original source bytes rather than assuming today's generator still
produces a July/August artifact.

Today's Weave output has a separate contract in
`tests/golden/weave/current-output-contract.json`, regenerated through the
production pipeline from `bb1b7c841ffba0de086ce51cff521bfbb151c141` on 2026-11-02.
Each file independently lints, and its complete actual warning counts and
layer count are recorded. Only the application release header is normalized
for hashing, after asserting it equals the current package release; pressure,
geometry, extrusion, warnings, source identities and every other byte remain
part of the hash.

The changes from the original Weave oracles include the documented October 3
nearest-top rule (`1aad095`): a 30 mm cylinder now finishes at Z30 rather than
Z28, and a cone's spiral/rim likewise reaches its full height. Later interior
work (`c209a7b`, 2026-08-04, followed by `ac7bf3b`, 2026-10-07) joins the solid
lid into one welded run instead of six separate runs.
The current solid lid still reports its overhang; the infill tumbler reports
its ramp-bridge and drift warnings. These are retained in the current contract.
