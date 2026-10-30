// PluginProcessor.cpp — see PluginProcessor.h for the thread layout.
#include "PluginProcessor.h"
#include "PluginEditor.h"

#include "mdvst_engine.h"
#include "mdvst_controls.h"

std::atomic<MilkDropProcessor*> MilkDropProcessor::owner { nullptr };

namespace
{
    // The Speed choices, as Live shows them, and the factor each one means (shared with the app).
    const juce::StringArray kSpeedNames(kMdvstSpeedNames, kMdvstSpeedCount);
    const float* const kSpeeds = kMdvstSpeeds;
    constexpr int kSpeedDefault = kMdvstSpeedDefault;
}

// Moves audio from the FIFO into the engine every few milliseconds. The engine's own ring holds
// the last ~0.5 s, and the render thread reads it once per frame, so 5 ms of jitter is invisible.
class MilkDropProcessor::Feeder : public juce::Thread
{
public:
    explicit Feeder(MilkDropProcessor& p) : juce::Thread("Milk Pump feeder"), processor(p)
    {
        left.resize(kFifoFrames);
        right.resize(kFifoFrames);
    }

    void run() override
    {
        while (!threadShouldExit())
        {
            wait(5);

            const int ready = processor.fifo.getNumReady();
            if (ready == 0)
                continue;
            {
                const auto scope = processor.fifo.read(ready);
                const auto& buf = processor.fifoBuffer;
                if (scope.blockSize1 > 0)
                {
                    std::copy_n(buf.getReadPointer(0, scope.startIndex1), scope.blockSize1, left.data());
                    std::copy_n(buf.getReadPointer(1, scope.startIndex1), scope.blockSize1, right.data());
                }
                if (scope.blockSize2 > 0)
                {
                    std::copy_n(buf.getReadPointer(0, scope.startIndex2), scope.blockSize2, left.data() + scope.blockSize1);
                    std::copy_n(buf.getReadPointer(1, scope.startIndex2), scope.blockSize2, right.data() + scope.blockSize1);
                }
            }

            if (MDVST_Engine_IsRunning())
                MDVST_Engine_PushAudio(left.data(), right.data(), ready, (int)processor.sampleRate.load());
            else
                processor.feeding = false; // the user closed the window; stop filling the FIFO
        }
    }

private:
    MilkDropProcessor& processor;
    std::vector<float> left, right;
};

MilkDropProcessor::MilkDropProcessor()
    : AudioProcessor(BusesProperties()
                         .withInput("Input", juce::AudioChannelSet::stereo(), true)
                         .withOutput("Output", juce::AudioChannelSet::stereo(), true))
{
    addParameter(hq = new juce::AudioParameterBool(juce::ParameterID { "hq", 1 }, "HQ", false));
    addParameter(speed = new juce::AudioParameterChoice(juce::ParameterID { "speed", 1 }, "Speed", kSpeedNames, kSpeedDefault));
    tryClaimEngine();
    startTimerHz(10);
}

juce::AudioProcessorEditor* MilkDropProcessor::createEditor()
{
    return new MilkPumpEditor(*this);
}

void MilkDropProcessor::timerCallback()
{
    if (ownsEngine())
    {
        // Keys in the visuals window: move the parameters, so the host's device follows.
        int steps = 0, toggles = 0;
        MDVST_Engine_TakeKeyRequests(&steps, &toggles);
        if (steps != 0)
        {
            const int index = juce::jlimit(0, kSpeedNames.size() - 1, speed->getIndex() + steps);
            speed->beginChangeGesture();
            speed->setValueNotifyingHost(speed->convertTo0to1((float)index));
            speed->endChangeGesture();
        }
        if (toggles % 2 != 0)
        {
            hq->beginChangeGesture();
            hq->setValueNotifyingHost(hq->get() ? 0.0f : 1.0f);
            hq->endChangeGesture();
        }
        MDVST_Engine_SetSpeed(kSpeeds[speed->getIndex()]);

        // Say so on screen whenever either changes, from a key or from the device.
        if (visualsOpen())
        {
            const int s = speed->getIndex(), q = (int)hq->get();
            if (shownSpeed >= 0 && s != shownSpeed)
                MDVST_Engine_ShowMessage(("Speed " + kSpeedNames[s]).toWideCharPointer());
            if (shownHq >= 0 && q != shownHq)
                MDVST_Engine_ShowMessage(q ? L"HQ on: 60 fps" : L"HQ off: 30 fps");
            shownSpeed = s;
            shownHq = q;
        }
    }

    // HQ: tell the window on every open and whenever the switch moves.
    if (!visualsOpen())
        sentHq = -1;
    else if (sentHq != (int)hq->get())
    {
        sentHq = (int)hq->get();
        MDVST_Engine_SetMaxFps(sentHq ? 60 : 30);
    }

    refreshPreset(); // kept current, so the state is right even after the visuals close
}

MilkDropProcessor::~MilkDropProcessor()
{
    stopTimer();
    if (!ownsEngine())
        return;
    closeVisuals();
    feeder->stopThread(1000);
    feeder.reset();
    owner = nullptr;
}

bool MilkDropProcessor::tryClaimEngine()
{
    MilkDropProcessor* expected = nullptr;
    if (!owner.compare_exchange_strong(expected, this) && expected != this)
        return false;
    if (feeder == nullptr)
    {
        feeder = std::make_unique<Feeder>(*this);
        feeder->startThread();
    }
    return true;
}

bool MilkDropProcessor::openVisuals(void* hostWindow)
{
    if (!tryClaimEngine())
        return false;
    if (!MDVST_Engine_IsRunning()) // a fresh start: the set's preset, if it has one
    {
        const juce::ScopedLock sl(presetLock);
        MDVST_Engine_SetStartPreset(preset.toWideCharPointer(), presetLocked);
    }
    if (!MDVST_Engine_Start(static_cast<HINSTANCE>(juce::Process::getCurrentModuleInstanceHandle()),
                            static_cast<HWND>(hostWindow)))
        return false;
    feeding = true;
    return true;
}

void MilkDropProcessor::editorClosing()
{
    if (!ownsEngine())
        return;
    if (!MDVST_Engine_IsRunning())
        return;
    if (MDVST_Engine_InsideHost())
        MDVST_Engine_Park(); // hidden and paused; the next window gets them back as they were
    else
        MDVST_Engine_ReleaseHost(); // full screen: stays up for the projector
}

void MilkDropProcessor::closeVisuals()
{
    if (!ownsEngine())
        return;
    feeding = false;
    MDVST_Engine_Stop();
}

bool MilkDropProcessor::visualsOpen() const
{
    return ownsEngine() && MDVST_Engine_IsRunning();
}

void MilkDropProcessor::prepareToPlay(double newSampleRate, int)
{
    sampleRate = newSampleRate;
}

bool MilkDropProcessor::isBusesLayoutSupported(const BusesLayout& layouts) const
{
    const auto out = layouts.getMainOutputChannelSet();
    if (out != juce::AudioChannelSet::mono() && out != juce::AudioChannelSet::stereo())
        return false;
    return layouts.getMainInputChannelSet() == out;
}

void MilkDropProcessor::processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer&)
{
    // Pass-through: input and output share this buffer, so leaving it alone is bit-exact.
    const int numIn = getTotalNumInputChannels();
    for (int ch = numIn; ch < getTotalNumOutputChannels(); ++ch)
        buffer.clear(ch, 0, buffer.getNumSamples());

    if (!feeding.load(std::memory_order_relaxed) || numIn == 0)
        return;

    const int n = buffer.getNumSamples();
    if (fifo.getFreeSpace() < n)
    {
        dropped.fetch_add(1, std::memory_order_relaxed);
        return;
    }

    const float* inL = buffer.getReadPointer(0);
    const float* inR = buffer.getReadPointer(numIn > 1 ? 1 : 0);
    const auto scope = fifo.write(n);
    if (scope.blockSize1 > 0)
    {
        fifoBuffer.copyFrom(0, scope.startIndex1, inL, scope.blockSize1);
        fifoBuffer.copyFrom(1, scope.startIndex1, inR, scope.blockSize1);
    }
    if (scope.blockSize2 > 0)
    {
        fifoBuffer.copyFrom(0, scope.startIndex2, inL + scope.blockSize1, scope.blockSize2);
        fifoBuffer.copyFrom(1, scope.startIndex2, inR + scope.blockSize1, scope.blockSize2);
    }
}

void MilkDropProcessor::getStateInformation(juce::MemoryBlock& data)
{
    // Byte 0 was the Visuals switch (Builds 7-10), then always 1; now the layout: 2 = Speed's index
    // counts the 1/32 and 1/16 steps (Build 17).
    juce::MemoryOutputStream out(data, false);
    out.writeByte(2);
    out.writeBool(hq->get());
    out.writeByte((char)speed->getIndex());
    out.writeShort((short)editorWidth);
    out.writeShort((short)editorHeight);
    refreshPreset();
    const juce::ScopedLock sl(presetLock);
    out.writeString(preset);
    out.writeBool(presetLocked);
}

void MilkDropProcessor::refreshPreset()
{
    if (!visualsOpen())
        return;
    wchar_t path[2048];
    bool locked = false;
    if (MDVST_Engine_CurrentPreset(path, (int)std::size(path), &locked))
    {
        const juce::ScopedLock sl(presetLock);
        preset = juce::String(path);
        presetLocked = locked;
    }
}

void MilkDropProcessor::setStateInformation(const void* data, int size)
{
    juce::MemoryInputStream in(data, (size_t)size, false);
    const int layout = size >= 1 ? (int)in.readByte() : 0; // 0/1: the old Visuals switch
    if (size >= 2) // sets saved before HQ existed hold one byte: HQ stays off
        *hq = in.readBool();
    if (size >= 3) // and before Speed, two: Speed stays at 1
        *speed = juce::jlimit(0, kSpeedNames.size() - 1, (int)in.readByte() + (layout < 2 ? kMdvstSpeedOldOffset : 0));
    if (size >= 7) // and before the window, three: the default size
    {
        editorWidth = juce::jlimit(320, 7680, (int)in.readShort());
        editorHeight = juce::jlimit(180, 4320, (int)in.readShort());
    }
    if (!in.isExhausted()) // and before the preset, seven: the start-up preset
    {
        const juce::ScopedLock sl(presetLock);
        preset = in.readString();
        presetLocked = in.readBool();
    }
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new MilkDropProcessor();
}

