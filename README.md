# 通用Zigbee网关 `毕设`
- Zigbee网关的作用是将zigbee网络里的数据转发至其他类型的网络（如互联网），同时可以将其他网络的数据转发至zigbee网络
- 通过flask假设web服务器，通过浏览器，人工输入数据及得到数据
## 程序运行
**克隆仓库**
    
    git clone https://github.com/ChenPY101/gateway
    cd gateway
**安装依赖**

    pipenv install --dev
    pipenv shell

***如果没有安装pipenv,可以通过pip安装（pip install pipenv）***

**其他**  
路由 

    flask routes
    

    Endpoint  Methods    Rule
    --------  ---------  -----------------------
    dataList  GET        /data
    get_data  POST       /post_pi
    hello     GET        /
    hello     GET        /hello/<name>
    index     GET, POST  /index
    login     GET, POST  /login
    logout    GET        /logout
    static    GET        /static/<path:filename>
帮助

    flask --help


    Commands:
    db      Perform database migrations.
    init
    initdb
    routes  Show the routes for the app.
    run     Runs a development server.
    shell   Runs a shell in the app context.

其中  
初始化数据库

    flask initdb
初始化（更新用户信息）

    flask init

**运行**  
理论上

    flask run
就可以运行程序，但程序有报错，可以是程序里开了线程的关系吧

    ValueError: signal only works in main thread
可以使用

    python app.py
然后就可以在浏览器输入 ***127.0.0.1:5000*** 获取界面（本地测试）

**登陆** ***127.0.0.1:5000/login***
<div align=center><img width="200" height="170" src="./picture/login.jpg"/></div>

**数据交换** ***127.0.0.1:5000/index*** （登陆后自动跳转）
<div align=center><img width="200" height="200" src="./picture/index.jpg"/></div>

**数据** ***127.0.0.1:5000/data***
<div align=center><img width="225" height="250" src="./picture/data.jpg"/></div>

--- 
还没完成，还存在的很多问题 :bug:
