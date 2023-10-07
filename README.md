# ddns-py
一款用于 cloudflare DNS 的 IPv4 DDNS 工具。

请确认您的宽带有公网IPv4再使用。判断方法：路由器显示的 WAN IP 与 <https://4.ipw.cn> 显示的一致

***
## 启动方法
### Windows
预先安装python3  
然后双击 `ddns.py.bat` 启动，或者在命令行输入 `python ddns.py`  

### Linux
预先安装python3  
然后在命令行输入 `python3 ddns.py`  

***
## 使用命令行参数跳过询问模式
前置命令见[启动方法](#启动方法)  
在命令后面按照如下格式加上参数  
```
mode=2
```
其中 `=` 后面是模式编号，请参照下方列出的编号进行修改，不得在等号两侧添加空格。
```
1 更新记录后退出
2 循环检查IP变化并更新记录
3 删除记录后退出
```
