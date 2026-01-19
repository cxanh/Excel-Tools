#!/usr/bin/env node
/**
 * 工作表管理功能测试脚本
 * 测试插入、删除、重命名工作表功能
 */

const { spawn } = require('child_process');
const path = require('path');

// 测试文件路径
const TEST_FILE = path.join(__dirname, 'test.xlsx');

// 启动 Python 后端
const pythonProcess = spawn('python', [
  path.join(__dirname, 'python-backend', 'main.py')
], {
  stdio: ['pipe', 'pipe', 'pipe'],
  env: {
    ...process.env,
    PYTHONIOENCODING: 'utf-8'
  }
});

let testResults = [];
let currentTest = '';

// 监听 stdout（JSON 响应）
pythonProcess.stdout.on('data', (data) => {
  const lines = data.toString().split('\n');
  for (const line of lines) {
    if (line.trim()) {
      try {
        const message = JSON.parse(line);
        console.log(`[PYTHON] ${JSON.stringify(message, null, 2)}`);
        
        if (message.type === 'result') {
          testResults.push({
            test: currentTest,
            status: message.status,
            message: message.message,
            data: message.data
          });
        }
      } catch (e) {
        console.log(`[PYTHON OUTPUT] ${line}`);
      }
    }
  }
});

// 监听 stderr（日志）
pythonProcess.stderr.on('data', (data) => {
  console.log(`[PYTHON LOG] ${data.toString()}`);
});

// 监听进程退出
pythonProcess.on('exit', (code) => {
  console.log(`\n[TEST] Python process exited with code: ${code}`);
  printTestResults();
});

// 发送命令到 Python
function sendCommand(command) {
  const commandJson = JSON.stringify(command);
  console.log(`\n[TEST] Sending command: ${commandJson}`);
  pythonProcess.stdin.write(commandJson + '\n');
}

// 延迟执行
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// 打印测试结果
function printTestResults() {
  console.log('\n' + '='.repeat(60));
  console.log('测试结果汇总');
  console.log('='.repeat(60));
  
  let successCount = 0;
  let failCount = 0;
  
  testResults.forEach((result, index) => {
    const status = result.status === 'success' ? '✓' : '✗';
    const color = result.status === 'success' ? '\x1b[32m' : '\x1b[31m';
    console.log(`${color}${status}\x1b[0m ${index + 1}. ${result.test}`);
    console.log(`   ${result.message}`);
    
    if (result.status === 'success') {
      successCount++;
    } else {
      failCount++;
    }
  });
  
  console.log('='.repeat(60));
  console.log(`总计: ${testResults.length} 个测试`);
  console.log(`\x1b[32m成功: ${successCount}\x1b[0m`);
  console.log(`\x1b[31m失败: ${failCount}\x1b[0m`);
  console.log('='.repeat(60));
}

// 运行测试
async function runTests() {
  console.log('[TEST] Starting sheet management tests...\n');
  
  // 等待后端启动
  await delay(2000);
  
  // 测试 1: 加载文件
  currentTest = '加载测试文件';
  sendCommand({
    action: 'load_file',
    params: {
      file_path: TEST_FILE
    }
  });
  await delay(1000);
  
  // 测试 2: 插入工作表（默认名称）
  currentTest = '插入工作表（默认名称）';
  sendCommand({
    action: 'insert_sheet',
    params: {}
  });
  await delay(1000);
  
  // 测试 3: 插入工作表（自定义名称）
  currentTest = '插入工作表（自定义名称："测试工作表"）';
  sendCommand({
    action: 'insert_sheet',
    params: {
      sheet_name: '测试工作表',
      position: 0
    }
  });
  await delay(1000);
  
  // 测试 4: 重命名工作表
  currentTest = '重命名工作表（"测试工作表" → "新名称"）';
  sendCommand({
    action: 'rename_sheet',
    params: {
      old_name: '测试工作表',
      new_name: '新名称'
    }
  });
  await delay(1000);
  
  // 测试 5: 删除工作表
  currentTest = '删除工作表（"新名称"）';
  sendCommand({
    action: 'delete_sheet',
    params: {
      sheet_name: '新名称'
    }
  });
  await delay(1000);
  
  // 测试 6: 尝试删除唯一工作表（应该失败）
  currentTest = '尝试删除唯一工作表（应该失败）';
  sendCommand({
    action: 'delete_sheet',
    params: {
      sheet_name: 'Sheet1'
    }
  });
  await delay(1000);
  
  // 测试 7: 尝试插入重复名称（应该失败）
  currentTest = '尝试插入重复名称的工作表（应该失败）';
  sendCommand({
    action: 'insert_sheet',
    params: {
      sheet_name: 'Sheet1'
    }
  });
  await delay(1000);
  
  // 测试 8: 尝试重命名为已存在的名称（应该失败）
  currentTest = '尝试重命名为已存在的名称（应该失败）';
  sendCommand({
    action: 'insert_sheet',
    params: {
      sheet_name: 'Sheet2'
    }
  });
  await delay(500);
  sendCommand({
    action: 'rename_sheet',
    params: {
      old_name: 'Sheet2',
      new_name: 'Sheet1'
    }
  });
  await delay(1000);
  
  // 测试 9: 保存文件
  currentTest = '保存文件';
  sendCommand({
    action: 'save_file',
    params: {
      overwrite: true,
      create_backup: true
    }
  });
  await delay(1000);
  
  // 测试 10: 关闭文件
  currentTest = '关闭文件';
  sendCommand({
    action: 'close_file',
    params: {}
  });
  await delay(1000);
  
  // 结束测试
  console.log('\n[TEST] All tests completed. Waiting for results...');
  await delay(2000);
  pythonProcess.kill();
}

// 启动测试
runTests().catch(err => {
  console.error('[TEST] Error running tests:', err);
  pythonProcess.kill();
});
