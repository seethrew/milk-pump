
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


  ============================================================================

   [ 01 ] what it is            [ 06 ] which presets work
   [ 02 ] the plugin            [ 07 ] installing + removing
   [ 03 ] the app               [ 08 ] if something is wrong
   [ 04 ] keys                  [ 09 ] credits + licences
   [ 05 ] presets

  ============================================================================
   [ 01 ]  W H A T   I T   I S         ..(-_-)..
  ----------------------------------------------------------------------------

   Milk Pump runs the real MilkDrop 2 visualiser engine (through BeatDrop,
   which brought it to 64-bit), so classic MilkDrop presets look and move the
   way they always have. Two ways in:

     > THE PLUGIN  a VST3 for Ableton Live or any VST3 host. Audio passes
                   through untouched; the visuals are drawn from it.
     > THE APP     a window of its own that reacts to whatever your PC is
                   playing, like the original MilkDrop.

   Both share the same presets, textures and settings, kept in

         Documents\Milk Pump

  ============================================================================
   [ 02 ]  T H E   P L U G I N       ..(-_-)..
  ----------------------------------------------------------------------------

   * The plugin's window IS the visuals. Open and close it like any plugin
     (in Live: the wrench). Drag its edge to resize.
   * Full screen: double-click the visuals (or ALT+ENTER) - a second monitor,
     a projector. Double-click again or ESC to come back.
   * Closing the window pauses the visuals. Reopen it and they're back as you
     left them: same size, same preset, any menu still open.
   * Your set remembers its preset (and its lock), the window size, HQ and
     Speed.
   * One Milk Pump per set. A second copy passes audio through and shows a
     note instead of visuals.

   The two controls on the device:

     HQ ........ off = 30 frames a second, on = 60 (smoother, more GPU)  [F3]
     SPEED ..... how fast the visuals move:                            [ [ ] ]
                 1/32  1/16  1/8  1/4  1/2  3/4  1  1.5x  2x
                 Slows motion for slow music; beats still land instantly.
                 Also slows automatic preset changes and the Life clocks.

   The keys move the device's controls too, so Live can record them.

  ============================================================================
   [ 03 ]  T H E   A P P           ..(-_-)..
  ----------------------------------------------------------------------------

   * Start menu  >  Milk Pump.
   * It listens to your DEFAULT PLAYBACK DEVICE: YouTube, Spotify, games,
     anything through Windows' sound. Switch device and it follows within a
     second.
   * It opens on the Milk Pump banner, then blends into your last preset.
     It remembers Speed, HQ, the preset and its lock, and the window size.
   * Double-click for full screen. Close the window to quit.

     .------------------------------------------------------------------.
     |  ASIO: a DAW on an ASIO driver (Elektron Overbridge, ASIO4ALL...) |
     |  sends its sound straight to the hardware, around Windows, so the |
     |  app may not hear it. Inside the DAW, use the PLUGIN: it gets the |
     |  sound directly, whatever the driver.                             |
     '------------------------------------------------------------------'

  ============================================================================
   [ 04 ]  K E Y S    ..(-_-)..           (click the visuals first; F1 = all)
  ----------------------------------------------------------------------------

     F1 .................. help on screen
     SPACE / H ........... next preset: blend / hard cut
     BACKSPACE ........... previous preset
     L ................... preset browser (arrows, ENTER, type to jump)
     ` or ~ .............. lock / unlock the preset (no automatic changes)
     R ................... random or in-order preset changes
     A ................... random mash-up: layers from different presets
     F3 .................. HQ on / off
     [ / ] ............... speed slower / faster
     UP / DOWN, Q ........ audio sensitivity up / down, reset
     F4, F5 .............. preset name, frames per second
     CTRL+X .............. screenshot (Documents\Milk Pump\screenshots)
     W ................... webcam into the visuals (cycles modes)
     CTRL+Z .............. Spout output on / off (visuals to video software)
     ESC ................. leave full screen, close a menu

  ============================================================================
   [ 05 ]  P R E S E T S..(-_-)....(-_-)....(-_-)....(-_-)....(-_-)..
  ----------------------------------------------------------------------------

   They live in  Documents\Milk Pump\presets . Add your own anywhere in
   there; the browser (L) shows folders and files. Ours:

     SEETHREW\PATCHES .... our own, all mixed together:
       Pixel Life - ...... Conway's Game of Life + cousins as pixel art.
                           Real Life movement, seeded by the music: a sound
                           line, a spectrum floor, gliders on the beat.
       Life - ............ SwarmSynth Revived(as of 11/26 unrealeased)
                           patches that use its Life sequencer: the patch's
                           rule, clock, starting picture, sensors, bees or
                           wanderers.
       the rest .......... one per SwarmSynth patch with its visualiser on.
     SEETHREW\MODES ...... one per SwarmSynth visualiser mode.
     the rest ............ BeatDrop's collection: 574 with the main install,
                           ~11,000 more (+1.2 GB of textures) from the
                           Milk Pump Presets installer.

  ============================================================================
   [ 06 ]  W H I C H   P R E S E T S   W O R K..(-_-)..
  ----------------------------------------------------------------------------

   Milk Pump IS the MilkDrop 2 engine, so nearly every MilkDrop preset works.

   [+] MilkDrop 1 + 2 presets (.milk), shader ones too: the great majority
       of what's out there.
   [+] projectM and Butterchurn presets: they're MilkDrop presets.
   [+] MilkDrop3 double presets (.milk2), and MilkDrop3 3.12's spectrum
       features for shaders.
   [+] Presets that use images, if the image is in
       Documents\Milk Pump\textures.
   [~] Presets from MilkDrop3 3.2 and later: those versions' source was
       never published, so features they added may not work.
   [~] A few shaders the old DirectX compiler can't handle: you get a shader
       error message and the preset runs without that effect. It never
       crashes: if the compiler itself falls over, Milk Pump retries with the
       newer compiler, then gives up quietly.
   [~] Rare maths quirks: BeatDrop's 64-bit expression engine (projectM-eval)
       replaces MilkDrop's 32-bit one. It matches MilkDrop, but a preset that
       leans on an odd quirk of the original may move a little differently.
   [-] Video files inside presets: off for now. Webcam + Spout still work.
   [-] Song titles / lyrics from the internet, BeatDrop's desktop mode: not
       part of Milk Pump.

  ============================================================================
   [ 07 ]  I N S T A L L I N G   +   R E M O V I N G  ..(-_-)..
  ----------------------------------------------------------------------------

     MILK PUMP <version>.MSI  (9 MB)
       tick what you want:
         [x] VST3 plugin ..... into Windows' standard VST3 folder
                               (C:\Program Files\Common Files\VST3)
         [x] standalone app .. Start menu: Milk Pump
       and always: this readme, and the essentials in Documents\Milk Pump:
       settings, the opening screen, fonts, all of our presets,
       BeatDrop's 574-preset light set.

     MILK PUMP PRESETS.MSI  (1.2 GB, optional)
       BeatDrop's full pack: ~11,000 presets and 1.2 GB of textures.

   * UPDATING: run the newer installer. It replaces the old one.
   * ADDING OR DROPPING ONE: run the installer again > Change > tick boxes.
   * YOUR DAW: make sure it scans the standard VST3 folder (in Live:
     Preferences > Plug-Ins > "Use VST3 Plug-In System Folders"), rescan.
   * REMOVING: Settings > Apps > Installed apps. Milk Pump and Milk Pump
     Presets are separate; removing one leaves the other.
   * LEFT BEHIND ON PURPOSE in Documents\Milk Pump: your settings, your own
     presets, screenshots, the shader cache. Delete the folder by hand to
     remove everything.

  ============================================================================
   [ 08 ]  I F   S O M E T H I N G   I S   W R O N G..(-_-)....(-_-)..
  ----------------------------------------------------------------------------

   the app doesn't react ...... is the sound on Windows' default device? A
                                DAW on ASIO goes around Windows: use the
                                plugin there. More sensitivity: UP.
   "shader error" message ..... that preset's shader didn't compile; the rest
                                still runs. SPACE to move on.
   too intense for the music .. SPEED down ( [ ), as low as 1/32.
   two Milk Pumps in a list ... an old copy is where the DAW scans, or an old
                                shortcut: keep only the installed one.
   keys do nothing ............ click the visuals first.
   2nd copy in a set is blank . as designed: one visualiser per set.

  ============================================================================
   [ 09 ]  C R E D I T S   +   L I C E N C E S   ..(-_-)..
  ----------------------------------------------------------------------------

     BeatDrop ......... OfficialIncubo + contributors (the 64-bit engine)
                        BSD 3-Clause
     MilkDrop3 3.12 ... milkdrop2077                          BSD 3-Clause
     MilkDrop 2 ....... Ryan Geiss / Nullsoft                 BSD 3-Clause
     projectM-eval .... the projectM team (preset expressions)         MIT
     JUCE 8 ........... the plugin                                 AGPL v3
     VST3 SDK ......... Steinberg                                     MIT
     Spout ............ Lynn Jarvis (video out)               BSD 2-Clause
     D3DX9 ............ Microsoft (DirectX 9 helpers)     redistributable
     fonts ............ 04b_30 by 04 (the logo); Ac437 EagleSpCGA Alt2 by
                        VileR, The Ultimate Oldschool PC Font Pack
                        (on-screen text)                      CC BY-SA 4.0
     presets .......... their many authors; some CC BY-NC-SA 3.0
                        (not for commercial use)

   MILK PUMP ITSELF is free software: the engine + the app under the
   BSD 3-Clause licence, the plugin under the GNU AGPL v3 (it is built with
   JUCE). Free to use, change and share; never to be sold.

   Full licence texts:  C:\Program Files\Milk Pump\Licences

   ============================================================================
  ..(-_-).. milk pump beta  ::  made(ported) by seethrew  ::  free, not for sale 
   ============================================================================


..(-_-)
▗ ▌ ▌▗
▛▘█▌█▌ ▜▘▌▌▛█▌ ▌▌▌.....(-_-)
▄▌▙▖▙▖ ▐▖▛▌▌▙▖▚▚▘..▗ ▌ ▌▗ 
