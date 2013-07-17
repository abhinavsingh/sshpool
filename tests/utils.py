import mock
import StringIO

class TestObj(object): 
    pass

def exec_command(out, err, code):
    stdin = StringIO.StringIO()
    stdin.write('')
    stdin.seek(0)
    
    stdout = StringIO.StringIO()
    stdout.channel = TestObj()
    stdout.channel.recv_exit_status = mock.MagicMock(return_value=code)
    stdout.write(out)
    stdout.seek(0)
    
    stderr = StringIO.StringIO()
    stderr.write('')
    stderr.seek(0)
    
    return stdin, stdout, stderr
