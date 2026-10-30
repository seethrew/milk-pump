# HostTest: loads the built Milk Pump.vst3 the way a DAW does (JUCE's VST3 hosting) and checks
# pass-through, a second copy, and removing the plugin while its window is open. See main.cpp.
juce_add_console_app(HostTest PRODUCT_NAME "HostTest" VERSION 0.2.0)
target_sources(HostTest PRIVATE main.cpp)
target_compile_definitions(HostTest PRIVATE
    JUCE_PLUGINHOST_VST3=1
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    MDVST_VST3_DLL_DIR="$<TARGET_FILE_DIR:MDVST_Plugin_VST3>") # .../Milk Pump.vst3/Contents/x86_64-win
target_link_libraries(HostTest PRIVATE
    juce::juce_audio_processors
    juce::juce_recommended_config_flags
    juce::juce_recommended_warning_flags)
add_dependencies(HostTest MDVST_Plugin_VST3)
set_target_properties(HostTest PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/HostTest/$<CONFIG>")
