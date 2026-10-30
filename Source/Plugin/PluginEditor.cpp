// PluginEditor.cpp — see PluginEditor.h.
#include "PluginEditor.h"

#include "mdvst_engine.h"

MilkPumpEditor::MilkPumpEditor(MilkDropProcessor& p)
    : AudioProcessorEditor(p), processor(p)
{
    // Read the saved size first: setting the limits resizes (to the minimum) on the way.
    const int w = processor.editorWidth, h = processor.editorHeight;
    setOpaque(true);
    setResizable(true, true);
    setResizeLimits(320, 180, 7680, 4320);
    setSize(w, h);
    startTimerHz(4); // retries: the window may reach the screen late, or another copy may let go
}

MilkPumpEditor::~MilkPumpEditor()
{
    stopTimer();
    if (attached)
        processor.editorClosing(); // before the host destroys the window the visuals sit in
}

void MilkPumpEditor::attach()
{
    if (attached)
    {
        // The visuals closed themselves (full screen left after the editor went, or D3D failed).
        if (!processor.visualsOpen())
        {
            attached = false;
            repaint();
        }
        else
            MDVST_Engine_HostResized(); // the window's size can reach Windows after resized()
        return;
    }
    auto* peer = getPeer();
    if (peer == nullptr || !isShowing())
        return;
    auto hwnd = static_cast<HWND>(peer->getNativeHandle());
    // JUCE paints this window too; keep it off the visuals.
    SetWindowLongW(hwnd, GWL_STYLE, GetWindowLongW(hwnd, GWL_STYLE) | WS_CLIPCHILDREN);
    attached = processor.openVisuals(hwnd);
    if (attached)
        MDVST_Engine_HostResized();
    repaint();
}

void MilkPumpEditor::paint(juce::Graphics& g)
{
    g.fillAll(juce::Colours::black);
    if (attached)
        return;
    g.setColour(juce::Colours::white);
    g.setFont(16.0f);
    g.drawFittedText(processor.ownsEngine()
                         ? juce::String("Milk Pump could not start the visuals (Direct3D 9).")
                         : juce::String("Milk Pump is showing its visuals on another track.\n"
                                        "One set of visuals at a time; this copy passes audio only."),
                     getLocalBounds().reduced(16), juce::Justification::centred, 4);
}

void MilkPumpEditor::resized()
{
    if (getPeer() != nullptr) // only sizes seen on screen are kept (not set-up or teardown ones)
    {
        processor.editorWidth = getWidth();
        processor.editorHeight = getHeight();
    }
    if (attached)
        MDVST_Engine_HostResized();
}
