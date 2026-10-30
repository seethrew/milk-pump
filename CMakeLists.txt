cmake_minimum_required(VERSION 3.25)

# vcpkg (Tools\vcpkg) supplies projectM-eval through vcpkg.json in this folder.
if(NOT DEFINED CMAKE_TOOLCHAIN_FILE)
    set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/Tools/vcpkg/scripts/buildsystems/vcpkg.cmake")
endif()
set(VCPKG_TARGET_TRIPLET x64-windows CACHE STRING "")

project(MilkDropVST LANGUAGES C CXX RC)

if(NOT CMAKE_SIZEOF_VOID_P EQUAL 8)
    message(FATAL_ERROR "64-bit only: configure with -A x64")
endif()

# JUCE 8 (Tools\JUCE, a shallow clone of tag 8.0.16-security) for the VST3 shell.
add_subdirectory(Tools/JUCE "${CMAKE_BINARY_DIR}/JUCE" EXCLUDE_FROM_ALL)

add_subdirectory(Source/Engine)
add_subdirectory(Source/EngineTest)
add_subdirectory(Source/Plugin)
add_subdirectory(Source/HostTest)
add_subdirectory(Source/App)
