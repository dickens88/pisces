<template>
  <Teleport to="body">
    <TransitionGroup
      name="toast"
      tag="div"
      class="fixed top-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none"
    >
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="[
          'pointer-events-auto min-w-[320px] max-w-[480px] rounded-lg shadow-lg p-4 flex items-start gap-4',
          getToastClass(toast.type)
        ]"
      >
        <!-- Icon with circular background -->
        <div class="flex-shrink-0">
          <div :class="['size-10 rounded-full flex items-center justify-center', getIconBgClass(toast.type)]">
            <span class="material-symbols-outlined text-lg text-white">
              {{ getIcon(toast.type) }}
            </span>
          </div>
        </div>
        
        <!-- Content -->
        <div class="flex-1 min-w-0 flex flex-col gap-1">
          <p v-if="toast.title" class="text-base font-bold text-white">
            {{ toast.title }}
          </p>
          <p class="text-sm text-white/90 leading-relaxed">
            {{ toast.message }}
          </p>
        </div>
        
        <!-- Close button -->
        <button
          @click="removeToast(toast.id)"
          class="flex-shrink-0 text-white/60 hover:text-white transition-colors"
        >
          <span class="material-symbols-outlined text-base">close</span>
        </button>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const toasts = ref([])
let toastIdCounter = 0

const getToastClass = (type) => {
  const classes = {
    info: 'bg-green-600',
    warn: 'bg-amber-500',
    error: 'bg-red-600'
  }
  return classes[type] || classes.info
}

const getIconBgClass = (type) => {
  const classes = {
    info: 'bg-green-700',
    warn: 'bg-amber-600',
    error: 'bg-red-700'
  }
  return classes[type] || classes.info
}

const getIcon = (type) => {
  const icons = {
    info: 'check_circle',
    warn: 'warning',
    error: 'error'
  }
  return icons[type] || icons.info
}

const removeToast = (id) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

const addToast = (message, type = 'info', title = null) => {
  const id = ++toastIdCounter
  const toast = {
    id,
    message,
    type,
    title
  }
  
  toasts.value.push(toast)
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    removeToast(id)
  }, 5000)
  
  return id
}

// Expose methods to global
onMounted(() => {
  window.$toast = {
    info: (message, title) => addToast(message, 'info', title),
    warn: (message, title) => addToast(message, 'warn', title),
    error: (message, title) => addToast(message, 'error', title),
    success: (message, title) => addToast(message, 'info', title) // success uses info style
  }
})

onUnmounted(() => {
  if (window.$toast) {
    delete window.$toast
  }
})

// Also expose via defineExpose for template ref access
defineExpose({
  addToast,
  removeToast
})
</script>

<style scoped>
.toast-enter-active {
  transition: all 0.3s ease-out;
}

.toast-leave-active {
  transition: all 0.2s ease-in;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>

