# GitAgent
A web server receive HTTP request to pull local repository

##Need
 * Python3
 * Tornado
 * GitPython
 
##Usage

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
    "author": "AlexaZhou",
    "busy": false,
    "hash": "6ef63071ec9cfffa21edfc462cc7b1a2aa7eaaf6",
    "message": "加入异常处理\n"
}
```

busy means the repo is processing a pull request or other action

####repo pull / switch branch / switch hash

```curl -v -d 'branch=master&hash=abcdefg&block=1' 'http://localhost:10000/repo/demo1/pull'```

Return:

```
{
    "ret": "success"
}
```


if block = 1, the request will block until the git work finish 
 
