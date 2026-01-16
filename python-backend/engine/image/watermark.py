#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Watermark Processor - 水印处理器
为图片添加文字或图片水印
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont


def log(message):
    """将日志输出到 stderr"""
    sys.stderr.write(f"[WATERMARK] {message}\n")
    sys.stderr.flush()


class WatermarkProcessor:
    """水印处理器"""
    
    # 水印位置常量
    POSITION_TOP_LEFT = 'top_left'
    POSITION_TOP_RIGHT = 'top_right'
    POSITION_BOTTOM_LEFT = 'bottom_left'
    POSITION_BOTTOM_RIGHT = 'bottom_right'
    POSITION_CENTER = 'center'
    
    def add_text_watermark(self, params):
        """
        为图片添加文字水印
        
        Args:
            params: dict, 包含以下字段：
                - image_path: str, 图片路径
                - output_path: str, 输出路径（可选，默认覆盖原图）
                - text: str, 水印文字
                - position: str, 水印位置（可选，默认：bottom_right）
                - font_size: int, 字体大小（可选，默认：36）
                - color: tuple, 文字颜色 (R, G, B, A)（可选，默认：(255, 255, 255, 128)）
                - margin: int, 边距（可选，默认：10）
        
        Returns:
            dict, 包含处理结果
        """
        image_path = params.get('image_path')
        output_path = params.get('output_path', image_path)
        text = params.get('text')
        position = params.get('position', self.POSITION_BOTTOM_RIGHT)
        font_size = params.get('font_size', 36)
        color = params.get('color', (255, 255, 255, 128))  # 白色，半透明
        margin = params.get('margin', 10)
        
        # 验证参数
        if not image_path:
            return {
                "type": "result",
                "status": "error",
                "error_code": "MISSING_IMAGE_PATH",
                "message": "缺少图片路径参数"
            }
        
        if not text:
            return {
                "type": "result",
                "status": "error",
                "error_code": "MISSING_TEXT",
                "message": "缺少水印文字参数"
            }
        
        if not os.path.exists(image_path):
            return {
                "type": "result",
                "status": "error",
                "error_code": "IMAGE_NOT_FOUND",
                "message": f"图片不存在: {image_path}"
            }
        
        try:
            # 打开图片
            image = Image.open(image_path)
            
            # 如果图片是 RGBA 模式，保持；否则转换为 RGBA
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # 创建一个透明图层用于绘制水印
            watermark_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark_layer)
            
            # 尝试加载字体（使用系统默认字体）
            try:
                # Windows 系统字体
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    # 尝试其他常见字体
                    font = ImageFont.truetype("simhei.ttf", font_size)
                except:
                    # 使用默认字体
                    font = ImageFont.load_default()
                    log("使用默认字体")
            
            # 获取文字尺寸
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 计算水印位置
            x, y = self._calculate_position(
                image.size[0], image.size[1],
                text_width, text_height,
                position, margin
            )
            
            # 绘制文字水印
            draw.text((x, y), text, font=font, fill=color)
            
            # 合并图层
            watermarked = Image.alpha_composite(image, watermark_layer)
            
            # 如果原图不是 RGBA，转换回原格式
            if Image.open(image_path).mode != 'RGBA':
                watermarked = watermarked.convert('RGB')
            
            # 保存图片
            watermarked.save(output_path)
            
            log(f"文字水印添加成功: {output_path}")
            
            return {
                "type": "result",
                "status": "success",
                "message": "文字水印添加成功",
                "data": {
                    "output_path": output_path,
                    "text": text,
                    "position": position
                }
            }
        
        except Exception as e:
            log(f"添加文字水印时发生错误: {str(e)}")
            return {
                "type": "result",
                "status": "error",
                "error_code": "WATERMARK_ERROR",
                "message": f"添加文字水印时发生错误: {str(e)}"
            }
    
    def add_image_watermark(self, params):
        """
        为图片添加图片水印
        
        Args:
            params: dict, 包含以下字段：
                - image_path: str, 原图片路径
                - watermark_path: str, 水印图片路径
                - output_path: str, 输出路径（可选，默认覆盖原图）
                - position: str, 水印位置（可选，默认：bottom_right）
                - opacity: float, 透明度 0.0-1.0（可选，默认：0.5）
                - scale: float, 缩放比例（可选，默认：0.2，即原图的 20%）
                - margin: int, 边距（可选，默认：10）
        
        Returns:
            dict, 包含处理结果
        """
        image_path = params.get('image_path')
        watermark_path = params.get('watermark_path')
        output_path = params.get('output_path', image_path)
        position = params.get('position', self.POSITION_BOTTOM_RIGHT)
        opacity = params.get('opacity', 0.5)
        scale = params.get('scale', 0.2)
        margin = params.get('margin', 10)
        
        # 验证参数
        if not image_path:
            return {
                "type": "result",
                "status": "error",
                "error_code": "MISSING_IMAGE_PATH",
                "message": "缺少图片路径参数"
            }
        
        if not watermark_path:
            return {
                "type": "result",
                "status": "error",
                "error_code": "MISSING_WATERMARK_PATH",
                "message": "缺少水印图片路径参数"
            }
        
        if not os.path.exists(image_path):
            return {
                "type": "result",
                "status": "error",
                "error_code": "IMAGE_NOT_FOUND",
                "message": f"图片不存在: {image_path}"
            }
        
        if not os.path.exists(watermark_path):
            return {
                "type": "result",
                "status": "error",
                "error_code": "WATERMARK_NOT_FOUND",
                "message": f"水印图片不存在: {watermark_path}"
            }
        
        try:
            # 打开图片
            image = Image.open(image_path)
            watermark = Image.open(watermark_path)
            
            # 转换为 RGBA 模式
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            if watermark.mode != 'RGBA':
                watermark = watermark.convert('RGBA')
            
            # 计算水印尺寸（按比例缩放）
            watermark_width = int(image.size[0] * scale)
            watermark_height = int(watermark.size[1] * (watermark_width / watermark.size[0]))
            watermark = watermark.resize((watermark_width, watermark_height), Image.Resampling.LANCZOS)
            
            # 调整水印透明度
            watermark_with_opacity = Image.new('RGBA', watermark.size)
            for x in range(watermark.size[0]):
                for y in range(watermark.size[1]):
                    r, g, b, a = watermark.getpixel((x, y))
                    watermark_with_opacity.putpixel((x, y), (r, g, b, int(a * opacity)))
            
            # 计算水印位置
            x, y = self._calculate_position(
                image.size[0], image.size[1],
                watermark_width, watermark_height,
                position, margin
            )
            
            # 创建透明图层
            watermark_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
            watermark_layer.paste(watermark_with_opacity, (x, y), watermark_with_opacity)
            
            # 合并图层
            watermarked = Image.alpha_composite(image, watermark_layer)
            
            # 如果原图不是 RGBA，转换回原格式
            if Image.open(image_path).mode != 'RGBA':
                watermarked = watermarked.convert('RGB')
            
            # 保存图片
            watermarked.save(output_path)
            
            log(f"图片水印添加成功: {output_path}")
            
            return {
                "type": "result",
                "status": "success",
                "message": "图片水印添加成功",
                "data": {
                    "output_path": output_path,
                    "watermark_path": watermark_path,
                    "position": position,
                    "opacity": opacity
                }
            }
        
        except Exception as e:
            log(f"添加图片水印时发生错误: {str(e)}")
            return {
                "type": "result",
                "status": "error",
                "error_code": "WATERMARK_ERROR",
                "message": f"添加图片水印时发生错误: {str(e)}"
            }
    
    def _calculate_position(self, image_width, image_height, watermark_width, watermark_height, position, margin):
        """
        计算水印位置
        
        Args:
            image_width: int, 图片宽度
            image_height: int, 图片高度
            watermark_width: int, 水印宽度
            watermark_height: int, 水印高度
            position: str, 位置
            margin: int, 边距
        
        Returns:
            tuple, (x, y) 坐标
        """
        if position == self.POSITION_TOP_LEFT:
            return (margin, margin)
        elif position == self.POSITION_TOP_RIGHT:
            return (image_width - watermark_width - margin, margin)
        elif position == self.POSITION_BOTTOM_LEFT:
            return (margin, image_height - watermark_height - margin)
        elif position == self.POSITION_BOTTOM_RIGHT:
            return (image_width - watermark_width - margin, image_height - watermark_height - margin)
        elif position == self.POSITION_CENTER:
            return ((image_width - watermark_width) // 2, (image_height - watermark_height) // 2)
        else:
            # 默认右下角
            return (image_width - watermark_width - margin, image_height - watermark_height - margin)
