**Milk Pump 0.3.24 beta**: smoother in a DAW. Tested in Ableton Live and Bitwig Studio.

### New

- **Choose what a new Milk Pump opens on.** Right-click the visuals: **Open on the Milk Pump banner**
  (the default) or **Open on this preset instead**. Shared by the plugin and the app.
- **The opening banner (or your start preset) holds for 8 seconds.** In a DAW with music playing,
  hard cuts used to swap it out on the first loud beat.
- **Full screen hides the plugin's own window.** It used to stay behind the full-screen visuals and
  show through transparency mode. It comes back when you leave full screen.
- **Spout output is now called "Milk Pump"** in OBS and other video software (it was "BeatDrop").

### Fixed (in the plugin; the app keeps all of these)

- **Z, X, C and V** sent Windows media keys (previous, play/pause, stop, next), so inside a DAW
  they could pause Spotify or YouTube in the background. In the plugin they now just say so.
- **Ctrl+W** (hide to the tray) left an empty plugin window. In a DAW, close the window instead.
- The right-click menu no longer offers window options that don't apply inside a DAW
  (monitor stretch, borderless, desktop mode, always on top, media buttons, Exit).
- Lyrics keys and menu items are gone: that part of BeatDrop isn't in Milk Pump.

### Tip: transparency in a DAW

**F12** makes **pure black** see-through (near-black stays solid, so it works best with presets
that have a true black background), and clicks on the see-through parts go to your DAW behind.
Click a lit part to bring Milk Pump back to the front. **Shift+Up / Down** fades the whole window.

### Download

| File | What |
|---|---|
| **Milk.Pump.0.3.24.msi** (9 MB) | The installer: replaces earlier versions. Tick the plugin, the app, or both. |
| Milk Pump Presets | Unchanged: get it from [0.3.21](https://github.com/seethrew/milk-pump/releases/tag/v0.3.21-beta) if you don't have it. |

Close your DAW before installing. **Windows may warn** "Windows protected your PC" because the
installer isn't signed: click **More info**, then **Run anyway**.
