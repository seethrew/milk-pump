// Milk Pump.exe — the standalone app (Daxy, 2026-10-29: "same as MilkDrop: it reacts to any
// sound on the machine"). The same engine as the plugin, in its own window, fed by a loopback
// recording of what the PC is playing (Loopback.h). Everything the plugin has, the app has:
// Speed ([ / ]), HQ (F3), the fonts, the logo screen, the presets and data folder.
//
// The app's own settings (Speed, HQ, the preset showing at exit and its lock) are in the data
// folder's milkpump_app.ini; the window's size and place in beatdrop.ini, as the engine keeps
// them. Close the window to quit.
//
//   "Milk Pump.exe test=N"  runs N seconds, then writes milkpump_app_test.txt in the working
//                           directory (sound seen, Speed, HQ, preset) and quits: for the tests.
#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <string>

#include "Loopback.h"
#include "mdvst_controls.h"
#include "mdvst_engine.h"
#include "mdvst_paths.h"

namespace
{
    std::wstring settingsFile()
    {
        std::wstring path = MDVST_DataDirectory();
        if (!path.empty() && path.back() != L'\\')
            path += L'\\';
        return path + L"milkpump_app.ini";
    }

    struct Settings
    {
        int speed = kMdvstSpeedDefault;
        bool hq = false;
        std::wstring preset;
        bool locked = false;

        void load()
        {
            const auto f = settingsFile();
            // "speed2" counts the 1/32 and 1/16 steps; "speed" (before Build 17) did not.
            speed = GetPrivateProfileIntW(L"app", L"speed2", -1, f.c_str());
            if (speed < 0)
                speed = GetPrivateProfileIntW(L"app", L"speed", kMdvstSpeedDefault - kMdvstSpeedOldOffset, f.c_str())
                        + kMdvstSpeedOldOffset;
            if (speed < 0 || speed >= kMdvstSpeedCount)
                speed = kMdvstSpeedDefault;
            hq = GetPrivateProfileIntW(L"app", L"hq", 0, f.c_str()) != 0;
            wchar_t buf[2048] = {};
            GetPrivateProfileStringW(L"app", L"preset", L"", buf, 2048, f.c_str());
            preset = buf;
            locked = GetPrivateProfileIntW(L"app", L"locked", 0, f.c_str()) != 0;
        }

        void save() const
        {
            const auto f = settingsFile();
            WritePrivateProfileStringW(L"app", L"speed", nullptr, f.c_str());
            WritePrivateProfileStringW(L"app", L"speed2", std::to_wstring(speed).c_str(), f.c_str());
            WritePrivateProfileStringW(L"app", L"hq", hq ? L"1" : L"0", f.c_str());
            WritePrivateProfileStringW(L"app", L"preset", preset.c_str(), f.c_str());
            WritePrivateProfileStringW(L"app", L"locked", locked ? L"1" : L"0", f.c_str());
        }
    };
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE, PSTR cmdLine, int)
{
    timeBeginPeriod(1);
    const char* test = cmdLine ? strstr(cmdLine, "test=") : nullptr;
    const double testSeconds = test ? atof(test + 5) : 0.0;

    Settings settings;
    settings.load();
    MDVST_Engine_SetSpeed(kMdvstSpeeds[settings.speed]);
    MDVST_Engine_SetMaxFps(settings.hq ? 60 : 30);
    MDVST_Engine_SetStartPreset(settings.preset.c_str(), settings.locked);
    MDVST_Engine_SetIntroFirst(true); // the Milk Pump opening screen, then the last preset
    MDVST_Engine_SetMicAvailable(true); // CTRL+D: the microphone instead of what the PC plays

    if (!MDVST_Engine_Start(hInstance)) // no host window: a window of its own
    {
        MessageBoxW(nullptr, L"Milk Pump could not start the visuals (Direct3D 9 unavailable?).", L"Milk Pump", MB_ICONERROR);
        return 1;
    }

    auto loopback = std::make_unique<Loopback>();
    const DWORD started = GetTickCount();
    while (MDVST_Engine_IsRunning())
    {
        Sleep(50);

        // [ / ] and F3 in the window: the same Speed steps and HQ switch as the plugin's device.
        int steps = 0, toggles = 0;
        MDVST_Engine_TakeKeyRequests(&steps, &toggles);
        if (steps != 0)
        {
            int s = settings.speed + steps;
            settings.speed = s < 0 ? 0 : s >= kMdvstSpeedCount ? kMdvstSpeedCount - 1 : s;
            MDVST_Engine_SetSpeed(kMdvstSpeeds[settings.speed]);
            MDVST_Engine_ShowMessage((std::wstring(L"Speed ") + kMdvstSpeedNames[settings.speed]).c_str());
        }
        if (toggles % 2 != 0)
        {
            settings.hq = !settings.hq;
            MDVST_Engine_SetMaxFps(settings.hq ? 60 : 30);
            MDVST_Engine_ShowMessage(settings.hq ? L"HQ on: 60 fps" : L"HQ off: 30 fps");
        }

        wchar_t path[2048];
        bool locked = false;
        if (MDVST_Engine_CurrentPreset(path, 2048, &locked))
        {
            settings.preset = path;
            settings.locked = locked;
        }

        if (testSeconds > 0.0 && (GetTickCount() - started) / 1000.0 >= testSeconds)
        {
            if (FILE* f = fopen("milkpump_app_test.txt", "w"))
            {
                fprintf(f, "sound_seconds_ago=%.1f\nspeed=%ls\nhq=%d\npreset=%ls\nlocked=%d\n",
                        loopback->secondsSinceSound(), kMdvstSpeedNames[settings.speed], (int)settings.hq,
                        settings.preset.c_str(), (int)settings.locked);
                fclose(f);
            }
            break;
        }
    }

    settings.save();
    MDVST_Engine_Stop();
    loopback.reset();
    timeEndPeriod(1);
    return 0;
}
