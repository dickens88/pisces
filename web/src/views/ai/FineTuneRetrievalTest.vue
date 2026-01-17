<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-end bg-black/50 dark:bg-black/70 backdrop-blur-sm transition-opacity"
      @click.self="$emit('update:modelValue', false)"
    >
      <!-- Detail panel - with slide-in animation -->
      <Transition name="slide" appear>
        <div
          v-if="modelValue"
          class="relative w-[80vw] h-full bg-white dark:bg-panel-dark shadow-2xl flex flex-col overflow-hidden"
          @click.stop
        >
          <!-- Header -->
          <div class="sticky top-0 z-20 bg-white/80 dark:bg-panel-dark/80 backdrop-blur-sm border-b border-gray-200 dark:border-border-dark">
            <div class="flex items-center justify-between px-6 py-4">
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <span class="material-symbols-outlined text-base">tune</span>
                  {{ $t('aiPlayground.fineTuneAI') }}
                </h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ $t('aiPlayground.fineTuneSubtitle') || 'Train and debug AI models' }}</p>
              </div>
              <div class="flex items-center gap-2">
                <button
                  class="p-2 text-gray-500 dark:text-text-light hover:text-gray-900 dark:hover:text-white transition-colors"
                  @click="loadAllFinetuneRecords()"
                  :disabled="loadingFinetuneRecords"
                  aria-label="Refresh"
                  :title="$t('common.refresh') || 'Refresh'"
                >
                  <span 
                    class="material-symbols-outlined"
                    :class="{ 'animate-spin': loadingFinetuneRecords }"
                  >
                    refresh
                  </span>
                </button>
                <button
                  class="p-2 text-gray-500 dark:text-text-light hover:text-gray-900 dark:hover:text-white transition-colors"
                  @click="$emit('update:modelValue', false)"
                  aria-label="Close"
                >
                  <span class="material-symbols-outlined">close</span>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Content -->
          <div class="flex-1 p-6 min-h-0 overflow-hidden flex flex-col">
            <div class="flex-1 flex gap-6 min-h-0">
              <!-- Left Panel: All Selected Alerts with Workflow Selectors -->
              <div class="w-full lg:w-[36%] flex flex-col min-h-0">
                <h4 class="text-base font-semibold text-gray-900 dark:text-white mb-4">{{ $t('aiPlayground.retrievalTest.selectdAlertInfo') || 'Selected Alerts' }}</h4>
                
                <!-- Combined Execute/Cancel Button -->
                <button
                  type="button"
                  @click="runningWorkflow ? handleCancelWorkflows() : handleRunAllWorkflows()"
                  :disabled="!runningWorkflow && (!canRunAllWorkflows || runningWorkflow)"
                  :class="[
                    'w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold transition-colors mb-4',
                    runningWorkflow 
                      ? 'bg-gray-200 dark:bg-[#2a3546] text-gray-700 dark:text-white hover:bg-gray-300 dark:hover:bg-[#3c4a60]' 
                      : 'bg-primary text-white hover:bg-primary/90 disabled:opacity-60 disabled:cursor-not-allowed'
                  ]"
                >
                  <span
                    v-if="runningWorkflow"
                    class="material-symbols-outlined text-base"
                  >
                    cancel
                  </span>
                  <span
                    v-else
                    class="material-symbols-outlined text-base"
                  >
                    play_arrow
                  </span>
                  {{ runningWorkflow 
                    ? ($t('aiPlayground.retrievalTest.cancelRun') || 'Cancel') 
                    : ($t('aiPlayground.retrievalTest.runAnalysis') || 'Run Analysis') 
                  }}
                </button>
                
                <div class="flex-1 overflow-y-auto custom-scrollbar min-h-0 space-y-4">
                  <template v-for="alertData in selectedAlertsData" :key="`finetune-${getAlertId(alertData?.alert) || alertData?.alertId || 'unknown'}`">
                    <div
                      v-if="alertData && alertData.alert && (getAlertId(alertData.alert) || alertData.alertId)"
                      :class="[
                        'bg-gray-50 dark:bg-[#1c2533] border border-gray-200 dark:border-[#324867] rounded-lg overflow-hidden transition-colors'
                      ]"
                    >
                    <!-- Alert Drawer Header (clickable to expand/collapse) -->
                    <div 
                      class="p-4 cursor-pointer hover:bg-gray-100 dark:hover:bg-[#192233] transition-colors"
                      @click="toggleFinetuneAlertDrawer(getAlertId(alertData?.alert) || alertData?.alertId)"
                    >
                      <div class="flex items-center justify-between gap-3 mb-3">
                        <div class="flex-1 min-w-0">
                          <h5 class="text-sm font-semibold text-gray-900 dark:text-white truncate">
                            {{ $t('alerts.detail.title') }} #{{ getAlertId(alertData?.alert) || alertData?.alertId }}
                          </h5>
                          <p class="text-xs text-gray-600 dark:text-gray-400 truncate mt-0.5">
                            {{ alertData?.alert?.title || '' }}
                          </p>
                        </div>
                        <div class="flex items-center gap-2 flex-shrink-0">
                          <!-- Remove from selection button (fine-tune overlay) -->
                          <button
                            @click.stop="$emit('remove-alert', getAlertId(alertData?.alert) || alertData?.alertId)"
                            class="p-1 rounded-full hover:bg-gray-200 dark:hover:bg-[#1c2533] text-gray-400 hover:text-gray-700 dark:hover:text-white transition-colors"
                            :aria-label="$t('common.delete') || 'Remove from selection'"
                          >
                            <span class="material-symbols-outlined text-sm">delete</span>
                          </button>
                          <span
                            class="material-symbols-outlined text-gray-400 dark:text-gray-500 transition-transform flex-shrink-0"
                            :class="alertData.finetuneExpanded ? 'rotate-180' : ''"
                          >
                            expand_more
                          </span>
                        </div>
                      </div>
                      
                      <!-- Workflow Selection -->
                      <div class="flex flex-col gap-2" @click.stop>
                        <label class="text-xs font-semibold text-gray-700 dark:text-gray-300">{{ $t('aiPlayground.retrievalTest.workflowSelection') || 'Workflow Selection' }}</label>
                        <div class="flex items-center gap-2">
                          <div class="relative flex-1">
                            <select
                              v-model="finetuneWorkflowSelections[getAlertId(alertData?.alert) || alertData?.alertId]"
                              :disabled="loadingWorkflows"
                              :class="[
                                'pl-3 pr-8 appearance-none block w-full rounded-lg border h-9 text-xs text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary disabled:opacity-60 disabled:cursor-not-allowed transition-colors',
                                finetuneWorkflowSelections[getAlertId(alertData?.alert) || alertData?.alertId] 
                                  ? 'border-gray-200 dark:border-[#324867] bg-white dark:bg-[#1c2533]' 
                                  : 'border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20'
                              ]"
                            >
                              <option value="">{{ $t('aiPlayground.retrievalTest.selectWorkflow') }}</option>
                              <option v-if="loadingWorkflows" value="__loading__" disabled>{{ $t('common.loading') }}</option>
                              <option
                                v-for="workflow in workflows"
                                :key="workflow.id"
                                :value="workflow.id"
                              >
                                {{ workflow.name }}
                              </option>
                            </select>
                            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500 dark:text-gray-400">
                              <span
                                v-if="loadingWorkflows"
                                class="material-symbols-outlined animate-spin text-sm"
                              >
                                sync
                              </span>
                              <span
                                v-else
                                class="material-symbols-outlined text-sm"
                              >
                                arrow_drop_down
                              </span>
                            </div>
                          </div>
                          <!-- Dify logo and link -->
                          <a
                            v-if="getWorkflowUrlForAlert(getAlertId(alertData?.alert) || alertData?.alertId)"
                            :href="getWorkflowUrlForAlert(getAlertId(alertData?.alert) || alertData?.alertId)"
                            target="_blank"
                            rel="noopener noreferrer"
                            class="flex items-center justify-center w-9 h-9 rounded-lg border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#1c2533] hover:bg-gray-50 dark:hover:bg-[#192233] transition-colors flex-shrink-0"
                            :title="getWorkflowNameForAlert(getAlertId(alertData?.alert) || alertData?.alertId)"
                            @click.stop
                          >
                            <img src="/dify-logo.png" alt="Dify" class="w-4 h-4" />
                          </a>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Alert Details (expandable) -->
                    <div v-if="alertData.finetuneExpanded" class="border-t border-gray-200 dark:border-[#324867] p-4 space-y-3">
                      <!-- Alert ID -->
                      <div class="flex flex-col gap-1.5">
                        <label class="text-xs font-medium text-gray-600 dark:text-gray-400">{{ $t('alerts.detail.id') }}</label>
                        <input
                          type="text"
                          class="w-full rounded-lg border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#1c2533] text-xs text-gray-900 dark:text-white px-2.5 py-1.5"
                          :value="getAlertId(alertData?.alert) || alertData?.alertId || ''"
                          readonly
                        />
                      </div>

                      <!-- Title -->
                      <div class="flex flex-col gap-1.5">
                        <label class="text-xs font-medium text-gray-600 dark:text-gray-400">{{ $t('alerts.list.alertTitle') }}</label>
                        <textarea
                          class="w-full rounded-lg border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#1c2533] text-xs text-gray-900 dark:text-white px-2.5 py-1.5 resize-none overflow-y-auto min-h-[60px]"
                          :value="alertData.alert?.title || ''"
                          readonly
                        ></textarea>
                      </div>

                      <!-- Close Comment -->
                      <div class="flex flex-col gap-1.5">
                        <label class="text-xs font-medium text-gray-600 dark:text-gray-400">{{ $t('aiPlayground.retrievalTest.comments') || 'Close Comment' }}</label>
                        <textarea
                          class="w-full rounded-lg border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#1c2533] text-xs text-gray-900 dark:text-white p-2 resize-none min-h-[60px]"
                          :value="alertData.alert?.close_comment || ''"
                          readonly
                        ></textarea>
                      </div>

                      <!-- Description -->
                      <div class="flex flex-col gap-1.5">
                        <label class="text-xs font-medium text-gray-600 dark:text-gray-400">{{ $t('alerts.detail.alertContent') }}</label>
                        <div class="flex gap-2 mb-1.5">
                          <button
                            @click="contentFormatMode = 'json'"
                            :class="[
                              'px-2 py-1 text-xs font-medium rounded-md transition-colors',
                              contentFormatMode === 'json'
                                ? 'bg-primary text-white'
                                : 'bg-gray-100 dark:bg-[#233348] text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-[#324867]'
                            ]"
                          >
                            Raw JSON
                          </button>
                          <button
                            @click="contentFormatMode = 'richtext'"
                            :class="[
                              'px-2 py-1 text-xs font-medium rounded-md transition-colors',
                              contentFormatMode === 'richtext'
                                ? 'bg-primary text-white'
                                : 'bg-gray-100 dark:bg-[#233348] text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-[#324867]'
                            ]"
                          >
                            Rendered View
                          </button>
                        </div>
                        <textarea
                          :class="[
                            'w-full rounded-lg border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#1c2533] text-xs text-gray-900 dark:text-white p-2 resize-none overflow-y-auto h-[200px]',
                            contentFormatMode === 'json' ? 'font-mono' : ''
                          ]"
                          :value="getFormattedContentForAlert(alertData)"
                          readonly
                        ></textarea>
                      </div>
                    </div>
                  </div>
                  </template>
                </div>
              </div>

              <!-- Right Panel: AI Agent Workspace -->
              <div class="w-full lg:w-[64%] flex flex-col min-h-0">
                <!-- Fine-tune Records Table -->
                <div class="flex flex-col gap-2 mb-4">
                  <h4 class="text-sm font-semibold text-gray-900 dark:text-white">{{ $t('aiPlayground.retrievalTest.retrievalTestRecords') || 'Retrieval Test Records' }}</h4>
                  <div class="border border-gray-200 dark:border-[#324867] rounded-lg overflow-hidden bg-white dark:bg-[#1c2533]">
                    <div v-if="loadingFinetuneRecords" class="p-8 text-center text-gray-500 dark:text-gray-400 text-sm">
                      <span class="material-symbols-outlined animate-spin text-base inline-block mr-2">sync</span>
                      {{ $t('common.loading') || 'Loading...' }}
                    </div>
                    <div v-else-if="allFinetuneRecords.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400 text-sm">
                      {{ $t('aiPlayground.retrievalTest.noFinetuneRecords') || 'No fine-tune records found.' }}
                    </div>
                    <div v-else class="overflow-x-auto">
                      <table class="w-full text-xs">
                        <thead class="bg-gray-50 dark:bg-[#192233] border-b border-gray-200 dark:border-[#324867]">
                          <tr>
                            <th class="px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-300">{{ $t('aiPlayground.retrievalTest.updatedAt') || 'Updated At' }}</th>
                            <th class="px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-300">{{ $t('aiPlayground.retrievalTest.isThreat') || 'Is Threat' }}</th>
                            <th class="px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-300">{{ $t('aiPlayground.retrievalTest.confidenceScore') || 'Confidence Score' }}</th>
                            <th class="px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-300">{{ $t('aiPlayground.retrievalTest.agentName') || 'Agent Name' }}</th>
                            <th class="px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-300">{{ $t('aiPlayground.retrievalTest.updatedBy') || 'Updated By' }}</th>
                            <th class="px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-300">{{ $t('alerts.list.alertTitle') || 'Alert Title' }}</th>
                          </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200 dark:divide-[#324867]">
                          <tr
                            v-for="(record, index) in allFinetuneRecords"
                            :key="`record-${record.id || index}`"
                            class="hover:bg-gray-50 dark:hover:bg-[#192233] transition-colors"
                          >
                            <td class="px-4 py-2 text-gray-900 dark:text-white whitespace-nowrap">
                              {{ formatDateTime(record.updated_at) }}
                            </td>
                            <td class="px-4 py-2 text-gray-900 dark:text-white">
                              {{ record.is_threat || '-' }}
                            </td>
                            <td class="px-4 py-2 text-gray-900 dark:text-white">
                              {{ record.confidence_score || '-' }}
                            </td>
                            <td class="px-4 py-2 text-gray-900 dark:text-white">
                              {{ record.agent_name || '-' }}
                            </td>
                            <td class="px-4 py-2 text-gray-900 dark:text-white">
                              {{ record.updated_by || '-' }}
                            </td>
                            <td class="px-4 py-2 text-gray-900 dark:text-white max-w-xs truncate" :title="record.alert_title || ''">
                              {{ record.alert_title || '-' }}
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
                
                <div class="flex-1 flex flex-col gap-4 overflow-y-auto custom-scrollbar min-h-0">
                  <!-- Workflow Results Feed -->
                  <div class="flex flex-col gap-2">
                    <h5 class="text-sm font-semibold text-gray-900 dark:text-white">{{ $t('aiPlayground.retrievalTest.aiResponseFeed') || 'AI Response Details' }}</h5>
                    <div class="flex-1 overflow-y-auto space-y-3">
                      <div v-if="!runningWorkflow && Object.keys(finetuneWorkflowResults).length === 0 && selectedAlertsData.length > 0" class="text-center text-gray-500 dark:text-gray-400 text-sm py-8">
                        {{ $t('aiPlayground.retrievalTest.noResult') || 'No workflow result yet. Run workflows to see the output.' }}
                      </div>

                      <template
                        v-for="alertData in selectedAlertsData"
                        :key="`result-${getAlertId(alertData?.alert) || alertData?.alertId || 'unknown'}`"
                      >
                        <div
                          v-if="alertData && (getAlertId(alertData?.alert) || alertData?.alertId) && finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]"
                          class="bg-white dark:bg-[#1c2533] border border-gray-200 dark:border-[#324867] rounded-lg overflow-hidden"
                        >
                          <!-- Card Header (clickable to expand/collapse only for completed results) -->
                          <div 
                            :class="[
                              'p-4 transition-colors',
                              (finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.status === 'completed' || finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.data) && finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.status !== 'error'
                                ? 'cursor-pointer hover:bg-gray-50 dark:hover:bg-[#192233]'
                                : 'cursor-default'
                            ]"
                            @click="(finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.status === 'completed' || finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.data) && finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.status !== 'error' ? toggleFinetuneResultCard(getAlertId(alertData?.alert) || alertData?.alertId) : null"
                          >
                            <div class="flex items-center justify-between gap-3">
                              <div class="flex-1 min-w-0">
                                <div class="text-xs font-semibold text-gray-900 dark:text-white mb-1">
                                  Alert #{{ getAlertId(alertData?.alert) || alertData?.alertId }}
                                </div>
                                
                                <!-- Waiting/In Queue state -->
                                <div v-if="finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.status === 'waiting'" class="flex items-center gap-2">
                                  <span class="material-symbols-outlined text-gray-400 dark:text-gray-500 text-sm">
                                    schedule
                                  </span>
                                  <p class="text-xs text-gray-500 dark:text-gray-400">{{ $t('aiPlayground.retrievalTest.inQueue') }}</p>
                                </div>
                                
                                <!-- Running state (only for currently running alert) -->
                                <div v-else-if="finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.status === 'running' && currentRunningAlertId === (getAlertId(alertData?.alert) || alertData?.alertId)" class="flex items-center gap-2">
                                  <span class="material-symbols-outlined animate-spin text-primary text-sm">
                                    sync
                                  </span>
                                  <div class="flex items-center gap-2">
                                    <p class="text-xs text-primary font-medium">{{ $t('aiPlayground.retrievalTest.running') }}</p>
                                    <span class="text-xs text-gray-500 dark:text-gray-400">
                                      ({{ formatElapsedTime(finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.elapsedTime || 0) }})
                                    </span>
                                  </div>
                                </div>
                                
                                <!-- Cancelled state -->
                                <div v-else-if="finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.status === 'cancelled'" class="flex items-center gap-2">
                                  <span class="material-symbols-outlined text-gray-400 dark:text-gray-500 text-sm">
                                    cancel
                                  </span>
                                  <p class="text-xs text-gray-500 dark:text-gray-400">{{ $t('aiPlayground.retrievalTest.cancelled') }}</p>
                                </div>
                                
                                <!-- Error state -->
                                <div v-else-if="finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.status === 'error' || finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.error" class="flex items-center gap-2">
                                  <span class="text-xs font-semibold text-red-600 dark:text-red-400">
                                    {{ finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId].error || $t('aiPlayground.retrievalTest.error') }}
                                  </span>
                                  <span v-if="finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.elapsedTime" class="text-xs text-gray-500 dark:text-gray-400">
                                    ({{ formatElapsedTime(finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId].elapsedTime) }})
                                  </span>
                                </div>
                                
                                <!-- Success/Completed state -->
                                <div v-else-if="finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.status === 'completed' || finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.data" class="flex items-center gap-2">
                                  <span class="text-xs text-green-600 dark:text-green-400 font-medium">✓ Completed</span>
                                  <span v-if="finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.workflowName" class="text-xs text-gray-500 dark:text-gray-400">
                                    • {{ finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId].workflowName }}
                                  </span>
                                  <span v-if="finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.elapsedTime" class="text-xs text-gray-500 dark:text-gray-400">
                                    • {{ formatElapsedTime(finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId].elapsedTime) }}
                                  </span>
                                </div>
                              </div>
                              
                              <!-- Expand/collapse icon (only show if completed and has data) -->
                              <span
                                v-if="(finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.status === 'completed' || finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.data) && finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.status !== 'error'"
                                class="material-symbols-outlined text-gray-400 dark:text-gray-500 transition-transform flex-shrink-0 text-sm"
                                :class="finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.expanded ? 'rotate-180' : ''"
                              >
                                expand_more
                              </span>
                            </div>
                          </div>
                          
                          <!-- Card Content (expandable) -->
                          <div 
                            v-if="finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.expanded && (finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.status === 'completed' || finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.data)"
                            class="border-t border-gray-200 dark:border-[#324867] p-4 space-y-3"
                          >
                            <!-- Is Threat -->
                            <div v-if="finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.is_threat" class="border border-gray-200 dark:border-[#324867] rounded-lg p-2 bg-gray-50 dark:bg-[#192233]">
                              <div class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1">
                                [Is Threat]
                              </div>
                              <div class="text-xs text-gray-900 dark:text-white whitespace-pre-wrap break-words">
                                {{ finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId].is_threat }}
                              </div>
                            </div>

                            <!-- Confidence Score -->
                            <div v-if="finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.confidence_score" class="border border-gray-200 dark:border-[#324867] rounded-lg p-2 bg-gray-50 dark:bg-[#192233]">
                              <div class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1">
                                [Confidence Score]
                              </div>
                              <div class="text-xs text-gray-900 dark:text-white whitespace-pre-wrap break-words">
                                {{ finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId].confidence_score }}
                              </div>
                            </div>

                            <!-- Reason -->
                            <div v-if="finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.reason" class="border border-gray-200 dark:border-[#324867] rounded-lg p-2 bg-gray-50 dark:bg-[#192233]">
                              <div class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1">
                                [Reason]
                              </div>
                              <div class="text-xs text-gray-900 dark:text-white whitespace-pre-wrap break-words">
                                {{ finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId].reason }}
                              </div>
                            </div>

                            <!-- Raw Text (fallback if no separated values) -->
                            <div v-if="!finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.is_threat && !finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.confidence_score && !finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.reason && finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId]?.raw_text" class="border border-gray-200 dark:border-[#324867] rounded-lg p-2 bg-gray-50 dark:bg-[#192233]">
                              <div class="text-xs text-gray-900 dark:text-white whitespace-pre-wrap break-words">
                                {{ finetuneWorkflowResults[getAlertId(alertData?.alert) || alertData?.alertId].raw_text }}
                              </div>
                            </div>
                            
                            <div class="text-xs text-gray-500 dark:text-gray-400 pt-2 border-t border-gray-200 dark:border-[#324867]">
                              Results saved. Check the sidebar to view fine-tune investigation results.
                            </div>
                          </div>
                        </div>
                      </template>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { saveAlertAiFineTuneResult, getAlertAiFineTuneResults } from '@/api/alerts'
import { useToast } from '@/composables/useToast'
import { formatDateTime } from '@/utils/dateTime'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  selectedAlertsData: {
    type: Array,
    required: true
  },
  workflows: {
    type: Array,
    default: () => []
  },
  loadingWorkflows: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'remove-alert', 'refresh-results'])

const { t } = useI18n()
const toast = useToast()

// API configuration
const aiWorkflowApi = import.meta.env.VITE_AI_WORKFLOW_API
const aiWorkflowRunnerKey = import.meta.env.VITE_PLAYGROUND_RUNNER_KEY
const workflowAppBaseUrl = import.meta.env.VITE_WORKFLOW_APP_BASE_URL || 'https://sectools.cloudbu.huawei.com:9443'

// State
const finetuneWorkflowSelections = ref({})
const finetuneWorkflowResults = ref({})
const runningWorkflow = ref(false)
const currentRunningAlertId = ref(null)
const cancelWorkflows = ref(false)
const contentFormatMode = ref('json')
const allFinetuneRecords = ref([]) // Store all fine-tune records for display in table
const loadingFinetuneRecords = ref(false)

// Helper function to get alert ID
const getAlertId = (alert) => {
  return String(alert?.alert_id || alert?.id || '').trim()
}

// Get workflow ID by workflow name (case-insensitive match)
const getWorkflowIdByName = (workflowName) => {
  if (!workflowName || !props.workflows || props.workflows.length === 0) {
    return null
  }
  const matched = props.workflows.find(
    w => w.name && workflowName && w.name.toLowerCase() === workflowName.toLowerCase()
  )
  return matched?.id || null
}

// Get workflow URL by workflow name
const getWorkflowUrl = (workflowName) => {
  const workflowId = getWorkflowIdByName(workflowName)
  if (!workflowId) {
    return null
  }
  return `${workflowAppBaseUrl}/app/${workflowId}/workflow`
}

// Get workflow URL for a specific alert by alert ID
const getWorkflowUrlForAlert = (alertId) => {
  const workflowId = finetuneWorkflowSelections.value[alertId]
  if (!workflowId) {
    return null
  }
  return `${workflowAppBaseUrl}/app/${workflowId}/workflow`
}

// Get workflow name for a specific alert by alert ID
const getWorkflowNameForAlert = (alertId) => {
  const workflowId = finetuneWorkflowSelections.value[alertId]
  if (!workflowId) {
    return null
  }
  const workflow = props.workflows.find(w => w.id === workflowId)
  return workflow?.name || null
}

// Get raw description from alert data
const getRawDescription = (detail = null, alert = null) => {
  return (
    detail?.description ??
    detail?.data?.description ??
    detail?.data_object?.description ??
    alert?.description ??
    alert?.data_object?.description ??
    ''
  )
}

// Format description as JSON
const formatDescriptionAsJson = (desc) => {
  if (desc === null || desc === undefined) return ''
  if (typeof desc === 'string') return desc
  try {
    return JSON.stringify(desc, null, 2)
  } catch {
    return String(desc)
  }
}

// Format description as rich text
const formatDescriptionAsRichText = (desc) => {
  if (desc === null || desc === undefined) return ''
  if (typeof desc === 'string') {
    try {
      const parsed = JSON.parse(desc)
      return formatObjectAsRichText(parsed)
    } catch {
      return desc
    }
  }
  return formatObjectAsRichText(desc)
}

const formatObjectAsRichText = (obj, indent = 0) => {
  if (obj === null || obj === undefined) return String(obj)
  
  if (Array.isArray(obj)) {
    if (obj.length === 0) return '[]'
    return obj.map((item, index) => {
      const prefix = '  '.repeat(indent)
      const bullet = `${prefix}- `
      if (typeof item === 'object' && item !== null) {
        return `${bullet}${formatObjectAsRichText(item, indent + 1)}`
      }
      return `${bullet}${String(item)}`
    }).join('\n')
  }
  
  if (typeof obj === 'object') {
    const entries = Object.entries(obj)
    if (entries.length === 0) return '{}'
    return entries.map(([key, value]) => {
      const prefix = '  '.repeat(indent)
      const formattedKey = key.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim()
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        return `${prefix}${formattedKey}:\n${formatObjectAsRichText(value, indent + 1)}`
      } else if (Array.isArray(value)) {
        return `${prefix}${formattedKey}:\n${formatObjectAsRichText(value, indent + 1)}`
      }
      return `${prefix}${formattedKey}: ${String(value)}`
    }).join('\n\n')
  }
  
  return String(obj)
}

// Get formatted content for an alert
const getFormattedContentForAlert = (alertData) => {
  const desc = getRawDescription(alertData.detail, alertData.alert)
  if (contentFormatMode.value === 'json') {
    return formatDescriptionAsJson(desc)
  } else {
    return formatDescriptionAsRichText(desc)
  }
}

// Extract all text values from an object recursively
const extractAllTextValues = (obj, depth = 0) => {
  if (obj === null || obj === undefined) return []

  const textValues = []

  if (typeof obj === 'string') {
    textValues.push(obj)
  } else if (Array.isArray(obj)) {
    obj.forEach((item) => {
      const extracted = extractAllTextValues(item, depth + 1)
      textValues.push(...extracted)
    })
  } else if (typeof obj === 'object') {
    Object.entries(obj).forEach(([, value]) => {
      const extracted = extractAllTextValues(value, depth + 1)
      textValues.push(...extracted)
    })
  }

  return textValues
}

// Get workflow text from data
const getWorkflowTextFromData = (data) => {
  if (!data || data.error) return null

  const resultObject = data?.data?.outputs?.result
  if (!resultObject) return null

  const textValues = extractAllTextValues(resultObject)
  const filtered = textValues.filter(text => text && text.trim().length > 0)
  return filtered.length > 0 ? filtered.join('\n\n') : null
}

// Parse workflow blocks
const parseWorkflowBlocks = (text) => {
  if (!text || typeof text !== 'string') {
    return {
      isThreat: null,
      confidence: null,
      reason: null,
      hasAny: false,
      raw: text || ''
    }
  }

  const patterns = {
    isThreat: /\[\s*Is\s*Threat\s*\]\s*:\s*([\s\S]*?)(?=\[\s*Confidence\s*Score\s*\]|\[\s*Reason\s*\]|$)/i,
    confidence: /\[\s*Confidence\s*Score\s*\]\s*:\s*([\s\S]*?)(?=\[\s*Is\s*Threat\s*\]|\[\s*Reason\s*\]|$)/i,
    reason: /\[\s*Reason\s*\]\s*:\s*([\s\S]*?)(?=\[\s*Is\s*Threat\s*\]|\[\s*Confidence\s*Score\s*\]|$)/i
  }

  const result = {
    isThreat: null,
    confidence: null,
    reason: null,
    hasAny: false,
    raw: text
  }

  Object.entries(patterns).forEach(([key, regex]) => {
    const match = text.match(regex)
    if (match && match[1]) {
      result[key] = match[1].trim()
    }
  })

  result.hasAny = !!(result.isThreat || result.confidence || result.reason)
  return result
}

// Format elapsed time
const formatElapsedTime = (milliseconds) => {
  if (!milliseconds || milliseconds < 0) return '0s'
  
  const seconds = Math.floor(milliseconds / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`
  }
  return `${seconds}s`
}

// Load fine-tune results for an alert
const loadFinetuneResults = async (alertId) => {
  const alertIdStr = String(alertId).trim()
  if (!alertIdStr) {
    console.warn('loadFinetuneResults: Invalid alertId', alertId)
    return
  }
  
  const alertData = props.selectedAlertsData.find(d => {
    const dataAlertId = getAlertId(d.alert) || d.alertId
    return String(dataAlertId) === alertIdStr
  })
  if (!alertData) {
    console.warn(`Alert data not found for alertId: ${alertIdStr}`)
    return
  }
  
  alertData.finetuneLoading = true
  try {
    const response = await getAlertAiFineTuneResults(alertIdStr)
    
    let results = []
    if (response?.data?.data && Array.isArray(response.data.data)) {
      results = response.data.data
    } else if (Array.isArray(response?.data)) {
      results = response.data
    } else if (response?.data?.data && !Array.isArray(response.data.data)) {
      // Single result
      results = [response.data.data]
    } else {
      console.warn(`Unexpected response structure for alert ${alertIdStr}:`, response)
      results = []
    }
    
    alertData.finetuneResults = results.map(r => ({
      ...r,
      expanded: false
    }))
    
    emit('refresh-results', alertId)
  } catch (error) {
    console.error(`Failed to load fine-tune results for alert ${alertIdStr}:`, error)
    alertData.finetuneResults = []
  } finally {
    alertData.finetuneLoading = false
  }
}

// Load fine-tune records for all selected alerts in order (one record per alert)
const loadAllFinetuneRecords = async () => {
  if (props.selectedAlertsData.length === 0) {
    allFinetuneRecords.value = []
    return
  }
  
  loadingFinetuneRecords.value = true
  allFinetuneRecords.value = []
  
  try {
    // Load records sequentially, one alert at a time, one record per alert
    for (const alertData of props.selectedAlertsData) {
      if (!alertData || !alertData.alert) continue
      
      const alertId = getAlertId(alertData.alert) || alertData.alertId
      if (!alertId) continue
      
      // Query one record (latest) for this alert
      try {
        const response = await getAlertAiFineTuneResults(alertId)
        
        let record = null
        if (response?.data?.data) {
          // Single record response
          record = response.data.data
        } else if (response?.data && typeof response.data === 'object' && !Array.isArray(response.data)) {
          record = response.data
        }
        
        // Add alert title to the record for display
        if (record) {
          allFinetuneRecords.value.push({
            ...record,
            alert_title: alertData.alert?.title || '',
            alert_id: alertId
          })
        } else {
          // If no record found, still add an entry with alert info
          allFinetuneRecords.value.push({
            alert_title: alertData.alert?.title || '',
            alert_id: alertId,
            updated_at: null,
            is_threat: null,
            confidence_score: null,
            agent_name: null,
            updated_by: null
          })
        }
      } catch (error) {
        console.error(`Failed to load fine-tune record for alert ${alertId}:`, error)
        // Continue with next alert even if one fails
        allFinetuneRecords.value.push({
          alert_title: alertData.alert?.title || '',
          alert_id: alertId,
          updated_at: null,
          is_threat: null,
          confidence_score: null,
          agent_name: null,
          updated_by: null
        })
      }
    }
  } catch (error) {
    console.error('Failed to load fine-tune records:', error)
    toast.error('Failed to load fine-tune records', 'ERROR')
  } finally {
    loadingFinetuneRecords.value = false
  }
}


// Toggle fine-tune alert drawer
const toggleFinetuneAlertDrawer = (alertId) => {
  const alertData = props.selectedAlertsData.find(d => {
    const dataAlertId = getAlertId(d.alert) || d.alertId
    return String(dataAlertId) === String(alertId)
  })
  if (alertData) {
    if (alertData.finetuneExpanded === undefined) {
      alertData.finetuneExpanded = false
    }
    alertData.finetuneExpanded = !alertData.finetuneExpanded
  }
}

// Toggle fine-tune result card
const toggleFinetuneResultCard = (alertId) => {
  const result = finetuneWorkflowResults.value[alertId]
  if (result) {
    result.expanded = !result.expanded
  }
}

// Check if all alerts have workflows selected
const canRunAllWorkflows = computed(() => {
  if (props.selectedAlertsData.length === 0) return false
  return props.selectedAlertsData.every(alertData => {
    if (!alertData || !alertData.alert) return false
    const alertId = getAlertId(alertData.alert) || alertData.alertId
    if (!alertId) return false
    const workflowId = finetuneWorkflowSelections.value[alertId]
    return workflowId && workflowId !== '' && workflowId !== '__loading__'
  })
})

// Handle running workflows
const handleRunAllWorkflows = async () => {
  if (!canRunAllWorkflows.value || runningWorkflow.value) return

  runningWorkflow.value = true
  cancelWorkflows.value = false
  currentRunningAlertId.value = null
  const results = []

  try {
    // Initialize state for alerts that will be processed
    props.selectedAlertsData.forEach(alertData => {
      if (alertData && alertData.alert) {
        const alertIdValue = getAlertId(alertData.alert) || alertData.alertId
        if (alertIdValue) {
          const workflowId = finetuneWorkflowSelections.value[alertIdValue]
          if (workflowId && workflowId !== '') {
            finetuneWorkflowResults.value[alertIdValue] = { 
              data: null, 
              error: null, 
              loading: false,
              status: 'waiting',
              is_threat: null,
              confidence_score: null,
              reason: null,
              raw_text: null,
              workflowName: null,
              expanded: false,
              startTime: null,
              elapsedTime: 0,
              timerInterval: null
            }
          }
        }
      }
    })

    // Run workflow for each alert sequentially
    for (const alertData of props.selectedAlertsData) {
      // Check if cancellation was requested
      if (cancelWorkflows.value) {
        // Mark remaining alerts as cancelled
        const remainingAlerts = props.selectedAlertsData.slice(
          props.selectedAlertsData.indexOf(alertData)
        )
        remainingAlerts.forEach(remainingAlert => {
          if (remainingAlert && remainingAlert.alert) {
            const remainingAlertId = getAlertId(remainingAlert.alert) || remainingAlert.alertId
            if (remainingAlertId && finetuneWorkflowResults.value[remainingAlertId]) {
              if (finetuneWorkflowResults.value[remainingAlertId].status === 'waiting') {
                finetuneWorkflowResults.value[remainingAlertId].status = 'cancelled'
                finetuneWorkflowResults.value[remainingAlertId].loading = false
                if (finetuneWorkflowResults.value[remainingAlertId].timerInterval) {
                  clearInterval(finetuneWorkflowResults.value[remainingAlertId].timerInterval)
                  finetuneWorkflowResults.value[remainingAlertId].timerInterval = null
                }
              }
            }
          }
        })
        break
      }

      if (!alertData || !alertData.alert) continue
      const alertIdValue = getAlertId(alertData.alert) || alertData.alertId
      if (!alertIdValue) continue
      const workflowId = finetuneWorkflowSelections.value[alertIdValue]
      if (!workflowId || workflowId === '') continue

      // Update status to running and start timer
      if (finetuneWorkflowResults.value[alertIdValue]) {
        finetuneWorkflowResults.value[alertIdValue].status = 'running'
        finetuneWorkflowResults.value[alertIdValue].loading = true
        finetuneWorkflowResults.value[alertIdValue].startTime = Date.now()
        finetuneWorkflowResults.value[alertIdValue].elapsedTime = 0
        
        finetuneWorkflowResults.value[alertIdValue].timerInterval = setInterval(() => {
          if (finetuneWorkflowResults.value[alertIdValue] && finetuneWorkflowResults.value[alertIdValue].startTime) {
            finetuneWorkflowResults.value[alertIdValue].elapsedTime = Date.now() - finetuneWorkflowResults.value[alertIdValue].startTime
          }
        }, 100)
      }
      currentRunningAlertId.value = alertIdValue
      const subjectValue = alertData.alert?.title || ''
      const descriptionValue = getRawDescription(alertData.detail, alertData.alert)
      const descriptionString = typeof descriptionValue === 'object' && descriptionValue !== null
        ? JSON.stringify(descriptionValue)
        : String(descriptionValue || '')

      const payload = {
        inputs: {
          appid: String(workflowId),
          subject: String(subjectValue),
          description: descriptionString,
          alarm_id: String(alertIdValue)
        },
        response_mode: 'blocking',
        user: 'Pisces AI Playground'
      }

      try {
        const response = await fetch(aiWorkflowApi, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${aiWorkflowRunnerKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        
        // Check if cancellation was requested after fetch completed
        if (cancelWorkflows.value) {
          if (finetuneWorkflowResults.value[alertIdValue]?.timerInterval) {
            clearInterval(finetuneWorkflowResults.value[alertIdValue].timerInterval)
          }
          
          const finalElapsedTime = finetuneWorkflowResults.value[alertIdValue]?.startTime 
            ? Date.now() - finetuneWorkflowResults.value[alertIdValue].startTime 
            : 0
          
          finetuneWorkflowResults.value[alertIdValue] = { 
            data: null, 
            error: null, 
            loading: false,
            status: 'cancelled',
            is_threat: null,
            confidence_score: null,
            reason: null,
            raw_text: null,
            workflowName: null,
            expanded: false,
            startTime: finetuneWorkflowResults.value[alertIdValue]?.startTime || null,
            elapsedTime: finalElapsedTime,
            timerInterval: null
          }
          
          currentRunningAlertId.value = null
          continue
        }
        
        results.push({ alertId: alertIdValue, success: true, data })
        
        // Parse workflow result
        const text = getWorkflowTextFromData(data)
        const parsed = parseWorkflowBlocks(text || '')
        const workflowName = props.workflows.find(w => w.id === workflowId)?.name || 'Model'
        
        const is_threat = parsed?.isThreat || null
        const confidence_score = parsed?.confidence || null
        const reason = parsed?.reason || null
        
        // Stop timer
        if (finetuneWorkflowResults.value[alertIdValue]?.timerInterval) {
          clearInterval(finetuneWorkflowResults.value[alertIdValue].timerInterval)
        }
        
        const finalElapsedTime = finetuneWorkflowResults.value[alertIdValue]?.startTime 
          ? Date.now() - finetuneWorkflowResults.value[alertIdValue].startTime 
          : 0
        
        // Store result
        finetuneWorkflowResults.value[alertIdValue] = { 
          data, 
          error: null, 
          loading: false,
          status: 'completed',
          is_threat,
          confidence_score,
          reason,
          raw_text: text || '',
          workflowName,
          expanded: false,
          startTime: finetuneWorkflowResults.value[alertIdValue]?.startTime || null,
          elapsedTime: finalElapsedTime,
          timerInterval: null
        }
        
        currentRunningAlertId.value = null
        
        // Save fine-tune result
        const savePayload = {
          workflow_id: String(workflowId),
          agent_name: workflowName,
          is_threat,
          confidence_score,
          reason,
          raw_text: text || ''
        }
        
        await saveAlertAiFineTuneResult(alertIdValue, savePayload)
        
        // Refresh fine-tune results for this alert
        await loadFinetuneResults(alertIdValue)
      } catch (error) {
        console.error(`Failed to run workflow for alert ${alertIdValue}:`, error)
        results.push({ alertId: alertIdValue, success: false, error: error.message })
        
        if (finetuneWorkflowResults.value[alertIdValue]?.timerInterval) {
          clearInterval(finetuneWorkflowResults.value[alertIdValue].timerInterval)
        }
        
        const finalElapsedTime = finetuneWorkflowResults.value[alertIdValue]?.startTime 
          ? Date.now() - finetuneWorkflowResults.value[alertIdValue].startTime 
          : 0
        
        finetuneWorkflowResults.value[alertIdValue] = { 
          data: null, 
          error: error?.message || 'Failed to run workflow', 
          loading: false,
          status: 'error',
          is_threat: null,
          confidence_score: null,
          reason: null,
          raw_text: null,
          workflowName: null,
          expanded: false,
          startTime: finetuneWorkflowResults.value[alertIdValue]?.startTime || null,
          elapsedTime: finalElapsedTime,
          timerInterval: null
        }
        
        currentRunningAlertId.value = null
      }
    }

    if (results.length > 0) {
      const successCount = results.filter(r => r.success).length
      toast.success(`Successfully ran workflows for ${successCount} of ${results.length} alerts`, 'SUCCESS')
    }
  } catch (error) {
    console.error('Failed to run workflows:', error)
    toast.error('Failed to run workflows', 'ERROR')
  } finally {
    if (!cancelWorkflows.value) {
      runningWorkflow.value = false
      currentRunningAlertId.value = null
    }
    Object.keys(finetuneWorkflowResults.value).forEach(alertId => {
      if (finetuneWorkflowResults.value[alertId]?.loading) {
        finetuneWorkflowResults.value[alertId].loading = false
      }
      if (finetuneWorkflowResults.value[alertId]?.status === 'running') {
        if (finetuneWorkflowResults.value[alertId].timerInterval) {
          clearInterval(finetuneWorkflowResults.value[alertId].timerInterval)
          finetuneWorkflowResults.value[alertId].timerInterval = null
        }
        if (finetuneWorkflowResults.value[alertId].startTime) {
          finetuneWorkflowResults.value[alertId].elapsedTime = Date.now() - finetuneWorkflowResults.value[alertId].startTime
        }
        finetuneWorkflowResults.value[alertId].status = 'error'
      }
      if (finetuneWorkflowResults.value[alertId]?.timerInterval) {
        clearInterval(finetuneWorkflowResults.value[alertId].timerInterval)
        finetuneWorkflowResults.value[alertId].timerInterval = null
      }
    })
    cancelWorkflows.value = false
  }
}

// Handle canceling workflow execution
const handleCancelWorkflows = () => {
  cancelWorkflows.value = true
  
  // Cancel all waiting tasks
  Object.keys(finetuneWorkflowResults.value).forEach(alertId => {
    const result = finetuneWorkflowResults.value[alertId]
    if (result && result.status === 'waiting') {
      result.status = 'cancelled'
      result.loading = false
      if (result.timerInterval) {
        clearInterval(result.timerInterval)
        result.timerInterval = null
      }
    }
  })
  
  // Cancel currently running task
  if (currentRunningAlertId.value && finetuneWorkflowResults.value[currentRunningAlertId.value]) {
    const runningResult = finetuneWorkflowResults.value[currentRunningAlertId.value]
    if (runningResult && runningResult.status === 'running') {
      runningResult.status = 'cancelled'
      runningResult.loading = false
      if (runningResult.timerInterval) {
        clearInterval(runningResult.timerInterval)
        runningResult.timerInterval = null
      }
      if (runningResult.startTime) {
        runningResult.elapsedTime = Date.now() - runningResult.startTime
      }
    }
  }
  
  // Reset UI states
  runningWorkflow.value = false
  currentRunningAlertId.value = null
}

// Initialize workflow selections when overlay opens
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    finetuneWorkflowSelections.value = {}
    finetuneWorkflowResults.value = {}
    props.selectedAlertsData.forEach(alertData => {
      if (alertData && alertData.alert) {
        const alertId = getAlertId(alertData.alert) || alertData.alertId
        if (alertId) {
          finetuneWorkflowSelections.value[alertId] = ''
        }
        if (alertData.finetuneExpanded === undefined) {
          alertData.finetuneExpanded = false
        }
      }
    })
    
    // Auto-select workflows based on agent_name match
    nextTick(() => {
      props.selectedAlertsData.forEach(alertData => {
        if (!alertData || !alertData.alert) return
        const alertId = getAlertId(alertData.alert) || alertData.alertId
        if (!alertId) return
        const agentName = alertData.alert?.agent_name
        if (agentName && props.workflows.length > 0) {
          const matchedWorkflow = props.workflows.find(w => 
            w.name && agentName.toLowerCase() === w.name.toLowerCase()
          )
          if (matchedWorkflow) {
            finetuneWorkflowSelections.value[alertId] = matchedWorkflow.id
          }
        }
      })
    })
    
    // Load all fine-tune records for all selected alerts in order
    loadAllFinetuneRecords()
  }
})
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease-out;
}

.slide-enter-from {
  transform: translateX(100%);
}

.slide-leave-to {
  transform: translateX(100%);
}
</style>

