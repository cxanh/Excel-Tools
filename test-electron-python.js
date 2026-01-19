/**
 * 测试 Electron 和 Python 后端连接
 */

const { spawn } = require('child_process');
const path = require('path');

console.log('=== 测试 Electron-Python 连接 ===\n');

// 1. 测试 Python 是否可用
console.log('1. 检查 Python...');
const pythonCheck = spawn('python', ['--version']);

pythonCheck.stdout.on('data', (data) => {
  console.log('   ✓ Python 版本:', data.toString().trim());
});

pythonCheck.stderr.on('data', (data) => {
  console.log('   ✓ Python 版本:', data.toString().trim());
});

pythonCheck.on('close', (code) => {
  if (code === 0) {
    console.log('   ✓ Python 可用\n');
    
    // 2. 测试 Python 后端启动
    console.log('2. 启动 Python 后端...');
    const scriptPath = path.join(__dirname, 'python-backend', 'main.py');
    console.log('   脚本路径:', scriptPath);
    
    const pythonProcess = spawn('python', [scriptPath], {
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    let startupReceived = false;
    
    pythonProcess.stdout.on('data', (data) => {
      const lines = data.toString().split('\n');
      for (const line of lines) {
        if (line.trim()) {
          try {
            const message = JSON.parse(line);
            console.log('   ✓ 收到消息:', message);
            
            if (message.type === 'startup' && message.status === 'ready') {
              startupReceived = true;
              console.log('   ✓ 后端启动成功！\n');
              
              // 3. 测试发送命令
              console.log('3. 测试发送命令...');
              const testCommand = {
                action: 'test',
                params: {}
              };
              console.log('   发送命令:', testCommand);
              pythonProcess.stdin.write(JSON.stringify(testCommand) + '\n');
              
              // 等待 2 秒后关闭
              setTimeout(() => {
                console.log('\n4. 测试完成，关闭进程...');
                pythonProcess.kill();
                process.exit(0);
              }, 2000);
            }
          } catch (e) {
            console.log('   ✗ JSON 解析失败:', line);
          }
        }
      }
    });
    
    pythonProcess.stderr.on('data', (data) => {
      console.log('   [Python Log]', data.toString().trim());
    });
    
    pythonProcess.on('error', (err) => {
      console.error('   ✗ 进程错误:', err);
      process.exit(1);
    });
    
    pythonProcess.on('exit', (code) => {
      console.log('   Python 进程退出，代码:', code);
      if (!startupReceived) {
        console.error('   ✗ 未收到启动消息！');
        process.exit(1);
      }
    });
    
    // 超时检测
    setTimeout(() => {
      if (!startupReceived) {
        console.error('   ✗ 超时：10秒内未收到启动消息');
        pythonProcess.kill();
        process.exit(1);
      }
    }, 10000);
    
  } else {
    console.error('   ✗ Python 不可用');
    process.exit(1);
  }
});

pythonCheck.on('error', (err) => {
  console.error('   ✗ 无法运行 Python:', err.message);
  console.error('   请确保已安装 Python 并添加到 PATH');
  process.exit(1);
});
