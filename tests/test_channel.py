import unittest
import getpass
import socket
import mock
import paramiko
from sshpool.channel import Channel

class TestChannel(unittest.TestCase):
    
    def test_dsn_parsing1(self):
        with self.assertRaises(AssertionError):
            chan = Channel('localhost')
    
    def test_dsn_parsing2(self):
        chan = Channel('localhost://localhost')
        self.assertEqual(chan.alias, 'localhost')
        self.assertEqual(chan.username, getpass.getuser())
        self.assertEqual(chan.password, None)
        self.assertEqual(chan.hostname, 'localhost')
        self.assertEqual(chan.port, 22)
    
    def test_dsn_parsing2(self):
        chan = Channel('localhost://localhost')
        self.assertEqual(chan.alias, 'localhost')
        self.assertEqual(chan.username, getpass.getuser())
        self.assertEqual(chan.password, None)
        self.assertEqual(chan.hostname, 'localhost')
        self.assertEqual(chan.port, 22)
    
    def test_dsn_parsing3(self):
        chan = Channel('localhost://user:pass@localhost:2222')
        self.assertEqual(chan.alias, 'localhost')
        self.assertEqual(chan.username, 'user')
        self.assertEqual(chan.password, 'pass')
        self.assertEqual(chan.hostname, 'localhost')
        self.assertEqual(chan.port, 2222)
    
    def test_ssh_host_unknown(self):
        chan = Channel.init('dummy://dummy.host', False)
        with self.assertRaises(socket.gaierror):
            chan.connect()
    
    @mock.patch('sshpool.channel.paramiko.SSHClient.connect')
    def test_ssh_auth_failure(self, mock_connect):
        mock_connect.side_effect = paramiko.AuthenticationException('Authentication failed.')
        chan = Channel.init('dummy://dummy.host', False)
        with self.assertRaises(paramiko.AuthenticationException):
            chan.connect()
    
    @mock.patch('sshpool.channel.paramiko.SSHClient.connect')
    def test_ssh_bad_auth_types(self, mock_connect):
        mock_connect.side_effect = paramiko.BadAuthenticationType('Bad authentication type', ['publickey'])
        chan = Channel.init('dummy://user:pass@dummy.host', False)
        with self.assertRaises(paramiko.BadAuthenticationType):
            chan.connect()
    
    @mock.patch('sshpool.channel.paramiko.SSHClient.connect')
    def test_ssh_connect_success(self, mock_connect):
        mock_connect.return_value = None
        chan = Channel.init('dummy://dummy.host', False)
        chan.connect()
        mock_connect.assert_called_once_with(chan.hostname, chan.port, chan.username, chan.password)
    
    def test_send(self):
        chan = Channel.init('dummy://dummy.host', False)
        chan.send('ls -l')
        self.assertTrue(chan.inner.poll())
        self.assertEqual(chan.inner.recv(), 'ls -l')
    
    def test_recv(self):
        chan = Channel.init('dummy://dummy.host', False)
        chan.inner.send('ls -l')
        self.assertTrue(chan.outer.poll())
        self.assertEqual(chan.recv(), 'ls -l')
