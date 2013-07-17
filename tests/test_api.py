import time
import mock
import json
import unittest

from .utils import TestObj
from sshpool.rest import API, HTTP

class TestAPI(unittest.TestCase):
    
    def setUp(self):
        self.http = HTTP('127.0.0.1', 8877)
        self.http.web.config['TESTING'] = True
        self.app = self.http.web.test_client()
    
    def test_alias_not_found(self):
        r = self.app.get('/channels/non-existent-alias')
        self.assertEqual(r.status_code, 404)
    
    def test_add_channel_failure(self):
        r = self.app.post('/channels', data='invalid-dsn-string')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data, 'BAD REQUEST')
    
    # NOTE: patch exec_command before process start for test_execute_cmd_success
    @mock.patch('sshpool.rest.Channel.exec_command')
    @mock.patch('sshpool.rest.Channel.connect')
    def test_add_channel_success(self, mock_connect, mock_exec_command):
        mock_connect.return_value = None
        mock_exec_command.return_value = 'Hello World', '', 0
        r = self.app.post('/channels', data='dummy://dummy.host')
        self.assertEqual(r.data, 'OK')
        self.assertEqual(r.status_code, 200)
        r = self.app.get('/channels/dummy')
        self.assertEqual(r.status_code, 200)
        resp = json.loads(r.data)
        self.assertDictContainsSubset({'host':'dummy.host'}, resp)
        self.assertDictContainsSubset({'is_alive':True}, resp)
    
    def test_channel_list(self):
        r = self.app.get('/channels')
        self.assertEqual(r.status_code, 200)
        resp = json.loads(r.data)
        self.assertEqual(resp.keys(), ['dummy'])
    
    def test_execute_cmd_failure(self):
        r = self.app.post('/channels/non-existent-alias', 'echo Hello World')
        self.assertEqual(r.status_code, 404)
    
    def test_execute_cmd_success(self):
        r = self.app.post('/channels/dummy', 'echo Hello World')
        self.assertEqual(r.status_code, 200)
        resp = json.loads(r.data)
        self.assertEqual(resp['stdout'], 'Hello World')
    
    def test_stop_channel_failure(self):
        r = self.app.delete('/channels/non-existent-alias')
        self.assertEqual(r.status_code, 404)
    
    def test_stop_channel_success(self):
        r = self.app.delete('/channels/dummy')
        self.assertEqual(r.status_code, 200)
