# 简单远程监控系统——服务器端程序  
>Xien  
>2021/3  
>Python 3.7  

## 第三方库  
>pymysql  


## 文件  



## Code  
### 1xx  Controller
>100 连接登录请求 + userName + password    
>//110 断开连接  

### 2xx  Client
>200 连接登录请求 + userName + password  
>210 用户注册请求 + userName + password  
>220 视频流选择请求 + camera  
>250 关闭控制线程（client to client）  

### 3xx  Server
>300 允许登录  
>301 拒绝登录  
>310 用户注册成功  
>311 用户注册失败  
>320 视频流线程连接请求 + port  
>321 摄像头数量通知(to client) + num  
>322 视频流线程关闭请求
>/331 无视频流  
>340 心跳包

### 4xx  Error
>400 未定义错误  
>410 缺少code  
>411 非预期code  
>412 缺少必要字段  
>420 数据库错误  
>430 Json解析错误  
>440 设置失败  
>441 设置的摄像头不存在  

### 500  Other
>500 数据长度通知 + frameLen  
>510 清晰度设置 + camera + definition  
>511 帧数设置 + camera + rate  
>520 动作指令 + camera + move  
>530 设置成功   