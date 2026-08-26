# Appendix: the red rows, diagnosed

*A late finding, after the article's draft closed. The article's claims are
unchanged: GR-34/35/36 failed, sit red, and stay red until a certified test says
otherwise. This appendix records a diagnosis of WHY they failed, and a scout that
shows the shape of the repair. It is an existence proof, not a fix.*

## What failed

Three pre-registered tests asked whether the toy's derived hole obeys the
Bekenstein–Hawking pattern. All three failed: radius grew as flux^4.88 (the
Schwarzschild pattern wants exponent 1), surface gravity grew as flux^2.80 —
bigger holes came out *hotter*, the sign backwards — and entropy scaled as
radius^0.16 (the area law wants 2).

## The suspect: a hole with no mass

Temperature, in any horizon system, is the *steepness* of the flow profile at the
horizon — the gradient of (flow speed minus wave speed). That is not my convention;
it is Unruh's 1981 definition of analog surface gravity, and it is measured physics:
Steinhauer's Bose–Einstein-condensate experiments observed thermal Hawking radiation
at exactly the flow-gradient temperature (Nature 569, 2019).

Now look at the instrument my red rows tested. Its hole is a sink that *discards*
what it swallows — the absorbed budget vanishes, nothing accumulates — and the
sink's width is a hand-painted constant. So the hole that sat the thermodynamics
exams has **no mass variable at all**, and its only length scale is the painted
width. Every Schwarzschild thermodynamic law hangs on one fact: the horizon's only
length scale is GM/c², proportional to the mass. An object with no mass cannot obey
mass-dependent laws. The red rows measured my imposed flow profiles — not the
congestion mechanism.

## The scout: what the repair would have to produce

`python sim/sg_river_scout.py` — numpy only, runs in seconds.

Instead of painting a sink, assemble the river from the model's *own measured
laws*: the load field around mass M takes the Newton shape M/r (a certified row),
the local rate compounds to e^(−M/r) (a certified row), and infalling material
free-falls in that field, reaching v = √(2M/r). Then measure the horizon the same
way the red rows did, on a mass ladder from 2 to 64:

- **Radius:** r_h = 3.526·M — exponent 1.000 (the red row said 4.88).
- **Temperature:** the peeling rate (how fast outgoing signals e-fold off the
  horizon — the analog temperature read) scales as M^−1.000. **Bigger holes come
  out colder.** The sign flip is gone.
- **Entropy:** the Clausius sum over the measured temperatures fits S ~ r_h^1.83 on
  the short ladder; the deficit from 2 is the integration anchor biasing the small
  holes — extend the ladder to M = 512 and the top points fit s = 1.999. The area
  exponent.
- **Control:** a river with a *fixed* length scale and growing amplitude — the shape
  of the failed instrument — comes out hotter with size, every time. The failure
  direction reproduces from the profile shape alone.

This is the Hamilton–Lisle "river model" fact (Am. J. Phys. 76, 2008): a
Schwarzschild hole *is* a medium flowing inward at escape velocity, and
κ = c⁴/4GM follows from the profile automatically. Escape-velocity shaping *is*
Newtonian gravity — the one ingredient the failed instrument lacked.

## What this does NOT show

- **It is not a derivation.** The scout *imposes* the escape-velocity profile,
  assembled from measured laws; the model's dynamics did not grow it. The honest
  statement: *if* back-reaction — a sink that stores what it eats, the stored load
  driving its own river — produces escape-velocity shaping, *then* the
  thermodynamic scalings follow. Whether it does is a pre-registered future test:
  r_h ∝ M, κ ∝ 1/M, S ∝ r_h², declared before the run. Until that test runs green,
  the rows stay red.
- **The coefficients are wrong and stay on the record.** r_h = 3.526M, not 2M — the
  compounded rate field pushes the horizon outward. T·8πM = 0.667, not 1. Scalings
  match; coefficients differ. These are falsifiable differences, the same
  strong-field frontier the article already confesses.
- **The area law from first principles remains open — for everyone.** No analog or
  computational medium has derived S ∝ area from its own microdynamics. Jacobson's
  1995 theorem shows the area-entropy law plus the Clausius relation are
  *equivalent* to Einstein's equations; emergent-gravity programs (Verlinde,
  Padmanabhan) take area scaling as an input. The scout assembles the exponent from
  two measured scalings; deriving it from substrate rules is research, not a patch.

## Sources

Unruh, "Experimental black-hole evaporation?", PRL 46 (1981). Visser, "Essential
and inessential features of Hawking radiation", Int. J. Mod. Phys. D 12 (2003).
Barceló, Liberati, Visser, "Analogue Gravity", Living Reviews in Relativity.
Jacobson, "Thermodynamics of spacetime: the Einstein equation of state", PRL 75
(1995). Hamilton & Lisle, "The river model of black holes", Am. J. Phys. 76 (2008).
Muñoz de Nova, Golubkov, Kolobov, Steinhauer, Nature 569 (2019).
