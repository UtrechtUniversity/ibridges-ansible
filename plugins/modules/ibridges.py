# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: ibridges

short_description: Download or sync files from an iRODS server using iBridges.

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "0.0.1"

description: Download or sync files from an iRODS server using iBridges. Also see the iBridges documentation for specific parameters.

options:
    irods_path:
        description: The path on the iRODS instance to be downloaded or synced to.
        required: true
        type: str
    local_path:
        description: The local path (on the Ansible target) to be copied to or synced from.
        required: true
        type: str
    env_file:
        description: The local path (on the Ansible target) to read the iRODS environment file from.
        required: false
        type: str
        default: ~/.irods/irods_environment.json
    env:
        description: A dictionary containing all the information about your iRODS environment.
        required: false
        type: str
    password:
        description: The password to use to connect to iRODS.
        required: true
        type: str
    mode:
        description: What should be done with the data. Valid values are 'sync_up', 'sync_down', 'get'.
        required: false
        type: str
        default: get
    ignore_checksum:
        description: Should checksums be ignored when deciding which files should be synced?
        required: false
        type: bool
        default: False
    copy_empty_folders:
        description: Should empty folders be skipped?
        required: false
        type: bool
        default: True
    max_level:
        description: In sync mode, how many directory levels deep should files be synced? Default (0) means no maximum.
        required: false
        type: int
        default: 0

author:
    - Dawa Ometto (@dometto)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  my_namespace.my_collection.my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_namespace.my_collection.my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_namespace.my_collection.my_test:
    name: fail me
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''

from ansible.module_utils.basic import AnsibleModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        irods_path=dict(type='str', required=True),
        local_path=dict(type='str', required=True),
        env=dict(type='str', required=False),
        mode=dict(type='str', required=False, default='get'),
        env_file=dict(type='str', required=False, default="~/.irods/irods_environment.json"),
        password=dict(type='str', required=True, no_log=True),
        max_level=dict(type='int', required=False, default=0),
        ignore_checksum=dict(type='bool', required=False, default=False),
        copy_empty_folders=dict(type='bool', required=False, default=True),
    )

    # seed the result dict in the object
    result = dict(
        changed=False,
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True  # !!
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    from ibridges import Session
    from pathlib import Path
    if module.params['env']:
        session = Session(irods_env=module.params['env'], password=module.params['password'])
    elif module.params['env_file']:
        session = Session(irods_env_path=module.params['env_file'], password=module.params['password'])
    else:
        module.fail_json(msg='Neither env nor env_file were specified, do not know how to continue.', **result)

    if module.params['mode'] == 'get':
        from ibridges import download
        download(session, module.params['irods_path'], module.params['local_path'])
    else:
        from ibridges import sync_data, IrodsPath
        locations = (module.params['local_path'], IrodsPath(session, module.params['irods_path']))

        if module.params['mode'] == 'sync_up':
            source = locations[0]
            target = locations[1]
        else:
            source = locations[1]
            target = locations[0]

        sync_data(
            session=session,
            source=source,
            target=target,
            max_level=None if module.params['max_level'] == 0 else module.params['max_level'],
            ignore_checksum=module.params['ignore_checksum'],
            copy_empty_folders=module.params['copy_empty_folders'],
            dry_run=False,
        )

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    # if module.params['name'] == 'fail me':
    #     module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
