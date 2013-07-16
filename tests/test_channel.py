import time
import mock
import socket
import getpass
import unittest
import paramiko
import StringIO
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
        self.assertEqual(chan.recv(), 'SSHException()')
    
    @mock.patch('sshpool.channel.paramiko.SSHClient.exec_command')
    @mock.patch('sshpool.channel.paramiko.SSHClient.connect')
    def test_run_catches_keyboard_irq(self, mock_connect, mock_exec_command):
        mock_connect.return_value = None
        mock_exec_command.side_effect = KeyboardInterrupt()
        chan = Channel.init('dummy://dummy.host', False)
        chan.send('ls -l')
        chan.run()
        self.assertTrue(chan.outer.poll())
        self.assertEqual(chan.recv(), 'KeyboardInterrupt()')
    
    @mock.patch('sshpool.channel.paramiko.SSHClient.exec_command')
    @mock.patch('sshpool.channel.paramiko.SSHClient.connect')
    def test_run(self, mock_connect, mock_exec_command):
        mock_connect.return_value = None
        stdin = StringIO.StringIO()
        stdin.write('')
        stdin.seek(0)
        stdout = StringIO.StringIO()
        stdout.write('Hello World')
        stdout.seek(0)
        stderr = StringIO.StringIO()
        stderr.write('')
        stderr.seek(0)
        mock_exec_command.return_value = stdin, stdout, stderr
        chan = Channel.init('dummy://dummy.host', False)
        chan.send('echo Hello World')
        chan.connect()
        chan.run_once()
        time.sleep(0.1)
        self.assertTrue(chan.outer.poll())
        self.assertEqual(chan.recv(), 'Hello World')
        time.sleep(0.1)
    
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
        self.assertEqual(info['username'], getpass.getuser())
        self.assertEqual(info['password'], None)
        self.assertEqual(info['hostname'], 'dummy.host')
        self.assertEqual(info['port'], 22)
        self.assertFalse(info['is_alive'])
