#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Watermark Processor Tests - 水印处理器测试
"""

import os
import sys
import pytest
import tempfile
from PIL import Image

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.image.watermark import WatermarkProcessor


class TestWatermarkProcessor:
    """水印处理器测试类"""
    
    @pytest.fixture
    def processor(self):
        """创建水印处理器实例"""
        return WatermarkProcessor()
    
    @pytest.fixture
    def test_image(self):
        """创建测试图片"""
        # 创建一个简单的测试图片
        img = Image.new('RGB', (800, 600), color='white')
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name)
        temp_file.close()
        yield temp_file.name
        # 清理
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    
    @pytest.fixture
    def test_watermark_image(self):
        """创建测试水印图片"""
        # 创建一个小的水印图片
        img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name)
        temp_file.close()
        yield temp_file.name
        # 清理
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    
    def test_add_text_watermark_missing_image_path(self, processor):
        """测试添加文字水印 - 缺少图片路径"""
        result = processor.add_text_watermark({
            'text': 'Test Watermark'
        })
        
        assert result['type'] == 'result'
        assert result['status'] == 'error'
        assert result['error_code'] == 'MISSING_IMAGE_PATH'
    
    def test_add_text_watermark_missing_text(self, processor, test_image):
        """测试添加文字水印 - 缺少水印文字"""
        result = processor.add_text_watermark({
            'image_path': test_image
        })
        
        assert result['type'] == 'result'
        assert result['status'] == 'error'
        assert result['error_code'] == 'MISSING_TEXT'
    
    def test_add_text_watermark_image_not_found(self, processor):
        """测试添加文字水印 - 图片不存在"""
        result = processor.add_text_watermark({
            'image_path': 'nonexistent.png',
            'text': 'Test'
        })
        
        assert result['type'] == 'result'
        assert result['status'] == 'error'
        assert result['error_code'] == 'IMAGE_NOT_FOUND'
    
    def test_add_text_watermark_success(self, processor, test_image):
        """测试成功添加文字水印"""
        output_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        output_file.close()
        
        try:
            result = processor.add_text_watermark({
                'image_path': test_image,
                'output_path': output_file.name,
                'text': 'Test Watermark',
                'position': 'bottom_right'
            })
            
            assert result['type'] == 'result'
            assert result['status'] == 'success'
            assert os.path.exists(output_file.name)
            assert result['data']['text'] == 'Test Watermark'
            assert result['data']['position'] == 'bottom_right'
        finally:
            if os.path.exists(output_file.name):
                os.unlink(output_file.name)
    
    def test_add_text_watermark_different_positions(self, processor, test_image):
        """测试不同位置的文字水印"""
        positions = ['top_left', 'top_right', 'bottom_left', 'bottom_right', 'center']
        
        for position in positions:
            output_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            output_file.close()
            
            try:
                result = processor.add_text_watermark({
                    'image_path': test_image,
                    'output_path': output_file.name,
                    'text': f'Test {position}',
                    'position': position
                })
                
                assert result['status'] == 'success'
                assert os.path.exists(output_file.name)
            finally:
                if os.path.exists(output_file.name):
                    os.unlink(output_file.name)
    
    def test_add_image_watermark_missing_image_path(self, processor):
        """测试添加图片水印 - 缺少图片路径"""
        result = processor.add_image_watermark({
            'watermark_path': 'watermark.png'
        })
        
        assert result['type'] == 'result'
        assert result['status'] == 'error'
        assert result['error_code'] == 'MISSING_IMAGE_PATH'
    
    def test_add_image_watermark_missing_watermark_path(self, processor, test_image):
        """测试添加图片水印 - 缺少水印路径"""
        result = processor.add_image_watermark({
            'image_path': test_image
        })
        
        assert result['type'] == 'result'
        assert result['status'] == 'error'
        assert result['error_code'] == 'MISSING_WATERMARK_PATH'
    
    def test_add_image_watermark_image_not_found(self, processor, test_watermark_image):
        """测试添加图片水印 - 图片不存在"""
        result = processor.add_image_watermark({
            'image_path': 'nonexistent.png',
            'watermark_path': test_watermark_image
        })
        
        assert result['type'] == 'result'
        assert result['status'] == 'error'
        assert result['error_code'] == 'IMAGE_NOT_FOUND'
    
    def test_add_image_watermark_watermark_not_found(self, processor, test_image):
        """测试添加图片水印 - 水印图片不存在"""
        result = processor.add_image_watermark({
            'image_path': test_image,
            'watermark_path': 'nonexistent.png'
        })
        
        assert result['type'] == 'result'
        assert result['status'] == 'error'
        assert result['error_code'] == 'WATERMARK_NOT_FOUND'
    
    def test_add_image_watermark_success(self, processor, test_image, test_watermark_image):
        """测试成功添加图片水印"""
        output_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        output_file.close()
        
        try:
            result = processor.add_image_watermark({
                'image_path': test_image,
                'watermark_path': test_watermark_image,
                'output_path': output_file.name,
                'position': 'bottom_right',
                'opacity': 0.5
            })
            
            assert result['type'] == 'result'
            assert result['status'] == 'success'
            assert os.path.exists(output_file.name)
            assert result['data']['opacity'] == 0.5
            assert result['data']['position'] == 'bottom_right'
        finally:
            if os.path.exists(output_file.name):
                os.unlink(output_file.name)
    
    def test_position_constants(self, processor):
        """测试位置常量"""
        assert processor.POSITION_TOP_LEFT == 'top_left'
        assert processor.POSITION_TOP_RIGHT == 'top_right'
        assert processor.POSITION_BOTTOM_LEFT == 'bottom_left'
        assert processor.POSITION_BOTTOM_RIGHT == 'bottom_right'
        assert processor.POSITION_CENTER == 'center'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
