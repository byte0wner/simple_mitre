#include <iostream>
#include <queue>
#include <iostream>
#include <mutex>
#include <condition_variable>
#include <stop_token>
#include <windows.h>

// Struct for Logon
struct Logon {
    std::string creation_time;         // SystemTime
    std::string logon_type;            // LogonType
    std::string target_username;       // TargetUserName
    std::string target_logon_id;       // TargetLogonId (both events)
    std::string workstation_name;      // WorkstationName
    std::string logon_process_name;    // LogonProcessName
    std::string process_name;          // ProcessName
    std::string ip_addr;               // IpAddress
    std::string port;                  // IpPort
    std::string subject_domain_name;   // SubjectDomainName
    std::string subject_logon_id;      // SubjectLogonId
    std::string target_domain_name;    // TargetDomainName
};

class OwnQueue {
    private:
        mutable std::mutex mutex;
        std::queue<Logon> q;
        std::condition_variable cv;

    public:
        void push(Logon&& data) {
            std::lock_guard<std::mutex> lock_guard(mutex);
            q.push(std::move(data));
            cv.notify_one();
        }

        bool pop(Logon & data) {
            std::unique_lock<std::mutex> lock(mutex);
            cv.wait(lock, [&]{ return !q.empty(); });
            if (q.empty()) return false;

            data = std::move(q.front());
            q.pop();
            return true;
        }
};

std::string GetFieldByName(std::wstring field_name, std::wstring & xml);