# 测试与验证流程

## 1. 测试框架概述

### 1.1 测试分层
- **单元测试**：测试单个函数或模块的功能
- **集成测试**：测试多个模块之间的交互
- **端到端测试**：测试完整的用户流程

### 1.2 技术栈
- **Python 单元测试**：`unittest` 或 `pytest`（现有代码使用的是简单断言）
- **前端集成测试**：`Cypress` 或 `Playwright`
- **性能测试**：`PyPerformance`（Python）和浏览器开发者工具（前端）

## 2. Python 单元测试

### 2.1 现有测试分析
已存在的测试文件：`../test/test_excelbox_plugins.py`
- ✅ `merge-excel`：合并Excel文件功能测试
- ✅ `delete-duplicate-rows`：删除重复行功能测试
- ✅ `delete-formula`：删除公式功能测试
- ✅ `generate-from-template`：模板生成功能测试

### 2.2 待完善的测试
- ❌ `replace-content`：按规则修改Excel内容
- ❌ `import-rules`：导入Excel规则修改内容
- ❌ `replace-picture`：替换Excel中的图片
- ❌ `url-to-image`：Excel中图片地址转为图片
- ❌ `remove-empty-row`：删除Excel空白内容

### 2.3 测试用例设计

#### 2.3.1 replace-content 插件测试
```python
def test_replace_content_basic():
    """测试基本的内容替换功能。"""
    from plugins.replace-content.worker import process
    import io
    
    # 构造测试工作簿
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(["姓名", "课程", "成绩"])
    ws.append(["张三", "数学", "90"])
    ws.append(["李四", "英语", "85"])
    
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    
    data = {
        "file": buf.getvalue(),
        "fileName": "test.xlsx",
        "settings": {
            "replacementRules": [
                {"findText": "数学", "replaceText": "高等数学", "matchMode": "normal"}
            ],
            "sheetOption": "all"
        }
    }
    
    result = process(data)
    assert result["success"] is True, f"替换失败: {result.get('error')}"
    assert result["buffer"], "替换结果 buffer 为空"
    
    # 验证替换结果
    wb = openpyxl.load_workbook(io.BytesIO(result["buffer"]))
    ws = wb["Sheet1"]
    assert ws.cell(row=2, column=2).value == "高等数学", "内容替换失败"
    wb.close()
```

#### 2.3.2 remove-empty-row 插件测试
```python
def test_remove_empty_rows_basic():
    """测试删除空白行功能。"""
    from plugins.remove-empty-row.worker import process
    import io
    
    # 构造测试工作簿
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(["姓名", "课程", "成绩"])
    ws.append([])  # 空行
    ws.append(["张三", "数学", "90"])
    ws.append([])  # 空行
    ws.append(["李四", "英语", "85"])
    
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    
    data = {
        "file": buf.getvalue(),
        "fileName": "test.xlsx",
        "settings": {
            "sheetOption": "all",
            "removeEmptyRows": True
        }
    }
    
    result = process(data)
    assert result["success"] is True, f"删除空白行失败: {result.get('error')}"
    assert result["buffer"], "处理结果 buffer 为空"
    
    # 验证结果
    wb = openpyxl.load_workbook(io.BytesIO(result["buffer"]))
    ws = wb["Sheet1"]
    assert ws.max_row == 3, f"预期 3 行，实际 {ws.max_row} 行"
    wb.close()
```

### 2.4 测试运行方式
```bash
# 在 excelbox 根目录下运行
python ../test/test_excelbox_plugins.py
```

## 3. 前端集成测试

### 3.1 测试工具选择
推荐使用 `Cypress` 进行前端集成测试，因为它：
- 易于安装和配置
- 提供可视化的测试运行界面
- 支持 Electron 应用测试
- 提供丰富的断言和操作API

### 3.2 测试场景设计

#### 3.2.1 基本的文件上传和处理流程
```javascript
describe('Excel 工具基本功能测试', () => {
  it('应该能上传文件并完成基本处理', () => {
    // 访问首页
    cy.visit('http://localhost:5173/')
    
    // 点击第一个插件 "按规则修改 Excel 内容"
    cy.contains('按规则修改 Excel 内容').click()
    
    // 验证插件页面是否加载成功
    cy.url().should('include', '/plugin/replace-content')
    cy.contains('按规则修改 Excel 内容')
    
    // 上传测试文件
    cy.get('input[type="file"]').attachFile('../test/课程信息表1.xlsx')
    
    // 验证文件是否上传成功
    cy.get('.ant-table-row').should('have.length', 1)
    cy.get('.ant-table-row').contains('课程信息表1.xlsx')
    
    // 点击下一步
    cy.get('.ant-btn-primary').contains('下一步').click()
    
    // 设置替换规则
    cy.get('.ant-input').eq(0).type('数学')
    cy.get('.ant-input').eq(1).type('高等数学')
    
    // 点击下一步
    cy.get('.ant-btn-primary').contains('下一步').click()
    
    // 设置输出目录
    cy.get('.ant-select-selector').click()
    cy.get('.ant-select-item-option-content').contains('与源文件相同目录').click()
    
    // 点击开始处理
    cy.get('.ant-btn-primary').contains('开始处理').click()
    
    // 验证处理是否完成
    cy.contains('处理完成', { timeout: 60000 })
    cy.contains('成功').should('be.visible')
  })
})
```

#### 3.2.2 错误处理测试
```javascript
describe('错误处理测试', () => {
  it('应该能正确处理无效的 Excel 文件', () => {
    // 访问插件页面
    cy.visit('http://localhost:5173/plugin/replace-content')
    
    // 上传非 Excel 文件
    cy.get('input[type="file"]').attachFile('../test/invalid.txt')
    
    // 点击下一步
    cy.get('.ant-btn-primary').contains('下一步').click()
    
    // 验证错误提示
    cy.contains('文件格式错误').should('be.visible')
    cy.contains('错误日志').should('be.visible')
  })
})
```

### 3.3 测试配置
创建 `cypress.json` 配置文件：
```json
{
  "baseUrl": "http://localhost:5173",
  "integrationFolder": "cypress/integration",
  "fixturesFolder": "cypress/fixtures",
  "supportFile": "cypress/support/index.js",
  "pluginsFile": "cypress/plugins/index.js",
  "screenshotsFolder": "cypress/screenshots",
  "videosFolder": "cypress/videos",
  "video": true,
  "viewportWidth": 1280,
  "viewportHeight": 720
}
```

## 4. 性能测试

### 4.1 Python 性能测试
```python
def test_performance_large_file():
    """测试处理大文件的性能。"""
    from plugins.replace-content.worker import process
    import time
    
    # 使用真实的大文件进行测试
    file_bytes = load_bytes("large_file.xlsx")  # 假设存在一个大文件
    
    data = {
        "file": file_bytes,
        "fileName": "large_file.xlsx",
        "settings": {
            "replacementRules": [
                {"findText": "测试", "replaceText": "生产", "matchMode": "normal"}
            ]
        }
    }
    
    start_time = time.time()
    result = process(data)
    end_time = time.time()
    
    assert result["success"] is True, f"处理失败: {result.get('error')}"
    print(f"处理大文件耗时: {end_time - start_time:.2f} 秒")
    
    # 性能指标：处理 10MB 文件应在 30 秒内完成
    assert end_time - start_time < 30, "处理时间过长"
```

### 4.2 前端性能测试
使用 Chrome 开发者工具的 Performance 面板进行测试：
1. 记录从点击"开始处理"到处理完成的整个过程
2. 分析 CPU 使用率、内存占用和页面响应时间
3. 重点关注 Pyodide 加载时间和 Python 脚本执行时间

## 5. 测试数据管理

### 5.1 测试数据结构
```
test/
├── 基础测试数据/
│   ├── 课程信息表1.xlsx
│   ├── 课程信息表2.xlsx
│   └── 课程信息表3.xlsx
├── 特殊场景测试数据/
│   ├── 空白单元格.xlsx
│   ├── 公式单元格.xlsx
│   └── 图片嵌入.xlsx
├── 性能测试数据/
│   └── large_file.xlsx (10MB+)
└── test_excelbox_plugins.py
```

### 5.2 数据生成脚本
创建 `generate_test_data.py` 用于生成测试数据：
```python
import openpyxl
import os
import random

# 生成包含大量数据的 Excel 文件
def generate_large_file(file_path, rows=10000, cols=10):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    
    # 生成表头
    headers = [f"Column_{i+1}" for i in range(cols)]
    ws.append(headers)
    
    # 生成数据行
    for _ in range(rows):
        row = [random.randint(1, 1000) for _ in range(cols)]
        ws.append(row)
    
    wb.save(file_path)
    print(f"生成文件: {file_path}, 大小: {os.path.getsize(file_path)/1024/1024:.2f} MB")

if __name__ == "__main__":
    generate_large_file("../test/performance/large_file.xlsx", 10000, 10)
```

## 6. 测试执行与报告

### 6.1 测试执行脚本
创建 `run_tests.sh` 或 `run_tests.bat` 用于批量执行测试：
```bash
#!/bin/bash

echo "开始执行 Python 单元测试..."
python ../test/test_excelbox_plugins.py

if [ $? -eq 0 ]; then
    echo "Python 单元测试通过！"
else
    echo "Python 单元测试失败！"
    exit 1
fi

echo "\n开始执行前端集成测试..."
npx cypress run

if [ $? -eq 0 ]; then
    echo "前端集成测试通过！"
else
    echo "前端集成测试失败！"
    exit 1
fi

echo "\n所有测试通过！"
```

### 6.2 测试报告
使用 `pytest-html` 生成 Python 测试报告：
```bash
pip install pytest pytest-html
cd ../test
pytest test_excelbox_plugins.py -v --html=test_report.html
```

## 7. 持续集成

### 7.1 GitHub Actions 配置
创建 `.github/workflows/test.yml`：
```yaml
name: Test

on: [push, pull_request]

jobs:
  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install openpyxl pandas pillow
      - name: Run Python tests
        run: |
          cd excelbox
          python ../test/test_excelbox_plugins.py

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "18"
      - name: Install dependencies
        run: |
          cd excelbox
          npm install
      - name: Build frontend
        run: |
          cd excelbox
          npm run build
      - name: Run frontend tests
        run: |
          cd excelbox
          npm run test:e2e
```

## 8. 测试验证流程

### 8.1 功能验证清单

| 插件名称 | 功能描述 | 验证方法 | 预期结果 |
|----------|----------|----------|----------|
| replace-content | 按规则修改 Excel 内容 | 上传文件并设置替换规则 | 内容被正确替换 |
| delete-duplicate-rows | 删除重复行 | 上传包含重复行的文件 | 重复行被删除 |
| delete-formula | 删除公式 | 上传包含公式的文件 | 公式被替换为值 |
| generate-from-template | 模板生成 | 上传模板和数据文件 | 生成符合模板的文件 |
| merge-excel | 合并Excel | 上传多个Excel文件 | 文件被正确合并 |
| replace-picture | 替换图片 | 上传包含图片的文件 | 图片被正确替换 |
| url-to-image | 地址转图片 | 上传包含图片URL的文件 | URL转为图片 |
| remove-empty-row | 删除空白行 | 上传包含空白行的文件 | 空白行被删除 |

### 8.2 性能验证清单

| 指标 | 预期值 | 验证方法 |
|------|--------|----------|
| Pyodide 加载时间 | < 30 秒 | 浏览器开发者工具 |
| 1MB 文件处理时间 | < 5 秒 | 性能测试脚本 |
| 10MB 文件处理时间 | < 30 秒 | 性能测试脚本 |
| 内存占用 | < 500 MB | 浏览器开发者工具 |

### 8.3 兼容性验证清单

| 平台 | 浏览器 | Excel 版本 | 预期结果 |
|------|--------|------------|----------|
| Windows | Chrome | 2013-2021 | 正常工作 |
| Windows | Edge | 2013-2021 | 正常工作 |
| macOS | Safari | 2016-2021 | 正常工作 |
| macOS | Chrome | 2016-2021 | 正常工作 |

## 9. 文档与维护

### 9.1 测试文档更新
- 每次插件功能变更时，更新对应的测试用例
- 记录测试结果和发现的问题
- 定期评审测试覆盖范围

### 9.2 测试环境维护
- 保持测试环境与生产环境一致
- 定期更新测试数据
- 维护测试工具和依赖版本

## 10. 下一步计划

1. 完善所有插件的单元测试
2. 设置前端集成测试环境
3. 实现性能测试自动化
4. 配置持续集成流程
5. 建立测试结果报告机制