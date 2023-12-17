# FileRemover
For unix-based OS, schedule a cron job to run the script at 10pm every Sunday using `crontab -e `
```
0 22 * * 0 /path/to/python /path/to/FileRemover/script.py
```