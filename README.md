ircbot
======

The bot that inhabits the #tjhsst channel on freenode.

Created by fwilson (Fox Wilson, Class of 2016).  
Improved by pfoley (Peter Foley, Class of 2013).
Improved by TechFilmer
Improved by csssuf

Setup
-----
Copy config.example to config.py and change values as needed.  
Install irc (https://pypi.python.org/pypi/irc) and lxml (https://pypi.python.org/pypi/lxml)

Adding Modules
--------------
To add a module place a <mod>.py file in the commands dir.  
The file must contain a def cmd(e, c, msg): method definition.  
The file will only be run if it is marked executable.
