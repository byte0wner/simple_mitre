#include <windows.h>
#include <iostream>
#include <winevt.h>
#include <regex>
#include <thread>
#include <winhttp.h>

#include "json.hpp"
#include "events.h"
#include "utils.h"

#pragma comment(lib, "wevtapi.lib")   // lib for events

using json = nlohmann::json;

OwnQueue queue;

void AnalyzeEvent(
    std::wstring xml
) {
    const int buffer_size = MAX_COMPUTERNAME_LENGTH + 1;
    char buffer[buffer_size];
    DWORD lpnSize = buffer_size;

    BOOL hResult = GetComputerNameA(buffer, &lpnSize);

    Logon current_logon {
        GetFieldByName(L"SystemTime", xml),
        GetFieldByName(L"LogonType", xml),
        GetFieldByName(L"TargetUserName", xml),
        GetFieldByName(L"TargetLogonId", xml),
        std::string(buffer),
        GetFieldByName(L"LogonProcessName", xml),
        GetFieldByName(L"ProcessName", xml),
        GetFieldByName(L"IpAddress", xml),
        GetFieldByName(L"IpPort", xml),
        GetFieldByName(L"SubjectDomainName", xml),
        GetFieldByName(L"SubjectLogonId", xml),
        GetFieldByName(L"TargetDomainName", xml),
    };

    queue.push(std::move(current_logon));
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
    LPWSTR pwsPath = L"Security";
    // Microsoft-Windows-Sysmon/Operational - proc_creation

    LPCWSTR pwsQuery = L"<QueryList>"
                       L"  <Query Id=\"0\" Path=\"Security\">"
                       L"    <Select Path=\"Security\">"
                       L"      *[System[(EventID=4624)]]"
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
    BOOL bResults = FALSE;
    HINTERNET hSession, hConnect, hRequest = NULL;

    hSession = WinHttpOpen(
        L"A WinHTTP Example Program/1.0", 
        WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
        WINHTTP_NO_PROXY_NAME, 
        WINHTTP_NO_PROXY_BYPASS,
        0
    );

    if (!hSession) {
        return 1;
    }

    hConnect = WinHttpConnect(
        hSession,
        L"127.0.0.1",
        INTERNET_DEFAULT_HTTPS_PORT,
        0
    );

    if (!hConnect) {
        WinHttpCloseHandle(hSession);
        return 1;
    }

    std::jthread gather_sender([&] (std::stop_token st) {
        Logon data;
        while(!st.stop_requested()) {
            if (queue.pop(data)) {
                json json_event;

                json_event["creation_time"] = data.creation_time;
                json_event["logon_type"] = data.logon_type;
                json_event["target_username"] = data.target_username;
                json_event["workstation_name"] = data.workstation_name;
                json_event["ip_addr"] = data.ip_addr;

                std::string json_str = json_event.dump();

                DWORD dwLength = (DWORD)json_str.size();

                hRequest = WinHttpOpenRequest( hConnect, L"POST", L"/api/events", 
                    NULL, WINHTTP_NO_REFERER, WINHTTP_DEFAULT_ACCEPT_TYPES, 0
                );

                if (!hRequest) {
                    continue;
                }

                bResults = WinHttpSendRequest( hRequest,  WINHTTP_NO_ADDITIONAL_HEADERS,
                    0, (LPVOID)json_str.c_str(), dwLength, dwLength,0
                );
            }
        }
    });
    SubscribeToEvt();
    return 0;
}