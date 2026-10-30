# Milk Pump (was "MilkDrop VST"): the VST3 shell around mdvst_engine. Audio passes through
# untouched; a copy goes to the visuals (the plugin's own window, PluginEditor.h) through a lock-free FIFO and a feeder thread
# (PluginProcessor.h).

juce_add_plugin(MDVST_Plugin
    PRODUCT_NAME "Milk Pump"
    VERSION 0.3.21 # 0.<phase>.<n>
    COMPANY_NAME "seethrew" # what DAWs list as the maker; the codes below are what they identify it by
    BUNDLE_ID com.daxy.milkpump
    PLUGIN_MANUFACTURER_CODE Daxy
    PLUGIN_CODE Mdvs # kept through the rename: Live identifies the plugin by these two codes
    FORMATS VST3
    IS_SYNTH FALSE
    NEEDS_MIDI_INPUT FALSE
    NEEDS_MIDI_OUTPUT FALSE
    IS_MIDI_EFFECT FALSE
    EDITOR_WANTS_KEYBOARD_FOCUS FALSE
    VST3_CATEGORIES Fx Analyzer
    COPY_PLUGIN_AFTER_BUILD FALSE) # Program Files\Common Files\VST3 needs admin; see CLAUDE.md

target_sources(MDVST_Plugin PRIVATE
    PluginProcessor.h PluginProcessor.cpp
    PluginEditor.h PluginEditor.cpp)

# The engine's dialogs/menus/icons go into the DLL itself (see Source/Engine/CMakeLists.txt).
target_sources(MDVST_Plugin_VST3 PRIVATE "${MDVST_ENGINE_RC}")
target_compile_definitions(MDVST_Plugin_VST3 PRIVATE MDVST_JUCE_VERSIONINFO # skip plugin.rc's VERSIONINFO
    MDVST_MILKPUMP_ICON) # and use Milk Pump's icon (Source\App\milkpump.ico), as the app does

target_compile_definitions(MDVST_Plugin PUBLIC
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_VST3_CAN_REPLACE_VST2=0)

target_link_libraries(MDVST_Plugin
    PRIVATE
        mdvst_engine
        juce::juce_audio_utils
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_warning_flags)

# Delay-load D3DX so portable_dll_loader.cpp can find it in "BeatDrop Resources\dlls\x64" beside
# the DLL (the engine's INTERFACE link option, stated again here for the final DLL).
target_link_options(MDVST_Plugin_VST3 PRIVATE "/DELAYLOAD:d3dx9_43.dll")

# Beside the DLL inside the bundle (Contents\x86_64-win): only the two D3DX DLLs, where
# portable_dll_loader.cpp looks for them. Presets, textures and settings live in the data folder
# (Documents\Milk Pump, see mdvst_paths.h), filled by install-data.ps1.
set(dlls "${MDVST_D3DX_DLLS}")
set(out "$<TARGET_FILE_DIR:MDVST_Plugin_VST3>/BeatDrop Resources/dlls/x64")
add_custom_command(TARGET MDVST_Plugin_VST3 POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory "${out}"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${dlls}/d3dx9_43.dll" "${dlls}/d3dx9_31.dll" "${out}"
    VERBATIM)
