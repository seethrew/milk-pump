# The Milk Pump app (Milk Pump.exe): the engine in its own window, reacting to whatever the PC is
# playing (WASAPI loopback, Loopback.cpp). Same data folder as the plugin (Documents\Milk Pump).
add_executable(MilkPumpApp WIN32 main.cpp Loopback.h Loopback.cpp "${MDVST_ENGINE_RC}")
target_link_libraries(MilkPumpApp PRIVATE mdvst_engine ole32)
# Its icon: milkpump.ico here (Tools\make-icon.ps1), which plugin.rc takes in place of BeatDrop's.
target_compile_definitions(MilkPumpApp PRIVATE MDVST_MILKPUMP_ICON)
set_target_properties(MilkPumpApp PROPERTIES
    OUTPUT_NAME "Milk Pump"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/App/$<CONFIG>")

# The two D3DX DLLs where the engine looks for them, as for the plugin and EngineTest.
set(dlls "${MDVST_D3DX_DLLS}")
set(out "$<TARGET_FILE_DIR:MilkPumpApp>/BeatDrop Resources/dlls/x64")
add_custom_command(TARGET MilkPumpApp POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory "${out}"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${dlls}/d3dx9_43.dll" "${dlls}/d3dx9_31.dll" "${out}"
    VERBATIM)
