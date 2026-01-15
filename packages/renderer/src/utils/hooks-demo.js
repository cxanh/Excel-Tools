// Hook 使用示例演示
import { userPromptSubmitHook, stopEventHook } from './hooks.js';

// 示例 1: 使用 UserPromptSubmit Hook
// 模拟用户输入
const userPrompt = '我需要修复replace-content插件中的错误，当处理多个文件时会崩溃';

console.log('\n========================================');
console.log('🎯 示例 1: UserPromptSubmit Hook 演示');
console.log('========================================');
console.log('用户输入:', userPrompt);

// 执行 UserPromptSubmit Hook
const enhancedContext = userPromptSubmitHook.execute(userPrompt);

console.log('\n🔧 增强后的上下文:');
console.log('检测到的技能:', enhancedContext.enhancedContext.analysis.detectedSkills);
console.log('关键词:', enhancedContext.enhancedContext.analysis.keywords);
console.log('检测到的意图:', enhancedContext.enhancedContext.analysis.detectedIntents);
console.log('\n💡 生成的提醒:');
enhancedContext.enhancedContext.reminders.forEach(reminder => console.log(reminder));

// 示例 2: 使用 Stop Event Hook
// 模拟编辑的文件
const editedFiles = [
  {
    path: 'plugins/replace-content/index.vue',
    content: `
<template>
  <div class="replace-content">
    <!-- 组件内容 -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { runPy } from '@/utils/py';

const files = ref([]);
const isProcessing = ref(false);
const logs = ref([]);

// 处理文件
const processFiles = async () => {
  if (files.value.length === 0) return;

  isProcessing.value = true;
  logs.value = ['开始处理文件...'];
  
  try {
    const script = await getPythonScript();
    
    for (let i = 0; i < files.value.length; i++) {
      const fileItem = files.value[i];
      logs.value.push(`正在处理文件：${fileItem.name}`);
      
      const processingData = {
        file: fileItem.file,
        fileName: fileItem.name,
        settings: settings.value
      };
      
      const result = await runPy(script, processingData);
      logs.value.push(`${fileItem.name} 处理完成！`);
    }
    
    logs.value.push('所有文件处理完成！');
  } catch (error) {
    logs.value.push(`错误：${error.message}`);
    console.error('Processing error:', error);
  } finally {
    isProcessing.value = false;
  }
};
</script>`
  },
  {
    path: 'plugins/replace-content/worker.py',
    content: `
import openpyxl
import io
import json

# 处理Excel文件
def process(input_data):
    try:
        # 读取文件
        file_content = input_data['file']
        workbook = openpyxl.load_workbook(io.BytesIO(file_content))
        
        # 获取替换规则
        rules = input_data['settings']['replacementRules']
        
        # 处理每个工作表
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            
            # 遍历所有单元格
            for row in sheet.iter_rows():
                for cell in row:
                    if cell.value:
                        for rule in rules:
                            if rule['findText'] in str(cell.value):
                                cell.value = str(cell.value).replace(rule['findText'], rule['replaceText'])
        
        # 保存结果
        output_stream = io.BytesIO()
        workbook.save(output_stream)
        output_stream.seek(0)
        
        return {
            'success': True,
            'buffer': output_stream.getvalue(),
            'logs': ['文件处理成功']
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'logs': [f'处理失败: {str(e)}']
        }
`
  }
];

// 执行 Stop Event Hook
const stopEventResult = stopEventHook.execute(editedFiles);

console.log('\n\n========================================');
console.log('🎯 示例 2: Stop Event Hook 演示');
console.log('========================================');
console.log('模拟编辑的文件:');
editedFiles.forEach(file => console.log(`  - ${file.path}`));

console.log('\n🔍 分析结果:');
console.log('编辑的文件数:', stopEventResult.analysis.totalFiles);
console.log('文件类型:', stopEventResult.analysis.fileTypes);
console.log('检测到的风险模式:');
for (const [pattern, count] of Object.entries(stopEventResult.analysis.riskPatterns)) {
  console.log(`  - ${stopEventHook.formatPatternName(pattern)}: ${count} 处`);
}

console.log('\n🔔 自查提醒:');
stopEventResult.reminders.forEach(reminder => console.log(reminder));

console.log('\n\n========================================');
console.log('✅ Hook 演示完成');
console.log('========================================');

// 示例 3: 集成到实际工作流中
console.log('\n\n========================================');
console.log('🎯 示例 3: 实际工作流集成');
console.log('========================================');

const integratedWorkflow = async (userInput) => {
  console.log('1. 用户输入:', userInput);
  
  // Step 1: 执行 UserPromptSubmit Hook
  const enhancedContext = userPromptSubmitHook.execute(userInput);
  console.log('2. 增强上下文完成');
  
  // Step 2: 模拟Claude处理
  console.log('3. Claude 正在处理请求...');
  // 这里是Claude的实际处理逻辑
  
  // Step 3: 模拟生成的响应和编辑的文件
  const generatedResponse = '我已经修复了replace-content插件中的错误，主要是在处理多文件时没有正确初始化状态';
  const simulatedEditedFiles = editedFiles;
  
  console.log('4. Claude 处理完成，响应:', generatedResponse);
  
  // Step 4: 执行 Stop Event Hook
  stopEventHook.execute(simulatedEditedFiles);
  
  console.log('5. 工作流完成');
};

// 运行集成工作流
integratedWorkflow('修复replace-content插件中的多文件处理错误');
