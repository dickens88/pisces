<template>
  <Teleport to="body">
    <div
      v-if="visible || currentAlertId"
      class="fixed inset-0 z-50 flex items-center justify-end"
      @click.self="handleClose"
    >
      <!-- Overlay - displayed directly, no animation -->
      <div 
        class="fixed inset-0 bg-black/75"
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
              <div class="flex items-center gap-2">
                <h2 class="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <span class="material-symbols-outlined text-base">security</span>
                  {{ $t('alerts.detail.title') }}
                </h2>
                <button
                  @click="handleToggleActor"
                  :disabled="isUpdatingActor"
                  class="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  :title="isActorEmpty ? $t('alerts.detail.actorUnlocked') : $t('alerts.detail.actorLocked')"
                >
                  <span class="material-symbols-outlined text-base">
                    {{ isActorEmpty ? 'lock_open' : 'lock' }}
                  </span>
                </button>
              </div>
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
                  {{ $t('alerts.detail.closeAlert') }}
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
                    <button
                      @click="handleAssociateVulnerabilityFromMenu"
                      class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867]"
                    >
                      <span class="material-symbols-outlined text-base">link</span>
                      {{ $t('alerts.list.associateVulnerability') }}
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
              <!-- 面包屑导航 -->
              <nav class="mb-5">
                <ol class="flex items-center gap-2.5 text-sm">
                  <li>
                    <router-link
                      to="/alerts"
                      class="inline-flex items-center gap-1.5 text-gray-500 dark:text-gray-400 hover:text-primary dark:hover:text-primary transition-colors duration-200 font-medium"
                    >
                      <span class="material-symbols-outlined text-base">folder</span>
                      <span>{{ $t('alerts.title') }}</span>
                    </router-link>
                  </li>
                  <li class="flex items-center text-gray-300 dark:text-gray-600">
                    <span class="material-symbols-outlined text-lg">chevron_right</span>
                  </li>
                  <li class="flex items-center gap-2">
                    <span class="text-gray-400 dark:text-gray-500 font-medium">ID:</span>
                    <span class="text-gray-900 dark:text-white font-semibold font-mono text-sm bg-gray-100 dark:bg-slate-700/50 px-2.5 py-1 rounded-md border border-gray-200 dark:border-slate-600">
                      {{ currentAlertId || '--' }}
                    </span>
                    <button
                      @click="handleCopyId"
                      class="inline-flex items-center justify-center p-0.5 text-gray-500 dark:text-gray-400 hover:text-primary dark:hover:text-primary transition-colors duration-200 rounded"
                      :title="$t('alerts.detail.copyId')"
                    >
                      <span class="material-symbols-outlined text-sm">content_copy</span>
                    </button>
                  </li>
                </ol>
              </nav>
              <!-- Title and severity -->
              <div>
                <h1 class="text-lg font-bold text-gray-900 dark:text-white">{{ alert.title }}</h1>
                <div class="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-text-light">
                  <div class="flex items-center gap-1.5">
                    <span
                      :class="[
                        'inline-flex items-center rounded-full px-3 py-1 text-xs font-medium',
                        getSeverityClass(alert.riskLevel || alert.severity?.toLowerCase())
                      ]"
                    >
                      <svg class="-ml-0.5 mr-1 h-1.5 w-1.5" fill="currentColor" viewBox="0 0 8 8">
                        <circle cx="4" cy="4" r="3"></circle>
                      </svg>
                      {{
                        $t(`common.severity.${alert.riskLevel || alert.severity?.toLowerCase() || 'medium'}`)
                      }}
                    </span>
                    <div class="h-4 w-px bg-gray-300 dark:bg-gray-600 flex-shrink-0"></div>
                    <!-- AI研判结果图标 -->
                    <span
                      v-if="alert.verification_state === 'True_Positive'"
                      class="material-symbols-outlined text-red-500 flex-shrink-0"
                      style="font-size: 20px;"
                      :title="$t('alerts.list.aiJudge') + ': ' + $t('alerts.list.aiJudgeResult.truePositive')"
                    >
                      Input_circle
                    </span>
                    <span
                      v-else-if="alert.verification_state === 'False_Positive'"
                      class="material-symbols-outlined text-green-500 flex-shrink-0"
                      style="font-size: 20px;"
                      :title="$t('alerts.list.aiJudge') + ': ' + $t('alerts.list.aiJudgeResult.falsePositive')"
                    >
                      output_circle
                    </span>
                    <span
                      v-else-if="alert.verification_state === 'Unknown' || !alert.verification_state"
                      class="material-symbols-outlined text-gray-400 flex-shrink-0"
                      style="font-size: 20px;"
                      :title="$t('alerts.list.aiJudge') + ': ' + $t('alerts.list.aiJudgeResult.unknown')"
                    >
                      Unknown_5
                    </span>
                  </div>
                  <div class="h-4 w-px bg-border-dark/50"></div>
                  <div class="flex items-center gap-1.5">
                    <span class="font-semibold text-gray-900 dark:text-white mr-1">
                      {{ $t('alerts.detail.relatedIncident') }}
                    </span>
                    <template v-if="relatedIncidentId">
                      <button
                        type="button"
                        @click="openIncidentInNewWindow"
                        class="inline-flex items-center gap-1.5 rounded-full bg-red-500/10 hover:bg-red-500/20 text-red-500 px-2 py-0.5 transition-colors"
                        :title="t('alerts.detail.openRelatedIncident', { id: relatedIncidentId })"
                      >
                        <span class="material-symbols-outlined text-sm">link</span>
                      </button>
                    </template>
                    <span v-else class="text-gray-500 dark:text-gray-400">-</span>
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
                          <template v-if="key === 'log_analysis' && isHttpLink(value)">
                            <button
                              @click="openLinkInNewWindow(value)"
                              class="inline-flex items-center gap-2 px-3 py-1.5 bg-primary hover:bg-primary/90 text-white text-sm font-medium rounded-md transition-colors"
                              :title="value"
                            >
                              <span class="material-symbols-outlined text-base">open_in_new</span>
                              {{ $t('alerts.detail.openLogAnalysis')}}
                            </button>
                          </template>
                          <!-- 其他情况正常显示 -->
                          <template v-else>
                            <p class="font-medium text-gray-900 dark:text-[#E3E3E3] break-all">
                              <span v-if="typeof value === 'object' && value !== null">{{ JSON.stringify(value) }}</span>
                              <span v-else>{{ value }}</span>
                            </p>
                            <button
                              v-if="isFieldMatchedWithEntity(key, value)"
                              @click="handleSendFieldToAISidebar(key, value)"
                              class="inline-flex items-center justify-center shrink-0 cursor-pointer transition-all duration-200 hover:brightness-125 hover:scale-110 ml-2"
                              :title="$t('alerts.detail.aiAssistant')"
                            >
                              <img 
                                src="/ai-chat.png" 
                                :alt="$t('alerts.detail.aiAssistant')" 
                                class="w-4 h-4"
                              />
                            </button>
                          </template>
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
                
                
                <div v-if="!alert?.ai || alert.ai.length === 0" class="text-text-light text-sm py-12 text-center">
                  {{ $t('alerts.detail.noAiResponse') }}
                </div>

                <div v-else class="grid grid-cols-1 @lg:grid-cols-2 gap-4">
                  <AlertInfoCard
                    v-for="(aiItem, index) in alert.ai"
                    :key="`ai-${index}`"
                    :owner="aiItem.author || 'AI Agent'"
                    owner-icon="smart_toy"
                    :header-meta="aiItem.create_time || aiItem.time || '-'"
                    :html-content="aiItem.content || ''"
                    :summary="stripHtmlTags(aiItem.content || '')"
                  />
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
              class="w-[260px] border-l border-gray-200 dark:border-border-dark bg-gray-50 dark:bg-[#1f2937]/20 flex flex-col overflow-hidden flex-shrink-0"
            >

              <!-- Response 页签内容 -->
              <div class="overflow-y-auto custom-scrollbar flex-1 pl-6 pb-6">
                <div class="pr-6 space-y-6">
                <!-- 关联实体 -->
                <div class="space-y-4" v-if="alert?.associatedEntities">
                  <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ $t('alerts.detail.associatedEntities') }}</h3>
                  <div class="space-y-3">
                    <div
                      v-for="(entity, index) in alert.associatedEntities"
                      :key="index"
                      @click="handleSendEntityToAISidebar(entity)"
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
                <AlertTimeline :timeline="alert?.timeline || []" />
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

    <!-- 关联漏洞对话框 -->
    <AssociateIncidentDialog
      :visible="showAssociateVulnerabilityDialog"
      :alert-ids="[currentAlertId]"
      mode="vulnerability"
      @close="closeAssociateVulnerabilityDialog"
      @associated="handleAssociateVulnerabilitySuccess"
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
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { getAlertDetail, getAlertRelations, batchCloseAlerts, openAlert, closeAlert, updateAlert } from '@/api/alerts'
import { useAuthStore } from '@/stores/auth'
import { postComment } from '@/api/comments'
import CreateIncidentDialog from '@/components/incidents/CreateIncidentDialog.vue'
import EditAlertDialog from '@/components/alerts/EditAlertDialog.vue'
import AssociateIncidentDialog from '@/components/alerts/AssociateIncidentDialog.vue'
import CreateVulnerabilityDialog from '@/components/vulnerabilities/CreateVulnerabilityDialog.vue'
import AlertInfoCard from '@/components/alerts/AlertInfoCard.vue'
import AiChatDialog from '@/components/alerts/AiChatDialog.vue'
import { formatDateTime, calculateTTR, parseToDate } from '@/utils/dateTime'
import { severityToNumber } from '@/utils/severity'
import DOMPurify from 'dompurify'
import UserAvatar from '@/components/common/UserAvatar.vue'
import CommentInput from '@/components/common/CommentInput.vue'
import CommentSection from '@/components/common/CommentSection.vue'
import AISidebar from '@/components/common/AISidebar.vue'
import AlertTimeline from '@/components/common/AlertTimeline.vue'
import { useToast } from '@/composables/useToast'
import { useRecentCloseCommentSuggestions } from '@/composables/useRecentCloseCommentSuggestions'
import { useDarkModeObserver } from '@/composables/useDarkModeObserver'

const props = defineProps({
  alertId: {
    type: [Number, String],
    required: false,
    default: null
  },
  // 可选 workspace，用于在特定页面（如 ASM 漏洞详情）下带上 workspace 查询参数
  workspace: {
    type: String,
    required: false,
    default: null
  }
})

const emit = defineEmits(['close', 'closed', 'created'])

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const toast = useToast()
const authStore = useAuthStore()

const visible = ref(false)
const alert = ref(null)
const isLoading = ref(false)
const relatedIncidentId = ref(null)

const currentAlertId = computed(() => {
  return props.alertId || route.params.id
})
const activeTab = ref('overview')
const newComment = ref('')
const newAiMessage = ref('')
const uploadedAiFiles = ref([])
const aiFileInput = ref(null)
const isAiDragging = ref(false)
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
const showCreateIncidentDialog = ref(false)
const createIncidentInitialData = ref(null)
const showEditAlertDialog = ref(false)
const editAlertInitialData = ref(null)
const showAssociateVulnerabilityDialog = ref(false)
const showShareSuccess = ref(false)
const associatedAlerts = ref([])
const loadingAssociatedAlerts = ref(false)
const showAssociateIncidentDialog = ref(false)
const showMoreActionsMenu = ref(false)
const isRefreshing = ref(false)
const showCreateVulnerabilityDialog = ref(false)
const createVulnerabilityInitialData = ref(null)
const isSubmittingComment = ref(false)
const isUpdatingActor = ref(false)
const showAISidebar = ref(false)
const aiSidebarRef = ref(null)
const aiFindingSummary = ref('')
const showFindingSummary = ref(false)

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
    const rawTime = event.time || event.timestamp
    const formattedTime = formatDateTime(rawTime)
    return {
      time: formattedTime !== '-' ? formattedTime : (rawTime || '-'),
      event: event.event || '',
      author: event.author || '',
      content: event.content || '',
      rawTime: rawTime || ''
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
    actor: apiData.actor || apiData.is_auto_closed|| '-',
    creator: apiData.creator || apiData.owner || '',
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
    verification_state: apiData.verification_state,
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

// 提取HTML标签和实体字符的工具函数
const stripHtmlAndEntities = (html) => {
  if (typeof html !== 'string') return String(html || '')
  return html
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .trim()
}

const findInvestigationContent = () => {
  if (!alert.value?.ai?.length) return ''
  const firstContent = alert.value.ai[0]?.content || ''
  return stripHtmlAndEntities(firstContent)
}

// 记录是否已因 AI Investigation 自动展开过，避免重复展开
const hasAutoOpenedAiSidebar = ref(false)

// 打开AI侧边栏并设置investigation内容
const openAISidebarWithInvestigation = async () => {
  if (!alert.value) return
  const investigationContent = findInvestigationContent()
  aiFindingSummary.value = investigationContent
  showFindingSummary.value = !!investigationContent
  showAISidebar.value = true
  await nextTick()
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
    const [detailResponse, relationsResponse] = await Promise.allSettled([
      getAlertDetail(currentAlertId.value, props.workspace),
      getAlertRelations(currentAlertId.value, props.workspace)
    ])
    
    // 处理告警详情响应
    if (detailResponse.status === 'fulfilled') {
      alert.value = transformAlertDetailData(detailResponse.value.data)
      loadAssociatedAlerts()
    } else {
      throw detailResponse.reason
    }
    
    // 处理关系响应（即使失败也不影响主流程）
    if (relationsResponse.status === 'fulfilled') {
      relatedIncidentId.value = relationsResponse.value.data?.incident_id || null
    } else {
      console.error('Failed to load alert relations:', relationsResponse.reason)
      relatedIncidentId.value = null
    }
    
    // 重置自动展开标记，交由 watcher 根据 AI Investigation 决定是否展开
    hasAutoOpenedAiSidebar.value = false
  } catch (error) {
    console.error('Failed to load alert detail:', error)
    const errorMessage = error?.response?.data?.message || error?.response?.data?.error_message || error?.message || t('alerts.detail.loadAlertDetailError') || '加载告警详情失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
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
    associatedAlerts.value = alert.value?.historic?.length
      ? transformHistoricEntries(alert.value.historic, alert.value?.id)
      : []
  } catch (error) {
    console.error('Failed to load associated alerts:', error)
    associatedAlerts.value = []
  } finally {
    loadingAssociatedAlerts.value = false
  }
}

const handleClose = async () => {
  showMoreActionsMenu.value = false
  
  // 如果正在加载，等待加载完成
  if (isLoading.value) {
    const startTime = Date.now()
    while (isLoading.value && (Date.now() - startTime) < 300) {
      await new Promise(resolve => setTimeout(resolve, 50))
    }
  }
  
  visible.value = false
  setTimeout(() => emit('close'), 300)
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

const isActorEmpty = computed(() => {
  if (!alert.value) return true
  const actor = alert.value.actor
  return !actor || actor === '-' || actor.trim() === ''
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
  
  let alertDescription = ''
  if (alert.value.description) {
    if (typeof alert.value.description === 'string') {
      alertDescription = alert.value.description
    } else if (typeof alert.value.description === 'object' && alert.value.description !== null) {
      alertDescription = JSON.stringify(alert.value.description, null, 2)
    } else {
      alertDescription = String(alert.value.description)
    }
  }
  
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

const openAssociateVulnerabilityDialog = () => {
  if (!currentAlertId.value) {
    console.warn('No alert ID available')
    return
  }
  showAssociateVulnerabilityDialog.value = true
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

const handleAssociateVulnerabilityFromMenu = () => {
  openAssociateVulnerabilityDialog()
  showMoreActionsMenu.value = false
}

const handleConvertToVulnerabilityFromMenu = () => {
  openCreateVulnerabilityDialog()
  showMoreActionsMenu.value = false
}

const closeAssociateIncidentDialog = () => {
  showAssociateIncidentDialog.value = false
}

const closeAssociateVulnerabilityDialog = () => {
  showAssociateVulnerabilityDialog.value = false
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

const handleAssociateVulnerabilitySuccess = async () => {
  closeAssociateVulnerabilityDialog()
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

// 向AI侧边栏发送消息的通用函数
const sendMessageToAISidebar = (message) => {
  if (!message) return
  showAISidebar.value = true
  setTimeout(() => {
    aiSidebarRef.value?.setMessage?.(message)
  }, 100)
}

const handleSendFieldToAISidebar = (key, value) => {
  if (!alert.value) return
  const valueStr = typeof value === 'object' && value !== null 
    ? JSON.stringify(value) 
    : String(value)
  sendMessageToAISidebar(`${key}: ${valueStr}`)
}

const handleSendEntityToAISidebar = (entity) => {
  if (!alert.value || !entity) return
  const from = entity.from || entity.label || ''
  const name = entity.name || ''
  sendMessageToAISidebar(`${from}: ${name}`)
}

const isHttpLink = (value) => {
  const valueStr = String(value || '').trim()
  return valueStr ? /^https?:\/\/.+/.test(valueStr) : false
}

const openLinkInNewWindow = (url) => {
  if (isHttpLink(url)) {
    window.open(url.trim(), '_blank', 'noopener,noreferrer')
  }
}

const getAlertUrl = () => {
  const raw = import.meta.env.VITE_WEB_BASE_PATH
  const basePath = raw && raw !== '/' 
    ? (raw.startsWith('/') ? raw : `/${raw}`).replace(/\/$/, '')
    : ''
  return `${window.location.origin}${basePath}/alerts/${currentAlertId.value}`
}

const getIncidentUrl = (incidentId) => {
  const raw = import.meta.env.VITE_WEB_BASE_PATH
  const basePath = raw && raw !== '/'
    ? (raw.startsWith('/') ? raw : `/${raw}`).replace(/\/$/, '')
    : ''
  return `${window.location.origin}${basePath}/incidents/${incidentId}`
}

const openIncidentInNewWindow = () => {
  if (!relatedIncidentId.value) return
  const url = getIncidentUrl(relatedIncidentId.value)
  window.open(url, '_blank', 'noopener,noreferrer')
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

const showShareSuccessMessage = () => {
  showShareSuccess.value = true
  setTimeout(() => { showShareSuccess.value = false }, 2000)
}

const handleShare = async () => {
  if (!alert.value) return
  
  const textToCopy = `${alert.value.title || ''}: ${getAlertUrl()}`
  
  try {
    await navigator.clipboard.writeText(textToCopy)
    showShareSuccessMessage()
  } catch (err) {
    console.error('Failed to copy to clipboard:', err)
    // 降级方案：使用传统方法
    const textArea = document.createElement('textarea')
    Object.assign(textArea.style, {
      position: 'fixed',
      opacity: '0'
    })
    textArea.value = textToCopy
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      showShareSuccessMessage()
    } catch (fallbackErr) {
      console.error('Fallback copy failed:', fallbackErr)
    }
    document.body.removeChild(textArea)
  }
}

const handleCopyId = async () => {
  if (!currentAlertId.value) return
  await navigator.clipboard.writeText(String(currentAlertId.value))
}

const handleToggleActor = async () => {
  if (!currentAlertId.value || isUpdatingActor.value) {
    return
  }

  const currentUser = authStore.user?.username || authStore.user?.name || authStore.user?.cn
  if (!currentUser) {
    toast.error(t('alerts.detail.actorUpdateError') || '无法获取当前用户信息', 'ERROR')
    return
  }

  isUpdatingActor.value = true

  try {
    await updateAlert(currentAlertId.value, {
      actor: currentUser
    })
    
    await loadAlertDetail(false)
    toast.success(t('alerts.detail.actorUpdateSuccess') || '操作成功', 'SUCCESS')
  } catch (error) {
    console.error('Failed to update actor:', error)
    const errorMessage = error?.response?.data?.error_message || error?.message || t('alerts.detail.actorUpdateError') || '操作失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
  } finally {
    isUpdatingActor.value = false
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

