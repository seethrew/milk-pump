// HostTest — hosts the built "Milk Pump.vst3" through JUCE's VST3 hosting, like a DAW would,
// including the plugin's window (JUCE's host-side window embeds the plugin's view, as Live does).
//
//   1. pass-through: 20 s of noise + kicks in blocks of varying size, output must equal input
//      bit for bit (the null test), at 48 kHz and at 96 kHz; a second copy at the same time
//   2. HQ and Speed: present, defaults, saved with the set (with the window size); HQ costs more
//   3. the plugin's window: no visuals until it opens (a plugin scan opens nothing); then the
//      visuals inside it, filling it, following a resize; double-click to full screen and back;
//      closing the window stops them; a second copy's window adds no second visuals; full screen
//      outlives the window, and leaving full screen then closes the visuals
//   4. feed 6 s in real time with the window open, then delete the plugin with it still open,
//      twice (reopen after a delete)
//
// Exit code 0 = all passed. Prints one line per check.
#include <juce_audio_processors/juce_audio_processors.h>
#include <windows.h>

namespace
{
    int failures = 0;

    void check(bool ok, const juce::String& what)
    {
        std::printf("%s  %s\n", ok ? "PASS" : "FAIL", what.toRawUTF8());
        std::fflush(stdout);
        if (!ok)
            ++failures;
    }

    // Noise plus a decaying 60 Hz kick every half second.
    void fill(juce::AudioBuffer<float>& b, juce::Random& rng, int64_t& t, double sampleRate)
    {
        for (int i = 0; i < b.getNumSamples(); ++i, ++t)
        {
            const double s = std::fmod((double)t / sampleRate, 0.5);
            const float kick = (float)(0.8 * std::sin(6.283185307 * 60.0 * s) * std::exp(-s / 0.1));
            b.setSample(0, i, kick + 0.1f * (rng.nextFloat() * 2.0f - 1.0f));
            b.setSample(1, i, kick + 0.1f * (rng.nextFloat() * 2.0f - 1.0f));
        }
    }

    std::unique_ptr<juce::AudioPluginInstance> load(juce::AudioPluginFormatManager& fm,
                                                    const juce::PluginDescription& d, double sr, int block)
    {
        juce::String error;
        auto p = fm.createPluginInstance(d, sr, block, error);
        if (p == nullptr)
        {
            check(false, "load: " + error);
            return nullptr;
        }
        p->setPlayConfigDetails(2, 2, sr, block);
        p->prepareToPlay(sr, block);
        return p;
    }

    bool nullTest(juce::AudioPluginInstance& p, double sr, double seconds)
    {
        juce::Random rng(1234);
        int64_t t = 0;
        juce::MidiBuffer midi;
        const int64_t total = (int64_t)(seconds * sr);
        while (t < total)
        {
            const int n = 32 + rng.nextInt(1024 - 32); // hosts vary the block size
            juce::AudioBuffer<float> in(2, n), io(2, n);
            fill(in, rng, t, sr);
            io.makeCopyOf(in);
            p.processBlock(io, midi);
            for (int ch = 0; ch < 2; ++ch)
                if (std::memcmp(in.getReadPointer(ch), io.getReadPointer(ch), sizeof(float) * (size_t)n) != 0)
                    return false;
        }
        return true;
    }

    // Every render window of this process: top-level (full screen) or inside a plugin window.
    BOOL CALLBACK considerWindow(HWND h, LPARAM lp)
    {
        wchar_t cls[64] = {};
        GetClassNameW(h, cls, 64);
        DWORD pid = 0;
        GetWindowThreadProcessId(h, &pid);
        if (pid == GetCurrentProcessId() && wcscmp(cls, L"Direct3DWindowClass") == 0 && IsWindowVisible(h))
            reinterpret_cast<std::vector<HWND>*>(lp)->push_back(h);
        return TRUE;
    }

    std::vector<HWND> renderWindows()
    {
        std::vector<HWND> found;
        EnumWindows([](HWND top, LPARAM lp) -> BOOL
        {
            considerWindow(top, lp);
            EnumChildWindows(top, considerWindow, lp); // all descendants
            return TRUE;
        }, reinterpret_cast<LPARAM>(&found));
        return found;
    }

    juce::AudioProcessorParameter* findParam(juce::AudioPluginInstance& p, const char* name)
    {
        for (auto* param : p.getParameters())
            if (param->getName(32) == name)
                return param;
        return nullptr;
    }

    double processCpuSeconds()
    {
        FILETIME created, exited, kernel, user;
        GetProcessTimes(GetCurrentProcess(), &created, &exited, &kernel, &user);
        auto secs = [](FILETIME f) { return (double)(((uint64_t)f.dwHighDateTime << 32) | f.dwLowDateTime) / 1e7; };
        return secs(kernel) + secs(user);
    }

    void pumpMessages()
    {
        MSG msg;
        while (PeekMessageW(&msg, nullptr, 0, 0, PM_REMOVE)) { TranslateMessage(&msg); DispatchMessageW(&msg); }
    }

    // Feeds audio in real time while pumping this thread's messages. Returns true if every output
    // block equalled its input bit for bit (the null test with the visuals running).
    bool runRealTime(juce::AudioPluginInstance& p, double sr, double seconds)
    {
        juce::Random rng(99);
        int64_t t = 0;
        bool exact = true;
        juce::MidiBuffer midi;
        const int block = 480;
        juce::AudioBuffer<float> in(2, block), io(2, block);
        const auto start = juce::Time::getMillisecondCounterHiRes();
        while (juce::Time::getMillisecondCounterHiRes() - start < seconds * 1000.0)
        {
            const int64_t due = (int64_t)((juce::Time::getMillisecondCounterHiRes() - start) * sr / 1000.0);
            while (t + block <= due)
            {
                fill(in, rng, t, sr);
                io.makeCopyOf(in);
                p.processBlock(io, midi);
                for (int ch = 0; ch < 2; ++ch)
                    exact = exact && std::memcmp(in.getReadPointer(ch), io.getReadPointer(ch), sizeof(float) * block) == 0;
            }
            pumpMessages(); // as a DAW's UI thread would
            Sleep(5);
        }
        return exact;
    }

    // The host's plugin window: JUCE's host-side editor (which embeds the plugin's own view, as
    // a DAW does) on the desktop with a title bar.
    struct HostWindow
    {
        std::unique_ptr<juce::AudioProcessorEditor> editor;

        bool open(juce::AudioPluginInstance& p)
        {
            editor.reset(p.createEditorIfNeeded());
            if (editor == nullptr)
                return false;
            editor->addToDesktop(juce::ComponentPeer::windowHasTitleBar | juce::ComponentPeer::windowAppearsOnTaskbar);
            editor->setTopLeftPosition(100, 100);
            editor->setVisible(true);
            return true;
        }
        HWND frame() const
        {
            return editor && editor->getPeer() ? static_cast<HWND>(editor->getPeer()->getNativeHandle()) : nullptr;
        }
        void close() { editor.reset(); } // the host deletes its window, and with it the plugin's view
    };

    bool insideAndFilling(HWND frame)
    {
        auto w = renderWindows();
        if (w.size() != 1 || frame == nullptr || !IsChild(frame, w[0]))
            return false;
        RECT mine, parent;
        GetClientRect(w[0], &mine);
        GetClientRect(GetParent(w[0]), &parent);
        return mine.right == parent.right && mine.bottom == parent.bottom && mine.right > 100;
    }

    bool isFullScreen(HWND w)
    {
        if (w == nullptr || GetParent(w) != nullptr)
            return false;
        MONITORINFO mi = { sizeof(mi) };
        GetMonitorInfoW(MonitorFromWindow(w, MONITOR_DEFAULTTONEAREST), &mi);
        RECT r;
        GetWindowRect(w, &r);
        return EqualRect(&r, &mi.rcMonitor) != FALSE;
    }

    void doubleClick(HWND w) { PostMessageW(w, WM_LBUTTONDBLCLK, MK_LBUTTON, MAKELPARAM(50, 50)); }

    void openThenDelete(juce::AudioPluginFormatManager& fm, const juce::PluginDescription& d, const char* label)
    {
        auto p = load(fm, d, 48000.0, 480);
        if (p == nullptr)
            return;
        HostWindow win;
        win.open(*p);
        check(runRealTime(*p, 48000.0, 6.0), juce::String(label) + ": null test with the visuals running");
        check(insideAndFilling(win.frame()), juce::String(label) + ": visuals inside the plugin window after 6 s");
        const auto t0 = juce::Time::getMillisecondCounterHiRes();
        win.close(); // a DAW deleting a track: the window goes first, then the plugin
        p.reset();
        const double ms = juce::Time::getMillisecondCounterHiRes() - t0;
        check(ms < 5000.0, juce::String(label) + ": plugin deleted with its window open in " + juce::String((int)ms) + " ms");
        check(renderWindows().empty(), juce::String(label) + ": visuals gone after delete");
    }
}

// Quit tests, one per run because each ends the process: "HostTest quit-open|quit-closed
// exit|exitprocess". The plugin is left alive (window open or closed) and the process ends the way a
// DAW might: returning through exit() (static destructors run) or ExitProcess(). The caller checks
// that the process is actually gone within a few seconds (a hang here = a phantom DAW process).
static int quitTest(juce::AudioPluginFormatManager& fm, const juce::PluginDescription& d, bool open, bool viaExitProcess)
{
    auto* p = load(fm, d, 48000.0, 480).release(); // deliberately never deleted
    if (p == nullptr)
        return 1;
    auto* win = new HostWindow(); // deliberately never deleted either
    if (open)
        win->open(*p);
    runRealTime(*p, 48000.0, 4.0);
    std::printf("quitting with the plugin alive, window %s, via %s\n", open ? "open" : "closed",
                viaExitProcess ? "ExitProcess" : "exit");
    std::fflush(stdout);
    if (viaExitProcess)
        ExitProcess(0);
    std::exit(0);
}

int main(int argc, char** argv)
{
    juce::ScopedJuceInitialiser_GUI juce;

    juce::AudioPluginFormatManager fm;
    fm.addFormat(std::make_unique<juce::VST3PluginFormat>());
    juce::OwnedArray<juce::PluginDescription> found;
    juce::VST3PluginFormat vst3;
    const auto bundle = juce::File(MDVST_VST3_DLL_DIR).getParentDirectory().getParentDirectory();
    vst3.findAllTypesForFile(found, bundle.getFullPathName());
    check(found.size() == 1, "found 1 plugin in " + bundle.getFullPathName());
    if (found.isEmpty())
        return 1;
    const auto& d = *found[0];
    std::printf("      %s by %s, %d in / %d out\n", d.name.toRawUTF8(), d.manufacturerName.toRawUTF8(),
                d.numInputChannels, d.numOutputChannels);

    if (argc >= 3 && std::strncmp(argv[1], "quit-", 5) == 0)
        return quitTest(fm, d, std::strcmp(argv[1], "quit-open") == 0, std::strcmp(argv[2], "exitprocess") == 0);

    {
        auto a = load(fm, d, 48000.0, 1024);
        auto b = load(fm, d, 96000.0, 1024);
        if (a && b)
        {
            check(nullTest(*a, 48000.0, 20.0), "null test, first copy, 48 kHz, 20 s, random block sizes");
            check(nullTest(*b, 96000.0, 20.0), "null test, second copy at the same time, 96 kHz, 20 s");
        }
    }

    {   // the plugin's window
        auto p = load(fm, d, 48000.0, 480);
        if (p == nullptr)
            return 1;
        auto* h = findParam(*p, "HQ");
        auto* s = findParam(*p, "Speed");
        check(h != nullptr && h->getValue() < 0.5f, "HQ present, off by default");
        check(s != nullptr && s->getCurrentValueAsText() == "1", "Speed present, at 1 by default");
        check(findParam(*p, "Visuals") == nullptr, "no Visuals switch (the plugin window does that)");

        runRealTime(*p, 48000.0, 1.5);
        check(renderWindows().empty(), "no visuals while the plugin window is closed (a scan opens nothing)");

        HostWindow win;
        check(win.open(*p), "the plugin has a window");
        runRealTime(*p, 48000.0, 3.0);
        check(insideAndFilling(win.frame()), "visuals inside the plugin window, filling it");
        check(win.editor->getWidth() == 640 && win.editor->getHeight() == 360,
              "first opens at 640x360 (" + juce::String(win.editor->getWidth()) + "x"
                  + juce::String(win.editor->getHeight()) + ")");

        win.editor->setSize(800, 450);
        runRealTime(*p, 48000.0, 1.0);
        check(insideAndFilling(win.frame()), "plugin window resized: the visuals follow");

        if (h != nullptr && s != nullptr)
        {
            // HQ: 30 fps off, 60 on. Measured as the process's CPU over 5 s each way (after 1 s
            // to settle). Only 1.1: the logo screen in a small window is cheap, so the gap is
            // small (6-8% vs 4-6%); the frame rate itself was traced at 30.5 / 60.0 (2026-10-29).
            auto cpuOver = [&](float hqValue)
            {
                h->setValue(hqValue);
                runRealTime(*p, 48000.0, 1.0);
                const double c0 = processCpuSeconds();
                runRealTime(*p, 48000.0, 5.0);
                return (processCpuSeconds() - c0) / 5.0 * 100.0;
            };
            const double low = cpuOver(0.0f), high = cpuOver(1.0f);
            check(high > low * 1.1, juce::String::formatted("HQ on costs more than off (%.0f%% vs %.0f%% of a core)", high, low));

            s->setValue(s->getValueForText("1/4"));
            juce::MemoryBlock state;
            p->getStateInformation(state);
            s->setValue(s->getValueForText("1"));
            h->setValue(0.0f);
            p->setStateInformation(state.getData(), (int)state.getSize());
            check(s->getCurrentValueAsText() == "1/4" && h->getValue() > 0.5f && insideAndFilling(win.frame()),
                  "Speed 1/4 and HQ on survive a save and reload; visuals still inside");
            s->setValue(s->getValueForText("1"));
            h->setValue(0.0f);
            runRealTime(*p, 48000.0, 0.5);

            // Keys in the visuals window move the device's controls: ] faster, [ slower, F3 HQ.
            auto keys = renderWindows();
            if (keys.size() == 1)
            {
                PostMessageW(keys[0], WM_CHAR, ']', 0);
                PostMessageW(keys[0], WM_KEYDOWN, VK_F3, 0);
                runRealTime(*p, 48000.0, 1.0);
                const auto faster = s->getCurrentValueAsText();
                const bool hqOn = h->getValue() > 0.5f;
                PostMessageW(keys[0], WM_CHAR, '[', 0);
                PostMessageW(keys[0], WM_CHAR, '[', 0);
                PostMessageW(keys[0], WM_KEYDOWN, VK_F3, 0);
                runRealTime(*p, 48000.0, 1.0);
                check(faster == "1.5x" && hqOn && s->getCurrentValueAsText() == "3/4" && h->getValue() < 0.5f,
                      "keys: ] and [ step Speed (1 -> " + faster + " -> " + s->getCurrentValueAsText()
                          + "), F3 toggles HQ, and the device follows");
                s->setValue(s->getValueForText("1"));
            }
        }

        auto w = renderWindows();
        if (!w.empty())
        {
            doubleClick(w[0]);
            runRealTime(*p, 48000.0, 1.5);
            w = renderWindows();
            check(w.size() == 1 && isFullScreen(w[0]), "double-click: full screen");
            if (w.size() == 1)
                doubleClick(w[0]);
            runRealTime(*p, 48000.0, 1.5);
            check(insideAndFilling(win.frame()), "double-click again: back inside the plugin window");
        }

        {   // a second copy, its window open too
            auto q = load(fm, d, 48000.0, 480);
            HostWindow win2;
            if (q != nullptr)
                win2.open(*q);
            if (q != nullptr)
                runRealTime(*q, 48000.0, 2.0);
            check(renderWindows().size() == 1, "a second copy's window adds no second visuals");
            win2.close();
        }

        // Closing the window hides and pauses the visuals; reopening brings back the same ones
        // (same window: nothing restarted, so preset, menus and settings are as they were).
        w = renderWindows();
        const HWND first = w.empty() ? nullptr : w[0];
        win.close();
        runRealTime(*p, 48000.0, 0.5);
        check(renderWindows().empty() && IsWindow(first), "closing the plugin window hides the visuals (still running)");

        win.open(*p);
        runRealTime(*p, 48000.0, 2.0);
        w = renderWindows();
        check(insideAndFilling(win.frame()) && w.size() == 1 && w[0] == first,
              "reopening it brings back the same visuals, not a restart");
        check(win.editor->getWidth() == 800 && win.editor->getHeight() == 450,
              "and at the size it was closed at (" + juce::String(win.editor->getWidth()) + "x"
                  + juce::String(win.editor->getHeight()) + ")");

        if (!w.empty())
            doubleClick(w[0]);
        runRealTime(*p, 48000.0, 1.5);
        win.close();
        runRealTime(*p, 48000.0, 1.0);
        w = renderWindows();
        check(w.size() == 1 && isFullScreen(w[0]), "full screen stays up when the plugin window closes (projector)");
        if (w.size() == 1)
            doubleClick(w[0]);
        runRealTime(*p, 48000.0, 1.5);
        check(renderWindows().empty() && IsWindow(first), "leaving full screen with no plugin window hides them");

        win.open(*p);
        runRealTime(*p, 48000.0, 2.0);
        w = renderWindows();
        check(insideAndFilling(win.frame()) && w.size() == 1 && w[0] == first,
              "and the plugin window brings the same visuals back");
        win.close();
        p.reset();
        check(renderWindows().empty() && !IsWindow(first), "visuals closed after delete");
    }

    {   // the preset saved with the set: a set naming a preset (locked) opens on it. Saved under the
        // folder's old name, presets\SwarmSynth (before 2026-10-30): it comes back from presets\seethrew.
        const auto patches = juce::File::getSpecialLocation(juce::File::userDocumentsDirectory)
                                 .getChildFile("Milk Pump/presets/seethrew/Patches");
        const auto files = patches.findChildFiles(juce::File::findFiles, false, "*.milk");
        auto p = load(fm, d, 48000.0, 480);
        if (p != nullptr && !files.isEmpty())
        {
            const juce::String savedAs = "presets\\SwarmSynth\\Patches\\" + files[0].getFileName();
            const juce::String wanted = "presets\\seethrew\\Patches\\" + files[0].getFileName();
            juce::MemoryOutputStream set;
            set.writeBool(true); // a set from before Build 17: Speed counted from 1/8
            set.writeBool(false);
            set.writeByte(4); // Speed 1 in the old seven steps
            set.writeShort(960);
            set.writeShort(540);
            set.writeString(savedAs);
            set.writeBool(true); // locked
            // The host wraps the plugin's own bytes: "VC2!" + XML, the bytes as base64 in
            // <IComponent>. Swap ours in, as a set saved with that preset would hold them.
            juce::MemoryBlock blob;
            p->getStateInformation(blob);
            auto xml = juce::AudioProcessor::getXmlFromBinary(blob.getData(), (int)blob.getSize());
            auto* comp = xml ? xml->getChildByName("IComponent") : nullptr;
            if (comp == nullptr)
            {
                check(false, "set preset: could not read the host's state format");
                return 1;
            }
            comp->deleteAllTextElements();
            comp->addTextElement(set.getMemoryBlock().toBase64Encoding());
            juce::MemoryBlock newBlob;
            juce::AudioProcessor::copyXmlToBinary(*xml, newBlob);
            p->setStateInformation(newBlob.getData(), (int)newBlob.getSize());

            HostWindow win;
            win.open(*p);
            runRealTime(*p, 48000.0, 4.0);
            juce::MemoryBlock saved, inner;
            p->getStateInformation(saved);
            if (auto x = juce::AudioProcessor::getXmlFromBinary(saved.getData(), (int)saved.getSize()))
                if (auto* c = x->getChildByName("IComponent"))
                    inner.fromBase64Encoding(c->getAllSubText());
            juce::MemoryInputStream in(inner, false);
            in.skipNextBytes(7);
            const auto now = in.readString();
            const bool locked = in.readBool();
            check(now == wanted && locked, "a set's preset comes back, locked, from the renamed folder: " + now);
            auto* sp = findParam(*p, "Speed");
            check(sp != nullptr && sp->getCurrentValueAsText() == "1",
                  "an old set's Speed 1 is still 1 with the slower steps: "
                      + (sp ? sp->getCurrentValueAsText() : juce::String("missing")));
            if (sp != nullptr)
            {
                sp->setValue(0.0f);
                runRealTime(*p, 48000.0, 0.3);
                check(sp->getCurrentValueAsText() == "1/32", "Speed goes down to 1/32");
            }
            win.close();
        }
        else
            std::printf("SKIP  set preset: no seethrew patch presets in the data folder\n");
    }

    openThenDelete(fm, d, "open #1");
    openThenDelete(fm, d, "open #2 (after a delete)");

    std::printf("%s\n", failures == 0 ? "ALL PASSED" : "FAILURES");
    return failures == 0 ? 0 : 1;
}
