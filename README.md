# mysql-backup-docker

Python script to run Docker image for MySQL backups 

```
usage: backup.py [-h] [--hostfile [file]] [--backupdir [directory]]
                 [--user [username]] [--verbose]

MySQL Backup Script using Docker

optional arguments:
  -h, --help            show this help message and exit
  --hostfile [file]     YAML hostfile path - default: ./hosts.yaml
  --backupdir [directory]
                        Directory where backups will be stored (created if
                        needed) - default: ./backup
  --user [username]     User who will own the backup files - default: current
                        user
  --verbose             Increase verbosity level
```
