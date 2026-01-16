# Plugin Migration Status

## Overview
Migration of 13 plugins to use the new PluginLayout component with 5-step workflow.

## Completed Migrations (4/13)

### ✅ 1. modify-by-rules
- **Status**: Complete
- **Features**: Rules configuration with find/replace pairs, regex support
- **Step 1**: Add/remove rules with regex toggle
- **Special**: Dynamic rule list with add/remove functionality

### ✅ 2. merge-excel  
- **Status**: Complete
- **Features**: Merge mode selection (keep sheets vs merge to single)
- **Step 1**: Radio button selection for merge mode
- **Special**: Requires minimum 2 files, single result output

### ✅ 3. split-excel
- **Status**: Complete
- **Features**: Split options (by sheets or row count)
- **Step 1**: Mode selection with conditional row count input
- **Special**: Single file input, multiple file outputs

### ✅ 4. remove-image
- **Status**: Complete
- **Features**: Simple processing (no special config needed)
- **Step 1**: Info message only, no configuration required
- **Special**: Shows file size reduction statistics

## Remaining Plugins (9/13)

### 5. replace-image
- **Step 1 Config**: Image upload for replacement with preview
- **Special**: Requires image file upload, shows preview

### 6. url-to-image
- **Step 1 Config**: URL column selection, insert position, image size
- **Special**: Complex form with multiple options

### 7. extract-image
- **Step 1 Config**: Naming pattern and format options
- **Special**: Outputs ZIP file with extracted images

### 8. remove-formula
- **Step 1 Config**: Simple checkboxes for formatting options
- **Special**: Minimal configuration

### 9. generate-from-template
- **Step 0 Config**: Two file uploads (template + data source)
- **Step 1 Config**: Naming pattern and field selection
- **Special**: Requires two input files

### 10. format-converter
- **Step 1 Config**: Target format selection (CSV/HTML/JSON) with format-specific options
- **Special**: Conditional options based on format selection

### 11. import-rules
- **Step 0 Config**: Two file uploads (Excel + rules file)
- **Step 1 Config**: Case sensitive and error handling options
- **Special**: Requires rules file (JSON/CSV)

### 12. extract-content
- **Step 1 Config**: Filter conditions configuration with dynamic condition list
- **Special**: Complex condition builder with operators

### 13. remove-macro
- **Step 1 Config**: Simple checkboxes for conversion options
- **Special**: File format conversion option

## Migration Pattern

Each plugin follows this structure:

```vue
<template>
  <PluginLayout
    title="Plugin Title"
    :can-proceed="canProceed"
    :processing="processing"
    @step-change="handleStepChange"
    @next="handleNext"
    @add-files="handleAddFiles"
    @import-from-folder="handleImportFromFolder"
    @clear-all="handleClearAll"
    ref="layoutRef"
  >
    <template #default="{ currentStep }">
      <!-- Step 0: File Upload -->
      <!-- Step 1: Plugin-specific Configuration -->
      <!-- Step 2: Export Options -->
      <!-- Step 3: Output Directory -->
      <!-- Step 4: Processing & Results -->
    </template>
  </PluginLayout>
</template>
```

## Key Components

### Step 0 - File Upload
- FileUpload component
- File table display
- Empty state

### Step 1 - Configuration
- Plugin-specific forms
- Validation logic
- Conditional fields

### Step 2 - Export Options
- File naming options
- Format selection (if applicable)

### Step 3 - Output Directory
- Directory selection
- Auto-open checkbox

### Step 4 - Processing
- Progress indicator
- Results display
- Download buttons
- Statistics cards

## Common Features

All migrated plugins include:
- ✅ 5-step workflow
- ✅ File table with actions
- ✅ Progress tracking
- ✅ Result statistics
- ✅ Download functionality
- ✅ Error handling
- ✅ Consistent styling
- ✅ Worker script integration

## Next Steps

To complete the remaining 9 plugins:

1. **replace-image**: Add image upload in step 1
2. **url-to-image**: Add URL column and position config
3. **extract-image**: Add naming pattern options
4. **remove-formula**: Add simple checkboxes
5. **generate-from-template**: Modify step 0 for dual upload
6. **format-converter**: Add format selection with conditional options
7. **import-rules**: Modify step 0 for dual upload
8. **extract-content**: Add condition builder
9. **remove-macro**: Add conversion options

Each plugin maintains its existing functionality while adopting the new unified layout.
