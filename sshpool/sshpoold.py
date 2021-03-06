# -*- coding: utf-8 -*-
"""
    sshpool.sshpoold
    ~~~~~~~~~~~~~~~~

    This module maintain pool of SSH channels and allow communication via RESTful API

    :copyright: (c) 2013 by Abhinav Singh.
    :license: BSD, see LICENSE for more details.
"""
import sshpool
import argparse
import logging

from .channel import Channel
from .rest import HTTP

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger('sshpoold')

def main():
    parser = argparse.ArgumentParser(
        description='SSHPool daemon v%s' % sshpool.__version__,
        epilog='Having difficulty using SSHPool? Report at: %s/issues/new' % sshpool.__homepage__
    )
    parser.add_argument('--channel', default=list(), action='append', help='Channel DSN e.g. alias://user:pass@host:port. Consult %s#channel-dsn for more details.' % sshpool.__homepage__)
    parser.add_argument('--config', help='Config file path containing one channel per line')
    parser.add_argument('--host', default='127.0.0.1', help='SSHPool interface (default: 127.0.0.1)')
    parser.add_argument('--port', default=8877, type=int, help='SSHPool listening port (default: 8877)')
    args = parser.parse_args()
    
    channels = args.channel
    
    if args.config:
        try:
            channels += open(args.config, 'rb').read().strip().split()
        except IOError as e:
            logger.error(e)
    
    for channel in channels:
        Channel.init(channel)
    
    HTTP(args.host, args.port).start()
    
    for alias in Channel.channels:
        chan = Channel.channels[alias]
        chan.join()
    
    print('done!')

if __name__ == '__main__':
    main()
