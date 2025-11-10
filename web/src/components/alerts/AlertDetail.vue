<template>
  <Teleport to="body">
    <div
      v-if="alert"
      class="fixed inset-0 z-50 flex items-center justify-end"
      @click.self="handleClose"
    >
      <!-- 遮罩层 - 直接显示，无动画 -->
      <div 
        class="fixed inset-0 bg-black/90"
        @click="handleClose"
      ></div>
      
      <!-- 详情面板 - 有滑入动画 -->
      <Transition name="slide">
        <div
          v-if="visible"
          class="relative w-[70vw] h-full bg-panel-dark shadow-2xl flex flex-col overflow-hidden"
          @click.stop
        >
          <!-- 头部 -->
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
                <!-- 更多操作下拉菜单 -->
                <div class="relative">
                  <button
                    @click.stop="showMoreActionsMenu = !showMoreActionsMenu"
                    class="more-actions-button bg-[#2a3546] hover:bg-[#3c4a60] text-sm font-medium text-white px-4 py-2 rounded-md transition-colors flex items-center gap-2"
                  >
                    <span class="material-symbols-outlined text-base">more_vert</span>
                    {{ $t('alerts.detail.moreActions') }}
                    <span class="material-symbols-outlined text-base">arrow_drop_down</span>
                  </button>
                  <!-- 下拉菜单 -->
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
                  </div>
                </div>
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

          <!-- 内容区 -->
          <div class="flex flex-1 overflow-hidden">
            <main class="flex-1 p-6 space-y-8 overflow-y-auto custom-scrollbar">
              <!-- 标题和严重程度 -->
              <div v-if="alert">
                <span
                  :class="[
                    'inline-flex items-center rounded-full px-3 py-1 text-sm font-medium',
                    getSeverityClass(alert.severity)
                  ]"
                >
                  <svg class="-ml-0.5 mr-1.5 h-2 w-2" fill="currentColor" viewBox="0 0 8 8">
                    <circle cx="4" cy="4" r="3"></circle>
                  </svg>
                  {{ $t(`alerts.detail.severity.${alert.severity}`) }}
                </span>
                <h1 class="mt-2 text-3xl font-bold text-white">{{ alert.title }}</h1>
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
                    <span class="font-semibold text-white mr-1">{{ $t('alerts.detail.model') }}:</span>
                    <span class="font-mono text-white">{{ alert.ruleName || '-' }}</span>
                  </div>
                  <div class="h-4 w-px bg-border-dark/50"></div>
                  <div class="flex items-center gap-1.5">
                    <span class="font-semibold text-white mr-1">{{ $t('alerts.detail.created') }}:</span>
                    <span class="text-white">{{ alert.timestamp || alert.createTime || '-' }}</span>
                  </div>
                  <div class="h-4 w-px bg-border-dark/50"></div>
                  <div class="flex items-center gap-1.5">
                    <span class="font-semibold text-white mr-1">{{ $t('alerts.detail.responseTime') }}:</span>
                    <span class="text-white">{{ alert.responseTime || '2m 15s' }}</span>
                  </div>
                </div>
              </div>

              <!-- 标签页 -->
              <div class="border-b border-border-dark">
                <nav aria-label="Tabs" class="-mb-px flex space-x-6">
                  <button
                    v-for="tab in tabs"
                    :key="tab.key"
                    @click="activeTab = tab.key"
                    :class="[
                      'shrink-0 border-b-2 px-1 pb-3 text-sm font-medium transition-colors',
                      activeTab === tab.key
                        ? 'border-primary text-primary font-semibold'
                        : 'border-transparent text-text-light hover:border-text-dark hover:text-white'
                    ]"
                  >
                    {{ $t(tab.label) }}
                  </button>
                </nav>
              </div>

              <!-- 标签页内容 -->
              <div v-if="activeTab === 'overview'">
                <h3 class="text-lg font-semibold mb-3 text-white">{{ $t('alerts.detail.alertInfo') }}</h3>
                <div class="grid grid-cols-1 @lg:grid-cols-2 gap-x-6 gap-y-2 text-sm font-mono @container">
                  <div class="flex items-baseline">
                    <p class="text-text-light w-40 shrink-0">{{ $t('alerts.detail.timestamp') }}:</p>
                    <p class="font-medium text-white break-all">{{ alert?.timestamp || alert?.createTime || '-' }}</p>
                  </div>
                  <div class="flex items-baseline">
                    <p class="text-text-light w-40 shrink-0">{{ $t('alerts.detail.status') }}:</p>
                    <p class="font-medium text-white break-all">{{ $t(`alerts.list.${alert?.status}`) || '-' }}</p>
                  </div>
                  <div class="flex items-baseline">
                    <p class="text-text-light w-40 shrink-0">{{ $t('alerts.detail.ruleName') }}:</p>
                    <p class="font-medium text-white break-all">{{ alert?.ruleName || '-' }}</p>
                  </div>
                  <div class="flex items-baseline">
                    <p class="text-text-light w-40 shrink-0">{{ $t('alerts.detail.owner') }}:</p>
                    <p class="font-medium text-white break-all">{{ alert?.owner || $t('alerts.detail.unassigned') }}</p>
                  </div>
                  <div v-if="alert?.sourceIp" class="flex items-baseline">
                    <p class="text-text-light w-40 shrink-0">source.ip:</p>
                    <p class="font-medium text-white break-all">{{ alert.sourceIp }}</p>
                  </div>
                  <div v-if="alert?.destinationHostname" class="flex items-baseline">
                    <p class="text-text-light w-40 shrink-0">destination.hostname:</p>
                    <p class="font-medium text-white break-all">{{ alert.destinationHostname }}</p>
                  </div>
                  <div v-if="alert?.userName" class="flex items-baseline">
                    <p class="text-text-light w-40 shrink-0">user.name:</p>
                    <p class="font-medium text-white break-all">{{ alert.userName }}</p>
                  </div>
                </div>
                
                <!-- 分割线 -->
                <div class="mt-6 border-t border-border-dark"></div>

                <!-- 评论区域 -->
                <div class="pt-4">
                  <h3 class="text-lg font-semibold mb-4 text-white">{{ $t('alerts.detail.comments') }}</h3>
                  <div class="space-y-6">
                    <div
                      v-for="comment in alert?.comments || []"
                      :key="comment.id"
                      class="flex items-start gap-4"
                    >
                      <div
                        class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full"
                        :class="getAvatarColor(comment.authorInitials)"
                      >
                        <span class="font-bold text-white">{{ comment.authorInitials }}</span>
                      </div>
                      <div class="flex-1">
                        <div class="flex items-baseline gap-2">
                          <p class="font-semibold text-white">{{ comment.author }}</p>
                          <p class="text-xs text-text-light">{{ comment.time }}</p>
                        </div>
                        <div class="mt-1 text-sm text-[#c3d3e8] bg-[#2a3546] p-3 rounded-lg rounded-tl-none">
                          {{ comment.content }}
                          <!-- 显示附件 -->
                          <div v-if="comment.files && comment.files.length > 0" class="mt-3 flex flex-wrap gap-2">
                            <a
                              v-for="(file, fileIndex) in comment.files"
                              :key="fileIndex"
                              href="#"
                              class="inline-flex items-center gap-2 rounded-md bg-[#1e293b] border border-[#3c4a60] px-2.5 py-1.5 text-xs text-text-light hover:text-white hover:border-primary/50 transition-colors"
                            >
                              <span class="material-symbols-outlined text-primary text-sm">
                                {{ getFileIcon(file.type) }}
                              </span>
                              <span class="max-w-[150px] truncate">{{ file.name }}</span>
                              <span class="text-text-light/60">{{ formatFileSize(file.size) }}</span>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div v-if="!alert?.comments || alert.comments.length === 0" class="text-text-light text-sm">
                      {{ $t('common.noComments') || 'No comments yet' }}
                    </div>
                  </div>
                  
                  <!-- 评论输入框 -->
                  <div class="mt-6 pt-6 border-t border-border-dark">
                    <div class="flex items-start gap-4">
                      <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-blue-600 shadow-lg">
                        <span class="font-bold text-white text-sm">ME</span>
                      </div>
                      <div class="flex-1">
                        <!-- 输入框容器 -->
                        <div 
                          class="relative rounded-xl border-2 border-[#3c4a60] bg-[#1e293b] transition-all duration-200 focus-within:border-primary focus-within:shadow-lg focus-within:shadow-primary/20"
                          :class="{ 
                            'border-primary shadow-lg shadow-primary/20 drag-active': isDragging,
                            'border-primary/50': isDragging
                          }"
                          @drop.prevent="handleDrop"
                          @dragover.prevent="isDragging = true"
                          @dragleave.prevent="isDragging = false"
                        >
                          <textarea
                            v-model="newComment"
                            class="w-full rounded-xl bg-transparent p-4 pr-32 text-white placeholder:text-text-light/60 focus:outline-none text-sm resize-none min-h-[100px]"
                            :placeholder="$t('alerts.detail.addComment') || 'Add a comment...'"
                            rows="3"
                            @input="handleTextareaInput"
                          ></textarea>
                          
                          <!-- 工具栏 -->
                          <div class="absolute bottom-3 left-4 flex items-center gap-2">
                            <!-- 文件上传按钮 -->
                            <label class="cursor-pointer">
                              <input
                                ref="fileInput"
                                type="file"
                                multiple
                                class="hidden"
                                @change="handleFileSelect"
                              />
                              <button
                                type="button"
                                class="flex items-center justify-center w-8 h-8 rounded-lg bg-[#2a3546] hover:bg-[#3c4a60] text-text-light hover:text-white transition-all duration-200 group"
                                title="Upload file"
                              >
                                <span class="material-symbols-outlined text-lg">attach_file</span>
                              </button>
                            </label>
                            
                            <!-- 表情按钮（可选） -->
                            <button
                              type="button"
                              class="flex items-center justify-center w-8 h-8 rounded-lg bg-[#2a3546] hover:bg-[#3c4a60] text-text-light hover:text-white transition-all duration-200"
                              title="Add emoji"
                            >
                              <span class="material-symbols-outlined text-lg">mood</span>
                            </button>
                          </div>
                          
                          <!-- 提交按钮 -->
                          <button
                            @click="handleAddComment"
                            :disabled="!canSubmit"
                            class="absolute bottom-3 right-3 flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-primary to-blue-600 px-4 py-2 text-xs font-semibold text-white transition-all duration-200 hover:from-blue-500 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl disabled:shadow-none"
                          >
                            <span class="material-symbols-outlined text-base">send</span>
                            <span>{{ $t('common.submit') || 'Send' }}</span>
                          </button>
                        </div>
                        
                        <!-- 已上传文件列表 -->
                        <div v-if="uploadedFiles.length > 0" class="mt-3 flex flex-wrap gap-2">
                          <div
                            v-for="(file, index) in uploadedFiles"
                            :key="index"
                            class="group relative flex items-center gap-2 rounded-lg bg-[#2a3546] border border-[#3c4a60] px-3 py-2 hover:bg-[#3c4a60] transition-colors"
                          >
                            <span class="material-symbols-outlined text-primary text-sm">
                              {{ getFileIcon(file.type) }}
                            </span>
                            <span class="text-sm text-white max-w-[200px] truncate">{{ file.name }}</span>
                            <span class="text-xs text-text-light">{{ formatFileSize(file.size) }}</span>
                            <button
                              @click="removeFile(index)"
                              class="ml-1 flex items-center justify-center w-5 h-5 rounded-full bg-red-500/20 hover:bg-red-500/30 text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                              <span class="material-symbols-outlined text-xs">close</span>
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 分割线 -->
                  <div class="mt-6 border-t border-border-dark"></div>
                </div>
              </div>

              <!-- 关联告警标签页 -->
              <div v-if="activeTab === 'associatedAlerts'">

                <div v-if="loadingAssociatedAlerts" class="flex items-center justify-center py-12">
                  <div class="text-text-light text-sm">加载中...</div>
                </div>
                
                <div v-else-if="associatedAlerts.length === 0" class="text-text-light text-sm py-12 text-center">
                  {{ $t('alerts.detail.noAssociatedAlerts') || '暂无关联告警' }}
                </div>
                
                <div v-else class="grid grid-cols-1 @lg:grid-cols-2 gap-4">
                  <div
                    v-for="associatedAlert in associatedAlerts"
                    :key="associatedAlert.id"
                    @click="openAssociatedAlert(associatedAlert.id)"
                    class="rounded-lg border border-border-dark bg-[#1f2937]/30 p-4 transition-all hover:border-primary/50 hover:bg-[#1f2937]/60 cursor-pointer"
                  >
                    <div class="flex items-start justify-between">
                      <h4 class="text-base font-semibold text-white">{{ associatedAlert.title }}</h4>
                    </div>
                    <p class="mt-2 text-sm text-text-light">{{ associatedAlert.description }}</p>
                    <div class="mt-4 flex items-center justify-between text-xs text-text-light">
                      <div class="flex items-center gap-1.5">
                        <span class="material-symbols-outlined text-base">person</span>
                        <span>{{ associatedAlert.owner || $t('alerts.detail.unassigned') }}</span>
                      </div>
                      <div class="flex items-center gap-1.5">
                        <span class="material-symbols-outlined text-base">schedule</span>
                        <span>{{ associatedAlert.createTime }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 威胁情报标签页 -->
              <div v-if="activeTab === 'threatIntelligence'">

                
                <div v-if="loadingThreatIntel" class="flex items-center justify-center py-12">
                  <div class="text-text-light text-sm">加载中...</div>
                </div>
                
                <div v-else-if="threatIntelligence.length === 0" class="text-text-light text-sm py-12 text-center">
                  {{ $t('alerts.detail.noThreatIntelligence') || '暂无威胁情报匹配' }}
                </div>
                
                <div v-else class="grid grid-cols-1 @lg:grid-cols-2 gap-4">
                  <div
                    v-for="item in threatIntelligence"
                    :key="item.id"
                    class="rounded-lg border border-border-dark bg-[#1f2937]/30 p-4 transition-all hover:border-primary/50 hover:bg-[#1f2937]/60"
                  >
                    <div class="flex items-start justify-between">
                      <h4 class="text-base font-semibold text-white">{{ item.title }}</h4>
                    </div>
                    <p class="mt-2 text-sm text-text-light">{{ item.description }}</p>
                    <div class="mt-4 flex items-center justify-between text-xs text-text-light">
                      <div class="flex items-center gap-1.5">
                        <span class="material-symbols-outlined text-base">person</span>
                        <span>{{ item.source }}</span>
                      </div>
                      <div class="flex items-center gap-1.5">
                        <span class="material-symbols-outlined text-base">schedule</span>
                        <span>{{ item.timestamp }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="activeTab === 'aiAgent'">
                <h3 class="text-lg font-semibold mb-4 text-white">{{ $t('alerts.detail.aiAgent') }}</h3>
                <div class="space-y-6">
                  <div
                    v-for="comment in alert?.comments || []"
                    :key="comment.id"
                    class="flex items-start gap-4"
                  >
                    <div
                      class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full"
                      :class="getAvatarColor(comment.authorInitials)"
                    >
                      <span class="font-bold text-white">{{ comment.authorInitials }}</span>
                    </div>
                    <div class="flex-1">
                      <div class="flex items-baseline gap-2">
                        <p class="font-semibold text-white">{{ comment.author }}</p>
                        <p class="text-xs text-text-light">{{ comment.time }}</p>
                      </div>
                      <div class="mt-1 text-sm text-[#c3d3e8] bg-[#2a3546] p-3 rounded-lg rounded-tl-none">
                        {{ comment.content }}
                        <!-- 显示附件 -->
                        <div v-if="comment.files && comment.files.length > 0" class="mt-3 flex flex-wrap gap-2">
                          <a
                            v-for="(file, fileIndex) in comment.files"
                            :key="fileIndex"
                            href="#"
                            class="inline-flex items-center gap-2 rounded-md bg-[#1e293b] border border-[#3c4a60] px-2.5 py-1.5 text-xs text-text-light hover:text-white hover:border-primary/50 transition-colors"
                          >
                            <span class="material-symbols-outlined text-primary text-sm">
                              {{ getFileIcon(file.type) }}
                            </span>
                            <span class="max-w-[150px] truncate">{{ file.name }}</span>
                            <span class="text-text-light/60">{{ formatFileSize(file.size) }}</span>
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-if="!alert?.comments || alert.comments.length === 0" class="text-text-light text-sm">
                    {{ $t('common.noComments') || 'No comments yet' }}
                  </div>
                </div>
                
                <!-- AI 对话输入框 -->
                <div class="mt-6 pt-6 border-t border-border-dark">
                  <div class="flex items-start gap-4">
                    <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-blue-600 shadow-lg">
                      <span class="font-bold text-white text-sm">ME</span>
                    </div>
                    <div class="flex-1">
                      <!-- 输入框容器 -->
                      <div 
                        class="relative rounded-xl border-2 border-[#3c4a60] bg-[#1e293b] transition-all duration-200 focus-within:border-primary focus-within:shadow-lg focus-within:shadow-primary/20"
                        :class="{ 
                          'border-primary shadow-lg shadow-primary/20 drag-active': isAiDragging,
                          'border-primary/50': isAiDragging
                        }"
                        @drop.prevent="handleAiDrop"
                        @dragover.prevent="isAiDragging = true"
                        @dragleave.prevent="isAiDragging = false"
                      >
                        <textarea
                          v-model="newAiMessage"
                          class="w-full rounded-xl bg-transparent p-4 pr-32 text-white placeholder:text-text-light/60 focus:outline-none text-sm resize-none min-h-[100px]"
                          :placeholder="$t('alerts.detail.aiAgentPlaceholder') || 'Ask AI about this alert...'"
                          rows="3"
                          @input="handleAiMessageInput"
                        ></textarea>
                        
                        <!-- 工具栏 -->
                        <div class="absolute bottom-3 left-4 flex items-center gap-2">
                          <!-- 文件上传按钮 -->
                          <label class="cursor-pointer">
                            <input
                              ref="aiFileInput"
                              type="file"
                              multiple
                              class="hidden"
                              @change="handleAiFileSelect"
                            />
                            <button
                              type="button"
                              class="flex items-center justify-center w-8 h-8 rounded-lg bg-[#2a3546] hover:bg-[#3c4a60] text-text-light hover:text-white transition-all duration-200 group"
                              title="Upload file"
                            >
                              <span class="material-symbols-outlined text-lg">attach_file</span>
                            </button>
                          </label>
                          
                          <!-- 表情按钮（可选） -->
                          <button
                            type="button"
                            class="flex items-center justify-center w-8 h-8 rounded-lg bg-[#2a3546] hover:bg-[#3c4a60] text-text-light hover:text-white transition-all duration-200"
                            title="Add emoji"
                          >
                            <span class="material-symbols-outlined text-lg">mood</span>
                          </button>
                        </div>
                        
                        <!-- 提交按钮 -->
                        <button
                          @click="handleSendAiMessage"
                          :disabled="!canSubmitAiMessage"
                          class="absolute bottom-3 right-3 flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-primary to-blue-600 px-4 py-2 text-xs font-semibold text-white transition-all duration-200 hover:from-blue-500 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl disabled:shadow-none"
                        >
                          <span class="material-symbols-outlined text-base">send</span>
                          <span>{{ $t('common.submit') || 'Send' }}</span>
                        </button>
                      </div>
                      
                      <!-- 已上传文件列表 -->
                      <div v-if="uploadedAiFiles.length > 0" class="mt-3 flex flex-wrap gap-2">
                        <div
                          v-for="(file, index) in uploadedAiFiles"
                          :key="index"
                          class="group relative flex items-center gap-2 rounded-lg bg-[#2a3546] border border-[#3c4a60] px-3 py-2 hover:bg-[#3c4a60] transition-colors"
                        >
                          <span class="material-symbols-outlined text-primary text-sm">
                            {{ getFileIcon(file.type) }}
                          </span>
                          <span class="text-xs text-text-light max-w-[200px] truncate">{{ file.name }}</span>
                          <span class="text-xs text-text-light/60">{{ formatFileSize(file.size) }}</span>
                          <button
                            @click="removeAiFile(index)"
                            class="ml-2 flex items-center justify-center w-5 h-5 rounded-full bg-[#1e293b] hover:bg-red-500/20 text-text-light hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                            title="Remove file"
                          >
                            <span class="material-symbols-outlined text-sm">close</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </main>

            <!-- 侧边栏 -->
            <aside class="w-80 border-l border-border-dark p-6 space-y-8 bg-[#1f2937]/20 overflow-y-auto custom-scrollbar">
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
                    <div class="text-sm">
                      <p class="font-medium text-white">{{ entity.name }}</p>
                      <p class="text-text-light">{{ entity.label }}</p>
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
            <option value="convertedToIncident">{{ $t('alerts.list.batchCloseDialog.categories.convertedToIncident') }}</option>
            <option value="other">{{ $t('alerts.list.batchCloseDialog.categories.other') }}</option>
          </select>
        </div>

        <!-- 调查结论输入框 -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-white mb-2">
            {{ $t('alerts.list.batchCloseDialog.conclusion') }}
          </label>
          <textarea
            v-model="closeConclusion.notes"
            rows="4"
            class="w-full bg-[#1e293b] text-white border border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary resize-none"
            :placeholder="$t('alerts.list.batchCloseDialog.conclusionPlaceholder')"
          ></textarea>
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
            :disabled="!closeConclusion.category || !closeConclusion.notes.trim()"
            class="px-4 py-2 text-sm text-white bg-primary rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ $t('common.submit') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 创建事件对话框 -->
    <CreateIncidentDialog
      :visible="showCreateIncidentDialog"
      :initial-data="createIncidentInitialData"
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
import { getAlertDetail, batchCloseAlerts, openAlert, getThreatIntelligence, getAssociatedAlerts } from '@/api/alerts'
import CreateIncidentDialog from '@/components/incidents/CreateIncidentDialog.vue'
import EditAlertDialog from '@/components/alerts/EditAlertDialog.vue'
import AssociateIncidentDialog from '@/components/alerts/AssociateIncidentDialog.vue'

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

const visible = ref(false)
const alert = ref(null)

// 获取告警ID：优先使用props，如果没有则从路由参数获取
const currentAlertId = computed(() => {
  return props.alertId || route.params.id
})
const activeTab = ref('overview')
const newComment = ref('')
const uploadedFiles = ref([])
const fileInput = ref(null)
const isDragging = ref(false)
// AI 对话相关
const newAiMessage = ref('')
const uploadedAiFiles = ref([])
const aiFileInput = ref(null)
const isAiDragging = ref(false)
const showBatchCloseDialog = ref(false)
const closeConclusion = ref({
  category: '',
  notes: ''
})
const showCreateIncidentDialog = ref(false)
const createIncidentInitialData = ref(null)
const showEditAlertDialog = ref(false)
const editAlertInitialData = ref(null)
const showShareSuccess = ref(false)
const threatIntelligence = ref([])
const associatedAlerts = ref([])
const loadingThreatIntel = ref(false)
const loadingAssociatedAlerts = ref(false)
const showAssociateIncidentDialog = ref(false)
const showMoreActionsMenu = ref(false)

const tabs = [
  { key: 'overview', label: 'alerts.detail.overview' },
  { key: 'associatedAlerts', label: 'alerts.detail.associatedAlerts' },
  { key: 'threatIntelligence', label: 'alerts.detail.threatIntelligence' },
  { key: 'aiAgent', label: 'alerts.detail.aiAgent' }
]

/**
 * @brief 加载告警详情
 * @details 从API获取告警详细信息并显示
 */
const loadAlertDetail = async () => {
  if (!currentAlertId.value) return
  
  try {
    const response = await getAlertDetail(currentAlertId.value)
    alert.value = response.data
    // 延迟显示以触发动画
    setTimeout(() => {
      visible.value = true
    }, 10)
    // 加载威胁情报和关联告警
    loadThreatIntelligence()
    loadAssociatedAlerts()
  } catch (error) {
    console.error('Failed to load alert detail:', error)
    // 如果是从路由访问，跳转回告警列表
    if (route.params.id) {
      router.push('/alerts')
    } else {
      emit('close')
    }
  }
}

/**
 * @brief 加载威胁情报数据
 * @details 从API获取当前告警的威胁情报匹配信息
 */
const loadThreatIntelligence = async () => {
  if (!currentAlertId.value) return
  
  loadingThreatIntel.value = true
  try {
    const response = await getThreatIntelligence(currentAlertId.value)
    threatIntelligence.value = response.data || []
  } catch (error) {
    console.error('Failed to load threat intelligence:', error)
    threatIntelligence.value = []
  } finally {
    loadingThreatIntel.value = false
  }
}

/**
 * @brief 加载关联告警数据
 * @details 从API获取与当前告警相关的其他告警列表
 */
const loadAssociatedAlerts = async () => {
  if (!currentAlertId.value) return
  
  loadingAssociatedAlerts.value = true
  try {
    const response = await getAssociatedAlerts(currentAlertId.value)
    associatedAlerts.value = response.data || []
  } catch (error) {
    console.error('Failed to load associated alerts:', error)
    associatedAlerts.value = []
  } finally {
    loadingAssociatedAlerts.value = false
  }
}

/**
 * @brief 打开关联告警详情
 * @param {number} alertId - 告警ID
 * @details 当用户点击关联告警时，打开该告警的详情页面。通过更新路由来触发父组件重新加载告警详情。
 */
const openAssociatedAlert = (alertId) => {
  // 关闭当前详情面板
  handleClose()
  // 延迟更新路由，确保关闭动画完成后再打开新的详情
  setTimeout(() => {
    router.push(`/alerts/${alertId}`)
  }, 300)
}

const handleClose = () => {
  visible.value = false
  setTimeout(() => {
    // 如果是从路由访问，跳转回告警列表
    if (route.params.id) {
      router.push('/alerts')
    } else {
      emit('close')
    }
  }, 300)
}

const openBatchCloseDialog = () => {
  if (!canCloseAlert.value) {
    return
  }
  showBatchCloseDialog.value = true
}

const closeBatchCloseDialog = () => {
  showBatchCloseDialog.value = false
  // 重置表单
  closeConclusion.value = {
    category: '',
    notes: ''
  }
}

const handleBatchClose = async () => {
  if (!closeConclusion.value.category || !closeConclusion.value.notes.trim()) {
    return
  }

  try {
    await batchCloseAlerts({
      alertIds: [props.alertId],
      category: closeConclusion.value.category,
      notes: closeConclusion.value.notes.trim()
    })
    
    // 关闭对话框并重置表单
    closeBatchCloseDialog()
    
    // 关闭详情面板
    handleClose()
    
    // 触发刷新事件，让父组件知道需要刷新列表
    emit('closed')
  } catch (error) {
    console.error('Failed to close alert:', error)
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

const closeAssociateIncidentDialog = () => {
  showAssociateIncidentDialog.value = false
}

const handleAssociateIncidentSuccess = async () => {
  // 关联成功后，关闭对话框并重新加载详情
  closeAssociateIncidentDialog()
  await loadAlertDetail()
  // 触发刷新事件，让父组件知道需要刷新列表
  emit('closed')
}

const canSubmit = computed(() => {
  return newComment.value.trim().length > 0 || uploadedFiles.value.length > 0
})

const handleTextareaInput = () => {
  // 可以在这里添加自动调整高度的逻辑
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files || [])
  addFiles(files)
  // 清空input，以便可以再次选择相同文件
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  const files = Array.from(event.dataTransfer.files || [])
  addFiles(files)
}

const addFiles = (files) => {
  files.forEach(file => {
    // 检查文件大小（限制为10MB）
    if (file.size > 10 * 1024 * 1024) {
      console.warn(`File ${file.name} is too large (max 10MB)`)
      return
    }
    // 检查是否已存在
    if (!uploadedFiles.value.find(f => f.name === file.name && f.size === file.size)) {
      uploadedFiles.value.push(file)
    }
  })
}

const removeFile = (index) => {
  uploadedFiles.value.splice(index, 1)
}

const getFileIcon = (mimeType) => {
  if (!mimeType) return 'description'
  if (mimeType.startsWith('image/')) return 'image'
  if (mimeType.startsWith('video/')) return 'video_file'
  if (mimeType.startsWith('audio/')) return 'audio_file'
  if (mimeType.includes('pdf')) return 'picture_as_pdf'
  if (mimeType.includes('word') || mimeType.includes('document')) return 'description'
  if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return 'table_chart'
  if (mimeType.includes('zip') || mimeType.includes('archive')) return 'folder_zip'
  return 'attach_file'
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const handleAddComment = () => {
  if (!canSubmit.value) return
  
  // TODO: 实现添加评论的逻辑，包含文件上传
  if (!alert.value.comments) {
    alert.value.comments = []
  }
  
  const commentData = {
    id: Date.now(),
    author: 'Current User',
    authorInitials: 'CU',
    time: 'Just now',
    content: newComment.value,
    files: uploadedFiles.value.map(file => ({
      name: file.name,
      size: file.size,
      type: file.type
    }))
  }
  
  alert.value.comments.unshift(commentData)
  
  // 清空输入
  newComment.value = ''
  uploadedFiles.value = []
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

const getSeverityClass = (severity) => {
  const classes = {
    high: 'bg-red-500/10 text-red-400',
    medium: 'bg-orange-500/10 text-orange-400',
    low: 'bg-blue-500/10 text-blue-400'
  }
  return classes[severity] || classes.low
}

const getStatusBadgeClass = (status) => {
  const classes = {
    open: 'bg-yellow-400/10 text-yellow-500 ring-yellow-400/20',
    pending: 'bg-orange-400/10 text-orange-500 ring-orange-400/20',
    closed: 'bg-gray-400/10 text-gray-500 ring-gray-400/20'
  }
  return classes[status] || classes.open
}

const getAvatarColor = (initials) => {
  const colors = ['bg-slate-500', 'bg-purple-500', 'bg-blue-500', 'bg-green-500']
  const index = initials.charCodeAt(0) % colors.length
  return colors[index]
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
 * @param {string} level - 风险等级（high/medium/low）
 * @returns {string} 返回对应的CSS类名
 */
const getRiskLevelClass = (level) => {
  const classes = {
    high: 'bg-red-900 text-red-300',
    medium: 'bg-orange-900 text-orange-300',
    low: 'bg-blue-900 text-blue-300'
  }
  return classes[level] || classes.low
}

/**
 * @brief 获取状态样式类
 * @param {string} status - 状态（open/pending/closed）
 * @returns {string} 返回对应的CSS类名
 */
const getStatusClass = (status) => {
  const classes = {
    open: 'bg-primary/20 text-primary',
    pending: 'bg-orange-500/20 text-orange-400',
    closed: 'bg-gray-500/20 text-gray-400'
  }
  return classes[status] || classes.open
}

/**
 * @brief 获取状态点样式类
 * @param {string} status - 状态（open/pending/closed）
 * @returns {string} 返回对应的CSS类名
 */
const getStatusDotClass = (status) => {
  const classes = {
    open: 'bg-primary',
    pending: 'bg-orange-400',
    closed: 'bg-gray-400'
  }
  return classes[status] || classes.open
}

// 生成告警URL
const getAlertUrl = () => {
  const baseUrl = window.location.origin
  return `${baseUrl}/alerts/${currentAlertId.value}`
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

// 监听告警ID变化（包括props和路由参数）
watch([() => props.alertId, () => route.params.id], () => {
  if (currentAlertId.value) {
    loadAlertDetail()
  }
}, { immediate: true })

// 监听标签页切换，按需加载数据
watch(activeTab, (newTab) => {
  if (newTab === 'threatIntelligence' && threatIntelligence.value.length === 0 && !loadingThreatIntel.value) {
    loadThreatIntelligence()
  } else if (newTab === 'associatedAlerts' && associatedAlerts.value.length === 0 && !loadingAssociatedAlerts.value) {
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
</style>

