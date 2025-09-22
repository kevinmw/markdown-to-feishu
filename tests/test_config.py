#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块单元测试
"""

import unittest
import os
import sys

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.config import FeishuConfig, get_default_config


class TestFeishuConfig(unittest.TestCase):
    """飞书配置测试类"""
    
    def test_init(self):
        """测试初始化"""
        config = FeishuConfig()
        self.assertIsNone(config.app_id)
        self.assertIsNone(config.app_secret)
        self.assertIsNone(config.user_access_token)
        self.assertIsNone(config.tenant_access_token)
    
    def test_from_dict(self):
        """测试从字典创建配置"""
        test_dict = {
            'app_id': 'test_app_id',
            'app_secret': 'test_app_secret',
            'user_access_token': 'test_user_token',
            'tenant_access_token': 'test_tenant_token'
        }
        
        config = FeishuConfig.from_dict(test_dict)
        
        self.assertEqual(config.app_id, 'test_app_id')
        self.assertEqual(config.app_secret, 'test_app_secret')
        self.assertEqual(config.user_access_token, 'test_user_token')
        self.assertEqual(config.tenant_access_token, 'test_tenant_token')
    
    def test_from_env(self):
        """测试从环境变量创建配置"""
        # 设置环境变量
        os.environ['FEISHU_APP_ID'] = 'env_app_id'
        os.environ['FEISHU_APP_SECRET'] = 'env_app_secret'
        os.environ['FEISHU_USER_ACCESS_TOKEN'] = 'env_user_token'
        
        try:
            config = FeishuConfig.from_env()
            
            self.assertEqual(config.app_id, 'env_app_id')
            self.assertEqual(config.app_secret, 'env_app_secret')
            self.assertEqual(config.user_access_token, 'env_user_token')
        finally:
            # 清理环境变量
            for key in ['FEISHU_APP_ID', 'FEISHU_APP_SECRET', 'FEISHU_USER_ACCESS_TOKEN']:
                if key in os.environ:
                    del os.environ[key]
    
    def test_validate_valid_config(self):
        """测试有效配置验证"""
        config = FeishuConfig()
        config.app_id = 'test_app_id'
        config.app_secret = 'test_app_secret'
        config.user_access_token = 'test_user_token'
        
        self.assertTrue(config.validate())
    
    def test_validate_invalid_config(self):
        """测试无效配置验证"""
        # 缺少app_id
        config = FeishuConfig()
        config.app_secret = 'test_app_secret'
        config.user_access_token = 'test_user_token'
        self.assertFalse(config.validate())
        
        # 缺少app_secret
        config = FeishuConfig()
        config.app_id = 'test_app_id'
        config.user_access_token = 'test_user_token'
        self.assertFalse(config.validate())
        
        # 缺少访问令牌
        config = FeishuConfig()
        config.app_id = 'test_app_id'
        config.app_secret = 'test_app_secret'
        self.assertFalse(config.validate())
    
    def test_get_access_token(self):
        """测试获取访问令牌"""
        config = FeishuConfig()
        
        # 优先返回用户令牌
        config.user_access_token = 'user_token'
        config.tenant_access_token = 'tenant_token'
        self.assertEqual(config.get_access_token(), 'user_token')
        
        # 用户令牌为空时返回租户令牌
        config.user_access_token = None
        self.assertEqual(config.get_access_token(), 'tenant_token')
        
        # 都为空时返回None
        config.tenant_access_token = None
        self.assertIsNone(config.get_access_token())
    
    def test_get_default_config(self):
        """测试获取默认配置"""
        config = get_default_config()
        
        self.assertIsNotNone(config.app_id)
        self.assertIsNotNone(config.app_secret)
        self.assertIsNotNone(config.user_access_token)
        self.assertTrue(config.validate())


if __name__ == '__main__':
    unittest.main()