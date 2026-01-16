/**
 * 测试 Python 后端连接
 * 运行方式：node test-backend-connection.js
 */

const { spawn } = require('child_process');
const path = require('path');

console.log('🔍 测试 Python 后端连接...\n');

// 启动 Python 进程
const pythonPath = 'python';
const scriptPath = path.join(__dirname, 'python-backend', 'main.py');

console.log(`📂 Python 路径: ${pythonPath}`);
console.log(`📂 脚本路径: ${scriptPath}\n`);

const pythonProcess = spawn(pythonPath, [scriptPath], {
  stdio: ['pipe', 'pipe', 'pipe']
});

let startupReceived = false;
let testsPassed = 0;
let testsFailed = 0;

// 监听 stdout
pythonProcess.stdout.on('data', (data) => {
  const lines = data.toString().split('\n');
  for (const line of lines) {
    if (line.trim()) {
      try {
        const message = JSON.parse(line);
        console.log('📨 收到消息:', JSON.stringify(message, null, 2));
        
        if (message.type === 'startup' && message.status === 'ready') {
          console.log('✅ 后端启动成功！\n');
          startupReceived = true;
          
          // 发送测试命令
          setTimeout(() => {
            console.log('📤 发送测试命令: load_file\n');
            const testCommand = {
              action: 'load_file',
              params: {
                file_path: 'test.xlsx'
              }
            };
            pythonProcess.stdin.write(JSON.stringify(testCommand) + '\n');
          }, 500);
        } else if (message.type === 'result') {
          if (message.status === 'success') {
            console.log('✅ 测试通过！');
            testsPassed++;
          } else {
            console.log('⚠️  收到错误响应（这是正常的，因为文件不存在）');
            console.log('   错误信息:', message.message);
            testsPassed++; // 能收到错误响应也说明通信正常
          }
          
          // 测试完成，关闭进程
          setTimeout(() => {
            console.log('\n📊 测试结果:');
            console.log(`   ✅ 通过: ${testsPassed}`);
            console.log(`   ❌ 失败: ${testsFailed}`);
            console.log('\n🎉 前后端通信测试完成！');
            pythonProcess.kill();
            process.exit(0);
          }, 1000);
        }
      } catch (e) {
        console.error('❌ 解析消息失败:', line);
        console.error('   错误:', e.message);
        testsFailed++;
      }
    }
  }
});

// 监听 stderr
pythonProcess.stderr.on('data', (data) => {
  console.log('📋 后端日志:', data.toString().trim());
});

// 监听进程退出
pythonProcess.on('exit', (code) => {
  console.log(`\n🔚 Python 进程退出，代码: ${code}`);
  if (!startupReceived) {
    console.error('❌ 后端未能成功启动！');
    process.exit(1);
  }
});

// 监听进程错误
pythonProcess.on('error', (err) => {
  console.error('❌ Python 进程错误:', err.message);
  console.error('\n💡 可能的原因:');
  console.error('   1. Python 未安装或不在 PATH 中');
  console.error('   2. 依赖包未安装（运行: pip install -r python-backend/requirements.txt）');
  console.error('   3. Python 版本不兼容（需要 Python 3.7+）');
  process.exit(1);
});

// 超时检测
setTimeout(() => {
  if (!startupReceived) {
    console.error('\n❌ 后端启动超时（10秒）');
    console.error('💡 请检查:');
    console.error('   1. Python 是否正确安装');
    console.error('   2. 依赖包是否已安装');
    console.error('   3. 查看上方的错误日志');
    pythonProcess.kill();
    process.exit(1);
  }
}, 10000);
