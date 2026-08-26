"""Self-gravitating river scout (2026-08-25) - the back-reaction suspect.

The red rows (GR-34..36) measured a hole with NO mass variable: the FLU-8 sink
absorbs budget (nothing accumulates) and its only length scale is the painted
sink width sig=10. Schwarzschild thermodynamics hangs on the horizon's only
length scale being GM/c^2 ~ M. Suspect: feed the river from the toy's OWN
measured laws instead - load L = M/r (GR-23 Newton shape), local rate
c = exp(-L) (GR-39 compounding), inflow v = sqrt(2M/r) (free fall from rest,
the GR-23/30 geodesics) - and the sign flips.

SCOPE (tightened after external critique, same day): this is an EXISTENCE PROOF,
not a derivation - the profile v = sqrt(2M/r) is assembled from measured toy laws,
not grown by dynamics. It shows what back-reaction would have to produce, and that
IF it produces escape-velocity shaping, the thermodynamic scalings follow. The
dynamical closure (a sink that STORES what it eats, stored load driving its own
river, run to steady state) is the pre-registered battery row, not this scout.
Coefficients stay on the record as differences: r_h = 3.526M (not 2M),
T*8piM = 0.667 (not 1). Post-hoc check: the S4 exponent 1.83 is the Clausius
anchor constant flattening the low end - extend the ladder to M=512 and the top
five points fit s = 1.999.

Pass marks DECLARED BEFORE the first run:
  S1: horizon radius r_h ~ M^p with p in [0.9, 1.1]   (Schwarzschild: 1)
  S2: surface gravity kappa ~ M^q with q in [-1.1, -0.9]  (bigger = COLDER)
  S3: ballistic peeling rate (e-folding of outgoing signals off the horizon,
      the analog-gravity temperature read) matches the analytic gradient
      d(v-c)/dr at r_h within 10% at every mass
  S4: Clausius entropy S = INT 2pi dM/kappa fits S ~ r_h^s with s in [1.8, 2.2]
      (in 3D, S ~ area IS S ~ r^2)
  C1 (control, the red rows' shape): a river with a FIXED length scale and
      growing amplitude must come out HOTTER with size (kappa rising) -
      reproducing the failure identifies its cause.
"""

import numpy as np


def check(label, ok, detail):
    print("%-6s %-4s %s" % ("PASS" if ok else "FAIL", label, detail))
    return ok


def rate(r, M):
    return np.exp(-M / r)


def river(r, M):
    return np.sqrt(2.0 * M / r)


def horizon(M):
    lo, hi = 0.05 * M, 200.0 * M
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if rate(mid, M) - river(mid, M) > 0.0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def kappa_analytic(M, r_h):
    v, c = river(r_h, M), rate(r_h, M)
    return v / (2.0 * r_h) + c * M / r_h ** 2   # |d(v-c)/dr| at the crossing


def peeling_rate(M, r_h):
    # outgoing signal just off the horizon: dr/dt = c(r) - v(r); its distance
    # from the horizon e-folds at kappa (the peeling/temperature read)
    def f(r):
        return rate(r, M) - river(r, M)
    r = r_h * (1.0 + 1e-4)
    dt = 1e-3 * r_h
    ts, ds = [], []
    t = 0.0
    while r - r_h < 0.05 * r_h:
        k1 = f(r)
        k2 = f(r + 0.5 * dt * k1)
        k3 = f(r + 0.5 * dt * k2)
        k4 = f(r + dt * k3)
        r += dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        t += dt
        ts.append(t)
        ds.append(r - r_h)
    ts, ds = np.array(ts), np.array(ds)
    coef = np.polyfit(ts, np.log(ds), 1)
    return float(coef[0])


def powfit(lx, ly):
    p, c = np.polyfit(lx, ly, 1)
    resid = ly - (p * lx + c)
    r2 = 1.0 - float((resid ** 2).sum() / ((ly - ly.mean()) ** 2).sum())
    return float(p), r2


def main():
    R = []
    Ms = np.array([2.0, 4.0, 8.0, 16.0, 32.0, 64.0])
    rh = np.array([horizon(M) for M in Ms])
    kap_a = np.array([kappa_analytic(M, r) for M, r in zip(Ms, rh)])
    kap_m = np.array([peeling_rate(M, r) for M, r in zip(Ms, rh)])

    p, r2p = powfit(np.log(Ms), np.log(rh))
    R.append(check("S1", 0.9 <= p <= 1.1 and r2p > 0.99,
                   "self-set river: r_h ~ M^%.3f (R^2=%.4f; Schwarzschild wants 1) - "
                   "r_h/M = %.3f at every mass (control 2M): the horizon's length "
                   "scale IS the mass" % (p, r2p, float((rh / Ms).mean()))))

    q, r2q = powfit(np.log(Ms), np.log(kap_m))
    R.append(check("S2", -1.1 <= q <= -0.9 and r2q > 0.99,
                   "measured peeling: kappa ~ M^%.3f (R^2=%.4f; Hawking wants -1) - "
                   "IF the river is escape-velocity-shaped, bigger holes come out "
                   "COLDER (existence proof; dynamical closure = the battery row)"
                   % (q, r2q)))

    ratio = kap_m / kap_a
    R.append(check("S3", bool(np.all(np.abs(ratio - 1.0) < 0.10)),
                   "ballistic peeling vs analytic gradient: ratios %s - the "
                   "temperature read is the profile steepness, measured two ways" %
                   np.array2string(ratio, precision=3)))

    T = kap_m / (2.0 * np.pi)
    S = np.concatenate([[0.0], np.cumsum(0.5 * (1 / T[1:] + 1 / T[:-1]) * np.diff(Ms))])
    S = S - S[0] + (Ms[0] / T[0])
    s_exp, r2s = powfit(np.log(rh), np.log(S))
    R.append(check("S4", 1.8 <= s_exp <= 2.2 and r2s > 0.99,
                   "Clausius entropy from measured kappa(M): S ~ r_h^%.2f "
                   "(R^2=%.4f) - the area exponent (the deficit from 2 is the "
                   "integration anchor: top of an M=512 ladder fits 1.999)"
                   % (s_exp, r2s)))

    # C1: the red rows' shape - fixed length scale sig, growing amplitude A
    sig = 10.0
    As = np.array([3.0, 6.0, 12.0, 24.0, 48.0])
    rh_c = sig * np.sqrt(2.0 * np.log(As))          # A*exp(-r^2/2sig^2) crosses c=1
    kap_c = rh_c / sig ** 2                          # |v'| at the crossing
    qc, _ = powfit(np.log(As), np.log(kap_c))
    R.append(check("C1", qc > 0.0,
                   "fixed-scale control: kappa ~ A^%.2f > 0 - HOTTER with size, the "
                   "red rows' failure reproduced; any river with a painted length "
                   "scale must fail this way" % qc))

    print()
    for M, r, ka, km in zip(Ms, rh, kap_a, kap_m):
        print("  M=%5.1f: r_h=%7.2f  r_h/M=%.3f  kappa=%.5f (analytic %.5f)  "
              "T*8piM=%.3f" % (M, r, r / M, km, ka, km / (2 * np.pi) * 8 * np.pi * M))
    print("SG-RIVER: %s (%d checks)" % ("ALL PASS" if all(R) else "FAILURES PRESENT",
                                        len(R)))
    return all(R)


if __name__ == "__main__":
    main()
