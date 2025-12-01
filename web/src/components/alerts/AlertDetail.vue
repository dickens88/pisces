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
      
      <!-- Detail panel - with slide-in animation -->
      <Transition name="slide" appear>
        <div
          v-if="visible"
          :class="[
            rightSidebarTab === 'securityAgent' ? 'w-[80vw]' : 'w-[70vw]',
            'relative h-full bg-white dark:bg-panel-dark shadow-2xl flex flex-col overflow-hidden'
          ]"
          @click.stop="handlePanelClick"
        >
          <!-- Header -->
          <div class="sticky top-0 z-20 bg-white/80 dark:bg-panel-dark/80 backdrop-blur-sm border-b border-gray-200 dark:border-border-dark">
            <div class="flex items-center justify-between px-6 py-4">
              <h2 class="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <span class="material-symbols-outlined text-base">security</span>
                {{ $t('alerts.detail.title') }}
              </h2>
              <div class="flex items-center gap-2">
                <button
                  @click="openBatchCloseDialog"
                  :disabled="!canCloseAlert"
                  class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-200 dark:disabled:hover:bg-[#2a3546]"
                >
                  <span class="material-symbols-outlined text-base">archive</span>
                  {{ $t('alerts.detail.closeAlert') }}
                </button>
                <!-- More actions dropdown menu -->
                <div class="relative">
                  <button
                    @click.stop="showMoreActionsMenu = !showMoreActionsMenu"
                    class="more-actions-button bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center gap-2"
                  >
                    <span class="material-symbols-outlined text-base">more_vert</span>
                    {{ $t('alerts.detail.moreActions') }}
                    <span class="material-symbols-outlined text-base">arrow_drop_down</span>
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
                      {{ $t('alerts.detail.openAlert') }}
                    </button>
                    <button
                      @click="handleEditAlertFromMenu"
                      class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867]"
                    >
                      <span class="material-symbols-outlined text-base">edit</span>
                      {{ $t('alerts.detail.editAlert') }}
                    </button>
                    <button
                      @click="handleConvertToIncidentFromMenu"
                      class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867]"
                    >
                      <span class="material-symbols-outlined text-base">shield</span>
                      {{ $t('alerts.detail.convertToIncident') }}
                    </button>
                    <button
                      @click="handleAssociateIncidentFromMenu"
                      class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867]"
                    >
                      <span class="material-symbols-outlined text-base">link</span>
                      {{ $t('alerts.list.associateIncident') }}
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
                  @click="handleShare"
                  class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center"
                  :title="$t('alerts.detail.share') || 'Share'"
                >
                  <span class="material-symbols-outlined text-base">share</span>
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
                            v-if="isFieldMatchedWithEntity(key, value)"
                            @click="handleSendFieldToSecurityAgent(key, value)"
                            class="inline-flex items-center justify-center shrink-0 cursor-pointer transition-all duration-200 hover:brightness-125 hover:scale-110"
                            :title="$t('alerts.detail.aiAssistant')"
                          >
                            <img 
                              src="/ai-chat.png" 
                              :alt="$t('alerts.detail.aiAssistant')" 
                              class="w-4 h-4"
                            />
                          </button>
                        </div>
                      </div>
                    </template>
                  </template>
                  <!-- 如果 description 不是对象（字符串、数字、布尔值等），直接显示 -->
                  <div v-else-if="alert?.description !== null && alert?.description !== undefined" class="flex items-baseline">
                    <p class="w-40 shrink-0 font-bold text-gray-900 dark:text-[#f5f5f5]">{{ $t('alerts.detail.description') || '描述' }}:</p>
                    <p class="font-medium text-gray-900 dark:text-[#f5f5f5] break-all">{{ alert.description }}</p>
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

              <!-- Associated alerts tab -->
              <div v-if="activeTab === 'associatedAlerts'">

                <div v-if="loadingAssociatedAlerts" class="flex items-center justify-center py-12">
                  <div class="text-gray-600 dark:text-text-light text-sm">加载中...</div>
                </div>
                
                <div v-else-if="associatedAlerts.length === 0" class="text-gray-600 dark:text-text-light text-sm py-12 text-center">
                  {{ $t('alerts.detail.noAssociatedAlerts') }}
                </div>
                
                <div v-else class="grid grid-cols-1 @lg:grid-cols-2 gap-4">
                  <AlertInfoCard
                    v-for="associatedAlert in associatedAlerts"
                    :key="associatedAlert.id"
                    :title="associatedAlert.title"
                    :header-meta="associatedAlert.displayCreateTime"
                    :html-content="associatedAlert.content || ''"
                    :summary="associatedAlert.summary"
                    :owner="associatedAlert.owner"
                  />
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
              :class="[
                rightSidebarTab === 'securityAgent' ? 'w-[32rem]' : 'w-80',
                'border-l border-gray-200 dark:border-border-dark bg-gray-50 dark:bg-[#1f2937]/20 flex flex-col overflow-hidden'
              ]"
            >
              <!-- 页签导航 -->
              <div class="border-b border-border-dark pb-4 mb-4 flex-shrink-0 px-6 pt-6">
                <nav class="flex -mb-px space-x-4">
                  <button
                    @click="rightSidebarTab = 'response'"
                    :class="[
                      'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm transition-colors',
                      rightSidebarTab === 'response'
                        ? 'text-primary border-primary'
                        : 'text-gray-500 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white border-transparent'
                    ]"
                  >
                    {{ $t('alerts.detail.responseTab') }}
                  </button>
                  <button
                    @click="rightSidebarTab = 'securityAgent'"
                    :class="[
                      'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm transition-colors',
                      rightSidebarTab === 'securityAgent'
                        ? 'text-primary border-primary'
                        : 'text-gray-500 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white border-transparent'
                    ]"
                  >
                    {{ $t('alerts.detail.securityAgentTab') }}
                  </button>
                </nav>
              </div>

              <!-- Response 页签内容 -->
              <div v-if="rightSidebarTab === 'response'" class="overflow-y-auto custom-scrollbar flex-1 pl-6 pb-6">
                <div class="pr-6 space-y-6">
                <!-- 自动化响应 -->
                <div class="space-y-4">
                  <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ $t('alerts.detail.automatedResponse') }}</h3>
                  
                  <!-- 加载状态 -->
                  <div v-if="loadingToolkits || loadingToolkitRecords" class="flex items-center justify-center py-8">
                    <span class="material-symbols-outlined animate-spin text-primary text-2xl">refresh</span>
                  </div>
                  
                  <div v-else class="space-y-4">
                    <!-- 工具清单部分：显示所有可用工具 -->
                    <div v-if="toolkits.length" class="space-y-2">
                      <h4 class="text-sm font-medium text-gray-600 dark:text-text-light">{{ $t('alerts.detail.availableTools') }}</h4>
                      <template v-for="tool in toolkits" :key="tool.app_id">
                        <details class="group rounded-lg bg-gray-100 dark:bg-[#2a3546]">
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
                              </label>
                              <input 
                                class="w-full rounded-md border border-gray-300 dark:border-border-dark bg-white dark:bg-[#1a202c] p-2 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-text-dark focus:border-primary focus:ring-primary text-sm" 
                                :id="`toolkit-${tool.app_id}-${param.name}`"
                                :placeholder="`e.g., ${param.label}`"
                                type="text" 
                                :value="toolkitParams[tool.app_id]?.[param.name] || ''"
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

                <!-- 关联实体 -->
                <div class="space-y-4" v-if="alert?.associatedEntities">
                  <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ $t('alerts.detail.associatedEntities') }}</h3>
                  <div class="space-y-3">
                    <div
                      v-for="(entity, index) in alert.associatedEntities"
                      :key="index"
                      @click="handleSendEntityToSecurityAgent(entity)"
                      class="flex items-center gap-3 p-3 rounded-lg bg-gray-100 dark:bg-[#2a3546] hover:bg-gray-200 dark:hover:bg-[#3c4a60] cursor-pointer transition-colors border border-gray-200 dark:border-transparent"
                    >
                      <span class="material-symbols-outlined text-primary">
                        {{ getEntityIcon(entity.type) }}
                      </span>
                      <div class="text-sm flex-1 min-w-0">
                        <p class="font-medium text-gray-900 dark:text-white truncate">{{ entity.name }}</p>
                        <p class="text-gray-600 dark:text-text-light truncate">{{ entity.label }}</p>
                      </div>
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

              <!-- Security Agent 页签内容 -->
              <div v-if="rightSidebarTab === 'securityAgent'" class="flex flex-col flex-1 min-h-0 min-w-0 pl-6 pb-6 pr-6">
                
                <!-- Security Agent 聊天组件 -->
                <div class="flex-1 min-h-0 min-w-0">
                  <SecurityAgentChat
                    ref="securityAgentChatRef"
                    :messages="securityAgentMessages"
                    :auto-scroll="true"
                    :disabled="isSendingSecurityAgentMessage"
                    :loading="isSendingSecurityAgentMessage"
                    @send="handleRightSidebarAiSend"
                  />
                </div>
              </div>
            </aside>
          </div>
        </div>
      </Transition>
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

    <!-- 创建事件对话框 -->
    <CreateIncidentDialog
      :visible="showCreateIncidentDialog"
      :initial-data="createIncidentInitialData"
      :alert-ids="currentAlertId ? [currentAlertId] : []"
      @close="closeCreateIncidentDialog"
      @created="handleIncidentCreated"
    />

    <!-- 编辑告警对话框 -->
    <EditAlertDialog
      :visible="showEditAlertDialog"
      :alert-id="currentAlertId"
      :initial-data="editAlertInitialData"
      @close="closeEditAlertDialog"
      @updated="handleAlertUpdated"
    />

    <!-- 关联事件对话框 -->
    <AssociateIncidentDialog
      :visible="showAssociateIncidentDialog"
      :alert-ids="[currentAlertId]"
      @close="closeAssociateIncidentDialog"
      @associated="handleAssociateIncidentSuccess"
    />

    <!-- 创建漏洞对话框 -->
    <CreateVulnerabilityDialog
      :visible="showCreateVulnerabilityDialog"
      :initial-data="createVulnerabilityInitialData"
      :alert-ids="currentAlertId ? [currentAlertId] : []"
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { getAlertDetail, batchCloseAlerts, openAlert, closeAlert } from '@/api/alerts'
import { postComment } from '@/api/comments'
import { getToolkits, getToolkitRecords, executeToolkit } from '@/api/toolkits'
import CreateIncidentDialog from '@/components/incidents/CreateIncidentDialog.vue'
import EditAlertDialog from '@/components/alerts/EditAlertDialog.vue'
import AssociateIncidentDialog from '@/components/alerts/AssociateIncidentDialog.vue'
import CreateVulnerabilityDialog from '@/components/vulnerabilities/CreateVulnerabilityDialog.vue'
import AlertInfoCard from '@/components/alerts/AlertInfoCard.vue'
import AiChatDialog from '@/components/alerts/AiChatDialog.vue'
import SecurityAgentChat from '@/components/alerts/SecurityAgentChat.vue'
import { sendSecurityAgentMessage } from '@/api/securityAgent'
import { formatDateTime, calculateTTR, parseToDate } from '@/utils/dateTime'
import DOMPurify from 'dompurify'
import UserAvatar from '@/components/common/UserAvatar.vue'
import CommentInput from '@/components/common/CommentInput.vue'
import CommentSection from '@/components/common/CommentSection.vue'
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
// 右侧侧边栏页签
const rightSidebarTab = ref('response')
// 右侧侧边栏AI问答相关（独立于主内容区域的AI问答）
const rightSidebarAiMessage = ref('')
const rightSidebarAiFiles = ref([])
const rightSidebarAiFileInput = ref(null)
const isRightSidebarAiDragging = ref(false)
const isSendingSecurityAgentMessage = ref(false)
const securityAgentMessages = ref([])
const securityAgentChatRef = ref(null)
const conversationId = ref(null)
const showBatchCloseDialog = ref(false)
const isClosing = ref(false)
const closeConclusion = ref({
  category: '',
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
const showCreateIncidentDialog = ref(false)
const createIncidentInitialData = ref(null)
const showEditAlertDialog = ref(false)
const editAlertInitialData = ref(null)
const showShareSuccess = ref(false)
const associatedAlerts = ref([])
const loadingAssociatedAlerts = ref(false)
const showAssociateIncidentDialog = ref(false)
const showMoreActionsMenu = ref(false)
const isRefreshing = ref(false)
const showCreateVulnerabilityDialog = ref(false)
const createVulnerabilityInitialData = ref(null)
const isSubmittingComment = ref(false)

// Toolkit related state
const toolkits = ref([])
const toolkitRecords = ref([])
const loadingToolkits = ref(false)
const loadingToolkitRecords = ref(false)
const executingToolkitId = ref(null) // 正在执行的工具ID
const toolkitParams = ref({}) // 存储每个工具的输入参数 { app_id: { param_name: value } }

const tabs = [
  { key: 'overview', label: 'alerts.detail.overview' },
  { key: 'associatedAlerts', label: 'alerts.detail.associatedAlerts' },
  { key: 'threatIntelligence', label: 'alerts.detail.threatIntelligence' },
  { key: 'aiAgent', label: 'alerts.detail.aiAgent' }
]

const getTabCount = (tabKey) => {
  if (!alert.value) return 0
  
  switch (tabKey) {
    case 'overview':
      return alert.value.comments?.length || 0
    case 'associatedAlerts':
      return associatedAlerts.value?.length || 0
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

const transformHistoricEntries = (entries = [], baseAlertId) => {
  return entries.map((item, index) => {
    const titleFromContent = extractFirstBoldText(item.content)
    const fallbackTitle = titleFromContent || `Historical Reference ${index + 1}`
    const plainSummary = stripHtmlTags(item.content)
    let formattedTime = ''
    if (item.create_time) {
      try {
        formattedTime = formatDateTime(item.create_time)
      } catch (error) {
        formattedTime = item.create_time
      }
    }

    return {
      id: item.id || `${baseAlertId || 'alert'}-historic-${index}`,
      title: fallbackTitle,
      owner: item.author || '',
      content: item.content || '',
      summary: plainSummary,
      rawCreateTime: item.create_time || '',
      displayCreateTime: formattedTime
    }
  })
}

const transformAssociatedAlertsResponse = (data = []) => {
  return data.map((item, index) => {
    const rawTime = item.create_time || item.createTime || ''

    return {
      id: item.id || item.alert_id || `associated-${index}`,
      title: item.title || item.subject || `Associated Alert ${index + 1}`,
      owner: item.owner || item.author || '',
      content: item.content || '',
      summary: item.description || '',
      rawCreateTime: rawTime,
      displayCreateTime: rawTime
    }
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

const loadAlertDetail = async (showLoading = true) => {
  if (!currentAlertId.value) return
  
  if (showLoading) {
    alert.value = null
    isLoading.value = true
  }
  conversationId.value = null
  
  visible.value = true
  await new Promise(resolve => setTimeout(resolve, 50))
  
  try {
    const response = await getAlertDetail(currentAlertId.value)
    alert.value = transformAlertDetailData(response.data)
    securityAgentMessages.value = []
    loadAssociatedAlerts()
    loadToolkits()
    loadToolkitRecords()
  } catch (error) {
    console.error('Failed to load alert detail:', error)
    emit('close')
  } finally {
    if (showLoading) {
      isLoading.value = false
    }
  }
}

const loadAssociatedAlerts = async () => {
  if (!currentAlertId.value) return

  loadingAssociatedAlerts.value = true
  try {
    if (alert.value?.historic?.length) {
      const data = transformHistoricEntries(alert.value.historic, alert.value?.id)
      associatedAlerts.value = data
    } else {
      associatedAlerts.value = []
    }
  } catch (error) {
    console.error('Failed to load associated alerts:', error)
    associatedAlerts.value = []
  } finally {
    loadingAssociatedAlerts.value = false
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
  if (!currentAlertId.value) return

  loadingToolkitRecords.value = true
  try {
    const response = await getToolkitRecords(currentAlertId.value)
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
  if (!currentAlertId.value) {
    toast.error(t('alerts.detail.alertIdRequired') || '告警ID不存在')
    return
  }

  const params = toolkitParams.value[tool.app_id] || {}
  const requiredParams = tool.params || []
  const missingParams = requiredParams.filter(p => !params[p.name] || params[p.name].trim() === '')
  
  if (missingParams.length > 0) {
    toast.error(t('alerts.detail.toolkitParamsRequired') || `请填写参数: ${missingParams.map(p => p.label).join(', ')}`)
    return
  }

  executingToolkitId.value = tool.app_id

  try {
    const requestData = {
      title: tool.title,
      app_id: tool.app_id,
      app_type: tool.app_type,
      params: params
    }

    await executeToolkit(currentAlertId.value, requestData)
    toast.success(t('alerts.detail.toolkitExecuteSuccess') || '工具执行成功')
    await loadToolkitRecords()
  } catch (error) {
    console.error('Failed to execute toolkit:', error)
    toast.error(error?.response?.data?.error_message || error?.message || t('alerts.detail.toolkitExecuteError') || '工具执行失败')
  } finally {
    executingToolkitId.value = null
  }
}

const updateToolkitParam = (appId, paramName, value) => {
  if (!toolkitParams.value[appId]) {
    toolkitParams.value[appId] = {}
  }
  toolkitParams.value[appId][paramName] = value
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
  conversationId.value = null
  
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
    category: '',
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
    await closeAlert(currentAlertId.value, {
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
    await openAlert(currentAlertId.value)
    await loadAlertDetail()
    emit('closed')
  } catch (error) {
    console.error('Failed to open alert:', error)
  }
}

const openCreateIncidentDialog = () => {
  if (!alert.value) {
    console.warn('Alert data not loaded')
    return
  }
  
  const createTime = getAlertCreateTime()
  const alertDescription = alert.value.aiAnalysis?.description || alert.value.description || ''
  
  createIncidentInitialData.value = {
    title: alert.value.title || '',
    createTime,
    description: alertDescription
  }
  
  showCreateIncidentDialog.value = true
}

const closeCreateIncidentDialog = () => {
  showCreateIncidentDialog.value = false
  createIncidentInitialData.value = null
}

const handleIncidentCreated = () => {
  closeCreateIncidentDialog()
  emit('created')
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

const handleVulnerabilityCreated = () => {
  closeCreateVulnerabilityDialog()
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

const openAssociateIncidentDialog = () => {
  if (!currentAlertId.value) {
    console.warn('No alert ID available')
    return
  }
  showAssociateIncidentDialog.value = true
}

const handleOpenAlertFromMenu = () => {
  handleOpenAlert()
  showMoreActionsMenu.value = false
}

const handleEditAlertFromMenu = () => {
  openEditAlertDialog()
  showMoreActionsMenu.value = false
}

const handleConvertToIncidentFromMenu = () => {
  openCreateIncidentDialog()
  showMoreActionsMenu.value = false
}

const handleAssociateIncidentFromMenu = () => {
  openAssociateIncidentDialog()
  showMoreActionsMenu.value = false
}

const handleConvertToVulnerabilityFromMenu = () => {
  openCreateVulnerabilityDialog()
  showMoreActionsMenu.value = false
}

const closeAssociateIncidentDialog = () => {
  showAssociateIncidentDialog.value = false
}

const handlePanelClick = (event) => {
  const dropdown = event.target.closest('.more-actions-dropdown')
  const button = event.target.closest('.more-actions-button')

  if (!dropdown && !button) {
    showMoreActionsMenu.value = false
  }
}

const handleAssociateIncidentSuccess = async () => {
  closeAssociateIncidentDialog()
  await loadAlertDetail()
  emit('closed')
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
    await postComment(currentAlertId.value, commentText, files || [])
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

const getSecurityAgentUserLabel = () => t('alerts.detail.securityAgentUserLabel') || 'You'
const getSecurityAgentAssistantLabel = () =>
  t('alerts.detail.securityAgentAssistantLabel') ||
  t('alerts.detail.securityAgentTab') ||
  'Security Agent'

const formatSecurityAgentContent = (text = '') => {
  if (!text || typeof text !== 'string') return ''
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br />')
}

const generateSecurityAgentMessageId = () =>
  `security-agent-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`

const appendSecurityAgentMessage = (message) => {
  if (!message) return null
  const rawContent = message.content || ''
  const normalizedMessage = {
    id: message.id || generateSecurityAgentMessageId(),
    author: message.author || getSecurityAgentAssistantLabel(),
    rawContent,
    content: formatSecurityAgentContent(rawContent),
    create_time: message.create_time || new Date().toISOString(),
    role: message.role || 'assistant',
    isLocal: message.isLocal || false,
    // 执行节点信息（由 streaming 事件 node_started / node_finished 填充）
    nodes: Array.isArray(message.nodes) ? [...message.nodes] : []
  }
  securityAgentMessages.value = [...securityAgentMessages.value, normalizedMessage]
  return normalizedMessage.id
}

// 根据 node_started / node_finished 事件更新某条消息上的节点状态
const updateSecurityAgentMessageNodes = (messageId, nodeTitle, status) => {
  if (!messageId || !nodeTitle || !status) return
  securityAgentMessages.value = securityAgentMessages.value.map(message => {
    if (message.id !== messageId) return message

    const nodes = Array.isArray(message.nodes) ? [...message.nodes] : []
    const existingIndex = nodes.findIndex(
      n => n.title === nodeTitle || n.name === nodeTitle || n?.data?.title === nodeTitle
    )

    if (existingIndex === -1) {
      nodes.push({
        title: nodeTitle,
        status
      })
    } else {
      nodes[existingIndex] = {
        ...nodes[existingIndex],
        title: nodes[existingIndex].title || nodeTitle,
        status
      }
    }

    return {
      ...message,
      nodes
    }
  })
}

const setSecurityAgentMessageContent = (messageId, text) => {
  if (!messageId) return
  securityAgentMessages.value = securityAgentMessages.value.map(message => {
    if (message.id !== messageId) return message
    const newRawContent = text || ''
    return {
      ...message,
      rawContent: newRawContent,
      content: formatSecurityAgentContent(newRawContent)
    }
  })
}

const appendToSecurityAgentMessage = (messageId, chunk) => {
  if (!messageId || !chunk) return
  securityAgentMessages.value = securityAgentMessages.value.map(message => {
    if (message.id !== messageId) return message
    const newRawContent = (message.rawContent || '') + chunk
    return {
      ...message,
      rawContent: newRawContent,
      content: formatSecurityAgentContent(newRawContent)
    }
  })
}

const handleRightSidebarAiSend = async (data) => {
  if (!alert.value?.id) {
    const missingAlertMsg = t('alerts.detail.securityAgentSendError') || 'Unable to send message: missing alert context'
    toast.error(missingAlertMsg, 'ERROR')
    return
  }

  if (!data || (!data.message && (!data.files || data.files.length === 0))) {
    return
  }

  if (isSendingSecurityAgentMessage.value) {
    return
  }

  const sanitizedUserMessage = (data.message || '').trim()
  const payload = {
    alertId: alert.value.id,
    message: sanitizedUserMessage,
    files: data.files,
    conversationId: conversationId.value
  }

  if (sanitizedUserMessage) {
    appendSecurityAgentMessage({
      author: getSecurityAgentUserLabel(),
      content: sanitizedUserMessage,
      role: 'user',
      isLocal: true
    })
  }

  let assistantMessageId = null

  try {
    isSendingSecurityAgentMessage.value = true
    assistantMessageId = appendSecurityAgentMessage({
      author: getSecurityAgentAssistantLabel(),
      content: '',
      role: 'assistant',
      isLocal: true
    })

    await sendSecurityAgentMessage({
      ...payload,
      onEvent: (event) => {
        const receivedConversationId = event?.conversation_id || event?.conversationId
        if (receivedConversationId) {
          conversationId.value = receivedConversationId
        }
        if (!event) return
        const eventType = event.event || event.type
        if (eventType === 'message' || eventType === 'message_end') {
          // 追加消息内容，实现真正的前端流式渲染
          if (assistantMessageId && typeof event.answer === 'string') {
            appendToSecurityAgentMessage(assistantMessageId, event.answer)
          }
        } else if (eventType === 'node_started' || eventType === 'node_finished') {
          // 处理节点执行状态，填充到当前 assistant 消息上
          const nodeData = event.data || {}
          const nodeTitle =
            nodeData.title ||
            nodeData.name ||
            (typeof nodeData === 'string' ? nodeData : '') ||
            ''
          if (assistantMessageId && nodeTitle) {
            const status = eventType === 'node_started' ? 'running' : 'finished'
            updateSecurityAgentMessageNodes(assistantMessageId, nodeTitle, status)
          }
        } else if (eventType === 'error') {
          const streamError = event?.message || t('alerts.detail.securityAgentSendError') || 'Failed to send message to Security Agent'
          toast.error(streamError, 'ERROR')
          if (assistantMessageId) {
            setSecurityAgentMessageContent(assistantMessageId, streamError)
          } else {
            appendSecurityAgentMessage({
              author: getSecurityAgentAssistantLabel(),
              content: streamError,
              role: 'assistant',
              isLocal: true
            })
          }
        }
      }
    })
  } catch (error) {
    const rawMessage = error?.message || ''
    const errorMsg = rawMessage.includes('VITE_AI_CHAT_API') || rawMessage.toLowerCase().includes('not configured')
      ? t('alerts.detail.securityAgentMissingConfig') || 'Security Agent endpoint is not configured. Please set VITE_AI_CHAT_API.'
      : rawMessage || t('alerts.detail.securityAgentSendError') || 'Failed to send message to Security Agent'
    toast.error(errorMsg, 'ERROR')
    if (assistantMessageId) {
      setSecurityAgentMessageContent(assistantMessageId, errorMsg)
    } else {
      appendSecurityAgentMessage({
        author: getSecurityAgentAssistantLabel(),
        content: errorMsg,
        role: 'assistant',
        isLocal: true
      })
    }
  } finally {
    isSendingSecurityAgentMessage.value = false
  }
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

const handleSendFieldToSecurityAgent = (key, value) => {
  if (!alert.value) {
    return
  }
  
  rightSidebarTab.value = 'securityAgent'
  
  const valueStr = typeof value === 'object' && value !== null 
    ? JSON.stringify(value) 
    : String(value)
  const message = `${key}: ${valueStr}`
  
  setTimeout(() => {
    if (securityAgentChatRef.value && securityAgentChatRef.value.setMessage) {
      securityAgentChatRef.value.setMessage(message)
    }
  }, 100)
}

const handleSendEntityToSecurityAgent = (entity) => {
  if (!alert.value || !entity) {
    return
  }
  
  rightSidebarTab.value = 'securityAgent'
  
  const from = entity.from || entity.label || ''
  const name = entity.name || ''
  const message = `${from}: ${name}`
  
  setTimeout(() => {
    if (securityAgentChatRef.value && securityAgentChatRef.value.setMessage) {
      securityAgentChatRef.value.setMessage(message)
    }
  }, 100)
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
  const path = basePath === '/' ? '/alerts' : `${basePath}/alerts`
  return `${origin}${path}/${currentAlertId.value}`
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

watch(activeTab, (newTab) => {
  if (newTab === 'associatedAlerts' && associatedAlerts.value.length === 0 && !loadingAssociatedAlerts.value) {
    loadAssociatedAlerts()
  }
})

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
  conversationId.value = null
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

