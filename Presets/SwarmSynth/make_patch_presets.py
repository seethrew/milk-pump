"""MilkDrop presets from Daxy's own SwarmSynth Revived patches: every patch whose visualiser is on becomes
one preset with the patch's name, built from that patch's viz* settings. Run:
    python make_patch_presets.py         -> writes Patches\\<patch>.milk and Modes\\SwarmSynth - <Mode>.milk

What carries over from the patch (SwarmSynthRevived\\Source\\VizEngine.h is the original):
  Mode (Chords, 3D, Mandala, Tunnel, Sphere, Sections, Hypertrace, Attractor, Hopf), Source X/Y/Z and
  the Test Wave (Saw, Swarm, FM, Sine + 3rd are generated here exactly as SwarmSynth generates them,
  so a patch drawn from a test wave keeps its figure; Master/OSC/Noise read the music), Delay (a
  fraction of the note period, or ms), Drift, Span, Density, Reach, Lines, Spokes, Dot, Spin, Tilt,
  Tumble, Persp, Depth Cue, Zoom, Fold (Mirror X, Mirror XY, Kaleido), Segments, Angle, Turn, 4D Turn,
  Bright, Ink (Paper = black on white), Pulse, Flip on hits, Trail, Colour (Vivid / Pearl).

What MilkDrop changes:
  - No note pitch. The music's period is measured from its rising zero crossings (the recorder, wave
    0); a test wave runs at a fixed period, as SwarmSynth's does with TEST RETRIG off.
  - The music is the newest 480 samples a frame, not SwarmSynth's long ring: reaches further back wrap.
  - Three drawn waves of up to 512 points (wave 0 is the recorder), so Density tops out near 509 and
    each patch keeps its three most important layers (lines, dots, spokes, a second trace).
  - Mirror and kaleido copies are made in the composite shader, from one drawn picture.
Every preset is ours (Daxy & Claude, 2026).
"""
import glob
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SWARM = os.path.join(os.path.expanduser("~"), "Documents", "SwarmSynth Revived", "Presets")

MODES = ["Chords", "3D", "Mandala", "Tunnel", "Terrain", "Sphere", "Sections", "Bubbles",
         "Hypertrace", "Attractor", "Knot", "Hopf"]

# SwarmSynth's own defaults (PluginProcessor.cpp), for anything a patch does not store.
DEFAULTS = dict(vizOn=0, vizMode=0, vizSrcX=0, vizSrcY=0, vizSrcZ=0, vizLock=0, vizDelay=25, vizDrift=0,
                vizSpan=2, vizDensity=320, vizReach=23, vizReach2=0, vizLines=55, vizSpokes=0, vizSpin=25,
                vizTilt=25, vizTumble=0, vizPersp=60, vizDepth=50, vizZoom=100, vizFold=0, vizSegs=6,
                vizAngle=0, vizTurn=0, vizDot=2.6, vizShape=0, vizCue=70, vizBright=90, vizInk=0,
                vizPulse=0, vizFlip=0, vizTrail=0, vizTest=0, vizColour=0, vizColSet=0, vizTurn4=30,
                vizDraw=0, vizWinding=1)

BASE = dict(
    fRating=4.0, fGammaAdj=1.0, fDecay=1.0, fVideoEchoZoom=1.0, fVideoEchoAlpha=0.0,
    nVideoEchoOrientation=0, nWaveMode=0, bAdditiveWaves=0, bWaveDots=0, bWaveThick=0,
    bModWaveAlphaByVolume=0, bMaximizeWaveColor=0, bTexWrap=0, bDarkenCenter=0, bRedBlueStereo=0,
    bBrighten=0, bDarken=0, bSolarize=0, bInvert=0, fWaveAlpha=0.0, fWaveScale=1.0,
    fWaveSmoothing=0.0, fWaveParam=0.0, fModWaveAlphaStart=0.75, fModWaveAlphaEnd=0.95,
    fWarpAnimSpeed=1.0, fWarpScale=1.0, fZoomExponent=1.0, fShader=0.0, zoom=1.0, rot=0.0,
    cx=0.5, cy=0.5, dx=0.0, dy=0.0, warp=0.0, sx=1.0, sy=1.0, wave_r=1.0, wave_g=1.0, wave_b=1.0,
    wave_x=0.5, wave_y=0.5, ob_size=0.0, ob_r=0.0, ob_g=0.0, ob_b=0.0, ob_a=0.0, ib_size=0.0,
    ib_r=0.0, ib_g=0.0, ib_b=0.0, ib_a=0.0, nMotionVectorsX=0.0, nMotionVectorsY=0.0, mv_dx=0.0,
    mv_dy=0.0, mv_l=0.0, mv_r=0.0, mv_g=0.0, mv_b=0.0, mv_a=0.0,
)

# Wave 0, the RECORDER: the mono mix into gmegabuf(0..479), the auto-range peak in gmegabuf(1001), and
# the rising zero crossings (with hysteresis, so noise does not count) - their positions in
# gmegabuf(1100 + n), how many in gmegabuf(1004), the newest in gmegabuf(1003) (SwarmSynth's anchor,
# so the figure holds still) and the smoothed period between them in gmegabuf(1002).
RECORDER = [
    "i = int(sample*479 + 0.5);",
    "v = (value1 + value2)*0.5;",
    "gmegabuf(i) = v;",
    "st = equal(i, 0);",
    "pk = if(st, 0, pk); nc = if(st, 0, nc); fc = if(st, 0, fc); lc = if(st, 0, lc); arm = if(st, 0, arm);",
    "pk = max(pk, abs(v));",
    "arm = if(below(v, -0.08*gmegabuf(1001)), 1, arm);",
    "c_ = arm*above(v, 0);",
    "gmegabuf(1100 + nc) = if(c_, i, gmegabuf(1100 + nc));",
    "nc = nc + c_; fc = if(c_*equal(nc, 1), i, fc); lc = if(c_, i, lc); arm = arm*(1 - c_);",
    "en = equal(i, 479);",
    "pr = if(above(nc, 1), (lc - fc)/(nc - 1), 240);",
    "gmegabuf(1002) = if(en, gmegabuf(1002)*0.85 + min(240, max(8, pr))*0.15, gmegabuf(1002));",
    "gmegabuf(1003) = if(en, if(nc, lc, 470), gmegabuf(1003));",
    "gmegabuf(1004) = if(en, nc, gmegabuf(1004));",
    "gmegabuf(1001) = if(en, max(max(pk, gmegabuf(1001)*0.985), 0.004), gmegabuf(1001));",
]

READ_GAIN = "gn = 0.9/gmegabuf(1001);"   # SwarmSynth's auto-range: the loudest recent level = 0.9


def src(s, k):
    """One source's value at position k (an eel expression; older = smaller)."""
    if s < 7:   # Master, L, R, Side, OSC 1, OSC 2, Noise: all the music's mono mix here
        return f"gmegabuf((int({k}) + 48000) % 480)*gn"
    ph = f"(({k})/q11 + 1000)"
    if s == 7:   # Saw
        return f"(0.9*(2*({ph} - int({ph})) - 1))"
    if s == 8:   # Swarm: three detuned saws drifting against each other
        z = [ph, f"({ph}*1.006 + 0.137 + time*0.05)", f"({ph}*0.994 + 0.274 + time*0.031)"]
        return "(0.3*(" + " + ".join(f"2*({p} - int({p})) - 1" for p in z) + "))"
    if s == 9:   # FM, its index swaying as SwarmSynth's does
        return f"(0.9*sin(6.2831853*{ph} + q12*sin(6.2831853*{ph})))"
    return f"(0.818*(sin(6.2831853*{ph}) + 0.33*sin(18.849556*{ph})))"   # Sine + 3rd


# The camera (VizEngine project()): spin about y (q1), tilt + tumble about x (q2), perspective q3.
PROJECT = [
    "cy_ = cos(q1); sy_ = sin(q1); cx_ = cos(q2); sx_ = sin(q2);",
    "x1 = x3*cy_ + z3*sy_; z1 = z3*cy_ - x3*sy_;",
    "y2 = y3*cx_ - z1*sx_; z2 = y3*sx_ + z1*cx_;",
    "w_ = if(above(q3, 0), q3/(q3 + z2), 1);",
    "px = x1*w_; py = y2*w_; dd = min(1, max(0, 0.5 - z2*0.5));",
]

# Picture units -> screen: turned by Angle + Turn (q10), sized by Zoom and Pulse (q7), kept round.
TAIL = [
    "rx = px*cos(q10) - py*sin(q10); ry = px*sin(q10) + py*cos(q10);",
    "x = 0.5 + rx*q7*q32; y = 0.5 - ry*q7*q29;",
]

# KALEIDO folds every point into one wedge first (VizEngine kaleidoFold), the composite shader makes
# the mirrored copies from it.
FOLD = [
    "rd_ = sqrt(px*px + py*py); an_ = atan2(py, px); wk = 6.2831853/q27;",
    "an_ = an_ - 2*wk*floor(an_/(2*wk)); an_ = min(an_, 2*wk - an_);",
    "px = rd_*cos(an_); py = rd_*sin(an_);",
]

WARP = """shader_body
{
    ret = tex2D(sampler_main, uv).xyz*q30;
}"""


def comp(fold, colour, colset, paper):
    """Fold copies (q28 = Angle + Turn, q27 = segments), ink and colour (lightness-led)."""
    L = ["shader_body", "{", "    float2 sc = float2(q32, q29);", "    float2 d = (uv - 0.5)/sc; d.y = -d.y;   // y up, as SwarmSynth",
         "    float3 c = tex2D(sampler_main, uv).xyz;"]
    ax = "float2(-sin(q28), cos(q28))"   # Mirror X flips across the turned y axis
    ay = "float2(cos(q28), sin(q28))"
    if fold == 1:
        L += [f"    float2 m = {ax};", "    float2 e = 2*dot(d, m)*m - d;",
              "    c = max(c, tex2D(sampler_main, 0.5 + float2(e.x, -e.y)*sc).xyz);"]
    elif fold == 2:
        L += [f"    float2 m = {ax};", f"    float2 n = {ay};",
              "    float2 e = 2*dot(d, m)*m - d;", "    float2 f = 2*dot(d, n)*n - d;",
              "    c = max(c, tex2D(sampler_main, 0.5 + float2(e.x, -e.y)*sc).xyz);",
              "    c = max(c, tex2D(sampler_main, 0.5 + float2(f.x, -f.y)*sc).xyz);",
              "    c = max(c, tex2D(sampler_main, 0.5 + float2(-d.x, d.y)*sc).xyz);"]
    elif fold == 3:
        L += ["    float r = length(d);", "    float w = 6.2831853/q27;",
              "    float a = atan2(d.y, d.x) - q28;",
              "    a = a - 2*w*floor(a/(2*w));", "    a = min(a, 2*w - a) + q28;",
              "    c = tex2D(sampler_main, 0.5 + float2(cos(a), -sin(a))*r*sc).xyz;"]
    L += ["    float3 o = 1 - exp(-c*2.2);"]
    if colour:
        mix, sat = (0.8, 1.7) if colset == 0 else (0.45, 1.3)   # Vivid, Pearl (paler)
        L += ["    float l = dot(o, float3(0.333, 0.333, 0.333));",
              "    float3 hue = 0.5 + 0.5*cos(6.2831853*(q26 + l*0.35 + float3(0, 0.33, 0.67)));",
              f"    o = lerp(float3(l, l, l), min(1, l*hue*{sat}), {mix});"]
    L += ["    ret = 1 - o;" if paper else "    ret = o;", "}"]
    return "\n".join(L)


def wave(n, per_point, samples, dots=0, thick=0):
    return dict(n=n, per_point=list(per_point), samples=samples, dots=dots, thick=thick)


def write(path, waves, per_frame, init, comp_src):
    out = ["MILKDROP_PRESET_VERSION=201", "PSVERSION=2", "PSVERSION_WARP=2", "PSVERSION_COMP=2", "[preset00]"]
    out += [f"{k}={v:.5f}" if isinstance(v, float) else f"{k}={v}" for k, v in BASE.items()]
    for w in [wave(0, RECORDER, 480)] + waves:
        i = w["n"]
        out += [f"wavecode_{i}_enabled=1", f"wavecode_{i}_samples={w['samples']}", f"wavecode_{i}_sep=0",
                f"wavecode_{i}_bSpectrum=0", f"wavecode_{i}_bUseDots={w['dots']}",
                f"wavecode_{i}_bDrawThick={w['thick']}", f"wavecode_{i}_bAdditive=1",
                f"wavecode_{i}_scaling=1.00000", f"wavecode_{i}_smoothing=0.00000",
                f"wavecode_{i}_r=1.000", f"wavecode_{i}_g=1.000", f"wavecode_{i}_b=1.000",
                f"wavecode_{i}_a={0 if i == 0 else 1}.000"]
        out += [f"wave_{i}_per_point{k + 1}={line}" for k, line in enumerate(w["per_point"])]
    out += [f"per_frame_init_{k + 1}={line}" for k, line in enumerate(init)]
    out += [f"per_frame_{k + 1}={line}" for k, line in enumerate(per_frame)]
    out += [f"warp_{k + 1}=`{line}" for k, line in enumerate(WARP.split("\n"))]
    out += [f"comp_{k + 1}=`{line}" for k, line in enumerate(comp_src.split("\n"))]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\r\n", encoding="latin-1", errors="replace") as f:
        f.write("\n".join(out) + "\n")


def largest_prime_at_most(n):
    for m in range(max(2, n), 1, -1):
        if all(m % d for d in range(2, int(m ** 0.5) + 1)):
            return m
    return 2


# ---- the modes: each says how many points it has and how to place point n (px, py, dd, vv) ----

class Mode:
    def __init__(self, p):
        self.p = p
        test = int(p["vizTest"])
        self.sx, self.sy, self.sz = ((6 + test,) * 3 if test else
                                     (int(p["vizSrcX"]), int(p["vizSrcY"]), int(p["vizSrcZ"])))
        self.audio = self.sx < 7
        self.reach = int(round(p["vizReach"]))
        self.reach2 = int(round(p["vizReach2"]))

    def X(self, k): return src(self.sx, k)
    def Y(self, k): return src(self.sy, k)
    def Z(self, k): return src(self.sz, k)

    # Lines: a list of (samples, order lines that set n and vv from j). Default: chords at Reach.
    def chord_orders(self, N):
        orders = []
        for R in (self.reach, self.reach2):
            if R > 0:
                orders.append((N, [f"n = (j*{R % N or 1}) % {N};", "vv = 1;"]))
        return orders

    # How many sample positions one pass of the figure covers (the per-frame step q6 = this / N).
    def length(self):
        return f"q16*{self.p['vizSpan']:.3f}"


class Chords(Mode):
    N = 509
    def __init__(self, p, three_d):
        super().__init__(p)
        self.three_d = three_d
    def point(self):
        L = ["kx = q15 - n*q6;", f"x3 = {self.X('kx')};", f"y3 = {self.Y('kx - q14')};"]
        if self.three_d:
            return L + [f"z3 = {self.Z('kx - 2*q14')};"] + PROJECT + ["vv = 1;"]
        return L + ["px = x3; py = y3; dd = 1; vv = 1;"]
    def lines(self):
        return self.chord_orders(self.N)


class Attractor(Mode):
    N = 509
    def point(self):
        D = [0.0, 1.0, 2.6, 4.1, 5.9]
        L = ["ka = q15 - n*q6;"]
        L += [f"v{k} = {self.X(f'ka - {D[k] * 0.6:.2f}*q14')};" for k in range(5)]
        for k, (i, j) in enumerate([(0, 3), (1, 4), (2, 4)]):   # turned in three planes by 4D Turn
            c, s = f"q{17 + 2 * k}", f"q{18 + 2 * k}"
            L += [f"t_ = v{i}*{c} - v{j}*{s}; v{j} = v{i}*{s} + v{j}*{c}; v{i} = t_;"]
        L += ["sv = 2.6/(2.6 - 0.8*v4);", "sw = 2.4/(2.4 - v3*sv)*sv*0.55;",
              "x3 = v0*sw; y3 = v1*sw; z3 = v2*sw;"] + PROJECT + ["vv = below(abs(sw), 2.5);"]
        return L
    def lines(self):
        return [(self.N, ["n = j;", "vv = 1;"])] + self.chord_orders(self.N)
    def length(self):
        return f"q16*{self.p['vizSpan']:.3f}"


class Hypertrace(Mode):
    N = 509
    def __init__(self, p, second=False):
        super().__init__(p)
        self.T = "q14*1.12" if second else "q14"
    def point(self):
        T = self.T
        L = ["ka = q15 - n*q6;", f"v0 = {self.X('ka')};", f"v1 = {self.X(f'ka - {T}')};",
             f"v2 = {self.X(f'ka - 2*{T}')};", f"v3 = {self.X(f'ka - 3*{T}')};"]
        for k, i in enumerate((0, 1, 2)):   # XW, YW, ZW
            c, s = f"q{17 + 2 * k}", f"q{18 + 2 * k}"
            L += [f"t_ = v{i}*{c} - v3*{s}; v3 = v{i}*{s} + v3*{c}; v{i} = t_;"]
        L += ["w4 = 2.4/(2.4 - v3*0.8);", "x3 = v0*w4*0.6; y3 = v1*w4*0.6; z3 = v2*w4*0.6;"] + PROJECT + ["vv = 1;"]
        return L
    def lines(self):
        return [(self.N, ["n = j;", "vv = 1;"])] + self.chord_orders(self.N)


class Mandala(Mode):
    def __init__(self, p):
        super().__init__(p)
        self.C = max(1, min(8, int(round(p["vizSpan"]))))
        self.Mc = largest_prime_at_most(509 // self.C)
        self.N = self.C * self.Mc
    def point(self):
        C, Mc = self.C, self.Mc
        return [f"c_ = int(n/{Mc}); i_ = n - c_*{Mc};",
                f"vx = {self.X(f'q15 - c_*q16 - q16 + i_*q16/{Mc}')};",
                "rd = 0.52 + 0.45*vx;", f"an = 6.2831853*i_/{Mc} - 1.5707963;",
                f"px = rd*cos(an); py = -rd*sin(an); dd = 1 - c_/{C}; vv = 1;"]
    def lines(self):
        if self.reach <= 0:
            return []
        R = self.reach % self.Mc or 1
        return [(self.N, [f"c_ = int(j/{self.Mc}); k_ = j - c_*{self.Mc};",
                          f"n = c_*{self.Mc} + (k_*{R}) % {self.Mc};", "vv = above(k_, 0);"])]


class Tunnel(Mode):
    def __init__(self, p):
        super().__init__(p)
        self.K = max(2, min(24, int(round(p["vizSpan"] * 4))))
        self.Mr = max(8, 509 // self.K)
        self.N = self.K * self.Mr
        self.dz = 0.08 + 0.5 * p["vizDepth"] / 100
    def point(self):
        K, Mr = self.K, self.Mr
        return [f"k_ = int(n/{Mr}); i_ = n - k_*{Mr};",
                f"vx = {self.X(f'q15 - k_*q16 - q16 + i_*q16/{Mr}')};",
                f"wt = 1/(1 + k_*{self.dz:.3f}); sw_ = (1 - wt)*0.5;",
                "rd = 0.55 + 0.4*vx;", f"an = 6.2831853*i_/{Mr} + q1;",
                "px = rd*cos(an)*wt + sw_*sin(q1*0.7); py = rd*sin(an)*wt + sw_*cos(q1*0.5);",
                f"dd = 1 - k_/{K}; vv = 1;"]
    def lines(self):
        K, Mr = self.K, self.Mr
        rings = (self.N, [f"k_ = int(j/{Mr}); i_ = j - k_*{Mr};",
                          f"n = k_*{Mr} + (i_ + 1) % {Mr};", "vv = above(i_, 0);"])
        # Ring to ring, inward (each spoke of the tunnel), a point per ring.
        depth = (min(512, Mr * K), [f"i_ = int(j/{K}); k_ = j - i_*{K};", f"n = k_*{Mr} + i_;",
                                    "vv = above(k_, 0);"])
        out = [rings, depth]
        if self.reach > 0:
            R = self.reach % Mr or 1
            out.append((self.N, [f"k_ = int(j/{Mr}); i_ = j - k_*{Mr};",
                                 f"n = k_*{Mr} + (i_*{R}) % {Mr};", "vv = above(i_, 0);"]))
        return out


class Sphere(Mode):
    N = 509
    def point(self):
        return ["fr_ = n/508;", "lat = -1.5708 + 3.14159*fr_;", "lon = fr_*6.2831853*14;",
                "ph_ = fr_*14 - int(fr_*14);",
                f"vx = {self.X('q15 - q16 + ph_*q16')};",
                "rd = 0.55*(1 + 0.35*vx);",
                "x3 = rd*cos(lat)*cos(lon); y3 = rd*sin(lat); z3 = rd*cos(lat)*sin(lon);"] + PROJECT + ["vv = 1;"]
    def lines(self):
        return [(self.N, ["n = j;", "vv = 1;"])]


class Sections(Mode):
    # A dot where X rises through zero, at (Y a Delay later, Z two Delays later). From the music: the
    # crossings the recorder found this frame (Trail builds the picture). From a test wave: one cycle
    # after another, each a 240th of a cycle later (a slow detune), so the section is drawn whole.
    N = 240
    def point(self):
        if self.audio:   # newest first from the history ring that history() fills
            return ["m_ = (q9 - 1 - n + 480) % 240;", "px = gmegabuf(3000 + m_*2); py = gmegabuf(3001 + m_*2);",
                    "dd = 1 - n/240; vv = 1;"]
        else:
            L = ["kc = n*q16 + n*q16/240;", "vv = 1;"]
        return L + [f"px = {self.Y('kc + q14')}; py = {self.Z('kc + 2*q14')}; dd = 1 - n/240;"]
    def lines(self):
        return [(self.N, ["n = j;", "vv = 1;"])] if self.reach > 0 else []
    # Per frame: last frame's crossings pushed into a 240-section ring, so the picture has a past as
    # SwarmSynth's long ring gives it (one frame's few crossings alone are a handful of dots).
    def history(self):
        if not self.audio:
            return []
        return [READ_GAIN, "c_ = 0;",
                "loop(gmegabuf(1004), kc = gmegabuf(1100 + c_); "
                f"gmegabuf(3000 + hd_*2) = {self.Y('kc + q14')}; gmegabuf(3001 + hd_*2) = {self.Z('kc + 2*q14')}; "
                "hd_ = (hd_ + 1) % 240; c_ = c_ + 1;);", "q9 = hd_;"]


class Hopf(Mode):
    N = 512
    def point(self):
        return ["ci = int(n/32); pi_ = n - ci*32;",
                f"eta = min(1.5, max(0.07, 0.7854 + 0.55*{self.X('q15 - ci*7')}));",
                f"xi = 6.2831853*ci/16 + 0.9*{self.X('q15 - ci*7 - 40')} + q1;",
                "ps = 6.2831853*min(29, max(0, pi_ - 1))/29;",
                "p0 = cos(eta)*cos(ps); p1 = cos(eta)*sin(ps);",
                "p2 = sin(eta)*cos(xi + ps); p3 = sin(eta)*sin(xi + ps);",
                "r1 = p1*q17 - p3*q18; r3 = p1*q18 + p3*q17;",
                "d_ = 1/(1.2 - r3);", "px = p0*d_*0.55; py = r1*d_*0.55; dd = min(1, 1/d_);",
                "vv = (1 - equal(pi_, 0))*(1 - equal(pi_, 31))*below(d_, 3);"]
    def lines(self):
        return [(self.N, ["n = j;", "vv = 1;"])]


def make_mode(p):
    m = int(p["vizMode"])
    name = MODES[m]
    if name in ("Chords", "3D"):
        return Chords(p, name == "3D")
    return {"Mandala": Mandala, "Tunnel": Tunnel, "Sphere": Sphere, "Sections": Sections,
            "Hypertrace": Hypertrace, "Attractor": Attractor, "Hopf": Hopf}[name](p)


def build(p, path):
    md = make_mode(p)
    br = p["vizBright"] / 100
    lines_a = min(1.0, 0.9 * br * p["vizLines"] / 100)
    spokes_a = min(1.0, 0.12 * br * p["vizSpokes"] / 100)
    point = [READ_GAIN] + md.point()
    shade = "fc_ = 1 - q8*(1 - dd);"
    tail = (FOLD if int(p["vizFold"]) == 3 else []) + TAIL
    # A long Trail piles every frame's ink on the last: draw fainter so it builds to white, not past it.
    keep = 1 - 0.75 * p["vizTrail"] / 100
    lines_a *= keep; spokes_a *= keep; br_d = br * keep

    layers = []   # in order of importance; the first three are drawn
    line_orders = md.lines() if p["vizLines"] > 0 else []
    if line_orders:
        layers.append(("lines", line_orders[0]))
    if p["vizDot"] > 0.05:
        layers.append(("dots", None))
    if p["vizSpokes"] > 0:
        layers.append(("spokes", None))
    layers += [("lines", o) for o in line_orders[1:]]
    if isinstance(md, Hypertrace) and p["vizLines"] > 0:   # the second trace, at 1.12 x the Delay
        md2 = Hypertrace(p, second=True)
        layers.insert(1, ("lines2", (md2.N, ["n = j;", "vv = 1;"], md2)))

    waves = []
    for slot, (kind, spec) in enumerate(layers[:3], start=1):
        if kind in ("lines", "lines2"):
            N, order = spec[0], spec[1]
            pt = [READ_GAIN] + (spec[2].point() if kind == "lines2" else md.point())
            code = [f"j = int(sample*{N - 1} + 0.5);"] + order + ["vo = vv;"] + pt[1:] + [shade] + tail + \
                   [f"a = vo*vv*{lines_a * (0.5 if kind == 'lines2' else 1):.3f}*(0.25 + 0.75*fc_);"]
            waves.append(wave(slot, [READ_GAIN] + code, N))
        elif kind == "dots":
            code = [f"n = int(sample*{md.N - 1} + 0.5);"] + point[1:] + [shade] + tail + \
                   [f"a = vv*{br_d:.3f}*(0.25 + 0.75*fc_);"]
            waves.append(wave(slot, [READ_GAIN] + code, md.N, dots=1, thick=int(p["vizDot"] >= 2)))
        else:   # spokes: point, centre, next point...
            S = min(256, md.N)
            code = [f"m_ = int(sample*{2 * S - 1} + 0.5); n = int(int(m_/2)*{md.N}/{S});", "od = m_ % 2;"] + \
                   point[1:] + [shade] + tail + \
                   ["x = if(od, 0.5, x); y = if(od, 0.5, y);", f"a = vv*{spokes_a:.3f}*(0.25 + 0.75*fc_);"]
            waves.append(wave(slot, [READ_GAIN] + code, 2 * S))

    # Per frame: SwarmSynth's clocks and the patch's numbers into q variables.
    lock, delay = int(p["vizLock"]), p["vizDelay"]
    persp = p["vizPersp"] / 100
    D = 1.6 + 8.0 * (1 - persp)
    period = "q11" if not md.audio else "q13"
    tau = f"q16*{delay / 100:.4f}" if lock == 0 else f"{delay / 100 * 0.012 * 48000:.2f}"
    span_len = md.length()
    limit = "1e9" if not md.audio else "max(40, 470 - 6*q14)"
    t4 = p["vizTurn4"]
    if isinstance(md, Attractor):
        turns = ["t4_", "t4_*0.8 + 0.5", "t4_*0.53 + 1.3"]
    elif isinstance(md, Hopf):
        turns = ["t4_*0.43"]
    else:
        turns = ["t4_", "t4_*0.73 + 0.6", "t4_*0.41 + 1.1"]
    frame = [
        "dt_ = min(0.25, max(0, time - lt_)); lt_ = time;",
        "hit = above(bass, 1.4)*above(bass, bass_att*1.2)*above(time - lh_, 0.25); lh_ = if(hit, time, lh_);",
        f"dir_ = if({int(p['vizFlip'])}*hit, -dir_, dir_);",
        f"ay_ = ay_ + dir_*{p['vizSpin'] / 100 * 1.2:.4f}*dt_;",
        f"ax_ = ax_ + dir_*{p['vizTumble'] / 100 * 0.9:.4f}*dt_;",
        f"ft_ = ft_ + {p['vizTurn'] / 100 * 0.8:.4f}*dt_;",
        f"t4_ = t4_ + {t4 / 100 * 0.9:.4f}*dt_;",
        f"q1 = ay_; q2 = {math.radians(p['vizTilt']):.4f} + ax_; q3 = {D if persp >= 0.01 else 0:.3f};",
        "pn_ = pn_*0.8 + 0.2*min(1, max(0, (bass_att - 0.8)/1.2));",
        f"q7 = {0.44 * p['vizZoom'] / 100:.4f}*(1 + {p['vizPulse'] / 100 * 0.35:.4f}*pn_);",
        f"q8 = {p['vizCue'] / 100:.3f};",
        f"q10 = {math.radians(p['vizAngle']):.4f} + ft_; q28 = q10; q27 = {int(round(p['vizSegs']))};",
        "q11 = 96; q12 = 1.6 + 1.4*sin(time*0.7);",
        "q13 = min(240, max(8, gmegabuf(1002)));",
        f"q16 = {period};",
        f"q14 = max(1, min(110, {tau}*(1 + {p['vizDrift'] / 100 * 0.6:.4f}*sin(time*0.35))));",
        "q15 = " + ("gmegabuf(1003);" if md.audio else "470;"),
        f"q6 = min({span_len}, {limit})/{md.N};",
        f"q30 = {p['vizTrail'] / 100:.3f};",
        "q26 = time*0.03 + bass_att*0.04;",
        "q32 = min(1, pixelsy/pixelsx); q29 = min(1, pixelsx/pixelsy);",
    ]
    frame += md.history() if isinstance(md, Sections) else []
    for k, t in enumerate(turns):
        frame.append(f"q{17 + 2 * k} = cos({t}); q{18 + 2 * k} = sin({t});")
    init = ["hd_ = 0; dir_ = 1; ay_ = 0; ax_ = 0; ft_ = 0; t4_ = 0; lt_ = 0; lh_ = 0; pn_ = 0;",
            "gmegabuf(1001) = 0.1; gmegabuf(1002) = 100; gmegabuf(1003) = 470; gmegabuf(1004) = 0;"]
    write(path, waves, frame, init,
          comp(int(p["vizFold"]), int(p["vizColour"]), int(p["vizColSet"]), int(p["vizInk"])))


def read_patch(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    p = dict(DEFAULTS)
    p.update({k: float(v) for k, v in re.findall(r'<PARAM id="(viz\w+)" value="([^"]*)"', text) if k in DEFAULTS})
    return p


if __name__ == "__main__":
    made, skipped = [], []
    for f in sorted(glob.glob(os.path.join(SWARM, "*", "*.swarm"))):
        name = os.path.splitext(os.path.basename(f))[0]
        p = read_patch(f)
        if p["vizOn"] < 0.5:
            skipped.append(name)
            continue
        build(p, os.path.join(HERE, "Patches", f"{name}.milk"))
        made.append(f"{name}  ({MODES[int(p['vizMode'])]})")

    # One preset per mode at SwarmSynth's defaults, with a trail so the music builds a picture.
    for m in ("Chords", "3D", "Mandala", "Tunnel", "Sphere", "Sections", "Hypertrace", "Attractor", "Hopf"):
        p = dict(DEFAULTS, vizOn=1, vizMode=MODES.index(m), vizTrail=60)
        build(p, os.path.join(HERE, "Modes", f"SwarmSynth - {m}.milk"))

    print("patches:", len(made)); print("\n".join("  " + m for m in made))
    print("visualiser off, skipped:", ", ".join(skipped))
