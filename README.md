# Milk Pump

MilkDrop music visuals for Windows: a **VST3 plugin** for Ableton Live and other DAWs, and a
**standalone app** that reacts to whatever the PC is playing. Beta, by seethrew.

Milk Pump runs the real MilkDrop 2 engine, through [BeatDrop](https://github.com/OfficialIncubo/BeatDrop-Music-Visualizer)'s
64-bit version of it, so classic MilkDrop presets look and move as they always have. It adds:

- the visuals as the plugin's own window, resizable, full screen on a second screen or projector;
- **Speed** (1/32 to 2x) and **HQ** (30 / 60 fps) controls, automatable in the DAW;
- the set remembers its preset; the app opens on the Milk Pump banner and its last preset;
- Game of Life presets: real Life movement in a pixel-art style, seeded by the music;
- a guard around the old DirectX shader compiler, so a preset can never crash the host.

**Just want to use it?** Download the installers from the [Releases](../../releases) page:
`Milk Pump <version>.msi` (pick the plugin, the app or both) and, optionally,
`Milk Pump Presets.msi` (BeatDrop's 11,000-preset pack). The user guide is
[Docs/Milk Pump README.txt](Docs/Milk%20Pump%20README.txt).

## Building it

Windows 10/11 x64, with:

- Visual Studio 2022, workload "Desktop development with C++" (MSVC v143, Windows 10/11 SDK)
- Git
- for the installers: the .NET 8 SDK

Then, in PowerShell in this folder:

```
powershell -ExecutionPolicy Bypass -File setup.ps1 -WithBeatDrop -WithInstaller
powershell -ExecutionPolicy Bypass -File build.ps1
powershell -ExecutionPolicy Bypass -File install-data.ps1
```

1. `setup.ps1` fetches the tools into `Tools\` (JUCE 8, vcpkg, Microsoft's D3DX9 headers and
   DLLs) and, with `-WithBeatDrop`, BeatDrop's repository into `Reference\` for its presets and
   textures (1.4 GB). Nothing is installed system-wide.
2. `build.ps1` builds, Release by default (`-Config Debug` or `RelWithDebInfo` otherwise):
   - `build\Source\Plugin\MDVST_Plugin_artefacts\Release\VST3\Milk Pump.vst3`
   - `build\App\Release\Milk Pump.exe`
   - `build\EngineTest\Release\EngineTest.exe` and `build\HostTest\Release\HostTest.exe` (tests)
3. `install-data.ps1` fills the data folder, `Documents\Milk Pump`: presets, textures, fonts,
   settings (`-Pack Light` for the 574-preset set instead of the full pack).

Optional: `Installer\build-installer.ps1` builds the two `.msi` installers; `install.ps1` copies
the plugin into `VST3\` here, for a DAW pointed at this folder while developing.

**Testing:** `HostTest.exe` loads the built plugin as a DAW would and prints PASS/FAIL lines
(audio null tests, the controls and saved state, the window, full screen, deleting with the
window open). `Tools\preset-shot.ps1` screenshots a preset; `Tools\preset-flick.ps1` hammers
preset changes.

## How it's put together

| Folder | What |
|---|---|
| `Source/Engine` | BeatDrop's engine (MilkDrop 2), copied from BeatDrop at commit `44b7ee0f`. Every change from upstream is marked `MDVST:` (`grep -rn "MDVST:"` lists them). Plus our glue: `mdvst_engine.h`, `mdvst_paths.*`, `mdvst_audio.cpp`, `mdvst_controls.h`. |
| `Source/Plugin` | The JUCE VST3: passes audio through untouched, feeds the engine, hosts its window. |
| `Source/App` | The standalone app: the engine plus WASAPI loopback of the PC's sound. |
| `Source/EngineTest`, `Source/HostTest` | Test programs. |
| `Presets` | Our presets and the Python scripts that generate them; the opening screen; the logo. |
| `Docs` | The user guide. |
| `Installer` | WiX 5 sources for the installers. |
| `Tools` | Scripts: the logo, the icon, preset screenshots, stress tests. |

The engine keeps one global instance, so there is one visualiser per process: a second copy of
the plugin in the same DAW passes audio through and shows a note.

## Licence

Free software, never to be sold. The engine and the app are **BSD 3-Clause**; the plugin, built
with JUCE, is **GNU AGPL v3**. See [LICENSE.md](LICENSE.md) and
[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

Milk Pump stands on the shoulders of MilkDrop 2 (Ryan Geiss / Nullsoft), BeatDrop
(OfficialIncubo and contributors) and MilkDrop3 (milkdrop2077). It is not made or endorsed by
them.
