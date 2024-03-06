## About

The package implements dev-ops command line programs.

## Programs

Make sure the venv is activated.

Activation example (may differ from your case):
```commandline
source venv/Scripts/activate
```

### update_storage

The program updates the storage.  
It's recommended to run it and then start the application.

Usage:
```commandline
py -m devops_cli.update_storage "/tmp/pwned-storage" -m -c 64
```
In this example, storage resources will be located in ***/tmp/pwned-storage***, and a mocked Pwned requester will be used for making requests from 64 coroutines.
