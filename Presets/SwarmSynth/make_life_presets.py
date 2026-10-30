"""MilkDrop presets from Daxy's SwarmSynth Revived patches that use LIFE MOD (the Game of Life
sequencer, SwarmSynthRevived\\Source\\LifeEngine.h): one preset per patch with Life on, named after
the patch. Daxy, 2026-10-30: "make some from any preset that use game of life ... can they be warp
or comp shaders?" They are: the WARP shader runs the automaton, the COMP shader draws it. Run:
    python make_life_presets.py   -> Life\\Life - <patch>.milk, and ..\\Textures\\life_<patch>.png
(only the patches in KEEP; install-data.ps1 puts them in the data folder's presets\\SwarmSynth)

What carries over from the patch:
  - The grid: 32 x 32, wrapping (a torus), as SwarmSynth's.
  - The RULE (B/S notation, the six published rules SwarmSynth offers) as birth/survive bit masks.
  - The CLOCK: Life Division (synced, at 120 BPM: MilkDrop has no tempo) or Life Rate, and Evolve
    Every (a generation every N steps). Engine time, so the Speed control slows it too.
  - The PICTURE the patch starts from (SWARM_LIFE's stored cells, else its saved cells) and its
    SENSORS, as a 32 x 32 texture (red = cell, green = sensor). No picture: a random soup at the
    patch's Life Random Density.
  - The MODE: Playhead Scan and Plot show the playhead sweeping the columns, cells flashing as it
    plays them; Sensors (and every mode) flash when a cell is born on a sensor ("On Arrival").
  - BEES (yellow, a black stripe) or WANDERERS (round dots), up to six, if the patch has them.
What MilkDrop changes:
  - KEEP ALIVE becomes the music: a strong beat stirs a square patch of random cells, its size
    from Keep Alive (and some even at zero, or the colony goes still), as SwarmSynth stirs a stalled field.
  - Bees and wanderers wander; they do not play notes or bounce off the colony.
Channels of the feedback picture, which IS the grid (each cell a block of pixels): red alive,
green age (1 newborn, fading), blue the flash. The comp shader draws a square grid from it.
Every preset is ours (Daxy & Claude, 2026).
"""
import glob
import os
import re
import struct
import zlib
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Life")
TEXTURES = os.path.join(HERE, "..", "Textures")
SWARM = os.path.join(os.path.expanduser("~"), "Documents", "SwarmSynth Revived", "Presets")

# LifeEngine.h's rules: (name, birth counts, survive counts, soup density).
RULES = [("Conway", [3], [2, 3], 0.35), ("HighLife", [3, 6], [2, 3], 0.35), ("Seeds", [2], [], 0.10),
         ("Day & Night", [3, 6, 7, 8], [3, 4, 6, 7, 8], 0.50), ("Maze", [3], [1, 2, 3, 4, 5], 0.12),
         ("Life w/o Death", [3], list(range(9)), 0.06)]
# FXParameters.h's syncDivisionChoices(), in quarter notes, by stored index.
DIV_QUARTERS = [4, 6, 8 / 3, 2, 3, 4 / 3, 1, 1.5, 2 / 3, 0.5, 0.75, 1 / 3, 0.25, 0.375, 1 / 6,
                0.125, 0.1875, 1 / 12, 8, 16, 32, 64, 128, 256, 512, 0.0625, 0.09375, 0.0625 * 2 / 3]
DEFAULTS = dict(lifeEnable=0, lifeRule=0, lifeSync=1, lifeDiv=12, lifeRate=8.0, lifeEvolve=4,
                lifeMode=1, lifeKeep=0, lifeDensity=20, lifeBees=0, lifeBeeCount=6, lifeWander=0,
                lifeWandCount=1)
MOVERS = 6  # bees or wanderers drawn, at most
# The ones Daxy kept (2026-10-30: "the first game of life preset set can go except shitty
# wankpuffin, tiktoc, budah1g, felix, night of the piranna"; the Pixel Art felix went too).
KEEP = {"Shitty Wankpuffin", "tiktoc", "buddha 1G", "felix", "Night of the Piranha"}

BASE = dict(
    fRating=4.0, fGammaAdj=1.0, fDecay=1.0, fVideoEchoZoom=1.0, fVideoEchoAlpha=0.0,
    nVideoEchoOrientation=0, nWaveMode=0, bAdditiveWaves=0, bWaveDots=0, bWaveThick=0,
    bModWaveAlphaByVolume=0, bMaximizeWaveColor=0, bTexWrap=1, bDarkenCenter=0, bRedBlueStereo=0,
    bBrighten=0, bDarken=0, bSolarize=0, bInvert=0, fWaveAlpha=0.0, fWaveScale=1.0,
    fWaveSmoothing=0.0, fWaveParam=0.0, fModWaveAlphaStart=0.75, fModWaveAlphaEnd=0.95,
    fWarpAnimSpeed=1.0, fWarpScale=1.0, fZoomExponent=1.0, fShader=0.0, zoom=1.0, rot=0.0,
    cx=0.5, cy=0.5, dx=0.0, dy=0.0, warp=0.0, sx=1.0, sy=1.0, wave_r=1.0, wave_g=1.0, wave_b=1.0,
    wave_x=0.5, wave_y=0.5, ob_size=0.0, ob_r=0.0, ob_g=0.0, ob_b=0.0, ob_a=0.0, ib_size=0.0,
    ib_r=0.0, ib_g=0.0, ib_b=0.0, ib_a=0.0, nMotionVectorsX=0.0, nMotionVectorsY=0.0, mv_dx=0.0,
    mv_dy=0.0, mv_l=0.0, mv_r=0.0, mv_g=0.0, mv_b=0.0, mv_a=0.0,
)


def read_patch(path):
    root = ET.parse(path).getroot()
    p = dict(DEFAULTS)
    for e in root.iter("PARAM"):
        if e.get("id", "").startswith("life"):
            try:
                p[e.get("id")] = float(e.get("value"))
            except (TypeError, ValueError):
                pass
    rows = {}
    for life in root.iter("SWARM_LIFE"):
        for r in life.iter("ROW"):
            rows[int(r.get("y"))] = {k: int(r.get(k, "0"), 16) for k in ("c", "s", "sc", "ss")}
    return p, rows


def grid_of(rows, keys):
    for k in keys:
        g = [rows.get(y, {}).get(k, 0) for y in range(32)]
        if any(g):
            return g
    return None


def write_png(path, cells, sensors):
    """32 x 32 RGB: red = a live cell, green = a sensor. Row 0 at the top, bit x = column x."""
    raw = b""
    for y in range(32):
        raw += b"\0"
        for x in range(32):
            raw += bytes((255 if cells and cells[y] >> x & 1 else 0,
                          255 if sensors and sensors[y] >> x & 1 else 0, 0))

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 32, 32, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


def slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


WARP = """{decl}shader_body
{{
    // The grid lives in this picture, each cell a block of pixels: red alive, green age, blue flash.
    float2 cell = 1.0/32.0;
    float2 cid = floor(uv*32);
    float2 c = (cid + 0.5)*cell;
    float3 me = tex2D(sampler_pw_main, c).xyz;
    float n = 0;   // live neighbours; the wrapping sampler makes the grid a torus
    n += step(0.5, tex2D(sampler_pw_main, c + cell*float2(-1,-1)).x);
    n += step(0.5, tex2D(sampler_pw_main, c + cell*float2( 0,-1)).x);
    n += step(0.5, tex2D(sampler_pw_main, c + cell*float2( 1,-1)).x);
    n += step(0.5, tex2D(sampler_pw_main, c + cell*float2(-1, 0)).x);
    n += step(0.5, tex2D(sampler_pw_main, c + cell*float2( 1, 0)).x);
    n += step(0.5, tex2D(sampler_pw_main, c + cell*float2(-1, 1)).x);
    n += step(0.5, tex2D(sampler_pw_main, c + cell*float2( 0, 1)).x);
    n += step(0.5, tex2D(sampler_pw_main, c + cell*float2( 1, 1)).x);
    float alive = step(0.5, me.x);
    // The rule: bit n of q4 (birth) or q5 (survive).
    float next = lerp(fmod(floor(q4/exp2(n)), 2), fmod(floor(q5/exp2(n)), 2), alive);
    // A beat stirs a square patch (centre q8,q9, half-size q12) with random cells (density q6).
    float2 d = abs(cid - float2(q8, q9));
    d = min(d, 32 - d);
    float soup = step(1 - q6, tex2D(sampler_noise_lq, (cid + 0.5)/256.0 + q11).x);
    next = lerp(next, soup, q7*step(max(d.x, d.y), q12));
    float now = lerp(alive, next, q1);          // q1: a generation this frame
    float born = q1*now*(1 - alive);
    float age = lerp(me.y, born > 0.5 ? 1.0 : (now > 0.5 ? max(me.y*0.8, 0.22) : me.y*0.5), q1);
{sensor}
    // Flashes: a cell born on a sensor, and live cells the playhead plays (q3: a step, q13 shown).
    float played = q3*q13*step(abs(cid.x - q10), 0.5)*now;
    float flash = max(me.z*0.88, max(born*sensor, played));
    // The start (q2): the patch's picture, or a random soup.
{seed}
    ret = float3(now, age, flash);
}}"""

COMP = """{decl}shader_body
{{
    // A square grid in the middle of the screen.
    float2 sq = texsize.xy/min(texsize.x, texsize.y);
    float2 g = (uv - 0.5)*sq/0.92 + 0.5;
    float inside = step(0, g.x)*step(g.x, 1)*step(0, g.y)*step(g.y, 1);
    float2 cid = floor(g*32);
    float2 f = frac(g*32) - 0.5;
    float3 s = tex2D(sampler_pw_main, (cid + 0.5)/32).xyz;
    float edge = max(abs(f.x), abs(f.y));
    float box = smoothstep(0.45, 0.38, edge);
    float ring = box - smoothstep(0.33, 0.27, edge);
    float alive = step(0.5, s.x);
    // Brightness carries the story (newborn brightest, old dimmer, the dead fading out), so it
    // reads without colour.
    float lum = alive*(0.5 + 0.5*s.y) + (1 - alive)*s.y*0.28;
    float3 milk = float3(1.0, 0.97, 0.9);
    float3 tint = {tint};
    float glow = GetBlur1(saturate(g)).x*inside;
    float3 col = box*lum*lerp(milk, tint, 0.35*(1 - s.y)) + glow*0.35*tint;
    col += ring*0.07*inside;                                        // the empty grid, faintly
{sensor}
    col += box*s.z*float3(1, 1, 0.8);                               // flashes
    col += q13*inside*step(abs(cid.x - q10), 0.5)*0.12;            // the playhead
{movers}
    ret = col*inside;
}}"""

COMP_SENSOR = """    float sensor = tex2D(sampler_pc_life_{slug}, (cid + 0.5)/32).y;
    col += sensor*(ring*0.22 + box*0.03)*inside;                   // sensors: outlined squares"""

COMP_BEE = """    for (int i = 0; i < {count}; i++)
    {{
        float2 p = float2(i == 0 ? q16 : i == 1 ? q18 : i == 2 ? q20 : i == 3 ? q22 : i == 4 ? q24 : q26,
                          i == 0 ? q17 : i == 1 ? q19 : i == 2 ? q21 : i == 3 ? q23 : i == 4 ? q25 : q27);
        float2 b = g*32 - p;
        float body = smoothstep(1.0, 0.9, length(b/float2(0.85, 0.55)))*inside;
        float stripe = step(abs(abs(b.x) - 0.25), 0.09);
        col = lerp(col, float3(1, 0.82, 0.12)*(1 - stripe), body);     // a bee: yellow, two black stripes
    }}"""

COMP_WANDERER = """    for (int i = 0; i < {count}; i++)
    {{
        float2 p = float2(i == 0 ? q16 : i == 1 ? q18 : i == 2 ? q20 : i == 3 ? q22 : i == 4 ? q24 : q26,
                          i == 0 ? q17 : i == 1 ? q19 : i == 2 ? q21 : i == 3 ? q23 : i == 4 ? q25 : q27);
        float r = length(g*32 - p);
        col += (smoothstep(0.55, 0.35, r) + 0.25*smoothstep(1.6, 0.3, r))*inside;   // a wanderer: a bright dot
    }}"""


def movers_code(kind, count):
    """Per-frame random walks for up to six movers, in grid units (0..32), wrapping. Bees jitter
    and turn often; wanderers glide."""
    if not kind:
        return []
    speed, turn = (5.0, 2.5) if kind == "bee" else (3.0, 0.8)
    lines = ["dt = min(time - lastt, 0.1);", "lastt = time;"]
    for i in range(count):
        q = 16 + 2 * i
        lines += [f"h{i} = h{i} + (rand(1000)/1000 - 0.5)*{turn}*dt*30;",
                  f"v{i} = {speed}*(0.6 + bass_att*0.3);",
                  f"px{i} = px{i} + cos(h{i})*v{i}*dt;", f"py{i} = py{i} + sin(h{i})*v{i}*dt;",
                  f"px{i} = px{i} - 32*below(32, px{i}) + 32*below(px{i}, 0);",
                  f"py{i} = py{i} - 32*below(32, py{i}) + 32*below(py{i}, 0);",
                  f"q{q} = px{i};", f"q{q + 1} = py{i};"]
    return lines


def tint_of(name):
    # A colour per patch, only an accent: brightness carries the picture.
    h = sum(ord(ch) * (i + 1) for i, ch in enumerate(name)) % 360 / 360.0
    return f"(0.55 + 0.45*cos(6.2831853*({h:.3f} + float3(0, 0.33, 0.67))))"


def make(path):
    name = os.path.splitext(os.path.basename(path))[0]
    folder = os.path.basename(os.path.dirname(path))
    if folder not in ("User", "Factory 2026", os.path.basename(SWARM)):
        name = f"{name} ({folder})"   # "felix" is in User and in User\Pixel Art
    p, rows = read_patch(path)
    if p["lifeEnable"] < 0.5 or name not in KEEP:
        return None
    rule = RULES[min(max(int(p["lifeRule"]), 0), len(RULES) - 1)]
    birth, survive = sum(1 << n for n in rule[1]), sum(1 << n for n in rule[2])
    if p["lifeSync"] >= 0.5:
        step_len = DIV_QUARTERS[min(max(int(p["lifeDiv"]), 0), len(DIV_QUARTERS) - 1)] * 0.5  # 120 BPM
    else:
        step_len = 1.0 / max(p["lifeRate"], 0.01)
    evolve = max(int(p["lifeEvolve"]), 1)
    while step_len * evolve < 0.06:   # faster than the screen can show: fewer, whole generations
        evolve *= 2
    mode = int(p["lifeMode"])
    playhead = 1 if mode in (1, 3) else 0
    cells = grid_of(rows, ("sc", "c"))
    sensors = grid_of(rows, ("ss", "s"))
    density = min(max(p["lifeDensity"] / 100.0, 0.05), 0.6)
    keep = p["lifeKeep"] / 100.0
    kind = "bee" if p["lifeBees"] >= 0.5 else ("wanderer" if p["lifeWander"] >= 0.5 else None)
    count = min(int(p["lifeBeeCount"] if kind == "bee" else p["lifeWandCount"]), MOVERS) if kind else 0

    s = slug(name)
    has_tex = bool(cells or sensors)
    decl = f"sampler sampler_pc_life_{s};\n" if has_tex else ""
    if has_tex:
        write_png(os.path.join(TEXTURES, f"life_{s}.png"), cells, sensors)
        sensor_warp = f"    float sensor = step(0.5, tex2D(sampler_pc_life_{s}, c).y);"
    else:
        sensor_warp = "    float sensor = 0;"
    if cells:
        seed = f"    float start = step(0.5, tex2D(sampler_pc_life_{s}, c).x);"
    else:
        seed = "    float start = step(1 - q6, tex2D(sampler_noise_lq, (cid + 0.5)/256.0 + q11).x);"
    seed += "\n    now = lerp(now, start, q2);\n    age = lerp(age, start, q2);\n    flash = flash*(1 - q2);"

    warp = WARP.format(decl=decl, sensor=sensor_warp, seed=seed)
    movers = ""
    if kind == "bee":
        movers = COMP_BEE.format(count=count)
    elif kind == "wanderer":
        movers = COMP_WANDERER.format(count=count)
    comp = COMP.format(decl=decl, tint=tint_of(name), sensor=COMP_SENSOR.format(slug=s) if sensors else "",
                       movers=movers)

    init = ["t0 = time;", "laststep = -1;", "pending = 0;", "lasthit = 0;", "lastt = time;",
            "q8 = 16;", "q9 = 16;"]
    init += [f"px{i} = rand(3200)/100;" for i in range(count)] + [f"py{i} = rand(3200)/100;" for i in range(count)]
    init += [f"h{i} = rand(628)/100;" for i in range(count)]
    frame = [
        "el = time - t0;",
        f"st = int(el/{step_len:.6f});",
        "q3 = above(st, laststep);",                         # a new step
        "laststep = st;",
        f"q1 = q3*equal(st % {evolve}, 0);",                 # a generation
        "q10 = st % 32;",                                     # the playhead column
        f"q13 = {playhead};",
        "q2 = below(el, 2.8);",                               # the start, held through the blend in (2.5 s at most)
        f"q4 = {birth};", f"q5 = {survive};",
        # A beat: bass well over its average, at most four a second. It stirs on the next generation.
        "beat = above(bass, 1.3)*above(bass, bass_att*1.15)*above(time - lasthit, 0.25);",
        "lasthit = if(beat, time, lasthit);",
        "pending = max(pending, beat);",
        "q7 = q1*pending*(1 - q2);",
        "pending = pending*(1 - q1);",
        "q8 = if(beat, rand(32), q8);", "q9 = if(beat, rand(32), q9);",
        f"q12 = {1 + round(keep * 4)};",                      # the patch: 3 x 3 up to 11 x 11 cells
        f"q6 = {max(density, rule[3]) if not cells else rule[3]:.3f};",
        "q11 = if(q2, q11, if(beat, rand(1000)/1000, q11));",
        "q11 = if(below(el, 0.05), rand(1000)/1000, q11);",
    ] + movers_code(kind, count)

    vals = dict(BASE)
    out = ["MILKDROP_PRESET_VERSION=201", "PSVERSION=3", "PSVERSION_WARP=3", "PSVERSION_COMP=3", "[preset00]"]
    out += [f"{k}={v:.5f}" if isinstance(v, float) else f"{k}={v}" for k, v in vals.items()]
    out += [f"per_frame_init_{k + 1}={line}" for k, line in enumerate(init)]
    out += [f"per_frame_{k + 1}={line}" for k, line in enumerate(frame)]
    out += [f"warp_{k + 1}=`{line}" for k, line in enumerate(warp.split("\n"))]
    out += [f"comp_{k + 1}=`{line}" for k, line in enumerate(comp.split("\n"))]
    target = os.path.join(OUT, f"Life - {name}.milk")
    with open(target, "w", newline="\r\n") as f:
        f.write("\n".join(out) + "\n")
    return (name, rule[0], ["Grid Off", "Scan", "Sensors", "Plot"][mode], "picture" if cells else "soup",
            kind or "-", round(step_len * evolve, 3))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for old in glob.glob(os.path.join(OUT, "*.milk")) + glob.glob(os.path.join(TEXTURES, "life_*.png")):
        os.remove(old)
    made = [m for m in (make(f) for f in sorted(glob.glob(os.path.join(SWARM, "**", "*.swarm"), recursive=True))) if m]
    for m in made:
        print("%-45s %-14s %-8s %-7s %-8s %5.2fs/gen" % m)
    print(len(made), "presets in", OUT)
