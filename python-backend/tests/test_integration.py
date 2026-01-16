#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试：模拟 Electron 与 Python 后端的完整通信流程
"""

import sys
import os
import json
import subprocess
import time
import threading

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class PythonBackendTester:
    """Python 后端测试器"""
    
    def __init__(self):
        self.process = None
        self.stdout_thread = None
        self.stderr_thread = None
        self.messages = []
        self.logs = []
        self.running = False
    
    def start(self):
        """启动 Python 后端进程"""
        script_path = os.path.join(os.path.dirname(__file__), '..', 'main.py')
        
        self.process = subprocess.Popen(
            [sys.executable, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        self.running = True
        
        # 启动线程读取 stdout 和 stderr
        self.stdout_thread = threading.Thread(target=self._read_stdout)
        self.stderr_thread = threading.Thread(target=self._read_stderr)
        
        self.stdout_thread.start()
        self.stderr_thread.start()
        
        # 等待启动消息
        time.sleep(0.5)
    
    def _read_stdout(self):
        """读取 stdout（JSON 消息）"""
        while self.running:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                
                line = line.strip()
                if line:
                    try:
                        message = json.loads(line)
                        self.messages.append(message)
                        print(f"[STDOUT] {message}")
                    except json.JSONDecodeError:
                        print(f"[STDOUT] Invalid JSON: {line}")
            except Exception as e:
                print(f"[STDOUT ERROR] {e}")
                break
    
    def _read_stderr(self):
        """读取 stderr（日志）"""
        while self.running:
            try:
                line = self.process.stderr.readline()
                if not line:
                    break
                
                line = line.strip()
                if line:
                    self.logs.append(line)
                    print(f"[STDERR] {line}")
            except Exception as e:
                print(f"[STDERR ERROR] {e}")
                break
    
    def send_command(self, command):
        """发送命令到 Python 后端"""
        command_json = json.dumps(command) + '\n'
        self.process.stdin.write(command_json)
        self.process.stdin.flush()
        print(f"[SEND] {command}")
    
    def stop(self):
        """停止 Python 后端进程"""
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
        
        if self.stdout_thread:
            self.stdout_thread.join(timeout=2)
        if self.stderr_thread:
            self.stderr_thread.join(timeout=2)
    
    def get_messages(self, message_type=None):
        """获取指定类型的消息"""
        if message_type:
            return [msg for msg in self.messages if msg.get('type') == message_type]
        return self.messages


def test_startup():
    """测试后端启动"""
    print("\n=== 测试 1: 后端启动 ===")
    tester = PythonBackendTester()
    
    try:
        tester.start()
        time.sleep(1)
        
        # 检查启动消息
        startup_messages = tester.get_messages('startup')
        assert len(startup_messages) > 0, "未收到启动消息"
        assert startup_messages[0]['status'] == 'ready', "启动状态不正确"
        
        print("✓ 后端启动成功")
    finally:
        tester.stop()


def test_ping_command():
    """测试 ping 命令"""
    print("\n=== 测试 2: Ping 命令 ===")
    tester = PythonBackendTester()
    
    try:
        tester.start()
        time.sleep(1)
        
        # 发送 ping 命令
        tester.send_command({
            "action": "ping",
            "params": {"timestamp": 123456}
        })
        
        time.sleep(0.5)
        
        # 检查响应
        result_messages = tester.get_messages('result')
        assert len(result_messages) > 0, "未收到响应"
        
        result = result_messages[0]
        assert result['status'] == 'success', "命令执行失败"
        assert result['message'] == 'pong', "响应消息不正确"
        assert result['data']['timestamp'] == 123456, "时间戳不匹配"
        
        print("✓ Ping 命令测试通过")
    finally:
        tester.stop()


def test_echo_command():
    """测试 echo 命令"""
    print("\n=== 测试 3: Echo 命令 ===")
    tester = PythonBackendTester()
    
    try:
        tester.start()
        time.sleep(1)
        
        # 发送 echo 命令
        test_data = {
            "message": "Hello World",
            "number": 42,
            "nested": {"key": "value"}
        }
        
        tester.send_command({
            "action": "echo",
            "params": test_data
        })
        
        time.sleep(0.5)
        
        # 检查响应
        result_messages = tester.get_messages('result')
        assert len(result_messages) > 0, "未收到响应"
        
        result = result_messages[0]
        assert result['status'] == 'success', "命令执行失败"
        assert result['data'] == test_data, "数据不匹配"
        
        print("✓ Echo 命令测试通过")
    finally:
        tester.stop()


def test_progress_command():
    """测试进度更新"""
    print("\n=== 测试 4: 进度更新 ===")
    tester = PythonBackendTester()
    
    try:
        tester.start()
        time.sleep(1)
        
        # 发送进度测试命令
        tester.send_command({
            "action": "test_progress",
            "params": {
                "steps": 5,
                "delay": 0.2
            }
        })
        
        # 等待完成
        time.sleep(2)
        
        # 检查进度消息
        progress_messages = tester.get_messages('progress')
        assert len(progress_messages) == 5, f"进度消息数量不正确: {len(progress_messages)}"
        
        # 验证进度递增
        for i, msg in enumerate(progress_messages):
            expected_progress = int((i + 1) / 5 * 100)
            assert msg['progress'] == expected_progress, f"进度值不正确: {msg['progress']} != {expected_progress}"
        
        # 检查最终结果
        result_messages = tester.get_messages('result')
        assert len(result_messages) > 0, "未收到最终结果"
        assert result_messages[0]['status'] == 'success', "命令执行失败"
        
        print("✓ 进度更新测试通过")
    finally:
        tester.stop()


def test_multiple_commands():
    """测试多个连续命令"""
    print("\n=== 测试 5: 多个连续命令 ===")
    tester = PythonBackendTester()
    
    try:
        tester.start()
        time.sleep(1)
        
        # 发送多个命令
        commands = [
            {"action": "ping", "params": {"id": 1}},
            {"action": "echo", "params": {"id": 2}},
            {"action": "ping", "params": {"id": 3}},
        ]
        
        for cmd in commands:
            tester.send_command(cmd)
            time.sleep(0.3)
        
        time.sleep(0.5)
        
        # 检查响应数量
        result_messages = tester.get_messages('result')
        assert len(result_messages) == 3, f"响应数量不正确: {len(result_messages)}"
        
        # 验证所有命令都成功
        for result in result_messages:
            assert result['status'] == 'success', "命令执行失败"
        
        print("✓ 多命令测试通过")
    finally:
        tester.stop()


def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试 6: 错误处理 ===")
    tester = PythonBackendTester()
    
    try:
        tester.start()
        time.sleep(1)
        
        # 发送无效命令
        tester.send_command({
            "action": "unknown_action",
            "params": {}
        })
        
        time.sleep(0.5)
        
        # 检查错误响应
        result_messages = tester.get_messages('result')
        assert len(result_messages) > 0, "未收到响应"
        
        result = result_messages[0]
        assert result['status'] == 'error', "应该返回错误状态"
        assert result['error_code'] == 'UNKNOWN_ACTION', "错误代码不正确"
        
        print("✓ 错误处理测试通过")
    finally:
        tester.stop()


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Python 后端集成测试")
    print("=" * 60)
    
    tests = [
        test_startup,
        test_ping_command,
        test_echo_command,
        test_progress_command,
        test_multiple_commands,
        test_error_handling,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ 测试失败: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ 测试异常: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
