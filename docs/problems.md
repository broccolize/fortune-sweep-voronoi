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
- Solution: an initial 5e-15 distance cutoff fixed the visible failures but was
  rejected after stronger checks found missing tiny cells. The final cleanup
  removes supports only when `concurrent(p,q,r)` proves exact rational concurrence.
  Distinct circles use `circle_identity` rather than rounded-centre grouping.
- Verification: both initial failures and six new positive-cell regressions
  pass. The intermediate missing-cell failures are in `evidence/tiny-cell-initial.xml`.
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
- Solution: the initial fix reduced the tolerance to 8e-16. The final
  `corner_inside` uses exact rational signs for uncertain decisions, retaining
  high-precision intersection coordinates without an acceptance epsilon.
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

## P006 Positive microscopic cells were lost despite sampled checks

- Symptom: the 1e-14 and 1e-15 cluster inputs had empty interior cells although
  area and sampled ownership tests passed.
- Investigation: added per-site checks for a positive polygon containing its
  generating site. The saved tiny-cell-initial.xml has two failing regressions.
- Root cause: a distance-based zero-edge cutoff deleted genuine short edges;
  rounded-centre hashing also merged distinct circle vertices, losing finite
  edge identities. Sampling missed cells with microscopic area.
- Solution: exact rational concurrency removes only truly redundant supports;
  exact input-circle keys preserve distinct vertices. Uncertain half-plane
  topology uses rational signs, and positive edges have no distance cutoff.
- Verification: all six per-site cluster cases and the complete 81-test suite pass.
- Prevention/lesson: require every distinct in-box site to retain its own cell;
  do not use a display-scale tolerance as a topology simplification rule.

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

## P007 Cocircular triangulation diagonals were counted as rays

- Symptom: twelve exact integer sites on x*x+y*y=25 produced one vertex but
  seventeen visible edges, instead of twelve rays. Area and sampled ownership passed.
- Investigation: manually inspected the counts and traced the extra microscopic
  edges after normalization. See evidence/cocircular-12-initial.json.
- Root cause: the sweep's triangulation can include redundant cocircular
  diagonals. Floating normalization made those constraints appear to have tiny
  positive length, and a one-ended trace was classified as a ray unconditionally.
- Solution: a one-ended trace is a ray only when the pair is a convex-hull
  adjacency; other such traces are zero-length diagonals and are removed before
  clipping. World vertices are taken directly from their exact input-circle keys.
- Verification: the exact twelve-site ring now gives one vertex and twelve rays;
  the existing square regression also checks this larger ring. All 82 tests pass.
- Prevention/lesson: validate topology counts and ray classification in addition
  to geometric tolerances, especially for exact cocircular inputs beyond four sites.

## Initial environment observations

The DOCX extraction initially failed to print Unicode under the terminal's
default encoding and was rerun successfully using UTF-8. Restricted WSL access
initially failed; the read-only inspection succeeded with approved access.
Windows runtime dependencies are not yet installed. These observations belong
to the real log, but are not automatically five substantive algorithm problems.
