GitAgent
========

A web server receive HTTP request to pull local repository

install
-------

python3 -m pip install gitagent

require
-------

GitAgent based on python3, and those libs was required.

-  Tornado
-  GitPython

if you use pip install GitAgent, the requirements will be install
automatic.

Desc
----

GitAgent run as a webserver. It receive command from http requests and
do operation to local git repositorys.

So GitAgent let you can do git operation over http request.

With GitAgent, you can a git repository on other machine to:

-  get current status
-  pull latest code
-  checkout branch …

GitAgent also support execute some commant after pull success, and use a
password to protect http request.

You can see detail documents over https://github.com/alexazhou/GitAgent