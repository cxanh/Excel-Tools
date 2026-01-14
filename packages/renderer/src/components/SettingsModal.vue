<template>
  <a-modal
    :open="visible"
    title="软件设置"
    :width="600"
    @ok="handleOk"
    @cancel="handleCancel"
    @update:open="(value) => emit('update:visible', value)"
    ok-text="保存"
    cancel-text="取消"
  >
    <div class="settings-container">
      <!-- 机器编码 -->
      <div class="setting-section">
        <div class="setting-title">
          机器编码
          <a-tooltip title="用于软件授权和识别">
            <QuestionCircleOutlined style="margin-left: 4px; color: #999" />
          </a-tooltip>
        </div>
        <a-button type="primary" style="margin-top: 8px"
          >查看当前电脑的机器编码</a-button
        >
      </div>

      <div class="setting-grid">
        <!-- 开机自动启动 -->
        <div class="setting-item">
          <div class="setting-label">开机自动启动</div>
          <a-switch v-model:checked="settings.startupOnBoot" />
        </div>

        <!-- 显示托盘图标 -->
        <div class="setting-item">
          <div class="setting-label">
            显示托盘图标
            <a-tooltip title="在系统托盘中显示软件图标">
              <QuestionCircleOutlined
                style="margin-left: 4px; color: #999; font-size: 12px"
              />
            </a-tooltip>
          </div>
          <a-switch v-model:checked="settings.showTrayIcon" />
        </div>
      </div>

      <div class="setting-grid">
        <!-- 处理完成后通知 -->
        <div class="setting-item">
          <div class="setting-label">处理完成后通知</div>
          <a-select
            v-model:value="settings.notificationMode"
            style="width: 150px"
          >
            <a-select-option value="none">不显示通知</a-select-option>
            <a-select-option value="toast">弹窗通知</a-select-option>
            <a-select-option value="tray">托盘通知</a-select-option>
          </a-select>
        </div>

        <!-- 最大同时运行任务数量 -->
        <div class="setting-item">
          <div class="setting-label">最大同时运行任务数量</div>
          <a-input-number
            v-model:value="settings.maxConcurrentTasks"
            :min="1"
            :max="10"
            style="width: 100px"
          />
        </div>
      </div>

      <!-- 备份设置 -->
      <div class="setting-section">
        <div class="setting-title">
          <span class="required">*</span
          >每次启动软件时，自动备份软件的设置数据文件到此文件夹中
        </div>
        <div class="backup-path">
          <a-input v-model:value="settings.backupPath" style="flex: 1" />
          <a-button type="default" style="margin-left: 8px">浏览</a-button>
          <a-button type="default" style="margin-left: 8px">打开</a-button>
          <a-button type="default" style="margin-left: 8px">清空</a-button>
        </div>

        <div class="setting-title" style="margin-top: 16px">
          <span class="required">*</span>只保留最近的多少个备份文件
        </div>
        <a-input-number
          v-model:value="settings.maxBackupFiles"
          :min="1"
          :max="100"
          style="width: 100px; margin-top: 8px"
        />

        <a-button
          type="primary"
          style="margin-top: 12px; margin-bottom: 12px"
          ghost
        >
          恢复
          <a-tooltip title="恢复到指定的备份版本">
            <SearchOutlined style="margin-left: 4px" />
          </a-tooltip>
        </a-button>
      </div>
    </div>
  </a-modal>
</template>

<script setup>
import { ref, reactive, watch } from "vue";
import { QuestionCircleOutlined, SearchOutlined } from "@ant-design/icons-vue";

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:visible", "save"]);

// 保存初始设置
const initialSettings = {
  startupOnBoot: false,
  showTrayIcon: false,
  notificationMode: "none",
  maxConcurrentTasks: 5,
  backupPath: "C:\\Users\\12607\\AppData\\Roaming\\inxunoffice\\db-backup",
  maxBackupFiles: 50,
};

// 设置数据
const settings = reactive({ ...initialSettings });

// 监听visible变化，重置设置
watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      // 可以从本地存储或API加载设置
      console.log("加载设置");
    }
  },
);

const handleOk = () => {
  emit("save", { ...settings });
  emit("update:visible", false);
};

const handleCancel = () => {
  // 重置设置
  Object.assign(settings, initialSettings);
  emit("update:visible", false);
};
</script>

<style scoped>
.settings-container {
  padding: 8px 0;
}

.setting-section {
  margin-bottom: 24px;
}

.setting-title {
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}

.setting-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.setting-label {
  display: flex;
  align-items: center;
  color: #333;
}

.required {
  color: #ff4d4f;
  margin-right: 2px;
}

.backup-path {
  display: flex;
  align-items: center;
  margin-top: 8px;
}
</style>
