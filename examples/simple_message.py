#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import lark_oapi as lark
from lark_oapi.api.im.v1 import *

def send_message():
    """发送文本消息到飞书"""
    
    # 创建客户端
    client = lark.Client.builder() \
        .app_id("your_app_id_here") \
        .app_secret("your_app_secret_here") \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request = CreateMessageRequest.builder() \
        .receive_id_type("open_id") \
        .request_body(CreateMessageRequestBody.builder()
                      .receive_id("target_user_open_id")
                      .msg_type("text")
                      .content("{\"text\":\"这是claude发送的内容\"}")
                      .build()) \
        .build()

    # 发起请求
    response = client.im.v1.message.create(request)

    # 处理返回结果
    if not response.success():
        print(f"发送消息失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return False
    else:
        print(f"发送消息成功!")
        print(f"消息ID: {response.data.message_id}")
        print(f"消息内容: {response.data.body.content}")
        return True

if __name__ == "__main__":
    send_message()