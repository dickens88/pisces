<template>
  <div class="w-full">
    <!-- Page title and actions -->
    <header class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div class="flex min-w-72 flex-col gap-2">
        <h1 class="text-gray-900 dark:text-white text-4xl font-black leading-tight tracking-[-0.033em]">
          {{ $t('aiPlayground.title') }}
        </h1>
        <p class="text-gray-600 dark:text-gray-400 text-sm">
          {{ $t('aiPlayground.list.title') }}
        </p>
      </div>
      <div class="flex items-center gap-4">
        <button
          @click="handleRefresh"
          :disabled="loadingAlerts || aiAccuracyLoading"
          class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-200 dark:disabled:hover:bg-[#2a3546] h-10"
          :title="$t('common.refresh') || 'Refresh'"
        >
          <span
            class="material-symbols-outlined text-base"
            :class="{ 'animate-spin': loadingAlerts || aiAccuracyLoading }"
          >
            refresh
          </span>
        </button>
        <TimeRangePicker
          v-model="selectedTimeRange"
          :custom-range="customTimeRange"
          storage-key="ai-playground"
          @change="handleTimeRangeChange"
          @custom-range-change="handleCustomRangeChange"
        />
      </div>
    </header>

    <!-- Charts -->
    <section
      v-if="showCharts"
      class="grid grid-cols-1 lg:grid-cols-1 gap-6 mb-6"
    >
      <div class="flex flex-col rounded-xl border border-gray-200 dark:border-[#324867]/50 bg-white dark:bg-[#19222c] p-0">
        <div class="flex justify-between items-center p-3 pt-2">
          <p class="text-gray-900 dark:text-white text-lg font-semibold">{{ $t('dashboard.charts.aiAccuracy') }}</p>
          <span class="text-xs text-gray-600 dark:text-white/60">{{ timeRangeLabel }}</span>
        </div>
        <div class="flex flex-col gap-1 px-3 pb-2">
          <span class="text-gray-600 dark:text-white/60 text-sm font-medium uppercase tracking-wide">
            {{ $t('common.averageAccuracy') || 'Average Accuracy' }}
          </span>
          <span class="text-gray-900 dark:text-white text-3xl font-bold tracking-tight">
            {{ aiAccuracyAverage }}%
          </span>
        </div>
        <div class="relative h-52">
          <div
            v-if="aiAccuracyLoading"
            class="absolute inset-0 flex items-center justify-center text-white/50 text-sm"
          >
            {{ $t('common.loading') }}
          </div>
          <div
            v-else-if="aiAccuracyData.length === 0"
            class="absolute inset-0 flex items-center justify-center text-white/50 text-sm"
          >
            {{ $t('dashboard.charts.noData') }}
          </div>
          <div
            v-show="!aiAccuracyLoading && aiAccuracyData.length > 0"
            ref="aiAccuracyChartRef"
            class="absolute inset-0"
            style="margin: 0; padding: 0;"
          ></div>
        </div>
      </div>
    </section>

    <!-- Alert list table -->
    <section :class="['grid grid-cols-1 gap-4', selectedAlert ? 'lg:grid-cols-3' : 'lg:grid-cols-1']">
      <div :class="['bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-xl relative', selectedAlert ? 'lg:col-span-2' : 'lg:col-span-1']">
        <div
          v-if="loadingAlerts"
          class="absolute inset-0 bg-white/80 dark:bg-[#111822]/80 backdrop-blur-sm z-50 flex items-center justify-center rounded-xl"
        >
          <div class="flex flex-col items-center gap-4">
            <div class="relative w-16 h-16">
              <div class="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
              <div class="absolute inset-0 border-4 border-transparent border-t-primary rounded-full animate-spin"></div>
            </div>
            <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">{{ $t('common.loading') }}</p>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-3 p-4 border-b border-gray-200 dark:border-[#324867]">
          <div class="relative w-full max-w-xl" ref="searchContainerRef">
            <div
              class="flex items-start gap-2 rounded-lg border-0 bg-gray-100 dark:bg-[#233348] px-3 py-2 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary"
              @click="handleSearchContainerClick"
            >
              <div class="pointer-events-none flex items-center shrink-0 pt-[2px]">
                <span class="material-symbols-outlined text-gray-500 dark:text-gray-400" style="font-size: 20px;">search</span>
              </div>
              <div class="flex flex-1 flex-wrap items-center gap-2 max-h-32 overflow-y-auto pr-1">
                <div
                  v-for="(keywordObj, index) in searchKeywords"
                  :key="`${keywordObj.field}-${keywordObj.value}-${index}`"
                  class="flex items-center gap-1 px-2 py-1 bg-primary/20 text-primary rounded text-sm max-w-full min-w-0"
                >
                  <span class="min-w-0 break-all">{{ getFieldLabel(keywordObj.field) }}: {{ keywordObj.value }}</span>
                  <button
                    @click.stop="removeKeyword(index)"
                    class="flex items-center justify-center hover:text-primary/70 transition-colors ml-0.5"
                    type="button"
                    :aria-label="$t('common.delete')"
                  >
                    <span class="material-symbols-outlined" style="font-size: 16px;">close</span>
                  </button>
                </div>
                <input
                  v-model="displaySearchInput"
                  @keydown.enter.prevent="addKeyword"
                  @keydown.backspace="handleKeywordDeleteKey"
                  @focus="showFieldMenu = !currentField.value"
                  class="flex-1 min-w-[160px] border-0 bg-transparent text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none sm:text-sm"
                  :placeholder="getSearchPlaceholder()"
                  type="text"
                  ref="searchInputRef"
                />
              </div>
            </div>
            <div
              v-if="showFieldMenu && !currentField"
              class="absolute left-0 top-full mt-2 bg-white dark:bg-[#233348] border border-gray-200 dark:border-[#324867] rounded-lg shadow-lg z-50 min-w-[200px]"
              @mousedown.prevent
            >
              <button
                v-for="field in searchFields"
                :key="field.value"
                @click="selectField(field.value)"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867]"
              >
                <span class="material-symbols-outlined text-base">{{ field.icon }}</span>
                <span>{{ field.label }}</span>
              </button>
            </div>
          </div>

          <div class="relative min-w-[120px] max-w-[12rem]">
            <ClearableSelect
              v-model="aiJudgeFilter"
              clear-value="all"
              @change="handleFilter"
            >
              <option value="all">{{ $t('alerts.list.allAiJudge') }}</option>
              <option value="True_Positive">{{ $t('alerts.list.aiJudgeResult.truePositive') }}</option>
              <option value="False_Positive">{{ $t('alerts.list.aiJudgeResult.falsePositive') }}</option>
              <option value="Unknown">{{ $t('alerts.list.aiJudgeResult.unknown') }}</option>
            </ClearableSelect>
          </div>

          <div class="relative">
            <select
              v-model="matchFilter"
              @change="handleFilter"
              class="pl-4 pr-9 appearance-none block w-full rounded-lg border-0 bg-gray-100 dark:bg-[#233348] h-10 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm text-sm"
            >
              <option value="all">{{ $t('aiPlayground.matchFilter.all') }}</option>
              <option value="match">{{ $t('aiPlayground.matchStatus.match') }}</option>
              <option value="mismatch">{{ $t('aiPlayground.matchStatus.mismatch') }}</option>
              <option value="empty">{{ $t('aiPlayground.matchFilter.empty') }}</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500 dark:text-gray-400">
              <span class="material-symbols-outlined" style="font-size: 20px;">arrow_drop_down</span>
            </div>
          </div>

          <button
            @click="handleToggleWordWrap"
            class="flex items-center justify-center gap-2 rounded-lg h-10 bg-gray-100 dark:bg-[#233348] text-gray-700 dark:text-white text-sm font-medium px-4 hover:bg-gray-200 dark:hover:bg-[#324867] transition-colors"
            :title="isWordWrapEnabled ? 'Disable word wrap' : 'Enable word wrap'"
          >
            <span class="material-symbols-outlined text-base">
              {{ isWordWrapEnabled ? 'text_fields' : 'wrap_text' }}
            </span>
          </button>
        </div>

        <DataTable
          ref="dataTableRef"
          :columns="columns"
          :items="alerts"
          :selectable="false"
          :resizable="true"
          storage-key="ai-playground-alerts-table-columns"
          :default-widths="defaultWidths"
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          @update:current-page="handlePageChange"
          @update:page-size="handlePageSizeChange"
          @row-click="handleRowClick"
        >
          <template #cell-createTime="{ value, item }">
            {{ formatDateTime(value || item?.create_time) }}
          </template>
          <template #cell-alertTitle="{ item }">
            <span
              class="text-primary hover:underline cursor-pointer"
              :title="item.title"
            >
              {{ item.title }}
            </span>
          </template>
          <template #cell-riskLevel="{ item }">
            <span
              :class="[
                'text-xs font-medium px-2.5 py-0.5 rounded-full inline-flex items-center justify-center min-w-[70px]',
                getRiskLevelClass(item.riskLevel)
              ]"
              :title="$t(`common.severity.${item.riskLevel}`)"
            >
              {{ $t(`common.severity.${item.riskLevel}`) }}
            </span>
          </template>
          <template #cell-aiJudge="{ item }">
            <div class="flex items-center justify-center">
              <span
                v-if="item.verification_state === 'True_Positive'"
                class="text-sm font-medium text-red-600 dark:text-red-400"
              >
                {{ $t('alerts.list.aiJudgeResult.truePositive') }}
              </span>
              <span
                v-else-if="item.verification_state === 'False_Positive'"
                class="text-sm font-medium text-green-600 dark:text-green-400"
              >
                {{ $t('alerts.list.aiJudgeResult.falsePositive') }}
              </span>
              <span
                v-else
                class="text-sm font-medium text-gray-400 dark:text-gray-500"
              >
                {{ $t('alerts.list.aiJudgeResult.unknown') }}
              </span>
            </div>
          </template>
          <template #cell-humanVerdict="{ item }">
            <div class="flex items-center justify-center">
              <span class="text-sm text-gray-900 dark:text-white">
                {{ item.close_reason || item.closeReason || '-' }}
              </span>
            </div>
          </template>
          <template #cell-match="{ item }">
            <div class="flex items-center justify-center">
              <span
                v-if="getMatchStatus(item) === 'match'"
                class="material-symbols-outlined text-green-600 dark:text-green-400"
                style="font-size: 20px; font-variation-settings: 'FILL' 1, 'wght' 600, 'GRAD' 200, 'opsz' 24;"
                :title="$t('aiPlayground.matchStatus.match')"
              >
                check_circle
              </span>
              <span
                v-else-if="getMatchStatus(item) === 'mismatch'"
                class="material-symbols-outlined text-red-600 dark:text-red-400"
                style="font-size: 20px; font-variation-settings: 'FILL' 1, 'wght' 600, 'GRAD' 200, 'opsz' 24;"
                :title="$t('aiPlayground.matchStatus.mismatch')"
              >
                cancel
              </span>
              <span
                v-else
                class="text-sm text-gray-400 dark:text-gray-500"
              >
                -
              </span>
            </div>
          </template>
        </DataTable>
      </div>

      <div v-if="selectedAlert" class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-xl min-h-[300px] flex flex-col">
        <!-- Header with title and close button -->
        <div class="flex items-center justify-between px-5 pt-5 pb-4 border-b border-gray-200 dark:border-[#324867]">
          <h2 class="text-base font-semibold text-gray-900 dark:text-white">
            {{ $t('alerts.detail.title') }} #{{ alertId }}
          </h2>
          <button
            @click="selectedAlert = null"
            class="p-1.5 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-[#1c2533] rounded-md transition-colors"
            :aria-label="$t('common.close') || 'Close'"
          >
            <span class="material-symbols-outlined text-xl">close</span>
          </button>
        </div>
        
        <div class="flex-1 p-5 overflow-y-auto">
          <!-- Judgment Comparison Section -->
          <div class="grid grid-cols-2 gap-4 mb-6">
          <!-- AI Judgment -->
          <div class="bg-gray-50 dark:bg-[#1c2533] border border-gray-200 dark:border-[#324867] rounded-lg p-4">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
              <span class="material-symbols-outlined text-base">smart_toy</span>
              {{ $t('aiPlayground.aiJudgment') }}
            </h3>
            <div class="space-y-2">
              <div>
                <span class="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1.5">
                  <span class="material-symbols-outlined text-sm">gavel</span>
                  {{ $t('aiPlayground.verdict') }}: 
                </span>
                <span class="text-sm font-semibold text-gray-900 dark:text-white">
                  {{ getAiVerdictText(selectedAlert) }}
                </span>
              </div>
            </div>
          </div>
          
          <!-- Human Judgment -->
          <div class="bg-gray-50 dark:bg-[#1c2533] border border-gray-200 dark:border-[#324867] rounded-lg p-4">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
              <span class="material-symbols-outlined text-base">person</span>
              {{ $t('aiPlayground.humanJudgment') }}
            </h3>
            <div class="space-y-2">
              <div>
                <span class="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1.5">
                  <span class="material-symbols-outlined text-sm">gavel</span>
                  {{ $t('aiPlayground.verdict') }}: 
                </span>
                <span class="text-sm font-semibold text-gray-900 dark:text-white">
                  {{ getHumanVerdictText(selectedAlert) }}
                </span>
              </div>
              <div>
                <span class="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1.5">
                  <span class="material-symbols-outlined text-sm">badge</span>
                  {{ $t('aiPlayground.analyst') }}: 
                </span>
                <span class="text-sm font-semibold text-gray-900 dark:text-white">
                  {{ selectedAlert?.actor || selectedAlert?.creator || '-' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Reasoning Comparison Section -->
        <div class="space-y-4 mb-6">
          <!-- AI Reasoning -->
          <div>
            <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
              <span class="material-symbols-outlined text-base">psychology</span>
              {{ $t('aiPlayground.aiReasoning') }}
            </h3>
            <div v-if="selectedAlertLoading" class="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-2">
              <span class="material-symbols-outlined animate-spin text-base">refresh</span>
              {{ $t('common.loading') }}
            </div>
            <div
              v-else-if="aiItems.length"
              :class="[
                'bg-gray-50 dark:bg-[#1c2533] border border-gray-200 dark:border-[#324867] rounded-lg p-4 text-sm text-gray-700 dark:text-gray-300 ai-agent__html',
                { 'ai-agent__html--dark': isDarkMode() }
              ]"
            >
              <div v-for="(aiItem, index) in aiItems" :key="`ai-${aiItem.id || index}`">
                <div v-html="sanitizeHtml(aiItem.content || '')"></div>
              </div>
            </div>
            <div v-else class="bg-gray-50 dark:bg-[#1c2533] border border-gray-200 dark:border-[#324867] rounded-lg p-4 text-sm text-gray-500 dark:text-gray-400">
              {{ $t('alerts.detail.noAiResponse') }}
            </div>
          </div>

          <!-- Human Reasoning -->
          <div>
            <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
              <span class="material-symbols-outlined text-base">edit_note</span>
              {{ $t('aiPlayground.humanReasoning') }}
            </h3>
            <div class="bg-gray-50 dark:bg-[#1c2533] border border-gray-200 dark:border-[#324867] rounded-lg p-4 text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line min-h-[80px]">
              {{ humanConclusionValue || ($t('alerts.detail.noAiResponse') || 'No conclusion available.') }}
            </div>
          </div>
        </div>

        <!-- Edit Human Verdict Section -->
        <div class="border-t border-gray-200 dark:border-[#324867] pt-6">
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-base">edit</span>
            {{ $t('aiPlayground.editHumanVerdict') }}
          </h3>
          <div class="relative mb-4">
            <select
              v-model="humanVerdictValue"
              class="w-full bg-white dark:bg-[#1c2533] text-gray-900 dark:text-white border border-gray-200 dark:border-[#324867] rounded-lg px-4 py-2.5 text-sm appearance-none cursor-pointer focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors"
            >
              <option value="">{{ $t('aiPlayground.selectVerdict') }}</option>
              <option value="falsePositive">{{ $t('aiPlayground.closeReason.falsePositive') }}</option>
              <option value="resolved">{{ $t('aiPlayground.closeReason.resolved') }}</option>
              <option value="repeated">{{ $t('aiPlayground.closeReason.repeated') }}</option>
              <option value="other">{{ $t('aiPlayground.closeReason.other') }}</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500 dark:text-gray-400">
              <span class="material-symbols-outlined" style="font-size: 20px;">arrow_drop_down</span>
            </div>
          </div>
          <div class="flex gap-3">
            <button
              type="button"
              @click="handleUpdateVerdict"
              :disabled="!selectedAlert || isUpdatingVerdict"
              class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-primary text-white rounded-lg text-sm font-semibold hover:bg-primary/90 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <span v-if="isUpdatingVerdict" class="material-symbols-outlined animate-spin text-base">sync</span>
              <span v-else class="material-symbols-outlined text-base">save</span>
              {{ $t('aiPlayground.saveChanges') }}
            </button>
            <button
              type="button"
              class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-transparent border-2 border-gray-300 dark:border-[#324867] text-gray-700 dark:text-white rounded-lg text-sm font-semibold hover:bg-gray-50 dark:hover:bg-[#1c2533] transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
              :disabled="!selectedAlert"
              @click="handleFineTuneClick"
            >
              <span class="material-symbols-outlined text-base">tune</span>
              {{ $t('aiPlayground.fineTuneAI') }}
            </button>
          </div>
        </div>
        </div>
      </div>
    </section>

    <!-- Retrieval overlay -->
    <Teleport to="body">
      <div
        v-if="showRetrievalOverlay"
        class="fixed inset-0 z-50 flex items-center justify-end"
        @click.self="showRetrievalOverlay = false"
      >
        <!-- Overlay background -->
        <div 
          class="fixed inset-0 bg-black/75"
          @click="showRetrievalOverlay = false"
        ></div>
        
        <!-- Detail panel - with slide-in animation -->
        <Transition name="slide" appear>
          <div
            v-if="showRetrievalOverlay"
            class="relative w-[80vw] h-full bg-white dark:bg-panel-dark shadow-2xl flex flex-col overflow-hidden"
            @click.stop
          >
            <!-- Header -->
            <div class="sticky top-0 z-20 bg-white/80 dark:bg-panel-dark/80 backdrop-blur-sm border-b border-gray-200 dark:border-border-dark">
              <div class="flex items-center justify-between px-6 py-4">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <span class="material-symbols-outlined text-base">travel_explore</span>
                  Retrieval Test
                </h3>
                <button
                  class="p-2 text-gray-500 dark:text-text-light hover:text-gray-900 dark:hover:text-white transition-colors"
                  @click="showRetrievalOverlay = false"
                  aria-label="Close"
                >
                  <span class="material-symbols-outlined">close</span>
                </button>
              </div>
            </div>
            
            <!-- Content -->
            <div class="flex-1 p-6 min-h-0 overflow-hidden flex flex-col">
              <div class="flex-1 flex gap-4 min-h-0">
                <div class="w-full lg:w-1/2 border border-dashed border-gray-300 dark:border-[#324867] rounded-xl bg-gray-50 dark:bg-[#111822] p-4 flex flex-col space-y-4 overflow-y-auto custom-scrollbar min-h-0">
                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-semibold text-gray-900 dark:text-white">{{ $t('alerts.detail.id') }}</label>
                    <textarea
                      ref="alertIdTextarea"
                      class="w-full rounded-lg border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#1c2533] text-sm text-gray-900 dark:text-white p-3 resize-none overflow-hidden"
                      :value="alertId"
                      readonly
                    ></textarea>
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-semibold text-gray-900 dark:text-white">{{ $t('alerts.list.alertTitle') }}</label>
                    <textarea
                      ref="alertSubjectTextarea"
                      class="w-full rounded-lg border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#1c2533] text-sm text-gray-900 dark:text-white p-3 resize-none overflow-hidden"
                      :value="alertSubject"
                      readonly
                    ></textarea>
                  </div>
                  <div class="flex flex-col gap-2">
                    <div class="flex items-center justify-between">
                      <label class="text-sm font-semibold text-gray-900 dark:text-white">{{ $t('alerts.detail.alertContent') }}</label>
                      <button
                        @click="toggleContentFormat"
                        class="flex items-center gap-1.5 px-2 py-1 text-xs font-medium rounded-md transition-colors bg-gray-100 dark:bg-[#233348] text-gray-700 dark:text-white hover:bg-gray-200 dark:hover:bg-[#324867]"
                        :title="contentFormatMode === 'json' ? 'Switch to rich text format' : 'Switch to JSON format'"
                      >
                        <span class="material-symbols-outlined text-sm">
                          {{ contentFormatMode === 'json' ? 'text_fields' : 'code' }}
                        </span>
                        <span>{{ contentFormatMode === 'json' ? 'Rich Text' : 'JSON' }}</span>
                      </button>
                    </div>
                    <textarea
                      ref="alertContentTextarea"
                      :class="[
                        'w-full rounded-lg border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#1c2533] text-sm text-gray-900 dark:text-white p-3 resize-none overflow-hidden',
                        contentFormatMode === 'json' ? 'font-mono' : ''
                      ]"
                      :value="formattedAlertContent"
                      readonly
                    ></textarea>
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-semibold text-gray-900 dark:text-white">{{ $t('aiPlayground.retrievalTest.selectWorkflow') }}</label>
                    <div class="relative">
                      <select
                        v-model="selectedWorkflow"
                        :disabled="loadingWorkflows"
                        class="pl-4 pr-9 appearance-none block w-full rounded-lg border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#1c2533] h-10 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm text-sm disabled:opacity-60 disabled:cursor-not-allowed"
                      >
                        <option value="" disabled>{{ $t('aiPlayground.retrievalTest.selectWorkflow') }}</option>
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
                          class="material-symbols-outlined animate-spin"
                          style="font-size: 20px;"
                        >
                          sync
                        </span>
                        <span
                          v-else
                          class="material-symbols-outlined"
                          style="font-size: 20px;"
                        >
                          arrow_drop_down
                        </span>
                      </div>
                    </div>
                    <button
                      type="button"
                      @click="handleRunWorkflow"
                      :disabled="!selectedWorkflow || selectedWorkflow === '' || runningWorkflow"
                      class="w-full mt-2 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-primary text-white rounded-lg text-sm font-semibold hover:bg-primary/90 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                    >
                      <span
                        v-if="runningWorkflow"
                        class="material-symbols-outlined animate-spin text-base"
                      >
                        sync
                      </span>
                      <span
                        v-else
                        class="material-symbols-outlined text-base"
                      >
                        play_arrow
                      </span>
                      {{ $t('aiPlayground.retrievalTest.runWorkflow') }}
                    </button>
                  </div>
                </div>
                <div class="w-full lg:w-1/2 border border-dashed border-gray-300 dark:border-[#324867] rounded-xl bg-gray-50 dark:bg-[#111822] p-4 flex flex-col space-y-4 overflow-y-auto custom-scrollbar min-h-0">
                  <h3 class="text-sm font-semibold text-gray-900 dark:text-white">{{ $t('aiPlayground.retrievalTest.workflowResult') || 'Workflow Result' }}</h3>
                  <div v-if="!workflowResult && !runningWorkflow" class="flex items-center justify-center h-full text-gray-500 dark:text-gray-400 text-sm">
                    {{ $t('aiPlayground.retrievalTest.noResult') || 'No workflow result yet. Run a workflow to see the output.' }}
                  </div>
                  <div v-else-if="runningWorkflow" class="flex items-center justify-center h-full">
                    <div class="flex flex-col items-center gap-3">
                      <span class="material-symbols-outlined animate-spin text-gray-500 dark:text-gray-400" style="font-size: 32px;">
                        sync
                      </span>
                      <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">{{ $t('common.loading') }}</p>
                    </div>
                  </div>
                  <div v-else-if="workflowResult" class="flex-1 overflow-y-auto">
                    <pre class="text-xs text-gray-900 dark:text-white bg-white dark:bg-[#1c2533] p-4 rounded-lg border border-gray-200 dark:border-[#324867] whitespace-pre-wrap break-words">{{ JSON.stringify(workflowResult, null, 2) }}</pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import DOMPurify from 'dompurify'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts'
import TimeRangePicker from '@/components/common/TimeRangePicker.vue'
import DataTable from '@/components/common/DataTable.vue'
import ClearableSelect from '@/components/common/ClearableSelect.vue'
import { useTimeRangeStorage } from '@/composables/useTimeRangeStorage'
import { getAiAccuracyByModel, getAlertDetail, updateAlert } from '@/api/alerts'
import service from '@/api/axios'
import { useToast } from '@/composables/useToast'

import { formatDateTime, formatDateTimeWithOffset } from '@/utils/dateTime'

const { t } = useI18n()
const toast = useToast()

// Dify workflow API configuration (frontend env vars)
const aiWorkflowApi = import.meta.env.VITE_AI_WORKFLOW_API
const aiWorkflowApiKey = import.meta.env.VITE_PLAYGROUND_WORKFLOWS_KEY
const aiWorkflowRunnerKey = import.meta.env.VITE_PLAYGROUND_RUNNER_KEY

const { selectedTimeRange, customTimeRange } = useTimeRangeStorage('ai-playground', 'last30Days')

const showCharts = ref(true)

// AI accuracy chart state
const aiAccuracyChartRef = ref(null)
const aiAccuracyData = ref([])
const aiAccuracyLoading = ref(false)
let aiAccuracyChartInstance = null
let aiAccuracyResizeListenerBound = false
const aiAccuracyAverage = computed(() => {
  if (!aiAccuracyData.value.length) {
    return '0.0'
  }
  const sum = aiAccuracyData.value.reduce((total, item) => total + (Number(item.accuracy) || 0), 0)
  return (sum / aiAccuracyData.value.length).toFixed(1)
})

// Alert list state
const alerts = ref([])
const loadingAlerts = ref(false)
const dataTableRef = ref(null)
const searchKeywords = ref([])
const currentSearchInput = ref('')
const currentField = ref('')
const showFieldMenu = ref(false)
const searchInputRef = ref(null)
const searchContainerRef = ref(null)
const selectedAlert = ref(null)
const selectedAlertDetail = ref(null)
const selectedAlertLoading = ref(false)
const showRetrievalOverlay = ref(false)
const selectedWorkflow = ref('')
const workflows = ref([])
const loadingWorkflows = ref(false)
const runningWorkflow = ref(false)
const workflowResult = ref(null)
const aiJudgeFilter = ref('all')
const matchFilter = ref('all')
const humanVerdictValue = ref('')
const humanConclusionValue = ref('')
const isUpdatingVerdict = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// Textarea refs for auto-resize
const alertIdTextarea = ref(null)
const alertSubjectTextarea = ref(null)
const alertContentTextarea = ref(null)

const alertId = computed(() => selectedAlert.value?.alert_id || selectedAlert.value?.id || '')
const alertSubject = computed(() => selectedAlert.value?.title || '')
const contentFormatMode = ref('json') // 'json' or 'richtext'

// Helper function to auto-resize textarea
const autoResizeTextarea = (textarea, minHeight = 44, addExtraSpace = false) => {
  if (!textarea) return
  // Store current scroll position
  const scrollTop = textarea.scrollTop
  // Reset height to get accurate scrollHeight
  textarea.style.height = 'auto'
  textarea.style.overflow = 'hidden'
  // Force a reflow to ensure content is measured
  void textarea.offsetHeight
  // Get the actual scroll height including padding
  const scrollHeight = textarea.scrollHeight
  // Calculate extra space only if requested (for content textarea)
  let extraSpace = 0
  if (addExtraSpace) {
    const computedStyle = getComputedStyle(textarea)
    const lineHeight = parseFloat(computedStyle.lineHeight) || 20
    // Add extra space (about 1 line height) to ensure last line is fully visible and readable
    extraSpace = Math.ceil(lineHeight * 1) + 6
  }
  // Set the height, ensuring it's at least the minimum
  const newHeight = Math.max(scrollHeight + extraSpace, minHeight)
  textarea.style.height = newHeight + 'px'
  // Restore scroll position if needed
  textarea.scrollTop = scrollTop
}

const formatDescriptionAsJson = (desc) => {
  if (desc === null || desc === undefined) return ''
  if (typeof desc === 'string') return desc
  // If it's an object, stringify for display
  try {
    return JSON.stringify(desc, null, 2)
  } catch {
    return String(desc)
  }
}

const formatDescriptionAsRichText = (desc) => {
  if (desc === null || desc === undefined) return ''
  if (typeof desc === 'string') {
    // Try to parse as JSON first
    try {
      const parsed = JSON.parse(desc)
      return formatObjectAsRichText(parsed)
    } catch {
      // If not JSON, return as is
      return desc
    }
  }
  // If it's already an object, format it
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

const getRawDescription = () => {
  const detail = selectedAlertDetail.value
  const list = selectedAlert.value
  return (
    detail?.description ??
    detail?.data?.description ??
    detail?.data_object?.description ??
    list?.description ??
    list?.data_object?.description ??
    ''
  )
}

const formattedAlertContent = computed(() => {
  const desc = getRawDescription()
  if (contentFormatMode.value === 'json') {
    return formatDescriptionAsJson(desc)
  } else {
    return formatDescriptionAsRichText(desc)
  }
})

const toggleContentFormat = () => {
  contentFormatMode.value = contentFormatMode.value === 'json' ? 'richtext' : 'json'
  // Force height recalculation after format change
  if (alertContentTextarea.value) {
    // Use double nextTick and delay to ensure content is fully rendered
    nextTick(() => {
      nextTick(() => {
        // Longer delay to ensure content is fully rendered, especially for rich text
        setTimeout(() => {
          autoResizeTextarea(alertContentTextarea.value, 200, true)
          // Recalculate after a short delay to catch any layout changes
          setTimeout(() => {
            autoResizeTextarea(alertContentTextarea.value, 200, true)
          }, 50)
        }, 50)
      })
    })
  }
}

// Watch content changes and auto-resize textareas
watch([alertId, alertIdTextarea], () => {
  nextTick(() => {
    if (alertIdTextarea.value) {
      // Use a smaller minHeight that accounts for padding (p-3 = 12px top + 12px bottom = 24px)
      // Plus minimal space for text, so around 28-30px total
      autoResizeTextarea(alertIdTextarea.value, 28)
    }
  })
}, { immediate: true })

watch([alertSubject, alertSubjectTextarea], () => {
  nextTick(() => {
    if (alertSubjectTextarea.value) {
      autoResizeTextarea(alertSubjectTextarea.value, 64)
    }
  })
}, { immediate: true })

watch([formattedAlertContent, alertContentTextarea, contentFormatMode], () => {
  if (alertContentTextarea.value) {
    // Use double nextTick to ensure DOM is fully updated
    nextTick(() => {
      nextTick(() => {
        // Longer delay to ensure content is fully rendered, especially for rich text
        setTimeout(() => {
          autoResizeTextarea(alertContentTextarea.value, 200, true)
          // Recalculate after a short delay to catch any layout changes
          setTimeout(() => {
            autoResizeTextarea(alertContentTextarea.value, 200, true)
          }, 50)
        }, 50)
      })
    })
  }
}, { immediate: true })

const columns = computed(() => [
  { key: 'createTime', label: t('alerts.list.createTime') },
  { key: 'alertTitle', label: t('alerts.list.alertTitle') },
  { key: 'riskLevel', label: t('alerts.list.riskLevel') },
  { key: 'aiJudge', label: t('alerts.list.aiJudge') },
  { key: 'humanVerdict', label: t('aiPlayground.humanVerdict') },
  { key: 'match', label: t('aiPlayground.match') }
])

const defaultWidths = {
  createTime: 180,
  alertTitle: 360,
  riskLevel: 120,
  aiJudge: 120,
  humanVerdict: 150,
  match: 120
}

const searchFields = computed(() => [
  { value: 'id', label: t('alerts.list.alertId'), icon: 'tag' },
  { value: 'title', label: t('alerts.list.alertTitle'), icon: 'title' },
  { value: 'model_name', label: t('aiPlayground.modelName'), icon: 'smart_toy' }
])

const getFieldLabel = (field) => {
  const fieldObj = searchFields.value.find(f => f.value === field)
  return fieldObj ? fieldObj.label : field
}

const displaySearchInput = computed({
  get() {
    if (currentField.value) {
      const fieldObj = searchFields.value.find(f => f.value === currentField.value)
      const prefix = fieldObj ? `${fieldObj.label}: ` : `${currentField.value}: `
      return prefix + currentSearchInput.value
    }
    return currentSearchInput.value
  },
  set(value) {
    if (currentField.value) {
      const fieldObj = searchFields.value.find(f => f.value === currentField.value)
      const prefix = fieldObj ? `${fieldObj.label}: ` : `${currentField.value}: `
      if (value.startsWith(prefix)) {
        currentSearchInput.value = value.slice(prefix.length)
      } else {
        currentField.value = ''
        currentSearchInput.value = value
      }
    } else {
      currentSearchInput.value = value
    }
  }
})

const getSearchPlaceholder = () => {
  return !currentField.value && searchKeywords.value.length === 0 
    ? (t('alerts.list.searchPlaceholder') || '点击选择搜索字段...') 
    : ''
}

const timeRangeLabel = computed(() => {
  if (selectedTimeRange.value === 'customRange') {
    if (customTimeRange.value && customTimeRange.value.length === 2) {
      const start = new Date(customTimeRange.value[0])
      const end = new Date(customTimeRange.value[1])
      return `${start.toLocaleDateString()} ~ ${end.toLocaleDateString()}`
    }
    return t('common.timeRange.customRange')
  }
  return t(`common.timeRange.${selectedTimeRange.value}`) || t('common.timeRange.last30Days')
})

const wrapAxisLabel = (label) => {
  if (!label) return ''
  const normalized = String(label)
  const chunkSize = normalized.length > 12 ? 12 : 8
  const segments = normalized.match(new RegExp(`.{1,${chunkSize}}`, 'g'))
  return segments ? segments.join('\n') : normalized
}

const ensureAiAccuracyChart = () => {
  if (!aiAccuracyChartInstance && aiAccuracyChartRef.value) {
    aiAccuracyChartInstance = echarts.init(aiAccuracyChartRef.value)
    if (!aiAccuracyResizeListenerBound) {
      window.addEventListener('resize', handleAiAccuracyResize)
      aiAccuracyResizeListenerBound = true
    }
  }
}

const handleAiAccuracyResize = () => {
  if (aiAccuracyChartInstance) {
    aiAccuracyChartInstance.resize()
  }
}

const disposeAiAccuracyChart = () => {
  if (aiAccuracyChartInstance) {
    aiAccuracyChartInstance.dispose()
    aiAccuracyChartInstance = null
  }
  if (aiAccuracyResizeListenerBound) {
    window.removeEventListener('resize', handleAiAccuracyResize)
    aiAccuracyResizeListenerBound = false
  }
}

const updateAiAccuracyChart = () => {
  ensureAiAccuracyChart()
  if (!aiAccuracyChartInstance) {
    return
  }

  aiAccuracyChartInstance.clear()

  const categories = aiAccuracyData.value.map((item) => item.name)
  const accuracies = aiAccuracyData.value.map((item) => item.accuracy)

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderWidth: 0,
      textStyle: { color: '#e2e8f0' },
      padding: [10, 12],
      formatter: (params) => {
        if (!params || params.length === 0) {
          return ''
        }
        const dataIndex = params[0].dataIndex
        const dataPoint = aiAccuracyData.value[dataIndex]
        if (!dataPoint) {
          return `${params[0].name}: ${params[0].value}%`
        }
        return `
          <div style="min-width:140px">
            <div style="font-weight:600;margin-bottom:4px;">${dataPoint.name}</div>
            <div>Accuracy: ${dataPoint.accuracy}%</div>
            <div>Correct: ${dataPoint.correct}/${dataPoint.total}</div>
          </div>
        `
      }
    },
    grid: {
      top: 10,
      right: 12,
      bottom: 6,
      left: 28,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        color: '#cbd5f5',
        fontSize: 11,
        lineHeight: 11,
        margin: 1,
        interval: 0,
        formatter: wrapAxisLabel
      },
      axisLine: {
        lineStyle: { color: '#334155' }
      },
      axisTick: {
        show: true,
        inside: true,
        alignWithLabel: true
      }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: {
        color: '#94a3b8',
        formatter: '{value}%'
      },
      splitLine: {
        lineStyle: { color: '#1f2a37' }
      },
      axisLine: { show: false }
    },
    series: [
      {
        name: t('dashboard.charts.aiAccuracy'),
        type: 'bar',
        data: accuracies,
        barWidth: '45%',
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#34d399' },
            { offset: 0.7, color: '#10b981' },
            { offset: 1, color: '#059669' }
          ])
        }
      }
    ]
  }

  aiAccuracyChartInstance.setOption(option, true)
  setTimeout(() => {
    aiAccuracyChartInstance?.resize()
  }, 0)

  // Bind click to filter alerts by model name
  aiAccuracyChartInstance.off('click')
  aiAccuracyChartInstance.on('click', (params) => {
    if (!params?.name) return
    // Remove existing model/model_name filters before adding the new one
    searchKeywords.value = searchKeywords.value.filter(
      k => k.field !== 'model_name' && k.field !== 'model'
    )
    addKeywordIfMissing('model_name', params.name)
  })
}

const computeSelectedRange = () => {
  if (selectedTimeRange.value === 'customRange' && customTimeRange.value && customTimeRange.value.length === 2) {
    return {
      start: new Date(customTimeRange.value[0]),
      end: new Date(customTimeRange.value[1])
    }
  }

  const end = new Date()
  const start = new Date(end)

  switch (selectedTimeRange.value) {
    case 'last24Hours':
      start.setHours(start.getHours() - 24)
      break
    case 'last3Days':
      start.setDate(start.getDate() - 3)
      break
    case 'last7Days':
      start.setDate(start.getDate() - 7)
      break
    case 'last30Days':
      start.setDate(start.getDate() - 30)
      break
    case 'last3Months':
      start.setMonth(start.getMonth() - 3)
      break
    default:
      start.setDate(start.getDate() - 30)
      break
  }

  return { start, end }
}

const loadAiAccuracyStatistics = async () => {
  aiAccuracyLoading.value = true
  try {
    const { start, end } = computeSelectedRange()
    const response = await getAiAccuracyByModel(start, end, 10)
    const data = response?.data || []
    aiAccuracyData.value = data.map((item) => ({
      name: item.model_name || item.model || 'Unknown',
      accuracy: Number(item.accuracy) || 0,
      correct: item.correct || 0,
      total: item.total || 0
    }))
  } catch (error) {
    console.error('Failed to load AI accuracy statistics:', error)
    aiAccuracyData.value = []
  } finally {
    aiAccuracyLoading.value = false
    await nextTick()
    updateAiAccuracyChart()
  }
}

const getRiskLevelClass = (level) => {
  const classes = {
    fatal: 'bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-200',
    high: 'bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-300',
    medium: 'bg-orange-100 dark:bg-orange-900 text-orange-600 dark:text-orange-300',
    low: 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300',
    tips: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
  }
  return classes[level] || classes.low
}


// Get AI Verdict text
const getAiVerdictText = (alert) => {
  if (!alert) return '-'
  const verificationState = alert.verification_state
  if (verificationState === 'True_Positive') {
    return t('alerts.list.aiJudgeResult.truePositive')
  } else if (verificationState === 'False_Positive') {
    return t('alerts.list.aiJudgeResult.falsePositive')
  }
  return t('alerts.list.aiJudgeResult.unknown')
}

// Get Human Verdict text
const getHumanVerdictText = (alert) => {
  if (!alert) return '-'
  const closeReason = alert.close_reason || alert.closeReason || ''
  if (!closeReason) return '-'
  
  const normalized = String(closeReason).trim().toLowerCase()
  const displayMap = {
    'falsepositive': t('aiPlayground.closeReason.falsePositive'),
    'false detection': t('aiPlayground.closeReason.falsePositive'),
    'false positive': t('aiPlayground.closeReason.falsePositive'),
    'resolved': t('aiPlayground.closeReason.resolved'),
    'repeated': t('aiPlayground.closeReason.repeated'),
    'other': t('aiPlayground.closeReason.other')
  }
  
  return displayMap[normalized] || closeReason
}

// Determine match status between AI Verdict and Human Verdict
// Match: (AI = False_Positive AND Human = "False Detection") OR (AI = True_Positive AND Human = "Resolved")
// Mismatch: (AI = False_Positive AND Human = "Resolved") OR (AI = True_Positive AND Human = "False Detection")
// Empty: Any other combination
const getMatchStatus = (item) => {
  const aiVerdict = item.verification_state
  const humanVerdict = item.close_reason || item.closeReason || ''
  
  // Normalize values (case-insensitive)
  const aiNormalized = aiVerdict ? String(aiVerdict).trim() : ''
  const humanNormalized = humanVerdict ? String(humanVerdict).trim() : ''
  
  // Check if values are in the expected set
  const isAiLow = aiNormalized === 'False_Positive'
  const isAiHigh = aiNormalized === 'True_Positive'
  const isHumanFalseDetection = humanNormalized.toLowerCase() === 'false detection'
  const isHumanResolved = humanNormalized.toLowerCase() === 'resolved'
  
  // If either value is not in the expected set, return empty
  if (!isAiLow && !isAiHigh) return ''
  if (!isHumanFalseDetection && !isHumanResolved) return ''
  
  // Check match conditions
  if ((isAiLow && isHumanFalseDetection) || (isAiHigh && isHumanResolved)) {
    return 'match'
  }
  
  // Check mismatch conditions
  if ((isAiLow && isHumanResolved) || (isAiHigh && isHumanFalseDetection)) {
    return 'mismatch'
  }
  
  // Default to empty for any other combination
  return ''
}

const handleSearchContainerClick = () => {
  if (searchInputRef.value) {
    searchInputRef.value.focus()
  }
}

const addKeywordIfMissing = (field, value) => {
  if (!field || !value) return
  const exists = searchKeywords.value.some(k => k.field === field && k.value === value)
  if (!exists) {
    searchKeywords.value.push({ field, value })
  }
  currentField.value = ''
  currentSearchInput.value = ''
  currentPage.value = 1
  loadAlerts()
}

const addKeyword = () => {
  const keyword = currentSearchInput.value.trim()
  if (keyword && currentField.value) {
    addKeywordIfMissing(currentField.value, keyword)
    showFieldMenu.value = false
  }
}

const removeKeyword = (index) => {
  searchKeywords.value.splice(index, 1)
  currentPage.value = 1
  loadAlerts()
}

const handleKeywordDeleteKey = (event) => {
  if (!currentSearchInput.value && searchKeywords.value.length > 0 && event.key === 'Backspace') {
    searchKeywords.value.pop()
    currentPage.value = 1
    loadAlerts()
  }
}

const selectField = (field) => {
  currentField.value = field
  showFieldMenu.value = false
  nextTick(() => {
    searchInputRef.value?.focus()
  })
}

const handleClickOutside = (event) => {
  const target = event.target
  if (!searchContainerRef.value) return
  if (!searchContainerRef.value.contains(target)) {
    showFieldMenu.value = false
  }
}

const handleSearch = () => {
  addKeyword()
}

const clearSearch = () => {
  searchKeywords.value = []
  currentField.value = ''
  currentSearchInput.value = ''
  currentPage.value = 1
  loadAlerts()
}

const sanitizeHtml = (html = '') => DOMPurify.sanitize(html)

const handleRowClick = async (item) => {
  // Seed with list data (includes close_comment and close_reason) to avoid stale values
  selectedAlert.value = {
    ...item,
    close_comment: item.close_comment || item.closeComment || item?.data_object?.close_comment || null,
    close_reason: item.close_reason || item.closeReason || item?.data_object?.close_reason || null
  }
  selectedAlertDetail.value = null
  selectedAlertLoading.value = true
  try {
    const detailId = item.alert_id || item.id
    const response = await getAlertDetail(detailId)
    const detail =
      response?.data?.data ||
      response?.data ||
      response ||
      null
    selectedAlertDetail.value = detail || null

    const closeComment =
      detail?.close_comment ||
      detail?.data?.close_comment ||
      detail?.data_object?.close_comment ||
      null

    const closeReason =
      detail?.close_reason ||
      detail?.data?.close_reason ||
      detail?.data_object?.close_reason ||
      null

    selectedAlert.value = {
      ...selectedAlert.value,
      close_comment: closeComment ?? selectedAlert.value.close_comment ?? null,
      close_reason: closeReason ?? selectedAlert.value.close_reason ?? null
    }

    // Update form values
    const finalCloseReason = selectedAlert.value.close_reason || selectedAlert.value.closeReason || ''
    humanVerdictValue.value = mapCloseReasonToKey(finalCloseReason)
    humanConclusionValue.value = selectedAlert.value.close_comment || ''
  } catch (error) {
    console.error('Failed to load alert detail:', error)
  } finally {
    selectedAlertLoading.value = false
  }
}

// Map close_reason value to dropdown option key
// Handles both key format (falsePositive) and display format (False detection)
const mapCloseReasonToKey = (closeReason) => {
  if (!closeReason) return ''
  const value = String(closeReason).trim()
  const normalized = value.toLowerCase()
  
  // Direct key match (case-insensitive)
  const keyMap = {
    'falsepositive': 'falsePositive',
    'resolved': 'resolved',
    'repeated': 'repeated',
    'other': 'other'
  }
  
  if (keyMap[normalized]) {
    return keyMap[normalized]
  }
  
  // Display value match (case-insensitive)
  const displayToKey = {
    'false detection': 'falsePositive',
    'false positive': 'falsePositive',
    'resolved': 'resolved',
    'repeated': 'repeated',
    'other': 'other'
  }
  
  return displayToKey[normalized] || ''
}

// Watch selectedAlert to update form values
watch(selectedAlert, (newAlert) => {
  if (newAlert) {
    const closeReason = newAlert.close_reason || newAlert.closeReason || ''
    humanVerdictValue.value = mapCloseReasonToKey(closeReason)
    humanConclusionValue.value = newAlert.close_comment || ''
  } else {
    humanVerdictValue.value = ''
    humanConclusionValue.value = ''
  }
}, { immediate: true })

// Handle update verdict
const handleUpdateVerdict = async () => {
  if (!selectedAlert.value || isUpdatingVerdict.value) return

  const alertId = selectedAlert.value.alert_id || selectedAlert.value.id
  if (!alertId) {
    toast.error(t('alerts.edit.error') || 'Invalid alert ID', 'ERROR')
    return
  }

  try {
    isUpdatingVerdict.value = true

    const updateData = {}
    if (humanVerdictValue.value) {
      updateData.close_reason = humanVerdictValue.value
    }

    await updateAlert(alertId, updateData)

    // Update local state
    if (selectedAlert.value) {
      selectedAlert.value.close_reason = humanVerdictValue.value
    }

    // Refresh the alerts list to reflect changes
    await loadAlerts()

    toast.success(t('aiPlayground.updateVerdictSuccess') || 'Verdict updated successfully', 'SUCCESS')
  } catch (error) {
    console.error('Failed to update verdict:', error)
    const errorMessage = error?.response?.data?.message || error?.message || t('alerts.edit.error') || 'Failed to update verdict'
    toast.error(errorMessage, 'ERROR')
  } finally {
    isUpdatingVerdict.value = false
  }
}

// Trigger Dify workflow API for the selected alert
const triggerAiWorkflow = async () => {
  if (!selectedAlert.value || !aiWorkflowApi || !aiWorkflowApiKey) return

  loadingWorkflows.value = true
  workflows.value = []
  selectedWorkflow.value = ''

  try {
    const alertId = selectedAlert.value.alert_id || selectedAlert.value.id
    if (!alertId) return

    const payload = {
      inputs:{},
      response_mode: 'blocking',
      user:'Pisces AI Playground'
    }

    const response = await fetch(aiWorkflowApi, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${aiWorkflowApiKey}`,
        'Content-Type': 'application/json'
      },
      // Note: In browsers, SSL certificate validation cannot be bypassed.
      // If the certificate is invalid, the request will fail at the network layer.
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    
    // Parse the response structure: data.outputs.results
    if (data?.data?.outputs?.results && Array.isArray(data.data.outputs.results)) {
      workflows.value = data.data.outputs.results.map(result => ({
        id: result.id,
        name: result.name
      }))
    } else {
      workflows.value = []
      console.warn('Unexpected response structure from AI workflow API:', data)
    }
  } catch (error) {
    console.error('Failed to call AI workflow API:', error)
    workflows.value = []
  } finally {
    loadingWorkflows.value = false
  }
}

// Handle Fine-tune AI button click
const handleFineTuneClick = () => {
  if (!selectedAlert.value) return
  showRetrievalOverlay.value = true
  triggerAiWorkflow()
}

// Handle Run Workflow button click
const handleRunWorkflow = async () => {
  if (!selectedWorkflow.value || !aiWorkflowApi || !aiWorkflowRunnerKey || !selectedAlert.value) return

  runningWorkflow.value = true

  try {
    const alertIdValue = selectedAlert.value?.alert_id || selectedAlert.value?.id || ''
    const subjectValue = selectedAlert.value?.title || ''
    const descriptionValue = getRawDescription()
    
    // Convert description to string - if it's an object, stringify it
    const descriptionString = typeof descriptionValue === 'object' && descriptionValue !== null
      ? JSON.stringify(descriptionValue)
      : String(descriptionValue || '')

    const payload = {
      inputs:{
        appid: String(selectedWorkflow.value),
        subject: String(subjectValue),
        description: descriptionString,
        alarm_id: String(alertIdValue)
      },
      response_mode: 'blocking',
      user:'Pisces AI Playground'
    }

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
    workflowResult.value = data
  } catch (error) {
    console.error('Failed to run workflow:', error)
    workflowResult.value = {
      error: true,
      message: error?.message || 'Failed to run workflow',
      details: error
    }
    toast.error('Failed to run workflow', 'ERROR')
  } finally {
    runningWorkflow.value = false
  }
}

const aiItems = computed(() => selectedAlertDetail.value?.ai || [])

const isDarkMode = () => document.documentElement.classList.contains('dark')

const handleFilter = () => {
  currentPage.value = 1
  loadAlerts()
}

// Track word wrap state - DataTable stores it in localStorage with the storage key
const getWordWrapState = () => {
  const stored = localStorage.getItem('datatable-wordwrap-ai-playground-alerts-table-columns')
  return stored !== null ? stored === 'true' : true
}
const wordWrapState = ref(getWordWrapState())

const isWordWrapEnabled = computed(() => wordWrapState.value)

const handleToggleWordWrap = () => {
  if (dataTableRef.value?.toggleWordWrap) {
    dataTableRef.value.toggleWordWrap()
    // Update local state immediately
    wordWrapState.value = !wordWrapState.value
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadAlerts()
}

const handlePageSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
  loadAlerts()
}

const buildConditions = () => {
  return searchKeywords.value
    .filter(k => k.field && k.value)
    .map(k => ({ [k.field]: k.value }))
}

const loadAlerts = async () => {
  loadingAlerts.value = true
  try {
    const { start, end } = computeSelectedRange()
    const params = {
      action: 'list_local',
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value,
      conditions: buildConditions(),
      start_time: formatDateTimeWithOffset(start),
      end_time: formatDateTimeWithOffset(end)
    }
    const response = await service.post('/alerts', params)
    const raw = response.data || []

    const normalizeSeverity = (value) => {
      if (value == null) return 'medium'
      const map = {
        fatal: 'fatal', critical: 'fatal', '1': 'fatal',
        high: 'high', '2': 'high',
        medium: 'medium', '3': 'medium',
        low: 'low', '4': 'low',
        tips: 'tips', info: 'tips', '5': 'tips'
      }
      return map[String(value).toLowerCase()] || 'medium'
    }

    const normalizeStatus = (value) => {
      if (!value) return 'open'
      return String(value).toLowerCase()
    }

    const normalized = raw.map(item => ({
      ...item,
      riskLevel: normalizeSeverity(item.riskLevel || item.severity),
      status: normalizeStatus(item.status || item.handle_status),
      model_name: item.model_name || item.model,
      close_comment: item.close_comment || item.closeComment || item?.data_object?.close_comment || null,
      close_reason: item.close_reason || item.closeReason || item?.data_object?.close_reason || null
    }))

    // Client-side filters
    let filtered = normalized
    
    const modelKeyword = searchKeywords.value.find(k => k.field === 'model_name' || k.field === 'model')
    if (modelKeyword) {
      filtered = filtered.filter(a => {
        const val = a.model_name || a.model || a?.extend_properties?.model_name || a?.extend_properties?.model
        return val && String(val).toLowerCase() === String(modelKeyword.value).toLowerCase()
      })
    }

    if (aiJudgeFilter.value !== 'all') {
      filtered = filtered.filter(a => 
        (a.verification_state || a.verificationState) === aiJudgeFilter.value
      )
    }

    if (matchFilter.value !== 'all') {
      filtered = filtered.filter(a => {
        const matchStatus = getMatchStatus(a)
        return matchFilter.value === 'empty' ? matchStatus === '' : matchStatus === matchFilter.value
      })
    }

    alerts.value = filtered
    total.value = response.total || filtered.length || 0
  } catch (error) {
    console.error('Failed to load alerts:', error)
    alerts.value = []
    total.value = 0
  } finally {
    loadingAlerts.value = false
  }
}

const handleTimeRangeChange = (rangeKey) => {
  selectedTimeRange.value = rangeKey
  if (rangeKey !== 'customRange') {
    handleRefresh()
  }
}

const handleCustomRangeChange = (range) => {
  customTimeRange.value = range
  if (selectedTimeRange.value === 'customRange' && range && range.length === 2) {
    handleRefresh()
  }
}

const handleRefresh = async () => {
  await Promise.all([
    loadAiAccuracyStatistics(),
    loadAlerts()
  ])
}

watch([currentPage, pageSize], () => {
  loadAlerts()
})

watch(showRetrievalOverlay, (isOpen) => {
  if (isOpen) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
    // Reset workflow selection when overlay closes
    selectedWorkflow.value = ''
    workflows.value = []
    loadingWorkflows.value = false
    workflowResult.value = null
  }
})

// Watch selectedAlert to constrain table columns when detail panel opens/closes
watch(selectedAlert, () => {
  // Reset workflow selection when a new alert is selected
  selectedWorkflow.value = ''
  workflows.value = []
  loadingWorkflows.value = false
  workflowResult.value = null
  
  // Wait for layout to update, then constrain columns
  nextTick(() => {
    setTimeout(() => {
      if (dataTableRef.value?.constrainColumns) {
        dataTableRef.value.constrainColumns()
      }
    }, 100)
  })
})

onMounted(() => {
  ensureAiAccuracyChart()
  document.addEventListener('click', handleClickOutside)
  // Sync word wrap state with DataTable
  wordWrapState.value = getWordWrapState()
  handleRefresh()
})

onBeforeUnmount(() => {
  disposeAiAccuracyChart()
  document.removeEventListener('click', handleClickOutside)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.ai-agent__html {
  max-width: 100%;
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
}

.ai-agent__html :deep(pre) {
  background: #f5f5f5;
  border: 1px solid #cccccc;
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
  background: #0f172a !important;
  border: 1px solid rgba(94, 114, 164, 0.45) !important;
  color: #e2e8f0 !important;
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

/* Slide animation for retrieval overlay */
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

/* Custom scrollbar for retrieval overlay */
.custom-scrollbar {
  /* Firefox */
  scrollbar-width: thin;
  scrollbar-color: rgba(59, 130, 246, 0.3) transparent;
}

/* WebKit browsers (Chrome, Safari, Edge) */
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
</style>

