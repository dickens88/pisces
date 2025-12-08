<template>
  <div class="w-full">
    <!-- Page header -->
    <header class="flex flex-wrap justify-between items-center gap-4 mb-6">
      <h1 class="text-gray-900 dark:text-white text-4xl font-black leading-tight tracking-[-0.033em]">
        {{ $t('alerts.title') }}
      </h1>
      <div class="flex gap-2 items-center">
        <button
          @click="handleRefresh"
          :disabled="isRefreshing"
          class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-200 dark:disabled:hover:bg-[#2a3546] h-10"
          :title="$t('common.refresh') || 'Refresh'"
        >
          <span
            class="material-symbols-outlined text-base"
            :class="{ 'animate-spin': isRefreshing }"
          >
            refresh
          </span>
        </button>
        <TimeRangePicker
          v-model="selectedTimeRange"
          :custom-range="customTimeRange"
          storage-key="alerts"
          @change="handleTimeRangeChange"
          @custom-range-change="handleCustomRangeChange"
        />
      </div>
    </header>

    <!-- Statistics cards -->
    <section
      v-if="showCharts"
      class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8"
    >
      <div class="flex flex-col gap-2 rounded-xl border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#111822] p-6">
        <p class="text-gray-900 dark:text-white text-base font-medium leading-normal">
          {{ $t('alerts.list.statistics.alertStatusBySeverity') }}
        </p>
        <p class="text-gray-900 dark:text-white tracking-light text-[32px] font-bold leading-tight truncate">
          {{ alertStatusTotal.toLocaleString() }}
        </p>
        <p class="text-gray-600 dark:text-gray-400 text-sm font-normal leading-normal">
          {{ alertsTimeRangeLabel }}
        </p>
        <div class="relative h-40 w-full">
          <div
            v-if="alertStatusChartLoading"
            class="absolute inset-0 flex items-center justify-center text-gray-500 dark:text-gray-400 text-sm"
          >
            {{ $t('common.loading') }}
          </div>
          <div
            v-else-if="alertStatusChartSeries.length === 0"
            class="absolute inset-0 flex items-center justify-center text-gray-500 dark:text-gray-400 text-sm"
          >
            {{ $t('common.noData') }}
          </div>
          <div
            v-show="!alertStatusChartLoading && alertStatusChartSeries.length > 0"
            ref="alertStatusChartRef"
            class="absolute inset-0"
            style="margin: 0; padding: 0;"
          ></div>
        </div>
      </div>

      <div class="flex flex-col gap-2 rounded-xl border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#111822] p-6">
        <p class="text-gray-900 dark:text-white text-base font-medium leading-normal">
          {{ $t('alerts.list.statistics.alertTypeStats') }}
        </p>
        <p class="text-gray-900 dark:text-white tracking-light text-[32px] font-bold leading-tight truncate">
          {{ alertTypeChartTotal.toLocaleString() }}
        </p>
        <p class="text-gray-600 dark:text-gray-400 text-sm font-normal leading-normal">
          {{ alertsTimeRangeLabel }}
        </p>
        <div class="relative h-40 w-full">
          <div
            v-if="alertTypeChartLoading"
            class="absolute inset-0 flex items-center justify-center text-gray-500 dark:text-gray-400 text-sm"
          >
            {{ $t('common.loading') }}
          </div>
          <div
            v-else-if="alertTypeChartValues.length === 0"
            class="absolute inset-0 flex items-center justify-center text-gray-500 dark:text-gray-400 text-sm"
          >
            {{ $t('common.noData') }}
          </div>
          <div
            v-show="!alertTypeChartLoading && alertTypeChartValues.length > 0"
            ref="alertTypeChartRef"
            class="absolute inset-0"
            style="margin: 0; padding: 0;"
          ></div>
        </div>
      </div>

      <div class="flex flex-col gap-2 rounded-xl border border-gray-200 dark:border-[#324867] bg-white dark:bg-[#111822] p-6">
        <p class="text-gray-900 dark:text-white text-base font-medium leading-normal">
          {{ $t('alerts.list.statistics.automationClosureRate') }}
        </p>
        <p class="text-gray-900 dark:text-white tracking-light text-[32px] font-bold leading-tight truncate">
          {{ statistics.automationRate || '0' }}%
        </p>
        <p class="text-gray-600 dark:text-gray-400 text-sm font-normal leading-normal">
          {{ alertsTimeRangeLabel }}
        </p>
        <div class="relative h-40 w-full">
          <div
            v-if="automationRateLoading"
            class="absolute inset-0 flex items-center justify-center text-gray-500 dark:text-gray-400 text-sm"
          >
            {{ $t('common.loading') }}
          </div>
          <div
            v-else-if="!statistics.totalClosed && !statistics.autoClosed"
            class="absolute inset-0 flex items-center justify-center text-gray-500 dark:text-gray-400 text-sm"
          >
            {{ $t('common.noData') }}
          </div>
          <div
            v-show="!automationRateLoading && (statistics.totalClosed || statistics.autoClosed)"
            class="absolute inset-0 flex flex-col justify-between py-3"
          >
            <!-- Progress bar -->
            <div class="relative h-6 w-full bg-gray-200 dark:bg-[#233348] rounded-full mt-4">
              <div
                class="bg-primary h-6 rounded-full transition-all"
                :style="{ width: (statistics.automationRate || 0) + '%' }"
              ></div>
              <div class="absolute inset-0 flex items-center justify-center">
                <span class="text-gray-900 dark:text-white text-sm font-medium">{{ statistics.automationRate || '0' }}%</span>
              </div>
            </div>
            <!-- Two metrics -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-gray-600 dark:text-gray-400 text-xs font-medium mb-1">{{ $t('alerts.list.statistics.autoClosed') }}</p>
                <p class="text-gray-900 dark:text-white text-2xl font-bold">{{ (statistics.autoClosed || 0).toLocaleString() }}</p>
              </div>
              <div class="text-right">
                <p class="text-gray-600 dark:text-gray-400 text-xs font-medium mb-1">{{ $t('alerts.list.statistics.totalAlerts') }}</p>
                <p class="text-gray-900 dark:text-white text-2xl font-bold">{{ (statistics.totalClosed || 0).toLocaleString() }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Alert list table -->
    <section class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-xl relative">
      <!-- Loading overlay -->
      <div
        v-if="loadingAlerts"
        class="absolute inset-0 bg-white/80 dark:bg-[#111822]/80 backdrop-blur-sm z-50 flex items-center justify-center rounded-xl"
      >
        <div class="flex flex-col items-center gap-4">
          <div class="relative w-16 h-16">
            <div class="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
            <div class="absolute inset-0 border-4 border-transparent border-t-primary rounded-full animate-spin"></div>
          </div>
          <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">{{ $t('common.loading') || '加载中...' }}</p>
        </div>
      </div>
      <div class="flex flex-wrap items-center gap-3 p-4 border-b border-[#324867]">
        <div class="relative w-[20%] min-w-[200px] max-w-sm">
          <div class="flex items-start gap-2 min-h-[42px] rounded-lg border-0 bg-gray-100 dark:bg-[#233348] pl-3 pr-3 py-2 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary">
            <div class="pointer-events-none flex items-center shrink-0 pt-[2px]">
              <span class="material-symbols-outlined text-gray-500 dark:text-gray-400" style="font-size: 20px;">search</span>
            </div>
            <div class="flex flex-1 flex-wrap items-center gap-2 max-h-32 overflow-y-auto pr-1">
              <!-- Search keyword tags -->
              <div
                v-for="(keyword, index) in searchKeywords"
                :key="index"
                class="flex items-center gap-1 px-2 py-1 bg-primary/20 text-primary rounded text-sm max-w-full min-w-0"
              >
                <span class="min-w-0 break-all">{{ keyword }}</span>
                <button
                  @click="removeKeyword(index)"
                  class="flex items-center justify-center hover:text-primary/70 transition-colors ml-0.5"
                  type="button"
                  :aria-label="$t('common.delete')"
                >
                  <span class="material-symbols-outlined" style="font-size: 16px;">close</span>
                </button>
              </div>
              <!-- Input field -->
              <input
                v-model="currentSearchInput"
                @keydown.enter.prevent="addKeyword"
                @keydown.backspace="handleKeywordDeleteKey"
                @input="handleSearchInput"
                class="flex-1 min-w-[120px] border-0 bg-transparent text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none sm:text-sm"
                :placeholder="searchKeywords.length === 0 ? $t('alerts.list.searchPlaceholder') : ''"
                type="text"
              />
            </div>
          </div>
        </div>
        <div class="relative min-w-[140px] max-w-[12rem]">
          <div class="flex items-center gap-2 min-h-[42px] rounded-lg border-0 bg-gray-100 dark:bg-[#233348] pl-3 pr-3 py-2 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary">
              <div class="pointer-events-none flex items-center shrink-0">
              <span class="material-symbols-outlined text-gray-500 dark:text-gray-400" style="font-size: 20px;">person</span>
            </div>
            <input
              v-model="ownerSearch"
              @keydown.enter.prevent="handleOwnerSearch"
              @input="handleOwnerSearchInput"
              class="flex-1 min-w-[80px] border-0 bg-transparent text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none sm:text-sm"
              :placeholder="$t('alerts.list.ownerSearchPlaceholder')"
              type="text"
            />
          </div>
        </div>
        <div class="relative min-w-[140px] max-w-[12rem]">
          <div class="flex items-center gap-2 min-h-[42px] rounded-lg border-0 bg-gray-100 dark:bg-[#233348] pl-3 pr-3 py-2 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary">
              <div class="pointer-events-none flex items-center shrink-0">
              <span class="material-symbols-outlined text-gray-500 dark:text-gray-400" style="font-size: 20px;">person_search</span>
            </div>
            <input
              v-model="actorSearch"
              @keydown.enter.prevent="handleActorSearch"
              @input="handleActorSearchInput"
              class="flex-1 min-w-[80px] border-0 bg-transparent text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none sm:text-sm"
              :placeholder="$t('alerts.list.actorSearchPlaceholder')"
              type="text"
            />
          </div>
        </div>
        <div class="relative min-w-[140px] max-w-[12rem]">
          <select
            v-model="statusFilter"
            @change="handleFilter"
            class="pl-4 pr-9 appearance-none block w-full rounded-lg border-0 bg-gray-100 dark:bg-[#233348] h-10 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm text-sm"
          >
            <option value="all">{{ $t('alerts.list.allStatus') }}</option>
            <option value="open">{{ $t('alerts.list.open') }}</option>
            <option value="block">{{ $t('alerts.list.block') }}</option>
            <option value="closed">{{ $t('alerts.list.closed') }}</option>
          </select>
          <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500 dark:text-gray-400">
            <span class="material-symbols-outlined" style="font-size: 20px;">arrow_drop_down</span>
          </div>
        </div>
        <!-- Alert Filter Mode Switch -->
        <div class="flex-shrink-0">
          <ThreeWaySwitch
            v-model="alertFilterMode"
            :options="alertFilterOptions"
            i18n-prefix="alerts.list.filterMode"
            :label="$t('alerts.list.riskFilter') || '风险过滤'"
          />
        </div>
        <!-- Spacer to push right buttons to the right -->
        <div class="flex-1 min-w-0"></div>
        <div class="flex items-center gap-3 flex-shrink-0">
          <button
            :disabled="selectedAlerts.length === 0"
            @click="openBatchCloseDialog"
            class="flex items-center justify-center gap-2 rounded-lg h-10 bg-gray-100 dark:bg-[#233348] text-gray-700 dark:text-white text-sm font-bold px-4 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 dark:hover:bg-[#324867] transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
            <span>{{ $t('alerts.list.batchClose') }}</span>
          </button>
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
                  {{ isWordWrap ? 'wrap_text' : 'text_fields' }}
                </span>
                <span>{{ isWordWrap ? $t('common.wordWrap') : $t('common.singleLine') }}</span>
              </button>
              <button
                @click="handleToggleChartsVisibility"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867]"
              >
                <span class="material-symbols-outlined text-base">
                  {{ showCharts ? 'monitoring' : 'visibility_off' }}
                </span>
                <span>{{ showCharts ? $t('alerts.list.hideCharts') : $t('alerts.list.showCharts') }}</span>
              </button>
              <div class="mx-3 my-1 h-px bg-gray-200 dark:bg-[#3b4c65]"></div>
              <button
                @click="handleAssociateIncidentFromMenu"
                :disabled="selectedAlerts.length === 0"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867] disabled:hover:bg-transparent"
              >
                <span class="material-symbols-outlined text-base">link</span>
                <span>{{ $t('alerts.list.associateIncident') }}</span>
              </button>
              <button
                @click="handleCreateIncidentFromMenu"
                :disabled="selectedAlerts.length === 0"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867] disabled:hover:bg-transparent"
              >
                <span class="material-symbols-outlined text-base">transform</span>
                <span>{{ $t('alerts.list.batchConvert') }}</span>
              </button>
              <button
                @click="handleCreateAlertFromMenu"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867]"
              >
                <span class="material-symbols-outlined text-base">add</span>
                <span>{{ $t('alerts.list.createAlert') }}</span>
              </button>
              <button
                @click="handleConvertToVulnerability"
                :disabled="selectedAlerts.length === 0"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867] disabled:hover:bg-transparent"
              >
                <span class="material-symbols-outlined text-base">bug_report</span>
                <span>{{ $t('alerts.detail.convertToVulnerability') }}</span>
              </button>
              <button
                @click="openBatchDeleteDialog"
                :disabled="selectedAlerts.length === 0"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-[#324867] disabled:hover:bg-transparent"
              >
                <span class="material-symbols-outlined text-base">delete</span>
                <span>{{ $t('alerts.list.batchDelete') }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <DataTable
        ref="dataTableRef"
        :columns="columns"
        :items="alerts"
        :selectable="true"
        :resizable="true"
        storage-key="alerts-table-columns"
        :default-widths="defaultWidths"
        :current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        @update:current-page="handlePageChange"
        @update:page-size="pageSize = $event"
        @select="handleSelect"
        @select-all="handleSelectAll"
        @page-size-change="handlePageSizeChange"
      >
        <template #cell-createTime="{ value, item }">
          {{ formatDateTime(value || item?.createTime || item?.create_time) }}
        </template>
        <template #cell-alertTitle="{ item }">
          <div class="flex items-center gap-2">
            <button
              @click.stop="openAlertDetailInNewWindow(item.id)"
              class="flex-shrink-0 text-gray-500 dark:text-gray-400 hover:text-primary transition-colors p-1"
              :title="$t('alerts.list.openInNewWindow') || '在新窗口打开'"
            >
              <span class="material-symbols-outlined text-base">open_in_new</span>
            </button>
            <a
              @click="openAlertDetail(item.id)"
              :class="[
                'hover:underline cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap flex-1 font-medium',
                (item.handle_status?.toLowerCase() === 'closed' || item.status === 'closed') 
                  ? 'text-gray-500 dark:text-gray-400' 
                  : 'text-primary'
              ]"
              :title="item.title"
            >
              {{ item.title }}
            </a>
          </div>
        </template>
        <template #cell-riskLevel="{ item }">
          <div class="flex items-center gap-2">
            <span
              :class="[
                'text-xs font-medium px-2.5 py-0.5 rounded-full inline-flex items-center justify-center min-w-[70px]',
                getRiskLevelClass(item.riskLevel)
              ]"
              :title="$t(`common.severity.${item.riskLevel}`)"
            >
              {{ $t(`common.severity.${item.riskLevel}`) }}
            </span>
            <div class="h-4 w-px bg-gray-300 dark:bg-gray-600 flex-shrink-0"></div>
            <span
              v-if="item.verification_state === 'True_Positive'"
              class="material-symbols-outlined text-red-500 flex-shrink-0"
              style="font-size: 20px;"
              :title="$t('alerts.list.aiJudge') + ': ' + $t('alerts.list.aiJudgeResult.truePositive')"
            >
              Input_circle
            </span>
            <span
              v-else-if="item.verification_state === 'False_Positive'"
              class="material-symbols-outlined text-green-500 flex-shrink-0"
              style="font-size: 20px;"
              :title="$t('alerts.list.aiJudge') + ': ' + $t('alerts.list.aiJudgeResult.falsePositive')"
            >
              output_circle
            </span>
            <span
              v-else
              class="material-symbols-outlined text-gray-400 flex-shrink-0"
              style="font-size: 20px;"
              :title="$t('alerts.list.aiJudge') + ': ' + $t('alerts.list.aiJudgeResult.unknown')"
            >
              Unknown_5
            </span>
          </div>
        </template>
        <template #cell-status="{ item }">
          <span
            :class="[
              'inline-flex items-center gap-1.5 rounded-full px-2 py-1 text-xs font-medium',
              getStatusClass(item.status)
            ]"
            :title="$t(`alerts.list.${item.status}`)"
          >
            <span :class="['size-1.5 rounded-full', getStatusDotClass(item.status)]"></span>
            {{ $t(`alerts.list.${item.status}`) }}
          </span>
        </template>
        <template #cell-actor="{ value, item }">
          <div class="flex justify-center w-full">
            <UserAvatar :name="value || item?.owner" />
          </div>
        </template>
      </DataTable>
    </section>

    <!-- Alert detail drawer -->
    <AlertDetail
      v-if="currentAlertId"
      :alert-id="currentAlertId"
      @close="closeAlertDetail"
      @closed="handleAlertClosed"
      @created="handleAlertConvertedToIncident"
    />

    <!-- Create incident dialog -->
    <CreateIncidentDialog
      :visible="showCreateIncidentDialog"
      :initial-data="createIncidentInitialData"
      :alert-ids="selectedAlerts"
      @close="closeCreateIncidentDialog"
      @created="handleIncidentCreated"
    />

    <!-- Create alert dialog -->
    <CreateAlertDialog
      :visible="showCreateAlertDialog"
      @close="closeCreateAlertDialog"
      @created="handleAlertCreated"
    />

    <!-- Associate incident dialog -->
    <AssociateIncidentDialog
      :visible="showAssociateIncidentDialog"
      :alert-ids="selectedAlerts"
      @close="closeAssociateIncidentDialog"
      @associated="handleAssociateIncidentSuccess"
    />

    <!-- Create vulnerability dialog -->
    <CreateVulnerabilityDialog
      :visible="showCreateVulnerabilityDialog"
      :initial-data="createVulnerabilityInitialData"
      :alert-ids="selectedAlerts"
      @close="closeCreateVulnerabilityDialog"
      @created="handleVulnerabilityCreated"
    />

    <!-- Batch delete dialog -->
    <div
      v-if="showBatchDeleteDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="closeBatchDeleteDialog"
    >
      <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-lg p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ $t('alerts.list.batchDeleteDialog.title') }}
          </h2>
          <button
            @click="closeBatchDeleteDialog"
            class="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
          </button>
        </div>

        <!-- Prompt message -->
        <div class="mb-4 p-3 bg-gray-100 dark:bg-[#1e293b] rounded-md">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ $t('alerts.list.batchDeleteDialog.confirmMessage', { count: selectedAlerts.length }) }}
          </p>
        </div>

        <!-- Confirmation input -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-900 dark:text-white mb-2">
            {{ $t('alerts.list.batchDeleteDialog.confirmInputLabel') }}
          </label>
          <input
            v-model="deleteConfirmInput"
            @keydown.enter.prevent="handleBatchDelete"
            type="text"
            class="w-full bg-gray-100 dark:bg-[#1e293b] text-gray-900 dark:text-white border border-gray-300 dark:border-[#324867] rounded-md px-4 py-2 focus:ring-2 focus:ring-primary focus:border-primary"
            :placeholder="$t('alerts.list.batchDeleteDialog.confirmInputPlaceholder')"
            autocomplete="off"
          />
        </div>

        <!-- Action buttons -->
        <div class="flex items-center justify-end gap-3">
          <button
            @click="closeBatchDeleteDialog"
            class="px-4 py-2 text-sm text-gray-700 dark:text-gray-400 bg-gray-100 dark:bg-[#1e293b] rounded-md hover:bg-gray-200 dark:hover:bg-primary/30 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="handleBatchDelete"
            :disabled="!isDeleteConfirmValid || isBatchDeleting"
            class="px-4 py-2 text-sm text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span v-if="isBatchDeleting" class="material-symbols-outlined animate-spin text-base">sync</span>
            {{ $t('common.delete') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Batch close dialog -->
    <div
      v-if="showBatchCloseDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
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

        <!-- Prompt message -->
        <div class="mb-4 p-3 bg-gray-100 dark:bg-[#1e293b] rounded-md">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ $t('alerts.list.batchCloseDialog.confirmMessage', { count: selectedAlerts.length }) }}
          </p>
        </div>

        <!-- Conclusion category dropdown -->
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

        <!-- Investigation conclusion input -->
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
              @focus="handleCloseNotesFocus"
              @click="handleCloseNotesClick"
              @blur="handleCloseNotesBlur"
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

        <!-- Action buttons -->
        <div class="flex items-center justify-end gap-3">
          <button
            @click="closeBatchCloseDialog"
            class="px-4 py-2 text-sm text-gray-700 dark:text-gray-400 bg-gray-100 dark:bg-[#1e293b] rounded-md hover:bg-gray-200 dark:hover:bg-primary/30 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="handleBatchClose"
            :disabled="!closeConclusion.category || !closeConclusion.notes.trim() || isBatchClosing"
            class="px-4 py-2 text-sm text-white bg-primary rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span v-if="isBatchClosing" class="material-symbols-outlined animate-spin text-base">sync</span>
            {{ $t('common.submit') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { getAlerts, getAlertStatistics, batchCloseAlerts, batchCloseAlertsByPut, getAlertCountsBySource, getAlertStatusBySeverity, closeAlert, deleteAlerts } from '@/api/alerts'
import AlertDetail from '@/components/alerts/AlertDetail.vue'
import CreateIncidentDialog from '@/components/incidents/CreateIncidentDialog.vue'
import CreateAlertDialog from '@/components/alerts/CreateAlertDialog.vue'
import AssociateIncidentDialog from '@/components/alerts/AssociateIncidentDialog.vue'
import CreateVulnerabilityDialog from '@/components/vulnerabilities/CreateVulnerabilityDialog.vue'
import DataTable from '@/components/common/DataTable.vue'
import TimeRangePicker from '@/components/common/TimeRangePicker.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import ThreeWaySwitch from '@/components/common/ThreeWaySwitch.vue'
import { formatDateTime, parseToDate, calculateTTR } from '@/utils/dateTime'
import { useToast } from '@/composables/useToast'
import { useTimeRangeStorage } from '@/composables/useTimeRangeStorage'
import { useRecentCloseCommentSuggestions } from '@/composables/useRecentCloseCommentSuggestions'

const { t } = useI18n()
const toast = useToast()

const columns = computed(() => [
  { key: 'createTime', label: t('alerts.list.createTime') },
  { key: 'alertTitle', label: t('alerts.list.alertTitle') },
  { key: 'riskLevel', label: t('alerts.list.riskLevel') },
  { key: 'status', label: t('alerts.list.status') },
  { key: 'responseTime', label: t('alerts.list.responseTime') },
  { key: 'actor', label: t('alerts.list.actor') }
])

const defaultWidths = {
  createTime: 200,
  alertTitle: 400,
  riskLevel: 120,
  status: 120,
  responseTime: 120,
  actor: 50
}

const chartsVisibilityStorageKey = 'alerts-showCharts-visible'
const getStoredChartsVisibility = () => {
  try {
    const stored = localStorage.getItem(chartsVisibilityStorageKey)
    if (stored === 'true' || stored === 'false') {
      return stored === 'true'
    }
  } catch (error) {
    console.warn('Failed to read charts visibility preference:', error)
  }
  return true
}
const showCharts = ref(getStoredChartsVisibility())

const alerts = ref([])
const loadingAlerts = ref(false)
const isRefreshing = ref(false)
const dataTableRef = ref(null)
const statistics = ref({
  totalAlerts: 0,
  trend: 0,
  alertCount: 0,
  alertTrend: 0,
  automationRate: 0,
  automationRateChange: 0,
  automationRateTrend: 'down',
  totalClosed: 0,
  autoClosed: 0,
  typeStats: []
})

const getStoredSearchKeywords = () => {
  try {
    const stored = localStorage.getItem('alerts-searchKeywords')
    if (stored) {
      const parsed = JSON.parse(stored)
      if (Array.isArray(parsed) && parsed.every(k => typeof k === 'string')) {
        return parsed
      }
    }
  } catch (error) {
    console.warn('Failed to read search keywords from localStorage:', error)
  }
  return []
}

const searchKeywords = ref(getStoredSearchKeywords())
const currentSearchInput = ref('')
const ownerSearch = ref('')
const actorSearch = ref('')

const getStoredStatusFilter = () => {
  try {
    const stored = localStorage.getItem('alerts-status-filter')
    if (stored && ['all', 'open', 'block', 'closed'].includes(stored)) {
      return stored
    }
  } catch (error) {
    console.warn('Failed to read status filter from localStorage:', error)
  }
  return 'all'
}
const statusFilter = ref(getStoredStatusFilter())

const getStoredAlertFilterMode = () => {
  try {
    const stored = localStorage.getItem('alerts-filter-mode')
    if (stored && ['allAlerts', 'normal', 'highRisk', 'unclosedHighRisk'].includes(stored)) {
      return stored === 'normal' ? 'allAlerts' : stored
    }
  } catch (error) {
    console.warn('Failed to read alert filter mode from localStorage:', error)
  }
  return 'allAlerts'
}
const alertFilterMode = ref(getStoredAlertFilterMode())

const alertFilterOptions = computed(() => [
  {
    value: 'allAlerts',
    icon: 'list_alt_check',
    i18nKey: 'allAlerts'
  },
  {
    value: 'highRisk',
    icon: 'data_alert',
    i18nKey: 'highRisk'
  },
  {
    value: 'unclosedHighRisk',
    icon: 'release_alert',
    i18nKey: 'unclosedHighRisk'
  }
])

const selectedAlerts = ref([])
const currentPage = ref(1)

const getStoredPageSize = () => {
  try {
    const stored = localStorage.getItem('alerts-pageSize')
    if (stored) {
      const size = Number(stored)
      if (size && [10, 20, 50, 100].includes(size)) {
        return size
      }
    }
  } catch (error) {
    console.warn('Failed to read page size from localStorage:', error)
  }
  return 10
}

const pageSize = ref(getStoredPageSize())
const total = ref(0)

const { selectedTimeRange, customTimeRange } = useTimeRangeStorage('alerts', 'last24Hours')
const showBatchCloseDialog = ref(false)
const isBatchClosing = ref(false)
const closeConclusion = ref({
  category: 'falsePositive',
  notes: ''
})
const {
  recentComments: recentCloseComments,
  showDropdown: showRecentCloseComments,
  refresh: refreshRecentCloseComments,
  persist: persistRecentCloseComment,
  handleFocus: handleCloseNotesFocus,
  handleClick: handleCloseNotesClick,
  handleBlur: handleCloseNotesBlur,
  handleSelect: applyRecentCloseComment,
  hideDropdown: hideRecentCloseCommentsDropdown
} = useRecentCloseCommentSuggestions({
  onApply: (comment) => {
    closeConclusion.value.notes = comment
  }
})
const handleRecentCommentSelect = (comment) => {
  applyRecentCloseComment(comment)
}
const showAssociateIncidentDialog = ref(false)
const showCreateIncidentDialog = ref(false)
const createIncidentInitialData = ref(null)
const showCreateAlertDialog = ref(false)
const showMoreMenu = ref(false)
const showCreateVulnerabilityDialog = ref(false)
const createVulnerabilityInitialData = ref(null)
const showBatchDeleteDialog = ref(false)
const deleteConfirmInput = ref('')
const isBatchDeleting = ref(false)

const persistChartsVisibilityPreference = (value) => {
  try {
    localStorage.setItem(chartsVisibilityStorageKey, value ? 'true' : 'false')
  } catch (error) {
    console.warn('Failed to save charts visibility preference:', error)
  }
}

const alertTypeChartRef = ref(null)
const alertTypeChartCategories = ref([])
const alertTypeChartValues = ref([])
const alertTypeChartSeries = ref([])
const alertTypeChartLoading = ref(false)
const alertTypeChartTotal = ref(0)

let alertTypeChartInstance = null
let alertTypeChartResizeBound = false

const automationRateLoading = ref(false)

const alertStatusChartRef = ref(null)
const alertStatusChartLoading = ref(false)
const alertStatusTotal = ref(0)
const alertStatusChartSeries = ref([])
const alertStatusYAxisCategories = ref([])

let alertStatusChartInstance = null
let alertStatusChartResizeBound = false

const formatDateForBackend = (date) => {
  const isoString = date.toISOString()
  return isoString.includes('.') ? isoString.split('.')[0] : isoString.replace('Z', '')
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
      start.setHours(start.getHours() - 24)
      break
  }

  return { start, end }
}

const handleAlertTypeResize = () => {
  if (alertTypeChartInstance) {
    alertTypeChartInstance.resize()
  }
}

const ensureAlertTypeChart = () => {
  if (!showCharts.value) {
    return
  }
  if (!alertTypeChartInstance && alertTypeChartRef.value) {
    alertTypeChartInstance = echarts.init(alertTypeChartRef.value)
    if (!alertTypeChartResizeBound) {
      window.addEventListener('resize', handleAlertTypeResize)
      alertTypeChartResizeBound = true
    }
  }
}

const disposeAlertTypeChart = () => {
  if (alertTypeChartInstance) {
    alertTypeChartInstance.dispose()
    alertTypeChartInstance = null
  }
  if (alertTypeChartResizeBound) {
    window.removeEventListener('resize', handleAlertTypeResize)
    alertTypeChartResizeBound = false
  }
}

const handleAlertStatusResize = () => {
  if (alertStatusChartInstance) {
    alertStatusChartInstance.resize()
  }
}

const ensureAlertStatusChart = () => {
  if (!showCharts.value) {
    return
  }
  if (!alertStatusChartInstance && alertStatusChartRef.value) {
    alertStatusChartInstance = echarts.init(alertStatusChartRef.value)
    if (!alertStatusChartResizeBound) {
      window.addEventListener('resize', handleAlertStatusResize)
      alertStatusChartResizeBound = true
    }
  }
}

const disposeAlertStatusChart = () => {
  if (alertStatusChartInstance) {
    alertStatusChartInstance.dispose()
    alertStatusChartInstance = null
  }
  if (alertStatusChartResizeBound) {
    window.removeEventListener('resize', handleAlertStatusResize)
    alertStatusChartResizeBound = false
  }
}

const updateAlertTypeChart = () => {
  if (!showCharts.value) {
    return
  }
  ensureAlertTypeChart()
  if (!alertTypeChartInstance) {
    return
  }

  alertTypeChartInstance.clear()

  // Detect dark mode
  const isDarkMode = document.documentElement.classList.contains('dark')
  
  // Set colors based on theme
  const axisLabelColor = isDarkMode ? '#cbd5f5' : '#374151'
  const yAxisLabelColor = isDarkMode ? '#94a3b8' : '#6b7280'
  const legendColor = isDarkMode ? '#cbd5f5' : '#374151'
  const axisLineColor = isDarkMode ? '#334155' : '#e5e7eb'
  const splitLineColor = isDarkMode ? '#1f2a37' : '#e5e7eb'
  const tooltipBg = isDarkMode ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)'
  const tooltipTextColor = isDarkMode ? '#e2e8f0' : '#374151'

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: tooltipBg,
      borderWidth: 0,
      textStyle: { color: tooltipTextColor },
      padding: [10, 12]
    },
    legend: {
      top: 0,
      textStyle: { color: legendColor, fontSize: 10 }
    },
    grid: {
      top: 20,
      right: 5,
      bottom: 25,
      left: 20,
      containLabel: false
    },
    xAxis: {
      type: 'category',
      data: alertTypeChartCategories.value,
      boundaryGap: true,
      axisLabel: {
        color: axisLabelColor,
        rotate: alertTypeChartCategories.value.length > 5 ? 20 : 0,
        margin: 8,
        fontSize: 10
      },
      axisLine: {
        show: true,
        lineStyle: { color: axisLineColor }
      },
      axisTick: { show: true, inside: true, alignWithLabel: true }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: yAxisLabelColor, margin: 0, fontSize: 10 },
      splitLine: {
        lineStyle: { color: splitLineColor }
      },
      axisLine: { show: true, lineStyle: { color: axisLineColor } },
      axisTick: { show: true, inside: true }
    },
    series: alertTypeChartSeries.value.length > 0 
      ? alertTypeChartSeries.value 
      : [
          {
            name: t('alerts.title'),
            type: 'bar',
            data: alertTypeChartValues.value,
            barWidth: '45%',
            itemStyle: {
              borderRadius: [8, 8, 0, 0],
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#60a5fa' },
                { offset: 0.7, color: '#3b82f6' },
                { offset: 1, color: '#2563eb' }
              ])
            }
          }
        ]
  }

  alertTypeChartInstance.setOption(option, true)
  nextTick(() => {
    alertTypeChartInstance.resize()
  })
}

const updateAlertStatusChart = () => {
  if (!showCharts.value) {
    return
  }
  ensureAlertStatusChart()
  if (!alertStatusChartInstance) {
    return
  }

  alertStatusChartInstance.clear()

  // Detect dark mode
  const isDarkMode = document.documentElement.classList.contains('dark')
  
  // Set colors based on theme
  const axisLabelColor = isDarkMode ? '#cbd5f5' : '#374151'
  const xAxisLabelColor = isDarkMode ? '#94a3b8' : '#6b7280'
  const legendColor = isDarkMode ? '#cbd5f5' : '#374151'
  const axisLineColor = isDarkMode ? '#334155' : '#e5e7eb'
  const splitLineColor = isDarkMode ? '#1f2a37' : '#e5e7eb'
  const tooltipBg = isDarkMode ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)'
  const tooltipTextColor = isDarkMode ? '#e2e8f0' : '#374151'

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: tooltipBg,
      borderWidth: 0,
      textStyle: { color: tooltipTextColor },
      padding: [10, 12]
    },
    legend: {
      top: 0,
      textStyle: { color: legendColor, fontSize: 10 }
    },
    grid: {
      top: 20,
      right: 10,
      bottom: 5,
      left: 0,
      containLabel: true
    },
    xAxis: {
      type: 'value',
      axisLabel: { color: xAxisLabelColor, fontSize: 10 },
      splitLine: {
        lineStyle: { color: splitLineColor }
      },
      axisLine: { show: true, lineStyle: { color: axisLineColor } },
      axisTick: { show: true, inside: true }
    },
    yAxis: {
      type: 'category',
      data: alertStatusYAxisCategories.value,
      axisLabel: {
        color: axisLabelColor,
        fontSize: 10,
        formatter: (value) => {
          // value 已经是翻译后的文案，直接返回
          return value
        }
      },
      axisLine: { show: true, lineStyle: { color: axisLineColor } },
      axisTick: { show: true, inside: true }
    },
    series: alertStatusChartSeries.value
  }

  alertStatusChartInstance.setOption(option, true)
  nextTick(() => {
    alertStatusChartInstance.resize()
  })
}

const loadAlertTypeDistribution = async () => {
  if (!showCharts.value) {
    return
  }
  alertTypeChartLoading.value = true
  alertTypeChartTotal.value = 0
  try {
    const range = computeSelectedRange()
    const response = await getAlertCountsBySource(
      range.start,
      range.end,
      statusFilter.value
    )
    const counts = response?.data || {}
    
    // Check if data is in new nested format (with is_auto_closed grouping)
    const isNestedFormat = counts && Object.keys(counts).length > 0 && typeof Object.values(counts)[0] === 'object'
    
    if (isNestedFormat) {
      // New format: { "ProductName": { "Manual": 10, "AutoClosed": 5, "None": 3 }, ... }
      const productNames = Object.keys(counts)
      
      // Calculate total for each product to sort
      const productTotals = productNames.map(name => {
        const productData = counts[name] || {}
        const total = (productData.Manual || 0) + (productData.AutoClosed || 0) + (productData.None || 0)
        return { name, total }
      })
      
      // Calculate total from all products (before limiting to TOP10)
      alertTypeChartTotal.value = productTotals.reduce((sum, item) => sum + item.total, 0)
      
      // Sort and take only TOP10 for chart display
      productTotals.sort((a, b) => b.total - a.total)
      const top10Products = productTotals.slice(0, 10)
      
      alertTypeChartCategories.value = top10Products.map(item => item.name)
      
      // Build series data for each closure type (only TOP10)
      const manualData = []
      const autoClosedData = []
      const noneData = []
      
      top10Products.forEach(item => {
        const productData = counts[item.name] || {}
        manualData.push(productData.Manual || 0)
        autoClosedData.push(productData.AutoClosed || 0)
        noneData.push(productData.None || 0)
      })
      
      // Create series for stacked bar chart
      alertTypeChartSeries.value = [
        {
          name: t('dashboard.charts.manual'),
          type: 'bar',
          stack: 'total',
          data: manualData,
          itemStyle: {
            borderRadius: [0, 0, 0, 0],
            color: '#2563eb' // Dark blue for manual
          }
        },
        {
          name: t('dashboard.charts.autoClosed'),
          type: 'bar',
          stack: 'total',
          data: autoClosedData,
          itemStyle: {
            borderRadius: [0, 0, 0, 0],
            color: '#3b82f6' // Medium blue for auto-closed
          }
        },
        {
          name: t('dashboard.charts.none'),
          type: 'bar',
          stack: 'total',
          data: noneData,
          itemStyle: {
            borderRadius: [0, 0, 0, 0],
            color: '#60a5fa' // Light blue for open/None
          }
        }
      ]
      
      alertTypeChartValues.value = top10Products.map(item => item.total)
    } else {
      // Old format: { "ProductName": count, ... } - fallback for compatibility
      const entries = Object.entries(counts).map(([name, value]) => [name, Number(value) || 0])
      
      // Calculate total from all products (before limiting to TOP10)
      alertTypeChartTotal.value = entries.reduce((sum, [, value]) => sum + value, 0)
      
      // Sort and take only TOP10 for chart display
      entries.sort((a, b) => b[1] - a[1])
      const top10Entries = entries.slice(0, 10)
      
      alertTypeChartCategories.value = top10Entries.map(([name]) => name)
      alertTypeChartValues.value = top10Entries.map(([, value]) => value)
      alertTypeChartSeries.value = []
    }
  } catch (error) {
    console.error('Failed to load alert type distribution:', error)
    alertTypeChartCategories.value = []
    alertTypeChartValues.value = []
    alertTypeChartSeries.value = []
    alertTypeChartTotal.value = 0
  } finally {
    alertTypeChartLoading.value = false
    await nextTick()
    updateAlertTypeChart()
  }
}

const loadAlertStatusBySeverity = async () => {
  if (!showCharts.value) {
    return
  }
  alertStatusChartLoading.value = true
  alertStatusTotal.value = 0
  alertStatusChartSeries.value = []
  alertStatusYAxisCategories.value = []

  try {
    const range = computeSelectedRange()
    const response = await getAlertStatusBySeverity(
      range.start,
      range.end,
      statusFilter.value
    )
    const rawData = response?.data || {}

    // 固定状态顺序和枚举
    const statusOrder = ['open', 'closed', 'block']
    const statusApiMap = {
      open: 'Open',
      block: 'Block',
      closed: 'Closed'
    }
    const severities = ['Fatal', 'High', 'Medium', 'Low', 'Tips']
    const severityColors = {
      Fatal: '#1e3a8a',      // 深蓝色
      High: '#2563eb',       // 中深蓝色
      Medium: '#3b82f6',     // 中蓝色
      Low: '#60a5fa',        // 浅蓝色
      Tips: '#93c5fd'        // 很浅的蓝色
    }

    const yAxisLabels = statusOrder.map(statusKey => {
      return t(`alerts.list.${statusKey}`)
    })
    alertStatusYAxisCategories.value = yAxisLabels

    const statusLabelMap = {}
    statusOrder.forEach((key, idx) => {
      statusLabelMap[statusApiMap[key]] = yAxisLabels[idx]
    })

    const yAxisIndexByStatusLabel = {}
    alertStatusYAxisCategories.value.forEach((label, idx) => {
      yAxisIndexByStatusLabel[label] = idx
    })

    const matrix = statusOrder.map(() => severities.map(() => 0))
    let totalCount = 0

    Object.entries(rawData).forEach(([statusApi, severityDict]) => {
      const yLabel = statusLabelMap[statusApi] || statusApi
      const rowIndex = yAxisIndexByStatusLabel[yLabel]
      if (rowIndex === undefined) {
        return
      }

      severities.forEach((sev, sevIdx) => {
        const count = Number(severityDict?.[sev] || 0)
        matrix[rowIndex][sevIdx] = count
        totalCount += count
      })
    })

    alertStatusTotal.value = totalCount

    const series = severities.map((sev, sevIdx) => ({
      name: t(`common.severity.${sev.toLowerCase()}`),
      type: 'bar',
      stack: 'total',
      emphasis: {
        focus: 'series'
      },
      itemStyle: {
        color: severityColors[sev] || '#6366f1'
      },
      barWidth: 25,
      data: matrix.map(row => row[sevIdx])
    }))

    alertStatusChartSeries.value = series
  } catch (error) {
    console.error('Failed to load alert status by severity:', error)
    alertStatusChartSeries.value = []
    alertStatusYAxisCategories.value = []
    alertStatusTotal.value = 0
  } finally {
    alertStatusChartLoading.value = false
    await nextTick()
    updateAlertStatusChart()
  }
}

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const loadAlerts = async () => {
  loadingAlerts.value = true
  try {
    const params = {
      searchKeywords: searchKeywords.value,
      status: statusFilter.value,
      page: currentPage.value,
      pageSize: pageSize.value,
      risk_mode: alertFilterMode.value
    }
    
    if (ownerSearch.value && ownerSearch.value.trim()) {
      params.owner = ownerSearch.value.trim()
    }
    
    if (actorSearch.value && actorSearch.value.trim()) {
      params.actor = actorSearch.value.trim()
    }
    
    const range = computeSelectedRange()
    if (range) {
      params.startTime = range.start
      params.endTime = range.end
    }
    
    const response = await getAlerts(params)
    const rawAlerts = response.data || []

    // 为列表中的每条告警计算 TTA（responseTime），与详情页保持一致
    alerts.value = rawAlerts.map(item => {
      const createdAt = item.create_time || item.createTime
      const closedAt = item.close_time || item.closeTime
      const handleStatus = item.handle_status || item.status

      const computedTtr = calculateTTR(createdAt, closedAt, handleStatus)
      const normalizedTtr = computedTtr === '-' && item.ttr ? item.ttr : computedTtr

      return {
        ...item,
        responseTime: normalizedTtr
      }
    })
    
    total.value = response.total
    
  } catch (error) {
    console.error('Failed to load alerts:', error)
  } finally {
    loadingAlerts.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  return loadAlerts()
}

const reloadAlertsFromFirstPage = () => {
  if (currentPage.value === 1) {
    return loadAlerts()
  }
  return handlePageChange(1)
}

const loadAllData = async (reloadFromFirstPage = false) => {
  const loadAlertsFn = reloadFromFirstPage ? reloadAlertsFromFirstPage : loadAlerts
  const tasks = [loadAlertsFn()]
  
  if (showCharts.value) {
    tasks.push(
      loadStatistics(),
      loadAlertTypeDistribution(),
      loadAlertStatusBySeverity()
    )
  }
  
  await Promise.all(tasks)
}

const handleRefresh = async () => {
  if (isRefreshing.value) return
  
  isRefreshing.value = true
  try {
    await loadAllData()
  } catch (error) {
    console.error('Failed to refresh:', error)
  } finally {
    isRefreshing.value = false
  }
}

const loadStatistics = async () => {
  if (!showCharts.value) {
    return
  }
  automationRateLoading.value = true
  try {
    const range = computeSelectedRange()
    const response = await getAlertStatistics(
      range.start,
      range.end
    )
    if (response && response.data) {
      if (response.data.automation_rate !== undefined) {
        statistics.value.automationRate = response.data.automation_rate
      }
      if (response.data.total_closed !== undefined) {
        statistics.value.totalClosed = response.data.total_closed
      }
      if (response.data.auto_closed !== undefined) {
        statistics.value.autoClosed = response.data.auto_closed
      }
      if (statistics.value.automationRateChange === 0) {
        statistics.value.automationRateChange = 0
        statistics.value.automationRateTrend = 'down'
      }
    }
  } catch (error) {
    console.error('Failed to load statistics:', error)
  } finally {
    automationRateLoading.value = false
  }
}

const saveSearchKeywords = () => {
  try {
    localStorage.setItem('alerts-searchKeywords', JSON.stringify(searchKeywords.value))
  } catch (error) {
    console.warn('Failed to save search keywords to localStorage:', error)
  }
}

const addKeyword = () => {
  const keyword = currentSearchInput.value.trim()
  if (keyword && !searchKeywords.value.includes(keyword)) {
    searchKeywords.value.push(keyword)
    currentSearchInput.value = ''
    saveSearchKeywords()
    reloadAlertsFromFirstPage()
  }
}

const removeKeyword = (index) => {
  searchKeywords.value.splice(index, 1)
  saveSearchKeywords()
  reloadAlertsFromFirstPage()
}

const handleKeywordDeleteKey = (event) => {
  if (event.key === 'Backspace' && !currentSearchInput.value && searchKeywords.value.length > 0) {
    event.preventDefault()
    removeKeyword(searchKeywords.value.length - 1)
  }
}

const handleOwnerSearch = () => {
  reloadAlertsFromFirstPage()
}

const handleOwnerSearchInput = () => {
  if (!ownerSearch.value.trim()) {
    reloadAlertsFromFirstPage()
  }
}

const handleActorSearch = () => {
  reloadAlertsFromFirstPage()
}

const handleActorSearchInput = () => {
  if (!actorSearch.value.trim()) {
    reloadAlertsFromFirstPage()
  }
}

const handleFilter = () => {
  try {
    localStorage.setItem('alerts-status-filter', statusFilter.value)
  } catch (error) {
    console.warn('Failed to save status filter to localStorage:', error)
  }
  reloadAlertsFromFirstPage()
  loadAlertTypeDistribution()
  loadAlertStatusBySeverity()
}

watch(alertFilterMode, (newMode) => {
  localStorage.setItem('alerts-filter-mode', newMode)
  
  if (newMode === 'highRisk') {
    statusFilter.value = 'all'
    localStorage.setItem('alerts-status-filter', 'all')
    loadAlertTypeDistribution()
    loadAlertStatusBySeverity()
  } else if (newMode === 'unclosedHighRisk') {
    statusFilter.value = 'open'
    localStorage.setItem('alerts-status-filter', 'open')
    loadAlertTypeDistribution()
    loadAlertStatusBySeverity()
  }
  
  reloadAlertsFromFirstPage()
})

const handlePageSizeChange = () => {
  pageSize.value = Number(pageSize.value)
  try {
    localStorage.setItem('alerts-pageSize', String(pageSize.value))
  } catch (error) {
    console.warn('Failed to save page size to localStorage:', error)
  }
  handlePageChange(1)
}

const handleSelect = (items) => {
  selectedAlerts.value = items.map(alert => alert.id)
}

const handleSelectAll = (items) => {
  selectedAlerts.value = items.map(alert => alert.id)
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

const router = useRouter()
const route = useRoute()
const currentAlertId = computed(() => route.params.id ?? null)

const openAlertDetail = (alertId) => {
  router.push({ path: `/alerts/${alertId}`, replace: true })
}

const openAlertDetailInNewWindow = (alertId) => {
  const route = router.resolve({ path: `/alerts/${alertId}` })
  const url = window.location.origin + route.href
  window.open(url, '_blank')
}

const closeAlertDetail = () => {
  router.push({ path: '/alerts', replace: true })
}

const handleAlertClosed = () => {
  loadAlerts()
  selectedAlerts.value = []
  if (dataTableRef.value) {
    dataTableRef.value.clearSelection()
  }
}

const handleAlertConvertedToIncident = () => {
  loadAlerts()
  selectedAlerts.value = []
  if (dataTableRef.value) {
    dataTableRef.value.clearSelection()
  }
}

const isWordWrap = computed(() => {
  return dataTableRef.value?.wordWrap?.value ?? true
})

const handleToggleWordWrap = () => {
  if (dataTableRef.value) {
    dataTableRef.value.toggleWordWrap()
    showMoreMenu.value = false
  }
}

const handleToggleChartsVisibility = async () => {
  const next = !showCharts.value
  showCharts.value = next
  persistChartsVisibilityPreference(next)
  showMoreMenu.value = false

  if (next) {
    ensureAlertTypeChart()
    ensureAlertStatusChart()
    await Promise.all([
      loadStatistics(),
      loadAlertTypeDistribution(),
      loadAlertStatusBySeverity()
    ])
  } else {
    disposeAlertTypeChart()
    disposeAlertStatusChart()
  }
}

const handleCreateAlertFromMenu = () => {
  openCreateAlertDialog()
  showMoreMenu.value = false
}

const handleAssociateIncidentFromMenu = () => {
  openAssociateIncidentDialog()
  showMoreMenu.value = false
}

const handleCreateIncidentFromMenu = () => {
  openCreateIncidentDialog()
  showMoreMenu.value = false
}

const handleConvertToVulnerability = () => {
  if (selectedAlerts.value.length === 0) {
    console.warn('No alerts selected')
    return
  }
  openCreateVulnerabilityDialog()
  showMoreMenu.value = false
}

const openCreateVulnerabilityDialog = () => {
  const selectedAlertObjects = alerts.value.filter(alert => selectedAlerts.value.includes(alert.id))
  
  if (selectedAlertObjects.length === 0) {
    console.warn('No alerts selected')
    return
  }
  
  const firstAlert = selectedAlertObjects[0]
  
  let alertDescription = ''
  if (firstAlert.aiAnalysis?.description) {
    alertDescription = typeof firstAlert.aiAnalysis.description === 'string' 
      ? firstAlert.aiAnalysis.description 
      : JSON.stringify(firstAlert.aiAnalysis.description)
  } else if (firstAlert.description) {
    alertDescription = typeof firstAlert.description === 'string' 
      ? firstAlert.description 
      : JSON.stringify(firstAlert.description)
  }
  
  createVulnerabilityInitialData.value = {
    title: firstAlert.title || '',
    riskLevel: firstAlert.riskLevel || 'medium',
    status: firstAlert.status || 'open',
    owner: firstAlert.owner || '',
    actor: firstAlert.actor || '',
    description: alertDescription
  }
  
  showCreateVulnerabilityDialog.value = true
}

const closeCreateVulnerabilityDialog = () => {
  showCreateVulnerabilityDialog.value = false
  createVulnerabilityInitialData.value = null
}

const handleVulnerabilityCreated = () => {
  loadAlerts()
  selectedAlerts.value = []
  if (dataTableRef.value) {
    dataTableRef.value.clearSelection()
  }
}

const handleClickOutside = (event) => {
  const dropdown = event.target.closest('.more-menu-dropdown')
  const button = event.target.closest('.more-menu-button')
  if (!dropdown && !button) {
    showMoreMenu.value = false
  }
}

const openBatchCloseDialog = () => {
  if (selectedAlerts.value.length === 0) {
    console.warn('No alerts selected')
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
}

const handleBatchClose = async () => {
  if (!closeConclusion.value.category || !closeConclusion.value.notes.trim() || isBatchClosing.value) {
    return
  }

  if (selectedAlerts.value.length === 0) {
    toast.warn('请至少选择一个告警', '提示')
    return
  }

  try {
    isBatchClosing.value = true
    
    await batchCloseAlertsByPut(
      selectedAlerts.value,
      closeConclusion.value.category,
      closeConclusion.value.notes.trim()
    )
    persistRecentCloseComment(closeConclusion.value.notes.trim())
    
    toast.success(
      t('alerts.list.batchCloseSuccess', { count: selectedAlerts.value.length }) || 
      `成功关闭 ${selectedAlerts.value.length} 个告警`, 
      t('common.operationSuccess')
    )
    
    closeBatchCloseDialog()
    selectedAlerts.value = []
    if (dataTableRef.value) {
      dataTableRef.value.clearSelection()
    }
    
    loadAlerts()
  } catch (error) {
    console.error('Failed to batch close alerts:', error)
    const errorMessage = error?.response?.data?.message || error?.response?.data?.error_message || error?.message || t('alerts.list.batchCloseError') || '批量关闭告警失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
  } finally {
    isBatchClosing.value = false
  }
}


const openAssociateIncidentDialog = () => {
  if (selectedAlerts.value.length === 0) {
    console.warn('No alerts selected')
    return
  }
  showAssociateIncidentDialog.value = true
}

const closeAssociateIncidentDialog = () => {
  showAssociateIncidentDialog.value = false
}

const handleAssociateIncidentSuccess = () => {
  closeAssociateIncidentDialog()
  selectedAlerts.value = []
  if (dataTableRef.value) {
    dataTableRef.value.clearSelection()
  }
  loadAlerts()
}

const openCreateIncidentDialog = () => {
  const selectedAlertObjects = alerts.value.filter(alert => selectedAlerts.value.includes(alert.id))

  const firstAlert = selectedAlertObjects[0]
  
  const createTime =
    parseToDate(firstAlert?.createTime)
    || parseToDate(firstAlert?.create_time)
    || parseToDate(firstAlert?.timestamp)
    || new Date()
  
  const incidentTitle = firstAlert.title || ''
  
  let alertDescription = ''
  if (firstAlert.aiAnalysis?.description) {
    alertDescription = typeof firstAlert.aiAnalysis.description === 'string' 
      ? firstAlert.aiAnalysis.description 
      : JSON.stringify(firstAlert.aiAnalysis.description)
  } else if (firstAlert.description) {
    alertDescription = typeof firstAlert.description === 'string' 
      ? firstAlert.description 
      : JSON.stringify(firstAlert.description)
  }
  
  createIncidentInitialData.value = {
    title: incidentTitle,
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
  loadAlerts()
  selectedAlerts.value = []
  if (dataTableRef.value) {
    dataTableRef.value.clearSelection()
  }
}

const openCreateAlertDialog = () => {
  showCreateAlertDialog.value = true
}

const closeCreateAlertDialog = () => {
  showCreateAlertDialog.value = false
}

const handleAlertCreated = async () => {
  await loadAllData()
}

const handleTimeRangeChange = async (rangeKey) => {
  selectedTimeRange.value = rangeKey
  if (rangeKey !== 'customRange') {
    await loadAllData(true)
  }
}

const handleCustomRangeChange = async (newRange) => {
  customTimeRange.value = newRange
  if (selectedTimeRange.value === 'customRange' && newRange && newRange.length === 2) {
    await loadAllData(true)
  }
}

onMounted(async () => {
  if (showCharts.value) {
    ensureAlertTypeChart()
    ensureAlertStatusChart()
  }
  await loadAllData()
  document.addEventListener('click', handleClickOutside)
  refreshRecentCloseComments()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  disposeAlertTypeChart()
  disposeAlertStatusChart()
  hideRecentCloseCommentsDropdown()
})

const alertsTimeRangeLabel = computed(() => {
  if (selectedTimeRange.value === 'customRange') {
    if (customTimeRange.value && customTimeRange.value.length === 2) {
      return `${formatDateTime(customTimeRange.value[0])} ~ ${formatDateTime(customTimeRange.value[1])}`
    }
    return t('common.timeRange.customRange')
  }
  return t(`common.timeRange.${selectedTimeRange.value}`) || t('common.timeRange.last24Hours')
})

// Delete confirmation validation
const isDeleteConfirmValid = computed(() => {
  return deleteConfirmInput.value.toLowerCase() === 'delete'
})

const openBatchDeleteDialog = () => {
  if (selectedAlerts.value.length === 0) {
    console.warn('No alerts selected')
    return
  }
  showBatchDeleteDialog.value = true
  deleteConfirmInput.value = ''
}

const closeBatchDeleteDialog = () => {
  showBatchDeleteDialog.value = false
  deleteConfirmInput.value = ''
}

const handleBatchDelete = async () => {
  if (!isDeleteConfirmValid.value || isBatchDeleting.value) {
    return
  }

  if (selectedAlerts.value.length === 0) {
    toast.warn('请至少选择一个告警', '提示')
    return
  }

  try {
    isBatchDeleting.value = true
    
    // 调用删除接口
    await deleteAlerts(selectedAlerts.value)
    
    // 显示成功提示
    toast.success(
      t('alerts.list.batchDeleteDialog.deleteSuccess', { count: selectedAlerts.value.length }) || 
      `成功删除 ${selectedAlerts.value.length} 条告警`, 
      t('common.operationSuccess')
    )
    
    // Close dialog and reset form
    closeBatchDeleteDialog()
    selectedAlerts.value = []
    if (dataTableRef.value) {
      dataTableRef.value.clearSelection()
    }
    
    // Reload alert list
    loadAlerts()
  } catch (error) {
    console.error('Failed to delete alerts:', error)
    // 显示错误提示
    const errorMessage = error?.response?.data?.message || error?.response?.data?.error_message || error?.message || t('alerts.list.batchDeleteDialog.deleteError') || '删除告警失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
  } finally {
    isBatchDeleting.value = false
  }
}
</script>


