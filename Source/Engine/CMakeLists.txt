# mdvst_engine: the BeatDrop (MilkDrop 2) engine as a static library, plugin mode.
#
# Mirrors vis_milk2/plugin.vcxproj (Release_x64) from upstream, with MDVST_PLUGIN defined:
#   - no WASAPI loopback (audio/loopback-capture, audiodevicehandler, prefs left out of the build)
#   - no WinMain; host entry points in mdvst_engine.h
#   - no SMTC now-playing (upstream's own _WIN10_BUILD switch is simply not defined)
#   - no lyrics network access, no Desktop Mode, no system-wide hotkey
#   - MDVST_NO_FFMPEG: no video-file textures (GIF via WIC and Spout input stay)
# Webcam stays (Daxy, 2026-10-28). grep -rn "MDVST:" lists every engine edit.

find_package(projectM-Eval REQUIRED COMPONENTS Milkdrop)

set(MDVST_DXSDK_DIR "${CMAKE_SOURCE_DIR}/Tools/DXSDK" CACHE PATH
    "D3DX9 headers + Lib/x64 (Microsoft.DXSDK.D3DX NuGet package, laid out like the June 2010 SDK)")

set(V vis_milk2)
add_library(mdvst_engine STATIC
    mdvst_engine.h
    mdvst_audio.cpp
    mdvst_paths.h
    mdvst_paths.cpp
    ${V}/AMDDetection.cpp
    ${V}/dxcontext.cpp
    ${V}/fft.cpp
    ${V}/menu.cpp
    ${V}/MediaTexture.cpp
    ${V}/webcam.cpp
    ${V}/Milkdrop2PcmVisualizer.cpp
    ${V}/milkdropfs.cpp
    ${V}/portable_dll_loader.cpp
    ${V}/plugin.cpp
    ${V}/pluginshell.cpp
    ${V}/songtitlegetter.cpp
    ${V}/lyrics_editor.cpp
    ${V}/lyrics_manager.cpp
    ${V}/lyrics_renderer.cpp
    ${V}/state.cpp
    ${V}/support.cpp
    ${V}/texmgr.cpp
    ${V}/textmgr.cpp
    ${V}/utility.cpp
    ${V}/wasabi.cpp
    audio/audiobuf.cpp
    audio/guid.cpp
    audio/log.cpp
    spoutDX9/SpoutCopy.cpp
    spoutDX9/SpoutDX9.cpp
    spoutDX9/SpoutFrameCount.cpp
    spoutDX9/SpoutSenderNames.cpp
    spoutDX9/SpoutSharedMemory.cpp
    spoutDX9/SpoutUtils.cpp
)

# Dialogs, menus, strings and icons. A .res cannot live in a .lib, so each final binary (the
# plugin DLL, EngineTest.exe) adds this file to its own sources. Not an INTERFACE source: JUCE's
# plugin targets link through an intermediate static library, where it would be lost.
set(MDVST_ENGINE_RC "${CMAKE_CURRENT_SOURCE_DIR}/${V}/plugin.rc" CACHE INTERNAL "")
# The two D3DX DLLs every final binary ships beside itself: d3dx9_43.dll (Microsoft.DXSDK.D3DX) and
# d3dx9_31.dll (the DirectX End-User Runtime, June 2010), both Microsoft redistributables. setup.ps1
# puts them here.
set(MDVST_D3DX_DLLS "${CMAKE_SOURCE_DIR}/Tools/redist/x64" CACHE PATH "Folder holding d3dx9_43.dll and d3dx9_31.dll (x64)")
foreach(dll d3dx9_43.dll d3dx9_31.dll)
    if(NOT EXISTS "${MDVST_D3DX_DLLS}/${dll}")
        message(FATAL_ERROR "${MDVST_D3DX_DLLS}/${dll} is missing: run setup.ps1 first")
    endif()
endforeach()

target_include_directories(mdvst_engine
    PUBLIC  "${CMAKE_CURRENT_SOURCE_DIR}"
    PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/${V}" "${CMAKE_CURRENT_SOURCE_DIR}/audio"
            "${CMAKE_CURRENT_SOURCE_DIR}/ns-eel2-shim"
            "${MDVST_DXSDK_DIR}/Include")

# Upstream: MultiByte character set, C++17, /W3, /wd4996, /Zc:forScope-, /O1 (MinSpace).
# PRIVATE: mdvst_engine.h needs none of these, and _MBCS must not reach JUCE (a UNICODE build).
target_compile_definitions(mdvst_engine PRIVATE
    MDVST_PLUGIN MDVST_NO_FFMPEG
    WIN32 _WINDOWS _MBCS USE_VIS_HDR_HWND STRSAFE_NO_DEPRECATE NSEEL_REENTRANT_EXECUTION
    _CRT_SECURE_NO_WARNINGS _CRT_NON_CONFORMING_SWPRINTFS)
target_compile_features(mdvst_engine PUBLIC cxx_std_17)
target_compile_options(mdvst_engine PRIVATE /W3 /wd4996 /Zc:forScope- $<$<CONFIG:Release>:/O1 /Ob2 /Oy>)

target_link_libraries(mdvst_engine PUBLIC
    projectM::ns-eel2
    "${MDVST_DXSDK_DIR}/Lib/x64/d3dx9.lib"
    d3d9 winhttp bcrypt dbghelp winmm shlwapi windowscodecs ole32 oleaut32 strmiids
    delayimp)

# portable_dll_loader.cpp hooks the delay-load of d3dx9_43.dll to find it in
# "BeatDrop Resources\dlls\x64" (upstream DelayLoadDLLs, minus the FFmpeg DLLs).
target_link_options(mdvst_engine INTERFACE "/DELAYLOAD:d3dx9_43.dll")
