/**
 * 使用真实 Excel 文件测试完整流程
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('🔍 测试完整的 Excel 处理流程...\n');

// 检查是否有测试文件
const testFiles = [
  'test.xlsx',
  'sample.xlsx',
  'data.xlsx'
];

let testFile = null;
for (const file of testFiles) {
  if (fs.existsSync(file)) {
    testFile = file;
    break;
  }
}

if (!testFile) {
  console.log('⚠️  未找到测试 Excel 文件');
  console.log('💡 请在项目根目录放置一个 Excel 文件（test.xlsx 或 sample.xlsx）');
  console.log('   或者指定一个现有的 Excel 文件路径\n');
  
  // 尝试查找任何 .xlsx 文件
  const files = fs.readdirSync('.');
  const xlsxFiles = files.filter(f => f.endsWith('.xlsx') || f.endsWith('.xls'));
  
  if (xlsxFiles.length > 0) {
    testFile = xlsxFiles[0];
    console.log(`✅ 找到文件: ${testFile}\n`);
  } else {
    console.log('❌ 当前目录没有 Excel 文件');
    console.log('   测试将使用不存在的文件来验证错误处理\n');
    testFile = 'nonexistent.xlsx';
  }
}

console.log(`📄 测试文件: ${testFile}`);
console.log(`📂 完整路径: ${path.resolve(testFile)}\n`);

// 启动 Python 进程
const pythonProcess = spawn('python', [path.join(__dirname, 'python-backend', 'main.py')], {
  stdio: ['pipe', 'pipe', 'pipe']
});

let currentWorkbook = null;

// 监听 stdout
pythonProcess.stdout.on('data', (data) => {
  const lines = data.toString().split('\n');
  for (const line of lines) {
    if (line.trim()) {
      try {
        const message = JSON.parse(line);
        
        if (message.type === 'startup') {
          console.log('✅ 后端启动成功\n');
          
          // 测试 1: 加载文件
          setTimeout(() => {
            console.log('📤 测试 1: 加载 Excel 文件');
            const command = {
              action: 'load_file',
              params: {
                file_path: path.resolve(testFile)
              }
            };
            pythonProcess.stdin.write(JSON.stringify(command) + '\n');
          }, 500);
          
        } else if (message.type === 'result') {
          console.log(`\n📨 收到响应: ${message.status}`);
          
          if (message.status === 'success') {
            console.log('✅ 操作成功!');
            
            if (message.data) {
              console.log('\n📊 文件信息:');
              console.log(`   文件名: ${message.data.file_name || 'N/A'}`);
              console.log(`   格式: ${message.data.file_format || 'N/A'}`);
              console.log(`   大小: ${message.data.file_size ? (message.data.file_size / 1024).toFixed(2) + ' KB' : 'N/A'}`);
              console.log(`   工作表数: ${message.data.sheet_count || 0}`);
              
              if (message.data.sheets && message.data.sheets.length > 0) {
                console.log('\n📋 工作表列表:');
                message.data.sheets.forEach((sheet, index) => {
                  console.log(`   ${index + 1}. ${sheet.name} (${sheet.max_row} 行 × ${sheet.max_column} 列)`);
                });
              }
              
              currentWorkbook = message.data;
              
              // 测试 2: 获取文件属性
              setTimeout(() => {
                console.log('\n📤 测试 2: 获取文件属性');
                const command = {
                  action: 'get_properties',
                  params: {}
                };
                pythonProcess.stdin.write(JSON.stringify(command) + '\n');
              }, 1000);
            }
            
          } else {
            console.log('⚠️  操作失败');
            console.log(`   错误代码: ${message.error_code || 'UNKNOWN'}`);
            console.log(`   错误信息: ${message.message}`);
            if (message.suggested_action) {
              console.log(`   建议: ${message.suggested_action}`);
            }
            
            // 如果是文件不存在，这是预期的
            if (message.error_code === 'FILE_NOT_FOUND') {
              console.log('\n✅ 错误处理正常工作！');
            }
            
            // 结束测试
            setTimeout(() => {
              console.log('\n🎉 测试完成！');
              pythonProcess.kill();
              process.exit(0);
            }, 1000);
          }
        } else if (message.type === 'progress') {
          console.log(`⏳ 进度: ${message.progress}% - ${message.message}`);
        }
        
      } catch (e) {
        console.error('❌ 解析消息失败:', line);
      }
    }
  }
});

// 监听 stderr
pythonProcess.stderr.on('data', (data) => {
  const log = data.toString().trim();
  if (log) {
    console.log('📋 后端日志:', log);
  }
});

// 监听进程退出
pythonProcess.on('exit', (code) => {
  console.log(`\n🔚 进程退出，代码: ${code}`);
});

// 监听进程错误
pythonProcess.on('error', (err) => {
  console.error('❌ 进程错误:', err.message);
  process.exit(1);
});

// 超时
setTimeout(() => {
  console.log('\n⏰ 测试超时，关闭进程');
  pythonProcess.kill();
  process.exit(0);
}, 20000);
