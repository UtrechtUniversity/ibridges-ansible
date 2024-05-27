[![Run ansible-test](https://github.com/UtrechtUniversity/ibridges-ansible/actions/workflows/ansible-test.yml/badge.svg)](https://github.com/UtrechtUniversity/ibridges-ansible/actions/workflows/ansible-test.yml)
[![Run integration tests against iRODS](https://github.com/UtrechtUniversity/ibridges-ansible/actions/workflows/irods-integration.yml/badge.svg)](https://github.com/UtrechtUniversity/ibridges-ansible/actions/workflows/irods-integration.yml)

# Ansible modules for syncing data with iRODS

This collection contains Ansible modules facilitating data transfer between an Ansible target machine and an [iRODS](https://irods.org) server.

Using the main `ibridges_sync` module you can easily sync data between the iRODS server and the Ansible target machine. The main advantages of this module (compared to other ways of automating iRODS transfers with Ansible) are:

* ease of use. The `ibridges_sync` module handles login, file comparison, and upload/download in one go.
    * The alternative is to manually install the `icommands` suite and call various commands from that suite in a number of separate `ansible.builtin.command` tasks.
* security. The password you pass to the `ibridges_sync` module is never stored on disk, as it directly calls the [iBridges](https://github.com/UtrechtUniversity/ibridges) Python API.
    * When using the `icommands`, credentials typically are stored on disk. This may be undesirable, e.g. in multiuser cloud environments.

This module is based on the excellent [iBridges](https://github.com/UtrechtUniversity/ibridges) Python library.

# Installation

Requirements:

* `ansible-galaxy`
* the `ibridges` `pip` package must be installed on the Ansible target (see [below](#Usage)).

`ansible-galaxy collection install git+https://github.com/UtrechtUniversity/ibridges-ansible.git`

# Usage

First make sure that the `ibridges` Python library is available on the Ansible target machine. For example, add the following to a playbook:

```yaml
- name: Install packages
  pip:
    name: "ibridges"
```

### A note on global pip installs

The above snippet installs `ibridges` as a global pip package. Although this will likely work just fine, it is not considered best practice
as updating the global pip dependencies may cause system packages that depend on them to fail. If this is a concern, you can instead install
`ibridges` to a custom location:

```yaml
- name: Install packages
  pip:
    name: "ibridges"
   extra_args: "--target /my/custom/location"
```

If you do this, subsequent invocations of the modules provided by this collection need to point to the location where iBridges was installed
by adding the right `PYTHONPATH` to the module's environment:

```
- name: iBridges sync down
  ibridges_sync:
    mode: down
    ... # etc.
  environment:
    PYTHONPATH: /my/custom/location
```

## Module ibridges_sync

The main module provided by this collection is `ibridges_sync`, which allows you to sync a local directory with a directory on the iRODS server.

Note: sync will only work if the folder already exists on iRODS. If you want to upload a new directory, use the `ibrdiges_upload` module.

```yaml
    - name: iBridges sync up
      ibridges_sync:
        mode: up # sync from the Ansible target to the iRODS server
        env:
          irods_host: irods.foo.bar
          irods_port: 1247
          irods_user_name: rods
          irods_default_resource: "demoResc"
          irods_home: /tempZone/home/rods
          irods_zone_name: tempZone
        irods_path: "~/testfiles"
        local_path: "/tmp/test/testfiles"
        password: rodspass
      check_mode: false # check_mode: true will perform a dry run, listing paths that would be changed

    - name: iBridges sync down
      ibridges_sync:
        mode: down # sync from the iRODS server to the Ansible target
        env_file: /path/to/environment.json # instead of defining env, you can also pass the location of an environment file.
        irods_path: "~/testfiles"
        local_path: "/home/rods/testfiles"
        password: rodspass
      check_mode: false # check_mode: true will perform a dry run, listing paths that would be changed
```

## Module ibridges_upload

There is also an `ibridges_upload` module for uploading separate files or folders:

```yaml
    - name: Upload testfiles
      ibridges_upload:
        env:
          irods_host: irods.foo.bar
          irods_port: 1247
          irods_user_name: rods
          irods_default_resource: "demoResc"
          irods_home: /tempZone/home/rods
          irods_zone_name: tempZone
        irods_path: "~/testfiles" # will create the ~/testfiles directory on iRODS if it doesn not exist yet
        local_path: "/tmp/test/testfiles"
        password: rodspass
```

