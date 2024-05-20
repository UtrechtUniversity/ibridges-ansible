# An ansible module for iBridges

[iBridges](https://github.com/UtrechtUniversity/iBridges) is a Python package for syncing data and managing metadata on iRODS servers in a userfriendly way, developed at Utrecht University. This repository contains an Ansible module that calls iBridges to download or sync a data collection from iRODS.

Usage example:

```
$ ansible-playbook -i localhost, -c local playbook.yml
Enter iRODS password: 
Enter absolute path to irods environment file: /bla/bla/.irods/irods_environment.json
Enter path to copy from irods: ~/New Folder/testdata
Enter path to copy to locally: /tmp/plzcopyhere

PLAY [Test ibridges module] *****************************************************************************************************************************************

TASK [Gathering Facts] **********************************************************************************************************************************************
[WARNING]: Platform darwin on host localhost is using the discovered Python interpreter at /opt/homebrew/bin/python3.11, but future installation of another Python
interpreter could change the meaning of that path. See https://docs.ansible.com/ansible-core/2.15/reference_appendices/interpreter_discovery.html for more
information.
ok: [localhost]

TASK [Download testdata to localhost] *******************************************************************************************************************************
[WARNING]: Module did not set no_log for password
changed: [localhost]

PLAY RECAP **********************************************************************************************************************************************************
localhost                  : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

$ ls /tmp/plzcopyhere 
testdata
$ ls /tmp/plzcopyhere/testdata 
bunny.rtf     newlocal.txt  newremote.txt plant.rtf     sun.rtf       suns
```
