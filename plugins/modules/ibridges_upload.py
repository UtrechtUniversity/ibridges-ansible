#!/usr/bin/python
# Copyright: (c) 2024, Utrecht University
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: ibridges_upload

short_description: Download or sync files from an iRODS server using iBridges.

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "0.0.1"

description: Upload files to an iRODS server using iBridges. Also see the iBridges documentation for specific parameters.

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
        type: dict
    password:
        description: The password to use to connect to iRODS.
        required: true
        type: str

author:
    - Dawa Ometto (@dometto)
'''

EXAMPLES = r'''
# Pass in a message
- name: Sync an iRODS path to a local path
  uusrc.ibridges_upload:
    env_file: /home/user/.irods/irods_environment.json
    irods_path: ResearchData/testdata
    local_path: /tmp/test
    password: letmein

# Sync a local path to an iRODS path
- name: Sync an iRODS path to a local path
  uusrc.ibridges_sync:
    env_file: /home/user/.irods/irods_environment.json
    irods_path: ResearchData/testdata
    local_path: /tmp/test
    password: letmein
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
        env=dict(type='dict', required=False),
        env_file=dict(type='str', required=False, default="~/.irods/irods_environment.json"),
        password=dict(type='str', required=True, no_log=True),
    )

    # seed the result dict in the object
    result = dict(
        changed=False,
        msg='',
        stdout=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )
    try:
        from ibridges import Session, upload, IrodsPath
    except ImportError:
        module.fail_json(msg="Please install the 'ibridges' python package.", changed=False)

    from pathlib import Path
    if module.params['env']:
        session = Session(irods_env=module.params['env'], password=module.params['password'])
    elif module.params['env_file']:
        session = Session(irods_env_path=module.params['env_file'], password=module.params['password'])
    else:
        module.fail_json(msg='Neither env nor env_file were specified, do not know how to continue.', changed=False)

    try:
        source = module.params['local_path']
        target = IrodsPath(session, module.params['irods_path'])

        from contextlib import redirect_stdout, redirect_stderr
        from io import StringIO
        ibridges_stdout = StringIO()
        ibridges_stderr = StringIO()

        with redirect_stdout(ibridges_stdout):
            with redirect_stderr(ibridges_stderr):
                upload_result = upload(
                    session=session,
                    local_path=source,
                    irods_path=target,
                )
    except Exception as e:
        module.fail_json(msg='Encountered an error when executing iBridges upload: {}'.format(repr(e)), changed=False)

    result['changed'] = True

    result['stdout'] = ibridges_stdout.getvalue()
    result['stdout_lines'] = result['stdout'].split("\n")

    result['stderr'] = ibridges_stderr.getvalue()
    result['stderr_lines'] = result['stderr'].split("\n")

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
