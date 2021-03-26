# 简单远程监控系统——服务器端程序  
>Xien  
>2021/3  
>Python 3.7  

## 第三方库  
>pymysql  


## 文件  



## Code  
### 1xx  Controller
>100 连接登录请求    
>110 断开连接  

### 2xx  Client
>200 连接登录请求  
>210 用户注册请求  
>220 视频流请求  
>250 关闭控制线程（client to client）  

### 3xx  Server
>300 允许登录  
>301 拒绝登录  
>310 用户注册成功  
>311 用户注册失败  
>320 视频流连接请求(to controller)  
>321 视频流连接请求(to client)  
>331 无视频流  
>340 心跳包

### 4xx  Error
>400 未定义错误  
>410 缺少code  
>411 非预期code  
>412 缺少必要字段  
>420 数据库错误  
>430 Json解析错误  
>440 设置失败  

### 500 Other
>500 数据长度通知  
>510 清晰度设置  
>511 帧数设置  
>520 遥控指令  
>530 OK  