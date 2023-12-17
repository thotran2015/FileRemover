# FileRemover
For unix-based OS, schedule a cron job to run this script to remove files weekly
```
crontab -e 
Add this weekly cron job:
0 0 * * 0 /path/to/python /path/to/FileRemover/script.py
```