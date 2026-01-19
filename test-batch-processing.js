#!/usr/bin/env node
/**
 * 批量处理功能测试脚本
 * 测试批量处理多个 Excel 文件
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// 测试文件路径
const TEST_FILES = [
  path.join(__dirname, 'test.xlsx'),
  path.join(__dirname, 'test.xlsx'),  // 使用同一个文件测试
  path.join(__dirname, 'test.xlsx'),
];

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
let batchProgressUpdates = [];

// 监听 stdout（JSON 响应）
pythonProcess.stdout.on('data', (data) => {
  const lines = data.toString().split('\n');
  for (const line of lines) {
    if (line.trim()) {
      try {
        const message = JSON.parse(line);
        
        if (message.type === 'batch_progress') {
          console.log(`[BATCH PROGRESS] ${message.progress}% - ${message.message}`);
          if (message.data) {
            console.log(`  Current: ${message.data.current_file} (${message.data.current_file_index}/${message.data.total_files})`);
          }
          batchProgressUpdates.push(message);
        } else if (message.type === 'result') {
          console.log(`[RESULT] ${message.status}: ${message.message}`);
          if (message.data) {
            console.log(`[DATA]`, JSON.stringify(message.data, null, 2));
          }
          testResults.push({
            test: currentTest,
            status: message.status,
            message: message.message,
            data: message.data
          });
        } else {
          console.log(`[PYTHON]`, JSON.stringify(message, null, 2));
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
    const status = result.status === 'success' || result.status === 'partial_success' ? '✓' : '✗';
    const color = result.status === 'success' || result.status === 'partial_success' ? '\x1b[32m' : '\x1b[31m';
    console.log(`${color}${status}\x1b[0m ${index + 1}. ${result.test}`);
    console.log(`   ${result.message}`);
    
    if (result.data && result.data.results) {
      console.log(`   详细结果:`);
      result.data.results.forEach((fileResult, idx) => {
        const fileStatus = fileResult.status === 'success' ? '✓' : '✗';
        const fileColor = fileResult.status === 'success' ? '\x1b[32m' : '\x1b[31m';
        console.log(`     ${fileColor}${fileStatus}\x1b[0m ${fileResult.file_name} - ${fileResult.message} (${fileResult.duration}ms)`);
      });
    }
    
    if (result.status === 'success' || result.status === 'partial_success') {
      successCount++;
    } else {
      failCount++;
    }
  });
  
  console.log('='.repeat(60));
  console.log(`批量进度更新次数: ${batchProgressUpdates.length}`);
  console.log(`总计: ${testResults.length} 个测试`);
  console.log(`\x1b[32m成功: ${successCount}\x1b[0m`);
  console.log(`\x1b[31m失败: ${failCount}\x1b[0m`);
  console.log('='.repeat(60));
}

// 运行测试
async function runTests() {
  console.log('[TEST] Starting batch processing tests...\n');
  
  // 等待后端启动
  await delay(2000);
  
  // 测试 1: 批量删除空白行
  currentTest = '批量删除空白行（3个文件）';
  sendCommand({
    action: 'batch_process',
    params: {
      files: TEST_FILES,
      operation: 'remove_blank_rows',
      operation_params: {},
      save_files: false  // 不保存，避免修改测试文件
    }
  });
  await delay(5000);
  
  // 测试 2: 批量清除空白单元格
  currentTest = '批量清除空白单元格（3个文件）';
  sendCommand({
    action: 'batch_process',
    params: {
      files: TEST_FILES,
      operation: 'clear_blank_cells',
      operation_params: {},
      save_files: false
    }
  });
  await delay(5000);
  
  // 测试 3: 批量删除公式
  currentTest = '批量删除公式（3个文件）';
  sendCommand({
    action: 'batch_process',
    params: {
      files: TEST_FILES,
      operation: 'remove_formulas',
      operation_params: {},
      save_files: false
    }
  });
  await delay(5000);
  
  // 测试 4: 批量处理不存在的文件（应该部分失败）
  currentTest = '批量处理包含不存在的文件（应该部分失败）';
  sendCommand({
    action: 'batch_process',
    params: {
      files: [
        TEST_FILES[0],
        path.join(__dirname, 'nonexistent.xlsx'),
        TEST_FILES[1]
      ],
      operation: 'remove_blank_rows',
      operation_params: {},
      save_files: false
    }
  });
  await delay(5000);
  
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
