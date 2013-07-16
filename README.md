SSHPool
=======

Pool of SSH channels accessible via RESTful API and command line utility

Install
-------

To install sshpool, simply:

    $ pip install sshpool

sshpoold
--------

sshpoold utility is responsible for maintaining pool of SSH channels and allow communication via RESTful API

    $ sshpoold -h
    
    usage: sshpoold [-h] [--channel CHANNEL] [--host HOST] [--port PORT]
    
    optional arguments:
      -h, --help         show this help message and exit
      --channel CHANNEL  alias://user:pass@host:port
      --host HOST        SSHPool interface (default: 127.0.0.1)
      --port PORT        SSHPool listening port (default: 8877)

Start sshpoold utility:

    $ sshpoold
    [2013-07-16 22:12:46,291]  * Running on http://127.0.0.1:8877/

Optionally, sshpoold also accepts one or more SSH channel configuration:

    $ $ sshpoold --channel=localhost://localhost
    [2013-07-16 22:14:31,325] connecting to localhost://abhinavsingh:None@localhost:22
    [2013-07-16 22:14:31,331]  * Running on http://127.0.0.1:8877/
    [2013-07-16 22:14:31,815] connected to localhost://abhinavsingh:None@localhost:22

sshpoolctl
----------

sshpoolctl provides an interactive shell to communicate with SSH channels via RESTful API

    $ sshpoolctl -h
    
    usage: sshpoolctl [-h] [--host HOST] [--port PORT]
    
    optional arguments:
      -h, --help   show this help message and exit
      --host HOST  SSHPool interface (default: 127.0.0.1)
      --port PORT  SSHPool listening port (default: 8877)

Start sshpoolctl utility:

    $ sshpoolctl 
    ==> Press Ctrl-C to exit <==
    sshpool> help
    
    Documented commands (type help <topic>):
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    exit  help  quit  run  start  status  stop

Run arbitrary shell commands:
    
    sshpool> help run
    run <alias> <cmd>   Run arbitrary commands over a channel
    
    sshpool> run localhost echo hello world
    hello world
    
    sshpool> run localhost pwd
    /Users/abhinavsingh

Start a new SSH channel:

    sshpool> help start
    start <dsn> Add a new channel
    
    sshpool> start local://localhost
    OK

View status of all SSH channels:

    sshpool> help status
    status      View status of started channels
    
    sshpool> status
    local       abhinavsingh:None@localhost:22  running 53
    localhost   abhinavsingh:None@localhost:22  running 449

Stop a SSH channel:

    sshpool> help stop
    stop <alias>    Stop an existing channel
    
    sshpool> stop localhost
    OK
    
    sshpool> status
    local       abhinavsingh:None@localhost:22  running 154
