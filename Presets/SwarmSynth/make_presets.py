"""MilkDrop presets from SwarmSynth Revived's visuals (Documents\\SwarmSynthRevived\\Source\\VizEngine.h,
HyperspaceVisualizer.h, LifeEngine.h). Run:  python make_presets.py   -> writes the .milk files beside it.

How SwarmSynth's ideas map onto MilkDrop:
  - SwarmSynth reads its own audio rings at any delay. MilkDrop gives a custom wave the newest 480
    samples per frame, so wave 0 of every preset is an invisible RECORDER: it copies the mono mix into
    gmegabuf(0..479) and keeps an auto-range peak in gmegabuf(1001) (SwarmSynth's AUTO-RANGE: the
    loudest recent level fills the frame). Waves 1-3 read any sample, any delay, in any order from it.
  - CHORDS' string art (dot i joined to dot i + Reach) = visiting the dots in steps of Reach.
  - Trail = MilkDrop's own feedback (the warp shader multiplies last frame by q30).
  - TUNNEL / MANDALA's rows of older cycles = the feedback zooming inward: last frame's ring shrinks.
  - FOLD Kaleido = a polar fold in the composite shader.
  - Ink white on black is SwarmSynth's default look; colour is lightness-led (Daxy is colour blind).
Every preset is ours (Daxy & Claude, 2026); the equations are SwarmSynth Revived's, re-expressed.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

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

# Wave 0 in every preset: the recorder (see the docstring). Mono, unsmoothed, 480 samples.
RECORDER_POINT = [
    "i = int(sample*479 + 0.5);",
    "v = (value1 + value2)*0.5;",
    "gmegabuf(i) = v;",
    "pk = if(equal(i,0), 0, pk);",
    "pk = max(pk, abs(v));",
    "gmegabuf(1001) = if(equal(i,479), max(max(pk, gmegabuf(1001)*0.985), 0.004), gmegabuf(1001));",
]

# Reader prelude for per-point code: gn = auto-range gain (not g: that is the green channel); s(k) in a wave is written out as
# gmegabuf((k + 4800) % 480)*gn (eel has no functions).
def S(expr):
    return f"gmegabuf((int({expr}) + 4800) % 480)*gn"

READ_GAIN = "gn = 0.42/gmegabuf(1001);"

WARP_DECAY = """shader_body
{
    ret = tex2D(sampler_main, uv).xyz;
    ret = ret*q30 - 0.003;
}"""

def comp(kaleido=False, glow=False, tint=False):
    lines = ["shader_body", "{", "    float2 p = uv;"]
    if kaleido:  # q27 = segments, q28 = turn (radians); SwarmSynth's kaleidoFold()
        lines += [
            "    float2 sc = float2(q32, q29);",
            "    float2 d = (uv - 0.5)/sc;",
            "    float r = length(d);",
            "    float w = 6.2831853/q27;",
            "    float a = atan2(d.y, d.x) + q28;",
            "    a = a - 2*w*floor(a/(2*w));",
            "    a = min(a, 2*w - a);",
            "    p = 0.5 + float2(cos(a), sin(a))*r*sc;",
        ]
    lines += ["    ret = tex2D(sampler_main, p).xyz;"]
    if glow:
        lines += ["    ret += GetBlur1(p)*0.6;"]
    if tint:  # lightness first: the ink keeps its brightness, colour only rides on top
        lines += [
            "    float l = dot(ret, float3(0.333, 0.333, 0.333));",
            "    float3 hue = 0.5 + 0.5*cos(6.2831853*(q26 + float3(0, 0.33, 0.67)));",
            "    ret = lerp(float3(l, l, l), l*hue*1.6, 0.75);",
        ]
    lines += ["    ret = 1 - exp(-ret*1.8);", "}"]
    return "\n".join(lines)


def wave(n, per_point, per_frame=(), samples=480, dots=0, thick=0, additive=1, r=1, g=1, b=1, a=1, round_=True):
    if round_:
        per_point = list(per_point) + ROUND
    return dict(n=n, per_point=list(per_point), per_frame=list(per_frame), samples=samples,
                dots=dots, thick=thick, additive=additive, r=r, g=g, b=b, a=a)


def shape(n, per_frame, sides=40, num_inst=1, thick=1, additive=1, rad=0.1, a=0.0, border_a=1.0):
    return dict(n=n, per_frame=list(per_frame), sides=sides, num_inst=num_inst, thick=thick,
                additive=additive, rad=rad, a=a, border_a=border_a)


def write(name, waves, per_frame, init=(), shapes=(), base=None, warp=WARP_DECAY, comp_src=None, ps=2):
    vals = dict(BASE)
    vals.update(base or {})
    out = ["MILKDROP_PRESET_VERSION=201", f"PSVERSION={ps}", f"PSVERSION_WARP={ps}", f"PSVERSION_COMP={ps}",
           "[preset00]"]
    for k, v in vals.items():
        out.append(f"{k}={v:.5f}" if isinstance(v, float) else f"{k}={v}")

    allwaves = [wave(0, RECORDER_POINT, a=0, round_=False)] + list(waves)
    for w in allwaves:
        i = w["n"]
        out += [f"wavecode_{i}_enabled=1", f"wavecode_{i}_samples={w['samples']}",
                f"wavecode_{i}_sep=0", f"wavecode_{i}_bSpectrum=0",
                f"wavecode_{i}_bUseDots={w['dots']}", f"wavecode_{i}_bDrawThick={w['thick']}",
                f"wavecode_{i}_bAdditive={w['additive']}", f"wavecode_{i}_scaling=1.00000",
                f"wavecode_{i}_smoothing=0.00000", f"wavecode_{i}_r={w['r']:.3f}",
                f"wavecode_{i}_g={w['g']:.3f}", f"wavecode_{i}_b={w['b']:.3f}",
                f"wavecode_{i}_a={w['a']:.3f}"]
        out += [f"wave_{i}_per_frame{k + 1}={line}" for k, line in enumerate(w["per_frame"])]
        out += [f"wave_{i}_per_point{k + 1}={line}" for k, line in enumerate(w["per_point"])]

    for s in shapes:
        i = s["n"]
        out += [f"shapecode_{i}_enabled=1", f"shapecode_{i}_sides={s['sides']}",
                f"shapecode_{i}_additive={s['additive']}", f"shapecode_{i}_thickOutline={s['thick']}",
                f"shapecode_{i}_textured=0", f"shapecode_{i}_num_inst={s['num_inst']}",
                f"shapecode_{i}_x=0.500", f"shapecode_{i}_y=0.500", f"shapecode_{i}_rad={s['rad']:.5f}",
                f"shapecode_{i}_ang=0.00000", f"shapecode_{i}_tex_ang=0.00000", f"shapecode_{i}_tex_zoom=1.00000",
                f"shapecode_{i}_r=1.000", f"shapecode_{i}_g=1.000", f"shapecode_{i}_b=1.000",
                f"shapecode_{i}_a={s['a']:.3f}", f"shapecode_{i}_r2=1.000", f"shapecode_{i}_g2=1.000",
                f"shapecode_{i}_b2=1.000", f"shapecode_{i}_a2={s['a']:.3f}",
                f"shapecode_{i}_border_r=1.000", f"shapecode_{i}_border_g=1.000",
                f"shapecode_{i}_border_b=1.000", f"shapecode_{i}_border_a={s['border_a']:.3f}"]
        out += [f"shape_{i}_per_frame{k + 1}={line}" for k, line in enumerate(s["per_frame"])]

    out += [f"per_frame_init_{k + 1}={line}" for k, line in enumerate(init)]
    out += [f"per_frame_{k + 1}={line}" for k, line in enumerate(per_frame)]
    out += [f"warp_{k + 1}=`{line}" for k, line in enumerate(warp.split("\n"))]
    out += [f"comp_{k + 1}=`{line}" for k, line in enumerate((comp_src or comp()).split("\n"))]

    path = os.path.join(HERE, f"SwarmSynth - {name}.milk")
    with open(path, "w", newline="\r\n") as f:
        f.write("\n".join(out) + "\n")
    return path


# Common per-frame lines: q30 trail, q26 slow hue clock, q27/q28 kaleido.
# q32 / q29 = how much to shrink x / y offsets from the centre so circles stay round: BeatDrop's
# default screen-dependent mode stretches wave coordinates to the window's shape.
def frame(trail, extra=()):
    return [f"q30 = {trail};", "q26 = time*0.03 + bass_att*0.05;",
            "q32 = min(1, pixelsy/pixelsx);", "q29 = min(1, pixelsx/pixelsy);"] + list(extra)

ROUND = ["x = 0.5 + (x - 0.5)*q32;", "y = 0.5 + (y - 0.5)*q29;"]


# 1-2. CHORDS: X(t) against X(t + tau), dots joined i -> i + Reach (string art), plus the trace.
def chords_waves(reach_expr, ink=1.0):
    trace = [READ_GAIN, "k = int(sample*479);",
             f"x = 0.5 + {S('k')};", f"y = 0.5 + {S('k - 90')};", f"a = {0.35 * ink};"]
    art = [READ_GAIN, "j = int(sample*479);", f"k = (j*({reach_expr})) % 480;",
           f"x = 0.5 + {S('k')};", f"y = 0.5 + {S('k - 90')};", f"a = {0.55 * ink};"]
    return [wave(1, trace), wave(2, art)]


write("Chords",
      chords_waves("17 + int(bass_att*4)"),
      frame(0.82, ["zoom = 1.0;"]))

write("Chords Kaleido",
      chords_waves("29 + int(treb_att*6)"),
      frame(0.9, ["q27 = 6;", "q28 = time*0.07;", "zoom = 0.995;", "rot = 0.002*sin(time*0.3);"]),
      comp_src=comp(kaleido=True, tint=True))

# 3. MANDALA: one cycle round a circle, radius = the wave; feedback zooms in, so older rings sit inside.
write("Mandala",
      [wave(1, [READ_GAIN, "j = int(sample*479);", "an = sample*6.2831853 - 1.5708;",
                f"rr = 0.27 + 0.16*{S('j')}/0.42;",
                "x = 0.5 + rr*cos(an);", "y = 0.5 + rr*sin(an);", "a = 0.7;"]),
       wave(2, [READ_GAIN, "m = int(sample*479);", "j = (m*37) % 480;", "an = j/480*6.2831853 - 1.5708;",
                f"rr = 0.27 + 0.16*{S('j')}/0.42;",
                "x = 0.5 + rr*cos(an);", "y = 0.5 + rr*sin(an);", "a = 0.25;"])],
      frame(0.94, ["zoom = 0.965;", "rot = 0.01;", "q27 = 8;", "q28 = time*0.05;"]),
      comp_src=comp(kaleido=True, tint=True))

# 4. TUNNEL: rings shrinking to a swaying vanishing point.
write("Tunnel",
      [wave(1, [READ_GAIN, "j = int(sample*479);", "an = sample*6.2831853 + time*0.4;",
                f"rr = 0.36 + 0.12*{S('j')}/0.42;",
                "x = 0.5 + rr*cos(an);", "y = 0.5 + rr*sin(an);", "a = 0.9;"], thick=1)],
      frame(0.965, ["zoom = 0.93 - bass_att*0.01;", "rot = 0.006*sin(time*0.21);",
                    "cx = 0.5 + 0.08*sin(time*0.7*0.5);", "cy = 0.5 + 0.08*cos(time*0.5*0.5);"]))

# 5. TERRAIN: the newest cycle as a line at the front; feedback recedes it toward the horizon.
write("Terrain",
      [wave(1, [READ_GAIN, "j = int(sample*479);", "x = 0.06 + sample*0.88;",
                f"y = 0.78 - {S('j')}*0.35;", "a = 0.95;"], thick=1, round_=False)],
      frame(0.975, ["zoom = 0.955;", "cx = 0.5;", "cy = 0.22;"]))

# 6. SPHERE: a spiral of latitude rings on a turning globe, each ring one cycle of the wave.
write("Sphere",
      [wave(1, [READ_GAIN, "lat = -1.5708 + 3.14159*sample;", "lon = sample*6.2831853*14 + time*0.5;",
                "j = int((sample*14 - int(sample*14))*479);",
                f"rr = 0.3*(1 + 0.4*{S('j')});",
                "x3 = rr*cos(lat)*cos(lon);", "y3 = rr*sin(lat);", "z3 = rr*cos(lat)*sin(lon);",
                "ti = 0.45 + 0.2*sin(time*0.13);",
                "y4 = y3*cos(ti) - z3*sin(ti);", "z4 = y3*sin(ti) + z3*cos(ti);",
                "w = 1.6/(1.6 + z4);", "x = 0.5 + x3*w;", "y = 0.5 + y4*w;",
                "a = 0.25 + 0.75*min(1, max(0, 0.5 - z4*1.4));"], samples=512)],
      frame(0.55))

# 7. SECTIONS: a dot each time the wave crosses zero rising, at (wave a Delay later, two Delays later).
write("Sections",
      [wave(1, [READ_GAIN, "j = int(sample*479);",
                f"c = below({S('j - 1')}, 0)*above({S('j')}, 0);",
                f"x = if(c, 0.5 + 1.1*{S('j + 31')}, -2);",
                f"y = if(c, 0.5 + 1.1*{S('j + 62')}, -2);", "a = c;"], dots=1, thick=1)],
      frame(0.992, ["zoom = 1.002;"]),
      comp_src=comp(glow=True))

# 8. HYPERTRACE: (x(t), x(t-T), x(t-2T), x(t-3T)) turned in 4D, two traces at T and 1.12 T.
def hyper(n, T, alpha):
    return wave(n, [READ_GAIN, "j = int(sample*479);",
                    f"x0 = {S('j')};", f"x1 = {S(f'j - {T}')};", f"x2 = {S(f'j - {2*T}')};", f"x3 = {S(f'j - {3*T}')};",
                    "ta = time*0.31;", "tb = time*0.23;",
                    "u0 = x0*cos(ta) - x3*sin(ta);", "u3 = x0*sin(ta) + x3*cos(ta);",
                    "u1 = x1*cos(tb) - x2*sin(tb);", "u2 = x1*sin(tb) + x2*cos(tb);",
                    "w4 = 1.3/(1.3 - u3);", "w3 = 1.8/(1.8 + u2*w4);",
                    "x = 0.5 + u0*w4*w3*0.9;", "y = 0.5 + u1*w4*w3*0.9;", f"a = {alpha};"])

write("Hypertrace", [hyper(1, 45, 0.8), hyper(2, 50, 0.4)], frame(0.85))

# 9. KNOT: (cos t, sin t, cos rt, sin rt) on the Clifford torus, stereographic; the ratio steps on hits.
write("Knot",
      [wave(1, [READ_GAIN, "tt = sample*6.2831853*q3;",
                "fr = tt/6.2831853 - int(tt/6.2831853);",
                f"e = 0.7854 + 0.25*{S('fr*479')};",
                "u = q2*tt + time*0.2;",
                "p0 = cos(e)*cos(tt);", "p1 = cos(e)*sin(tt);", "p2 = sin(e)*cos(u);", "p3 = sin(e)*sin(u);",
                "ta = time*0.17;", "r0 = p0*cos(ta) - p3*sin(ta);", "r3 = p0*sin(ta) + p3*cos(ta);",
                "d = 1/(1.15 - r3);", "x = 0.5 + r0*d*0.3;", "y = 0.5 + p1*d*0.3;",
                "a = if(below(d, 3.5), 0.9, 0);"], samples=512, thick=1)],
      frame(0.8, ["hit = above(bass, 1.5)*above(time - lasthit, 1.5);",
                  "lasthit = if(hit, time, lasthit);",
                  "kn = (kn + hit) % 6;",
                  "q2 = if(equal(kn,0), 1.5, if(equal(kn,1), 1.6667, if(equal(kn,2), 2.5, if(equal(kn,3), 1.3333, if(equal(kn,4), 2.3333, 3)))));",
                  "q3 = if(equal(kn,0), 2, if(equal(kn,1), 3, if(equal(kn,2), 2, if(equal(kn,3), 3, if(equal(kn,4), 3, 1)))));"]),
      comp_src=comp(glow=True))

# 10. HOPF: linked circles, each the lift of a point on the 2-sphere; 4 waves x 16 circles x 32 points.
def hopf(n):
    return wave(n, [READ_GAIN, "m = int(sample*511 + 0.5);", "ci = int(m/32);", "pi_ = m % 32;",
                    f"k = {(n - 1) * 16} + ci;",
                    f"eta = min(1.5, max(0.07, 0.7854 + 0.55*{S('k*7')}));",
                    f"xi = 6.2831853*k/48 + 0.9*{S('k*7 - 40')} + time*0.1;",
                    "ps = 6.2831853*min(29, max(0, pi_ - 1))/29;",
                    "p0 = cos(eta)*cos(ps);", "p1 = cos(eta)*sin(ps);",
                    "p2 = sin(eta)*cos(xi + ps);", "p3 = sin(eta)*sin(xi + ps);",
                    "ta = time*0.13;", "r1 = p1*cos(ta) - p3*sin(ta);", "r3 = p1*sin(ta) + p3*cos(ta);",
                    "d = 1/(1.2 - r3);", "x = 0.5 + p0*d*0.26;", "y = 0.5 + r1*d*0.26;",
                    "a = if(equal(pi_,0) || equal(pi_,31) || above(d, 3), 0, 0.55);"], samples=512)

write("Hopf", [hopf(1), hopf(2), hopf(3)], frame(0.7), comp_src=comp(tint=True))

# 11. BUBBLES: a hit blows a big bubble near the middle; while loud, small ones further out; they push
# apart, drift out, shrink and burst. State: gmegabuf(2000 + 4i) = x, y, r (40 bubbles).
BUB_FRAME = frame(0.6, [
    "dt = min(0.25, max(0, time - lastt));", "lastt = time;",
    "hit = above(bass, 1.4)*above(bass, bass_att*1.25)*above(time - lasthit, 0.25);",
    "lasthit = if(hit, time, lasthit);",
    "lvl = min(1, (bass_att + mid_att + treb_att)*0.25);",
    "spawn = spawn + if(above(lvl, 0.08), 27*dt, 0);",
    "nb = 0;",
    "blow = hit;",
    "bd = 0.2*rand(1000)/1000;", "br = 0.12 + 0.38*lvl;",
    "loop(2, if(blow, slot = slot % 40; ba = rand(1000)/1000*6.2831853; gmegabuf(2000 + slot*4) = bd*cos(ba); "
    "gmegabuf(2001 + slot*4) = bd*sin(ba); gmegabuf(2002 + slot*4) = br*0.5; slot = slot + 1; blow = 0, 0);"
    " blow = above(spawn, 1); spawn = spawn - blow; bd = 0.17 + 0.5*rand(1000)/1000; br = 0.02 + 0.08*lvl*rand(1000)/1000;);",
    "i = 0;",
    "loop(40, bx = gmegabuf(2000 + i*4); by = gmegabuf(2001 + i*4); r_ = gmegabuf(2002 + i*4);"
    " dd = sqrt(bx*bx + by*by) + 0.0001; bx = bx + bx*0.05*dt/dd; by = by + by*0.05*dt/dd;"
    " r_ = r_ - r_*0.6*dt; r_ = if(below(r_, 0.006) || above(abs(bx), 0.9) || above(abs(by), 0.9), 0, r_);"
    " gmegabuf(2000 + i*4) = bx; gmegabuf(2001 + i*4) = by; gmegabuf(2002 + i*4) = r_; i = i + 1;);",
    "i = 0;",
    "loop(40, j = i + 1; loop(39 - i, xi_ = gmegabuf(2000 + i*4); yi_ = gmegabuf(2001 + i*4); ri_ = gmegabuf(2002 + i*4);"
    " xj_ = gmegabuf(2000 + j*4); yj_ = gmegabuf(2001 + j*4); rj_ = gmegabuf(2002 + j*4);"
    " ddx = xj_ - xi_; ddy = yj_ - yi_; dd = sqrt(ddx*ddx + ddy*ddy) + 0.00001; ov = ri_ + rj_ + 0.008 - dd;"
    " ov = if(above(ov, 0)*above(ri_, 0)*above(rj_, 0), ov/(4*dd), 0);"
    " gmegabuf(2000 + i*4) = xi_ - ddx*ov; gmegabuf(2001 + i*4) = yi_ - ddy*ov;"
    " gmegabuf(2000 + j*4) = xj_ + ddx*ov; gmegabuf(2001 + j*4) = yj_ + ddy*ov; j = j + 1;); i = i + 1;);",
])

write("Bubbles",
      [wave(1, [READ_GAIN, "j = int(sample*479);", "an = sample*6.2831853;",
                f"rr = 0.05 + 0.03*{S('j')}/0.42 + bass_att*0.01;",
                "x = 0.5 + rr*cos(an);", "y = 0.5 + rr*sin(an);", "a = 0.5;"])],
      BUB_FRAME,
      init=["slot = 0;", "spawn = 0;", "lasthit = 0;", "lastt = 0;",
            "i = 0;", "loop(160, gmegabuf(2000 + i) = 0; i = i + 1;);"],
      shapes=[shape(0, ["x = 0.5 + gmegabuf(2000 + instance*4)*q32;", "y = 0.5 + gmegabuf(2001 + instance*4)*q29;",
                        "rad = gmegabuf(2002 + instance*4);", "border_a = if(above(rad, 0.004), 0.9, 0);",
                        "a = 0;", "a2 = 0;"], sides=36, num_inst=40, rad=0.0)])

# 12. LIFE: Conway's Life on a coarse grid in the warp shader (red = alive), seeded by the wave.
LIFE_WARP = """shader_body
{
    float2 cell = float2(6, 6)*texsize.zw;
    float2 c = (floor(uv/cell) + 0.5)*cell;
    float me = tex2D(sampler_pw_main, c).x;
    float n = 0;
    n += step(0.5, tex2D(sampler_pw_main, c + cell*float2(-1,-1)).x);
    n += step(0.5, tex2D(sampler_pw_main, c + cell*float2( 0,-1)).x);
    n += step(0.5, tex2D(sampler_pw_main, c + cell*float2( 1,-1)).x);
    n += step(0.5, tex2D(sampler_pw_main, c + cell*float2(-1, 0)).x);
    n += step(0.5, tex2D(sampler_pw_main, c + cell*float2( 1, 0)).x);
    n += step(0.5, tex2D(sampler_pw_main, c + cell*float2(-1, 1)).x);
    n += step(0.5, tex2D(sampler_pw_main, c + cell*float2( 0, 1)).x);
    n += step(0.5, tex2D(sampler_pw_main, c + cell*float2( 1, 1)).x);
    float alive = step(0.5, me);
    float next = alive*(step(1.5, n)*step(n, 3.5)) + (1 - alive)*step(2.5, n)*step(n, 3.5);
    next = lerp(alive, next, q31);
    float3 old = tex2D(sampler_pw_main, uv).xyz;
    ret = float3(next, max(next, old.y*0.93), max(next*0.6, old.z*0.97));
}"""

LIFE_COMP = """shader_body
{
    float3 s = tex2D(sampler_pw_main, uv).xyz;
    float l = max(s.x, s.y*0.55 + s.z*0.25);
    float3 hue = 0.5 + 0.5*cos(6.2831853*(q26 + float3(0, 0.33, 0.67)));
    ret = lerp(float3(l, l, l), l*hue*1.5, 0.35*(1 - s.x));
}"""

write("Life",
      [wave(1, [READ_GAIN, "j = int(sample*479);", "x = 0.08 + sample*0.84;",
                f"y = 0.5 + {S('j')}*0.7;", "r = 1;", "g = 1;", "b = 1;", "a = above(gmegabuf(1001), 0.01);"],
            thick=1, additive=0, round_=False)],
      frame(1.0, ["fr_ = fr_ + 1;", "q31 = equal(fr_ % 3, 0);"]),
      warp=LIFE_WARP, comp_src=LIFE_COMP, ps=3)  # 9 lookups + the rule: over ps_2_0's 64 instructions

# 13. HYPERSPACE: SwarmSynth's tesseract cube - 32 edges of a 4D cube, turned in two planes, the wave
# trembling its corners, bass breathing its size.
write("Hyperspace",
      [wave(1, [READ_GAIN, "m = int(sample*127 + 0.5);", "e = int(m/4);", "q = m % 4;",
                "bb = int(e/8);", "kk = e % 8;", "p2 = pow(2, bb);",
                "v = int(kk/p2)*p2*2 + (kk % p2) + if(above(q, 1), p2, 0);",
                "c0 = 2*(v % 2) - 1;", "c1 = 2*(int(v/2) % 2) - 1;", "c2 = 2*(int(v/4) % 2) - 1;", "c3 = 2*(int(v/8) % 2) - 1;",
                f"jit = 1 + 0.25*{S('v*29')};",
                "ta = time*0.27;", "tb = time*0.19;",
                "u0 = c0*cos(ta) - c3*sin(ta);", "u3 = c0*sin(ta) + c3*cos(ta);",
                "u1 = c1*cos(tb) - c2*sin(tb);", "u2 = c1*sin(tb) + c2*cos(tb);",
                "w4 = 2.6/(2.6 - u3);", "w3 = 3.2/(3.2 + u2*w4);",
                "sc = (0.075 + bass_att*0.01)*jit;",
                "x = 0.5 + u0*w4*w3*sc;", "y = 0.5 + u1*w4*w3*sc;",
                "a = if(equal(q,0) || equal(q,3), 0, 0.9);"], samples=128, thick=1)],
      frame(0.85, ["zoom = 1.0;"]),
      comp_src=comp(glow=True, tint=True))

print("written to", HERE)
