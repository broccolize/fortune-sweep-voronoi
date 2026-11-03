# Genuine Problems and Corrections

Actual investigation date: 10 November 2026. The following failures were observed
and corrected during this session; raw failing evidence is retained.

## P001 Rounded zero length edges rejected valid cell queries

- Symptom: the two-site diagonal case and nine cocircular sites failed polygon
  ownership with a reported hole despite passing the total-area check.
- Investigation: inspected consecutive polygon endpoints and cross products;
  reproduced using `test_degenerate_cells[two]` and `[cocircular]`.
- Root cause: three concurrent clipping constraints produced almost identical
  vertices. Their rounded difference made a tiny edge point in an arbitrary
  direction, adding a false constraint to convex containment.
- Solution: remove redundant supporting planes whose exported edge is below
  5e-15 in normalized coordinates, then recompute polygon intersections once.
  Excerpt: `if vertices[i].distance(vertices[(i+1)%len(vertices)]) > 5e-15`.
- Verification: both failures in `evidence/initial-cell-failures.xml` became
  passes in `evidence/tests-current.xml`.
- Prevention/lesson: include corner concurrence and zero-length topology in
  tests; area equality alone does not establish coverage.

## P002 Close site bisectors amplified rounded coefficients

- Symptom: six sites clustered at 1e-11 amid four unit-square corners produced
  total cell area 1.439996905390856 instead of 1.44.
- Investigation: the seeded cluster series isolated the failure to ill-conditioned
  intersections; inputs and error appear in `evidence/adversarial-initial.json`.
- Root cause: unit-normal bisector coefficients were rounded before intersecting
  almost parallel boundaries. Division by a tiny determinant amplified that error.
- Solution: when `abs(det) < 1e-7`, rebuild plane coefficients from original
  binary focus coordinates using Decimal at 80-digit precision and intersect there.
- Verification: the cluster exponent 11 test now passes area, ownership and
  empty-circle checks; higher-precision cluster regressions also pass.
- Prevention/lesson: retain defining sites alongside approximate planes. High
  precision applied only after information is rounded cannot recover it.

## P003 A reliable orientation sign did not ensure an accurate centre

- Symptom: the 1e-15 cluster produced a circle vertex not equidistant from its
  defining sites, recorded in `evidence/adversarial-initial.json`.
- Investigation: compared translated determinant products and the construction's
  conditioning, rather than changing the empty-circle tolerance to hide it.
- Root cause: the initial 8e-16 determinant filter was suitable for detecting
  severe cancellation of a sign, but too restrictive for centre accuracy.
- Solution: use Decimal circumcentre construction when the cross product is
  at most `1e-8 * (abs(ux*vy) + abs(uy*vx))`.
- Verification: all cluster exponents 8, 11, 13, 14 and 15 now pass the empty-circle
  checks in `tests/test_adversarial.py`.
- Prevention/lesson: distinguish a predicate's sign from a construction's
  conditioning; each needs its own error policy.

## P004 A large clipping epsilon retained contradictory tiny edges

- Symptom: after the precision fixes, exponent 13/14 cluster tests still reported
  a hole at (0.783765456996815, 0.7120393849074937).
- Investigation: inspected the corner site's polygon; one vertex was at
  y=1.100000000000123, just beyond the requested y=1.1 clipping boundary.
- Root cause: the original signed-distance epsilon 2e-13 retained an inactive
  plane, creating a reversed edge about 1.2e-13 long. Relaxing the validator did
  not solve this construction defect.
- Solution: reduce the normalized clipping tolerance to 8e-16, keeping explicit
  high-precision intersections for difficult constraints.
- Verification: the two remaining failures in `evidence/tests-adversarial.xml`
  passed afterward. The full core/adversarial suite reached 70 passes.
- Prevention/lesson: a larger epsilon is not a general robustness fix. Test the
  actual construction after each change and retain an independent ownership check.

## P005 Validation ignored representational error at large offsets

- Symptom: a diagram translated near 1e9 failed equidistance with a fixed 1e-8
  tolerance, although local construction used normalized coordinates.
- Investigation: checked the output float spacing; one coordinate ULP near 1e9
  is approximately 1.19e-7, greater than the original validation bound.
- Root cause: the validator ignored unavoidable rounding when exporting back
  into world coordinates, and tiny edges amplified endpoint subtraction error.
- Solution: include eight world-coordinate ULPs in the circle-distance bound;
  containment also includes endpoint-subtraction uncertainty in its cross product.
- Verification: translation and scaling regressions pass alongside cluster
  checks; construction fixes P002–P004 were still necessary for those checks.
- Prevention/lesson: error bounds must reflect data representation. Validators
  also need review; fixing their bounds must not replace repairing bad topology.

## Problem record template

### Pxxx — Specific problem title

- Work date and recorded date:
- Status: open / fixed / unresolved limitation.
- Symptom: actual failure, minimal input and raw error/result.
- Investigation: commands, reduction steps and competing explanations.
- Root cause: specific mechanism established by evidence.
- Solution: changed file/function, patch or excerpt; explain why it addresses cause.
- Verification: failing check before fix, same check after fix, raw-result paths.
- Prevention and lesson: regression coverage or design rule; AI's actual role.

## Initial environment observations

The DOCX extraction initially failed to print Unicode under the terminal's
default encoding and was rerun successfully using UTF-8. Restricted WSL access
initially failed; the read-only inspection succeeded with approved access.
Windows runtime dependencies are not yet installed. These observations belong
to the real log, but are not automatically five substantive algorithm problems.
