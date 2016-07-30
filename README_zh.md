# GitAgent
一个允许你通过 Http 请求来操作其他机器上 Git 仓库的服务

##Desc

GitAgent 作为一个web服务来运行. 接收来自 Http 请求的命令来对本地的 Git 仓库进行操作

有了 GitAgent，你可以对其他机器上的 Git 仓库做下面这些事情

* 获取当前仓库的状态
* pull 最新的代码
* checkout 分支／版本
...

GitAgent 还支持在 pull 成功之后执行指定的命令（主要是为了方便完成部署的附加工作），也允许设置密码来保护接口的安全性

##安装

python3 -m pip install gitagent

##依赖

GitAgent 基于 Python3，下面这些库是需要的。

 * Tornado
 * GitPython
 * ws4py
 
如果你是通过 pip 安装的 GitAgent, 那么这些依赖会被自动装好.

##配置

##### 最简配置割格式

最简化的配置文件格式如下
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
如果需要可以在里面定义多个仓库


#####完整配置格式

如果需要使用密码，或者在 pull 之后执行命令，那么像下面这样多定义一些字段。

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

command 中可以定义多个命令，通过 http 请求来控制 pull 的时候，可以指定在 pull 完成之后，来执行这里面的命令

 
##Usage

#### step 1: 生成配置文件
```python3 -m gitagent [-c config.json] write```

执行这条命令之后，默认配置模版会被写入到指定的文件

如果没有给出 -c 参数, gitagent 会写入配置模板到当前目录的 config.json

#### step 2: 编辑配置文件

按照自己的情况编辑配置模板

#### step 2: 运行 gitagent
```python3 -m gitagent [-c config.json] run```

如果没有报错，那么gitagent就已经在运行了（目前 gitagent 在前台运行，如果需要的话可以使用 supervisor 使其在后台运行 ）

##API

####列出当前仓库

```curl -v 'http://localhost:10000/repo'```

Return:

```
[
    "demo1",
    "demo2",
    "demo3"
]
```


####仓库状态

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

####对仓库进行 pull / 切换分支 / 切换版本 

```curl -v -d 'git_branch=master&git_hash=abcdefg&command=cmd1&block=1' 'http://localhost:10000/repo/demo1/pull'```

Return:

```
{
    "ret": "success"
}
```

参数:

* ****git_branch****: 需要 pull／checkout 的分支
* ****git_hash****: 可选参数. 如果没有指定 git_hash, gitagent 将自动 checkout 目标分支上面的最新一个提交 
* ****command****: 可选参数. 如果指定了 command，那么这个 command 将会被在 pull 成功之后来执行 
* ****block****: 可以是 0/1, 如果 block = 1, 那么这个请求会阻塞到操作全部完成之后才返回 



 
##Client

GitAgent 还包含了一个 client 实现，封装了 http 请求相关的代码。只需要通过

```from gitagent import client```

import 之后，就可以直接使用

#### 创建 client 对象

```
agent_client = client.AgentClient( SERVER_ADDR, SERVER_PORT )
```

#### 获取仓库列表

```
agent_client.repo_list()

>> ['repo1','repo2','repo3']
```

#### 获取仓库状态

```
agent_client.repo_status('repo1')
{'untracked_files': ['a.txt', 'config.json', 'xxx.json'], 'busy': False, 'hash': '827b39799a543fee30a174d44cd0c5451776e413', 'dirty': True, 'changed_files': {'R': [], 'A': [], 'D': [], 'M': []}, 'author': 'AlexaZhou', 'branch': 'master', 'message': '\u66f4\u65b0\u6587\u6863\n'}
```

#### 对仓库进行操作
```
agent_client.pull('repo1', branch='master', hash='abcdefg', command='cmd1', block=1)
>>{'ret': 'success', 'err_msg': None}
```  
注： branch, hash, command, block 都是可选参数



