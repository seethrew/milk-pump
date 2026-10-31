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

## Milk Pump 0.3.21 beta

**Music visuals that move with your sound, inside your DAW or on your desktop.**

### What is MilkDrop?

MilkDrop is a music visualiser, first made by Ryan Geiss for Winamp in 2001. It listens to the music, its bass, mids, treble and beats, and turns it into flowing, morphing, psychedelic visuals in real time. Each look is a **preset**: a small recipe of maths and shader code, and over twenty years people have written tens of thousands of them. It's still a favourite with VJs and anyone who wants something alive on screen while music plays.

### What is Milk Pump?

Milk Pump is a port of the **real MilkDrop 2 engine** (via [BeatDrop](https://github.com/OfficialIncubo/BeatDrop-Music-Visualizer), which brought it to 64-bit) into two things:

- **A VST3 plugin.** Put it on any track in Ableton Live or another VST3 host. The audio passes through untouched, and the plugin's window *is* the visuals, reacting to exactly that track.
- **A standalone app.** Its own window, reacting to whatever your PC is playing: YouTube, Spotify, games, anything through Windows' sound.

Because it's the original engine, not a remake, classic presets look and move the way they always have.

### Features

- **Visuals in the plugin window.** Open and close it like any plugin, drag to resize, double-click for **full screen on a second monitor or projector**.
- **Speed control, 1/32 to 2x.** Slow the motion right down for ambient or slow music while beats still land instantly. Automatable in your DAW.
- **HQ switch.** 30 fps to go easy on the computer, or 60 fps for smoothness.
- **Your set remembers its preset**, its lock, window size, Speed and HQ. The app remembers too, and opens on the Milk Pump banner.
- **About 640 presets included** (BeatDrop's 574 plus 65 of our own), plus an optional pack of about 11,000 more.
- **Game of Life presets.** Conway's Game of Life and its cousins as pixel art, seeded and stirred by the music.
- **Preset browser, random mash-ups, auto-switching**, screenshots, webcam into the visuals, and **Spout output** to send the visuals to VJ or streaming software.
- **Crash-proofed.** If DirectX's old shader compiler falls over on a preset, Milk Pump catches it and carries on.
- **Old-school README** with every key: Start menu > Milk Pump README.

### Why Windows only?

MilkDrop was written for **DirectX 9**, Windows' graphics system. Milk Pump keeps that original engine so presets stay true to how their authors made them, and that ties it to Windows. It may run on Linux through Wine (the app) or yabridge (the plugin), but that's untested. If you try it, open an issue and say how it went. For a native Mac or Linux MilkDrop, see [projectM](https://github.com/projectM-visualizer/projectm).

### Download

| File | What |
|---|---|
| **Milk.Pump.0.3.21.msi** (9 MB) | The installer. Tick the **VST3 plugin**, the **standalone app**, or both. Includes about 640 presets and the user guide. |
| **Milk.Pump.Presets.msi** (1.2 GB, optional) | BeatDrop's full pack: about 11,000 presets and 1.2 GB of textures. |

**Needs:** Windows 10 or 11, 64-bit, and a graphics card with DirectX 9 support (practically any graphics card or built-in graphics from the last decade or more).

**Installing:** run the installer and tick what you want. The plugin goes into the standard VST3 folder (`C:\Program Files\Common Files\VST3`), so make sure your DAW scans it, then rescan. To remove: Settings > Apps > Installed apps.

> **Windows may warn** "Windows protected your PC" because the installer isn't signed: click **More info**, then **Run anyway**.

### First steps

Click the visuals, then: **F1** help · **Space** next preset · **L** preset browser · **[ ]** speed · **F3** HQ · **double-click** full screen.

### Known limits (it's a beta)

- One visualiser per DAW project: a second Milk Pump in the same set passes audio through and shows a note.
- The **app** listens to Windows' playback device, so it may not hear a DAW running on an ASIO driver. Inside the DAW, use the **plugin**.
- Video files inside presets are off for now (webcam and Spout still work).

### Licence

Free software, never to be sold: the engine and app are BSD 3-Clause, the plugin (built with JUCE) is GNU AGPL v3. Built on MilkDrop 2 (Ryan Geiss / Nullsoft), BeatDrop (OfficialIncubo and contributors) and MilkDrop3 (milkdrop2077). Some bundled presets are CC BY-NC-SA 3.0. See `LICENSE.md` and `THIRD-PARTY-NOTICES.md`.

*Made (ported) by seethrew.*
