<template>
  <div class="space-y-2">
    <details class="group bg-white dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
      <summary class="flex items-center justify-between p-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50">
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white">{{ $t('common.automatedResponse') || 'Suggested Tools' }}</h3>
        <span class="material-symbols-outlined text-base text-gray-500 dark:text-gray-400 transition-transform group-open:rotate-180">expand_more</span>
      </summary>
      <div class="p-4 border-t border-gray-200 dark:border-gray-700 space-y-3">
        <!-- 加载状态 -->
        <div v-if="loadingToolkits || loadingToolkitRecords" class="flex items-center justify-center py-4">
          <span class="material-symbols-outlined animate-spin text-orange-500 text-lg">refresh</span>
        </div>
        
        <div v-else class="space-y-3">
          <!-- 工具清单部分：显示所有可用工具 -->
          <div v-if="toolkits.length" class="space-y-2">
            <h4 class="text-xs font-medium text-gray-600 dark:text-gray-400">{{ $t('common.availableTools') || 'Available Tools' }}</h4>
            <template v-for="tool in toolkits" :key="tool.app_id">
              <details 
                :open="expandedToolkitIds.has(tool.app_id)"
                class="group rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
              >
                <summary class="flex items-center justify-between p-2 cursor-pointer list-none hover:bg-gray-200 dark:hover:bg-gray-700">
                  <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-orange-500 text-sm">play_circle</span>
                    <div>
                      <p class="font-medium text-gray-900 dark:text-white text-xs">{{ tool.title }}</p>
                      <p class="text-[10px] text-gray-600 dark:text-gray-400">{{ $t('common.toolkitClickToConfigure') || 'Click to configure' }}</p>
                    </div>
                  </div>
                  <span class="material-symbols-outlined text-gray-500 dark:text-gray-400 text-sm group-hover:text-gray-700 dark:group-hover:text-gray-300">expand_more</span>
                </summary>
                <div class="px-2 pb-2 pt-1 text-xs text-gray-600 dark:text-gray-400 space-y-2 border-t border-gray-200 dark:border-gray-700">
                  <div v-for="param in tool.params" :key="param.name">
                    <label class="block text-[10px] font-medium text-gray-600 dark:text-gray-400 mb-0.5" :for="`toolkit-${tool.app_id}-${param.name}`">
                      {{ param.label }}
                      <span v-if="param.required !== false" class="text-red-500 ml-0.5">*</span>
                    </label>
                    <!-- Enum parameter: use select dropdown -->
                    <div v-if="param.enum && param.enum.length > 0" class="relative">
                      <select
                        class="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 p-1.5 pr-6 text-gray-900 dark:text-white focus:border-orange-500 focus:ring-orange-500 text-xs appearance-none cursor-pointer"
                        :id="`toolkit-${tool.app_id}-${param.name}`"
                        :value="toolkitParams[tool.app_id]?.[param.name] ?? (param.default_value !== undefined && param.default_value !== null ? param.default_value : '')"
                        @change="updateToolkitParam(tool.app_id, param.name, $event.target.value)"
                      >
                        <option v-if="param.default_value === undefined || param.default_value === null" value="" disabled>{{ $t('common.select') || '请选择' }}</option>
                        <option v-for="enumValue in param.enum" :key="enumValue" :value="enumValue">
                          {{ enumValue }}
                        </option>
                      </select>
                      <span class="material-symbols-outlined absolute right-1.5 top-1/2 -translate-y-1/2 pointer-events-none text-gray-500 dark:text-gray-400 text-sm">expand_more</span>
                    </div>
                    <!-- Regular parameter: use input -->
                    <input 
                      v-else
                      class="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 p-1.5 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:border-orange-500 focus:ring-orange-500 text-xs" 
                      :id="`toolkit-${tool.app_id}-${param.name}`"
                      :placeholder="param.default_value !== undefined && param.default_value !== null ? `默认: ${param.default_value}` : `e.g., ${param.label}`"
                      type="text" 
                      :value="toolkitParams[tool.app_id]?.[param.name] ?? (param.default_value !== undefined && param.default_value !== null ? param.default_value : '')"
                      @input="updateToolkitParam(tool.app_id, param.name, $event.target.value)"
                    />
                  </div>
                  <button 
                    @click="$emit('execute', tool)"
                    :disabled="executingToolkitId === tool.app_id"
                    class="w-full bg-orange-500 hover:bg-orange-600 text-xs font-medium text-white px-3 py-1.5 rounded-md transition-colors flex items-center gap-2 justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-orange-500 mt-2"
                  >
                    <span :class="['material-symbols-outlined text-sm', executingToolkitId === tool.app_id && 'animate-spin']">
                      {{ executingToolkitId === tool.app_id ? 'refresh' : 'play_arrow' }}
                    </span>
                    {{ executingToolkitId === tool.app_id ? ($t('common.toolkitExecuting') || '执行中...') : ($t('common.toolkitExecute') || '执行') }}
                  </button>
                  <!-- 执行结果展示 -->
                  <div 
                    v-if="toolkitExecutionResults[tool.app_id]"
                    :ref="el => { if (el) $emit('resultRef', tool.app_id, el) }"
                    class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700"
                  >
                    <div class="flex items-center gap-1.5 mb-1">
                      <span 
                        :class="[
                          'material-symbols-outlined text-xs',
                          toolkitExecutionResults[tool.app_id].status === 'completed' ? 'text-green-400' : 'text-red-400'
                        ]"
                      >
                        {{ toolkitExecutionResults[tool.app_id].status === 'completed' ? 'check_circle' : 'error' }}
                      </span>
                      <span 
                        :class="[
                          'text-[10px] font-medium',
                          toolkitExecutionResults[tool.app_id].status === 'completed' 
                            ? 'text-green-600 dark:text-green-400' 
                            : 'text-red-600 dark:text-red-400'
                        ]"
                      >
                        {{ toolkitExecutionResults[tool.app_id].status === 'completed' 
                          ? ($t('common.result') || '结果') 
                          : ($t('common.error') || '错误') 
                        }}
                      </span>
                    </div>
                    <pre 
                      :class="[
                        'text-[10px] whitespace-pre-wrap break-words font-mono',
                        toolkitExecutionResults[tool.app_id].status === 'failed' 
                          ? 'text-red-600 dark:text-red-300' 
                          : 'text-gray-700 dark:text-gray-300'
                      ]"
                    >
                      {{ formatToolkitResult(toolkitExecutionResults[tool.app_id].result) }}
                    </pre>
                  </div>
                </div>
              </details>
            </template>
          </div>
          
          <!-- 执行记录部分 -->
          <div v-if="toolkitRecords.length" class="space-y-2 mt-4">
            <h4 class="text-xs font-medium text-gray-600 dark:text-gray-400">{{ $t('common.executionRecords') || '执行记录' }}</h4>
            <template v-for="record in toolkitRecords" :key="record.id">
              <details :class="['group rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700', record.status === 'running' && 'animate-pulse']">
                <summary class="flex items-center justify-between p-2 cursor-pointer list-none hover:bg-gray-200 dark:hover:bg-gray-700">
                  <div class="flex items-center gap-2">
                    <span :class="[
                      'material-symbols-outlined text-sm',
                      record.status === 'completed' && 'text-green-400',
                      record.status === 'running' && 'text-yellow-400',
                      record.status === 'failed' && 'text-red-400'
                    ]">
                      {{ record.status === 'completed' ? 'task_alt' : record.status === 'running' ? 'hourglass_top' : 'error' }}
                    </span>
                    <div>
                      <p class="font-medium text-gray-900 dark:text-white text-xs">{{ record.title }}</p>
                      <p class="text-[10px] text-gray-600 dark:text-gray-400">
                        {{ formatDateTime(record.create_time) }}
                      </p>
                    </div>
                  </div>
                  <span class="material-symbols-outlined text-gray-500 dark:text-gray-400 text-sm group-hover:text-gray-700 dark:group-hover:text-gray-300">expand_more</span>
                </summary>
                <div class="px-2 pb-2 pt-1 text-[10px] text-gray-600 dark:text-gray-400 font-mono space-y-1 border-t border-gray-200 dark:border-gray-700">
                  <p><span class="text-gray-500 dark:text-gray-500">{{ $t('common.executionTime') || '执行时间' }}:</span> {{ formatDateTime(record.create_time) }}</p>
                  <p><span class="text-gray-500 dark:text-gray-500">{{ $t('common.executor') || '执行人' }}:</span> {{ record.owner || ($t('common.system') || '系统') }}</p>
                  <div v-if="record.result" :class="['mt-2 pt-2 border-t border-gray-200 dark:border-gray-700', record.status === 'failed' && 'text-red-600 dark:text-red-300']">
                    <span class="text-gray-500 dark:text-gray-500">{{ record.status === 'failed' ? ($t('common.error') || '错误') : ($t('common.result') || '结果') }}:</span>
                    <pre class="mt-1 text-[10px] whitespace-pre-wrap break-words">{{ formatToolkitResult(record.result) }}</pre>
                  </div>
                </div>
              </details>
            </template>
          </div>
          
          <!-- 如果没有工具和记录，显示空状态 -->
          <div v-if="!toolkits.length && !toolkitRecords.length" class="text-center py-4 text-gray-500 dark:text-gray-400">
            <p class="text-xs">{{ $t('common.noToolkitsAvailable') || '暂无可用工具' }}</p>
          </div>
        </div>
      </div>
    </details>
  </div>
</template>

<script setup>
import { formatDateTime } from '@/utils/dateTime'

defineProps({
  toolkits: { type: Array, default: () => [] },
  loadingToolkits: { type: Boolean, default: false },
  loadingToolkitRecords: { type: Boolean, default: false },
  toolkitParams: { type: Object, default: () => ({}) },
  executingToolkitId: { type: [String, Number], default: null },
  toolkitRecords: { type: Array, default: () => [] },
  toolkitExecutionResults: { type: Object, default: () => ({}) },
  expandedToolkitIds: { type: Set, default: () => new Set() }
})

const emit = defineEmits(['execute', 'updateParam', 'resultRef'])

const updateToolkitParam = (appId, paramName, value) => {
  emit('updateParam', appId, paramName, value)
}

const formatObjectAsKeyValue = (obj, indent = 0) => {
  if (obj === null || obj === undefined) return String(obj)
  
  if (Array.isArray(obj)) {
    if (obj.length === 0) return '[]'
    return obj.map((item, index) => {
      const prefix = '  '.repeat(indent)
      if (typeof item === 'object' && item !== null) {
        return `${prefix}${index}:\n${formatObjectAsKeyValue(item, indent + 1)}`
      }
      return `${prefix}${index}: ${String(item).replace(/\\n/g, '\n')}`
    }).join('\n')
  }
  
  if (typeof obj === 'object') {
    const entries = Object.entries(obj)
    if (entries.length === 0) return '{}'
    return entries.map(([key, value]) => {
      const prefix = '  '.repeat(indent)
      if (typeof value === 'object' && value !== null) {
        return `${prefix}${key}:\n${formatObjectAsKeyValue(value, indent + 1)}`
      }
      return `${prefix}${key}: ${String(value).replace(/\\n/g, '\n')}`
    }).join('\n')
  }
  
  return String(obj).replace(/\\n/g, '\n')
}

const formatToolkitResult = (result) => {
  if (typeof result === 'string') {
    try {
      const trimmed = result.trim()
      if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
        const parsed = JSON.parse(result)
        if (parsed && typeof parsed === 'object') {
          const dataToFormat = parsed.data ?? parsed
          return typeof dataToFormat === 'object' 
            ? formatObjectAsKeyValue(dataToFormat)
            : String(dataToFormat).replace(/\\n/g, '\n')
        }
      }
    } catch {
    }
    return result.replace(/\\n/g, '\n')
  }
  
  if (result && typeof result === 'object') {
    const data = result.data ?? result
    return typeof data === 'object' 
      ? formatObjectAsKeyValue(data)
      : String(data).replace(/\\n/g, '\n')
  }
  
  return String(result).replace(/\\n/g, '\n')
}
</script>

