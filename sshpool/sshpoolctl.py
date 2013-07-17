# -*- coding: utf-8 -*-
"""
    sshpool.sshpoolctl
    ~~~~~~~~~~~~~~~~~~

    This module provides an interactive shell to communicate with SSH channels using RESTful API

    :copyright: (c) 2013 by Abhinav Singh.
    :license: BSD, see LICENSE for more details.
"""
import sshpool
import argparse

from .ctl import Ctl

def main():
    parser = argparse.ArgumentParser(
        description='SSHPool interactive shell v%s' % sshpool.__version__,
        epilog='Having difficulty using SSHPool? Report at: %s/issues/new' % sshpool.__homepage__
    )
    parser.add_argument('--host', default='127.0.0.1', help='SSHPool interface (default: 127.0.0.1)')
    parser.add_argument('--port', default=8877, type=int, help='SSHPool listening port (default: 8877)')
    args = parser.parse_args()
    
    try:
        ctl = Ctl(args.host, args.port)
        ctl.cmdloop()
    except KeyboardInterrupt, e:
        pass
    except Exception, e:
        print e
    
    print 'done!'

if __name__ == '__main__':
    main()
