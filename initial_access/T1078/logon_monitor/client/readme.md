1. get logon events from etw
2. extract only useful info from etwevent
3. save to queue
4. get event from queue
5. convert to json
6. send to server via http
7. repeat

start this via service (before all user logons)