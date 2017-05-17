# mysql-backup-docker

Python script to run Docker image for MySQL backups 

```
usage: backup.py [-h] [--hostfile [file]] [--backupdir [directory]]

MySQL Backup Script using Docker

optional arguments:
  -h, --help            show this help message and exit
  --hostfile [file]     YAML hostfile path - default ./hosts.yaml
  --backupdir [directory]
                        Directory where backups will be stored (created if
                        needed) - default ./backup
```
