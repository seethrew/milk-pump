// EngineTest — opens the engine's visualiser window from the static library and feeds it a
// generated 120 BPM pattern through MDVST_Engine_PushAudio: the same route the VST3 will use,
// with no loopback capture anywhere. Close the window to exit.
//
// Pattern (stereo, 48 kHz, 10 ms blocks, paced to real time):
//   kick   every beat     sine, pitch 150 -> 50 Hz (30 ms), amp decay tau 120 ms, centre
//   snare  beats 2 and 4  white noise tau 60 ms + 190 Hz sine tau 40 ms, centre
//   hat    every 8th      first-difference (high-passed) noise tau 12 ms, 30% right
//   pad    always         2 detuned saws (A2 / A2+7 cents), one-pole LP, 0.07 Hz pan LFO
// Every 4th bar is pad only (drums drop out), so the visuals should visibly relax.
#include <windows.h>
#include <dbghelp.h>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <csignal>
#include <cstdlib>
#include <exception>
#include <cstring>
#include <vector>

#include "mdvst_engine.h"

namespace
{
    constexpr double kTwoPi = 6.283185307179586;
    constexpr int kSampleRate = 48000;
    constexpr int kBlock = 480; // 10 ms
    constexpr double kBpm = 120.0;

    struct Noise
    {
        uint32_t s = 0x12345678u;
        float next() { s = s * 1664525u + 1013904223u; return (int32_t)s * (1.0f / 2147483648.0f); }
    };

    class Pattern
    {
    public:
        void render(float* L, float* R, int n)
        {
            const double samplesPerBeat = kSampleRate * 60.0 / kBpm;
            for (int i = 0; i < n; ++i, ++m_t)
            {
                const double beatPos = m_t / samplesPerBeat;
                const int beat = (int)beatPos;
                const bool drums = (beat / 4) % 4 != 3;
                const double tBeat = (beatPos - beat) * samplesPerBeat / kSampleRate; // s since beat
                const double eighth = beatPos * 2.0;
                const double tEighth = (eighth - (int)eighth) * samplesPerBeat * 0.5 / kSampleRate;

                float kick = 0.0f, snare = 0.0f, hat = 0.0f;
                if (drums)
                {
                    const double f = 50.0 + 100.0 * std::exp(-tBeat / 0.03);
                    m_kickPhase += kTwoPi * f / kSampleRate;
                    if (tBeat * kSampleRate < 1.0) m_kickPhase = 0.0;
                    kick = 0.9f * (float)(std::sin(m_kickPhase) * std::exp(-tBeat / 0.12));

                    if (beat % 2 == 1)
                        snare = (float)(0.35 * m_noise.next() * std::exp(-tBeat / 0.06)
                                      + 0.3 * std::sin(kTwoPi * 190.0 * tBeat) * std::exp(-tBeat / 0.04));

                    const float w = m_noise.next();
                    hat = 0.25f * (w - m_hatPrev) * (float)std::exp(-tEighth / 0.012);
                    m_hatPrev = w;
                }

                // Pad: chord root steps A2, F2, C3, G2 every 2 bars.
                static const double roots[4] = { 110.0, 87.307, 130.813, 97.999 };
                const double root = roots[(beat / 8) % 4];
                m_saw1 += root / kSampleRate;           m_saw1 -= std::floor(m_saw1);
                m_saw2 += root * 1.00405 / kSampleRate; m_saw2 -= std::floor(m_saw2);
                const float raw = (float)((m_saw1 * 2.0 - 1.0) + (m_saw2 * 2.0 - 1.0)) * 0.5f;
                m_lp += 0.04f * (raw - m_lp);
                const double pan = 0.5 + 0.4 * std::sin(kTwoPi * 0.07 * m_t / kSampleRate);
                const float pad = 0.25f * m_lp;

                L[i] = kick + snare + 0.7f * hat + pad * (float)std::sqrt(1.0 - pan);
                R[i] = kick + snare + 1.0f * hat + pad * (float)std::sqrt(pan);
            }
        }

    private:
        int64_t m_t = 0;
        double m_kickPhase = 0.0, m_saw1 = 0.0, m_saw2 = 0.0;
        float m_hatPrev = 0.0f, m_lp = 0.0f;
        Noise m_noise;
    };
}

// Feeds the pattern in real time until the window closes or `seconds` pass (0 = no limit).
static void Feed(Pattern& pattern, double seconds)
{
    std::vector<float> L(kBlock), R(kBlock);
    LARGE_INTEGER freq, start, now;
    QueryPerformanceFrequency(&freq);
    QueryPerformanceCounter(&start);
    int64_t pushed = 0;

    while (MDVST_Engine_IsRunning())
    {
        QueryPerformanceCounter(&now);
        const int64_t due = (now.QuadPart - start.QuadPart) * kSampleRate / freq.QuadPart;
        if (seconds > 0.0 && due >= (int64_t)(seconds * kSampleRate))
            return;
        while (pushed + kBlock <= due)
        {
            pattern.render(L.data(), R.data(), kBlock);
            MDVST_Engine_PushAudio(L.data(), R.data(), kBlock, kSampleRate);
            pushed += kBlock;
        }
        Sleep(2);
    }
}

// Appends a line to EngineTest-cycle.log in the working directory (cycle mode only; crashes, any mode).
static void Log(const char* what, int n)
{
    if (FILE* f = fopen("EngineTest-cycle.log", "a")) { fprintf(f, "%s %d\n", what, n); fclose(f); }
}

// Any mode: CRT failures that end in a fail-fast (invalid parameter, abort, terminate, pure call)
// and hardware faults write a symbolised stack to the log instead of vanishing without a trace.
static void LogStack(const char* why)
{
    FILE* f = fopen("EngineTest-cycle.log", "a");
    if (!f)
        return;
    fprintf(f, "CRASH: %s\n", why);
    HANDLE process = GetCurrentProcess();
    SymSetOptions(SYMOPT_LOAD_LINES | SYMOPT_UNDNAME);
    SymInitialize(process, nullptr, TRUE);
    void* frames[48];
    const USHORT count = CaptureStackBackTrace(1, 48, frames, nullptr);
    alignas(SYMBOL_INFO) char storage[sizeof(SYMBOL_INFO) + 256];
    SYMBOL_INFO* symbol = reinterpret_cast<SYMBOL_INFO*>(storage);
    for (USHORT i = 0; i < count; ++i)
    {
        ZeroMemory(storage, sizeof(storage));
        symbol->SizeOfStruct = sizeof(SYMBOL_INFO);
        symbol->MaxNameLen = 255;
        DWORD64 offset = 0;
        IMAGEHLP_LINE64 line = { sizeof(line) };
        DWORD lineOffset = 0;
        const DWORD64 address = (DWORD64)frames[i];
        const char* name = SymFromAddr(process, address, &offset, symbol) ? symbol->Name : "?";
        if (SymGetLineFromAddr64(process, address, &lineOffset, &line))
            fprintf(f, "  %s  %s(%lu)\n", name, line.FileName, line.LineNumber);
        else
            fprintf(f, "  %s+0x%llx\n", name, offset);
    }
    fclose(f);
}

static void InstallCrashLogging()
{
    // Access violations and other hardware faults too, on any thread (the render thread's are
    // the ones that matter): the stack from here runs down through the faulting frame. Only the
    // first one, and not the ones the engine catches itself (__try blocks see them first).
    AddVectoredExceptionHandler(0, [](EXCEPTION_POINTERS* e) -> LONG
    {
        const DWORD code = e->ExceptionRecord->ExceptionCode;
        static LONG once = 0;
        if ((code == EXCEPTION_ACCESS_VIOLATION || code == EXCEPTION_ILLEGAL_INSTRUCTION
             || code == EXCEPTION_INT_DIVIDE_BY_ZERO || code == EXCEPTION_STACK_OVERFLOW)
            && InterlockedExchange(&once, 1) == 0)
        {
            char why[160];
            sprintf_s(why, "exception 0x%08lx at %p (address %p)", code, e->ExceptionRecord->ExceptionAddress,
                      e->ExceptionRecord->NumberParameters > 1 ? (void*)e->ExceptionRecord->ExceptionInformation[1] : nullptr);
            LogStack(why);
        }
        return EXCEPTION_CONTINUE_SEARCH;
    });
    _set_invalid_parameter_handler([](const wchar_t*, const wchar_t*, const wchar_t*, unsigned, uintptr_t)
        { LogStack("invalid parameter"); });
    _set_purecall_handler([] { LogStack("pure virtual call"); });
    signal(SIGABRT, [](int) { LogStack("abort"); });
    std::set_terminate([] { LogStack("terminate"); std::abort(); });
}

// "EngineTest.exe cycle" first opens and closes the window 5 times (the plugin's Open/Close
// button), including one Stop straight after Start, then runs normally.
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE, PSTR cmdLine, int)
{
    timeBeginPeriod(1);
    Pattern pattern;
    InstallCrashLogging(); // every mode: a crash leaves its stack in EngineTest-cycle.log

    if (cmdLine && strstr(cmdLine, "cycle"))
    {
        static const double runFor[5] = { 3.0, 0.0, 2.0, 0.5, 3.0 }; // 0.0: Stop immediately
        int n = 0;
        for (double seconds : runFor)
        {
            Log("start", ++n);
            if (!MDVST_Engine_Start(hInstance))
                return 2;
            if (seconds > 0.0)
                Feed(pattern, seconds);
            Log("stop", n);
            MDVST_Engine_Stop();
            Log("stopped", n);
            if (MDVST_Engine_IsRunning())
                return 3;
        }
    }

    // "EngineTest.exe speed=0.5": the plugin's Speed control, for comparing presets by eye.
    if (const char* s = cmdLine ? strstr(cmdLine, "speed=") : nullptr)
        MDVST_Engine_SetSpeed((float)atof(s + 6));

    if (!MDVST_Engine_Start(hInstance))
    {
        MessageBoxW(nullptr, L"The engine could not start (Direct3D 9 unavailable?).", L"EngineTest", MB_ICONERROR);
        return 1;
    }
    Feed(pattern, 0.0);

    timeEndPeriod(1);
    MDVST_Engine_Stop();
    return 0;
}
