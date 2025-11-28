<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-[#0f1419] px-4">
    <div class="w-full max-w-xl text-center">
      <div class="mb-8">
        <h1 class="text-9xl font-bold text-primary dark:text-[#2b7cee] mb-4 animate-pulse">
          403
        </h1>
      </div>

      <div class="mb-6">
        <span class="material-symbols-outlined text-8xl text-gray-400 dark:text-white/30 mb-4 inline-block animate-bounce">
          block
        </span>
        <h2 class="text-gray-900 dark:text-white text-3xl font-bold mb-3">
          哎呀，被拒之门外了！
        </h2>
        <p class="text-gray-600 dark:text-white/60 text-lg">
          就像试图用普通钥匙打开银行金库一样，这个操作需要更高级别的权限。
        </p>
      </div>

      <div class="bg-white dark:bg-[#19222c] border border-gray-200 dark:border-[#324867]/50 rounded-xl p-6 shadow-xl">
        <p class="text-gray-600 dark:text-white/60">
          如果你认为这是一个错误，请联系系统管理员。
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.animate-bounce {
  animation: bounce 2s infinite;
}
</style>

