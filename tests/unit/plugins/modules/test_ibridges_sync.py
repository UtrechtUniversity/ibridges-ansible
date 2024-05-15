import json
import unittest
import copy

from unittest.mock import patch
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes
from plugins.modules import ibridges_sync

DEFAULT_ARGS = {
    'irods_path': '/test',
    'local_path': '/tmp/',
    'password': 'test',
}  # This includes only required arguments


class MockedSession():
    def __init__(self, **kwargs):
        self.irods_env = 'test'
        self.irods_home = '/test'
        self.password = 'password'
        self.irods_session = 'mocked'


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    if not args:
        args = DEFAULT_ARGS
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


def setup_sync(check_mode=False, **kwargs):
    args = copy.deepcopy(DEFAULT_ARGS)
    args['env'] = {
        'irods_host': 'nowhere'
    }
    args['_ansible_check_mode'] = check_mode
    args = dict(**args, **kwargs)
    set_module_args(args)
    return args


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class TestiBridgesSync(unittest.TestCase):

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def test_module_fail_when_required_args_missing(self):
        for arg in DEFAULT_ARGS.keys():
            with self.assertRaises(AnsibleFailJson):
                args = copy.deepcopy(DEFAULT_ARGS)
                args.pop(arg)
                set_module_args(args)
                ibridges_sync.main()

    @patch('ibridges.sync_data')
    @patch('ibridges.Session')
    def test_sync_down(self, mocked_session, mocked_sync):
        mocked_session.return_value = MockedSession()
        mocked_sync.return_value = {
            'changed_files': ['foo'],
            'changed_folders': ['bar']
        }

        args = setup_sync()

        with self.assertRaises(AnsibleExitJson) as context:
            ibridges_sync.main()

        expectation = {
            'changed': True,
            'msg': '',
            'stdout': '',
            'stdout_lines': [''],
            'changed_files': ['foo'],
            'changed_folders': ['bar']
        }
        self.assertEqual(context.exception.args[0], expectation)

        mocked_sync.assert_called()
        call = mocked_sync.mock_calls[0]

        self.assertEqual(call.kwargs['source'].absolute_path(), args['irods_path'])

        expectations = {
            'target': args['local_path'],
            'dry_run': False,
            'max_level': None,
            'copy_empty_folders': True
        }
        for expectation in expectations.items():
            self.assertEqual(call.kwargs[expectation[0]], expectation[1])

    @patch('ibridges.sync_data')
    @patch('ibridges.Session')
    def test_sync_up(self, mocked_session, mocked_sync):
        mocked_session.return_value = MockedSession()
        mocked_sync.return_value = {
            'changed_files': [],
            'changed_folders': []
        }

        args = setup_sync(mode='up')

        with self.assertRaises(AnsibleExitJson) as context:
            ibridges_sync.main()

        expectation = {
            'changed': False,
            'msg': '',
            'stdout': '',
            'stdout_lines': [''],
            'changed_files': [],
            'changed_folders': []
        }
        self.assertEqual(context.exception.args[0], expectation)

        mocked_sync.assert_called()
        call = mocked_sync.mock_calls[0]

        self.assertEqual(call.kwargs['source'], args['local_path'])
        self.assertEqual(call.kwargs['target'].absolute_path(), args['irods_path'])

    @patch('ibridges.sync_data')
    @patch('ibridges.Session')
    def test_sync_dry_run(self, mocked_session, mocked_sync):
        mocked_session.return_value = MockedSession()
        mocked_sync.return_value = {
            'changed_files': ['foo'],
            'changed_folders': ['bar']
        }

        args = setup_sync(check_mode=True)

        with self.assertRaises(AnsibleExitJson) as context:
            ibridges_sync.main()

        expectation = {
            'changed': False,
            'msg': 'Executed iBridges dry run.',
            'stdout': '',
            'stdout_lines': [''],
            'changed_files': ['foo'],
            'changed_folders': ['bar']
        }
        self.assertEqual(context.exception.args[0], expectation)
