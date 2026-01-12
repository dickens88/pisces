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
          :disabled="loadingAlerts || aiAccuracyLoading || aiDecisionLoading"
          class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-200 dark:disabled:hover:bg-[#2a3546] h-10"
          :title="$t('common.refresh') || 'Refresh'"
        >
          <span
            class="material-symbols-outlined text-base"
            :class="{ 'animate-spin': loadingAlerts || aiAccuracyLoading || aiDecisionLoading }"
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
      class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6"
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
      
      <div class="flex flex-col rounded-xl border border-gray-200 dark:border-[#324867]/50 bg-white dark:bg-[#19222c] p-0">
        <div class="flex justify-between items-center p-3 pt-2">
          <p class="text-gray-900 dark:text-white text-lg font-semibold">{{ $t('aiPlayground.aiDecisionAnalysis') }}</p>
          <span class="text-xs text-gray-600 dark:text-white/60">{{ timeRangeLabel }}</span>
        </div>
        <div class="flex flex-col gap-1 px-3 pb-2">
          <span class="text-gray-600 dark:text-white/60 text-sm font-medium uppercase tracking-wide">
            {{ $t('aiPlayground.totalDecisions') || 'Total Decisions' }}
          </span>
          <span class="text-gray-900 dark:text-white text-3xl font-bold tracking-tight">
            {{ aiDecisionTotal }}
          </span>
        </div>
        <div class="relative h-52">
          <div
            v-if="aiDecisionLoading"
            class="absolute inset-0 flex items-center justify-center text-white/50 text-sm"
          >
            {{ $t('common.loading') }}
          </div>
          <div
            v-else-if="aiDecisionData.length === 0"
            class="absolute inset-0 flex items-center justify-center text-white/50 text-sm"
          >
            {{ $t('dashboard.charts.noData') }}
          </div>
          <div
            v-show="!aiDecisionLoading && aiDecisionData.length > 0"
            ref="aiDecisionChartRef"
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
          <!-- AI Judgment Filter Switch - moved before search box -->
          <div class="flex-shrink-0">
            <div class="flex items-center bg-gray-100 dark:bg-[#233348] p-0.5 rounded-lg h-10">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap px-2">
                {{ $t('aiPlayground.filter.aiJudgmentLabel') }}
              </span>
              <button
                @click="toggleAiJudgmentFilter"
                :class="[
                  'group relative px-2.5 py-1 rounded-md transition-all duration-300 h-full flex items-center justify-center',
                  isAiJudgmentFilterActive
                    ? 'text-white bg-primary hover:bg-primary/90 shadow-sm'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
                ]"
                :title="aiJudgmentFilterText"
              >
                <span
                  class="material-symbols-outlined"
                  :class="isAiJudgmentFilterActive ? '' : 'text-primary'"
                  style="font-variation-settings: 'FILL' 1, 'wght' 600, 'GRAD' 200, 'opsz' 24;"
                >
                  smart_toy
                </span>
                <div class="absolute top-[-28px] left-1/2 -translate-x-1/2 w-max pointer-events-none z-10">
                  <span class="text-xs font-medium text-gray-600 dark:text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap bg-white dark:bg-[#111822] px-2 py-1 rounded shadow-sm border border-gray-200 dark:border-[#324867]">
                    {{ aiJudgmentFilterText }}
                  </span>
                </div>
              </button>
            </div>
          </div>

          <div class="relative w-full max-w-md" ref="searchContainerRef">
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
                @blur="handleSearchBlur"
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

          <div class="relative min-w-[120px] max-w-[12rem]">
            <ClearableSelect
              v-model="humanJudgeFilter"
              clear-value="all"
              @change="handleFilter"
            >
              <option value="all">{{ $t('aiPlayground.humanJudgeFilter.all') }}</option>
              <option value="False detection">{{ $t('aiPlayground.closeReason.falsePositive') }}</option>
              <option value="Resolved">{{ $t('aiPlayground.closeReason.resolved') }}</option>
              <option value="Repeated">{{ $t('aiPlayground.closeReason.repeated') }}</option>
              <option value="Other">{{ $t('aiPlayground.closeReason.other') }}</option>
            </ClearableSelect>
          </div>

          <div class="relative min-w-[120px] max-w-[12rem]">
            <ClearableSelect
              v-model="matchFilter"
              clear-value="all"
              @change="handleFilter"
            >
              <option value="all">{{ $t('aiPlayground.matchFilter.all') }}</option>
              <option value="TT">{{ $t('aiPlayground.matchFilter.TT') }}</option>
              <option value="FP">{{ $t('aiPlayground.matchFilter.FP') }}</option>
              <option value="FN">{{ $t('aiPlayground.matchFilter.FN') }}</option>
              <option value="empty">{{ $t('aiPlayground.matchFilter.empty') }}</option>
            </ClearableSelect>
          </div>

          <!-- More actions button -->
          <div class="relative">
            <button
              @click="showMoreMenu = !showMoreMenu"
              class="more-menu-button flex items-center justify-center rounded-lg h-10 w-10 bg-gray-100 dark:bg-[#233348] text-gray-700 dark:text-white hover:bg-gray-200 dark:hover:bg-[#324867] transition-colors"
              :title="$t('common.more')"
            >
              <span class="material-symbols-outlined text-base">more_vert</span>
            </button>
            <!-- Dropdown menu -->
            <div
              v-if="showMoreMenu"
              class="more-menu-dropdown absolute right-0 top-full mt-2 bg-white dark:bg-[#233348] border border-gray-200 dark:border-[#324867] rounded-lg shadow-lg z-50 min-w-[180px]"
            >
              <button
                @click="handleToggleWordWrap"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867]"
              >
                <span class="material-symbols-outlined text-base">
                  {{ isWordWrapEnabled ? 'wrap_text' : 'text_fields' }}
                </span>
                <span>{{ isWordWrapEnabled ? $t('common.wordWrap') : $t('common.singleLine') }}</span>
              </button>
            </div>
          </div>
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
            <div class="flex items-center gap-2 flex-wrap">
              <span
                :class="[
                  'text-xs font-medium px-2.5 py-0.5 rounded-full inline-flex items-center justify-center',
                  getRiskLevelClass(item.riskLevel)
                ]"
                :title="$t(`common.severity.${item.riskLevel}`)"
              >
                {{ $t(`common.severity.${item.riskLevel}`) }}
              </span>
            </div>
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
                {{ getHumanVerdictText(item) }}
              </span>
            </div>
          </template>
          <template #cell-match="{ item }">
            <div class="flex items-center justify-center">
              <template v-for="(display, index) in [getMatchStatusDisplay(getMatchStatus(item))]" :key="index">
                <span
                  :class="[
                    'material-symbols-outlined flex-shrink-0',
                    display.colorClass
                  ]"
                  :style="getMatchStatus(item) ? 'font-size: 20px; font-variation-settings: \'FILL\' 1, \'wght\' 600, \'GRAD\' 200, \'opsz\' 24;' : 'font-size: 20px; font-variation-settings: \'FILL\' 0, \'wght\' 400, \'GRAD\' 0, \'opsz\' 24;'"
                  :title="display.title"
                >
                  {{ display.icon }}
                </span>
              </template>
            </div>
          </template>
        </DataTable>
      </div>

      <div v-if="selectedAlert" class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-xl min-h-[300px] flex flex-col">
        <!-- Header with title and close button -->
        <div class="flex items-center justify-between px-5 pt-5 pb-4 border-b border-gray-200 dark:border-[#324867] gap-3">
          <div class="flex items-center gap-2 flex-1 min-w-0">
            <button
              @click="openAlertDetailInNewWindow"
              class="p-1.5 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-[#1c2533] rounded-md transition-colors flex-shrink-0"
              :title="$t('common.openInNewWindow') || 'Open in new window'"
            >
              <span class="material-symbols-outlined text-lg">open_in_new</span>
            </button>
            <h2 class="text-base font-semibold text-gray-900 dark:text-white truncate">
              {{ $t('alerts.detail.title') }} #{{ alertId }}
            </h2>
          </div>
          <button
            @click="selectedAlert = null"
            class="p-1.5 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-[#1c2533] rounded-md transition-colors flex-shrink-0"
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
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1.5">
                <span class="material-symbols-outlined text-sm">gavel</span>
                {{ $t('aiPlayground.verdict') }}:
              </span>
              <span
                class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-300"
              >
                {{ getAiVerdictText(selectedAlert) }}
              </span>
            </div>
          </div>
          
          <!-- Human Judgment -->
          <div class="bg-gray-50 dark:bg-[#1c2533] border border-gray-200 dark:border-[#324867] rounded-lg p-4">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
              <span class="material-symbols-outlined text-base">person</span>
              {{ $t('aiPlayground.humanJudgment') }}
            </h3>
            <div class="space-y-2">
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1.5">
                  <span class="material-symbols-outlined text-sm">gavel</span>
                  {{ $t('aiPlayground.verdict') }}:
                </span>
                <span
                  class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-300"
                >
                  {{ getHumanVerdictText(selectedAlert) }}
                </span>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1.5">
                  <span class="material-symbols-outlined text-sm">badge</span>
                  {{ $t('alerts.list.actor') }}:
                </span>
                <UserAvatar :name="selectedAlert?.actor || selectedAlert?.creator || ''" />
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
                <div>
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <span class="material-symbols-outlined text-base">tune</span>
                    {{ $t('aiPlayground.fineTuneAI') }}
                  </h3>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ $t('aiPlayground.fineTuneSubtitle') || 'Train and debug AI models' }}</p>
                </div>
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
              <div class="flex-1 flex gap-6 min-h-0">
                <!-- Left Panel: Input Alert Information -->
                <div class="w-full lg:w-1/2 flex flex-col min-h-0">
                  <h4 class="text-base font-semibold text-gray-900 dark:text-white mb-4">{{ $t('aiPlayground.retrievalTest.inputAlertInfo') || 'Input Alert Information' }}</h4>
                  
                  <div class="flex-1 flex flex-col gap-4 overflow-y-auto custom-scrollbar min-h-0">
                    <!-- Alert ID -->
                    <div class="flex flex-col gap-2">
                      <label class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('alerts.detail.id') }}</label>
                      <input
                        type="text"
                        class="w-full rounded-lg border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#1c2533] text-sm text-gray-900 dark:text-white px-3 py-2"
                        :value="alertId"
                        readonly
                      />
                    </div>

                    <!-- Title -->
                    <div class="flex flex-col gap-2">
                      <label class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('alerts.list.alertTitle') }}</label>
                      <textarea
                        ref="overlayAlertTitleTextarea"
                        class="w-full rounded-lg border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#1c2533] text-sm text-gray-900 dark:text-white px-3 py-2 resize-none overflow-y-hidden"
                        :value="alertSubject"
                        readonly
                      ></textarea>
                    </div>

                    <!-- Close Comment -->
                    <div class="flex flex-col gap-2">
                      <label class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('aiPlayground.retrievalTest.comments') || 'Close Comment' }}</label>
                      <textarea
                        class="w-full rounded-lg border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#1c2533] text-sm text-gray-900 dark:text-white p-3 resize-none min-h-[100px]"
                        :value="humanConclusionValue || ''"
                        readonly
                      ></textarea>
                    </div>

                    <!-- Description -->
                    <div class="flex flex-col gap-2">
                      <label class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('alerts.detail.alertContent') }}</label>
                      <div class="flex gap-2 mb-2">
                        <button
                          @click="contentFormatMode = 'json'"
                          :class="[
                            'px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
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
                            'px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
                            contentFormatMode === 'richtext'
                              ? 'bg-primary text-white'
                              : 'bg-gray-100 dark:bg-[#233348] text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-[#324867]'
                          ]"
                        >
                          Rendered View
                        </button>
                      </div>
                      <textarea
                        ref="alertContentTextarea"
                        :class="[
                          'w-full rounded-lg border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#1c2533] text-sm text-gray-900 dark:text-white p-3 resize-none overflow-y-auto h-[300px]',
                          contentFormatMode === 'json' ? 'font-mono' : ''
                        ]"
                        :value="formattedAlertContent"
                        readonly
                      ></textarea>
                    </div>
                  </div>
                </div>

                <!-- Right Panel: AI Agent Workspace -->
                <div class="w-full lg:w-1/2 flex flex-col min-h-0">
                  <h4 class="text-base font-semibold text-gray-900 dark:text-white mb-4">{{ $t('aiPlayground.retrievalTest.aiAgentWorkspace') || 'AI Agent Workspace' }}</h4>
                  
                  <div class="flex-1 flex flex-col gap-4 overflow-y-auto custom-scrollbar min-h-0">
                    <!-- Inputs for Current Run -->
                    <div class="flex flex-col gap-2">
                      <h5 class="text-sm font-semibold text-gray-900 dark:text-white">{{ $t('aiPlayground.retrievalTest.inputsForCurrentRun') || 'Inputs for Current Run' }}</h5>
                      <p class="text-xs text-gray-600 dark:text-gray-400 mb-2">{{ $t('aiPlayground.retrievalTest.allInputsIncluded') || 'All inputs from the left panel are included for AI analysis.' }}</p>
                      <div class="bg-gray-100 dark:bg-[#1c2533] border border-gray-200 dark:border-[#324867] rounded-lg p-4 min-h-[80px] flex items-center justify-center">
                          <div class="text-xs text-gray-500 dark:text-gray-400 text-center">
                            <div class="mb-1">{{ $t('alerts.detail.id') }}: {{ alertId }}</div>
                            <div class="mb-1">{{ $t('alerts.list.alertTitle') }}: {{ alertSubject }}</div>
                            <div>{{ $t('alerts.detail.alertContent') }}: Included</div>
                          </div>
                      </div>
                    </div>

                    <!-- Model Selection -->
                    <div class="flex flex-col gap-2">
                      <label class="text-sm font-semibold text-gray-900 dark:text-white">{{ $t('aiPlayground.retrievalTest.modelSelection') || 'Model Selection' }}</label>
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
                    </div>

                    <!-- Run Analysis Button -->
                    <button
                      type="button"
                      @click="handleRunWorkflow"
                      :disabled="!selectedWorkflow || selectedWorkflow === '' || runningWorkflow"
                      class="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-primary text-white rounded-lg text-sm font-semibold hover:bg-primary/90 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
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
                      {{ $t('aiPlayground.retrievalTest.runAnalysis') || 'Run Analysis' }}
                    </button>

                    <!-- AI Response Feed -->
                    <div class="flex flex-col gap-2">
                      <h5 class="text-sm font-semibold text-gray-900 dark:text-white">{{ $t('aiPlayground.retrievalTest.aiResponseFeed') || 'AI Response Feed' }}</h5>
                      <div class="flex-1 overflow-y-auto">
                        <div v-if="workflowResult?.error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-3">
                          <p class="text-sm font-semibold text-red-600 dark:text-red-400 mb-2">{{ workflowResult.message || 'Error' }}</p>
                          <pre class="text-xs text-red-600 dark:text-red-400 whitespace-pre-wrap break-words">{{ JSON.stringify(workflowResult.details, null, 2) }}</pre>
                        </div>

                        <div v-if="runningWorkflow" class="flex items-center justify-center py-4">
                          <div class="flex flex-col items-center gap-3">
                            <span class="material-symbols-outlined animate-spin text-gray-500 dark:text-gray-400" style="font-size: 32px;">
                              sync
                            </span>
                            <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">{{ $t('common.loading') }}</p>
                          </div>
                        </div>

                        <div v-if="workflowRuns.length === 0 && !runningWorkflow" class="text-center text-gray-500 dark:text-gray-400 text-sm py-8">
                          {{ $t('aiPlayground.retrievalTest.noResult') || 'No workflow result yet. Run a workflow to see the output.' }}
                        </div>

                        <div v-if="workflowRuns.length > 0" class="space-y-3">
                          <div
                            v-for="run in workflowRuns.slice().reverse()"
                            :key="run.id"
                            class="bg-white dark:bg-[#1c2533] border border-gray-200 dark:border-[#324867] rounded-lg p-4 cursor-pointer transition hover:border-primary/60"
                            @click="toggleRunExpanded(run.id)"
                          >
                            <div class="flex items-start justify-between gap-3">
                              <div class="flex flex-col gap-1">
                                <span class="text-xs font-medium text-gray-600 dark:text-gray-400">{{ run.modelName || 'Model' }}</span>
                                <div class="flex items-center gap-2">
                                  <span class="text-xs uppercase text-gray-500 dark:text-gray-400">Verdict:</span>
                                  <span class="text-sm font-semibold" :class="run.parsed?.isThreat ? 'text-primary' : 'text-gray-700 dark:text-gray-200'">
                                    {{ run.parsed?.isThreat || (run.text ? 'View details' : 'No verdict') }}
                                  </span>
                                </div>
                                <div v-if="run.parsed?.confidence" class="text-xs text-gray-500 dark:text-gray-400">
                                  Confidence Score: {{ run.parsed.confidence }}
                                </div>
                              </div>
                              <div class="flex flex-col items-end gap-1">
                                <span class="text-xs text-gray-500 dark:text-gray-400">{{ formatRunTimestamp(run.timestamp) }}</span>
                                <span
                                  class="material-symbols-outlined text-gray-400 dark:text-gray-500 transition-transform"
                                  :class="run.expanded ? 'rotate-180' : ''"
                                >
                                  expand_more
                                </span>
                              </div>
                            </div>

                            <div
                              v-if="run.expanded"
                              class="mt-3 space-y-2 border-t border-gray-200 dark:border-[#324867] pt-3"
                            >
                              <div
                                v-if="run.parsed?.isThreat"
                                class="border border-gray-200 dark:border-[#324867] rounded-lg p-3 bg-gray-50 dark:bg-[#192233]"
                              >
                                <div class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1">
                                  [Is Threat]
                                </div>
                                <div class="text-sm text-gray-900 dark:text-white whitespace-pre-wrap break-words">
                                  {{ run.parsed.isThreat }}
                                </div>
                              </div>

                              <div
                                v-if="run.parsed?.confidence"
                                class="border border-gray-200 dark:border-[#324867] rounded-lg p-3 bg-gray-50 dark:bg-[#192233]"
                              >
                                <div class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1">
                                  [Confidence Score]
                                </div>
                                <div class="text-sm text-gray-900 dark:text-white whitespace-pre-wrap break-words">
                                  {{ run.parsed.confidence }}
                                </div>
                              </div>

                              <div
                                v-if="run.parsed?.reason"
                                class="border border-gray-200 dark:border-[#324867] rounded-lg p-3 bg-gray-50 dark:bg-[#192233]"
                              >
                                <div class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1">
                                  [Reason]
                                </div>
                                <div class="text-sm text-gray-900 dark:text-white whitespace-pre-wrap break-words">
                                  {{ run.parsed.reason }}
                                </div>
                              </div>

                              <div
                                v-if="!run.parsed?.hasAny && run.text"
                                class="text-sm text-gray-900 dark:text-white whitespace-pre-wrap break-words"
                              >
                                {{ run.text }}
                              </div>

                              <div class="bg-gray-50 dark:bg-[#111822] border border-dashed border-gray-200 dark:border-[#324867] rounded-lg p-3">
                                <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Raw result</p>
                                <pre class="text-xs text-gray-700 dark:text-gray-300 whitespace-pre-wrap break-words">{{ JSON.stringify(run.raw, null, 2) }}</pre>
                              </div>
                            </div>
                          </div>
                        </div>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import DOMPurify from 'dompurify'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import * as echarts from 'echarts'
import TimeRangePicker from '@/components/common/TimeRangePicker.vue'
import DataTable from '@/components/common/DataTable.vue'
import ClearableSelect from '@/components/common/ClearableSelect.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import { useTimeRangeStorage } from '@/composables/useTimeRangeStorage'
import { getAiAccuracyByModel, getAiDecisionAnalysis, getAlertDetail, updateAlert } from '@/api/alerts'
import service from '@/api/axios'
import { useToast } from '@/composables/useToast'

import { formatDateTime, formatDateTimeWithOffset } from '@/utils/dateTime'

const { t } = useI18n()
const toast = useToast()
const router = useRouter()
const route = useRoute()

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
const aiAccuracyChartInstance = { value: null }
const aiAccuracyResizeListenerBound = { value: false }
const aiAccuracyAverage = computed(() => {
  if (!aiAccuracyData.value.length) return '0.0'
  const sum = aiAccuracyData.value.reduce((total, item) => total + (Number(item.accuracy) || 0), 0)
  return (sum / aiAccuracyData.value.length).toFixed(1)
})

// AI decision analysis chart state
const aiDecisionChartRef = ref(null)
const aiDecisionData = ref([])
const aiDecisionLoading = ref(false)
const aiDecisionChartInstance = { value: null }
const aiDecisionResizeListenerBound = { value: false }
const aiDecisionTotal = computed(() => {
  if (!aiDecisionData.value.length) return 0
  return aiDecisionData.value.reduce((total, item) => total + (Number(item.value) || 0), 0)
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
const workflowRuns = ref([]) // store last 3 runs while overlay is open
const aiJudgeFilter = ref('all')
const humanJudgeFilter = ref('all')
const matchFilter = ref('all')
const humanVerdictValue = ref('')
const humanConclusionValue = ref('')
const isUpdatingVerdict = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const showMoreMenu = ref(false)
const isAiJudgmentFilterActive = ref(true) // Default to enabled

// Textarea refs for auto-resize
const alertIdTextarea = ref(null)
const alertSubjectTextarea = ref(null)
const alertContentTextarea = ref(null)
const overlayAlertTitleTextarea = ref(null)

const alertId = computed(() => selectedAlert.value?.alert_id || selectedAlert.value?.id || '')
const alertSubject = computed(() => selectedAlert.value?.title || '')
const contentFormatMode = ref('json') // 'json' or 'richtext'

// Match status configuration - centralized configuration for reuse
const MATCH_STATUS_CONFIG = {
  TT: {
    dbValue: 'TT',
    filterValue: 'TT',
    chartName: 'TT',
    color: '#10b981',
    i18nKey: 'aiPlayground.matchFilter.TT'
  },
  FP: {
    dbValue: 'FP',
    filterValue: 'FP',
    chartName: 'FP',
    color: '#ef4444',
    i18nKey: 'aiPlayground.matchFilter.FP'
  },
  FN: {
    dbValue: 'FN',
    filterValue: 'FN',
    chartName: 'FN',
    color: '#f59e0b',
    i18nKey: 'aiPlayground.matchFilter.FN'
  },
  Empty: {
    dbValue: null,
    filterValue: 'empty',
    chartName: 'Empty',
    color: '#94a3b8',
    i18nKey: 'aiPlayground.matchFilter.empty'
  }
}

// Helper function to get match status config
const getMatchStatusConfig = (status) => {
  if (!status) return MATCH_STATUS_CONFIG.Empty
  const upperStatus = String(status).toUpperCase()
  if (upperStatus === 'TT' || upperStatus === 'FP' || upperStatus === 'FN') {
    return MATCH_STATUS_CONFIG[upperStatus]
  }
  return MATCH_STATUS_CONFIG.Empty
}

// Map chart data name to filter value
const chartNameToFilterValue = (chartName) => {
  const config = Object.values(MATCH_STATUS_CONFIG).find(c => c.chartName === chartName)
  return config ? config.filterValue : null
}

// Open alert detail in new window
const openAlertDetailInNewWindow = () => {
  if (!alertId.value) return
  const route = router.resolve({ path: `/alerts/${alertId.value}` })
  const url = window.location.origin + route.href
  window.open(url, '_blank')
}

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

// Auto-resize Fine-tune panel alert title textarea
watch([alertSubject, overlayAlertTitleTextarea], () => {
  nextTick(() => {
    if (overlayAlertTitleTextarea.value) {
      // Slightly larger minimum height so it can grow to two lines comfortably
      autoResizeTextarea(overlayAlertTitleTextarea.value, 40)
    }
  })
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

// Chart management helper
const useChartManager = (chartRef, chartInstance, resizeListenerBound) => {
  const ensure = () => {
    if (!chartInstance.value && chartRef.value) {
      chartInstance.value = echarts.init(chartRef.value)
      if (!resizeListenerBound.value) {
        const resizeHandler = () => chartInstance.value?.resize()
        window.addEventListener('resize', resizeHandler)
        resizeListenerBound.value = true
        chartInstance.value._resizeHandler = resizeHandler
      }
    }
  }
  
  const dispose = () => {
    if (chartInstance.value) {
      if (chartInstance.value._resizeHandler) {
        window.removeEventListener('resize', chartInstance.value._resizeHandler)
      }
      chartInstance.value.dispose()
      chartInstance.value = null
    }
    resizeListenerBound.value = false
  }
  
  return { ensure, dispose }
}

const aiAccuracyChartManager = useChartManager(
  aiAccuracyChartRef,
  aiAccuracyChartInstance,
  aiAccuracyResizeListenerBound
)

const aiDecisionChartManager = useChartManager(
  aiDecisionChartRef,
  aiDecisionChartInstance,
  aiDecisionResizeListenerBound
)

const updateAiAccuracyChart = () => {
  aiAccuracyChartManager.ensure()
  if (!aiAccuracyChartInstance.value) return
  
  aiAccuracyChartInstance.value.clear()

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
        return `<div style="min-width:140px">
          <div style="font-weight:600;margin-bottom:4px;">${dataPoint.name}</div>
          <div>Accuracy: ${dataPoint.accuracy}%</div>
          <div>Correct: ${dataPoint.correct}/${dataPoint.total}</div>
        </div>`
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

  aiAccuracyChartInstance.value.setOption(option, true)
  setTimeout(() => aiAccuracyChartInstance.value?.resize(), 0)

  // Bind click to filter alerts by model name
  aiAccuracyChartInstance.value.off('click')
  aiAccuracyChartInstance.value.on('click', (params) => {
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
    const conditions = buildConditions()
    const response = await getAiAccuracyByModel(start, end, 10, conditions)
    aiAccuracyData.value = (response?.data || []).map((item) => ({
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

const updateAiDecisionChart = () => {
  aiDecisionChartManager.ensure()
  if (!aiDecisionChartInstance.value) return
  
  aiDecisionChartInstance.value.clear()

  // Build pie data using centralized config
  const isDark = isDarkMode()
  const pieData = aiDecisionData.value.map((item) => {
    const statusConfig = getMatchStatusConfig(item.name)
    // Use lighter/more vibrant colors for light mode, darker for dark mode
    let color = statusConfig.color
    if (!isDark) {
      // Adjust colors for light mode - use softer, more pleasant colors
      const colorMap = {
        '#10b981': '#94d2bd', // TT - slightly deeper green for better contrast
        '#ef4444': '#dc2626', // FP - slightly deeper red for better contrast
        '#f59e0b': '#d97706', // FN - slightly deeper orange for better contrast
        '#94a3b8': '#6b7280'  // Empty - darker gray for better visibility
      }
      color = colorMap[statusConfig.color] || statusConfig.color
    }
    return {
      name: t(statusConfig.i18nKey),
      value: item.value,
      itemStyle: { color },
      // Store original name for click event
      originalName: item.name
    }
  })

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: isDark ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.98)',
      borderWidth: isDark ? 0 : 1,
      borderColor: isDark ? 'transparent' : '#d1d5db',
      textStyle: { color: isDark ? '#e2e8f0' : '#111827' },
      padding: [10, 12],
      extraCssText: isDark ? '' : 'box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);',
      formatter: (params) => {
        if (!params) return ''
        const total = aiDecisionTotal.value
        const percent = total > 0 ? ((params.value / total) * 100).toFixed(1) : '0.0'
        return `<div style="min-width:140px">
          <div style="font-weight:600;margin-bottom:4px;">${params.name}</div>
          <div>Count: ${params.value}</div>
          <div>Percentage: ${percent}%</div>
        </div>`
      }
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: {
        color: isDark ? '#cbd5f5' : '#374151',
        fontSize: 11,
        fontWeight: isDark ? 'normal' : '500'
      },
      itemGap: 8
    },
    series: [
      {
        name: t('aiPlayground.aiDecisionAnalysis'),
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 4,
          borderColor: isDark ? '#19222c' : '#ffffff',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 12,
            fontWeight: 'bold',
            color: isDark ? '#e2e8f0' : '#1f2937'
          }
        },
        labelLine: {
          show: false
        },
        data: pieData
      }
    ]
  }

  aiDecisionChartInstance.value.setOption(option, true)
  setTimeout(() => aiDecisionChartInstance.value?.resize(), 0)

  // Bind click to filter alerts by match status
  aiDecisionChartInstance.value.off('click')
  aiDecisionChartInstance.value.on('click', (params) => {
    if (!params?.data?.originalName) return
    
    const filterValue = chartNameToFilterValue(params.data.originalName)
    if (filterValue) {
      // Set match filter and trigger filter
      matchFilter.value = filterValue
      handleFilter()
    }
  })
}

const loadAiDecisionAnalysis = async () => {
  aiDecisionLoading.value = true
  try {
    const { start, end } = computeSelectedRange()
    const conditions = buildConditions()
    const response = await getAiDecisionAnalysis(start, end, conditions)
    aiDecisionData.value = response?.data || []
  } catch (error) {
    console.error('Failed to load AI decision analysis:', error)
    aiDecisionData.value = []
  } finally {
    aiDecisionLoading.value = false
    await nextTick()
    updateAiDecisionChart()
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

// Determine match status based on is_ai_decision_correct field
// Returns: 'TT' (True Positive), 'FP' (False Positive), 'FN' (False Negative), or '' (empty)
const getMatchStatus = (item) => {
  const aiDecisionCorrect = item.is_ai_decision_correct
  
  // If field is missing or null/undefined, return empty
  if (!aiDecisionCorrect) {
    return ''
  }
  
  const value = String(aiDecisionCorrect).trim()
  
  // Return the value directly if it's TT, FP, or FN
  if (value === 'TT' || value === 'FP' || value === 'FN') {
    return value
  }
  
  // Default to empty for any other value
  return ''
}

// Get match status display info (icon, color class, title)
const getMatchStatusDisplay = (status) => {
  const config = getMatchStatusConfig(status)
  const statusUpper = status ? String(status).toUpperCase() : ''
  
  const displayMap = {
    'TT': {
      icon: 'check_circle',
      colorClass: 'text-green-500 dark:text-green-400',
      title: t(config.i18nKey)
    },
    'FP': {
      icon: 'cancel',
      colorClass: 'text-red-500 dark:text-red-400',
      title: t(config.i18nKey)
    },
    'FN': {
      icon: 'warning',
      colorClass: 'text-orange-500 dark:text-orange-400',
      title: t(config.i18nKey)
    },
    '': {
      icon: 'remove',
      colorClass: 'text-gray-400 dark:text-gray-500',
      title: t(MATCH_STATUS_CONFIG.Empty.i18nKey)
    }
  }
  
  return displayMap[statusUpper] || displayMap['']
}

const handleSearchContainerClick = () => {
  if (currentField.value) {
    nextTick(() => {
      searchInputRef.value?.focus()
    })
    return
  }
  showFieldMenu.value = true
  nextTick(() => {
    searchInputRef.value?.focus()
  })
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
  // Also reload charts with updated conditions
  loadAiAccuracyStatistics()
  loadAiDecisionAnalysis()
}

const addKeyword = () => {
  const keyword = currentSearchInput.value.trim()
  if (keyword) {
    // If no field selected, default to 'title'
    const field = currentField.value || 'title'
    
    // Check if this exact field:value combination already exists
    const exists = searchKeywords.value.some(
      k => k.field === field && k.value === keyword
    )
    
    if (!exists) {
      searchKeywords.value.push({ field, value: keyword })
      currentSearchInput.value = ''
      currentField.value = ''
      showFieldMenu.value = false
      currentPage.value = 1
      loadAlerts()
      // Also reload charts with updated conditions
      loadAiAccuracyStatistics()
      loadAiDecisionAnalysis()
    }
  }
}

const removeKeyword = (index) => {
  searchKeywords.value.splice(index, 1)
  currentPage.value = 1
  loadAlerts()
  // Also reload charts with updated conditions
  loadAiAccuracyStatistics()
  loadAiDecisionAnalysis()
}

const handleKeywordDeleteKey = (event) => {
  if (event.key === 'Backspace') {
    if (!currentSearchInput.value && searchKeywords.value.length > 0) {
      event.preventDefault()
      removeKeyword(searchKeywords.value.length - 1)
    } else if (!currentSearchInput.value && currentField.value) {
      event.preventDefault()
      currentField.value = ''
    } else if (currentField.value && currentSearchInput.value) {
      const fieldObj = searchFields.value.find(f => f.value === currentField.value)
      const prefix = fieldObj ? `${fieldObj.label}: ` : `${currentField.value}: `
      const cursorPos = event.target.selectionStart || 0
      if (cursorPos <= prefix.length) {
        event.preventDefault()
        currentField.value = ''
        currentSearchInput.value = ''
      }
    }
  }
}

const selectField = (field) => {
  currentField.value = field
  currentSearchInput.value = ''
  showFieldMenu.value = false
  // Focus the input after selecting field
  nextTick(() => {
    if (searchInputRef.value) {
      searchInputRef.value.focus()
      // Set cursor position after the prefix
      const fieldObj = searchFields.value.find(f => f.value === field)
      const prefix = fieldObj ? `${fieldObj.label}: ` : `${field}: `
      const input = searchInputRef.value
      if (input.setSelectionRange) {
        input.setSelectionRange(prefix.length, prefix.length)
      }
    }
  })
}

const handleSearchBlur = () => {
  setTimeout(() => {
    if (!currentField.value && !currentSearchInput.value) {
      showFieldMenu.value = false
    }
  }, 200)
}

const handleClickOutside = (event) => {
  const target = event.target
  // Handle more menu dropdown
  const dropdown = event.target.closest('.more-menu-dropdown')
  const button = event.target.closest('.more-menu-button')
  if (!dropdown && !button) {
    showMoreMenu.value = false
  }
  // Handle search field menu
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
    addWorkflowRun(data)
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

// Recursively extract all string values from an object
const extractAllTextValues = (obj, depth = 0) => {
  if (obj === null || obj === undefined) return []

  const textValues = []

  if (typeof obj === 'string') {
    // If it's a string, add it directly
    textValues.push(obj)
  } else if (Array.isArray(obj)) {
    // If it's an array, process each element
    obj.forEach((item) => {
      const extracted = extractAllTextValues(item, depth + 1)
      textValues.push(...extracted)
    })
  } else if (typeof obj === 'object') {
    // If it's an object, process each property
    Object.entries(obj).forEach(([, value]) => {
      const extracted = extractAllTextValues(value, depth + 1)
      textValues.push(...extracted)
    })
  }

  return textValues
}

const getWorkflowTextFromData = (data) => {
  if (!data || data.error) return null

  const resultObject = data?.data?.outputs?.result
  if (!resultObject) return null

  const textValues = extractAllTextValues(resultObject)
  const filtered = textValues.filter(text => text && text.trim().length > 0)
  return filtered.length > 0 ? filtered.join('\n\n') : null
}

const workflowResultText = computed(() => getWorkflowTextFromData(workflowResult.value))

// Parse structured blocks like:
// [Is Threat]: ...
// [Confidence Score]: ...
// [Reason]: ...
// in any order. If parsing fails, we fall back to workflowResultText.
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

const parsedWorkflowResult = computed(() => {
  const text = workflowResultText.value
  if (!text) {
    return {
      isThreat: null,
      confidence: null,
      reason: null,
      hasAny: false,
      raw: ''
    }
  }
  return parseWorkflowBlocks(text)
})

const formatRunTimestamp = (ts) => {
  const date = ts instanceof Date ? ts : new Date(ts)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleString()
}

const toggleRunExpanded = (id) => {
  const run = workflowRuns.value.find(r => r.id === id)
  if (run) {
    run.expanded = !run.expanded
  }
}

const addWorkflowRun = (data) => {
  const text = getWorkflowTextFromData(data)
  const parsed = parseWorkflowBlocks(text || '')
  const modelName = selectedWorkflow.value
    ? (workflows.value.find(w => w.id === selectedWorkflow.value)?.name || 'Model')
    : 'Model'

  const newRun = {
    id: `run-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
    modelName,
    timestamp: new Date().toISOString(),
    parsed,
    text,
    raw: data?.data?.outputs?.result,
    expanded: false
  }

  // Keep only the last 3 runs
  const runs = [...workflowRuns.value, newRun]
  workflowRuns.value = runs.slice(-3)
}

const isDarkMode = () => document.documentElement.classList.contains('dark')

const handleFilter = () => {
  currentPage.value = 1
  loadAlerts()
  // Also reload charts with updated conditions
  loadAiAccuracyStatistics()
  loadAiDecisionAnalysis()
}

// AI Judgment filter state
const aiJudgmentFilterText = computed(() =>
  isAiJudgmentFilterActive.value
    ? (t('common.clearFilter') || 'Clear Filter')
    : (t('aiPlayground.filter.aiJudgmentLabel') || 'AI Judgment')
)

const toggleAiJudgmentFilter = () => {
  isAiJudgmentFilterActive.value = !isAiJudgmentFilterActive.value
  currentPage.value = 1
  loadAlerts()
  // Also reload charts with updated conditions
  loadAiAccuracyStatistics()
  loadAiDecisionAnalysis()
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
  showMoreMenu.value = false
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
  const conditions = []
  
  // Add search keywords
  searchKeywords.value
    .filter(k => k.field && k.value)
    .forEach(k => {
      conditions.push({ [k.field]: k.value })
    })
  
  // Add AI judgment filter (exclude Unknown when filter is active)
  if (isAiJudgmentFilterActive.value) {
    // Exclude Unknown verification_state
    conditions.push({ 'verification_state!=': 'Unknown' })
  }
  
  // Add AI judge filter (verification_state)
  if (aiJudgeFilter.value && aiJudgeFilter.value !== 'all') {
    conditions.push({ verification_state: aiJudgeFilter.value })
  }
  
  // Add human judge filter (close_reason)
  if (humanJudgeFilter.value && humanJudgeFilter.value !== 'all') {
    conditions.push({ close_reason: humanJudgeFilter.value })
  }
  
  // Add match filter (is_ai_decision_correct)
  if (matchFilter.value && matchFilter.value !== 'all') {
    if (matchFilter.value === 'empty') {
      // For empty filter, we need to handle null/empty values
      // This will be handled in backend by checking for null or empty string
      conditions.push({ is_ai_decision_correct: '' })
    } else {
      conditions.push({ is_ai_decision_correct: matchFilter.value })
    }
  }
  
  return conditions
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

    // Client-side filters are now handled server-side via conditions
    // Only keep data normalization here
    alerts.value = normalized
    total.value = response.total || 0
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
    loadAiDecisionAnalysis(),
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
    workflowRuns.value = []
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
  aiAccuracyChartManager.ensure()
  aiDecisionChartManager.ensure()
  document.addEventListener('click', handleClickOutside)
  wordWrapState.value = getWordWrapState()
  
  // Check if alertId is provided in query params
  const alertId = route.query.alertId
  if (alertId) {
    // Add alertId to search keywords and perform search
    const alertIdStr = String(alertId).trim()
    if (alertIdStr) {
      // Check if already exists
      const exists = searchKeywords.value.some(k => k.field === 'id' && k.value === alertIdStr)
      if (!exists) {
        searchKeywords.value.push({ field: 'id', value: alertIdStr })
        currentPage.value = 1
        // Load alerts will be called by handleRefresh
      }
    }
  }
  
  handleRefresh()
})

onBeforeUnmount(() => {
  aiAccuracyChartManager.dispose()
  aiDecisionChartManager.dispose()
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

