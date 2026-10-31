// Loopback.cpp — see Loopback.h.
#include "Loopback.h"

#include <windows.h>
#include <mmdeviceapi.h>
#include <audioclient.h>
#include <functiondiscoverykeys_devpkey.h>
#include <ks.h>
#include <ksmedia.h>
#include <chrono>
#include <string>
#include <vector>

#include "mdvst_engine.h"

namespace
{
    template <class T> void release(T*& p) { if (p) { p->Release(); p = nullptr; } }

    long long nowMs()
    {
        using namespace std::chrono;
        return duration_cast<milliseconds>(steady_clock::now().time_since_epoch()).count();
    }

    std::wstring defaultDeviceId(IMMDeviceEnumerator* e, EDataFlow flow)
    {
        std::wstring id;
        IMMDevice* d = nullptr;
        if (SUCCEEDED(e->GetDefaultAudioEndpoint(flow, eConsole, &d)))
        {
            LPWSTR s = nullptr;
            if (SUCCEEDED(d->GetId(&s)))
            {
                id = s;
                CoTaskMemFree(s);
            }
            d->Release();
        }
        return id;
    }
}

Loopback::Loopback() : thread([this] { run(); }) {}

Loopback::~Loopback()
{
    stop = true;
    if (thread.joinable())
        thread.join();
}

double Loopback::secondsSinceSound() const
{
    const long long t = lastSoundMs.load();
    return t < 0 ? 1e9 : (nowMs() - t) / 1000.0;
}

void Loopback::run()
{
    CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    while (!stop && capture())
        for (int i = 0; i < 10 && !stop; ++i) // the device went away: try again shortly
            Sleep(50);
    CoUninitialize();
}

bool Loopback::capture()
{
    IMMDeviceEnumerator* enumerator = nullptr;
    IMMDevice* device = nullptr;
    IAudioClient* client = nullptr;
    IAudioCaptureClient* cap = nullptr;
    WAVEFORMATEX* fmt = nullptr;
    bool keepGoing = true;
    // CTRL+D in the window: the default recording device (a microphone, a line in) instead of
    // what the PC plays. Read once per session; a change ends the session and reopens.
    const bool mic = MDVST_Engine_CaptureMic();
    const EDataFlow flow = mic ? eCapture : eRender;

    auto cleanup = [&]
    {
        if (client) client->Stop();
        release(cap);
        release(client);
        release(device);
        release(enumerator);
        if (fmt) { CoTaskMemFree(fmt); fmt = nullptr; }
    };

    if (FAILED(CoCreateInstance(__uuidof(MMDeviceEnumerator), nullptr, CLSCTX_ALL, __uuidof(IMMDeviceEnumerator), (void**)&enumerator))
        || FAILED(enumerator->GetDefaultAudioEndpoint(flow, eConsole, &device))
        || FAILED(device->Activate(__uuidof(IAudioClient), CLSCTX_ALL, nullptr, (void**)&client))
        || FAILED(client->GetMixFormat(&fmt))
        || FAILED(client->Initialize(AUDCLNT_SHAREMODE_SHARED, mic ? 0 : AUDCLNT_STREAMFLAGS_LOOPBACK, 2000000 /* 200 ms */, 0, fmt, nullptr))
        || FAILED(client->GetService(__uuidof(IAudioCaptureClient), (void**)&cap))
        || FAILED(client->Start()))
    {
        cleanup();
        // No microphone, or Windows' privacy settings keep it from desktop apps: say so once
        // per switch, then keep retrying quietly (it may be plugged in or allowed later).
        if (mic && !micFailShown)
        {
            micFailShown = true;
            MDVST_Engine_ShowMessage(L"No microphone: check one is plugged in and Windows lets apps use it");
        }
        return true; // no device yet (or none at all): retry
    }
    micFailShown = false;

    // The mix format: float (usual) or integer PCM, any channel count; we take the first two.
    bool isFloat = fmt->wFormatTag == WAVE_FORMAT_IEEE_FLOAT;
    if (fmt->wFormatTag == WAVE_FORMAT_EXTENSIBLE)
        isFloat = reinterpret_cast<WAVEFORMATEXTENSIBLE*>(fmt)->SubFormat == KSDATAFORMAT_SUBTYPE_IEEE_FLOAT;
    const int channels = fmt->nChannels, bits = fmt->wBitsPerSample, frameBytes = fmt->nBlockAlign;
    const int rate = (int)fmt->nSamplesPerSec;
    std::vector<float> L, R;

    const std::wstring id = defaultDeviceId(enumerator, flow);
    long long lastDeviceCheck = nowMs();

    while (!stop)
    {
        Sleep(10);
        if (MDVST_Engine_CaptureMic() != mic) // CTRL+D: reopen on the other side
            break;
        if (nowMs() - lastDeviceCheck > 1000) // Windows switched the default device: follow it
        {
            lastDeviceCheck = nowMs();
            if (defaultDeviceId(enumerator, flow) != id)
                break;
        }
        UINT32 packet = 0;
        HRESULT hr = cap->GetNextPacketSize(&packet);
        if (FAILED(hr))
            break; // device gone (AUDCLNT_E_DEVICE_INVALIDATED and friends): reopen
        while (packet > 0)
        {
            BYTE* data = nullptr;
            UINT32 frames = 0;
            DWORD flags = 0;
            if (FAILED(cap->GetBuffer(&data, &frames, &flags, nullptr, nullptr)))
                break;
            L.assign(frames, 0.0f);
            R.assign(frames, 0.0f);
            if (!(flags & AUDCLNT_BUFFERFLAGS_SILENT))
            {
                for (UINT32 i = 0; i < frames; ++i)
                {
                    const BYTE* f = data + (size_t)i * frameBytes;
                    auto sample = [&](int ch) -> float
                    {
                        const BYTE* s = f + (size_t)ch * (bits / 8);
                        if (isFloat)
                            return bits == 64 ? (float)*reinterpret_cast<const double*>(s) : *reinterpret_cast<const float*>(s);
                        switch (bits)
                        {
                            case 16: return *reinterpret_cast<const int16_t*>(s) / 32768.0f;
                            case 24: return (int32_t)((uint32_t)s[0] << 8 | (uint32_t)s[1] << 16 | (uint32_t)s[2] << 24) / 2147483648.0f;
                            case 32: return *reinterpret_cast<const int32_t*>(s) / 2147483648.0f;
                            default: return 0.0f;
                        }
                    };
                    L[i] = sample(0);
                    R[i] = sample(channels > 1 ? 1 : 0);
                    if (L[i] != 0.0f || R[i] != 0.0f)
                        lastSoundMs = nowMs();
                }
            }
            cap->ReleaseBuffer(frames);
            if (frames > 0)
                MDVST_Engine_PushAudio(L.data(), R.data(), (int)frames, rate);
            if (FAILED(cap->GetNextPacketSize(&packet)))
                break;
        }
    }
    cleanup();
    return keepGoing;
}
