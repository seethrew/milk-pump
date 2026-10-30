// mdvst_controls.h — the Speed steps, shared by the plugin (its Speed parameter) and the app
// (its [ / ] keys), so both offer the same choices.
#pragma once

// 1/16 and 1/32 came in Build 17 (Daxy: "even slower"), ahead of the old seven steps, so an
// index saved before then is 2 lower (kMdvstSpeedOldOffset).
constexpr int kMdvstSpeedCount = 9;
constexpr int kMdvstSpeedDefault = 6; // 1
constexpr int kMdvstSpeedOldOffset = 2;
inline const wchar_t* const kMdvstSpeedNames[kMdvstSpeedCount] = { L"1/32", L"1/16", L"1/8", L"1/4", L"1/2", L"3/4", L"1", L"1.5x", L"2x" };
inline const float kMdvstSpeeds[kMdvstSpeedCount] = { 0.03125f, 0.0625f, 0.125f, 0.25f, 0.5f, 0.75f, 1.0f, 1.5f, 2.0f };
