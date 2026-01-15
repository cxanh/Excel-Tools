// Hook 1: UserPromptSubmit Hook
// 在 Claude 看到用户消息之前运行
class UserPromptSubmitHook {
  constructor() {
    this.skills = {
      'excel-processing': ['excel', '表格', 'xlsx', 'xls', '数据处理'],
      'file-operation': ['文件', '上传', '下载', '保存'],
      'image-processing': ['图片', '替换', '删除', '添加'],
      'code-modification': ['修改', '修复', '调试', '错误'],
      'project-management': ['分析', '架构', '设计', '规划'],
      'deployment': ['打包', '构建', '发布', '部署']
    };
  }

  // 分析用户提示词
  analyzePrompt(prompt) {
    const lowercasePrompt = prompt.toLowerCase();
    const detectedSkills = [];
    const keywords = [];

    // 检测相关技能
    for (const [skill, triggers] of Object.entries(this.skills)) {
      for (const trigger of triggers) {
        if (lowercasePrompt.includes(trigger)) {
          detectedSkills.push(skill);
          keywords.push(trigger);
        }
      }
    }

    // 检测意图模式
    const intentPatterns = {
      'bug-fix': lowercasePrompt.includes('错误') || lowercasePrompt.includes('修复') || lowercasePrompt.includes('调试'),
      'feature-request': lowercasePrompt.includes('添加') || lowercasePrompt.includes('实现') || lowercasePrompt.includes('开发'),
      'consultation': lowercasePrompt.includes('分析') || lowercasePrompt.includes('如何') || lowercasePrompt.includes('建议'),
      'troubleshooting': lowercasePrompt.includes('无法') || lowercasePrompt.includes('不工作') || lowercasePrompt.includes('问题')
    };

    const detectedIntents = Object.keys(intentPatterns).filter(key => intentPatterns[key]);

    return {
      detectedSkills: [...new Set(detectedSkills)], // 去重
      keywords: [...new Set(keywords)], // 去重
      detectedIntents,
      originalPrompt: prompt
    };
  }

  // 生成格式化提醒
  generateReminders(analysis) {
    const reminders = [];

    // 技能相关提醒
    if (analysis.detectedSkills.length > 0) {
      reminders.push(`⚠️ 检测到相关技能: ${analysis.detectedSkills.join(', ')}`);
      
      // 根据技能添加具体提醒
      if (analysis.detectedSkills.includes('excel-processing')) {
        reminders.push('💡 请确保考虑Excel文件格式兼容性(.xlsx/.xls)和大文件处理性能');
      }
      if (analysis.detectedSkills.includes('file-operation')) {
        reminders.push('💡 请确保处理文件路径和权限问题，特别是跨平台兼容性');
      }
      if (analysis.detectedSkills.includes('image-processing')) {
        reminders.push('💡 请考虑图片大小、格式和内存使用限制');
      }
      if (analysis.detectedSkills.includes('code-modification')) {
        reminders.push('💡 请确保代码修改符合项目现有风格和测试要求');
      }
    }

    // 意图相关提醒
    if (analysis.detectedIntents.length > 0) {
      if (analysis.detectedIntents.includes('bug-fix')) {
        reminders.push('🔍 请仔细分析错误堆栈和复现步骤，确保修复根本原因');
      }
      if (analysis.detectedIntents.includes('feature-request')) {
        reminders.push('🎯 请确保新功能符合项目整体架构和用户体验');
      }
      if (analysis.detectedIntents.includes('consultation')) {
        reminders.push('📊 请提供详细的分析和多种解决方案供用户选择');
      }
    }

    // 通用提醒
    reminders.push('✅ 请确保响应清晰、结构良好，并提供必要的代码示例和解释');
    reminders.push('🔒 请注意安全问题，特别是文件操作和权限管理');

    return reminders;
  }

  // 执行hook
  execute(prompt) {
    console.log('🔄 UserPromptSubmit Hook 正在执行...');
    const analysis = this.analyzePrompt(prompt);
    const reminders = this.generateReminders(analysis);
    
    // 格式化输出
    const formattedOutput = {
      analysis,
      reminders,
      timestamp: new Date().toISOString()
    };

    console.log('📋 Hook 分析结果:', JSON.stringify(formattedOutput, null, 2));
    
    // 返回增强的上下文
    return {
      originalPrompt: prompt,
      enhancedContext: {
        analysis,
        reminders,
        timestamp: formattedOutput.timestamp
      }
    };
  }
}

// Hook 2: Stop Event Hook
// 在 Claude 完成响应之后运行
class StopEventHook {
  constructor() {
    this.riskPatterns = {
      'try-catch': /try\s*\{[\s\S]*?\}catch\s*\([^)]*\)\s*\{[\s\S]*?\}/gi,
      'async-function': /async\s+function\s+\w+|const\s+\w+\s*=\s*async\s*\(|async\s*\(\)/gi,
      'database-operation': /connect|query|insert|update|delete|select|from|where|join/gi,
      'file-system': /fs\.|readFile|writeFile|appendFile|unlink|mkdir/gi,
      'external-api': /fetch|axios\.|http\.|https\./gi
    };
  }

  // 分析编辑的文件
  analyzeEditedFiles(files) {
    if (!files || files.length === 0) {
      return { totalFiles: 0, fileTypes: [], riskPatterns: {} };
    }

    const fileTypes = new Set();
    const allRiskPatterns = {};

    files.forEach(file => {
      // 提取文件类型
      const fileType = file.path.split('.').pop().toLowerCase();
      fileTypes.add(fileType);

      // 检查风险模式
      const fileRisks = {};
      for (const [patternName, regex] of Object.entries(this.riskPatterns)) {
        const matches = file.content.match(regex);
        if (matches) {
          fileRisks[patternName] = matches.length;
          allRiskPatterns[patternName] = (allRiskPatterns[patternName] || 0) + matches.length;
        }
      }

      file.risks = fileRisks;
    });

    return {
      totalFiles: files.length,
      fileTypes: Array.from(fileTypes),
      riskPatterns: allRiskPatterns,
      files
    };
  }

  // 生成自查提醒
  generateSelfCheckReminders(analysis) {
    const reminders = [];

    // 文件编辑提醒
    if (analysis.totalFiles > 0) {
      reminders.push(`📁 本次操作编辑了 ${analysis.totalFiles} 个文件`);
      reminders.push(`📝 文件类型: ${analysis.fileTypes.join(', ')}`);
    }

    // 风险模式提醒
    const riskCount = Object.keys(analysis.riskPatterns).length;
    if (riskCount > 0) {
      reminders.push('⚠️ 检测到以下风险模式:');
      for (const [pattern, count] of Object.entries(analysis.riskPatterns)) {
        reminders.push(`  - ${this.formatPatternName(pattern)}: ${count} 处`);
      }

      // 针对特定风险的提醒
      if (analysis.riskPatterns['try-catch']) {
        reminders.push('💡 请确保异常处理包含足够的日志记录和用户反馈');
      }
      if (analysis.riskPatterns['async-function']) {
        reminders.push('💡 请确保异步函数正确处理错误和取消操作');
      }
      if (analysis.riskPatterns['database-operation']) {
        reminders.push('💡 请确保数据库操作使用参数化查询并正确关闭连接');
      }
      if (analysis.riskPatterns['file-system']) {
        reminders.push('💡 请确保文件操作处理权限问题和路径安全');
      }
      if (analysis.riskPatterns['external-api']) {
        reminders.push('💡 请确保外部API调用包含超时处理和错误重试机制');
      }
    }

    // 通用提醒
    reminders.push('✅ 请再次检查代码是否符合项目的编码规范');
    reminders.push('🔍 请确保所有修改都经过充分测试');
    reminders.push('📋 请考虑添加或更新相关文档');

    return reminders;
  }

  // 格式化风险模式名称
  formatPatternName(pattern) {
    const patternNames = {
      'try-catch': '异常处理 (try-catch)',
      'async-function': '异步函数 (async/await)',
      'database-operation': '数据库操作',
      'file-system': '文件系统操作',
      'external-api': '外部API调用'
    };
    return patternNames[pattern] || pattern;
  }

  // 执行hook
  execute(editedFiles) {
    console.log('🔄 Stop Event Hook 正在执行...');
    const analysis = this.analyzeEditedFiles(editedFiles);
    const reminders = this.generateSelfCheckReminders(analysis);

    // 格式化输出
    const formattedOutput = {
      analysis,
      reminders,
      timestamp: new Date().toISOString()
    };

    console.log('📋 Hook 分析结果:', JSON.stringify(formattedOutput, null, 2));

    // 显示自查提醒
    this.displayReminders(reminders);

    return formattedOutput;
  }

  // 显示提醒
  displayReminders(reminders) {
    console.log('\n🔔 自查提醒:');
    reminders.forEach(reminder => {
      console.log(`  ${reminder}`);
    });
  }
}

// 导出Hook实例
const userPromptSubmitHook = new UserPromptSubmitHook();
const stopEventHook = new StopEventHook();

export { userPromptSubmitHook, stopEventHook };

export default {
  userPromptSubmitHook,
  stopEventHook
};