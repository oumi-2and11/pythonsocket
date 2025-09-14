import wx,time
from socket import socket,AF_INET,SOCK_STREAM
import threading

class YsjServer(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,id=1002,title='服务器端界面',pos=wx.DefaultPosition,size=(400,450))
        # 窗口放一个面板
        pl=wx.Panel(self)
        # 面板上放一个盒
        box=wx.BoxSizer(wx.VERTICAL)# 垂直放向上自动排版
        # 可伸缩的网格布局
        fgz1=wx.FlexGridSizer(wx.HSCROLL) # 水平方向布局

        start_server_btn = wx.Button(pl,size=(133,40),label='启动服务')
        record_btn = wx.Button(pl, size=(133, 40), label='保存聊天记录')
        stop_server_btn = wx.Button(pl, size=(133, 40), label='停止服务')

        # 将按钮添加到可伸缩的网格布局中
        fgz1.Add(start_server_btn,1,wx.TOP|wx.LEFT)
        fgz1.Add(record_btn, 1, wx.TOP)
        fgz1.Add(stop_server_btn, 1, wx.TOP | wx.RIGHT)

        # 将可伸缩的网格布局添加到盒子中
        box.Add(fgz1,1,wx.ALIGN_CENTRE)
        # 只读文本框，显示聊天内容
        self.show_text = wx.TextCtrl(pl, size=(400, 410), style=wx.TE_MULTILINE | wx.TE_READONLY)
        box.Add(self.show_text, 1, wx.ALIGN_CENTRE)

        # 将盒子添加到面板中
        pl.SetSizer(box)
        '''--------------------以上的代码都是页面的绘制代码-------------------------'''

        '''服务器功能实现的必要属性''' # 编写了6个实例属性
        self.isOn=False # 存储服务器的启动状态，默认值False，默认没有启动
        # 服务器端绑定的ip地址和端口
        self.host_port=('',8888)# 空的字符串代表的是本机的所有IP
        # 创建socket对象
        self.server_socket=socket(AF_INET,SOCK_STREAM)
        # 绑定ip地址和端口
        self.server_socket.bind(self.host_port)
        # 设置监听
        self.server_socket.listen(5)
        # 创建一个字典，存储与客户端对话的会话线程
        self.session_thread_dict={} # key_value:{客户端的名称key,会话线程value}

        # 当鼠标点击“启动服务”按钮时，要执行的操作
        self.Bind(wx.EVT_BUTTON,self.start_server,start_server_btn)
        # 当鼠标点击“保存聊天记录”按钮时，要执行的操作
        self.Bind(wx.EVT_BUTTON,self.save_record,record_btn)
        # 当鼠标点击“断开”按钮时，要执行的操作
        self.Bind(wx.EVT_BUTTON,self.stop_server,stop_server_btn)

    def stop_server(self,event):
        #
        print('服务器已停止服务')
        self.isOn=False

    def save_record(self,event):
        # 获取只读文本框中的内容
        record_data=self.show_text.GetValue()
        # 打开一个文本文件，将聊天记录写入到文本文件中
        with open('record.log','w',encoding='utf-8') as file:
            file.write(record_data)


    def start_server(self,event):
        # print('启动服务的按钮被点击了')
        # 判断服务器是否已经启动,只有当服务器没有启动时，才执行下面的代码
        if not self.isOn: # 如果服务器没有启动，等价于self.isOn==False
            # 启动服务器
            self.isOn=True
            # 创建主线程对象，函数形创建
            main_thread=threading.Thread(target=self.do_work)
            # 设置为守护线程,当父线程(窗体界面)执行结束，子线程也自动关闭
            main_thread.daemon=True
            # 启动主线程
            main_thread.start()



    def do_work(self):
        # 判断isOn的值
        while self.isOn:
            # 接收客户端的连接请求
            session_socket,client_addr=self.server_socket.accept()
            # 客户端发送连接请求后，发过来的第一条数据为客户端的名称，客户端的名称作为字典中的key
            user_name=session_socket.recv(1024).decode('utf-8')
            # 创建一个会话线程对象
            session_thread=SessionThread(session_socket,user_name,self)
            # 将绘画线程对象存储到字典中
            self.session_thread_dict[user_name]=session_thread
            # 启动绘画线程
            session_thread.start()
            # 输出服务器的提示信息
            self.show_info_and_send_client('服务器通知',f'欢迎{user_name}进入聊天室！',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
        # 当self.isOn为False时，关闭线程
        self.server_socket.close()

    def show_info_and_send_client(self,data_source,data,date_time):
        # 字符串拼接操作
        send_data=f'{data_source}:{data}\n时间:{date_time}'
        # 只读文本框
        self.show_text.AppendText('-'*40+'\n'+send_data+'\n')
        # 每一个客户端都发送数据
        for client in self.session_thread_dict.values():
            # 如果当前的会话是开启状态
            if client.isOn:
                client.client_socket.send(send_data.encode('utf-8'))


# 服务器端会话线程的类

class SessionThread(threading.Thread):
    def __init__(self,client_socket,user_name,server):
        # 调用父类的初始化方法
        threading.Thread.__init__(self)
        self.client_socket=client_socket
        self.user_name=user_name
        self.server=server
        self.isOn=True # 会话线程是否启动,在74行创建会话线程时启动




    def run(self)->None:
        print(f'客户端{self.user_name}已经和服务器连接成功,服务器启动一个会话线程')
        while self.isOn:
            # 从客户端接收数据，存储到data中
            data=self.client_socket.recv(1024).decode('utf-8')
            # 如果客户端点击断开按钮，先给服务器发送一句话，消息自定义
            if data=='Y-disconnect-SJ':# 自定义的结束词
                self.isOn=False
                # 发送一条服务器通知
                self.server.show_info_and_send_client('服务器通知',f'{self.user_name}离开了聊天室',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
            else:
                # 其他聊天信息显示给所有客户端，包含服务器也显示
                # 调用刚才编写分方法
                self.server.show_info_and_send_client(self.user_name,data,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))

        # 关闭socket
        self.client_socket.close()




if __name__ == '__main__':
    app=wx.App()
    # 创建自己的服务器端界面对象
    server=YsjServer()
    server.Show()

    # 循环刷新显示
    app.MainLoop()




