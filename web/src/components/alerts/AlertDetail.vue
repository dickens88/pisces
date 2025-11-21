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
            'relative h-full bg-panel-dark shadow-2xl flex flex-col overflow-hidden'
          ]"
          @click.stop="handlePanelClick"
        >
          <!-- Header -->
          <div class="sticky top-0 z-20 bg-panel-dark/80 backdrop-blur-sm border-b border-border-dark">
            <div class="flex items-center justify-between px-6 py-4">
              <h2 class="text-xl font-bold text-white flex items-center gap-2">
                <span class="material-symbols-outlined text-base">security</span>
                {{ $t('alerts.detail.title') }}
              </h2>
              <div class="flex items-center gap-2">
                <button
                  @click="openBatchCloseDialog"
                  :disabled="!canCloseAlert"
                  class="bg-[#2a3546] hover:bg-[#3c4a60] text-sm font-medium text-white px-4 py-2 rounded-md transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-[#2a3546]"
                >
                  <span class="material-symbols-outlined text-base">archive</span>
                  {{ $t('alerts.detail.closeAlert') }}
                </button>
                <!-- More actions dropdown menu -->
                <div class="relative">
                  <button
                    @click.stop="showMoreActionsMenu = !showMoreActionsMenu"
                    class="more-actions-button bg-[#2a3546] hover:bg-[#3c4a60] text-sm font-medium text-white px-4 py-2 rounded-md transition-colors flex items-center gap-2"
                  >
                    <span class="material-symbols-outlined text-base">more_vert</span>
                    {{ $t('alerts.detail.moreActions') }}
                    <span class="material-symbols-outlined text-base">arrow_drop_down</span>
                  </button>
                  <!-- Dropdown menu -->
                  <div
                    v-if="showMoreActionsMenu"
                    @click.stop
                    class="more-actions-dropdown absolute right-0 top-full mt-2 bg-[#233348] border border-[#324867] rounded-lg shadow-lg z-50 min-w-[180px]"
                  >
                    <button
                      @click="handleOpenAlertFromMenu"
                      :disabled="!canOpenAlert"
                      class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed text-white hover:bg-[#324867] disabled:hover:bg-transparent"
                    >
                      <span class="material-symbols-outlined text-base">unarchive</span>
                      {{ $t('alerts.detail.openAlert') }}
                    </button>
                    <button
                      @click="handleEditAlertFromMenu"
                      class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-white hover:bg-[#324867]"
                    >
                      <span class="material-symbols-outlined text-base">edit</span>
                      {{ $t('alerts.detail.editAlert') }}
                    </button>
                    <button
                      @click="handleConvertToIncidentFromMenu"
                      class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-white hover:bg-[#324867]"
                    >
                      <span class="material-symbols-outlined text-base">shield</span>
                      {{ $t('alerts.detail.convertToIncident') }}
                    </button>
                    <button
                      @click="handleAssociateIncidentFromMenu"
                      class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-white hover:bg-[#324867]"
                    >
                      <span class="material-symbols-outlined text-base">link</span>
                      {{ $t('alerts.list.associateIncident') }}
                    </button>
                    <button
                      @click="handleConvertToVulnerabilityFromMenu"
                      class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-white hover:bg-[#324867]"
                    >
                      <span class="material-symbols-outlined text-base">bug_report</span>
                      {{ $t('alerts.detail.convertToVulnerability') }}
                    </button>
                  </div>
                </div>
                <button
                  @click="handleRefresh"
                  :disabled="isRefreshing"
                  class="bg-[#2a3546] hover:bg-[#3c4a60] text-sm font-medium text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-[#2a3546]"
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
                  class="bg-[#2a3546] hover:bg-[#3c4a60] text-sm font-medium text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center"
                  :title="$t('alerts.detail.share') || 'Share'"
                >
                  <span class="material-symbols-outlined text-base">share</span>
                </button>
                <button
                  @click="handleClose"
                  class="p-2 text-text-light hover:text-white transition-colors"
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
              <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-[#111822]/90 z-10">
                <div class="flex flex-col items-center gap-4">
                  <div class="relative w-20 h-20">
                    <div class="absolute inset-0 border-4 border-primary/30 rounded-full"></div>
                    <div class="absolute inset-0 border-4 border-transparent border-t-primary border-r-primary/50 rounded-full animate-spin"></div>
                  </div>
                  <p class="text-white text-sm font-medium">{{ $t('common.loading') || '加载中...' }}</p>
                </div>
              </div>
            </Transition>
            
            <!-- Content -->
            <main v-if="!isLoading && alert" class="flex-1 p-6 space-y-8 overflow-y-auto custom-scrollbar">
              <!-- Title and severity -->
              <div>
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
                <h1 class="mt-2 text-xl font-bold text-white">{{ alert.title }}</h1>
                <div class="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-text-light">
                  <div class="flex items-center gap-1.5">
                    <span class="font-semibold text-white mr-1">{{ $t('alerts.detail.status') }}:</span>
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
                    <span class="font-semibold text-white mr-1">{{ $t('alerts.detail.actor') }}:</span>
                    <span class="font-mono text-white">{{ alert.actor || '-' }}</span>
                  </div>
                  <div class="h-4 w-px bg-border-dark/50"></div>
                  <div class="flex items-center gap-1.5">
                    <span class="font-semibold text-white mr-1">{{ $t('alerts.detail.created') }}:</span>
                    <span class="text-white">{{ formatDateTime(alert.timestamp || alert.createTime) }}</span>
                  </div>
                  <div class="h-4 w-px bg-border-dark/50"></div>
                  <div class="flex items-center gap-1.5">
                    <span class="font-semibold text-white mr-1">{{ $t('alerts.detail.responseTime') }}:</span>
                    <span class="text-white">{{ alert.responseTime || '2m 15s' }}</span>
                  </div>
                </div>
              </div>

              <!-- Tabs -->
              <div class="border-b border-border-dark">
                <nav aria-label="Tabs" class="-mb-px flex space-x-6">
                  <button
                    v-for="tab in tabs"
                    :key="tab.key"
                    @click="activeTab = tab.key"
                    :class="[
                      'shrink-0 border-b-2 px-1 pb-3 text-sm font-medium transition-colors flex items-center gap-2',
                      activeTab === tab.key
                        ? 'border-primary text-primary font-semibold'
                        : 'border-transparent text-text-light hover:border-text-dark hover:text-white'
                    ]"
                  >
                    <span>{{ $t(tab.label) }}</span>
                    <span 
                      v-if="getTabCount(tab.key) > 0" 
                      :class="[
                        'inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 text-xs font-medium rounded-full',
                        activeTab === tab.key
                          ? 'bg-primary/20 text-primary'
                          : 'bg-[#2a3546] text-text-light'
                      ]"
                    >
                      {{ getTabCount(tab.key) }}
                    </span>
                  </button>
                </nav>
              </div>

              <!-- Tab content -->
              <div v-if="activeTab === 'overview'">
                <h3 class="text-lg font-semibold mb-3 text-white">{{ $t('alerts.detail.alertInfo') }}</h3>
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
                        class="flex items-baseline"
                      >
                        <p class="text-text-light w-40 shrink-0">{{ key }}:</p>
                        <p class="font-medium text-white break-all">
                          <span v-if="typeof value === 'object' && value !== null">{{ JSON.stringify(value) }}</span>
                          <span v-else>{{ value }}</span>
                        </p>
                      </div>
                    </template>
                  </template>
                  <!-- 如果 description 不是对象（字符串、数字、布尔值等），直接显示 -->
                  <div v-else-if="alert?.description !== null && alert?.description !== undefined" class="flex items-baseline">
                    <p class="text-text-light w-40 shrink-0">{{ $t('alerts.detail.description') || '描述' }}:</p>
                    <p class="font-medium text-white break-all">{{ alert.description }}</p>
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
                    @submit="handleAddComment"
                  />
                  
                  <!-- 分割线 -->
                  <div class="mt-6 border-t border-border-dark"></div>
                </div>
              </div>

              <!-- Associated alerts tab -->
              <div v-if="activeTab === 'associatedAlerts'">

                <div v-if="loadingAssociatedAlerts" class="flex items-center justify-center py-12">
                  <div class="text-text-light text-sm">加载中...</div>
                </div>
                
                <div v-else-if="associatedAlerts.length === 0" class="text-text-light text-sm py-12 text-center">
                  {{ $t('alerts.detail.noAssociatedAlerts') || '暂无关联告警' }}
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
                  {{ $t('alerts.detail.noThreatIntelligence') || '暂无威胁情报匹配' }}
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
                <h3 class="text-lg font-semibold mb-4 text-white">{{ $t('alerts.detail.aiAgent') }}</h3>
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
                      <span class="material-symbols-outlined text-white text-sm">smart_toy</span>
                    </div>
                    <div class="flex-1">
                      <div class="flex items-baseline gap-2">
                        <p class="font-semibold text-white">{{ aiItem.author || 'AI Agent' }}</p>
                        <p class="text-xs text-text-light">{{ formatDateTime(aiItem.create_time || aiItem.time) }}</p>
                      </div>
                      <div class="mt-1 text-sm text-[#c3d3e8] bg-[#2a3546] p-3 rounded-lg rounded-tl-none ai-agent__html" v-html="sanitizeHtml(aiItem.content || '')">
                      </div>
                    </div>
                  </div>
                  
                  <!-- If no AI data, show prompt -->
                  <div v-if="!alert?.ai || alert.ai.length === 0" class="text-text-light text-sm">
                    {{ $t('alerts.detail.noAiResponse') || '暂无AI分析结果' }}
                  </div>
                </div>
                
              </div>
            </main>
            
            <!-- No data state -->
            <div v-if="!isLoading && !alert" class="flex-1 flex items-center justify-center">
              <p class="text-text-light text-sm">{{ $t('common.noData') || '暂无数据' }}</p>
            </div>

            <!-- Sidebar -->
            <aside
              v-if="!isLoading && alert"
              :class="[
                rightSidebarTab === 'securityAgent' ? 'w-[32rem]' : 'w-80',
                'border-l border-border-dark bg-[#1f2937]/20 flex flex-col overflow-hidden'
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
                        : 'text-slate-400 hover:text-white border-transparent'
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
                        : 'text-slate-400 hover:text-white border-transparent'
                    ]"
                  >
                    {{ $t('alerts.detail.securityAgentTab') }}
                  </button>
                </nav>
              </div>

              <!-- Response 页签内容 -->
              <div v-if="rightSidebarTab === 'response'" class="overflow-y-auto custom-scrollbar flex-1 pl-6 pb-6">
                <div class="pr-6 space-y-6">
                <!-- 关联实体 -->
                <div class="space-y-4" v-if="alert?.associatedEntities">
                  <h3 class="text-base font-semibold text-white">{{ $t('alerts.detail.associatedEntities') }}</h3>
                  <div class="space-y-3">
                    <div
                      v-for="(entity, index) in alert.associatedEntities"
                      :key="index"
                      class="flex items-center gap-3 p-3 rounded-lg bg-[#2a3546] hover:bg-[#3c4a60] cursor-pointer transition-colors"
                    >
                      <span class="material-symbols-outlined text-primary">
                        {{ getEntityIcon(entity.type) }}
                      </span>
                      <div class="text-sm flex-1 min-w-0">
                        <p class="font-medium text-white truncate">{{ entity.name }}</p>
                        <p class="text-text-light truncate">{{ entity.label }}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 事件时间线 -->
                <div class="space-y-4" v-if="alert?.timeline">
                  <h3 class="text-base font-semibold text-white">{{ $t('alerts.detail.eventTimeline') }}</h3>
                  <div class="relative pl-6">
                    <div class="absolute left-0 h-full w-0.5 bg-border-dark"></div>
                    <div class="relative space-y-6">
                      <div
                        v-for="(event, index) in alert.timeline"
                        :key="index"
                        class="relative"
                      >
                        <div
                          :class="[
                            'absolute -left-7 top-1.5 h-2 w-2 rounded-full ring-4 ring-panel-dark',
                            index === 0 ? 'bg-primary' : 'bg-border-dark'
                          ]"
                        ></div>
                        <p class="text-xs text-text-light">{{ event.time }}</p>
                        <p class="text-sm text-white">{{ event.event }}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 自动化响应 -->
                <div class="space-y-4">
                  <h3 class="text-base font-semibold text-white">{{ $t('alerts.detail.automatedResponse') }}</h3>
                  <div class="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
                    <div class="flex items-start gap-3">
                      <span class="material-symbols-outlined text-green-400 mt-0.5">task_alt</span>
                      <div>
                        <p class="font-semibold text-white text-sm">Block IP Address</p>
                        <p class="text-xs text-green-300/80">
                          Successfully blocked {{ alert?.associatedEntities?.find(e => e.type === 'ip')?.name || 'IP' }} at firewall.
                        </p>
                      </div>
                    </div>
                  </div>
                  <div class="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                    <div class="flex items-start gap-3">
                      <span class="material-symbols-outlined text-yellow-400 mt-0.5">hourglass_top</span>
                      <div>
                        <p class="font-semibold text-white text-sm">Threat Intel Scan</p>
                        <p class="text-xs text-yellow-300/80">Scan in progress for related indicators...</p>
                      </div>
                    </div>
                  </div>
                  <button
                    class="w-full bg-[#2a3546] hover:bg-[#3c4a60] text-sm font-medium text-white px-4 py-2 rounded-md transition-colors flex items-center gap-2 justify-center"
                  >
                    <span class="material-symbols-outlined text-base">play_circle</span>
                    {{ $t('alerts.detail.runPlaybook') }}
                  </button>
                </div>
                </div>
              </div>

              <!-- Security Agent 页签内容 -->
              <div v-if="rightSidebarTab === 'securityAgent'" class="flex flex-col flex-1 min-h-0 min-w-0 pl-6 pb-6 pr-6">
                
                <!-- Security Agent 聊天组件 -->
                <div class="flex-1 min-h-0 min-w-0">
                  <SecurityAgentChat
                    :messages="securityAgentMessages"
                    :auto-scroll="true"
                    :disabled="isSendingSecurityAgentMessage"
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
      <div class="bg-[#111822] border border-[#324867] rounded-lg p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-white">
            {{ $t('alerts.list.batchCloseDialog.title') }}
          </h2>
          <button
            @click="closeBatchCloseDialog"
            class="text-gray-400 hover:text-white transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
          </button>
        </div>

        <!-- 提示信息 -->
        <div class="mb-4 p-3 bg-[#1e293b] rounded-md">
          <p class="text-sm text-gray-400">
            {{ $t('alerts.list.batchCloseDialog.confirmMessage', { count: 1 }) }}
          </p>
        </div>

        <!-- 结论分类下拉框 -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-white mb-2">
            {{ $t('alerts.list.batchCloseDialog.conclusionCategory') }}
          </label>
          <select
            v-model="closeConclusion.category"
            class="w-full bg-[#1e293b] text-white border border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value="">{{ $t('alerts.list.batchCloseDialog.selectCategory') }}</option>
            <option value="falsePositive">{{ $t('alerts.list.batchCloseDialog.categories.falsePositive') }}</option>
            <option value="resolved">{{ $t('alerts.list.batchCloseDialog.categories.resolved') }}</option>
            <option value="repeated">{{ $t('alerts.list.batchCloseDialog.categories.repeated') }}</option>
            <option value="other">{{ $t('alerts.list.batchCloseDialog.categories.other') }}</option>
          </select>
        </div>

        <!-- 调查结论输入框 -->
        <div class="mb-6 relative">
          <label class="block text-sm font-medium text-white mb-2">
            {{ $t('alerts.list.batchCloseDialog.conclusion') }}
          </label>
          <div class="relative">
            <textarea
              v-model="closeConclusion.notes"
              @focus="showAlertHistoryDropdown = true"
              @blur="handleAlertTextareaBlur"
              rows="4"
              class="w-full bg-[#1e293b] text-white border border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary resize-none"
              :placeholder="$t('alerts.list.batchCloseDialog.conclusionPlaceholder')"
            ></textarea>
            <!-- 历史记录下拉菜单 -->
            <div
              v-if="showAlertHistoryDropdown && alertCommentHistory.length > 0"
              class="absolute z-10 w-full mt-1 bg-[#1e293b] border border-[#324867] rounded-md shadow-lg max-h-48 overflow-y-auto"
              @mousedown.prevent
            >
              <div
                v-for="(item, index) in alertCommentHistory"
                :key="index"
                @click="selectAlertHistoryItem(item)"
                class="px-4 py-2 text-sm text-white hover:bg-[#324867] cursor-pointer border-b border-[#324867] last:border-b-0"
              >
                <div class="truncate">{{ item }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex items-center justify-end gap-3">
          <button
            @click="closeBatchCloseDialog"
            class="px-4 py-2 text-sm text-gray-400 bg-[#1e293b] rounded-md hover:bg-primary/30 transition-colors"
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
import CreateIncidentDialog from '@/components/incidents/CreateIncidentDialog.vue'
import EditAlertDialog from '@/components/alerts/EditAlertDialog.vue'
import AssociateIncidentDialog from '@/components/alerts/AssociateIncidentDialog.vue'
import CreateVulnerabilityDialog from '@/components/vulnerabilities/CreateVulnerabilityDialog.vue'
import AlertInfoCard from '@/components/alerts/AlertInfoCard.vue'
import AiChatDialog from '@/components/alerts/AiChatDialog.vue'
import SecurityAgentChat from '@/components/alerts/SecurityAgentChat.vue'
import { sendSecurityAgentMessage } from '@/api/securityAgent'
import { formatDateTime, calculateTTR } from '@/utils/dateTime'
import { saveCloseComment, getCloseCommentHistory } from '@/utils/closeCommentHistory'
import DOMPurify from 'dompurify'
import UserAvatar from '@/components/common/UserAvatar.vue'
import CommentInput from '@/components/common/CommentInput.vue'
import CommentSection from '@/components/common/CommentSection.vue'
import { useToast } from '@/composables/useToast'

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
const showBatchCloseDialog = ref(false)
const isClosing = ref(false)
const showAlertHistoryDropdown = ref(false)
const alertCommentHistory = ref([])
const closeConclusion = ref({
  category: '',
  notes: ''
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

const tabs = [
  { key: 'overview', label: 'alerts.detail.overview' },
  { key: 'associatedAlerts', label: 'alerts.detail.associatedAlerts' },
  { key: 'threatIntelligence', label: 'alerts.detail.threatIntelligence' },
  { key: 'aiAgent', label: 'alerts.detail.aiAgent' }
]

/**
 * @brief 获取页签的计数
 * @param {string} tabKey - 页签的key
 * @returns {number} 该页签下的数据条数
 */
const getTabCount = (tabKey) => {
  if (!alert.value) return 0
  
  switch (tabKey) {
    case 'overview':
      // Overview 页签显示 comments 的数量
      return alert.value.comments?.length || 0
    case 'associatedAlerts':
      // Associated Alerts 页签显示关联告警的数量
      return associatedAlerts.value?.length || 0
    case 'threatIntelligence':
      // Threat Intelligence 页签显示威胁情报的数量
      return alert.value.intelligence?.length || 0
    case 'aiAgent':
      // AI Agent 页签显示 AI 分析结果的数量
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

/**
 * @brief 转换后端返回的告警详情数据为前端期望的格式
 * @param {Object} apiData - 后端返回的告警数据
 * @returns {Object} 转换后的告警对象
 */
const transformAlertDetailData = (apiData) => {
  if (!apiData) return null

  // 转换severity为riskLevel (Fatal/High/Medium/Low/Tips -> fatal/high/medium/low/tips)
  const severityMap = {
    'Fatal': 'fatal',
    'High': 'high',
    'Medium': 'medium',
    'Low': 'low',
    'Tips': 'tips'
  }
  
  // 转换handle_status为status (Open/Block/Closed -> open/block/closed)
  const statusMap = {
    'Open': 'open',
    'Block': 'block',
    'Closed': 'closed'
  }

  // 从description中提取字段
  // 保留原始的 description 值（可能是字符串或对象）
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

  // 转换comments格式
  const comments = (apiData.comments || []).map(comment => ({
    id: comment.id || Date.now(),
    author: comment.author || 'Unknown',
    authorInitials: (comment.author || 'U').substring(0, 2).toUpperCase(),
    time: formatDateTime(comment.create_time || comment.time),
    content: comment.content || '',
    file: comment.file || null  // 保留文件信息
  }))

  // 转换intelligence格式
  const intelligence = (apiData.intelligence || []).map(item => ({
    id: item.id || Date.now(),
    author: item.author || 'Unknown',
    time: item.create_time || item.time || '-',
    content: item.content || ''
  }))

  // 转换ai格式
  const ai = (apiData.ai || []).map(item => ({
    id: item.id || Date.now(),
    author: item.author || 'AI Agent',
    time: item.create_time || item.time || '-',
    content: item.content || ''
  }))

  // 转换entities格式
  const entities = (apiData.entities || []).map(entity => ({
    type: entity.type || 'unknown',
    name: entity.name || '',
    label: entity.from || entity.label || ''
  }))

  // 转换timeline格式（时间使用本地时区显示）
  const timeline = (apiData.timeline || []).map(event => {
    const formattedTime = formatDateTime(event.time || event.timestamp)
    return {
      time: formattedTime !== '-' ? formattedTime : (event.time || '-'),
      event: event.event || ''
    }
  })

  // 从description中提取字段（只有当description是对象时才尝试访问属性）
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

/**
 * @brief 加载告警详情
 * @details 从API获取告警详细信息并显示
 */
const loadAlertDetail = async () => {
  if (!currentAlertId.value) return
  
  // 重置状态
  alert.value = null
  isLoading.value = true
  
  // 先显示面板，确保滑入动画能触发
  visible.value = true
  
  // 添加一个小延迟确保动画能显示
  await new Promise(resolve => setTimeout(resolve, 50))
  
  try {
    const response = await getAlertDetail(currentAlertId.value)
    // 转换后端返回的数据格式
    alert.value = transformAlertDetailData(response.data)
    securityAgentMessages.value = []
    // 加载关联告警
    loadAssociatedAlerts()
  } catch (error) {
    console.error('Failed to load alert detail:', error)
    // 加载失败时只触发 close 事件，不进行路由跳转
    emit('close')
  } finally {
    // 确保加载状态在数据加载完成后才关闭
    isLoading.value = false
  }
}

/**
 * @brief 加载关联告警数据
 * @details 从 historic 数据中提取关联告警列表
 */
const loadAssociatedAlerts = async () => {
  if (!currentAlertId.value) return

  loadingAssociatedAlerts.value = true
  try {
    // 只使用 historic 数据，不调用其他接口
    if (alert.value?.historic?.length) {
      const data = transformHistoricEntries(alert.value.historic, alert.value?.id)
      associatedAlerts.value = data
    } else {
      // 如果没有 historic 数据，使用空数组
      associatedAlerts.value = []
    }
  } catch (error) {
    console.error('Failed to load associated alerts:', error)
    associatedAlerts.value = []
  } finally {
    loadingAssociatedAlerts.value = false
  }
}

const handleClose = async () => {
  showMoreActionsMenu.value = false
  
  // 如果还在加载，等待加载完成，但最多等待动画时间
  const closeDelay = 300 // 动画持续时间
  const startTime = Date.now()
  
  // 如果还在加载，等待加载完成（但不超过动画时间）
  if (isLoading.value) {
    while (isLoading.value && (Date.now() - startTime) < closeDelay) {
      await new Promise(resolve => setTimeout(resolve, 50))
    }
  }
  
  // 开始关闭动画
  visible.value = false
  
  setTimeout(() => {
    emit('close')
  }, closeDelay)
}

// 加载告警历史记录
const loadAlertHistory = () => {
  alertCommentHistory.value = getCloseCommentHistory('alert')
}

// 处理输入框失焦事件（延迟关闭下拉菜单，以便点击选项时能触发）
const handleAlertTextareaBlur = () => {
  // 延迟关闭，让点击事件先触发
  setTimeout(() => {
    showAlertHistoryDropdown.value = false
  }, 200)
}

// 选择历史记录项
const selectAlertHistoryItem = (item) => {
  closeConclusion.value.notes = item
  showAlertHistoryDropdown.value = false
}

const openBatchCloseDialog = () => {
  if (!canCloseAlert.value) {
    return
  }
  // 打开弹窗时加载历史记录
  loadAlertHistory()
  showBatchCloseDialog.value = true
}

const closeBatchCloseDialog = () => {
  showBatchCloseDialog.value = false
  // 重置表单
  closeConclusion.value = {
    category: '',
    notes: ''
  }
  // 重置加载状态
  isClosing.value = false
  showAlertHistoryDropdown.value = false
}

const handleBatchClose = async () => {
  if (!closeConclusion.value.category || !closeConclusion.value.notes.trim()) {
    return
  }

  if (!currentAlertId.value) {
    return
  }

  // 设置加载状态
  isClosing.value = true

  try {
    // 保存评论到历史记录
    saveCloseComment(closeConclusion.value.notes.trim(), 'alert')
    
    // 调用单个告警关闭接口
    await closeAlert(currentAlertId.value, {
      category: closeConclusion.value.category,
      notes: closeConclusion.value.notes.trim()
    })
    
    // 关闭对话框并重置表单
    closeBatchCloseDialog()
    
    await loadAlertDetail()
    
    emit('closed')
  } catch (error) {
    console.error('Failed to close alert:', error)
    // 发生错误时，保持对话框打开，但重置加载状态
    isClosing.value = false
  }
}

// 计算是否可以关闭告警（只有状态不是closed时才可关闭）
const canCloseAlert = computed(() => {
  return alert.value && alert.value.status !== 'closed'
})

// 计算是否可以开启告警（只有状态为closed时才可开启）
const canOpenAlert = computed(() => {
  return alert.value && alert.value.status === 'closed'
})

// 开启告警
const handleOpenAlert = async () => {
  if (!canOpenAlert.value || !currentAlertId.value) {
    return
  }

  try {
    await openAlert(currentAlertId.value)
    
    // 重新加载告警详情以更新状态
    await loadAlertDetail()
    
    // 触发刷新事件，让父组件知道需要刷新列表
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
  
  // 解析告警的创建时间
  let occurrenceTime = new Date()
  try {
    // 尝试解析告警的创建时间
    if (alert.value.createTime || alert.value.timestamp) {
      occurrenceTime = new Date(alert.value.createTime || alert.value.timestamp)
      // 如果解析失败，使用当前时间
      if (isNaN(occurrenceTime.getTime())) {
        occurrenceTime = new Date()
      }
    }
  } catch (error) {
    console.warn('Failed to parse alert create time:', error)
    occurrenceTime = new Date()
  }
  
  // 获取告警描述（优先使用 aiAnalysis.description，否则使用 description）
  const alertDescription = alert.value.aiAnalysis?.description || alert.value.description || ''
  
  // 设置初始数据
  createIncidentInitialData.value = {
    title: alert.value.title || '',
    occurrenceTime: occurrenceTime,
    description: alertDescription
  }
  
  // 打开对话框
  showCreateIncidentDialog.value = true
}

const closeCreateIncidentDialog = () => {
  showCreateIncidentDialog.value = false
  createIncidentInitialData.value = null
}

const handleIncidentCreated = () => {
  // 事件创建成功后，关闭对话框
  closeCreateIncidentDialog()
  // 触发刷新事件，让父组件知道需要刷新列表
  emit('created')
}

const openCreateVulnerabilityDialog = () => {
  if (!alert.value) {
    console.warn('Alert data not loaded')
    return
  }
  
  // 获取告警描述（优先使用 aiAnalysis.description，否则使用 description）
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
  
  // 设置初始数据
  createVulnerabilityInitialData.value = {
    title: alert.value.title || '',
    riskLevel: alert.value.riskLevel || alert.value.severity?.toLowerCase() || 'medium',
    status: alert.value.status || 'open',
    owner: alert.value.owner || '',
    actor: alert.value.actor || '',
    description: alertDescription
  }
  
  // 打开对话框
  showCreateVulnerabilityDialog.value = true
}

const closeCreateVulnerabilityDialog = () => {
  showCreateVulnerabilityDialog.value = false
  createVulnerabilityInitialData.value = null
}

const handleVulnerabilityCreated = () => {
  // 漏洞创建成功后，关闭对话框
  closeCreateVulnerabilityDialog()
  // 触发刷新事件，让父组件知道需要刷新列表
  emit('created')
}

const openEditAlertDialog = () => {
  if (!alert.value) {
    console.warn('Alert data not loaded')
    return
  }
  
  // 解析告警的时间戳
  let timestamp = new Date()
  try {
    if (alert.value.timestamp || alert.value.createTime) {
      timestamp = new Date(alert.value.timestamp || alert.value.createTime)
      // 如果解析失败，使用当前时间
      if (isNaN(timestamp.getTime())) {
        timestamp = new Date()
      }
    }
  } catch (error) {
    console.warn('Failed to parse alert timestamp:', error)
    timestamp = new Date()
  }
  
  // 设置初始数据
  editAlertInitialData.value = {
    title: alert.value.title || '',
    riskLevel: alert.value.riskLevel || alert.value.severity || '',
    status: alert.value.status || 'open',
    owner: alert.value.owner || '',
    ruleName: alert.value.ruleName || '',
    timestamp: timestamp,
    description: alert.value.description || ''
  }
  
  // 打开对话框
  showEditAlertDialog.value = true
}

const closeEditAlertDialog = () => {
  showEditAlertDialog.value = false
  editAlertInitialData.value = null
}

const handleAlertUpdated = async () => {
  // 告警更新成功后，关闭对话框并重新加载详情
  closeEditAlertDialog()
  await loadAlertDetail()
  // 触发刷新事件，让父组件知道需要刷新列表
  emit('closed')
}

const openAssociateIncidentDialog = () => {
  if (!currentAlertId.value) {
    console.warn('No alert ID available')
    return
  }
  showAssociateIncidentDialog.value = true
}

// 从菜单触发的包装函数
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
  // 关联成功后，关闭对话框并重新加载详情
  closeAssociateIncidentDialog()
  await loadAlertDetail()
  // 触发刷新事件，让父组件知道需要刷新列表
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

// Note: File handling functions (getFileIcon, formatFileSize, openImageModal, downloadFile) 
// have been moved to CommentSection component

const handleAddComment = async ({ comment, files }) => {
  if (!currentAlertId.value) {
    toast.error(t('alerts.detail.comments.postError') || '无法提交评论：告警ID不存在', 'ERROR')
    return
  }
  
  try {
    const commentText = comment.trim()
    // 允许只有文件没有文本的情况
    if (!commentText && (!files || files.length === 0)) {
      return
    }
    
    // 调用 API 提交评论（包含文件）
    await postComment(currentAlertId.value, commentText, files || [])
    
    // 清空输入（组件会自动清空）
    newComment.value = ''
    
    // 重新加载告警详情以获取最新评论
    await loadAlertDetail()
    
    // 显示成功提示
    toast.success(t('alerts.detail.comments.postSuccess') || '评论提交成功', 'SUCCESS')
  } catch (error) {
    console.error('Failed to post comment:', error)
    const errorMessage = error?.response?.data?.message || error?.message || t('alerts.detail.comments.postError') || '评论提交失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
  }
}

// AI 对话相关方法
const canSubmitAiMessage = computed(() => {
  return newAiMessage.value.trim().length > 0 || uploadedAiFiles.value.length > 0
})

const handleAiMessageInput = () => {
  // 可以在这里添加自动调整高度的逻辑
}

const handleAiFileSelect = (event) => {
  const files = Array.from(event.target.files || [])
  addAiFiles(files)
  // 清空input，以便可以再次选择相同文件
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
    // 检查文件大小（限制为10MB）
    if (file.size > 10 * 1024 * 1024) {
      console.warn(`File ${file.name} is too large (max 10MB)`)
      return
    }
    // 检查是否已存在
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
  
  // TODO: 实现发送 AI 消息的逻辑，包含文件上传
  console.log('Sending AI message:', newAiMessage.value)
  console.log('Files:', uploadedAiFiles.value)
  
  // 清空输入
  newAiMessage.value = ''
  uploadedAiFiles.value = []
}

// 右侧侧边栏AI问答相关方法
const canSubmitRightSidebarAiMessage = computed(() => {
  return rightSidebarAiMessage.value.trim().length > 0 || rightSidebarAiFiles.value.length > 0
})

const handleRightSidebarAiMessageInput = () => {
  // 可以在这里添加自动调整高度的逻辑
}

const handleRightSidebarAiFileSelect = (event) => {
  const files = Array.from(event.target.files || [])
  addRightSidebarAiFiles(files)
  // 清空input，以便可以再次选择相同文件
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
    // 检查文件大小（限制为10MB）
    if (file.size > 10 * 1024 * 1024) {
      console.warn(`File ${file.name} is too large (max 10MB)`)
      return
    }
    // 检查是否已存在
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

const stringifyAlertDescription = (description) => {
  if (!description) return ''
  if (typeof description === 'string') return description
  if (Array.isArray(description)) {
    return description.map(item => stringifyAlertDescription(item)).join(', ')
  }
  if (typeof description === 'object') {
    try {
      return JSON.stringify(description, null, 2)
    } catch {
      return Object.entries(description)
        .map(([key, value]) => `${key}: ${stringifyAlertDescription(value)}`)
        .join('\n')
    }
  }
  return String(description)
}

const buildSecurityAgentContext = (alertData, userMessage) => {
  if (!alertData) return {}
  return {
    alertId: alertData.id,
    alertTitle: alertData.title || '',
    alertSeverity: alertData.riskLevel || alertData.severity || '',
    alertStatus: alertData.status || '',
    alertOwner: alertData.owner || '',
    alertActor: alertData.actor || '',
    alertRuleName: alertData.ruleName || '',
    alertDescription: stringifyAlertDescription(alertData.description),
    alertTimestamp: alertData.timestamp || alertData.createTime || '',
    analystMessage: userMessage || ''
  }
}

const buildSecurityAgentPrompt = (userMessage, context) => {
  const lines = []
  if (context.alertTitle) {
    lines.push(`Alert Title: ${context.alertTitle}`)
  }
  if (context.alertSeverity) {
    lines.push(`Alert Severity: ${context.alertSeverity}`)
  }
  if (context.alertStatus) {
    lines.push(`Alert Status: ${context.alertStatus}`)
  }
  if (context.alertDescription) {
    lines.push(`Alert Description: ${context.alertDescription}`)
  }
  if (context.alertRuleName) {
    lines.push(`Rule Name: ${context.alertRuleName}`)
  }
  if (context.alertOwner) {
    lines.push(`Owner: ${context.alertOwner}`)
  }
  if (context.alertActor) {
    lines.push(`Actor: ${context.alertActor}`)
  }
  lines.push(`Analyst Message: ${userMessage || ''}`)
  return lines.join('\n')
}

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
    isLocal: message.isLocal || false
  }
  securityAgentMessages.value = [...securityAgentMessages.value, normalizedMessage]
  return normalizedMessage.id
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

// 处理复用的 AI 对话框组件发送事件
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
    message: buildSecurityAgentPrompt(sanitizedUserMessage, buildSecurityAgentContext(alert.value, sanitizedUserMessage)),
    files: data.files
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
        if (!event) return
        const eventType = event.event || event.type
        if (eventType === 'message') {
          if (assistantMessageId && typeof event.answer === 'string') {
            appendToSecurityAgentMessage(assistantMessageId, event.answer)
          }
        } else if (eventType === 'message_end') {
          if (assistantMessageId && typeof event.answer === 'string') {
            appendToSecurityAgentMessage(assistantMessageId, event.answer)
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

/**
 * @brief 获取风险等级样式类
 * @param {string} level - 风险等级（fatal/high/medium/low/tips）
 * @returns {string} 返回对应的CSS类名
 */
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

/**
 * @brief 获取状态样式类
 * @param {string} status - 状态（open/block/closed）
 * @returns {string} 返回对应的CSS类名
 */
const getStatusClass = (status) => {
  const classes = {
    open: 'bg-primary/20 text-primary',
    block: 'bg-yellow-500/20 text-yellow-400',
    closed: 'bg-gray-500/20 text-gray-400'
  }
  return classes[status] || classes.open
}

/**
 * @brief 获取状态点样式类
 * @param {string} status - 状态（open/block/closed）
 * @returns {string} 返回对应的CSS类名
 */
const getStatusDotClass = (status) => {
  const classes = {
    open: 'bg-primary',
    block: 'bg-yellow-400',
    closed: 'bg-gray-400'
  }
  return classes[status] || classes.open
}

// 生成告警URL
const getAlertUrl = () => {
  const raw = import.meta.env.VITE_WEB_BASE_PATH
  let basePath = '/'
  if (raw && raw !== '/') {
    basePath = raw.startsWith('/') ? raw : `/${raw}`
    // Remove trailing slash if present
    basePath = basePath.replace(/\/$/, '')
  }
  const origin = window.location.origin
  const path = basePath === '/' ? '/alerts' : `${basePath}/alerts`
  return `${origin}${path}/${currentAlertId.value}`
}

// 分享告警（复制标题和链接到剪切板）
const handleShare = async () => {
  if (!alert.value) return
  
  const title = alert.value.title || ''
  const url = getAlertUrl()
  const textToCopy = `${title}: ${url}`
  
  try {
    await navigator.clipboard.writeText(textToCopy)
    // 显示成功提示
    showShareSuccess.value = true
    setTimeout(() => {
      showShareSuccess.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy to clipboard:', err)
    // 降级方案：使用传统的复制方法
    const textArea = document.createElement('textarea')
    textArea.value = textToCopy
    textArea.style.position = 'fixed'
    textArea.style.opacity = '0'
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      // 显示成功提示
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

// 监听告警ID变化，避免重复加载
watch(currentAlertId, async (newId, oldId) => {
  if (!newId) {
    visible.value = false
    return
  }
  if (newId === oldId) {
    return
  }
  
  // 如果面板已经打开，先短暂隐藏以触发新的滑入动画
  if (visible.value && oldId) {
    visible.value = false
    await new Promise(resolve => setTimeout(resolve, 50))
  }
  
  loadAlertDetail()
}, { immediate: true })

// 监听标签页切换，按需加载数据
watch(activeTab, (newTab) => {
  if (newTab === 'associatedAlerts' && associatedAlerts.value.length === 0 && !loadingAssociatedAlerts.value) {
    loadAssociatedAlerts()
  }
})

// 点击外部关闭下拉菜单
const handleClickOutside = (event) => {
  const dropdown = event.target.closest('.more-actions-dropdown')
  const button = event.target.closest('.more-actions-button')
  if (!dropdown && !button) {
    showMoreActionsMenu.value = false
  }
}

onMounted(() => {
  // 阻止背景滚动
  document.body.style.overflow = 'hidden'
  // 添加点击外部关闭下拉菜单的监听器
  document.addEventListener('click', handleClickOutside)
})

// 组件卸载时恢复滚动
onUnmounted(() => {
  document.body.style.overflow = ''
  // 移除点击外部关闭下拉菜单的监听器
  document.removeEventListener('click', handleClickOutside)
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

.ai-agent__html :deep(pre) {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.2);
  padding: 12px;
  border-radius: 6px;
  white-space: pre-wrap;
  margin: 10px 0;
}

.ai-agent__html :deep(code) {
  font-family: 'Fira Code', 'Source Code Pro', monospace;
  font-size: 13px;
}

.ai-agent__html :deep(b) {
  color: #e2e8f0;
}

</style>

