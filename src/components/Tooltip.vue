<template>
  <div class="tooltip-wrapper" @mouseenter="handleShow" @mouseleave="handleHide">
    <slot></slot>
    <Teleport to="body" :disabled="!teleport">
      <transition name="tooltip-fade">
        <div v-if="isVisible" :class="tooltipClasses" :style="tooltipStyle" ref="tooltipRef">
          {{ text }}
          <div class="tooltip-arrow"></div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'Tooltip',
  props: {
    text: {
      type: String,
      required: true
    },
    position: {
      type: String,
      default: 'top',
      validator: (value: string) => ['top', 'bottom', 'left', 'right'].includes(value)
    },
    delay: {
      type: Number,
      default: 300
    },
    teleport: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      isVisible: false,
      timer: null as ReturnType<typeof setTimeout> | null,
      tooltipStyle: {} as Record<string, string>
    }
  },
  computed: {
    tooltipClasses() {
      return ['tooltip-content', this.position]
    }
  },
  methods: {
    handleShow() {
      this.clearTimer()
      this.timer = setTimeout(() => {
        this.isVisible = true
        if (this.teleport) {
          this.$nextTick(() => {
            this.updatePosition()
          })
        }
      }, this.delay)
    },
    handleHide() {
      this.clearTimer()
      this.isVisible = false
    },
    clearTimer() {
      if (this.timer !== null) {
        clearTimeout(this.timer)
        this.timer = null
      }
    },
    updatePosition() {
      const wrapper = this.$el as HTMLElement
      const tooltip = this.$refs.tooltipRef as HTMLElement
      if (!wrapper || !tooltip) return

      const rect = wrapper.getBoundingClientRect()
      const tooltipRect = tooltip.getBoundingClientRect()
      
      let top = 0
      let left = 0

      switch (this.position) {
        case 'top':
          top = rect.top - tooltipRect.height - 8
          left = rect.left + rect.width / 2 - tooltipRect.width / 2
          break
        case 'bottom':
          top = rect.bottom + 8
          left = rect.left + rect.width / 2 - tooltipRect.width / 2
          break
        case 'left':
          top = rect.top + rect.height / 2 - tooltipRect.height / 2
          left = rect.left - tooltipRect.width - 8
          break
        case 'right':
          top = rect.top + rect.height / 2 - tooltipRect.height / 2
          left = rect.right + 8
          break
      }

      this.tooltipStyle = {
        top: `${top}px`,
        left: `${left}px`,
        transform: 'none'
      }
    }
  },
  beforeUnmount() {
    this.clearTimer()
  }
})
</script>

<style scoped>
.tooltip-wrapper {
  position: relative;
  display: inline-block;
}

.tooltip-content {
  position: absolute;
  z-index: 9999;
  padding: 8px 12px;
  background: #1a202c;
  color: white;
  font-size: 13px;
  border-radius: 6px;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  pointer-events: none;
}

.tooltip-content.top {
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
}

.tooltip-content.bottom {
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
}

.tooltip-content.left {
  right: calc(100% + 8px);
  top: 50%;
  transform: translateY(-50%);
}

.tooltip-content.right {
  left: calc(100% + 8px);
  top: 50%;
  transform: translateY(-50%);
}

.tooltip-arrow {
  position: absolute;
  width: 0;
  height: 0;
  border: 5px solid transparent;
}

.tooltip-content.top .tooltip-arrow {
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  border-top-color: #1a202c;
}

.tooltip-content.bottom .tooltip-arrow {
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  border-bottom-color: #1a202c;
}

.tooltip-content.left .tooltip-arrow {
  right: -10px;
  top: 50%;
  transform: translateY(-50%);
  border-left-color: #1a202c;
}

.tooltip-content.right .tooltip-arrow {
  left: -10px;
  top: 50%;
  transform: translateY(-50%);
  border-right-color: #1a202c;
}

.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: opacity 0.2s ease;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
}
</style>
