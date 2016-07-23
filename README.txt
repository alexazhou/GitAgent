# GitAgent
A web server receive HTTP request to pull local repository

##install

GitAgent based on python3, and those libs was required.

 * Tornado
 * GitPython
 
you can use pip3 to install it. 
 
##Usage

```python3 agent.py```

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

```curl -v -d 'git_branch=master&git_hash=abcdefg&block=1' 'http://localhost:10000/repo/demo1/pull'```

Return:

```
{
    "ret": "success"
}
```


if block = 1, the request will block until the git work finish 
 
