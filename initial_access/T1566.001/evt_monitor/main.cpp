#include <Windows.h>
#include <mmsystem.h>
#include <winevt.h>
#include <regex>
#include <iostream>
#include <ranges>

#pragma comment(lib, "winmm.lib")     // lib for audio
#pragma comment(lib, "wevtapi.lib")   // lib for events

// add here any suspicious images
const std::vector<std::wstring> SUSPICIOUS_IMAGES = {
    L"powershell.exe",
    L"cmd.exe",
    L"calc.exe",
};

// add here any parents
const std::vector<std::wstring> PARENTS = {
    L"WINWORD.EXE",
    L"POWERPNT.EXE",
    L"OUTLOOK.EXE",
    L"ONENOTE.EXE",
    L"MSACCESS.EXE",
    L"EXCEL.EXE",
    L"explorer.exe"
};

void TerminateProcessByID(DWORD dwProcessId) {
    HANDLE hProcess = OpenProcess(PROCESS_TERMINATE, FALSE, dwProcessId);
    if (hProcess == NULL) {
        std::wcout << "Error: Could not open process with ID " << dwProcessId << std::endl;
        return;
    }

    BOOL result = TerminateProcess(hProcess, 0);
    if (!result) {
        std::wcout << "Error: Could not terminate process with ID " << dwProcessId << std::endl;
    }

    CloseHandle(hProcess);
    return;
}

// our function that checks the XML event fields and alerts you about anything suspicious
void AnalyzeEvent(
    std::wstring xml
) {
    // get image from xml event
    std::wregex image_pattern(L"\\<Data Name='Image'\\>([^\\<]+)\\</Data\\>");
    std::wsmatch image_match;
    if (std::regex_search(xml, image_match, image_pattern)) {
        std::wcout << L"Image: " << image_match[1].str() << std::endl;
    } else {
        return;
    }

    // get parent image from xml event
    std::wregex parent_image_pattern(L"\\<Data Name='ParentImage'\\>([^\\<]+)\\</Data\\>");
    std::wsmatch parent_image_match;
    if (std::regex_search(xml, parent_image_match, parent_image_pattern)) {
        std::wcout << L"ParentImage: " << parent_image_match[1].str() << std::endl;
    } else {
        return;
    }

    // get pid from xml event
    std::wregex pid_pattern(L"\\<Data Name='ProcessId'\\>([^\\<]+)\\</Data\\>");
    std::wsmatch pid_match;
    if (std::regex_search(xml, pid_match, pid_pattern)) {
        std::wcout << L"Pid: " << pid_match[1].str() << std::endl << std::endl;
    } else {
        return;
    }

    // does image end with at least one value from SUSPICIOUS_IMAGES
    bool image_match_found = std::any_of(SUSPICIOUS_IMAGES.begin(), SUSPICIOUS_IMAGES.end(), [&](const auto& suffix) {
        return image_match[1].str().ends_with(suffix);
    });

    // does parent image end with at least one value from PARENTS
    bool parent_image_match_found = std::any_of(PARENTS.begin(), PARENTS.end(), [&](const auto& suffix) {
        return parent_image_match[1].str().ends_with(suffix);
    });

    // if the two previous conditions are true, then we notify about it
    if (image_match_found && parent_image_match_found) {
        // convert std::wstring pid top DWORD
        DWORD dwordPID = 0;
        std::wistringstream iss(pid_match[1].str());
        iss >> dwordPID;

        // terminate that process by pid
        TerminateProcessByID(dwordPID);

        PlaySound(TEXT("naiden.wav"), NULL, SND_FILENAME | SND_SYNC);

        // notify about it
        MessageBoxW(
            NULL,
            L"ПАДАЛЬ УНИЧТОЖЕНА",
            L"My Application",
            MB_OK | MB_SYSTEMMODAL
        );

        PlaySound(TEXT("poisk.wav"), NULL, SND_FILENAME | SND_ASYNC | SND_LOOP);
    }
}

// getting XML from event
// https://learn.microsoft.com/ru-ru/windows/win32/wes/rendering-events
DWORD GetEventXml(
    EVT_HANDLE hEvent
) {
    DWORD status = ERROR_SUCCESS;
    DWORD dwBufferSize = 0;
    DWORD dwBufferUsed = 0;
    DWORD dwPropertyCount = 0;
    LPWSTR pRenderedContent = NULL;

    if (!EvtRender(NULL, hEvent, EvtRenderEventXml, dwBufferSize, pRenderedContent, &dwBufferUsed, &dwPropertyCount))
    {
        if (ERROR_INSUFFICIENT_BUFFER == (status = GetLastError()))
        {
            dwBufferSize = dwBufferUsed;
            pRenderedContent = (LPWSTR)malloc(dwBufferSize);
            if (pRenderedContent)
            {
                EvtRender(NULL, hEvent, EvtRenderEventXml, dwBufferSize, pRenderedContent, &dwBufferUsed, &dwPropertyCount);
            }
            else
            {
                std::wcout << "malloc failed" << std::endl;
                status = ERROR_OUTOFMEMORY;
                goto cleanup;
            }
        }

        if (ERROR_SUCCESS != (status = GetLastError()))
        {
            std::wcout << "EvtRender failed with " << status << std::endl;
            goto cleanup;
        }
    }

    AnalyzeEvent((std::wstring)pRenderedContent);

    cleanup:
        if (pRenderedContent)
            free(pRenderedContent);

        return status;
}

// our function, which is triggered whenever a process_exec event is created
// https://learn.microsoft.com/en-us/windows/win32/wes/subscribing-to-events
DWORD WINAPI SubscriptionCallback(
    EVT_SUBSCRIBE_NOTIFY_ACTION action,
    PVOID pContext,
    EVT_HANDLE hEvent
)  {
    UNREFERENCED_PARAMETER(pContext);
    
    DWORD status = ERROR_SUCCESS;

    switch(action)
    {
        // You should only get the EvtSubscribeActionError action if your subscription flags 
        // includes EvtSubscribeStrict and the channel contains missing event records.
        case EvtSubscribeActionError:
            std::wcout << "The subscription callback received the following Win32 error";
            break;

        case EvtSubscribeActionDeliver:
            if (ERROR_SUCCESS != (status = GetEventXml(hEvent)))
            {
                goto cleanup;
            }
            break;

        default:
            std::wcout << "SubscriptionCallback: Unknown action." << std::endl;
    }

    cleanup:
        return status;
}

void SubscribeToEvt() {
    DWORD status = ERROR_SUCCESS;
    EVT_HANDLE hSubscription = NULL;
    // path to events
    LPWSTR pwsPath = L"Microsoft-Windows-Sysmon/Operational";
    // query for only process_exec events
    LPCWSTR pwsQuery = L"<QueryList>"
                       L"  <Query Id=\"0\" Path=\"Microsoft-Windows-Sysmon/Operational\">"
                       L"    <Select Path=\"Microsoft-Windows-Sysmon/Operational\">"
                       L"      *[System[(EventID=1)]]"
                       L"    </Select>"
                       L"  </Query>"
                       L"</QueryList>";

    // subscribe for this events
    // https://learn.microsoft.com/en-us/windows/win32/wes/subscribing-to-events
    hSubscription = EvtSubscribe(
        NULL,                               // Session handle (NULL for local computer)
        NULL,                               // Bookmark handle (NULL to start from oldest record)
        pwsPath,                            // Log channel name
        pwsQuery,                           // XPath query to filter events
        NULL,                               // Reserved
        NULL,                               // Context for the callback
        (EVT_SUBSCRIBE_CALLBACK)SubscriptionCallback, // Your callback function
        EvtSubscribeToFutureEvents          // Flags
    );

    std::wcout << "Subscription successful. Press any key to exit." << std::endl;

    // wait for any user keyboard input
    _getwch();

    if (hSubscription)
    {
        EvtClose(hSubscription);
    }
}

int main() {
    // start playing intro
    PlaySound(TEXT("start.wav"), NULL, SND_FILENAME | SND_SYNC);

    // start playing main sound
    PlaySound(TEXT("poisk.wav"), NULL, SND_FILENAME | SND_ASYNC | SND_LOOP);

    // main logic for events
    SubscribeToEvt();
    return 0;
}