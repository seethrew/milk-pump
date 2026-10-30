// PluginEditor.h — Milk Pump's window: the visuals themselves, nothing else.
//
// The host opens and closes it like any plugin window (Live's wrench). Once the window is on
// screen its native handle goes to the engine, whose render thread draws in a child window that
// fills it (mdvst_engine.h). Resizable; the size is saved with the set. Double-click in the
// visuals takes them full screen on the window's monitor and back. A second copy of the plugin
// shows a line of text instead: the engine is one per process.
#pragma once

#include "PluginProcessor.h"

class MilkPumpEditor : public juce::AudioProcessorEditor, private juce::Timer
{
public:
    explicit MilkPumpEditor(MilkDropProcessor&);
    ~MilkPumpEditor() override;

    void paint(juce::Graphics&) override;
    void resized() override;
    void parentHierarchyChanged() override { attach(); }
    void visibilityChanged() override { attach(); }

private:
    void timerCallback() override { attach(); }
    void attach(); // hands the window to the engine once it is on screen

    MilkDropProcessor& processor;
    bool attached = false;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(MilkPumpEditor)
};
