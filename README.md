# pyRT
pyRT is an open source standalone front-end for the linux bittorrent client `rTorrent` written in python (current in alpha testing stages)

pyRT is licensed under the GNU General Public License, Version 3
(http://www.gnu.org/licenses/gpl.txt)

# Description
pyRT is designed to run standalone, with its own HTTP server, interfacing with rTorrent via XMLRPC through a socket file.

Assuming rTorrent has been compiled with xmlrpc and scgi_local has been enabled in .rtorrent.rc, pyRT should be able to run without further requirements other than a simple configuration.

No apache set up, no confusing SCGI configuration.

Since pyRT runs off a socket file, the XMLRPC interface can be kept secure by its file permissions. Many other rTorrent frontend result in this being thrown open to other users on the same server, or even to anyone with the knownledge of which port the XMLRPC interface is listening on.


# Dependencies
Tested on python 2.7 on a linux system running funtoo
Likely not to function with python 2.6 or lower (probably fixable by replacing the `json` module with `simplejson`)
Likely not to function with python 3.0 or higher

### Server dependencies
`tornado` version 2.2.1 (http://www.tornadoweb.org/)

### Client-side dependencies (major dependencies)
Javascript-enabled browser which supports the following features:
* HTML5
    * canvas
    * canvas text API
    * drag and drop
* javascript
    * File API
    * FileReader API
    * Web Sockets
    * XMLHttpRequest (for regression if web sockets don't work)
    * JSON parsing
* CSS
    * gradients
    * position:fixed
    * box-shadow
    * border-radius (or -moz-border-radius)
    * background-image
    * multiple backgrounds

Recent versions of chrome (tested 19) and firefox (tested 11) are fully supported

# Setup
### Install `tornado` using your favourite package manager
*Debian* `apt-get install python-tornado` (Note that you must use wheezy or sid to install a sufficiently high version of tornado)

*Gentoo/Funtoo* `emerge -av www-servers/tornado` (Note that you must use the `~x86` keyword if appropriate)

or *from source*
```
wget https://github.com/downloads/facebook/tornado/tornado-2.2.1.tar.gz
tar xvzf tornado-2.2.1.tar.gz
cd tornado-2.2.1
python setup.py install
```

### Configure pyRT
Copy example config `cp config/pyrtrc.example config/.pyrtrc`

Edit configuration and save

(See Configuration below)

### Start server
Make sure rTorrent is running

Start server with `./pyrt start`

# Configuration
The configuration file `.pyrtrc` uses JSON syntax, with comments permitted.

All configuration values are contained within a single dictionary, with keys wrapped in double quotes `"`, seperated from values by a colon `:`.

Every line excepting the final line must be terminated by a comma `,`.

`rtorrent_socket`: Full path to the rTorrent socket file as defined in .rtorrent.rc

`port`: Port that pyRT will listen on

`host`: Hostname or IP address that pyRT will bind to

`ssl_certificate`: _Optional_ Full path to the SSL certificate, pyRT will run on HTTP if this is not defined

`ssl_private_key`: _Optional_ Full path to the SSL private key

`ssl_ca_certs`: _Optional_ Full path to the certificate authority file

`root_directory`: _Optional_ Root directory that disk usage will be measured for (defaults to `/`)

`logfile`: _Optional_ Relative or full path to the log file, defaults to `pyrt.log`

`password`: Hashed password for pyRT, this can be generated with the command `./pyrt mkpasswd`

