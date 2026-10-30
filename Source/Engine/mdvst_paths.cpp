// mdvst_paths.cpp — see mdvst_paths.h.
#include "mdvst_paths.h"

#include <shlobj.h>
#include <string>

#pragma comment(lib, "shell32.lib")

const wchar_t* MDVST_ModuleDirectory()
{
    static const std::wstring directory = []
    {
        HMODULE self = nullptr;
        GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                           reinterpret_cast<LPCWSTR>(&MDVST_ModuleDirectory), &self);
        wchar_t path[MAX_PATH] = {};
        const DWORD length = GetModuleFileNameW(self, path, MAX_PATH);
        std::wstring result(path, (length > 0 && length < MAX_PATH) ? length : 0);
        result.erase(result.find_last_of(L"\\/") + 1); // npos + 1 == 0: empty if there is no slash
        return result;
    }();
    return directory.c_str();
}

const wchar_t* MDVST_DataDirectory()
{
    static const std::wstring directory = []
    {
        std::wstring result;

        // Test hook (Tools\preset-shot.ps1): a scratch data folder instead of Documents.
        wchar_t testDir[MAX_PATH] = {};
        const DWORD n = GetEnvironmentVariableW(L"MDVST_DATA_DIR", testDir, MAX_PATH);
        if (n > 0 && n < MAX_PATH)
        {
            result = testDir;
            if (result.back() != L'\\')
                result += L'\\';
            return result;
        }

        PWSTR documents = nullptr; // follows a Documents folder moved to OneDrive or another drive
        if (SUCCEEDED(SHGetKnownFolderPath(FOLDERID_Documents, KF_FLAG_CREATE, nullptr, &documents)))
        {
            result = std::wstring(documents) + L"\\" MDVST_DATA_FOLDER_NAME L"\\";
            CreateDirectoryW(result.c_str(), nullptr);
        }
        CoTaskMemFree(documents);
        if (result.empty() || GetFileAttributesW(result.c_str()) == INVALID_FILE_ATTRIBUTES)
            result = MDVST_ModuleDirectory();
        return result;
    }();
    return directory.c_str();
}

void MDVST_RegisterDataFonts()
{
    static const bool done = []
    {
        const std::wstring dir = std::wstring(MDVST_DataDirectory()) + L"fonts\\";
        WIN32_FIND_DATAW f;
        const HANDLE find = FindFirstFileW((dir + L"*.ttf").c_str(), &f);
        if (find != INVALID_HANDLE_VALUE)
        {
            do
                AddFontResourceExW((dir + f.cFileName).c_str(), FR_PRIVATE, nullptr);
            while (FindNextFileW(find, &f));
            FindClose(find);
        }
        return true;
    }();
    (void) done;
}
