#!/usr/bin/env python3
import yaml
import docker
import os
from datetime import datetime
import sys
import argparse
import pwd
import grp

parser = argparse.ArgumentParser(description='MySQL Backup Script using Docker')
parser.add_argument('--hostfile', nargs='?', metavar='file', help='YAML hostfile path - default: ./hosts.yaml', default=os.path.dirname(sys.argv[0])+"/hosts.yaml")
parser.add_argument('--backupdir', nargs='?', metavar='directory', help='Directory where backups will be stored (created if needed) - default: ./backup', default=os.path.dirname(sys.argv[0])+"/backup")
parser.add_argument('--user', nargs='?', metavar='username', help='User who will own the backup files - default: current user', default=None)
parser.add_argument('--verbose', help='Increase verbosity level', default=False, action="store_true")
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

# Get userid and groupid

uid, gid = None, None

if (args.user is not None):
    try:
        uid = pwd.getpwnam(args.user).pw_uid
        gid = grp.getgrnam(args.user).gr_gid
    except KeyError as exc:
        print ("ERROR: User not found - falling back to current user")
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
       
    filename = host["name"]+"-"+timestamp+".tar.gz"
    # write backup to the temp directory

    try: 
        cont = client.containers.get(host["name"])

        print("Backing up " + host["name"] +" to file " + path + "/" + filename )

        client.containers.run(image    = "docker-registry.vlp.cz:5000/xtrabackup", 
                          command      = [ "/bin/bash", "-c", "set -o pipefail && mkdir -p /backup/temp && innobackupex --user="+host["user"]+" --password="+host["password"]+" --host="+host["name"]+" --stream=tar /var/lib/mysql | gzip - > /backup/temp/"+filename],
                          remove       = True,
                          volumes_from = cont.id,
                          network_mode = "container:"+cont.id,
                          volumes      = {os.path.abspath(path): {'bind': '/backup', 'mode': 'rw'}}
                          )
    except Exception as exc:
        print (exc)

        try:
            os.remove(args.backupdir+"/temp/"+filename)
        except:
            pass

        try:
            os.rmdir(args.backupdir+"/temp/")
        except:
            pass

        exit(1)

    # move the file from temp directory to the actual directory

    try:
        if (args.verbose): print("Moving file from temporary directory")
        os.rename(args.backupdir+"/temp/"+filename, args.backupdir+"/"+filename)
        os.rmdir(args.backupdir+"/temp/")
    except Exception as exc:
        print(exc)
        exit(1)

    # chown the file to the desired user and group

    if (args.user is not None and uid is not None and gid is not None):
        try:
            if (args.verbose): print ("Changing owner to user \""+args.user+"\"")
            os.chown(args.backupdir+"/"+filename, uid, gid)
        except Exception as exc:
            print(exc)
            exit(1)
            
# all is done

print ("Done")