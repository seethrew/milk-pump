**Milk Pump 0.3.22 beta**: a small update to [0.3.21](https://github.com/seethrew/milk-pump/releases/tag/v0.3.21-beta).

### New

- **Microphone input in the app.** Press **Ctrl+D** (or use the right-click menu) and the app listens to
  Windows' default recording device instead of what the PC plays: a headset or laptop mic, or an
  audio interface input for live instruments or the room. Press it again to go back. To use a
  different mic, set it as default in Settings > System > Sound > Input; Milk Pump follows it.
- **Shader compiler crash note.** When DirectX's old shader compiler crashes on a preset, Milk Pump
  already compiled it with the newer one instead; now it says so on screen.

### Fixed

- Ctrl+D said "Switched to Microphone" but nothing changed. In the **plugin** it now says the plugin
  listens to its track (it always has: a mic goes into your DAW like any other input).
- One more place the old shader compiler runs (recompiling a stale cached shader) is now crash-proofed too.

Thanks to **OfficialIncubo** (BeatDrop's author) for reporting both, in issue #1.

### Download

| File | What |
|---|---|
| **Milk.Pump.0.3.22.msi** (9 MB) | The installer: replaces 0.3.21. Tick the plugin, the app, or both. |
| Milk Pump Presets | Unchanged: get it from [0.3.21](https://github.com/seethrew/milk-pump/releases/tag/v0.3.21-beta) if you don't have it. |

> **Windows may warn** "Windows protected your PC" because the installer isn't signed: click
> **More info**, then **Run anyway**.
