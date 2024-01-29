# FileRemover
For unix-based OS, schedule a cron job to run the script every 5 minutes using `crontab -e `
```
*/5 * * * * /path/to/FileRemover/script.py -t path/to/trash -d path/to/cluttered/directory -a 7 > /path/to/log.txt 2>&1
```
To read more about the script's command-line parameters, run `/path/to/FileRemover/script.py -h`