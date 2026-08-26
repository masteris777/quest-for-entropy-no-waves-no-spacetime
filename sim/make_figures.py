# Cartoon figures for "The Black Hole With No Singularity".
# A plain 2D wave equation with a position-dependent speed c(x,y) - the
# congestion field. Not the certified machine; the article says so.
# Output: ../assets/bending.gif and ../assets/trap.gif (light theme, Substack white).

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
ASSETS.mkdir(exist_ok=True)


def step(u, up, c2dt2):
    lap = (
        np.roll(u, 1, 0) + np.roll(u, -1, 0) + np.roll(u, 1, 1) + np.roll(u, -1, 1) - 4 * u
    )
    un = 2 * u - up + c2dt2 * lap
    return un


def sponge(N, width=70):
    s = np.ones((N, N))
    for i in range(width):
        f = 1.0 - 0.045 * ((width - i) / width) ** 2
        s[i, :] *= f
        s[-1 - i, :] *= f
        s[:, i] *= f
        s[:, -1 - i] *= f
    return s


def render_gif(path, frames, cfield, fps=14, title="", crawl_level=None, star=None):
    fig, ax = plt.subplots(figsize=(5.4, 5.4), dpi=90)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color("#cccccc")
    slow = 1.0 - cfield / cfield.max()
    smax = max(slow.max(), 1e-9)
    # grey-code the density: continuous gradual darkening, darker = slower
    frac = np.clip(slow / smax, 0.0, 1.0)
    grey = 1.0 - 0.5 * frac
    rgba = np.dstack([grey, grey, grey, np.where(frac > 0.005, 1.0, 0.0)])
    im_w = ax.imshow(rgba)
    ax.contour(slow, levels=list(smax * np.array([0.2, 0.4, 0.6, 0.8])),
               colors="#999999", linewidths=0.5, alpha=0.6)
    if crawl_level is not None:
        ax.contour(cfield, levels=[crawl_level], colors="#777777", linestyles="dashed", linewidths=1.1)
    if star is not None:
        ax.add_patch(plt.Circle(star[:2], star[2], facecolor="#f6c453",
                                edgecolor="#d99a2b", linewidth=1.0, alpha=0.95))
    ax.set_xlabel("darker = slower ticks", fontsize=9, color="#777777")
    cmap_u = plt.get_cmap("RdBu_r")
    im_u = ax.imshow(np.zeros(frames[0].shape + (4,)))
    if title:
        ax.set_title(title, fontsize=11, color="#333333", pad=8)
    fig.tight_layout()
    w = PillowWriter(fps=fps)
    scale = None
    with w.saving(fig, str(path), dpi=90):
        for f in frames:
            p = np.percentile(np.abs(f), 99.9) + 1e-12
            # display gain may grow at most 4% per frame: no sudden noise blow-up
            scale = p if scale is None else max(p, scale * 0.985)
            cl = np.clip(f / (1.4 * scale), -1, 1)
            rgba_u = cmap_u((cl + 1) / 2)
            # transparent where there is no wave, so the crowd shading shows through
            rgba_u[..., 3] = np.clip(np.abs(cl) * 2.5, 0, 0.9)
            im_u.set_data(rgba_u)
            w.grab_frame()
    plt.close(fig)
    print(f"wrote {path} ({path.stat().st_size/1e6:.2f} MB, {len(frames)} frames)")


def make_bending():
    N = 420
    dx = 1.0
    dt = 0.45
    x = np.arange(N)
    X, Y = np.meshgrid(x, x, indexing="xy")

    # a STAR: a drawn disc with its congestion halo - light passes its side
    cx, cy, sig = 235, 285, 55.0
    c = 1.0 - 0.75 * np.exp(-(((X - cx) ** 2 + (Y - cy) ** 2) / (2 * sig**2)))
    c2dt2 = (c * dt / dx) ** 2
    sp = sponge(N)

    # a rightward-moving gaussian beam, passing ABOVE the star
    x0, y0 = 60, 150
    env = np.exp(-(((X - x0) ** 2) / (2 * 18.0**2) + ((Y - y0) ** 2) / (2 * 34.0**2)))
    k = 0.55
    u = env * np.cos(k * (X - x0))
    up = np.exp(-(((X - x0 + c * dt) ** 2) / (2 * 18.0**2) + ((Y - y0) ** 2) / (2 * 34.0**2))) * np.cos(
        k * (X - x0 + c * dt)
    )

    frames = []
    steps_per_frame = 12
    for fi in range(78):
        for _ in range(steps_per_frame):
            un = step(u, up, c2dt2)
            un *= sp
            u *= sp
            up = u
            u = un
        frames.append(u.copy())
    render_gif(
        ASSETS / "bending.gif",
        frames,
        c,
        star=(235, 285, 30),
        title="light passing a star: the near side slows, the path bends",
    )


def make_trap():
    N = 420
    dx = 1.0
    dt = 0.45
    x = np.arange(N)
    X, Y = np.meshgrid(x, x, indexing="xy")

    # a deep congestion well: rate tiny at the center, never zero
    cx, cy = 230, 230
    r = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    a = 90.0
    c = np.exp(-a / np.maximum(r, 5.0))  # compounding profile: e^(-a/r); tiny inside, never zero
    c = np.clip(c, 0.05, None)
    c2dt2 = (c * dt / dx) ** 2
    sp = sponge(N)

    # a SMALL packet falling STRAIGHT in (dead radial): it sinks, slows,
    # compresses as the ticks stretch under it, and crawls - never quite stopping
    x0, y0 = 75.0, 230.0
    k, sig = 0.30, 16.0
    env = np.exp(-(((X - x0) ** 2) + ((Y - y0) ** 2)) / (2 * sig**2))
    u = env * np.cos(k * (X - x0))
    envp = np.exp(-(((X - x0 + c * dt) ** 2) + ((Y - y0) ** 2)) / (2 * sig**2))
    up = envp * np.cos(k * (X - x0 + c * dt))

    frames = []
    steps_per_frame = 16
    for fi in range(72):
        for _ in range(steps_per_frame):
            un = step(u, up, c2dt2)
            un *= sp
            u *= sp
            up = u
            u = un
        frames.append(u.copy())
    render_gif(
        ASSETS / "trap.gif",
        frames,
        c,
        crawl_level=0.15,
        title="a small packet falls into a deep crowd: it slows, compresses, and crawls",
    )


def make_compaction():
    N = 420
    dx = 1.0
    dt = 0.45
    x = np.arange(N)
    X, Y = np.meshgrid(x, x, indexing="xy")

    # a slow half-plane on the right: WIDE smooth interface around x = 260
    c = 1.0 - 0.62 * 0.5 * (1 + np.tanh((X - 260) / 45.0))
    c2dt2 = (c * dt / dx) ** 2
    sp = sponge(N)

    # a compact packet aimed obliquely at the interface (down-right, 38 degrees)
    th = np.deg2rad(38.0)
    kx, ky = np.cos(th), np.sin(th)
    x0, y0 = 100, 80
    k = 0.55
    sig_l, sig_t = 26.0, 26.0
    L = kx * (X - x0) + ky * (Y - y0)   # along motion
    T = -ky * (X - x0) + kx * (Y - y0)  # across motion
    env = np.exp(-(L**2) / (2 * sig_l**2) - (T**2) / (2 * sig_t**2))
    u = env * np.cos(k * L)
    Ls = L + dt  # the same packet one step earlier along its own track (c=1 out here)
    up = np.exp(-(Ls**2) / (2 * sig_l**2) - (T**2) / (2 * sig_t**2)) * np.cos(k * Ls)

    frames = []
    steps_per_frame = 12
    for fi in range(72):
        for _ in range(steps_per_frame):
            un = step(u, up, c2dt2)
            un *= sp
            u *= sp
            up = u
            u = un
        frames.append(u.copy())
    render_gif(
        ASSETS / "compaction.gif",
        frames,
        c,
        title="a matter wave entering a dense region: it compresses, and it turns",
    )


def make_equivalence():
    """The sealed elevator: an accelerating observer over empty fabric (top) and a
    resting observer beside a crowd (bottom) watch the same wave - and see the
    same fall. Correspondence a = g*c^2, the same one the redshift scout measures."""
    W = 420
    dt = 0.45
    c_mid = 0.85
    gy = 0.94e-3                      # gradient of ln(c) per cell, bottom slower
    a_cam = gy * (dt * c_mid) ** 2    # the equivalent camera acceleration
    steps_per_frame, n_frames = 12, 78

    def packet(H, row, c_here):
        x = np.arange(W)
        X, Y = np.meshgrid(x, np.arange(H), indexing="xy")
        k, x0, sig = 0.55, 70.0, 22.0
        env = np.exp(-(((X - x0) ** 2) + ((Y - row) ** 2)) / (2 * sig**2))
        u = env * np.cos(k * (X - x0))
        envp = np.exp(-(((X - x0 + c_here * dt) ** 2) + ((Y - row) ** 2)) / (2 * sig**2))
        up = envp * np.cos(k * (X - x0 + c_here * dt))
        return u, up

    def rect_sponge(H, width=40):
        s = np.ones((H, W))
        for i in range(width):
            f = 1.0 - 0.045 * ((width - i) / width) ** 2
            s[i, :] *= f
            s[-1 - i, :] *= f
            s[:, i] *= f
            s[:, -1 - i] *= f
        return s

    # bottom panel: gravity - linear crowd gradient, slower toward the bottom
    H_R = 280
    YR = np.arange(H_R)[:, None] * np.ones((1, W))
    c_R = np.clip(c_mid * (1.0 - gy * (YR - 90.0)), 0.4, 1.05)
    uR, upR = packet(H_R, 90, c_mid)
    c2R = (c_R * dt) ** 2
    spR = rect_sponge(H_R)

    # top panel: empty uniform fabric, camera accelerating upward
    H_L = 340
    uL, upL = packet(H_L, 150, c_mid)
    c2L = (c_mid * dt) ** 2
    spL = rect_sponge(H_L)

    VIEW = 210
    fig, (axL, axR) = plt.subplots(2, 1, figsize=(5.4, 5.4), dpi=90)
    fig.patch.set_facecolor("white")
    for ax in (axL, axR):
        ax.set_facecolor("white")
        ax.set_xticks([])
        ax.set_yticks([])
        for sp_ in ax.spines.values():
            sp_.set_color("#cccccc")
    slow = 1.0 - c_R[35:35 + VIEW] / c_R.max()
    smax = max(slow.max(), 1e-9)
    frac = np.clip(slow / smax, 0.0, 1.0)
    grey = 1.0 - 0.5 * frac
    axR.imshow(np.dstack([grey, grey, grey, np.where(frac > 0.005, 1.0, 0.0)]))
    axR.contour(slow, levels=list(smax * np.array([0.2, 0.4, 0.6, 0.8])),
                colors="#999999", linewidths=0.5, alpha=0.6)
    cmap_u = plt.get_cmap("RdBu_r")
    imL = axL.imshow(np.zeros((VIEW, W, 4)))
    imR = axR.imshow(np.zeros((VIEW, W, 4)))
    # grey dots = the fabric itself, so the camera motion is visible
    dot = 42
    gxx, gyy = np.meshgrid(np.arange(21, W, dot), np.arange(35 + 21, 35 + VIEW, dot))
    axR.plot(gxx.ravel(), (gyy - 35).ravel(), ls="", marker=".", color="#8a8a8a", ms=2.5)
    dots_rows = np.arange(5.0, H_L, dot)
    dots_cols = np.arange(21, W, dot)
    dotsL, = axL.plot([], [], ls="", marker=".", color="#b0b0b0", ms=2.5)
    trL, = axL.plot([], [], ls=":", color="#666666", lw=1.2)
    trR, = axR.plot([], [], ls=":", color="#666666", lw=1.2)
    axL.set_title("EMPTY fabric - the observer accelerates upward", fontsize=10,
                  color="#333333", pad=6)
    axR.set_title("a crowd below, observer at rest - the same fall", fontsize=10,
                  color="#333333", pad=6)
    axR.set_xlabel("darker = slower ticks", fontsize=9, color="#777777")
    fig.suptitle("the sealed elevator (grey dots = the fabric)", fontsize=11, color="#333333")
    fig.tight_layout(rect=(0, 0, 1, 0.96))

    def centroid(view):
        p = view**2
        tot = p.sum()
        if tot < 1e-8:
            return None
        cx = (p.sum(axis=0) * np.arange(W)).sum() / tot
        cy = (p.sum(axis=1) * np.arange(VIEW)).sum() / tot
        return cx, cy

    w = PillowWriter(fps=14)
    scL = scR = None
    histL, histR = [], []
    t = 0
    with w.saving(fig, str(ASSETS / "equivalence.gif"), dpi=90):
        for fi in range(n_frames):
            for _ in range(steps_per_frame):
                unL = step(uL, upL, c2L)
                unL *= spL
                uL *= spL
                upL, uL = uL, unL
                unR = step(uR, upR, c2R)
                unR *= spR
                uR *= spR
                upR, uR = uR, unR
                t += 1
            off = int(round(max(95.0 - 0.5 * a_cam * t * t, 0.0)))
            vL = uL[off:off + VIEW]
            vR = uR[35:35 + VIEW]
            rr = dots_rows - off
            sel = (rr >= 0) & (rr < VIEW)
            gx2, gy2 = np.meshgrid(dots_cols, rr[sel])
            dotsL.set_data(gx2.ravel(), gy2.ravel())
            for view, im, sc_name in ((vL, imL, "L"), (vR, imR, "R")):
                p = np.percentile(np.abs(view), 99.9) + 1e-12
                if sc_name == "L":
                    scL = p if scL is None else max(p, scL * 0.96)
                    sc = scL
                else:
                    scR = p if scR is None else max(p, scR * 0.96)
                    sc = scR
                cl = np.clip(view / (1.4 * sc), -1, 1)
                rgba = cmap_u((cl + 1) / 2)
                rgba[..., 3] = np.clip(np.abs(cl) * 2.5, 0, 0.9)
                im.set_data(rgba)
            cL = centroid(vL)
            cR_ = centroid(vR)
            if cL and 60 <= cL[0] <= 385:
                histL.append(cL)
            if cR_ and 60 <= cR_[0] <= 385:
                histR.append(cR_)
            trL.set_data([h[0] for h in histL], [h[1] for h in histL])
            trR.set_data([h[0] for h in histR], [h[1] for h in histR])
            w.grab_frame()
    plt.close(fig)
    path = ASSETS / "equivalence.gif"
    print(f"wrote {path} ({path.stat().st_size/1e6:.2f} MB, {n_frames} frames)")


def make_composite():
    """One picture with all four animations: 2x2 panorama, every 2nd frame."""
    from PIL import Image

    names = ["bending", "compaction", "equivalence", "trap"]
    imgs = [Image.open(ASSETS / f"{n}.gif") for n in names]
    counts = [im.n_frames for im in imgs]
    side = 486
    frames = []
    for i in range(0, 78, 2):
        canvas = Image.new("RGB", (2 * side, 2 * side), "white")
        for k, im in enumerate(imgs):
            im.seek(i % counts[k])
            f = im.convert("RGB")
            if f.size != (side, side):
                f = f.resize((side, side))
            canvas.paste(f, ((k % 2) * side, (k // 2) * side))
        frames.append(canvas.quantize(colors=256))
    out = ASSETS / "panorama.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=143,
                   loop=0, optimize=True)
    print(f"wrote {out} ({out.stat().st_size/1e6:.2f} MB, {len(frames)} frames)")


if __name__ == "__main__":
    make_bending()
    make_trap()
    make_compaction()
    make_equivalence()
    # make_composite()  # the 4-in-1 panorama - shelved for now, kept for later
