<template>
  <PluginTemplate
    :title="'添加 Excel 文字水印'"
    :description="'为 Excel 文件批量添加文字水印，支持自定义内容、样式、位置和透明度'"
    :hasHelp="true"
  >
    <template #step1-content>
      <div class="step-content">
        <a-form layout="vertical" class="setting-form">
          <a-form-item label="水印内容">
            <a-input
              v-model:value="watermarkText"
              placeholder="请输入水印内容"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="字体大小">
            <a-input-number
              v-model:value="fontSize"
              :min="8"
              :max="72"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="字体颜色">
            <a-input
              v-model:value="fontColor"
              placeholder="请输入颜色代码，如：#CCCCCC"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="透明度（0-1）">
            <a-slider
              v-model:value="opacity"
              :min="0"
              :max="1"
              :step="0.1"
            />
            <div style="margin-top: 8px; text-align: center;">{{ opacity }}</div>
          </a-form-item>
          <a-form-item label="旋转角度（度）">
            <a-input-number
              v-model:value="rotation"
              :min="-180"
              :max="180"
              style="width: 100%"
            />
          </a-form-item>
        </a-form>
      </div>
    </template>

    <template #step2-extra>
      <!-- 这里可以添加额外的选项，如处理范围等 -->
    </template>

    <template #step3-extra>
      <!-- 这里可以添加额外的输出选项 -->
    </template>

    <template #help-content>
      <div class="help-content">
        <h3>功能说明</h3>
        <p>本工具可以为 Excel 文件批量添加文字水印，支持自定义内容、样式、位置和透明度。</p>
        <h3>使用步骤</h3>
        <ol>
          <li>设置水印内容、字体大小、颜色、透明度和旋转角度</li>
          <li>选择要处理的 Excel 文件</li>
          <li>选择输出目录</li>
          <li>点击开始处理，等待处理完成</li>
        </ol>
        <h3>注意事项</h3>
        <ul>
          <li>支持处理 .xlsx 和 .xls 格式的 Excel 文件</li>
          <li>处理后的文件会保存在指定的输出目录</li>
          <li>建议使用浅色水印，避免影响原文件内容的可读性</li>
        </ul>
      </div>
    </template>
  </PluginTemplate>
</template>

<script setup>
import { ref, reactive } from 'vue';
import PluginTemplate from '@plugins/plugin-template/index.vue';
import { runPy } from '@utils/py';

// 水印设置
const watermarkText = ref('示例水印');
const fontSize = ref(36);
const fontColor = ref('#CCCCCC');
const opacity = ref(0.5);
const rotation = ref(-30);

// 定义处理函数
const processFiles = async (files, outputDir, selectedSheets = null) => {
  // 准备水印设置参数
  const watermarkSettings = {
    text: watermarkText.value,
    font_size: fontSize.value,
    font_color: fontColor.value,
    opacity: opacity.value,
    rotation: rotation.value
  };

  // 构建Python脚本
  const pythonCode = `
import os
import sys
from openpyxl import load_workbook
from openpyxl.drawing.text import RichTextProperties, Paragraph, ParagraphProperties, CharacterProperties
from openpyxl.drawing.shapes import ShapeStyle
from openpyxl.worksheet.drawing import Drawing, Shape
from openpyxl.utils.units import pixels_to_EMU
from PIL import Image, ImageDraw, ImageFont
import io

# 设置中文支持
sys.stdout.reconfigure(encoding='utf-8')

def add_watermark_to_sheet(sheet, watermark_settings):
    """为单个工作表添加水印"""
    # 获取工作表尺寸
    max_row = sheet.max_row
    max_col = sheet.max_column
    
    # 如果工作表为空，跳过
    if max_row == 1 and max_col == 1 and sheet.cell(row=1, column=1).value is None:
        return
    
    # 创建水印图片
    img_width, img_height = 300, 200
    img = Image.new('RGBA', (img_width, img_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 尝试使用系统字体，支持中文
    try:
        font = ImageFont.truetype('simhei.ttf', watermark_settings['font_size'])
    except:
        font = ImageFont.load_default()
    
    # 设置水印文本
    text = watermark_settings['text']
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
    
    # 计算文本位置（居中）
    x = (img_width - text_width) / 2
    y = (img_height - text_height) / 2
    
    # 设置文本颜色和透明度
    font_color = watermark_settings['font_color']
    opacity = int(watermark_settings['opacity'] * 255)
    
    # 将十六进制颜色转换为RGB
    rgb_color = tuple(int(font_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (opacity,)
    
    # 绘制水印文本
    draw.text((x, y), text, font=font, fill=rgb_color)
    
    # 旋转水印
    img = img.rotate(watermark_settings['rotation'], expand=True, resample=Image.BICUBIC)
    
    # 将PIL图像转换为字节流
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    # 创建Drawing对象
    drawing = Drawing()
    drawing.width = img_width
    drawing.height = img_height
    
    # 设置水印位置（覆盖整个工作表）
    drawing.left = 0
    drawing.top = 0
    
    # 将水印添加到工作表
    sheet.add_image(img_byte_arr, 'A1')
    
    print(f"  已为工作表 '{sheet.title}' 添加水印")

def add_watermark_to_file(file_path, output_path, watermark_settings):
    """为单个Excel文件添加水印"""
    print(f"正在处理文件: {file_path}")
    
    try:
        # 加载工作簿
        wb = load_workbook(file_path)
        
        # 为每个工作表添加水印
        for sheet in wb.worksheets:
            add_watermark_to_sheet(sheet, watermark_settings)
        
        # 保存文件
        wb.save(output_path)
        print(f"  文件处理完成，保存到: {output_path}")
        return True
    except Exception as e:
        print(f"  处理文件 {file_path} 时出错: {str(e)}")
        return False

# 主函数
if __name__ == "__main__":
    import json
    
    # 解析命令行参数
    input_files = json.loads(sys.argv[1])
    output_dir = sys.argv[2]
    watermark_settings = json.loads(sys.argv[3])
    
    print(f"开始处理 {len(input_files)} 个文件...")
    
    success_count = 0
    error_count = 0
    
    for input_file in input_files:
        # 构建输出文件路径
        file_name = os.path.basename(input_file)
        output_file = os.path.join(output_dir, file_name)
        
        # 处理文件
        if add_watermark_to_file(input_file, output_file, watermark_settings):
            success_count += 1
        else:
            error_count += 1
    
    print(f"\n处理完成！成功: {success_count} 个, 失败: {error_count} 个")
    `;

  try {
    // 调用Python脚本处理文件
    const result = await runPy(
      pythonCode,
      [files, outputDir, watermarkSettings],
      '添加水印'
    );
    return result;
  } catch (error) {
    console.error('处理文件时出错:', error);
    throw error;
  }
};
</script>

<style scoped>
.step-content {
  padding: 0 20px;
}

.setting-form {
  max-width: 600px;
  margin: 0 auto;
}

.help-content {
  padding: 10px;
}

.help-content h3 {
  margin-top: 20px;
  margin-bottom: 10px;
  font-size: 16px;
  font-weight: 500;
}

.help-content p,
.help-content li {
  margin-bottom: 8px;
  line-height: 1.5;
}
</style>