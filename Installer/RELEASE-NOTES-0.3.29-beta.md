**Milk Pump 0.3.29 beta**: fixes for the webcam and for switching the device off. Tested in Ableton Live.

### Fixed

- **The webcam could freeze the DAW.** In some sets the camera never opened, and turning the webcam
  off then froze Live ("not responding"). Milk Pump now lets go of a stuck camera, and after a few
  seconds without a picture it tells you on screen. We traced it to another plugin in that set
  blocking the camera: if the webcam won't start in one set but does in an empty one, try the set
  without its most unusual plugins.
- **Switching the device off now switches the visuals off**: in the plugin window and in full screen,
  menus and on-screen text included. Switching it on again brings them back exactly as they were.
  (Before, the full-screen visuals stayed up, and with transparency on, menu text floated over Live.)
- **The mouse pointer** could stay invisible over Live after switching off from full screen.

### New

- `Documents\Milk Pump\webcam.log` records each step of starting the camera, to help find what's
  blocking it if it ever won't start.

### Download

| File | What |
|---|---|
| **Milk.Pump.0.3.29.msi** (9 MB) | The installer: replaces earlier versions. Tick the plugin, the app, or both. |
| Milk Pump Presets | Unchanged: get it from [0.3.21](https://github.com/seethrew/milk-pump/releases/tag/v0.3.21-beta) if you don't have it. |

Close your DAW before installing. **Windows may warn** "Windows protected your PC" because the
installer isn't signed: click **More info**, then **Run anyway**.
