A dumb tool based on windows event logs for monitoring the launch of suspicious processes. Here the definition of a malicious process is primitive - if `ParentImage` and `Image` are included in a certain list (check `const` in `main.cpp`), then such a process is terminated

requirements:
- install sysmon https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
- compile with  `g++ main.cpp -o <some_name>.exe -lwinmm -lwevtapi -static`
- run as admin

useful links:
- https://learn.microsoft.com/en-us/windows/win32/api/winevt/nf-winevt-evtsubscribe
- https://learn.microsoft.com/en-us/windows/win32/wes/subscribing-to-events
- https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
- https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventid=90001