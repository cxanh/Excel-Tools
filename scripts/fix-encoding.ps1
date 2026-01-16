# Fix encoding issues in plugin files

$files = @(
    'plugins/modify-metadata/index.vue',
    'plugins/manage-protection/index.vue',
    'plugins/insert-sheet/index.vue',
    'plugins/csv-split/index.vue',
    'plugins/csv-merge/index.vue',
    'plugins/clear-metadata/index.vue',
    'plugins/optimize-excel/index.vue'
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "Processing: $file"
        
        # Read with default encoding
        $content = Get-Content $file -Raw
        
        # Fix common encoding issues
        $content = $content -replace '姝ｅ湪澶勭悊', '正在处理'
        $content = $content -replace '澶勭悊瀹屾垚锛?', '处理完成！'
        $content = $content -replace '鍑嗗寮€濮嬪鐞?', '准备开始处理'
        $content = $content -replace '鏀寔', '支持'
        $content = $content -replace '鍜?', '和'
        $content = $content -replace '鏍煎紡', '格式'
        $content = $content -replace '鍗曚釜', '单个'
        $content = $content -replace '鏂囦欢', '文件'
        $content = $content -replace '鏈€澶?', '最大'
        $content = $content -replace '閰嶇疆', '配置'
        $content = $content -replace '鍙傛暟', '参数'
        $content = $content -replace '寰呭鐞?', '待处理'
        $content = $content -replace '涓?', '个'
        
        # Save with UTF-8 encoding (no BOM)
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText((Resolve-Path $file), $content, $utf8NoBom)
        
        Write-Host "  Fixed: $file" -ForegroundColor Green
    } else {
        Write-Host "  Not found: $file" -ForegroundColor Yellow
    }
}

Write-Host "`nEncoding fix complete!" -ForegroundColor Cyan
