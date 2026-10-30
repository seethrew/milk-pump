// mdvst_paths.h — where the engine's files live in plugin builds (MDVST_PLUGIN).
//
// Upstream finds everything beside GetModuleFileNameW(NULL), which inside a DAW is the DAW's exe,
// and some things relative to the working directory, which is the DAW's too. In plugin builds:
//
//   code    the D3DX DLLs                 beside the module (plugin DLL or EngineTest.exe)
//   data    presets, textures, settings,  Documents\<MDVST_DATA_FOLDER_NAME>\  (Phase 3, Daxy's
//           shader cache, screenshots     choice: easy to add presets, untouched by rebuilds)
//
// The data folder replaces upstream's "<exe folder>\BeatDrop Resources\" *and* the .ini folder:
// presets\, textures\, data\, docs\, startuppreset\, shadercache\, screenshots\, beatdrop*.ini,
// precache.txt all sit directly in it.
#pragma once

#include <windows.h>

// The plugin's own name (Daxy, 2026-10-29: "Milk Pump"), in one place: the data folder, the
// visuals window's title (and the lookups that find it by title), the tray tooltip.
#define MDVST_DATA_FOLDER_NAME L"Milk Pump"
#define MDVST_WINDOW_TITLE_A   "Milk Pump"
#define MDVST_WINDOW_TITLE     L"Milk Pump"

// Folder of the module containing the engine, with a trailing backslash.
const wchar_t* MDVST_ModuleDirectory();

// Documents\Milk Pump\, with a trailing backslash; created if missing. Falls back to the
// module folder if Documents cannot be found.
const wchar_t* MDVST_DataDirectory();

// Makes every .ttf in the data folder's fonts\ usable by name (szFontFace* in beatdrop.ini) in this
// process only (FR_PRIVATE): nothing is installed in Windows. Once per process; cheap to call again.
void MDVST_RegisterDataFonts();
