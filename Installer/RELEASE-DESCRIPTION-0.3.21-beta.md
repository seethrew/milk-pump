```text
 $"$$,  ,$$$$  ,"$$$, ,""$$,       ,"$$$,  ,$,
 $$$$$,,$$$$$  $$$$$$ $$$$$$       $$$$$$$$$$"                  $$,,,,,,,,
 $$$$$$$$$$$$  $$$$$$ $$$$$$       $$$$$$$$$"                   $$"""" $"""$,
 $$$$"$$"$$$$  $$$$$$ $$$$$$       $$$$$$$$$$,                 ,$$,,,,,$,   "$
 $$$$    $$$$  $$$$$$ $$$$$$$$$$,  $$$$$$"$$$$                ,$$$$$$$$$,    "$
 """"    """"  """""" """""""""""  """"""  """               ,$$$$$$$$$$$$    $,
                                                             $$$$$$$$$$$$$    $$
 ,"$$$$$$$$,  ,"$$$, ,$$$  $""$$   $$$$$ ,""$$$$$$$,     ,,,,,,,,,,,,,$$$$    $$
 $$$$$$ $$$$  $$$$$$ $$$$  $$$$$$ $$$$$$ $$$$$$ $$$$$   $$"""$$$$$$$$$$$$$    "
 $$$$$$ $$$$  $$$$$$ $$$$  $$$$$$$$$$$$$ $$$$$$ $$$$$    $   $$$$$$$$$$$$$
 $$$$$$$$$$"  $$$$$$ $$$$  $$$$ $$$ $$$$ $$$$$$$$$$"     $   $$$$$$$$$$$$$
 $$$$$$       $$$$$$$$$$$  $$$$     $$$$ $$$$$$          ,   ,,,,,,,,,$$$"
 """"""        """"""""""  """"     """" """"""        ,,,,, """""""""

   .:: milkdrop music visuals  ::  vst3 plugin + the app  ::  beta ::.
  ...(-_-)
   ▗ ▌ ▌▗      ...(-_-)             seethrew..(-_-)..
                ..▗ ▌  ▌▗
```

**Milk Pump 0.3.21 beta**: MilkDrop music visuals for Windows, as a VST3 plugin and a standalone app.

Milk Pump runs the real MilkDrop 2 engine (through BeatDrop's 64-bit version), so classic MilkDrop
presets look and move as they always have, now inside your DAW or reacting to whatever your PC plays.

### Download

| File | What |
|---|---|
| **Milk Pump 0.3.21.msi** (9 MB) | The installer. Tick the **VST3 plugin**, the **standalone app**, or both. Comes with our presets, BeatDrop's 574-preset light set, and the user guide. |
| **Milk Pump Presets.msi** (1.2 GB, optional) | BeatDrop's full pack: about 11,000 presets and 1.2 GB of textures. |

Windows 10 or 11, 64-bit. The plugin goes into the standard VST3 folder
(`C:\Program Files\Common Files\VST3`); make sure your DAW scans it, then rescan.

> **Windows may warn** "Windows protected your PC" because the installer isn't signed: click
> **More info**, then **Run anyway**.

### What's in it

- **The visuals are the plugin's window**: open it like any plugin, resize it, double-click for
  full screen on a second monitor or projector.
- **Speed** (1/32 to 2x) to calm presets down for slower music, and **HQ** (30 / 60 fps). Both are
  automatable, and on keys (`[` `]`, `F3`).
- **Your set remembers its preset.** The app opens on the Milk Pump banner, then your last preset.
- **Game of Life presets**: real Life, as pixel art, seeded by the music. Plus presets made from
  SwarmSynth Revived patches.
- **Crash-proofed preset loading**: if the old DirectX shader compiler falls over on a preset,
  Milk Pump catches it and carries on.
- An old-school README with all the keys: Start menu > **Milk Pump README**.

### Known limits (it's a beta)

- One visualiser per DAW project: a second Milk Pump in the same set passes audio through and
  shows a note.
- The **app** listens to Windows' playback device, so it may not hear a DAW running on an ASIO
  driver. Inside the DAW, use the **plugin**.
- Video files inside presets are switched off for now (webcam and Spout still work).
- Windows only.

### Licence

Free software, never to be sold: the engine and the app are BSD 3-Clause, the plugin (built with
JUCE) is GNU AGPL v3. Built on MilkDrop 2 (Ryan Geiss / Nullsoft), BeatDrop (OfficialIncubo and
contributors) and MilkDrop3 (milkdrop2077); some bundled presets are CC BY-NC-SA 3.0. See
`LICENSE.md` and `THIRD-PARTY-NOTICES.md`.
