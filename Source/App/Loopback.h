// Loopback.h — what the PC is playing, for the Milk Pump app (as MilkDrop and BeatDrop do it).
//
// WASAPI loopback on the default playback device, on its own thread, pushed into the engine
// (MDVST_Engine_PushAudio) in its own sample rate. Follows the default device when Windows
// switches it (headphones in, a different output chosen) and reopens after the device goes away.
// Nothing playing = no packets = the visuals just get silence.
#pragma once

#include <atomic>
#include <thread>

class Loopback
{
public:
    Loopback();
    ~Loopback(); // stops and joins

    // Seconds since sound last came in (for the app's test mode), or a large number if never.
    double secondsSinceSound() const;

private:
    void run();
    bool capture(); // one session on the current default device; false = stop asked

    std::atomic<bool> stop { false };
    std::atomic<long long> lastSoundMs { -1 };
    std::thread thread;
};
