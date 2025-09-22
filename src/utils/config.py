#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块
提供飞书应用配置的统一管理
"""

import os
from typing import Optional


class FeishuConfig:
    """飞书配置管理类"""
    
    def __init__(self):
        self.app_id = None
        self.app_secret = None
        self.user_access_token = None
        self.tenant_access_token = None
        
    @classmethod
    def from_env(cls) -> 'FeishuConfig':
        """从环境变量加载配置"""
        config = cls()
        config.app_id = os.getenv('FEISHU_APP_ID')
        config.app_secret = os.getenv('FEISHU_APP_SECRET')
        config.user_access_token = os.getenv('FEISHU_USER_ACCESS_TOKEN')
        config.tenant_access_token = os.getenv('FEISHU_TENANT_ACCESS_TOKEN')
        return config
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'FeishuConfig':
        """从字典加载配置"""
        config = cls()
        config.app_id = config_dict.get('app_id')
        config.app_secret = config_dict.get('app_secret')
        config.user_access_token = config_dict.get('user_access_token')
        config.tenant_access_token = config_dict.get('tenant_access_token')
        return config
    
    def validate(self) -> bool:
        """验证配置是否完整"""
        if not self.app_id or not self.app_secret:
            return False
        if not self.user_access_token and not self.tenant_access_token:
            return False
        return True
    
    def get_access_token(self) -> Optional[str]:
        """获取可用的访问令牌（优先用户令牌）"""
        return self.user_access_token or self.tenant_access_token


def get_default_config() -> FeishuConfig:
    """获取默认配置（从环境变量）"""
    return FeishuConfig.from_env()


if __name__ == "__main__":
    # 测试配置
    config = get_default_config()
    print(f"配置验证: {config.validate()}")
    print(f"App ID: {config.app_id}")
    print(f"Access Token: {config.get_access_token()[:20]}...")