#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试格式转换器
"""

import os
import sys
import pytest
import openpyxl
import pandas as pd
import tempfile
import shutil

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.convert.converter import FormatConverter


class TestFormatConverter:
    """测试格式转换器"""
    
    @pytest.fixture
    def converter(self):
        """创建转换器实例"""
        return FormatConverter()
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # 清理
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_excel_file(self, temp_dir):
        """创建示例 Excel 文件"""
        file_path = os.path.join(temp_dir, "test.xlsx")
        wb = openpyxl.Workbook()
        
        # 第一个工作表
        ws1 = wb.active
        ws1.title = "Sales"
        ws1.append(["Product", "Price", "Quantity"])
        ws1.append(["Apple", 1.5, 100])
        ws1.append(["Banana", 0.8, 150])
        ws1.append(["Orange", 1.2, 120])
        
        # 第二个工作表
        ws2 = wb.create_sheet("Inventory")
        ws2.append(["Item", "Stock", "Location"])
        ws2.append(["Laptop", 50, "Warehouse A"])
        ws2.append(["Mouse", 200, "Warehouse B"])
        
        wb.save(file_path)
        wb.close()
        
        return file_path
    
    # ==================== Excel 转 CSV 测试 ====================
    
    def test_excel_to_csv_missing_file_path(self, converter, temp_dir):
        """测试缺少文件路径"""
        result = converter.excel_to_csv({
            'output_dir': temp_dir
        })
        
        assert result['status'] == 'error'
        assert result['error_code'] == 'MISSING_FILE_PATH'
    
    def test_excel_to_csv_missing_output_dir(self, converter, sample_excel_file):
        """测试缺少输出目录"""
        result = converter.excel_to_csv({
            'file_path': sample_excel_file
        })
        
        assert result['status'] == 'error'
        assert result['error_code'] == 'MISSING_OUTPUT_DIR'
    
    def test_excel_to_csv_file_not_found(self, converter, temp_dir):
        """测试文件不存在"""
        result = converter.excel_to_csv({
            'file_path': os.path.join(temp_dir, "nonexistent.xlsx"),
            'output_dir': temp_dir
        })
        
        assert result['status'] == 'error'
        assert result['error_code'] == 'FILE_NOT_FOUND'
    
    def test_excel_to_csv_all_sheets(self, converter, sample_excel_file, temp_dir):
        """测试转换所有工作表"""
        output_dir = os.path.join(temp_dir, "output")
        result = converter.excel_to_csv({
            'file_path': sample_excel_file,
            'output_dir': output_dir
        })
        
        assert result['status'] == 'success'
        assert result['data']['total_sheets'] == 2
        assert len(result['data']['output_files']) == 2
        
        # 验证输出文件
        for file_info in result['data']['output_files']:
            assert os.path.exists(file_info['path'])
            df = pd.read_csv(file_info['path'])
            assert len(df) > 0
    
    def test_excel_to_csv_specific_sheets(self, converter, sample_excel_file, temp_dir):
        """测试转换指定工作表"""
        output_dir = os.path.join(temp_dir, "output")
        result = converter.excel_to_csv({
            'file_path': sample_excel_file,
            'output_dir': output_dir,
            'sheet_names': ['Sales']
        })
        
        assert result['status'] == 'success'
        assert result['data']['total_sheets'] == 1
        assert len(result['data']['output_files']) == 1
        assert result['data']['output_files'][0]['sheet_name'] == 'Sales'
    
    def test_excel_to_csv_custom_encoding(self, converter, sample_excel_file, temp_dir):
        """测试自定义编码"""
        output_dir = os.path.join(temp_dir, "output")
        result = converter.excel_to_csv({
            'file_path': sample_excel_file,
            'output_dir': output_dir,
            'encoding': 'gbk',
            'delimiter': ';'
        })
        
        assert result['status'] == 'success'
        assert result['data']['encoding'] == 'gbk'
        assert result['data']['delimiter'] == ';'
    
    def test_excel_to_csv_sheet_not_found(self, converter, sample_excel_file, temp_dir):
        """测试指定的工作表不存在"""
        output_dir = os.path.join(temp_dir, "output")
        result = converter.excel_to_csv({
            'file_path': sample_excel_file,
            'output_dir': output_dir,
            'sheet_names': ['NonExistent']
        })
        
        assert result['status'] == 'error'
        assert result['error_code'] == 'SHEET_NOT_FOUND'
    
    # ==================== Excel 转 PDF 测试 ====================
    
    def test_excel_to_pdf_missing_file_path(self, converter, temp_dir):
        """测试缺少文件路径"""
        result = converter.excel_to_pdf({
            'output_path': os.path.join(temp_dir, "output.pdf")
        })
        
        assert result['status'] == 'error'
        assert result['error_code'] == 'MISSING_FILE_PATH'
    
    def test_excel_to_pdf_missing_output_path(self, converter, sample_excel_file):
        """测试缺少输出路径"""
        result = converter.excel_to_pdf({
            'file_path': sample_excel_file
        })
        
        assert result['status'] == 'error'
        assert result['error_code'] == 'MISSING_OUTPUT_PATH'
    
    def test_excel_to_pdf_file_not_found(self, converter, temp_dir):
        """测试文件不存在"""
        result = converter.excel_to_pdf({
            'file_path': os.path.join(temp_dir, "nonexistent.xlsx"),
            'output_path': os.path.join(temp_dir, "output.pdf")
        })
        
        assert result['status'] == 'error'
        assert result['error_code'] == 'FILE_NOT_FOUND'
    
    def test_excel_to_pdf_invalid_method(self, converter, sample_excel_file, temp_dir):
        """测试无效的转换方法"""
        result = converter.excel_to_pdf({
            'file_path': sample_excel_file,
            'output_path': os.path.join(temp_dir, "output.pdf"),
            'method': 'invalid'
        })
        
        assert result['status'] == 'error'
        assert result['error_code'] == 'INVALID_METHOD'
    
    # ==================== 依赖检查测试 ====================
    
    def test_check_dependencies(self, converter):
        """测试依赖检查"""
        result = converter.check_dependencies()
        
        assert result['status'] == 'success'
        assert 'data' in result
        assert 'platform' in result['data']
        assert 'excel_to_csv' in result['data']
        assert 'excel_to_pdf' in result['data']
        
        # CSV 转换应该总是可用
        assert result['data']['excel_to_csv']['available'] is True
        
        # PDF 转换方法列表
        assert 'methods' in result['data']['excel_to_pdf']
        assert len(result['data']['excel_to_pdf']['methods']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
