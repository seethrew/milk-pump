// mdvst_engine.h — the plugin's view of the BeatDrop engine (MDVST_PLUGIN builds only).
//
// One engine per process: BeatDrop keeps its state in the global CPlugin g_plugin.
// Implemented at the end of vis_milk2/Milkdrop2PcmVisualizer.cpp.
#pragma once

#include <windows.h>

// Opens the visualiser window on its own render thread. `module` is the HINSTANCE that holds the
// engine's resources (plugin.rc): the plugin DLL, or the test exe. `host`: the plugin editor's
// window, which the visuals then fill as a child window (full screen takes them out and puts them
// back); null = a free top-level window. Returns false if Direct3D 9 is unavailable. If already
// running (full screen, its editor closed) it only takes `host` as the window to return into.
bool MDVST_Engine_Start(HINSTANCE module, HWND host = nullptr);

// Closes the window and waits for the render thread to finish, answering messages sent to the
// calling thread meanwhile (safe from the editor's UI thread). Safe if not running.
void MDVST_Engine_Stop();

// The editor changed size: the visuals follow (asynchronously).
void MDVST_Engine_HostResized();

// True while the visuals are inside the editor (not full screen / stretched out of it).
bool MDVST_Engine_InsideHost();

// The editor is closing while the visuals are out of it (full screen): they stay up; leaving
// full screen then parks them, as there is nothing to return into.
void MDVST_Engine_ReleaseHost();

// The editor is closing with the visuals inside it: they leave it, hidden, and stop drawing
// (almost no CPU), keeping everything (preset, menus, settings); the next MDVST_Engine_Start
// with an editor's window puts them back as they were. Waits (pumping) until they are out.
void MDVST_Engine_Park();
bool MDVST_Engine_Parked();

// The preset saved with the set. CurrentPreset: the one showing now (relative to the data folder
// when inside it) and whether it is locked; false before the first one has loaded. SetStartPreset
// (before Start): the next start loads that one instead of the start-up preset, if the file is
// still there. TakeStartPreset: the engine's side of that, once.
// Keys in the visuals window for the plugin's parameters: [ / ] step Speed, F3 toggles HQ. The
// engine only records the presses; the plugin takes them (TakeKeyRequests), moves its parameters
// (so the host's device moves too) and says what it did (ShowMessage, any thread).
void MDVST_Engine_RequestSpeedStep(int direction); // -1 slower, +1 faster
void MDVST_Engine_RequestHqToggle();
void MDVST_Engine_TakeKeyRequests(int* speedSteps, int* hqToggles);
void MDVST_Engine_ShowMessage(const wchar_t* text);

bool MDVST_Engine_CurrentPreset(wchar_t* path, int maxChars, bool* locked);
void MDVST_Engine_SetStartPreset(const wchar_t* path, bool locked);
bool MDVST_Engine_TakeStartPreset(wchar_t* path, int maxChars, bool* locked);
// The app (before Start): the opening screen plays first, at normal speed, for 8 s; then the
// start preset blends in. The plugin restores a set's preset straight away.
void MDVST_Engine_SetIntroFirst(bool introFirst);

// The app (before Start): it can listen to the microphone, so CTRL+D and the menu switch between
// the playback device and the default recording device. The plugin hears its track only: there
// the switch just says so. MDVST_Engine_CaptureMic is the switch's state, for the capture thread.
void MDVST_Engine_SetMicAvailable(bool available);
bool MDVST_Engine_MicAvailable();
bool MDVST_Engine_CaptureMic();

// False once the window has been closed, by Stop() or by the user.
bool MDVST_Engine_IsRunning();

// Hands audio to the visualiser. `right` may be null for mono. Any sample rate; above 44.1 kHz
// the engine decimates by an integer ratio. Takes a lock and allocates: NOT for the audio thread.
// Phase 2 puts a lock-free ring buffer between processBlock and this call.
void MDVST_Engine_PushAudio(const float* left, const float* right, int numFrames, int sampleRate);

// Asks for a frame-rate cap (the plugin's HQ switch: 30 or 60). Any thread; the render thread
// picks it up on its next frame, after the .ini has been read, so it wins over the saved value.
// F3 in the window still changes it until the next request.
void MDVST_Engine_SetMaxFps(int fps);

// Engine side: the pending request, or 0 if none; clears it. Called by the render thread.
int MDVST_Engine_TakeRequestedFps();

// The Speed control: 1 = as the preset was written, 0.5 = half as fast. Scales each frame's motion
// (zoom, rotation, warp, drift), the animation clock (`time`, shaders) and the `fps` presets see.
// Not the trail fade: presets that draw new shapes every frame would pile up into solid colour.
// Beat reactions stay instant. Any thread; clamped to 0.01..4.
void MDVST_Engine_SetSpeed(float speed);
float MDVST_Engine_Speed();
