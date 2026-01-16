#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Router 集成测试
"""

import sys
import os
import json
import pytest

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cli_router import CLIRouter


class TestCLIRouter:
    """CLI Router 测试类"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.router = CLIRouter()
    
    def test_ping_command(self):
        """测试 ping 命令"""
        command = {
            "action": "ping",
            "params": {"timestamp": 123456}
        }
        
        result = self.router.route(command)
        
        assert result["type"] == "result"
        assert result["status"] == "success"
        assert result["message"] == "pong"
        assert result["data"]["timestamp"] == 123456
    
    def test_echo_command(self):
        """测试 echo 命令"""
        command = {
            "action": "echo",
            "params": {
                "message": "Hello World",
                "number": 42
            }
        }
        
        result = self.router.route(command)
        
        assert result["type"] == "result"
        assert result["status"] == "success"
        assert result["message"] == "echo"
        assert result["data"]["message"] == "Hello World"
        assert result["data"]["number"] == 42
    
    def test_missing_action(self):
        """测试缺少 action 字段"""
        command = {
            "params": {"test": "data"}
        }
        
        result = self.router.route(command)
        
        assert result["type"] == "result"
        assert result["status"] == "error"
        assert result["error_code"] == "MISSING_ACTION"
    
    def test_unknown_action(self):
        """测试未知的 action"""
        command = {
            "action": "unknown_action",
            "params": {}
        }
        
        result = self.router.route(command)
        
        assert result["type"] == "result"
        assert result["status"] == "error"
        assert result["error_code"] == "UNKNOWN_ACTION"
        assert "available_actions" in result
    
    def test_handler_exception(self):
        """测试处理器异常"""
        # 注册一个会抛出异常的处理器
        def bad_handler(params):
            raise ValueError("Test error")
        
        self.router.handlers["bad_action"] = bad_handler
        
        command = {
            "action": "bad_action",
            "params": {}
        }
        
        result = self.router.route(command)
        
        assert result["type"] == "result"
        assert result["status"] == "error"
        assert result["error_code"] == "HANDLER_ERROR"
        assert "Test error" in result["message"]


class TestProgressMessages:
    """进度消息测试类"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.router = CLIRouter()
        self.captured_output = []
    
    def test_progress_command(self, capsys):
        """测试进度命令（捕获输出）"""
        command = {
            "action": "test_progress",
            "params": {
                "steps": 3,
                "delay": 0.1
            }
        }
        
        result = self.router.route(command)
        
        # 验证最终结果
        assert result["type"] == "result"
        assert result["status"] == "success"
        assert result["data"]["total_steps"] == 3
        
        # 捕获 stdout 输出
        captured = capsys.readouterr()
        output_lines = [line for line in captured.out.split('\n') if line.strip()]
        
        # 应该有 3 条进度消息
        progress_messages = []
        for line in output_lines:
            try:
                msg = json.loads(line)
                if msg.get("type") == "progress":
                    progress_messages.append(msg)
            except json.JSONDecodeError:
                pass
        
        assert len(progress_messages) == 3
        
        # 验证进度递增
        for i, msg in enumerate(progress_messages):
            expected_progress = int((i + 1) / 3 * 100)
            assert msg["progress"] == expected_progress
            assert "处理步骤" in msg["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
