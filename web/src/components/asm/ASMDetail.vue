<template>
  <Teleport to="body">
    <div
      v-if="visible || currentAlertId"
      class="fixed inset-0 z-50 flex items-center justify-end"
      @click.self="handleClose"
    >
      <!-- Overlay - displayed directly, no animation -->
      <div 
        class="fixed inset-0 bg-black/90"
        @click="handleClose"
      ></div>
      
      <!-- Detail panel and AI Sidebar container -->
      <div class="relative h-full">
        <!-- Detail panel - with slide-in animation -->
        <Transition name="slide" appear>
          <div
            v-if="visible"
            class="absolute right-0 h-full bg-white dark:bg-panel-dark shadow-2xl flex flex-col overflow-hidden transition-transform duration-300 ease-in-out w-[65vw]"
            :class="showAISidebar ? '-translate-x-[400px]' : ''"
            @click.stop="handlePanelClick"
          >
          <!-- Header -->
          <div class="sticky top-0 z-20 bg-white/80 dark:bg-panel-dark/80 backdrop-blur-sm border-b border-gray-200 dark:border-border-dark">
            <div class="flex items-center justify-between px-6 py-4">
              <h2 class="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <span class="material-symbols-outlined text-base">radar</span>
                {{ $t('asm.detail.title') }}
              </h2>
              <div class="flex items-center gap-2">
                <button
                  @click="handleRefresh"
                  :disabled="isRefreshing"
                  class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-200 dark:disabled:hover:bg-[#2a3546]"
                  :title="$t('common.refresh') || 'Refresh'"
                >
                  <span
                    class="material-symbols-outlined text-base"
                    :class="{ 'animate-spin': isRefreshing }"
                  >
                    refresh
                  </span>
                </button>
                <button
                  @click="openBatchCloseDialog"
                  :disabled="!canCloseAlert"
                  class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-200 dark:disabled:hover:bg-[#2a3546]"
                >
                  <span class="material-symbols-outlined text-base">archive</span>
                  {{ $t('asm.detail.closeAlert') }}
                </button>
                <button
                  @click="handleShare"
                  class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center"
                  :title="$t('alerts.detail.share') || 'Share'"
                >
                  <span class="material-symbols-outlined text-base">share</span>
                </button>
                <!-- More actions dropdown menu -->
                <div class="relative">
                  <button
                    @click.stop="showMoreActionsMenu = !showMoreActionsMenu"
                    class="more-actions-button bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white p-2 rounded-md transition-colors flex items-center justify-center"
                  >
                    <span class="material-symbols-outlined text-base">more_vert</span>
                  </button>
                  <!-- Dropdown menu -->
                  <div
                    v-if="showMoreActionsMenu"
                    @click.stop
                    class="more-actions-dropdown absolute right-0 top-full mt-2 bg-white dark:bg-[#233348] border border-gray-200 dark:border-[#324867] rounded-lg shadow-lg z-50 min-w-[180px]"
                  >
                    <button
                      @click="handleOpenAlertFromMenu"
                      :disabled="!canOpenAlert"
                      class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867] disabled:hover:bg-transparent"
                    >
                      <span class="material-symbols-outlined text-base">unarchive</span>
                      {{ $t('asm.detail.openAlert') }}
                    </button>
                    <button
                      @click="handleEditAlertFromMenu"
                      class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867]"
                    >
                      <span class="material-symbols-outlined text-base">edit</span>
                      {{ $t('alerts.detail.editAlert') }}
                    </button>
                    <button
                      @click="handleConvertToVulnerabilityFromMenu"
                      class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867]"
                    >
                      <span class="material-symbols-outlined text-base">bug_report</span>
                      {{ $t('alerts.detail.convertToVulnerability') }}
                    </button>
                  </div>
                </div>
                <!-- AI 对话按钮 -->
                <button
                  @click="handleOpenAISidebar"
                  class="w-9 h-9 rounded-full bg-gradient-to-br from-pink-500 to-orange-500 flex items-center justify-center transition-all duration-200 hover:scale-110 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
                  :title="$t('common.aiChat') || 'AI对话'"
                >
                  <span class="material-symbols-outlined text-white text-lg">auto_awesome</span>
                </button>
                <button
                  @click="handleClose"
                  class="p-2 text-gray-500 dark:text-text-light hover:text-gray-900 dark:hover:text-white transition-colors"
                >
                  <span class="material-symbols-outlined">close</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Content area -->
          <div class="flex flex-1 overflow-hidden relative">
            <!-- Loading animation - shown when loading or when closing if still loading -->
            <Transition name="fade">
              <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-white/90 dark:bg-[#111822]/90 z-10">
                <div class="flex flex-col items-center gap-4">
                  <div class="relative w-20 h-20">
                    <div class="absolute inset-0 border-4 border-primary/30 rounded-full"></div>
                    <div class="absolute inset-0 border-4 border-transparent border-t-primary border-r-primary/50 rounded-full animate-spin"></div>
                  </div>
                  <p class="text-gray-900 dark:text-white text-sm font-medium">{{ $t('common.loading') || '加载中...' }}</p>
                </div>
              </div>
            </Transition>
            
            <!-- Content -->
            <main v-if="!isLoading && alert" class="flex-1 p-6 space-y-8 overflow-y-auto custom-scrollbar">
              <!-- Title and severity -->
              <div>
                <h1 class="text-xl font-bold text-gray-900 dark:text-white">{{ alert.title }}</h1>
                <div class="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-text-light">
                  <div class="flex items-center gap-1.5">
                    <span
                      :class="[
                        'inline-flex items-center rounded-full px-3 py-1 text-sm font-medium',
                        getSeverityClass(alert.riskLevel || alert.severity?.toLowerCase())
                      ]"
                    >
                      <svg class="-ml-0.5 mr-1.5 h-2 w-2" fill="currentColor" viewBox="0 0 8 8">
                        <circle cx="4" cy="4" r="3"></circle>
                      </svg>
                      {{ $t(`common.severity.${alert.riskLevel || alert.severity?.toLowerCase() || 'medium'}`) }}
                    </span>
                  </div>
                  <div class="h-4 w-px bg-border-dark/50"></div>
                  <div class="flex items-center gap-1.5">
                    <span class="font-semibold text-gray-900 dark:text-white mr-1">{{ $t('alerts.detail.status') }}:</span>
                    <span
                      :class="[
                        'inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset',
                        getStatusBadgeClass(alert.status)
                      ]"
                    >
                      {{ $t(`alerts.list.${alert.status}`) }}
                    </span>
                  </div>
                  <div class="h-4 w-px bg-border-dark/50"></div>
                  <div class="flex items-center gap-1.5">
                    <span class="font-semibold text-gray-900 dark:text-white mr-1">{{ $t('alerts.detail.actor') }}:</span>
                    <span class="font-mono text-gray-900 dark:text-white">{{ alert.actor || '-' }}</span>
                  </div>
                  <div class="h-4 w-px bg-border-dark/50"></div>
                  <div class="flex items-center gap-1.5">
                    <span class="font-semibold text-gray-900 dark:text-white mr-1">{{ $t('alerts.detail.created') }}:</span>
                    <span class="text-gray-900 dark:text-white">{{ formatDateTime(alert.timestamp || alert.createTime) }}</span>
                  </div>
                  <div class="h-4 w-px bg-border-dark/50"></div>
                  <div class="flex items-center gap-1.5">
                    <span class="font-semibold text-gray-900 dark:text-white mr-1">{{ $t('alerts.detail.responseTime') }}:</span>
                    <span class="text-gray-900 dark:text-white">{{ alert.responseTime || '2m 15s' }}</span>
                  </div>
                </div>
              </div>

              <!-- Tabs -->
              <div class="border-b border-gray-200 dark:border-border-dark">
                <nav aria-label="Tabs" class="-mb-px flex space-x-6">
                  <button
                    v-for="tab in tabs"
                    :key="tab.key"
                    @click="activeTab = tab.key"
                    :class="[
                      'shrink-0 border-b-2 px-1 pb-3 text-sm font-medium transition-colors flex items-center gap-2',
                      activeTab === tab.key
                        ? 'border-primary text-primary font-semibold'
                        : 'border-transparent text-gray-500 dark:text-text-light hover:border-gray-600 dark:hover:border-text-dark hover:text-gray-900 dark:hover:text-white'
                    ]"
                  >
                    <span>{{ $t(tab.label) }}</span>
                    <span 
                      v-if="getTabCount(tab.key) > 0" 
                      :class="[
                        'inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 text-xs font-medium rounded-full',
                        activeTab === tab.key
                          ? 'bg-primary/20 text-primary'
                          : 'bg-gray-100 dark:bg-[#2a3546] text-gray-700 dark:text-text-light'
                      ]"
                    >
                      {{ getTabCount(tab.key) }}
                    </span>
                  </button>
                </nav>
              </div>

              <!-- Tab content -->
              <div v-if="activeTab === 'overview'">
                <h3 class="text-lg font-semibold mb-3 text-gray-900 dark:text-white">{{ $t('alerts.detail.alertInfo') }}</h3>
                <div class="grid grid-cols-1 @lg:grid-cols-2 gap-x-6 gap-y-2 text-sm font-mono @container">
                  
                  <!-- Dynamically display all fields in description -->
                  <!-- 如果 description 是对象（且不为 null），遍历显示所有字段 -->
                  <template v-if="alert?.description && typeof alert.description === 'object' && alert.description !== null && !Array.isArray(alert.description)">
                    <template
                      v-for="(value, key) in alert.description"
                      :key="key"
                    >
                      <div
                        v-if="value !== null && value !== undefined && value !== ''"
                        class="flex items-baseline gap-2"
                      >
                        <p class="text-gray-600 dark:text-text-light w-40 shrink-0 font-bold">{{ key }}:</p>
                        <div class="flex-1 min-w-0 flex items-center gap-1.5">
                          <p class="font-medium text-gray-900 dark:text-[#E3E3E3] break-all">
                            <span v-if="typeof value === 'object' && value !== null">{{ JSON.stringify(value) }}</span>
                            <span v-else>{{ value }}</span>
                          </p>
                          <button
                            v-if="isUrl(value)"
                            @click="openUrlInNewTab(value)"
                            class="shrink-0 ml-1 p-1 text-primary hover:text-primary/80 transition-colors"
                            :title="$t('common.openInNewWindow')"
                          >
                            <span class="material-symbols-outlined text-base">open_in_new</span>
                          </button>
                        </div>
                      </div>
                    </template>
                  </template>
                  <!-- 如果 description 不是对象（字符串、数字、布尔值等），直接显示 -->
                  <div v-else-if="alert?.description !== null && alert?.description !== undefined" class="flex items-baseline">
                    <p class="w-40 shrink-0 font-bold text-gray-900 dark:text-[#f5f5f5]">{{ $t('alerts.detail.description') || '描述' }}:</p>
                    <div class="flex-1 min-w-0 flex items-center gap-1.5">
                      <p class="font-medium text-gray-900 dark:text-[#f5f5f5] break-all">{{ alert.description }}</p>
                      <button
                        v-if="isUrl(alert.description)"
                        @click="openUrlInNewTab(alert.description)"
                        class="shrink-0 ml-1 p-1 text-primary hover:text-primary/80 transition-colors"
                        :title="$t('common.openInNewWindow')"
                      >
                        <span class="material-symbols-outlined text-base">open_in_new</span>
                      </button>
                    </div>
                  </div>
                </div>
                
                <!-- 分割线 -->
                <div class="mt-6 border-t border-border-dark"></div>

                <!-- Comments area -->
                <div class="pt-4">
                  <CommentSection
                    :comments="alert?.comments || []"
                    :title="$t('alerts.detail.comments.title')"
                    use-avatar-component
                    :loading="isSubmittingComment"
                    @submit="handleAddComment"
                  />
                  
                  <!-- 分割线 -->
                  <div class="mt-6 border-t border-border-dark"></div>
                </div>
              </div>

              <!-- Threat intelligence tab -->
              <div v-if="activeTab === 'threatIntelligence'">
                <div v-if="!alert?.intelligence || alert.intelligence.length === 0" class="text-text-light text-sm py-12 text-center">
                  {{ $t('alerts.detail.noThreatIntelligence') }}
                </div>
                
                <div v-else class="space-y-6">
                  <!-- Display intelligence data returned from alert detail API -->
                  <div v-if="alert?.intelligence && alert.intelligence.length > 0" class="grid grid-cols-1 @lg:grid-cols-2 gap-4">
                    <AlertInfoCard
                      v-for="(item, index) in alert.intelligence"
                      :key="`intel-${index}`"
                    :title="item.title || $t('alerts.detail.threatIntelligence')"
                    :header-meta="item.time || '-'"
                    :html-content="item.content || ''"
                    :summary="item.summary"
                    :owner="item.author || $t('alerts.detail.unknownSource')"
                    />
                  </div>
                </div>
              </div>

              <div v-if="activeTab === 'aiAgent'">
                <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">{{ $t('alerts.detail.aiAgent') }}</h3>
                <div class="space-y-6">
                  <!-- Display AI data returned from backend -->
                  <div
                    v-for="(aiItem, index) in alert?.ai || []"
                    :key="`ai-${index}`"
                    class="flex items-start gap-4"
                  >
                    <div
                      class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600"
                    >
                      <span class="material-symbols-outlined text-gray-900 dark:text-white text-sm">smart_toy</span>
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="flex items-baseline gap-2">
                        <p class="font-semibold text-gray-900 dark:text-white">{{ aiItem.author || 'AI Agent' }}</p>
                        <p class="text-xs text-text-light">{{ formatDateTime(aiItem.create_time || aiItem.time) }}</p>
                      </div>
                      <div class="mt-1 text-sm text-gray-700 dark:text-[#c3d3e8] bg-white dark:bg-[#2a3546] border border-gray-200 dark:border-transparent p-3 rounded-lg rounded-tl-none max-w-full overflow-hidden">
                        <div
                          :class="[
                            'bg-gray-50 dark:bg-transparent text-gray-800 dark:text-inherit rounded-md p-2 border border-gray-200 dark:border-transparent ai-agent__html',
                            { 'ai-agent__html--dark': isDarkMode }
                          ]"
                          v-html="sanitizeHtml(aiItem.content || '')"
                        ></div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- If no AI data, show prompt -->
                  <div v-if="!alert?.ai || alert.ai.length === 0" class="text-text-light text-sm">
                    {{ $t('alerts.detail.noAiResponse') }}
                  </div>
                </div>
                
              </div>
            </main>
            
            <!-- No data state -->
            <div v-if="!isLoading && !alert" class="flex-1 flex items-center justify-center">
              <p class="text-text-light text-sm">{{ $t('common.noData') }}</p>
            </div>

            <!-- Sidebar -->
            <aside
              v-if="!isLoading && alert"
              class="w-80 border-l border-gray-200 dark:border-border-dark bg-gray-50 dark:bg-[#1f2937]/20 flex flex-col overflow-hidden"
            >

              <!-- Response 页签内容 -->
              <div ref="toolkitScrollContainerRef" class="overflow-y-auto custom-scrollbar flex-1 pl-6 pb-6">
                <div class="pr-6 space-y-6">
                <!-- 自动化响应 -->
                <div class="space-y-4">
                  <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ $t('common.automatedResponse') }}</h3>
                  
                  <!-- 加载状态 -->
                  <div v-if="loadingToolkits || loadingToolkitRecords" class="flex items-center justify-center py-8">
                    <span class="material-symbols-outlined animate-spin text-primary text-2xl">refresh</span>
                  </div>
                  
                  <div v-else class="space-y-4">
                    <!-- 工具清单部分：显示所有可用工具 -->
                    <div v-if="toolkits.length" class="space-y-2">
                      <h4 class="text-sm font-medium text-gray-600 dark:text-text-light">{{ $t('alerts.detail.availableTools') }}</h4>
                      <template v-for="tool in toolkits" :key="tool.app_id">
                        <details 
                          :open="expandedToolkitIds.has(tool.app_id)"
                          class="group rounded-lg bg-gray-100 dark:bg-[#2a3546]"
                        >
                          <summary class="flex items-center justify-between p-3 cursor-pointer list-none hover:bg-gray-200 dark:hover:bg-[#3c4a60]">
                            <div class="flex items-center gap-3">
                              <span class="material-symbols-outlined text-primary">play_circle</span>
                              <div>
                                <p class="font-medium text-gray-900 dark:text-white text-sm">{{ tool.title }}</p>
                                <p class="text-xs text-gray-600 dark:text-text-light">{{ $t('alerts.detail.toolkitClickToConfigure') }}</p>
                              </div>
                            </div>
                            <span class="material-symbols-outlined text-gray-600 dark:text-text-light group-hover:text-gray-900 dark:group-hover:text-white marker">expand_more</span>
                          </summary>
                          <div class="px-3 pb-3 pt-2 text-sm text-gray-600 dark:text-text-light space-y-3 border-t border-gray-200 dark:border-border-dark/50">
                            <div v-for="param in tool.params" :key="param.name">
                              <label class="block text-xs font-medium text-gray-600 dark:text-text-light mb-1" :for="`toolkit-${tool.app_id}-${param.name}`">
                                {{ param.label }}
                                <span v-if="param.required !== false" class="text-red-500 ml-1">*</span>
                              </label>
                              <!-- Enum parameter: use select dropdown -->
                              <div v-if="param.enum && param.enum.length > 0" class="relative">
                                <select
                                  class="w-full rounded-md border border-gray-300 dark:border-border-dark bg-white dark:bg-[#1a202c] p-2 pr-8 text-gray-900 dark:text-white focus:border-primary focus:ring-primary text-sm appearance-none cursor-pointer"
                                  :id="`toolkit-${tool.app_id}-${param.name}`"
                                  :value="toolkitParams[tool.app_id]?.[param.name] ?? (param.default_value !== undefined && param.default_value !== null ? param.default_value : '')"
                                  @change="updateToolkitParam(tool.app_id, param.name, $event.target.value)"
                                >
                                  <option v-if="param.default_value === undefined || param.default_value === null" value="" disabled>请选择</option>
                                  <option v-for="enumValue in param.enum" :key="enumValue" :value="enumValue">
                                    {{ enumValue }}
                                  </option>
                                </select>
                                <span class="material-symbols-outlined absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-gray-500 dark:text-gray-400 text-lg">expand_more</span>
                              </div>
                              <!-- Regular parameter: use input -->
                              <input 
                                v-else
                                class="w-full rounded-md border border-gray-300 dark:border-border-dark bg-white dark:bg-[#1a202c] p-2 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-text-dark focus:border-primary focus:ring-primary text-sm" 
                                :id="`toolkit-${tool.app_id}-${param.name}`"
                                :placeholder="param.default_value !== undefined && param.default_value !== null ? `默认: ${param.default_value}` : `e.g., ${param.label}`"
                                type="text" 
                                :value="toolkitParams[tool.app_id]?.[param.name] ?? (param.default_value !== undefined && param.default_value !== null ? param.default_value : '')"
                                @input="updateToolkitParam(tool.app_id, param.name, $event.target.value)"
                              />
                            </div>
                            <button 
                              @click="handleExecuteToolkit(tool)"
                              :disabled="executingToolkitId === tool.app_id"
                              class="w-full bg-primary hover:bg-blue-500 text-sm font-medium text-white px-4 py-2 rounded-md transition-colors flex items-center gap-2 justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-primary"
                            >
                              <span :class="['material-symbols-outlined text-base', executingToolkitId === tool.app_id && 'animate-spin']">
                                {{ executingToolkitId === tool.app_id ? 'refresh' : 'play_arrow' }}
                              </span>
                              {{ executingToolkitId === tool.app_id ? $t('alerts.detail.toolkitExecuting') : $t('alerts.detail.toolkitExecute') }}
                            </button>
                            <!-- 执行结果展示 -->
                            <div 
                              v-if="toolkitExecutionResults[tool.app_id]"
                              :ref="el => { if (el) toolkitResultRefs[tool.app_id] = el }"
                              class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700"
                            >
                              <div class="flex items-center gap-1.5 mb-1">
                                <span 
                                  :class="[
                                    'material-symbols-outlined text-sm',
                                    toolkitExecutionResults[tool.app_id].status === 'completed' ? 'text-green-400' : 'text-red-400'
                                  ]"
                                >
                                  {{ toolkitExecutionResults[tool.app_id].status === 'completed' ? 'check_circle' : 'error' }}
                                </span>
                                <span 
                                  :class="[
                                    'text-xs font-medium',
                                    toolkitExecutionResults[tool.app_id].status === 'completed' 
                                      ? 'text-green-600 dark:text-green-400' 
                                      : 'text-red-600 dark:text-red-400'
                                  ]"
                                >
                                  {{ toolkitExecutionResults[tool.app_id].status === 'completed' 
                                    ? ($t('alerts.detail.result') || '结果') 
                                    : ($t('alerts.detail.error') || '错误') 
                                  }}
                                </span>
                              </div>
                              <pre 
                                :class="[
                                  'text-xs whitespace-pre-wrap break-words font-mono',
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
                    <div v-if="toolkitRecords.length" class="space-y-2">
                      <h4 class="text-sm font-medium text-gray-600 dark:text-text-light">{{ $t('alerts.detail.executionRecords') }}</h4>
                      <template v-for="record in toolkitRecords" :key="record.id">
                        <details :class="['group rounded-lg bg-gray-100 dark:bg-[#2a3546]', record.status === 'running' && 'animate-pulse']">
                          <summary class="flex items-center justify-between p-3 cursor-pointer list-none hover:bg-gray-200 dark:hover:bg-[#3c4a60]">
                            <div class="flex items-center gap-3">
                              <span :class="[
                                'material-symbols-outlined',
                                record.status === 'completed' && 'text-green-400',
                                record.status === 'running' && 'text-yellow-400',
                                record.status === 'failed' && 'text-red-400'
                              ]">
                                {{ record.status === 'completed' ? 'task_alt' : record.status === 'running' ? 'hourglass_top' : 'error' }}
                              </span>
                              <div>
                                <p class="font-medium text-gray-900 dark:text-white text-sm">{{ record.title }}</p>
                                <p :class="[
                                  'text-xs',
                                  record.status === 'completed' && 'text-green-600 dark:text-green-300/80',
                                  record.status === 'running' && 'text-yellow-600 dark:text-yellow-300/80',
                                  record.status === 'failed' && 'text-red-600 dark:text-red-300/80'
                                ]">
                                  {{ record.status === 'completed' ? $t('alerts.detail.toolkitStatusSuccess') : 
                                     record.status === 'running' ? $t('alerts.detail.toolkitStatusInProgress') : 
                                     $t('alerts.detail.toolkitStatusFailed') }}
                                </p>
                              </div>
                            </div>
                            <span class="material-symbols-outlined text-gray-600 dark:text-text-light group-hover:text-gray-900 dark:group-hover:text-white marker">expand_more</span>
                          </summary>
                          <div class="px-3 pb-3 pt-2 text-sm text-gray-600 dark:text-text-light font-mono space-y-1 border-t border-gray-200 dark:border-border-dark/50">
                            <p><span class="text-gray-500 dark:text-text-dark">{{ $t('alerts.detail.executionTime') }}:</span> {{ formatDateTime(record.create_time) }}</p>
                            <p><span class="text-gray-500 dark:text-text-dark">{{ $t('alerts.detail.executor') }}:</span> {{ record.owner || $t('alerts.detail.system') }}</p>
                            <div v-if="record.result" :class="['mt-2 pt-2 border-t border-gray-200 dark:border-border-dark/50', record.status === 'failed' && 'text-red-600 dark:text-red-300']">
                              <span class="text-gray-500 dark:text-text-dark">{{ record.status === 'failed' ? $t('alerts.detail.error') : $t('alerts.detail.result') }}:</span>
                              <pre class="mt-1 text-xs whitespace-pre-wrap">{{ formatToolkitResult(record.result) }}</pre>
                            </div>
                          </div>
                        </details>
                      </template>
                    </div>
                    
                    <!-- 如果没有工具和记录，显示空状态 -->
                    <div v-if="!toolkits.length && !toolkitRecords.length" class="text-center py-8 text-text-light">
                      <p class="text-sm">{{ $t('alerts.detail.noToolkitsAvailable') }}</p>
                    </div>
                  </div>
                </div>

                <!-- 事件时间线 -->
                <div class="space-y-4" v-if="alert?.timeline">
                  <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ $t('alerts.detail.eventTimeline') }}</h3>
                  <div class="relative pl-6">
                    <div class="absolute left-0 h-full w-0.5 bg-gray-200 dark:bg-border-dark"></div>
                    <div class="relative space-y-6">
                      <div
                        v-for="(event, index) in alert.timeline"
                        :key="index"
                        class="relative"
                      >
                        <div
                          :class="[
                            'absolute -left-7 top-1.5 h-2 w-2 rounded-full ring-4 ring-gray-100 dark:ring-panel-dark',
                            index === 0 ? 'bg-primary' : 'bg-gray-300 dark:bg-border-dark'
                          ]"
                        ></div>
                        <p class="text-xs text-gray-500 dark:text-text-light">{{ event.time }}</p>
                        <p class="text-sm text-gray-900 dark:text-white">{{ event.event }}</p>
                      </div>
                    </div>
                  </div>
                </div>
                </div>
              </div>
            </aside>
          </div>
        </div>
      </Transition>

        <!-- AI Sidebar - 在Detail panel外部，从右侧展开，紧贴Detail panel右边缘 -->
        <Transition name="slide">
          <AISidebar
            v-if="showAISidebar && visible"
            ref="aiSidebarRef"
            :visible="showAISidebar"
            :alert-title="alert?.title || ''"
            :alert-id="currentAlertId"
            :finding-summary="aiFindingSummary"
            :show-finding-summary="showFindingSummary"
            :show-overlay="false"
            position="fixed"
            @close="showAISidebar = false"
            @open-in-new="handleAIOpenInNew"
            @send-message="handleAISendMessage"
            @tool-action="handleAIToolAction"
          />
        </Transition>
      </div>
    </div>

    <!-- 批量关闭对话框 -->
    <div
      v-if="showBatchCloseDialog"
      class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50"
      @click.self="closeBatchCloseDialog"
    >
      <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-lg p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ $t('alerts.list.batchCloseDialog.title') }}
          </h2>
          <button
            @click="closeBatchCloseDialog"
            class="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
          </button>
        </div>

        <!-- 提示信息 -->
        <div class="mb-4 p-3 bg-gray-100 dark:bg-[#1e293b] rounded-md">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ $t('alerts.list.batchCloseDialog.confirmMessage', { count: 1 }) }}
          </p>
        </div>

        <!-- 结论分类下拉框 -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
            {{ $t('alerts.list.batchCloseDialog.conclusionCategory') }}
            <span class="text-red-500 ml-1">*</span>
          </label>
          <select
            v-model="closeConclusion.category"
            class="w-full bg-gray-100 dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value="">{{ $t('alerts.list.batchCloseDialog.selectCategory') }}</option>
            <option value="falsePositive">{{ $t('alerts.list.batchCloseDialog.categories.falsePositive') }}</option>
            <option value="resolved">{{ $t('alerts.list.batchCloseDialog.categories.resolved') }}</option>
            <option value="repeated">{{ $t('alerts.list.batchCloseDialog.categories.repeated') }}</option>
            <option value="other">{{ $t('alerts.list.batchCloseDialog.categories.other') }}</option>
          </select>
        </div>

        <!-- 调查结论输入框 -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
            {{ $t('alerts.list.batchCloseDialog.conclusion') }}
          </label>
          <div class="relative">
            <textarea
              v-model="closeConclusion.notes"
              rows="4"
              class="w-full bg-gray-100 dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary resize-none"
              :placeholder="$t('alerts.list.batchCloseDialog.conclusionPlaceholder')"
              @focus="handleNotesFocus"
              @click="handleNotesClick"
              @blur="handleNotesBlur"
            ></textarea>
            <div
              v-if="showRecentCloseComments && recentCloseComments.length"
              class="absolute left-0 right-0 top-full mt-2 bg-white dark:bg-[#1e293b] border border-gray-200 dark:border-[#324867] rounded-md shadow-lg z-10 max-h-48 overflow-y-auto"
            >
              <p
                v-for="(comment, index) in recentCloseComments"
                :key="index"
                class="px-4 py-2 text-sm text-gray-900 dark:text-white border-b border-gray-200 dark:border-[#324867]/40 last:border-b-0 cursor-pointer hover:bg-gray-100 dark:hover:bg-[#22324a]"
                @mousedown.prevent="handleRecentCommentSelect(comment)"
              >
                {{ comment }}
              </p>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex items-center justify-end gap-3">
          <button
            @click="closeBatchCloseDialog"
            class="px-4 py-2 text-sm text-gray-700 dark:text-gray-400 bg-gray-100 dark:bg-[#1e293b] rounded-md hover:bg-gray-200 dark:hover:bg-primary/30 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="handleBatchClose"
            :disabled="!closeConclusion.category || !closeConclusion.notes.trim() || isClosing"
            class="px-4 py-2 text-sm text-white bg-primary rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span
              v-if="isClosing"
              class="material-symbols-outlined text-base animate-spin"
            >
              refresh
            </span>
            {{ $t('common.submit') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑告警对话框 -->
    <EditAlertDialog
      :visible="showEditAlertDialog"
      :alert-id="currentAlertId"
      :initial-data="editAlertInitialData"
      workspace="asm"
      @close="closeEditAlertDialog"
      @updated="handleAlertUpdated"
    />

    <!-- 创建漏洞对话框 -->
    <CreateVulnerabilityDialog
      :visible="showCreateVulnerabilityDialog"
      :initial-data="createVulnerabilityInitialData"
      :alert-ids="currentAlertId ? [currentAlertId] : []"
      workspace="asm"
      @close="closeCreateVulnerabilityDialog"
      @created="handleVulnerabilityCreated"
    />

    <!-- 分享成功提示 -->
    <Transition name="fade">
      <div
        v-if="showShareSuccess"
        class="fixed top-4 right-4 z-[100] bg-green-500 text-white px-4 py-2 rounded-md shadow-lg flex items-center gap-2"
      >
        <span class="material-symbols-outlined text-sm">check_circle</span>
        <span class="text-sm">{{ $t('alerts.detail.shareSuccess') || '已复制到剪切板' }}</span>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { getASMDetail, openASMItem, closeASMItem } from '@/api/asm'
import { postComment } from '@/api/comments'
import { getToolkits, getToolkitRecords, executeToolkit } from '@/api/toolkits'
import EditAlertDialog from '@/components/alerts/EditAlertDialog.vue'
import CreateVulnerabilityDialog from '@/components/vulnerabilities/CreateVulnerabilityDialog.vue'
import AlertInfoCard from '@/components/alerts/AlertInfoCard.vue'
import AiChatDialog from '@/components/alerts/AiChatDialog.vue'
import { formatDateTime, calculateTTR, parseToDate } from '@/utils/dateTime'
import DOMPurify from 'dompurify'
import UserAvatar from '@/components/common/UserAvatar.vue'
import CommentInput from '@/components/common/CommentInput.vue'
import CommentSection from '@/components/common/CommentSection.vue'
import AISidebar from '@/components/common/AISidebar.vue'
import { useToast } from '@/composables/useToast'
import { useRecentCloseCommentSuggestions } from '@/composables/useRecentCloseCommentSuggestions'
import { useDarkModeObserver } from '@/composables/useDarkModeObserver'

const props = defineProps({
  alertId: {
    type: [Number, String],
    required: false,
    default: null
  }
})

const emit = defineEmits(['close', 'closed', 'created'])

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const toast = useToast()

const visible = ref(false)
const alert = ref(null)
const isLoading = ref(false)

// 获取告警ID：优先使用props，如果没有则从路由参数获取
const currentAlertId = computed(() => {
  return props.alertId || route.params.id
})
const activeTab = ref('overview')
const newComment = ref('')
// Comment input is now handled by CommentInput component
// AI 对话相关
const newAiMessage = ref('')
const uploadedAiFiles = ref([])
const aiFileInput = ref(null)
const isAiDragging = ref(false)
// 右侧侧边栏AI问答相关（独立于主内容区域的AI问答）
const rightSidebarAiMessage = ref('')
const rightSidebarAiFiles = ref([])
const rightSidebarAiFileInput = ref(null)
const isRightSidebarAiDragging = ref(false)
const showBatchCloseDialog = ref(false)
const isClosing = ref(false)
const closeConclusion = ref({
  category: 'falsePositive',
  notes: ''
})
const { isDarkMode } = useDarkModeObserver()
const {
  recentComments: recentCloseComments,
  showDropdown: showRecentCloseComments,
  refresh: refreshRecentCloseComments,
  persist: persistRecentCloseComment,
  handleFocus: handleNotesFocus,
  handleClick: handleNotesClick,
  handleBlur: handleNotesBlur,
  handleSelect: applyRecentCloseComment,
  hideDropdown: hideRecentCloseCommentsDropdown
} = useRecentCloseCommentSuggestions({
  onApply: (comment) => {
    closeConclusion.value.notes = comment
  }
})
const showEditAlertDialog = ref(false)
const editAlertInitialData = ref(null)
const showShareSuccess = ref(false)
const showMoreActionsMenu = ref(false)
const isRefreshing = ref(false)
const showCreateVulnerabilityDialog = ref(false)
const createVulnerabilityInitialData = ref(null)
const isSubmittingComment = ref(false)
const showAISidebar = ref(false)
const aiSidebarRef = ref(null)
const aiFindingSummary = ref('')
const showFindingSummary = ref(false)
const hasAutoOpenedAiSidebar = ref(false)

// Toolkit related state
const toolkits = ref([])
const toolkitRecords = ref([])
const loadingToolkits = ref(false)
const loadingToolkitRecords = ref(false)
const executingToolkitId = ref(null) // 正在执行的工具ID
const toolkitParams = ref({}) // 存储每个工具的输入参数 { app_id: { param_name: value } }
const toolkitExecutionResults = ref({}) // 存储每个工具的执行结果 { app_id: { status, result } }
const expandedToolkitIds = ref(new Set()) // 存储展开的工具ID集合
const toolkitResultRefs = ref({}) // 存储每个工具结果区域的 ref
const toolkitScrollContainerRef = ref(null) // 工具区域的滚动容器 ref

const tabs = [
  { key: 'overview', label: 'alerts.detail.overview' },
  { key: 'threatIntelligence', label: 'alerts.detail.threatIntelligence' },
  { key: 'aiAgent', label: 'alerts.detail.aiAgent' }
]

const getTabCount = (tabKey) => {
  if (!alert.value) return 0
  
  switch (tabKey) {
    case 'overview':
      return alert.value.comments?.length || 0
    case 'threatIntelligence':
      return alert.value.intelligence?.length || 0
    case 'aiAgent':
      return alert.value.ai?.length || 0
    default:
      return 0
  }
}

const stripHtmlTags = (html = '') => {
  if (!html || typeof html !== 'string') return ''
  return html
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/(p|div|pre)>/gi, '\n')
    .replace(/<[^>]*>/g, '')
    .replace(/\n{2,}/g, '\n')
    .trim()
}

const extractFirstBoldText = (html = '') => {
  const match = html.match(/<b>([\s\S]*?)<\/b>/i)
  if (match && match[1]) {
    return stripHtmlTags(match[1])
  }
  return ''
}

const sanitizeHtml = (html) => {
  if (!html || typeof html !== 'string') return ''
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['br', 'strong', 'em', 'pre', 'code', 'b', 'i', 'u', 'p'],
    ALLOWED_ATTR: []
  })
}

const transformAlertDetailData = (apiData) => {
  if (!apiData) return null

  const severityMap = {
    'Fatal': 'fatal',
    'High': 'high',
    'Medium': 'medium',
    'Low': 'low',
    'Tips': 'tips'
  }
  
  const statusMap = {
    'Open': 'open',
    'Block': 'block',
    'Closed': 'closed'
  }

  const description = apiData.description !== null && apiData.description !== undefined
    ? apiData.description
    : {}
  const extendProperties = apiData.extend_properties || {}
  const computedTtr = calculateTTR(
    apiData.create_time || apiData.createTime,
    apiData.close_time || apiData.closeTime,
    apiData.handle_status
  )
  const normalizedTtr = computedTtr === '-' && apiData.ttr ? apiData.ttr : computedTtr

  const comments = (apiData.comments || []).map(comment => ({
    id: comment.id || Date.now(),
    author: comment.author || 'Unknown',
    authorInitials: (comment.author || 'U').substring(0, 2).toUpperCase(),
    time: formatDateTime(comment.create_time || comment.time),
    content: comment.content || '',
    file: comment.file || null
  }))

  const intelligence = (apiData.intelligence || []).map(item => ({
    id: item.id || Date.now(),
    author: item.author || 'Unknown',
    time: item.create_time || item.time || '-',
    content: item.content || ''
  }))

  const ai = (apiData.ai || []).map(item => ({
    id: item.id || Date.now(),
    author: item.author || 'AI Agent',
    time: item.create_time || item.time || '-',
    content: item.content || ''
  }))

  const entities = (apiData.entities || []).map(entity => ({
    type: entity.type || 'unknown',
    name: entity.name || '',
    label: entity.from || entity.label || ''
  }))

  const timeline = (apiData.timeline || []).map(event => {
    const formattedTime = formatDateTime(event.time || event.timestamp)
    return {
      time: formattedTime !== '-' ? formattedTime : (event.time || '-'),
      event: event.event || ''
    }
  })

  const descriptionObj = typeof description === 'object' && description !== null ? description : {}
  const sourceIp = descriptionObj.srcip || descriptionObj.sourceIp || descriptionObj.src_ip
  const userName = descriptionObj.username || descriptionObj.userName || descriptionObj.user_name
  const destinationHostname = descriptionObj.destinationHostname || descriptionObj.dest_hostname
  const ruleName = extendProperties.rule_name || descriptionObj.model_name || ''

  return {
    id: apiData.id,
    title: apiData.title || '',
    severity: apiData.severity || 'Medium',
    riskLevel: severityMap[apiData.severity] || apiData.severity?.toLowerCase() || 'medium',
    handle_status: apiData.handle_status || 'Open',
    status: statusMap[apiData.handle_status] || apiData.handle_status?.toLowerCase() || 'open',
    owner: apiData.owner || '',
    actor: apiData.actor || apiData.owner || '',
    creator: apiData.creator || '',
    createTime: apiData.create_time || apiData.createTime,
    updateTime: apiData.update_time || apiData.updateTime,
    closeTime: apiData.close_time || apiData.closeTime,
    arriveTime: apiData.arrive_time || apiData.arriveTime,
    timestamp: apiData.create_time || apiData.arrive_time || apiData.timestamp,
    labels: apiData.labels || '',
    close_reason: apiData.close_reason,
    is_auto_closed: apiData.is_auto_closed,
    close_comment: apiData.close_comment,
    responseTime: normalizedTtr,
    ttd: apiData.ttd,
    description: description,
    extend_properties: extendProperties,
    ruleName: ruleName,
    sourceIp: sourceIp,
    userName: userName,
    destinationHostname: destinationHostname,
    comments: comments,
    intelligence: intelligence,
    ai: ai,
    associatedEntities: entities,
    entities: entities,
    timeline: timeline,
    historic: apiData.historic || []
  }
}

const stripHtmlAndEntities = (html = '') => {
  if (!html || typeof html !== 'string') return ''
  return html
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/(p|div|pre)>/gi, '\n')
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&[a-z]+;/gi, ' ')
    .replace(/\n{2,}/g, '\n')
    .trim()
}

const findInvestigationContent = () => {
  if (!alert.value?.ai?.length) return ''
  const firstContent = alert.value.ai[0]?.content || ''
  return stripHtmlAndEntities(firstContent)
}

// 打开AI侧边栏并设置investigation内容
const openAISidebarWithInvestigation = async () => {
  if (!alert.value) return
  const investigationContent = findInvestigationContent()
  aiFindingSummary.value = investigationContent
  showFindingSummary.value = !!investigationContent
  showAISidebar.value = true
  await nextTick()
}

const getASMUrl = () => {
  const raw = import.meta.env.VITE_WEB_BASE_PATH
  const basePath = raw && raw !== '/' 
    ? (raw.startsWith('/') ? raw : `/${raw}`).replace(/\/$/, '')
    : ''
  return `${window.location.origin}${basePath}/asm/${currentAlertId.value}`
}

const loadAlertDetail = async (showLoading = true) => {
  if (!currentAlertId.value) return
  
  if (showLoading) {
    alert.value = null
    isLoading.value = true
  }
  
  visible.value = true
  await new Promise(resolve => setTimeout(resolve, 50))
  
  try {
    const response = await getASMDetail(currentAlertId.value)
    alert.value = transformAlertDetailData(response.data)
    loadToolkits()
    loadToolkitRecords()
    // 重置自动展开标记，交由 watcher 根据 AI Investigation 决定是否展开
    hasAutoOpenedAiSidebar.value = false
  } catch (error) {
    console.error('Failed to load alert detail:', error)
    emit('close')
  } finally {
    if (showLoading) {
      isLoading.value = false
    }
  }
}

const loadToolkits = async () => {
  loadingToolkits.value = true
  try {
    const response = await getToolkits()
    toolkits.value = response.tools || []
    console.log('Loaded toolkits:', toolkits.value, 'Response:', response)
    toolkits.value.forEach(tool => {
      if (!toolkitParams.value[tool.app_id]) {
        toolkitParams.value[tool.app_id] = {}
      }
    })
  } catch (error) {
    console.error('Failed to load toolkits:', error)
    toolkits.value = []
    toast.error(error?.response?.data?.error_message || error?.message || t('alerts.detail.loadToolkitsError') || '加载工具列表失败')
  } finally {
    loadingToolkits.value = false
  }
}

const loadToolkitRecords = async () => {
  loadingToolkitRecords.value = true
  try {
    const response = await getToolkitRecords(currentAlertId.value || null)
    toolkitRecords.value = response.data || []
    console.log('Loaded toolkit records:', toolkitRecords.value, 'Response:', response)
  } catch (error) {
    console.error('Failed to load toolkit records:', error)
    toolkitRecords.value = []
    if (error?.response?.status !== 400) {
      toast.error(error?.response?.data?.error_message || error?.message || t('alerts.detail.loadToolkitRecordsError') || '加载执行记录失败')
    }
  } finally {
    loadingToolkitRecords.value = false
  }
}

const handleExecuteToolkit = async (tool) => {
  const params = toolkitParams.value[tool.app_id] || {}
  const allParams = tool.params || []
  // 只验证 required 为 true 的参数，如果 required 字段不存在，默认为必填（向后兼容）
  const requiredParams = allParams.filter(p => p.required !== false)
  const missingParams = requiredParams.filter(p => {
    const value = params[p.name]
    // 如果参数值为空字符串、null 或 undefined，则认为缺失
    return !value || (typeof value === 'string' && value.trim() === '')
  })
  
  if (missingParams.length > 0) {
    const paramNames = missingParams.map(p => p.label).join(', ')
    toast.error(t('alerts.detail.toolkitParamsRequired', { params: paramNames }) || `请填写参数: ${paramNames}`)
    return
  }

  executingToolkitId.value = tool.app_id
  // 清空之前的结果
  toolkitExecutionResults.value[tool.app_id] = null

  try {
    const requestData = {
      title: tool.title,
      app_id: tool.app_id,
      app_type: tool.app_type,
      params: params
    }

    const response = await executeToolkit(currentAlertId.value || null, requestData)
    // 存储执行结果
    const resultData = response?.data || response
    if (resultData) {
      toolkitExecutionResults.value[tool.app_id] = {
        status: resultData.status || 'completed',
        result: resultData.result || null
      }
    }
    toast.success(t('alerts.detail.toolkitExecuteSuccess'))
    // 确保工具抽屉展开并滚动到结果区域
    await scrollToToolkitResult(tool.app_id)
  } catch (error) {
    console.error('Failed to execute toolkit:', error)
    // 存储错误结果
    toolkitExecutionResults.value[tool.app_id] = {
      status: 'failed',
      result: error?.response?.data?.error_message || error?.message || t('alerts.detail.toolkitExecuteError') || '工具执行失败'
    }
    toast.error(error?.response?.data?.error_message || error?.message || t('alerts.detail.toolkitExecuteError'))
    // 确保工具抽屉展开并滚动到结果区域
    await scrollToToolkitResult(tool.app_id)
  } finally {
    executingToolkitId.value = null
    await loadToolkitRecords()
  }
}

const updateToolkitParam = (appId, paramName, value) => {
  if (!toolkitParams.value[appId]) {
    toolkitParams.value[appId] = {}
  }
  toolkitParams.value[appId][paramName] = value
}

const scrollToToolkitResult = async (appId) => {
  // 确保工具抽屉展开
  expandedToolkitIds.value.add(appId)
  
  // 等待 DOM 更新
  await nextTick()
  
  // 再次等待，确保结果区域已渲染
  await nextTick()
  
  // 滚动到结果区域
  const resultElement = toolkitResultRefs.value[appId]
  if (resultElement && toolkitScrollContainerRef.value) {
    // 计算结果元素相对于滚动容器的位置
    const containerRect = toolkitScrollContainerRef.value.getBoundingClientRect()
    const elementRect = resultElement.getBoundingClientRect()
    const scrollTop = toolkitScrollContainerRef.value.scrollTop
    const targetScrollTop = scrollTop + elementRect.top - containerRect.top - 20 // 留20px的顶部间距
    
    // 平滑滚动到目标位置
    toolkitScrollContainerRef.value.scrollTo({
      top: targetScrollTop,
      behavior: 'smooth'
    })
  }
}

const formatToolkitResult = (result) => {
  if (typeof result === 'string') {
    try {
      if (result.startsWith('{')) {
        return JSON.stringify(JSON.parse(result), null, 2)
      }
      return result
    } catch {
      return result
    }
  }
  return String(result)
}

const handleClose = async () => {
  showMoreActionsMenu.value = false
  
  const closeDelay = 300
  const startTime = Date.now()
  
  if (isLoading.value) {
    while (isLoading.value && (Date.now() - startTime) < closeDelay) {
      await new Promise(resolve => setTimeout(resolve, 50))
    }
  }
  
  visible.value = false
  
  setTimeout(() => {
    emit('close')
  }, closeDelay)
}

const openBatchCloseDialog = () => {
  if (!canCloseAlert.value) {
    return
  }
  refreshRecentCloseComments()
  hideRecentCloseCommentsDropdown()
  showBatchCloseDialog.value = true
}

const closeBatchCloseDialog = () => {
  showBatchCloseDialog.value = false
  closeConclusion.value = {
    category: 'falsePositive',
    notes: ''
  }
  hideRecentCloseCommentsDropdown()
  isClosing.value = false
}

const handleBatchClose = async () => {
  if (!closeConclusion.value.category || !closeConclusion.value.notes.trim()) {
    return
  }

  if (!currentAlertId.value) {
    return
  }

  isClosing.value = true

  try {
    await closeASMItem(currentAlertId.value, {
      category: closeConclusion.value.category,
      notes: closeConclusion.value.notes.trim()
    })
    persistRecentCloseComment(closeConclusion.value.notes.trim())
    closeBatchCloseDialog()
    await loadAlertDetail()
    emit('closed')
  } catch (error) {
    console.error('Failed to close alert:', error)
    isClosing.value = false
  }
}

const handleRecentCommentSelect = (comment) => {
  applyRecentCloseComment(comment)
}

const canCloseAlert = computed(() => {
  return alert.value && alert.value.status !== 'closed'
})

const canOpenAlert = computed(() => {
  return alert.value && alert.value.status === 'closed'
})

const handleOpenAlert = async () => {
  if (!canOpenAlert.value || !currentAlertId.value) {
    return
  }

  try {
    await openASMItem(currentAlertId.value)
    await loadAlertDetail()
    emit('closed')
  } catch (error) {
    console.error('Failed to open alert:', error)
  }
}

const openCreateVulnerabilityDialog = () => {
  if (!alert.value) {
    console.warn('Alert data not loaded')
    return
  }
  
  let alertDescription = ''
  if (alert.value.aiAnalysis?.description) {
    alertDescription = typeof alert.value.aiAnalysis.description === 'string' 
      ? alert.value.aiAnalysis.description 
      : JSON.stringify(alert.value.aiAnalysis.description)
  } else if (alert.value.description) {
    alertDescription = typeof alert.value.description === 'string' 
      ? alert.value.description 
      : JSON.stringify(alert.value.description)
  }
  
  createVulnerabilityInitialData.value = {
    title: alert.value.title || '',
    riskLevel: alert.value.riskLevel || alert.value.severity?.toLowerCase() || 'medium',
    status: alert.value.status || 'open',
    owner: alert.value.owner || '',
    actor: alert.value.actor || '',
    description: alertDescription
  }
  
  showCreateVulnerabilityDialog.value = true
}

const closeCreateVulnerabilityDialog = () => {
  showCreateVulnerabilityDialog.value = false
  createVulnerabilityInitialData.value = null
}

const handleVulnerabilityCreated = async () => {
  closeCreateVulnerabilityDialog()
  await loadAlertDetail()
  emit('created')
}

const getAlertCreateTime = () => {
  if (!alert.value) return new Date()
  return (
    parseToDate(alert.value.createTime)
    || parseToDate(alert.value.create_time)
    || new Date()
  )
}

const openEditAlertDialog = () => {
  if (!alert.value) {
    console.warn('Alert data not loaded')
    return
  }
  
  const timestamp = getAlertCreateTime()
  
  editAlertInitialData.value = {
    title: alert.value.title || '',
    riskLevel: alert.value.riskLevel || alert.value.severity || '',
    status: alert.value.status || 'open',
    owner: alert.value.owner || '',
    ruleName: alert.value.ruleName || '',
    createTime: timestamp,
    description: alert.value.description || ''
  }
  
  showEditAlertDialog.value = true
}

const closeEditAlertDialog = () => {
  showEditAlertDialog.value = false
  editAlertInitialData.value = null
}

const handleAlertUpdated = async () => {
  closeEditAlertDialog()
  await loadAlertDetail()
  emit('closed')
}

const handleOpenAlertFromMenu = () => {
  handleOpenAlert()
  showMoreActionsMenu.value = false
}

const handleEditAlertFromMenu = () => {
  openEditAlertDialog()
  showMoreActionsMenu.value = false
}

const handleConvertToVulnerabilityFromMenu = () => {
  openCreateVulnerabilityDialog()
  showMoreActionsMenu.value = false
}

const handlePanelClick = (event) => {
  const dropdown = event.target.closest('.more-actions-dropdown')
  const button = event.target.closest('.more-actions-button')

  if (!dropdown && !button) {
    showMoreActionsMenu.value = false
  }
}

const handleRefresh = async () => {
  if (!currentAlertId.value || isRefreshing.value) {
    return
  }

  isRefreshing.value = true
  try {
    await loadAlertDetail()
  } catch (error) {
    console.error('Failed to refresh alert detail:', error)
  } finally {
    isRefreshing.value = false
  }
}

const handleAddComment = async ({ comment, files }) => {
  if (!currentAlertId.value) {
    toast.error(t('alerts.detail.comments.postError') || '无法提交评论：告警ID不存在', 'ERROR')
    return
  }
  
  const commentText = comment.trim()
  if (!commentText && (!files || files.length === 0)) {
    return
  }
  
  isSubmittingComment.value = true
  
  try {
    await postComment(currentAlertId.value, commentText, files || [], 'asm')
    newComment.value = ''
    await loadAlertDetail(false)
    toast.success(t('alerts.detail.comments.postSuccess') || '评论提交成功', 'SUCCESS')
  } catch (error) {
    console.error('Failed to post comment:', error)
    const errorMessage = error?.response?.data?.message || error?.message || t('alerts.detail.comments.postError') || '评论提交失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
  } finally {
    isSubmittingComment.value = false
  }
}

const canSubmitAiMessage = computed(() => {
  return newAiMessage.value.trim().length > 0 || uploadedAiFiles.value.length > 0
})

const handleAiMessageInput = () => {
}

const handleAiFileSelect = (event) => {
  const files = Array.from(event.target.files || [])
  addAiFiles(files)
  if (aiFileInput.value) {
    aiFileInput.value.value = ''
  }
}

const handleAiDrop = (event) => {
  isAiDragging.value = false
  const files = Array.from(event.dataTransfer.files || [])
  addAiFiles(files)
}

const addAiFiles = (files) => {
  files.forEach(file => {
    if (file.size > 10 * 1024 * 1024) {
      console.warn(`File ${file.name} is too large (max 10MB)`)
      return
    }
    if (!uploadedAiFiles.value.find(f => f.name === file.name && f.size === file.size)) {
      uploadedAiFiles.value.push(file)
    }
  })
}

const removeAiFile = (index) => {
  uploadedAiFiles.value.splice(index, 1)
}

const handleSendAiMessage = () => {
  if (!canSubmitAiMessage.value) return
  
  console.log('Sending AI message:', newAiMessage.value)
  console.log('Files:', uploadedAiFiles.value)
  
  newAiMessage.value = ''
  uploadedAiFiles.value = []
}

const canSubmitRightSidebarAiMessage = computed(() => {
  return rightSidebarAiMessage.value.trim().length > 0 || rightSidebarAiFiles.value.length > 0
})

const handleRightSidebarAiMessageInput = () => {
}

const handleRightSidebarAiFileSelect = (event) => {
  const files = Array.from(event.target.files || [])
  addRightSidebarAiFiles(files)
  if (rightSidebarAiFileInput.value) {
    rightSidebarAiFileInput.value.value = ''
  }
}

const handleRightSidebarAiDrop = (event) => {
  isRightSidebarAiDragging.value = false
  const files = Array.from(event.dataTransfer.files || [])
  addRightSidebarAiFiles(files)
}

const addRightSidebarAiFiles = (files) => {
  files.forEach(file => {
    if (file.size > 10 * 1024 * 1024) {
      console.warn(`File ${file.name} is too large (max 10MB)`)
      return
    }
    if (!rightSidebarAiFiles.value.find(f => f.name === file.name && f.size === file.size)) {
      rightSidebarAiFiles.value.push(file)
    }
  })
}

const removeRightSidebarAiFile = (index) => {
  rightSidebarAiFiles.value.splice(index, 1)
}


const getSeverityClass = (severity) => {
  const classes = {
    fatal: 'bg-red-950/20 text-red-300',
    high: 'bg-red-500/10 text-red-400',
    medium: 'bg-orange-500/10 text-orange-400',
    low: 'bg-blue-500/10 text-blue-400',
    tips: 'bg-gray-500/10 text-gray-400'
  }
  return classes[severity] || classes.medium
}

const getStatusBadgeClass = (status) => {
  const classes = {
    open: 'bg-yellow-400/10 text-yellow-500 ring-yellow-400/20',
    block: 'bg-orange-400/10 text-orange-500 ring-orange-400/20',
    closed: 'bg-gray-400/10 text-gray-500 ring-gray-400/20'
  }
  return classes[status] || classes.open
}

// 检测值是否是URL（http或https开头）
const isUrl = (value) => {
  if (!value || typeof value !== 'string') return false
  const trimmedValue = value.trim()
  return trimmedValue.startsWith('http://') || trimmedValue.startsWith('https://')
}

// 在新标签页打开URL
const openUrlInNewTab = (url) => {
  if (!url || typeof url !== 'string') return
  const trimmedUrl = url.trim()
  if (trimmedUrl.startsWith('http://') || trimmedUrl.startsWith('https://')) {
    window.open(trimmedUrl, '_blank', 'noopener,noreferrer')
  }
}



const getEntityIcon = (type) => {
  const icons = {
    host: 'computer',
    ip: 'public',
    user: 'person'
  }
  return icons[type] || 'help'
}

const isFieldMatchedWithEntity = (key, value) => {
  if (!alert.value?.associatedEntities || !value) {
    return false
  }
  
  const valueStr = String(value).trim()
  if (!valueStr) {
    return false
  }
  
  return alert.value.associatedEntities.some(entity => {
    if (!entity.name) return false
    const entityNameStr = String(entity.name).trim()
    const entityLabelStr = entity.label ? String(entity.label).trim().toLowerCase() : ''
    const keyLower = key.toLowerCase()
    
    if (entityNameStr === valueStr) {
      return true
    }
    
    if (entityLabelStr && (entityLabelStr === keyLower || keyLower.includes(entityLabelStr) || entityLabelStr.includes(keyLower))) {
      if (entityNameStr === valueStr || valueStr.includes(entityNameStr) || entityNameStr.includes(valueStr)) {
        return true
      }
    }
    
    return false
  })
}


const getRiskLevelClass = (level) => {
  const classes = {
    fatal: 'bg-red-950 text-red-200',
    high: 'bg-red-900 text-red-300',
    medium: 'bg-orange-900 text-orange-300',
    low: 'bg-blue-900 text-blue-300',
    tips: 'bg-gray-700 text-gray-300'
  }
  return classes[level] || classes.low
}

const getStatusClass = (status) => {
  const classes = {
    open: 'bg-primary/20 text-primary',
    block: 'bg-yellow-500/20 text-yellow-400',
    closed: 'bg-gray-500/20 text-gray-400'
  }
  return classes[status] || classes.open
}

const getStatusDotClass = (status) => {
  const classes = {
    open: 'bg-primary',
    block: 'bg-yellow-400',
    closed: 'bg-gray-400'
  }
  return classes[status] || classes.open
}

const getAlertUrl = () => {
  const raw = import.meta.env.VITE_WEB_BASE_PATH
  let basePath = '/'
  if (raw && raw !== '/') {
    basePath = raw.startsWith('/') ? raw : `/${raw}`
    basePath = basePath.replace(/\/$/, '')
  }
  const origin = window.location.origin
  const path = basePath === '/' ? '/asm' : `${basePath}/asm`
  return `${origin}${path}/${currentAlertId.value}`
}

const handleOpenAISidebar = () => {
  openAISidebarWithInvestigation()
}

const handleAIOpenInNew = () => {
  if (currentAlertId.value) {
    window.open(getAlertUrl(), '_blank')
  }
}

const handleAISendMessage = (message) => {
  // AI消息发送由AISidebar组件内部处理
}

const handleAIToolAction = (tool) => {
  // 工具操作由AISidebar组件内部处理
}

const handleShare = async () => {
  if (!alert.value) return
  
  const title = alert.value.title || ''
  const url = getAlertUrl()
  const textToCopy = `${title}: ${url}`
  
  try {
    await navigator.clipboard.writeText(textToCopy)
    showShareSuccess.value = true
    setTimeout(() => {
      showShareSuccess.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy to clipboard:', err)
    const textArea = document.createElement('textarea')
    textArea.value = textToCopy
    textArea.style.position = 'fixed'
    textArea.style.opacity = '0'
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      showShareSuccess.value = true
      setTimeout(() => {
        showShareSuccess.value = false
      }, 2000)
    } catch (fallbackErr) {
      console.error('Fallback copy failed:', fallbackErr)
    }
    document.body.removeChild(textArea)
  }
}

// 监听 AI 数据，满足触发条件时自动展开 AI 侧边栏
watch(
  () => alert.value?.ai,
  async (newAi) => {
    if (hasAutoOpenedAiSidebar.value) return
    const investigationContent = findInvestigationContent()
    const hasAnyAi = Array.isArray(newAi) && newAi.length > 0

    // 触发条件：有 investigation 文本，或至少有一条 AI 消息
    if (investigationContent || hasAnyAi) {
      hasAutoOpenedAiSidebar.value = true
      await openAISidebarWithInvestigation()
    }
  },
  { deep: true }
)

// 当 alert 变化时，重置自动展开标记
watch(
  () => alert.value?.id,
  () => {
    hasAutoOpenedAiSidebar.value = false
  }
)

watch(currentAlertId, async (newId, oldId) => {
  if (!newId) {
    visible.value = false
    return
  }
  if (newId === oldId) {
    return
  }
  
  if (visible.value && oldId) {
    visible.value = false
    await new Promise(resolve => setTimeout(resolve, 50))
  }
  
  loadAlertDetail()
}, { immediate: true })


const handleClickOutside = (event) => {
  const dropdown = event.target.closest('.more-actions-dropdown')
  const button = event.target.closest('.more-actions-button')
  if (!dropdown && !button) {
    showMoreActionsMenu.value = false
  }
}

onMounted(() => {
  document.body.style.overflow = 'hidden'
  document.addEventListener('click', handleClickOutside)
  refreshRecentCloseComments()
})

onUnmounted(() => {
  document.body.style.overflow = ''
  document.removeEventListener('click', handleClickOutside)
  hideRecentCloseCommentsDropdown()
})
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease-in-out;
}

.slide-enter-from {
  transform: translateX(100%);
}

.slide-leave-to {
  transform: translateX(100%);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 自定义滚动条样式 */
.custom-scrollbar {
  /* Firefox */
  scrollbar-width: thin;
  scrollbar-color: rgba(59, 130, 246, 0.3) transparent;
}

/* WebKit 浏览器 (Chrome, Safari, Edge) */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(59, 130, 246, 0.3);
  border-radius: 2px;
  transition: background-color 0.2s ease;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(59, 130, 246, 0.5);
}

/* 拖拽区域动画 */
@keyframes dragPulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.drag-active {
  animation: dragPulse 1.5s ease-in-out infinite;
}

.ai-agent__html {
  max-width: 100%;
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
}

.ai-agent__html :deep(pre) {
  background: rgba(226, 232, 240, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.5);
  padding: 12px;
  border-radius: 6px;
  white-space: pre-wrap;
  margin: 10px 0;
  max-width: 100%;
  overflow-x: auto;
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
}

:global(.dark) .ai-agent__html :deep(pre),
.ai-agent__html--dark :deep(pre) {
  background: #111b2e;
  border: 1px solid rgba(94, 114, 164, 0.45);
  color: #f1f5f9;
  box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.4);
}

.ai-agent__html :deep(code) {
  font-family: 'Fira Code', 'Source Code Pro', monospace;
  font-size: 13px;
  color: #0f172a;
}

:global(.dark) .ai-agent__html :deep(code),
.ai-agent__html--dark :deep(code) {
  color: #f1f5f9;
  background: transparent;
  padding: 0;
  border: none;
}

.ai-agent__html :deep(b) {
  color: #0f172a;
}

:global(.dark) .ai-agent__html :deep(b),
.ai-agent__html--dark :deep(b) {
  color: #e2e8f0;
}

/* Details element styles for Automated Response */
details > summary {
  list-style: none;
}

details > summary::-webkit-details-marker {
  display: none;
}

details > summary .marker {
  transition: transform 0.2s ease-in-out;
}

details[open] > summary .marker {
  transform: rotate(90deg);
}

</style>

