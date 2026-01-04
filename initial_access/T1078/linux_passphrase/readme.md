# wtf is this

linux pam module example that requests the secret phrase. made for additional verification after entering the password. to log in successfully, you need to enter the password and the answer to the question.

# TESTED ONLY ON LINUX MINT WITH LIGHTDM DISPLAY MANAGER

# how to compile module

```
gcc -fPIC -c pam_phrase.c -o pam_phrase.o
ld -x --shared -o pam_phrase.so pam_phrase.o
```

# how to connect module

1. place module to PAM folder (on mint - `/lib/x86_64-linux-gnu/security`)
2. go to `/etc/pam.d/` folder (this folder contains all pam configurations)
3. im using `common-auth`, so write in `Additional Block` in this file string like this

```
auth	required			pam_phrase.so
```


# THIS WILL AFFECT ALL LOGONS (INTERACTIVE, CONSOLE, ETC...) LAUNCH ONLY IN VM