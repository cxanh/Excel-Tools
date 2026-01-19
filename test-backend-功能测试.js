/**
 * 测试 Python 后端的完整功能
 * 测试文件加载、内容处理、文件保存等功能
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// 启动 Python 后端
const pythonPath = 'python';
const scriptPath = path.join(__dirname, 'python-backend', 'main.py');

console.log('启动 Python 后端...');
console.log('Python 路径:', pythonPath);
console.log('脚本路径:', scriptPath);

const pythonProcess = spawn(pythonPath, [scriptPath], {
  stdio: ['pipe', 'pipe', 'pipe'],
  env: {
    ...process.env,
    PYTHONIOENCODING: 'utf-8'
  }
});

// 监听 stdout（JSON 响应）
pythonProcess.stdout.on('data', (data) => {
  const lines = data.toString().split('\n');
  for (const line of lines) {
    if (line.trim()) {
      try {
        const message = JSON.parse(line);
        console.log('\n[收到响应]', JSON.stringify(message, null, 2));
        
        // 根据响应类型执行下一步测试
        if (message.type === 'startup') {
          console.log('\n✅ 后端启动成功！');
          console.log('\n开始测试...\n');
          runTests();
        }
      } catch (e) {
        console.error('[解析错误]', line);
      }
    }
  }
});

// 监听 stderr（日志）
pythonProcess.stderr.on('data', (data) => {
  console.log('[后端日志]', data.toString().trim());
});

// 监听进程退出
pythonProcess.on('exit', (code) => {
  console.log(`\n[进程退出] 退出码: ${code}`);
  process.exit(code);
});

// 监听进程错误
pythonProcess.on('error', (err) => {
  console.error('[进程错误]', err);
  process.exit(1);
});

/**
 * 发送命令到 Python 后端
 */
function sendCommand(action, params) {
  const command = { action, params };
  console.log(`\n[发送命令] ${action}`);
  console.log('参数:', JSON.stringify(params, null, 2));
  pythonProcess.stdin.write(JSON.stringify(command) + '\n');
}

/**
 * 运行测试
 */
let testStep = 0;
let testFilePath = '';

function runTests() {
  testStep++;
  
  switch (testStep) {
    case 1:
      console.log('=== 测试 1: 加载 Excel 文件 ===');
      // 使用项目中的测试文件
      testFilePath = path.join(__dirname, 'test.xlsx');
      
      if (!fs.existsSync(testFilePath)) {
        console.error('❌ 测试文件不存在:', testFilePath);
        console.log('请确保 test.xlsx 文件存在');
        pythonProcess.kill();
        return;
      }
      
      sendCommand('load_file', {
        file_path: testFilePath
      });
      
      // 等待响应后继续
      setTimeout(() => runTests(), 2000);
      break;
    
    case 2:
      console.log('\n=== 测试 2: 删除空白行 ===');
      sendCommand('remove_blank_rows', {});
      setTimeout(() => runTests(), 2000);
      break;
    
    case 3:
      console.log('\n=== 测试 3: 清除空白单元格 ===');
      sendCommand('clear_blank_cells', {});
      setTimeout(() => runTests(), 2000);
      break;
    
    case 4:
      console.log('\n=== 测试 4: 删除公式 ===');
      sendCommand('remove_formulas', {});
      setTimeout(() => runTests(), 2000);
      break;
    
    case 5:
      console.log('\n=== 测试 5: 替换内容 ===');
      sendCommand('replace_content', {
        find_text: '测试',
        replace_text: 'TEST',
        case_sensitive: false,
        use_regex: false
      });
      setTimeout(() => runTests(), 2000);
      break;
    
    case 6:
      console.log('\n=== 测试 6: 保存文件 ===');
      const outputPath = path.join(__dirname, 'test-output.xlsx');
      sendCommand('save_file', {
        file_path: outputPath,
        overwrite: true,
        create_backup: true
      });
      setTimeout(() => runTests(), 2000);
      break;
    
    case 7:
      console.log('\n=== 测试 7: 关闭文件 ===');
      sendCommand('close_file', {});
      setTimeout(() => {
        console.log('\n✅ 所有测试完成！');
        console.log('\n正在关闭...');
        setTimeout(() => {
          pythonProcess.kill();
        }, 1000);
      }, 2000);
      break;
    
    default:
      // 测试完成
      break;
  }
}

// 处理 Ctrl+C
process.on('SIGINT', () => {
  console.log('\n\n收到中断信号，正在关闭...');
  pythonProcess.kill();
  process.exit(0);
});
