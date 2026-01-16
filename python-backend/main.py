#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel Toolkit Backend - 主入口
使用长连接模式，通过 stdin/stdout 与 Electron 通信
"""

import sys
import json
from cli_router import CLIRouter


def log(message):
    """将日志输出到 stderr，避免干扰 stdout 中的 JSON 数据"""
    sys.stderr.write(f"[BACKEND] {message}\n")
    sys.stderr.flush()


def main():
    """主函数：启动 CLI 路由器，保持长连接"""
    log("Excel Toolkit Backend starting...")
    
    router = CLIRouter()
    
    # 发送启动成功消息
    startup_message = {
        "type": "startup",
        "status": "ready",
        "message": "Backend initialized successfully"
    }
    print(json.dumps(startup_message), flush=True)
    
    # 主循环：持续监听 stdin
    while True:
        try:
            # 读取一行命令
            line = sys.stdin.readline()
            
            # 如果没有输入，说明 stdin 已关闭，退出循环
            if not line:
                log("stdin closed, exiting...")
                break
            
            # 解析 JSON 命令
            command = json.loads(line.strip())
            log(f"Received command: {command.get('action', 'unknown')}")
            
            # 路由并处理命令
            result = router.route(command)
            
            # 输出结果到 stdout
            print(json.dumps(result), flush=True)
            
        except json.JSONDecodeError as e:
            log(f"JSON decode error: {str(e)}")
            error_result = {
                "type": "result",
                "status": "error",
                "error_code": "INVALID_JSON",
                "message": f"Invalid JSON format: {str(e)}"
            }
            print(json.dumps(error_result), flush=True)
            
        except Exception as e:
            log(f"Unexpected error: {str(e)}")
            error_result = {
                "type": "result",
                "status": "error",
                "error_code": "INTERNAL_ERROR",
                "message": f"Internal error: {str(e)}"
            }
            print(json.dumps(error_result), flush=True)
    
    log("Backend shutting down...")


if __name__ == "__main__":
    main()
