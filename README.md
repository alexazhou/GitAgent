# GitAgent
A web server receive HTTP request to pull local repository

[中文文档](https://github.com/alexazhou/GitAgent/blob/master/README_zh.md)

##Desc

GitAgent run as a webserver. It receive command from http requests and do operation to local git repositorys.

So GitAgent let you can do git operation over http request.

With GitAgent, you can a git repository on other machine to:

* get current status
* pull latest code 
* checkout branch
...

GitAgent also support execute some commant after pull success, and use a password to protect http request.

##install

python3 -m pip install gitagent

##require

GitAgent based on python3, and those libs was required.

 * Tornado
 * GitPython
 * ws4py
 
if you use pip install GitAgent, the requirements will be install automatic.

##config

##### Basic config format
The basic format of config.json is like this.

```
example_config = {
    "bind_ip":"0.0.0.0",
	"port":10000,
	"repo":{
		"self":{
			"repo_path":"./",
		}
	},
}
```
If need, you can put more than one repon into it.


#####full config format

if you need use password, or execute command after pull, you can add some args to config file like that.

```
example_config_full = {
    "bind_ip":"0.0.0.0",
	"port":10000,
	"repo":{
		"self":{
			"repo_path":"./",
            "command":{
                "cmd1":"the command 1",
                "cmd2":"the command 2",
            }
		}
	},
    "password":"123456"
}

```

 
##Usage

#### step 1: Write default config file
```python3 -m gitagent [-c config.json] write```

The default config file will by written to config.json, then you can known the config format.

if the -c arg don't gived, gitagent will write the config.json to current directory

#### step 2: Edit the config.json

Just edit the config file as you need

#### step 3: Run gitagent
```python3 -m gitagent [-c config.json] run```

If you havn't see any error message, the gitagent is running.

##API

####list all repos

```curl -v 'http://localhost:10000/repo'```

Return:

```
[
    "demo1",
    "demo2",
    "demo3"
]
```


####repo status

```curl -v 'http://localhost:10000/repo/demo1'```

Return:

```
{
    {
    "author": "AlexaZhou",
    "busy": false,
    "changed_files": {
        "A": [],
        "D": [],
        "M": [
            "agent.py"
        ],
        "R": []
    },
    "dirty": true,
    "hash": "c8c082d898c2dc18adb8e79f8992c074fb2294ce",
    "message": "some message text",
    "untracked_files": [
        "config.json"
    ]
}
```

busy means the repo is processing a pull request or other action

####repo pull / switch branch / switch hash 

```curl -v -d 'git_branch=master&git_hash=abcdefg&command=cmd1&block=1' 'http://localhost:10000/repo/demo1/pull'```

Return:

```
{
    "ret": "success"
}
```

args:

* ****git_branch****: the branch you want to checkout.
* ****git_hash****: is a optional arg. if git_hash not given, gitagent will checkout lastest commit on the target branch 
* ****command****: is a optional arg. if command was gived, it will be execute after pull. 
* ****block****: can be 0/1, if block = 1, the request will block until the git work finish 
 
