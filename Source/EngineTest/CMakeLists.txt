# EngineTest: Phase 1 check that the static engine runs on pushed audio (no loopback).
add_executable(EngineTest WIN32 main.cpp "${MDVST_ENGINE_RC}")
target_link_libraries(EngineTest PRIVATE mdvst_engine)
set_target_properties(EngineTest PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/EngineTest/$<CONFIG>")

# The D3DX DLLs beside the exe, as for the plugin. Presets, textures and settings come from the
# same data folder as the plugin (Documents\Milk Pump, filled by install-data.ps1), so
# EngineTest shares the plugin's settings.
set(dlls "${MDVST_D3DX_DLLS}")
set(out "$<TARGET_FILE_DIR:EngineTest>/BeatDrop Resources/dlls/x64")
add_custom_command(TARGET EngineTest POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory "${out}"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${dlls}/d3dx9_43.dll" "${dlls}/d3dx9_31.dll" "${out}"
    VERBATIM)
