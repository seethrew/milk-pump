// mdvst_audio.cpp — plugin-mode replacements for what the engine takes from
// audio/loopback-capture.cpp, which is left out of MDVST_PLUGIN builds.
//
// SAMPLE_RATE sets the FFT bin width (Hz per bin) for the bass/mid/treble beat-detection split in
// CPlugin::DoCustomSoundAnalysis. Upstream reads the default Windows playback device's rate; here
// it is the rate of the audio actually stored in audiobuf.cpp's ring, i.e. the host's rate after
// the engine's integer decimation (88.2/96 kHz -> 44.1/48 kHz, 176.4/192 kHz -> 44.1/48 kHz).
#include <windows.h>

extern UINT32 pcmSampleRate; // audio/audiobuf.cpp, written under its lock by SetAudioBuf

int SAMPLE_RATE = 44100;

HRESULT DetectSampleRate()
{
    const UINT32 rate = pcmSampleRate; // aligned 32-bit read; a stale value is harmless here
    if (rate != 0)
        SAMPLE_RATE = (int)rate;
    return S_OK;
}
