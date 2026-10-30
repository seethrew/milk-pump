// PluginProcessor.h — Milk Pump's audio side.
//
// Audio passes through untouched (the host's input buffer is the output buffer; processBlock
// never writes to it). The copy for the visualiser crosses threads like this:
//
//   audio thread:  processBlock  -> FIFO (juce::AbstractFifo, preallocated, lock-free)
//   feeder thread: FIFO -> MDVST_Engine_PushAudio (which locks and allocates, so it never runs
//                  on the audio thread)
//   render thread: the engine's own, draws into the plugin's window
//
// The engine is one per process (BeatDrop's global g_plugin). The first copy of the plugin owns
// it; any later copy passes audio only, and its window says so.
//
// The visuals ARE the plugin's window (Daxy, 2026-10-29: "behave like any other VST"): the host's
// wrench opens and closes them (PluginEditor). Double-click takes them full screen and back.
// Two parameters: HQ (off = 30 fps, about half the CPU; on = 60 fps) and Speed (how fast the
// visuals move, 1/8 to 2x).
#pragma once

#include <juce_audio_processors/juce_audio_processors.h>

class MilkDropProcessor : public juce::AudioProcessor, private juce::Timer
{
public:
    MilkDropProcessor();
    ~MilkDropProcessor() override;

    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override {}
    bool isBusesLayoutSupported(const BusesLayout& layouts) const override;
    void processBlock(juce::AudioBuffer<float>&, juce::MidiBuffer&) override;
    using AudioProcessor::processBlock;

    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }

    const juce::String getName() const override { return JucePlugin_Name; }
    bool acceptsMidi() const override { return false; }
    bool producesMidi() const override { return false; }
    double getTailLengthSeconds() const override { return 0.0; }

    int getNumPrograms() override { return 1; }
    int getCurrentProgram() override { return 0; }
    void setCurrentProgram(int) override {}
    const juce::String getProgramName(int) override { return {}; }
    void changeProgramName(int, const juce::String&) override {}

    void getStateInformation(juce::MemoryBlock&) override;
    void setStateInformation(const void*, int) override;

    // Message thread.
    bool ownsEngine() const { return owner.load() == this; }
    bool tryClaimEngine();          // true if this copy owns the engine afterwards
    bool openVisuals(void* hostWindow); // into the editor's window; false if another copy owns it
    void editorClosing();           // closes the visuals, unless they are full screen
    bool visualsOpen() const;
    double currentSampleRate() const { return sampleRate.load(); }
    int droppedBlocks() const { return dropped.load(); }

    // Saved with the set. Default 640x360: with Windows display scaling (Daxy's laptop) 960x540
    // came out ~1250x700 and covered most of Live (2026-10-29).
    int editorWidth = 640, editorHeight = 360;

private:
    class Feeder;

    void closeVisuals();
    void timerCallback() override; // message thread: keeps HQ and Speed in step with the engine

    static constexpr int kFifoFrames = 1 << 16; // ~0.34 s at 192 kHz, ~1.4 s at 48 kHz

    static std::atomic<MilkDropProcessor*> owner;

    juce::AbstractFifo fifo { kFifoFrames };
    juce::AudioBuffer<float> fifoBuffer { 2, kFifoFrames };
    std::atomic<double> sampleRate { 44100.0 };
    std::atomic<bool> feeding { false }; // audio thread writes only while the visuals are open
    std::atomic<int> dropped { 0 };      // blocks that did not fit (feeder stalled)
    std::unique_ptr<Feeder> feeder;

    juce::AudioParameterBool* hq = nullptr; // frame-rate cap: 30 off, 60 on
    int sentHq = -1;                         // what the open visuals were last told; -1 = nothing yet
    juce::AudioParameterChoice* speed = nullptr; // index into kSpeeds
    int shownSpeed = -1, shownHq = -1;           // last values seen, for the on-screen messages

    // The preset saved with the set (relative to the data folder when inside it) and its lock:
    // what the visuals show while they run, else what the set came with.
    juce::String preset;
    bool presetLocked = false;
    juce::CriticalSection presetLock; // hosts may save the state from any (non-audio) thread
    void refreshPreset(); // from the engine, if this copy's visuals are running

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(MilkDropProcessor)
};
