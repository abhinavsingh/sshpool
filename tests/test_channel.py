import time
import mock
import socket
import getpass
import unittest
import paramiko

from .utils import exec_command
from sshpool.channel import Channel

class TestChannel(unittest.TestCase):
    
    def test_dsn_parsing1(self):
        with self.assertRaises(AssertionError):
            chan = Channel('dummy.host')
    
    def test_dsn_parsing2(self):
        chan = Channel('dummy://dummy.host')
        self.assertEqual(chan.alias, 'dummy')
        self.assertEqual(chan.username, getpass.getuser())
        self.assertEqual(chan.password, None)
        self.assertEqual(chan.hostname, 'dummy.host')
        self.assertEqual(chan.port, 22)
    
    def test_dsn_parsing3(self):
        chan = Channel('dummy://user:pass@dummy.host:2222')
        self.assertEqual(chan.alias, 'dummy')
        self.assertEqual(chan.username, 'user')
        self.assertEqual(chan.password, 'pass')
        self.assertEqual(chan.hostname, 'dummy.host')
        self.assertEqual(chan.port, 2222)
    
    def test_ssh_host_unknown(self):
        chan = Channel.init('dummy://dummy.host', False)
        with self.assertRaises(socket.gaierror):
            chan.connect()
    
    @mock.patch('sshpool.channel.paramiko.SSHClient.connect')
    def test_ssh_bad_auth_types(self, mock_connect):
        mock_connect.side_effect = paramiko.BadAuthenticationType('Bad authentication type', ['publickey'])
        chan = Channel.init('dummy://user:pass@dummy.host', False)
        with self.assertRaises(paramiko.BadAuthenticationType):
            chan.connect()
    
    @mock.patch('sshpool.channel.paramiko.SSHClient.connect')
    def test_ssh_auth_failure(self, mock_connect):
        mock_connect.side_effect = paramiko.AuthenticationException('Authentication failed.')
        chan = Channel.init('dummy://dummy.host', False)
        with self.assertRaises(paramiko.AuthenticationException):
            chan.connect()
    
    @mock.patch('sshpool.channel.paramiko.SSHClient.connect')
    def test_ssh_connect_success(self, mock_connect):
        mock_connect.return_value = None
        chan = Channel.init('dummy://dummy.host', False)
        chan.connect()
        mock_connect.assert_called_once_with(chan.hostname, chan.port, chan.username, chan.password)
    
    @mock.patch('sshpool.channel.paramiko.SSHClient.exec_command')
    @mock.patch('sshpool.channel.paramiko.SSHClient.connect')
    def test_run_catches_ssh_exception(self, mock_connect, mock_exec_command):
        mock_connect.return_value = None
        mock_exec_command.side_effect = paramiko.SSHException()
        chan = Channel.init('dummy://dummy.host', False)
        chan.send('ls -l')
        chan.run()
        self.assertTrue(chan.outer.poll())
        self.assertEqual({'exception':'SSHException()'}, chan.recv())
    
    @mock.patch('sshpool.channel.paramiko.SSHClient.exec_command')
    @mock.patch('sshpool.channel.paramiko.SSHClient.connect')
    def test_run_catches_keyboard_irq(self, mock_connect, mock_exec_command):
        mock_connect.return_value = None
        mock_exec_command.side_effect = KeyboardInterrupt()
        chan = Channel.init('dummy://dummy.host', False)
        chan.send('ls -l')
        chan.run()
        self.assertTrue(chan.outer.poll())
        self.assertEqual({'exception':'KeyboardInterrupt()'}, chan.recv())
    
    @mock.patch('sshpool.channel.paramiko.SSHClient.exec_command')
    @mock.patch('sshpool.channel.paramiko.SSHClient.connect')
    def test_run(self, mock_connect, mock_exec_command):
        mock_connect.return_value = None
        mock_exec_command.return_value = exec_command('Hello World', '', 0)
        chan = Channel.init('dummy://dummy.host', False)
        chan.send('echo Hello World')
        chan.connect()
        chan.run_once()
        self.assertTrue(chan.outer.poll())
        rcvd = chan.recv()
        self.assertDictContainsSubset({'stdout': 'Hello World'}, rcvd)
        self.assertDictContainsSubset({'stderr': ''}, rcvd)
        self.assertDictContainsSubset({'exit_code': 0}, rcvd)
    
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
    
    def test_info(self):
        chan = Channel.init('dummy://dummy.host', False)
        info = chan.info()
        self.assertEqual(info['user'], getpass.getuser())
        self.assertEqual(info['pass'], None)
        self.assertEqual(info['host'], 'dummy.host')
        self.assertEqual(info['port'], 22)
        self.assertFalse(info['is_alive'])
    
    @mock.patch('sshpool.channel.paramiko.SSHClient.connect')
    def test_start_stop(self, mock_connect):
        mock_connect.return_value = None
        chan = Channel.init('dummy://dummy.host')
        time.sleep(0.1)
        self.assertTrue(chan.is_alive())
        self.assertDictContainsSubset({chan.alias: chan}, Channel.channels)
        chan.stop()
        time.sleep(0.1)
        self.assertTrue(not chan.is_alive())
        with self.assertRaises(KeyError):
            Channel.channels[chan.alias]
