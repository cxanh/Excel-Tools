#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Extractor Tests - 图片提取器测试
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.image.extractor import ImageExtractor


class TestImageExtractor:
    """图片提取器测试类"""
    
    @pytest.fixture
    def extractor(self):
        """创建图片提取器实例"""
        return ImageExtractor()
    
    @pytest.fixture
    def temp_output_dir(self):
        """创建临时输出目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def test_file_path(self):
        """测试文件路径"""
        return os.path.join(os.path.dirname(__file__), 'test_files', 'test_load.xlsx')
    
    def test_extract_images_missing_file_path(self, extractor, temp_output_dir):
        """测试缺少文件路径参数"""
        result = extractor.extract_images({
            'output_dir': temp_output_dir
        })
        
        assert result['type'] == 'result'
        assert result['status'] == 'error'
        assert result['error_code'] == 'MISSING_FILE_PATH'
    
    def test_extract_images_missing_output_dir(self, extractor, test_file_path):
        """测试缺少输出目录参数"""
        result = extractor.extract_images({
            'file_path': test_file_path
        })
        
        assert result['type'] == 'result'
        assert result['status'] == 'error'
        assert result['error_code'] == 'MISSING_OUTPUT_DIR'
    
    def test_extract_images_file_not_found(self, extractor, temp_output_dir):
        """测试文件不存在"""
        result = extractor.extract_images({
            'file_path': 'nonexistent.xlsx',
            'output_dir': temp_output_dir
        })
        
        assert result['type'] == 'result'
        assert result['status'] == 'error'
        assert result['error_code'] == 'FILE_NOT_FOUND'
    
    def test_extract_images_unsupported_format(self, extractor, temp_output_dir):
        """测试不支持的文件格式"""
        # 创建一个临时的 .txt 文件
        temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        temp_file.close()
        
        try:
            result = extractor.extract_images({
                'file_path': temp_file.name,
                'output_dir': temp_output_dir
            })
            
            assert result['type'] == 'result'
            assert result['status'] == 'error'
            assert result['error_code'] == 'UNSUPPORTED_FORMAT'
        finally:
            os.unlink(temp_file.name)
    
    def test_extract_images_success(self, extractor, test_file_path, temp_output_dir):
        """测试成功提取图片（如果文件中有图片）"""
        result = extractor.extract_images({
            'file_path': test_file_path,
            'output_dir': temp_output_dir
        })
        
        assert result['type'] == 'result'
        assert result['status'] == 'success'
        assert 'data' in result
        assert 'total_images' in result['data']
        assert 'extracted_images' in result['data']
        
        # 如果有图片，检查输出目录
        if result['data']['total_images'] > 0:
            assert os.path.exists(temp_output_dir)
            assert len(os.listdir(temp_output_dir)) == result['data']['total_images']
    
    def test_extract_images_custom_name_pattern(self, extractor, test_file_path, temp_output_dir):
        """测试自定义文件命名模式"""
        result = extractor.extract_images({
            'file_path': test_file_path,
            'output_dir': temp_output_dir,
            'name_pattern': 'pic_{index}{ext}'
        })
        
        assert result['type'] == 'result'
        assert result['status'] == 'success'
        
        # 如果有图片，检查文件名
        if result['data']['total_images'] > 0:
            for img in result['data']['extracted_images']:
                assert img['filename'].startswith('pic_')
    
    def test_get_image_info_missing_file_path(self, extractor):
        """测试获取图片信息 - 缺少文件路径"""
        result = extractor.get_image_info({})
        
        assert result['type'] == 'result'
        assert result['status'] == 'error'
        assert result['error_code'] == 'MISSING_FILE_PATH'
    
    def test_get_image_info_file_not_found(self, extractor):
        """测试获取图片信息 - 文件不存在"""
        result = extractor.get_image_info({
            'file_path': 'nonexistent.xlsx'
        })
        
        assert result['type'] == 'result'
        assert result['status'] == 'error'
        assert result['error_code'] == 'FILE_NOT_FOUND'
    
    def test_get_image_info_success(self, extractor, test_file_path):
        """测试成功获取图片信息"""
        result = extractor.get_image_info({
            'file_path': test_file_path
        })
        
        assert result['type'] == 'result'
        assert result['status'] == 'success'
        assert 'data' in result
        assert 'total_images' in result['data']
        assert 'images' in result['data']
        assert isinstance(result['data']['images'], list)
    
    def test_extract_images_creates_output_dir(self, extractor, test_file_path):
        """测试自动创建输出目录"""
        # 使用不存在的目录
        output_dir = os.path.join(tempfile.gettempdir(), 'test_extract_images_' + str(os.getpid()))
        
        try:
            result = extractor.extract_images({
                'file_path': test_file_path,
                'output_dir': output_dir
            })
            
            assert result['type'] == 'result'
            assert result['status'] == 'success'
            assert os.path.exists(output_dir)
        finally:
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
    
    def test_supported_formats(self, extractor):
        """测试支持的图片格式列表"""
        assert '.png' in extractor.SUPPORTED_FORMATS
        assert '.jpg' in extractor.SUPPORTED_FORMATS
        assert '.jpeg' in extractor.SUPPORTED_FORMATS
        assert '.gif' in extractor.SUPPORTED_FORMATS
        assert '.bmp' in extractor.SUPPORTED_FORMATS


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
