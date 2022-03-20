# 长安大学疫情自动打卡程序(chd-daka)

#### 环境

> python3.9.5
#### 版本
- 1.0.2
> 增加Github Action 自动运行
 
- 1.0.1
> 修复ChromeDriver在`headless`模式下获取定位失败的问题,copy自[chromiumbbug反馈](https://bugs.chromium.org/p/chromium/issues/detail?id=834808#c9)

- 1.0.0
> 第一次发布...

#### 使用说明

- 修改config.json中的信息

  ```json
  {
      "mailInfo": {
          "host_server": "smtp.qq.com",
          "sender_qq": "QQ号",
          "pwd": "QQ邮箱授权码",
          "sender_qq_mail": "xxxxx@qq.com"
      },
      "userInfo": [
          {
              "id": "学号",
              "pw": "密码",
              "wxkey": "",
              "email": "邮箱"
          },
          {
              "id": "学号",
              "pw": "密码",
              "wxkey": "",
              "email": "邮箱"
          },
          {
              "id": "学号",
              "pw": "密码",
              "wxkey": "",
              "email": "邮箱"
          }
      ],
      "address": [
          "宿舍",
          "XXXX",
          "学校",
          "校内"
      ]
  }
  ```

- 运行main.py,程序会在每天早上7点和中午13点定时执行,并将打卡结果发送到邮箱

#### 参考
部分代码参考自 [这位同学](https://gitee.com/git-lee/chd_DAKA/tree/master ), 感谢!!

