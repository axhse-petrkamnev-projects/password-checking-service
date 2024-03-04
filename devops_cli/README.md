## About

The package implements dev-ops command line programs.

## Programs

### update_storage

The program updates the storage.  
It's recommended to run it and then start the application.

Usage:
```commandline
py -m devops_cli.update_storage -r "/tmp/pwned-storage" -f 4096 -b 2 -m
```
In this example, storage resources will be located in ***/tmp/pwned-storage***, password leak data will be stored in 4096 files and leak occasions will be stored as 2-byte (short) unsigned number.

