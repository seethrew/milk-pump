"""PIXEL LIFE: Conway's Game of Life and its cousins as MilkDrop presets, looking and moving like the
real thing, drawn as pixel art (Daxy, 2026-10-30: the SwarmSynth Life presets' movement "doesn't
really translate"; these are "like a real game of life but in a pixel art style", in a different
shader layer). Run:
    python make_pixel_life.py   -> writes Pixel Life - <name>.milk beside it
(install-data.ps1 puts them in the data folder's SwarmSynth preset folder, Daxy 2026-10-30)

Two layers, each in its own shader:
  - WARP: the simulation. The feedback picture IS the grid: square cells of whole screen pixels,
    60-108 rows, the columns to fit, wrapping at the edges. Red = alive, green = age (1 when born,
    fading after death). A generation at a steady 10-15 a second on engine time (Speed slows it),
    one generation per step, so gliders glide and blinkers blink as they should.
  - COMP: the pixel art. A four-step palette per preset, ordered dark to light (the brightness
    alone tells newborn, older and fading cells apart, colour is extra), a bevel on each live
    cell, ordered dither for the fading trail, and a quiet background layer underneath.
The music feeds the colony gently, the way Life visualisers do: the spectrum seeds cells along a
SOUND LINE or up from a SPECTRUM FLOOR, or beats fire real GLIDERS. A strong beat can also drop a
small random patch (SOUP). The rules are the published B/S ones.
Every preset is ours (Daxy & Claude, 2026).
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

RULES = {"Conway": ([3], [2, 3]), "HighLife": ([3, 6], [2, 3]), "Day & Night": ([3, 6, 7, 8], [3, 4, 6, 7, 8]),
         "Seeds": ([2], []), "Maze": ([3], [1, 2, 3, 4, 5])}

# Four colours each, darkest (background) to lightest (a newborn cell).
PALETTES = {
    "Game Boy": [(15, 56, 15), (48, 98, 48), (139, 172, 15), (224, 248, 208)],
    "Amber": [(18, 9, 0), (95, 45, 0), (205, 120, 10), (255, 214, 120)],
    "Night": [(10, 8, 30), (96, 36, 112), (255, 110, 160), (255, 241, 232)],
    "CGA": [(0, 0, 0), (170, 0, 170), (85, 255, 255), (255, 255, 255)],
    "1-bit": [(0, 0, 0), (255, 255, 255), (255, 255, 255), (255, 255, 255)],
    "Fire": [(0, 0, 0), (130, 12, 0), (235, 95, 0), (255, 235, 130)],
}

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

WARP = """shader_body
{{
    // The grid: square cells of whole pixels, {rows} rows, as many columns as fit; it wraps.
    float cs = max(floor(texsize.y/{rows}), 1);
    float2 G = floor(texsize.xy/cs);
    float2 cid = floor(uv*texsize.xy/cs);
    float2 k = cs*texsize.zw;                       // one cell, in uv
    float2 c = (cid + 0.5)*k;
    float3 me = tex2D(sampler_pw_main, c).xyz;
    float n = 0;
    for (int j = -1; j <= 1; j++)
        for (int i = -1; i <= 1; i++)
            if (i != 0 || j != 0)
                n += step(0.5, tex2D(sampler_pw_main, (fmod(cid + float2(i, j) + G, G) + 0.5)*k).x);
    float alive = step(0.5, me.x);
    // The rule: bit n of q4 (birth) or q5 (survive).
    float next = lerp(fmod(floor(q4/exp2(n)), 2), fmod(floor(q5/exp2(n)), 2), alive);
    float rnd = tex2D(sampler_noise_lq, (cid + 0.5)/256.0 + float2(q11, q12)).x;
{seeding}
    float now = lerp(alive, next, q1);               // q1: a generation this frame
    float born = q1*now*(1 - alive);
    float age = lerp(me.y, born > 0.5 ? 1.0 : (now > 0.5 ? max(me.y*0.9, 0.55) : me.y*0.72), q1);
    // The start. While the previous preset blends out (q2), its picture would leak into the grid
    // as random cells, so the grid is held empty; then the random field, once (q3).
    float start = step(1 - {density}, rnd);
    now = lerp(now, start, q3);
    age = lerp(age, start, q3);
    now *= 1 - q2;
    age *= 1 - q2;
    float outside = 1 - step(cid.x, G.x - 1)*step(cid.y, G.y - 1);
    ret = float3(now, age, 0)*(1 - outside);
}}"""

# How the music adds cells, on a generation (q1). Gliders and soup are stamped at (q8, q9).
SEED_LINE = """    // SOUND LINE: across the middle, each column's frequency band (low on the left) seeds cells.
    float band = get_fft(0.01 + 0.45*cid.x/G.x)*q15;
    next = max(next, step(abs(cid.y - floor(G.y*0.5)), 0.5)*step(rnd, band - 0.15));"""
SEED_FLOOR = """    // SPECTRUM FLOOR: bars rise from the bottom; their tops seed cells.
    float band = get_fft(0.01 + 0.45*cid.x/G.x)*q15;
    float h = floor(band*G.y*0.18);
    next = max(next, step(G.y - 1 - h, cid.y)*step(cid.y, G.y - h + 0.5)*step(rnd, 0.5)*step(1, h));"""
SEED_GLIDER = """    // GLIDERS: a beat (q7) fires one from (q8, q9), heading (q13, q14) = (+-1, +-1).
    float2 r = fmod(cid - fmod(float2(q8, q9), G) + G, G);
    float2 o = float2(q13 > 0 ? r.x : 2 - r.x, q14 > 0 ? r.y : 2 - r.y);
    float glider = (o.x == 1 && o.y == 0) || (o.x == 2 && o.y == 1) || (o.y == 2 && o.x <= 2) ? 1 : 0;
    float box = step(r.x, 3)*step(r.y, 3);
    next = lerp(next, glider, q7*box);"""
SEED_SOUP = """    // SOUP: a beat (q10) drops a small random patch at (q8, q9).
    float2 d = abs(cid - fmod(float2(q8, q9), G));
    d = min(d, G - d);
    next = lerp(next, step(0.6, rnd), q10*step(max(d.x, d.y), 2.5));"""

COMP = """shader_body
{{
    float cs = max(floor(texsize.y/{rows}), 1);
    float2 G = floor(texsize.xy/cs);
    float2 px = floor(uv*texsize.xy);
    float2 cid = floor(px/cs);
    float2 sp = floor((px - cid*cs)/cs*5);           // the sprite pixel inside the cell, 0..4
    float inside = step(cid.x, G.x - 1)*step(cid.y, G.y - 1);
    float3 s = tex2D(sampler_pw_main, (cid + 0.5)*cs*texsize.zw).xyz;
    float alive = step(0.5, s.x);
    float3 c0 = {c0}, c1 = {c1}, c2 = {c2}, c3 = {c3};
    // 4 x 4 Bayer threshold, per sprite pixel: the dither every layer uses.
    float2 bp = fmod(cid*5 + sp, 4);
    float b2 = fmod(bp.x, 2)*2 + fmod(bp.y, 2);
    float2 bq = floor(bp/2);
    float bayer = (b2*4 + fmod(bq.x, 2)*2 + fmod(bq.y, 2) + 0.5)/16;

    // BACKGROUND LAYER
{background}

    // GLOW LAYER: the colony's light, in whole cells and dithered steps, not a smooth blur.
    float glow = GetBlur2((cid + 0.5)*cs*texsize.zw).x*{glow};
    col = lerp(col, c1, step(bayer, glow*1.6));

    // TRAIL LAYER: cells that just died fade out through the dither.
    float trail = (1 - alive)*step(bayer, s.y*1.2 - 0.15);
    col = lerp(col, {trail_colour}, trail);

    // LIFE LAYER: each live cell a 5 x 5 sprite, rounded, lit from the top left: a highlight, a
    // body (the lightest colour while newborn), a shadow edge.
    float corner = (sp.x == 0 || sp.x == 4) && (sp.y == 0 || sp.y == 4) ? 1 : 0;
    float shade = (sp.x == 4 || sp.y == 4) ? 1 : 0;
    float light = (sp.x == 1 && sp.y == 1) ? 1 : 0;
    float3 body = s.y > 0.85 ? c3 : c2;
    float3 sprite = light > 0.5 ? c3 : (shade > 0.5 ? c1 : body);
    col = lerp(col, sprite, alive*(1 - corner));
{crt}
    ret = col*inside;
}}"""

BG_SKY = """    // A sky: the two darkest colours in four dithered bands, top to bottom; the bass lifts it.
    float t = saturate(cid.y/G.y*1.1 - 0.1 - bass_att*0.08);
    float3 col = lerp(c1, c0, step(bayer, t));"""
BG_STARS = """    // Stars: a few sprite pixels, drifting left, twinkling.
    float3 col = c0;
    float2 sc = floor((px + float2(time*12, 0))/cs*5/3);
    float star = tex2D(sampler_noise_lq, sc/256.0).x;
    float tw = 0.5 + 0.5*sin(time*3 + star*40);
    col = lerp(col, lerp(c1, c3, step(0.996, star)), step(0.985, star)*step(0.3, tw));"""
BG_GRID = """    // Graph paper: the darkest colour, a dot of the next at each cell's corner.
    float3 col = lerp(c0, c1, (sp.x == 0 && sp.y == 0) ? 0.5 : 0);"""

CRT = """    // CRT: every other screen row a little darker.
    col *= 1 - 0.18*fmod(px.y, 2);"""


def rgb(t):
    # Never an exact 0.000: a palette colour with one crashed the engine every time (Day and Night,
    # Seeds, 2026-10-30; the legacy shader compiler, it seems). 1/255 looks the same.
    return "float3(%.3f, %.3f, %.3f)" % tuple(max(v, 1) / 255 for v in t)


def write(name, rule, palette, rows, rate, seeding, density=0.3, gain=2.0, soup=False,
          background="sky", glow=0.8, crt=False):
    birth, survive = RULES[rule]
    pal = PALETTES[palette]
    seeds = [{"line": SEED_LINE, "floor": SEED_FLOOR, "glider": SEED_GLIDER}[s] for s in seeding]
    if soup:
        seeds.append(SEED_SOUP)
    warp = WARP.format(rows=rows, density=density, seeding="\n".join(seeds))
    comp = COMP.format(rows=rows, c0=rgb(pal[0]), c1=rgb(pal[1]), c2=rgb(pal[2]), c3=rgb(pal[3]),
                       trail_colour=rgb(pal[1]) if palette != "1-bit" else "c3", glow=glow,
                       background={"sky": BG_SKY, "stars": BG_STARS, "grid": BG_GRID}[background],
                       crt=CRT if crt else "")
    gliders = "glider" in seeding
    init = ["t0 = time;", "seeded = 0;", "laststep = -1;", "pending = 0;", "lasthit = 0;", "q8 = 0;", "q9 = 0;",
            "q13 = 1;", "q14 = 1;", "nextglider = 0.8;"]
    frame = [
        "el = time - t0;",
        f"st = int(el*{rate});",
        "q1 = above(st, laststep);",                 # a generation: steady, one per step
        "laststep = st;",
        "q2 = below(el, 2.8);",                      # the blend in (2.5 s at most): grid held empty
        "q3 = (1 - q2)*(1 - seeded);",               # then the random field, once
        "seeded = max(seeded, q3);",
        f"q4 = {sum(1 << b for b in birth)};", f"q5 = {sum(1 << b for b in survive)};",
        "q11 = if(q1, rand(1000)/1000, q11);", "q12 = if(q1, rand(1000)/1000, q12);",
        f"q15 = {gain};",
        # A beat: bass well over its average, at most four a second, used on the next generation.
        "beat = above(bass, 1.25)*above(bass, bass_att*1.12)*above(time - lasthit, 0.25);",
        "lasthit = if(beat, time, lasthit);",
        # Gliders also launch by themselves every few seconds, so a quiet passage still has some.
        f"auto = {1 if gliders else 0}*above(el, nextglider);",
        "nextglider = if(auto + beat, el + 1 + rand(150)/100, nextglider);",
        "pending = max(pending, max(beat, auto));",
        "fire = q1*pending*(1 - q2);",
        "pending = pending*(1 - q1*(1 - q2));",
        "q8 = if(fire, rand(400), q8);", "q9 = if(fire, rand(400), q9);",
        "q13 = if(fire, if(rand(2), 1, -1), q13);", "q14 = if(fire, if(rand(2), 1, -1), q14);",
        f"q7 = fire*{1 if gliders else 0};",
        f"q10 = fire*{1 if soup else 0};",
    ]
    out = ["MILKDROP_PRESET_VERSION=201", "PSVERSION=3", "PSVERSION_WARP=3", "PSVERSION_COMP=3", "[preset00]"]
    out += [f"{k}={v:.5f}" if isinstance(v, float) else f"{k}={v}" for k, v in BASE.items()]
    out += [f"per_frame_init_{i + 1}={line}" for i, line in enumerate(init)]
    out += [f"per_frame_{i + 1}={line}" for i, line in enumerate(frame)]
    out += [f"warp_{i + 1}=`{line}" for i, line in enumerate(warp.split("\n"))]
    out += [f"comp_{i + 1}=`{line}" for i, line in enumerate(comp.split("\n"))]
    with open(os.path.join(HERE, f"Pixel Life - {name}.milk"), "w", newline="\r\n") as f:
        f.write("\n".join(out) + "\n")
    print(f"Pixel Life - {name}: {rule}, {palette}, {rows} rows, {rate} gen/s, {'+'.join(seeding)}{'+soup' if soup else ''}")


# Glider positions are rand(400): fmod against the grid in the shader puts them anywhere on it.
# Rows: fewer = chunkier sprites. 1080p at 54 rows = 20-pixel cells, 4 screen pixels a sprite pixel.
write("Game Boy", "Conway", "Game Boy", rows=54, rate=12, seeding=["line"], soup=True, background="sky", crt=True)
write("Gliders", "Conway", "Amber", rows=45, rate=12, seeding=["glider"], density=0.2, background="grid", crt=True)
write("HighLife", "HighLife", "Night", rows=64, rate=14, seeding=["floor"], density=0.3, background="stars")
write("Day and Night", "Day & Night", "CGA", rows=48, rate=10, seeding=["line"], density=0.5, soup=True, background="grid", glow=0.5)
write("1-bit", "Conway", "1-bit", rows=80, rate=15, seeding=["line", "glider"], density=0.25, background="stars", glow=0.4)
write("Seeds", "Seeds", "Fire", rows=54, rate=10, seeding=["glider"], density=0.03, soup=True, background="sky", glow=0.3)
write("Maze", "Maze", "Game Boy", rows=60, rate=12, seeding=["floor"], density=0.08, background="sky", crt=True)
