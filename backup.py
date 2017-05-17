#!/usr/bin/env python3
import yaml
import docker
import os
from datetime import datetime
import sys
import argparse

parser = argparse.ArgumentParser(description='MySQL Backup Script using Docker')
parser.add_argument('--hostfile', nargs='?', metavar='file', help='YAML hostfile path - default ./hosts.yaml', default=os.path.dirname(sys.argv[0])+"/hosts.yaml")
parser.add_argument('--backupdir', nargs='?', metavar='directory', help='Directory where backups will be stored (created if needed) - default ./backup', default=os.path.dirname(sys.argv[0])+"/backup")
args = parser.parse_args()


#Try to open and parse the hostfile

try:
    with open(args.hostfile, 'r') as hostfile:
        try: 
            hosts = yaml.load(hostfile)
        except yaml.YAMLError as exc:
            print(exc)
            exit(1)
except Exception as exc:
    print(exc)
    exit(1)
    

#Check if the outputdir exists and create it if necessary

try:
    path = args.backupdir.rstrip("/")
    if (not os.path.isdir(path)):
        try:
            os.makedirs(path)
        except Exception as e:
            print(e)
            exit(1)
except Exception as exc:
    print(exc)
    exit(1)


# Get the Docker environment

try:
    client = docker.from_env()
except Exception as exc:
    print(exc)


#One timestamp to rule them all

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")


# For every DB host run Docker container and back up the DB

for host in hosts:    
    try: 
        cont = client.containers.get(host["name"])

        print("Backing up " + host["name"] +" to file "+path+"/" + host["name"] + "-" + timestamp + ".tar.gz" )

        client.containers.run(image        = "docker-registry.vlp.cz:5000/xtrabackup", 
                          command      = [ "/bin/sh", "-c", "innobackupex --user="+host["user"]+" --password="+host["password"]+" --host="+host["name"]+" --stream=tar /var/lib/mysql | gzip - > /backup/"+host["name"]+"-"+timestamp+".tar.gz"],
                          remove       = True,
                          volumes_from = cont.id,
                          network_mode = "container:"+cont.id,
                          volumes      = {os.path.abspath(path): {'bind': '/backup', 'mode': 'rw'}}
                          )

    except Exception as exc:
        print (exc)
