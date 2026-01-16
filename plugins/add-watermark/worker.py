"""
添加水印插件 - Python处理脚本
为Excel文件添加文本或图片水印
"""

import sys
import json
import base64
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as OpenpyxlImage
from PIL import Image, ImageDraw, ImageFont


def create_text_watermark(text, width=800, height=600, font_size=48, color=(128, 128, 128), 
                          transparency=128, angle=-45):
    """
    创建文本水印图片
    
    Args:
        text: 水印文字
        width: 图片宽度
        height: 图片高度
        font_size: 字体大小
        color: 文字颜色 (R, G, B)
        transparency: 透明度 (0-255)
        angle: 旋转角度
    
    Returns:
        PIL.Image: 水印图片
    """
    # 创建透明背景图片
    watermark = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark)
    
    # 尝试使用系统字体，如果失败则使用默认字体
    try:
        # Windows系统字体
        font = ImageFont.truetype("msyh.ttc", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # 计算文字位置（居中）
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # 绘制文字（带透明度）
    text_color = (*color, transparency)
    draw.text((x, y), text, font=font, fill=text_color)
    
    # 旋转图片
    if angle != 0:
        watermark = watermark.rotate(angle, expand=True)
    
    return watermark


def add_watermark_to_sheet(sheet, watermark_image, position='center'):
    """
    将水印添加到工作表
    
    Args:
        sheet: openpyxl工作表对象
        watermark_image: PIL图片对象
        position: 水印位置 (center, top-left, top-right, bottom-left, bottom-right)
    """
    # 将PIL图片转换为字节流
    img_buffer = BytesIO()
    watermark_image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # 创建openpyxl图片对象
    img = OpenpyxlImage(img_buffer)
    
    # 设置图片位置
    if position == 'center':
        # 居中放置（大致位置）
        img.anchor = 'D10'
    elif position == 'top-left':
        img.anchor = 'A1'
    elif position == 'top-right':
        img.anchor = 'M1'
    elif position == 'bottom-left':
        img.anchor = 'A30'
    elif position == 'bottom-right':
        img.anchor = 'M30'
    else:
        img.anchor = 'D10'  # 默认居中
    
    # 添加图片到工作表
    sheet.add_image(img)


def process_file(file_data, watermark_config):
    """
    处理单个Excel文件，添加水印
    
    Args:
        file_data: Base64编码的文件数据
        watermark_config: 水印配置
            - type: 'text' 或 'image'
            - text: 文本内容（文本水印）
            - image_data: Base64图片数据（图片水印）
            - font_size: 字体大小
            - color: 颜色 [R, G, B]
            - transparency: 透明度 (0-255)
            - angle: 旋转角度
            - position: 位置
            - apply_to_all: 是否应用到所有工作表
    
    Returns:
        dict: 处理结果
    """
    try:
        # 解码文件数据
        file_bytes = base64.b64decode(file_data)
        
        # 加载工作簿
        wb = load_workbook(BytesIO(file_bytes))
        
        # 创建水印图片
        if watermark_config['type'] == 'text':
            # 文本水印
            watermark_img = create_text_watermark(
                text=watermark_config.get('text', 'WATERMARK'),
                font_size=watermark_config.get('font_size', 48),
                color=tuple(watermark_config.get('color', [128, 128, 128])),
                transparency=watermark_config.get('transparency', 128),
                angle=watermark_config.get('angle', -45)
            )
        else:
            # 图片水印
            image_data = base64.b64decode(watermark_config['image_data'])
            watermark_img = Image.open(BytesIO(image_data))
            
            # 调整透明度
            if watermark_img.mode != 'RGBA':
                watermark_img = watermark_img.convert('RGBA')
            
            # 应用透明度
            alpha = watermark_img.split()[3]
            alpha = alpha.point(lambda p: int(p * watermark_config.get('transparency', 128) / 255))
            watermark_img.putalpha(alpha)
        
        # 确定要处理的工作表
        sheets_to_process = wb.worksheets if watermark_config.get('apply_to_all', True) else [wb.active]
        
        # 添加水印到工作表
        processed_count = 0
        for sheet in sheets_to_process:
            add_watermark_to_sheet(sheet, watermark_img, watermark_config.get('position', 'center'))
            processed_count += 1
        
        # 保存到字节流
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        # 返回结果
        return {
            'success': True,
            'data': base64.b64encode(output.read()).decode('utf-8'),
            'statistics': {
                'total_sheets': len(wb.worksheets),
                'processed_sheets': processed_count,
                'watermark_type': watermark_config['type']
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# 主程序入口
if __name__ == '__main__':
    try:
        # 从stdin读取输入
        input_data = sys.stdin.read()
        params = json.loads(input_data)
        
        # 处理文件
        result = process_file(params['fileData'], params['watermarkConfig'])
        
        # 输出结果
        print(json.dumps(result))
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': f'处理失败: {str(e)}'
        }
        print(json.dumps(error_result))
