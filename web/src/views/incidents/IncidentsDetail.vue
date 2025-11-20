<template>
  <div class="w-full relative overflow-x-hidden">
    <!-- 加载遮罩层 -->
    <div
      v-if="loadingIncident"
      class="absolute inset-0 bg-[#111822]/80 backdrop-blur-sm z-50 flex items-center justify-center rounded-xl"
    >
      <div class="flex flex-col items-center gap-4">
        <div class="relative w-16 h-16">
          <div class="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-transparent border-t-primary rounded-full animate-spin"></div>
        </div>
        <p class="text-gray-400 text-sm font-medium">{{ $t('common.loading') || '加载中...' }}</p>
      </div>
    </div>
    <!-- 页面标题和操作 -->
    <header class="flex flex-wrap justify-between items-start gap-4 mb-6">
      <div class="flex flex-col gap-2">
        <h1 class="text-white text-xl font-bold leading-tight tracking-tight">
          {{ incident?.name }}
        </h1>
        <div class="flex flex-wrap items-center gap-x-4 gap-y-2 text-slate-400 text-base font-normal leading-normal">
          <div class="flex items-center gap-1.5">
            <span>{{ $t('incidents.detail.actor') }}:</span>
            <span class="text-white">{{ incident?.actor }}</span>
          </div>
          <div class="h-4 w-px bg-slate-600/50"></div>
          <div class="flex items-center gap-1.5">
            <span>{{ $t('incidents.detail.createTime') }}:</span>
            <span class="text-white">{{ formatDateTime(incident?.createTime) }}</span>
          </div>
          <div class="h-4 w-px bg-slate-600/50"></div>
          <div class="flex items-center gap-1.5">
            <span>{{ $t('incidents.detail.updateTime') }}:</span>
            <span class="text-white">{{ formatDateTime(incident?.updateTime) }}</span>
          </div>
        </div>
      </div>
      <div class="flex flex-1 gap-3 flex-wrap justify-start sm:justify-end min-w-max">
        <button
          @click="openEditDialog"
          class="flex min-w-[84px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-10 px-4 bg-slate-700 hover:bg-slate-600 text-white text-sm font-bold leading-normal tracking-[0.015em] transition-colors"
        >
          <span class="material-symbols-outlined text-base">edit</span>
          <span class="truncate">{{ $t('incidents.detail.edit') }}</span>
        </button>
        <button
          @click="openCloseDialog"
          class="flex min-w-[84px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-10 px-4 bg-primary hover:bg-primary/90 text-white text-sm font-bold leading-normal tracking-[0.015em] transition-colors"
        >
          <span class="material-symbols-outlined text-base">archive</span>
          <span class="truncate">{{ $t('incidents.detail.closeIncident') }}</span>
        </button>
        <button
          @click="handleRefresh"
          :disabled="loadingIncident"
          class="bg-[#2a3546] hover:bg-[#3c4a60] text-sm font-medium text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-[#2a3546] h-10"
          :title="$t('common.refresh') || 'Refresh'"
        >
          <span
            class="material-symbols-outlined text-base"
            :class="{ 'animate-spin': loadingIncident }"
          >
            refresh
          </span>
        </button>
        <button
          @click="handleShare"
          class="bg-[#2a3546] hover:bg-[#3c4a60] text-sm font-medium text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center h-10"
          :title="$t('incidents.detail.share') || 'Share'"
        >
          <span class="material-symbols-outlined text-base">share</span>
        </button>
      </div>
    </header>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
        <p class="text-slate-300 text-sm font-medium leading-normal">
          {{ $t('incidents.detail.status') }}
        </p>
        <div class="flex items-center gap-2">
          <span
            :class="[
              'w-2 h-2 rounded-full',
              getIncidentStatusDotClass(incident?.status)
            ]"
          ></span>
          <p class="text-white text-xl font-bold leading-tight">
            {{ getStatusText(incident?.status) }}
          </p>
        </div>
      </div>
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
        <p class="text-slate-300 text-sm font-medium leading-normal">
          {{ $t('incidents.detail.severity') }}
        </p>
        <div class="flex items-center gap-2">
          <span
            :class="[
              'w-2 h-2 rounded-full',
              getSeverityDotClass(incident?.severity)
            ]"
          ></span>
          <p
            :class="[
              'text-xl font-bold leading-tight',
              getSeverityTextClass(incident?.severity)
            ]"
          >
            {{ $t(`common.severity.${incident?.severity?.toLowerCase()}`) }}
          </p>
        </div>
      </div>
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
        <p class="text-slate-300 text-sm font-medium leading-normal">
          {{ $t('incidents.detail.affectedAssets') }}
        </p>
        <p class="text-white text-xl font-bold leading-tight">
          {{ incident?.affectedAssets || 0 }}
        </p>
      </div>
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
        <p class="text-slate-300 text-sm font-medium leading-normal">
          {{ $t('incidents.detail.responsibleDepartment') }}
        </p>
        <p class="text-white text-xl font-bold leading-tight">
          {{ incident?.responsibleDept || '-' }}
        </p>
      </div>
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
        <p class="text-slate-300 text-sm font-medium leading-normal">
          {{ $t('incidents.detail.responsiblePerson') }}
        </p>
        <p class="text-white text-xl font-bold leading-tight">
          {{ incident?.owner || incident?.responsiblePerson || '-' }}
        </p>
      </div>
    </div>

    <!-- 标签页导航 -->
    <div class="mt-8 border-b border-slate-700">
      <nav aria-label="Tabs" class="flex -mb-px space-x-6">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            'whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === tab.key
              ? 'text-primary border-primary'
              : 'text-slate-400 hover:text-white border-transparent'
          ]"
        >
          {{ $t(tab.label) }}
        </button>
      </nav>
    </div>

    <!-- 标签页内容 -->
    <div class="mt-6 flex-grow">
      <!-- Event Graph Intelligence -->
      <div v-if="activeTab === 'eventGraph'" class="space-y-6">
        <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6 space-y-4 relative overflow-hidden">
          <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div class="flex-1">
              <h3 class="text-white font-bold text-lg">
                {{ $t('incidents.detail.eventGraph.summaryTitle') }}
              </h3>
              <p class="text-slate-400 text-sm">
                {{ $t('incidents.detail.eventGraph.summaryParagraph1') }}
              </p>
            </div>
            <div class="flex items-center gap-2 md:justify-end">
              <button
                type="button"
                class="graph-regenerate-btn"
                :class="{ 'graph-regenerate-btn--loading': isRegeneratingGraph }"
                :disabled="isRegeneratingGraph"
                @click="handleRegenerateGraph"
              >
                <span class="material-symbols-outlined text-base">
                  {{ isRegeneratingGraph ? 'progress_activity' : 'auto_fix' }}
                </span>
                <span>{{ $t('incidents.detail.eventGraph.regenerateGraph') }}</span>
              </button>
            </div>
          </div>
          <div v-if="incident?.graphSummary" class="space-y-2">
            <div
              class="text-slate-200 leading-relaxed prose prose-invert max-w-none"
              :class="{ 'summary-collapsed': !isSummaryExpanded }"
              v-html="graphSummaryHtml"
            ></div>
            <button
              v-if="shouldShowSummaryExpand"
              type="button"
              @click="isSummaryExpanded = !isSummaryExpanded"
              class="text-primary hover:text-primary/80 text-sm font-medium flex items-center gap-1 transition-colors"
            >
              <span class="material-symbols-outlined text-base">
                {{ isSummaryExpanded ? 'expand_less' : 'expand_more' }}
              </span>
              <span>{{ isSummaryExpanded ? $t('common.collapse') : $t('common.expand') }}</span>
            </button>
          </div>
          <p v-else class="text-slate-500 leading-relaxed">
            {{ $t('incidents.detail.eventGraph.summaryUnavailable') }}
          </p>
          <p v-if="incident?.graphSummary" class="text-slate-400 text-sm">
            {{
              $t('incidents.detail.eventGraph.summaryParagraph2', {
                nodes: eventGraphStats.totalNodes,
                edges: eventGraphStats.totalEdges,
                alerts: eventGraphStats.alertNodes,
                ips: eventGraphStats.ipNodes
              })
            }}
          </p>
          <p v-if="incident?.graphSummary && graphLastGeneratedTime" class="text-slate-500 text-xs mt-2">
            上次生成时间：{{ graphLastGeneratedTime }}
          </p>
        </div>
        <div class="bg-slate-900/60 border border-slate-700 rounded-2xl overflow-hidden">
          <div v-if="hasGraphData" class="flex flex-col lg:flex-row min-h-[600px]">
            <div ref="graphContainerRef" class="flex-1 relative bg-[#0f172a] min-h-[600px]">
              <div class="absolute top-4 left-4 right-4 z-10 pointer-events-none">
                <div class="flex flex-col xl:flex-row gap-4 items-start pointer-events-auto" @click.stop>
                  <div class="flex flex-col md:flex-row gap-4 flex-1 w-full">
                    <div class="relative w-full md:w-64 flex items-center bg-slate-900/70 border border-slate-700 text-white rounded-lg pl-3 pr-3 h-11">
                      <span class="material-symbols-outlined text-slate-400 text-base mr-2">search</span>
                      <input
                        v-model="graphSearchQuery"
                        type="text"
                        class="w-full bg-transparent text-sm focus:ring-0 focus:outline-none placeholder:text-slate-500"
                        :placeholder="$t('incidents.detail.eventGraph.filterPlaceholder')"
                      />
                    </div>
                    <div class="relative w-full md:w-64">
                      <select
                        v-model="highlightedEntity"
                        class="w-full h-11 bg-slate-900/70 border border-slate-700 text-white rounded-lg pl-4 pr-10 text-sm focus:ring-2 focus:ring-primary/60 focus:border-primary/60 appearance-none"
                      >
                        <option value="">
                          {{
                            graphEntityOptions.length
                              ? $t('incidents.detail.eventGraph.selectorPlaceholder')
                              : $t('common.noData')
                          }}
                        </option>
                        <option
                          v-for="option in graphEntityOptions"
                          :key="option.id"
                          :value="option.id"
                        >
                          {{ option.label }}
                        </option>
                      </select>
                      <span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none text-base">expand_more</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-1 bg-slate-900/70 border border-slate-700 rounded-lg px-1 h-11">
                    <button
                      type="button"
                      class="graph-control-btn"
                      :disabled="!canZoomIn"
                      :title="$t('incidents.detail.eventGraph.controls.zoomIn')"
                      @click="handleGraphZoomIn"
                    >
                      <span class="material-symbols-outlined text-base">zoom_in</span>
                    </button>
                    <button
                      type="button"
                      class="graph-control-btn"
                      :disabled="!canZoomOut"
                      :title="$t('incidents.detail.eventGraph.controls.zoomOut')"
                      @click="handleGraphZoomOut"
                    >
                      <span class="material-symbols-outlined text-base">zoom_out</span>
                    </button>
                    <button
                      type="button"
                      class="graph-control-btn"
                      :title="$t('incidents.detail.eventGraph.controls.reset')"
                      @click="handleGraphResetView"
                    >
                      <span class="material-symbols-outlined text-base">center_focus_strong</span>
                    </button>
                    <button
                      type="button"
                      class="graph-control-btn"
                      :title="$t('incidents.detail.eventGraph.controls.fullscreen')"
                      @click="toggleGraphFullscreen"
                    >
                      <span class="material-symbols-outlined text-base">{{ graphFullscreenIcon }}</span>
                    </button>
                    <button
                      type="button"
                      class="graph-control-btn"
                      :title="$t('incidents.detail.eventGraph.controls.download')"
                      @click="handleGraphDownload"
                    >
                      <span class="material-symbols-outlined text-base">download</span>
                    </button>
                  </div>
                </div>
              </div>
              <div class="absolute inset-y-0 left-0 p-4 flex items-center z-10 pointer-events-none">
                <div class="pointer-events-auto flex items-start" @click.stop>
                  <div class="flex flex-col gap-1.5 text-[11px] uppercase tracking-wide">
                    <button
                      v-for="entry in legendEntries"
                      :key="entry.key"
                      type="button"
                      class="legend-entry"
                      :class="{ 'legend-entry--active': legendFlashKey === entry.key }"
                      @click.stop="handleLegendClick(entry.key)"
                    >
                      <span class="legend-entry__dot" :style="{ backgroundColor: entry.color }"></span>
                      <span class="legend-entry__label">{{ entry.label }}</span>
                    </button>
                  </div>
                </div>
              </div>
              <div class="w-full h-full" style="position: relative;" @click="handleGraphContainerClick">
                <div
                  ref="graphEchartsRef"
                  class="w-full h-full"
                  style="min-height: 480px; width: 100%; position: absolute; top: 0; left: 0; right: 0; bottom: 0;"
                ></div>
              </div>
            </div>
            <Transition name="fade">
              <div v-if="selectedGraphNode" class="flex w-full lg:w-auto">
                <div
                  class="hidden lg:block node-detail-resize-handle"
                  @pointerdown="startNodeDetailResize"
                ></div>
                <aside
                  class="w-full lg:w-auto bg-slate-950/80 border-t lg:border-t-0 lg:border-l border-slate-800 p-5 flex flex-col"
                  :style="nodeDetailPaneStyle"
                >
                  <div class="flex items-center justify-between mb-4">
                    <h3 class="text-white font-bold text-lg">{{ $t('incidents.detail.eventGraph.nodeDetail.title') }}</h3>
                    <div class="flex items-center space-x-1">
                      <button class="detail-action-btn" :title="$t('incidents.detail.eventGraph.nodeDetail.copy')" @click="copySelectedNode">
                        <span class="material-symbols-outlined text-sm">content_copy</span>
                      </button>
                      <button class="detail-action-btn" :title="$t('incidents.detail.eventGraph.nodeDetail.prune')" @click="pruneSelectedNode">
                        <span class="material-symbols-outlined text-sm">content_cut</span>
                      </button>
                      <button class="detail-action-btn" :title="$t('incidents.detail.eventGraph.nodeDetail.close')" @click="clearSelectedNode">
                        <span class="material-symbols-outlined text-sm">close</span>
                      </button>
                    </div>
                  </div>
                  <div class="flex-1 overflow-y-auto pr-1 space-y-5">
                    <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-4 space-y-3">
                      <div class="flex flex-col gap-1">
                        <p class="text-xs text-slate-400 uppercase tracking-wide">{{ $t('incidents.detail.eventGraph.nodeDetail.id') }}</p>
                        <p class="text-sm text-slate-200 break-all whitespace-pre-wrap">
                          {{ formatNodeDetailValue(selectedGraphNode.id) }}
                        </p>
                      </div>
                      <div class="flex flex-col gap-1">
                        <p class="text-xs text-slate-400 uppercase tracking-wide">{{ $t('incidents.detail.eventGraph.nodeDetail.labels') }}</p>
                        <p class="text-sm text-slate-200 whitespace-pre-wrap">
                          {{ formatNodeDetailValue((selectedGraphNode.labels || []).join(', ')) }}
                        </p>
                      </div>
                      <div class="flex flex-col gap-1">
                        <p class="text-xs text-slate-400 uppercase tracking-wide">{{ $t('incidents.detail.eventGraph.nodeDetail.entityType') }}</p>
                        <p class="text-sm text-slate-200 whitespace-pre-wrap">
                          {{ formatNodeDetailValue(selectedGraphNode.properties?.entity_type) }}
                        </p>
                      </div>
                      <div class="flex flex-col gap-1">
                        <p class="text-xs text-slate-400 uppercase tracking-wide">属性描述</p>
                        <div v-if="selectedNodePropertyDescription" class="space-y-1">
                          <p
                            class="text-sm text-slate-200 break-all whitespace-pre-wrap"
                            :class="{ 'property-description-collapsed': !isPropertyDescriptionExpanded }"
                          >
                            {{ formatNodeDetailValue(selectedNodePropertyDescription) }}
                          </p>
                          <button
                            v-if="shouldShowPropertyDescriptionExpand"
                            type="button"
                            @click="isPropertyDescriptionExpanded = !isPropertyDescriptionExpanded"
                            class="text-primary hover:text-primary/80 text-xs font-medium flex items-center gap-1 transition-colors"
                          >
                            <span class="material-symbols-outlined text-sm">
                              {{ isPropertyDescriptionExpanded ? 'expand_less' : 'expand_more' }}
                            </span>
                            <span>{{ isPropertyDescriptionExpanded ? $t('common.collapse') : $t('common.expand') }}</span>
                          </button>
                        </div>
                        <p v-else class="text-sm text-slate-500">
                          {{ $t('common.noData') || 'No data available' }}
                        </p>
                      </div>
                    </div>
                    <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                      <h3 class="text-sm font-semibold text-white mb-3">{{ $t('incidents.detail.eventGraph.nodeDetail.relations') }}</h3>
                      <div v-if="selectedNodeRelations.length" class="space-y-2">
                      <button
                        v-for="relation in selectedNodeRelations"
                        :key="`${relation.direction}-${relation.neighbor}`"
                        type="button"
                        class="block w-full text-left text-sm text-slate-200 py-0.5"
                        @click="handleRelationClick(relation.neighbor)"
                      >
                          {{ $t('incidents.detail.eventGraph.nodeDetail.neighborLabel') }}
                        <span class="neighbor-link">{{ relation.neighborLabel }}</span>
                      </button>
                      </div>
                      <p v-else class="text-xs text-slate-500">
                        {{ $t('common.noData') || 'No data available' }}
                      </p>
                    </div>
                  </div>
                </aside>
              </div>
            </Transition>
          </div>
          <div
            v-else
            class="min-h-[420px] flex flex-col items-center justify-center gap-3 text-center p-10 text-slate-400"
          >
            <p class="text-base font-medium">
              {{ $t('incidents.detail.eventGraph.summaryUnavailable') }}
            </p>
          </div>
        </div>
      </div>

      <!-- Overview 标签页 -->
      <div v-if="activeTab === 'overview'" class="flex flex-col gap-6">
        <!-- 事件描述 -->
        <div class="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-white font-bold text-lg">
              {{ $t('incidents.detail.overview.eventDescription') }}
            </h3>
          </div>
          <div class="overflow-x-hidden">
            <p class="text-slate-300 leading-relaxed whitespace-pre-wrap break-all event-description-text">
              {{ incident?.description || '-' }}
            </p>
            <p v-if="incident?.descriptionLastModified" class="text-slate-500 text-xs mt-3">
              {{ $t('incidents.detail.overview.lastModified') }} {{ formatLastModified(incident.descriptionLastModified) }} {{ $t('incidents.detail.overview.by') }} {{ incident.descriptionLastModifiedBy || '-' }}
            </p>
          </div>
        </div>

        <!-- 关联告警 -->
        <div class="bg-[#111822] border border-[#324867] rounded-xl">
          <div class="p-6 border-b border-[#324867]">
            <h3 class="text-white font-bold text-lg">
              {{ $t('incidents.detail.overview.associatedAlerts') }}
            </h3>
          </div>
          <DataTable
            :columns="associatedAlertsColumns"
            :items="formattedAssociatedAlerts"
            :selectable="false"
            :resizable="true"
            storage-key="incident-associated-alerts-table-columns"
            :default-widths="associatedAlertsDefaultWidths"
            :pagination="false"
          >
            <template #cell-createTime="{ value }">
              {{ formatDateTime(value) }}
            </template>
            <template #cell-alertTitle="{ item }">
              <div class="flex items-center gap-2">
                <button
                  @click.stop="openAlertDetailInNewWindow(item.id)"
                  class="flex-shrink-0 text-gray-400 hover:text-primary transition-colors p-1"
                  :title="$t('alerts.list.openInNewWindow') || '在新窗口打开'"
                >
                  <span class="material-symbols-outlined text-base">open_in_new</span>
                </button>
                <a
                  @click="openAlertDetail(item.id)"
                  class="text-primary hover:underline cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap flex-1 font-medium"
                  :title="item.title"
                >
                  {{ item.title }}
                </a>
              </div>
            </template>
            <template #cell-riskLevel="{ item }">
              <span
                :class="[
                  'text-xs font-medium me-2 px-2.5 py-0.5 rounded-full inline-block',
                  getRiskLevelClass(item.riskLevel)
                ]"
                :title="$t(`common.severity.${item.riskLevel}`)"
              >
                {{ $t(`common.severity.${item.riskLevel}`) }}
              </span>
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
            <template #cell-owner="{ value }">
              <div class="flex justify-center w-full">
                <UserAvatar :name="value" />
              </div>
            </template>
          </DataTable>
        </div>
      </div>

      <!-- Comments 标签页 -->
      <div v-if="activeTab === 'comments'" class="flex-grow">
        <div class="bg-slate-800/50 border border-slate-700 rounded-lg flex flex-col">
          <div class="p-6 pt-4 overflow-x-hidden">
            <CommentSection
              :comments="incident?.comments || []"
              @submit="handlePostComment"
            />
          </div>
        </div>
      </div>

    </div>

    <!-- 告警详情抽屉 -->
    <AlertDetail
      v-if="selectedAlertId"
      :alert-id="selectedAlertId"
      @close="closeAlertDetail"
    />

    <!-- 关闭事件对话框 -->
    <CloseIncidentDialog
      ref="closeDialogRef"
      :visible="showCloseDialog"
      :title="$t('incidents.detail.closeDialog.title')"
      :confirm-message="$t('incidents.detail.closeDialog.confirmMessage')"
      @close="closeCloseDialog"
      @submit="handleCloseIncident"
    />

    <!-- 编辑事件对话框 -->
    <EditIncidentDialog
      :visible="showEditDialog"
      :incident-id="route.params.id"
      :initial-data="editIncidentInitialData"
      @close="closeEditDialog"
      @updated="handleIncidentUpdated"
    />

    <!-- 分享成功提示 -->
    <Transition name="fade">
      <div
        v-if="showShareSuccess"
        class="fixed top-4 right-4 z-[100] bg-green-500 text-white px-4 py-2 rounded-md shadow-lg flex items-center gap-2"
      >
        <span class="material-symbols-outlined text-sm">check_circle</span>
        <span class="text-sm">{{ $t('incidents.detail.shareSuccess') || '已复制到剪切板' }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { getIncidentDetail, postComment, regenerateIncidentGraph } from '@/api/incidents'
import AlertDetail from '@/components/alerts/AlertDetail.vue'
import EditIncidentDialog from '@/components/incidents/EditIncidentDialog.vue'
import CloseIncidentDialog from '@/components/incidents/CloseIncidentDialog.vue'
import DataTable from '@/components/common/DataTable.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import CommentSection from '@/components/common/CommentSection.vue'
import { formatDateTime } from '@/utils/dateTime'
import { useToast } from '@/composables/useToast'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import * as echarts from 'echarts'

const ENTITY_COLOR_GRADIENT = {
  host: 'grad-rose',
  ip: 'grad-cyan',
  domain: 'grad-emerald',
  operation: 'grad-amber',
  user: 'grad-violet',
  tenant: 'grad-violet',
  alert: 'grad-rose',
  service: 'grad-emerald',
  other: 'grad-cyan'
}

const ENTITY_COLOR_SOLID = {
  host: '#fda4af',
  ip: '#67e8f9',
  domain: '#6ee7b7',
  operation: '#fcd34d',
  user: '#c4b5fd',
  tenant: '#c4b5fd',
  alert: '#fda4af',
  service: '#6ee7b7',
  other: '#60a5fa'
}

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const toast = useToast()
const translateOr = (key, fallback) => {
  const translated = t(key)
  return translated === key ? fallback : translated
}
const authStore = useAuthStore()

const incident = ref(null)
const loadingIncident = ref(false)
const activeTab = ref('overview')
const newComment = ref('')
const selectedAlertId = ref(null)
const showShareSuccess = ref(false)
const showCloseDialog = ref(false)
const isClosingIncident = ref(false)
const closeDialogRef = ref(null)
const showEditDialog = ref(false)
const editIncidentInitialData = ref(null)

const createEmptyGraphData = () => ({
  nodes: [],
  edges: []
})
const eventGraphData = ref(createEmptyGraphData())
const graphSearchQuery = ref('')
const highlightedEntity = ref('')
const selectedGraphNodeId = ref('')
const prunedNodeIds = ref(new Set())
const graphEchartsRef = ref(null)
const graphContainerRef = ref(null)
const graphEchartsInstance = ref(null)
const graphResizeHandler = ref(null)
const legendFlashKey = ref('')
const legendFlashTimer = ref(null)
const nodeDetailWidth = ref(320)
const resizingNodeDetail = ref(false)
const resizeStartX = ref(0)
const initialNodeDetailWidth = ref(320)
const isRefreshingGraph = ref(false)
const isRegeneratingGraph = ref(false)
const graphZoomLevel = ref(1)
const isGraphFullscreen = ref(false)
const isSummaryExpanded = ref(false)
const isPropertyDescriptionExpanded = ref(false)
const isDragging = ref(false)
const dragTimeout = ref(null)

const GRAPH_ZOOM_STEP = 0.2
const GRAPH_MIN_ZOOM = 0.5
const GRAPH_MAX_ZOOM = 2.5

const parseGraphData = (rawData) => {
  if (!rawData) {
    return createEmptyGraphData()
  }
  let parsed = rawData
  if (typeof rawData === 'string') {
    try {
      parsed = JSON.parse(rawData)
    } catch (error) {
      console.warn('Failed to parse graph data string', error)
      return createEmptyGraphData()
    }
  }
  return {
    nodes: Array.isArray(parsed.nodes) ? parsed.nodes : [],
    edges: Array.isArray(parsed.edges) ? parsed.edges : []
  }
}

const loadGraphData = (rawData) => {
  const parsed = parseGraphData(rawData)
  console.log('Loading graph data:', { 
    nodes: parsed.nodes?.length || 0, 
    edges: parsed.edges?.length || 0,
    rawData: rawData ? 'present' : 'missing',
    activeTab: activeTab.value
  })
  eventGraphData.value = parsed
  selectedGraphNodeId.value = ''
  highlightedEntity.value = ''
  prunedNodeIds.value = new Set()
  graphZoomLevel.value = 1
  
  // 如果当前在 Event Graph 标签页，初始化图表
  // 否则等待用户切换到该标签页时再初始化（通过 watch activeTab）
  if (activeTab.value === 'eventGraph') {
    nextTick(() => {
      // 使用多次重试，确保 DOM 已渲染
      let retries = 0
      const maxRetries = 10
      const tryInit = () => {
        if (graphEchartsRef.value && hasGraphData.value) {
          console.log('Initializing ECharts graph...')
          initEChartsGraph()
        } else if (retries < maxRetries) {
          retries++
          setTimeout(tryInit, 100)
        } else {
          console.warn('Cannot initialize graph after retries:', {
            hasRef: !!graphEchartsRef.value,
            hasData: hasGraphData.value,
            activeTab: activeTab.value
          })
        }
      }
      tryInit()
    })
  }
}

const baseGraphNodes = computed(() => {
  return (eventGraphData.value.nodes || []).filter((node) => !prunedNodeIds.value.has(node.id))
})

const displayGraphNodes = computed(() => {
  return baseGraphNodes.value
})

const displayGraphEdges = computed(() => {
  const nodeIds = new Set(displayGraphNodes.value.map((node) => node.id))
  return (eventGraphData.value.edges || []).filter(
    (edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target)
  )
})

const selectedGraphNode = computed(() => {
  if (!selectedGraphNodeId.value) {
    return null
  }
  return displayGraphNodes.value.find((node) => node.id === selectedGraphNodeId.value) || null
})

  // 初始化 ECharts 图表
const initEChartsGraph = () => {
  console.log('initEChartsGraph called', {
    hasRef: !!graphEchartsRef.value,
    hasData: hasGraphData.value,
    nodesCount: displayGraphNodes.value.length,
    edgesCount: displayGraphEdges.value.length
  })
  
  if (!graphEchartsRef.value) {
    console.warn('ECharts container ref is not available')
    return
  }
  
  if (!hasGraphData.value) {
    console.warn('No graph data available')
    return
  }
  
  if (displayGraphNodes.value.length === 0) {
    console.warn('No nodes to display')
    return
  }
  
  try {
    if (graphEchartsInstance.value) {
      graphEchartsInstance.value.dispose()
      graphEchartsInstance.value = null
    }
    
    // 确保容器有尺寸
    const container = graphEchartsRef.value
    console.log('Container dimensions:', {
      width: container.offsetWidth,
      height: container.offsetHeight,
      clientWidth: container.clientWidth,
      clientHeight: container.clientHeight
    })
    
    if (container.offsetWidth === 0 || container.offsetHeight === 0) {
      console.warn('ECharts container has no dimensions, retrying...')
      setTimeout(() => {
        initEChartsGraph()
      }, 200)
      return
    }
    
    graphEchartsInstance.value = echarts.init(container, 'dark')
    console.log('ECharts instance created')
    
    updateEChartsGraph()
    
    // 监听窗口大小变化
    if (typeof ResizeObserver !== 'undefined') {
      const resizeObserver = new ResizeObserver(() => {
        if (graphEchartsInstance.value) {
          graphEchartsInstance.value.resize()
        }
      })
      resizeObserver.observe(container)
    }
    
    // 监听全屏变化
    watch(isGraphFullscreen, () => {
      nextTick(() => {
        if (graphEchartsInstance.value) {
          graphEchartsInstance.value.resize()
        }
      })
    })
    
    // 监听窗口大小变化
    if (graphResizeHandler.value) {
      window.removeEventListener('resize', graphResizeHandler.value)
    }
    graphResizeHandler.value = () => {
      if (graphEchartsInstance.value) {
        graphEchartsInstance.value.resize()
      }
    }
    window.addEventListener('resize', graphResizeHandler.value)
  } catch (error) {
    console.error('Failed to initialize ECharts graph:', error)
  }
}

// 更新 ECharts 图表数据
const updateEChartsGraph = () => {
  if (!graphEchartsInstance.value) {
    console.warn('ECharts instance is not available')
    return
  }
  
  if (!hasGraphData.value) {
    console.warn('No graph data available for update')
    return
  }
  
  if (displayGraphNodes.value.length === 0) {
    console.warn('No nodes to display')
    return
  }
  
  console.log('Updating ECharts graph with:', {
    nodes: displayGraphNodes.value.length,
    edges: displayGraphEdges.value.length,
    sampleNode: displayGraphNodes.value[0],
    sampleEdge: displayGraphEdges.value[0]
  })
  
  const nodes = displayGraphNodes.value.map((node) => {
    const type = (node.properties?.entity_type || 'other').toLowerCase()
    const color = ENTITY_COLOR_SOLID[type] || ENTITY_COLOR_SOLID.other
    const degree = nodeDegreeMap.value[node.id] || 0
    const size = Math.min(20 + degree * 2, 40)
    
    // 根据搜索和选中状态设置样式
    // 中间透明度低，边缘透明度高（通过borderOpacity实现渐变效果）
    let itemStyle = { 
      color,
      opacity: 0.5, // 中间透明度低
      borderColor: 'rgba(148, 163, 184, 0.8)', // 边缘透明度高
      borderWidth: 1.5,
      borderOpacity: 0.8 // 边缘透明度高
    }
    let label = { show: true, fontSize: 10, color: '#fff' }
    
    if (graphSearchQuery.value.trim()) {
      if (!filteredNodeIds.value.has(node.id)) {
        itemStyle.opacity = 0.15
        label.show = false
      } else {
        // 搜索匹配的节点保持较高透明度
        itemStyle.opacity = 0.8
      }
    }
    
    if (selectedGraphNodeId.value) {
      if (relatedNodeIds.value.has(node.id)) {
        itemStyle.borderColor = '#fbbf24'
        itemStyle.borderWidth = 1.5
        itemStyle.borderOpacity = 0.7
        // 中间透明度低，边缘透明度高
        itemStyle.opacity = 0.6
      } else {
        itemStyle.opacity = 0.2
        label.show = false
      }
    }
    
    if (selectedGraphNodeId.value === node.id) {
      itemStyle.borderColor = '#60a5fa'
      itemStyle.borderWidth = 1.5
      itemStyle.borderOpacity = 0.8
      itemStyle.shadowBlur = 10
      itemStyle.shadowColor = '#60a5fa'
      // 中间透明度低，边缘透明度高（通过borderOpacity实现）
      itemStyle.opacity = 0.5
    }
    
    return {
      id: node.id,
      name: formatNodeLabel(node),
      value: node.id,
      symbolSize: size,
      itemStyle,
      label,
      category: type,
      properties: node.properties,
      labels: node.labels
    }
  })
  
  const edges = displayGraphEdges.value.map((edge) => {
    let lineStyle = {
      color: '#64748b',
      opacity: 0.25,
      width: 1.4
    }
    
    if (selectedGraphNodeId.value) {
      if (edge.source === selectedGraphNodeId.value || edge.target === selectedGraphNodeId.value) {
        lineStyle.color = '#38bdf8'
        lineStyle.opacity = 0.85
        lineStyle.width = 2.6
      } else if (relatedNodeIds.value.has(edge.source) && relatedNodeIds.value.has(edge.target)) {
        lineStyle.opacity = 0.6
      } else {
        lineStyle.opacity = 0.2
      }
    }
    
    return {
      source: edge.source,
      target: edge.target,
      lineStyle
    }
  })
  
  // 计算类别，用于分簇
  const categories = []
  const categoryMap = new Map()
  displayGraphNodes.value.forEach((node) => {
    const type = (node.properties?.entity_type || 'other').toLowerCase()
    if (!categoryMap.has(type)) {
      const color = ENTITY_COLOR_SOLID[type] || ENTITY_COLOR_SOLID.other
      categoryMap.set(type, categories.length)
      categories.push({
        name: type,
        itemStyle: { color }
      })
    }
  })
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      show: true,
      trigger: 'item',
      backgroundColor: 'rgba(30, 41, 59, 0.98)',
      borderColor: 'rgba(148, 163, 184, 0.4)',
      borderWidth: 1,
      borderRadius: 8,
      textStyle: {
        color: '#e2e8f0',
        fontSize: 12,
        fontFamily: 'system-ui, -apple-system, sans-serif'
      },
      padding: [12, 16],
      extraCssText: 'box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);',
      formatter: (params) => {
        if (params.dataType === 'node') {
          const node = displayGraphNodes.value.find(n => n.id === params.data.id)
          if (node) {
            const type = node.properties?.entity_type || 'unknown'
            const typeColor = ENTITY_COLOR_SOLID[type.toLowerCase()] || ENTITY_COLOR_SOLID.other
            // 获取完整的 label，不省略
            const label = node.labels?.[0] || node.id || node.properties?.entity_id || 'entity'
            return `<div style="padding: 0; line-height: 1.5;">
              <div style="font-weight: 600; margin-bottom: 8px; color: #ffffff; font-size: 13px; letter-spacing: 0.01em; word-wrap: break-word; max-width: 300px;">${label}</div>
              <div style="display: flex; align-items: center; gap: 6px;">
                <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: ${typeColor}; flex-shrink: 0;"></span>
                <span style="font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 500;">${type}</span>
              </div>
            </div>`
          }
        }
        return ''
      }
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: nodes,
        links: edges,
        categories,
        roam: true, // 启用缩放和平移（拖动画布）
        draggable: true, // 启用节点拖动
        label: {
          show: true,
          position: 'right',
          fontSize: 10,
          color: '#fff'
        },
        labelLayout: {
          hideOverlap: true
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 3
          }
        },
        force: {
          initLayout: 'circular',
          // 降低排斥力，使节点更容易聚集，拖动时只影响直接连接的节点
          repulsion: isDragging.value ? 50 : 100,
          // 降低重力，减少向中心聚集的趋势，让节点更自由地形成簇
          gravity: 0.05,
          // 动态调整边的长度：拖动时变长，稳定后变短
          edgeLength: isDragging.value ? [50, 120] : [30, 80],
          layoutAnimation: true,
          // 增加摩擦，使布局更稳定，减少拖动时的连锁反应
          friction: 0.95,
          // 拖动时只带动相关节点（通过降低repulsion实现）
          preventOverlap: true
        },
        lineStyle: {
          color: '#64748b',
          opacity: 0.25,
          curveness: 0.3
        },
        itemStyle: {
          borderColor: 'rgba(148, 163, 184, 0.4)',
          borderWidth: 1.5,
          opacity: 0.7
        }
      }
    ]
  }
  
  try {
    console.log('Setting ECharts option:', {
      nodesCount: nodes.length,
      edgesCount: edges.length,
      categoriesCount: categories.length,
      option: JSON.stringify(option, null, 2).substring(0, 500)
    })
    graphEchartsInstance.value.setOption(option, true)
    console.log('ECharts option set successfully')
    
    // 监听节点点击事件
    graphEchartsInstance.value.off('click')
    graphEchartsInstance.value.on('click', (params) => {
      console.log('ECharts click event:', params)
      // 检查是否是节点点击
      if (params && params.dataType === 'node' && params.data) {
        // 阻止事件冒泡，防止触发背景点击事件
        if (params.event && params.event.event) {
          params.event.event.stopPropagation()
        }
        // 尝试多种方式获取节点ID
        const nodeId = params.data.id || params.data.value || (params.data.name && displayGraphNodes.value.find(n => formatNodeLabel(n) === params.data.name)?.id)
        console.log('Node clicked, nodeId:', nodeId, 'params.data:', params.data)
        if (nodeId) {
          // 使用 nextTick 确保在下一个事件循环中处理，避免与背景点击冲突
          nextTick(() => {
            handleNodeClick(nodeId)
          })
        } else {
          console.warn('Node clicked but no id found:', params.data)
        }
      } else {
        // 点击的不是节点，是背景（params 为 null 或 params.dataType 不是 'node'）
        console.log('Background clicked, clearing selection', params)
        clearSelectedNode()
        // 立即更新图表以清除凸显效果
        if (graphEchartsInstance.value) {
          updateEChartsGraph()
        }
      }
    })
    
    
    // 监听拖动开始事件（ECharts graph 支持 dragstart）
    graphEchartsInstance.value.off('dragstart')
    graphEchartsInstance.value.on('dragstart', (params) => {
      if (params.dataType === 'node') {
        isDragging.value = true
        // 清除之前的超时
        if (dragTimeout.value) {
          clearTimeout(dragTimeout.value)
        }
        // 更新图表以应用拖长效果和降低排斥力
        nextTick(() => {
          if (graphEchartsInstance.value) {
            const option = graphEchartsInstance.value.getOption()
            if (option.series && option.series[0] && option.series[0].force) {
              option.series[0].force.edgeLength = [50, 120]
              option.series[0].force.repulsion = 50
              graphEchartsInstance.value.setOption(option, false)
            }
          }
        })
      }
    })
    
    // 监听拖动事件（持续更新）
    graphEchartsInstance.value.off('drag')
    graphEchartsInstance.value.on('drag', (params) => {
      if (params.dataType === 'node' && isDragging.value) {
        // 拖动时动态更新边的长度和排斥力
        if (graphEchartsInstance.value) {
          const option = graphEchartsInstance.value.getOption()
          if (option.series && option.series[0] && option.series[0].force) {
            option.series[0].force.edgeLength = [50, 120]
            option.series[0].force.repulsion = 50
            graphEchartsInstance.value.setOption(option, false)
          }
        }
      }
    })
    
    // 监听拖动结束事件
    graphEchartsInstance.value.off('dragend')
    graphEchartsInstance.value.on('dragend', (params) => {
      if (params.dataType === 'node') {
        // 延迟恢复，让布局稳定
        if (dragTimeout.value) {
          clearTimeout(dragTimeout.value)
        }
        dragTimeout.value = setTimeout(() => {
          isDragging.value = false
          // 恢复边的长度和排斥力
          if (graphEchartsInstance.value) {
            updateEChartsGraph()
          }
        }, 500)
      }
    })
  } catch (error) {
    console.error('Failed to update ECharts graph:', error)
    console.error('Error details:', {
      message: error.message,
      stack: error.stack
    })
  }
}


const canZoomIn = computed(() => true)
const canZoomOut = computed(() => true)
const graphFullscreenIcon = computed(() => (isGraphFullscreen.value ? 'fullscreen_exit' : 'fullscreen'))

const graphEntityOptions = computed(() =>
  displayGraphNodes.value.map((node) => ({
    id: node.id,
    label: `${(node.properties?.entity_type || 'entity').toUpperCase()} • ${node.id}`
  }))
)

const hasGraphData = computed(() => (eventGraphData.value.nodes || []).length > 0)
const graphStatus = computed(() => incident.value?.graphStatus || 'missing')
const graphStatusLabel = computed(() =>
  t(`incidents.detail.eventGraph.graphStatus.${graphStatus.value}`, graphStatus.value)
)
const graphStatusIcon = computed(() => {
  if (graphStatus.value === 'ready') {
    return 'task_alt'
  }
  if (graphStatus.value === 'processing') {
    return 'progress_activity'
  }
  if (graphStatus.value === 'error') {
    return 'error'
  }
  return 'motion_photos_paused'
})
const graphStatusClass = computed(() => {
  if (graphStatus.value === 'ready') {
    return 'text-emerald-300 bg-emerald-500/10 border border-emerald-500/20'
  }
  if (graphStatus.value === 'processing') {
    return 'text-sky-200 bg-sky-500/10 border border-sky-500/20'
  }
  if (graphStatus.value === 'error') {
    return 'text-red-300 bg-red-500/10 border border-red-500/20'
  }
  return 'text-amber-200 bg-amber-500/10 border border-amber-500/20'
})

const graphSummaryHtml = computed(() => {
  if (!incident.value?.graphSummary) {
    return ''
  }
  try {
    const rendered = marked.parse(incident.value.graphSummary)
    return DOMPurify.sanitize(rendered)
  } catch (error) {
    console.error('Failed to render graph summary markdown', error)
    return DOMPurify.sanitize(incident.value.graphSummary)
  }
})

const graphLastGeneratedTime = computed(() => {
  if (!incident.value?.updateTime) {
    return null
  }
  try {
    const date = new Date(incident.value.updateTime)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  } catch (error) {
    console.error('Failed to format graph generation time', error)
    return null
  }
})

const shouldShowSummaryExpand = computed(() => {
  if (!incident.value?.graphSummary) {
    return false
  }
  // Check if summary is long enough to need expansion
  // We'll use a simple heuristic: if the text is longer than ~200 characters, show expand button
  return incident.value.graphSummary.length > 200
})

const nodeLabelMap = computed(() => {
  const map = {}
  ;(eventGraphData.value.nodes || []).forEach((node) => {
    map[node.id] = node.labels?.[0] || node.properties?.entity_id || node.id
  })
  return map
})

const nodeTypeMap = computed(() => {
  const map = {}
  ;(eventGraphData.value.nodes || []).forEach((node) => {
    map[node.id] = (node.properties?.entity_type || 'entity').toLowerCase()
  })
  return map
})

const nodeDegreeMap = computed(() => {
  const map = {}
  ;(eventGraphData.value.edges || []).forEach((edge) => {
    if (edge.source) {
      map[edge.source] = (map[edge.source] || 0) + 1
    }
    if (edge.target) {
      map[edge.target] = (map[edge.target] || 0) + 1
    }
  })
  return map
})

const legendEntries = computed(() => {
  const seen = new Set()
  const entries = []
  displayGraphNodes.value.forEach((node) => {
    const type = (node.properties?.entity_type || 'entity').toLowerCase()
    if (seen.has(type)) {
      return
    }
    seen.add(type)
    entries.push({
      key: type,
      label: t(`incidents.detail.eventGraph.legendLabels.${type}`, type),
      color: ENTITY_COLOR_SOLID[type] || ENTITY_COLOR_SOLID.other
    })
  })
  return entries
})

const eventGraphStats = computed(() => {
  const nodes = eventGraphData.value.nodes || []
  const edges = eventGraphData.value.edges || []
  const ipNodes = nodes.filter((node) => node.properties?.entity_type === 'ip').length
  const alertNodes = nodes.filter((node) => node.properties?.entity_type === 'alert').length
  const tenantNodes = nodes.filter((node) => node.properties?.entity_type === 'tenant').length
  return {
    totalNodes: nodes.length,
    totalEdges: edges.length,
    ipNodes,
    alertNodes,
    tenantNodes
  }
})

const selectedNodeProperties = computed(() => {
  if (!selectedGraphNode.value) {
    return []
  }
  const properties = selectedGraphNode.value.properties || {}
  const preferredKeys = ['description', 'entity_type', 'entity_id', 'file_path', 'source_id', 'created_at']
  const orderedEntries = []
  preferredKeys.forEach((key) => {
    if (properties[key]) {
      orderedEntries.push([key, properties[key]])
    }
  })
  Object.entries(properties).forEach(([key, value]) => {
    if (!orderedEntries.find(([existingKey]) => existingKey === key)) {
      orderedEntries.push([key, value])
    }
  })
  return orderedEntries.slice(0, 6)
})

const selectedNodePropertyDescription = computed(() => {
  if (!selectedGraphNode.value) {
    return null
  }
  return selectedGraphNode.value.properties?.description || null
})

const shouldShowPropertyDescriptionExpand = computed(() => {
  if (!selectedNodePropertyDescription.value) {
    return false
  }
  // Show expand button if description is longer than ~150 characters
  return selectedNodePropertyDescription.value.length > 150
})

const selectedNodeRelations = computed(() => {
  if (!selectedGraphNode.value) {
    return []
  }
  const id = selectedGraphNode.value.id
  const related = displayGraphEdges.value.filter((edge) => edge.source === id || edge.target === id)
  return related.slice(0, 5).map((edge) => {
    const neighborId = edge.source === id ? edge.target : edge.source
    return {
      direction: edge.source === id ? 'outbound' : 'inbound',
      neighbor: neighborId,
      neighborLabel: nodeLabelMap.value[neighborId] || neighborId
    }
  })
})

const filteredNodeIds = computed(() => {
  const nodes = displayGraphNodes.value
  const query = graphSearchQuery.value.trim().toLowerCase()
  if (!query) {
    return new Set(nodes.map((node) => node.id))
  }
  return new Set(
    nodes
      .filter((node) => {
        const description = (node.properties?.description || '').toLowerCase()
        return (
          node.id.toLowerCase().includes(query) ||
          node.labels?.some((label) => label.toLowerCase().includes(query)) ||
          description.includes(query)
        )
      })
      .map((node) => node.id)
  )
})

const relatedNodeIds = computed(() => {
  const set = new Set()
  if (selectedGraphNodeId.value) {
    set.add(selectedGraphNodeId.value)
    displayGraphEdges.value.forEach((edge) => {
      if (edge.source === selectedGraphNodeId.value || edge.target === selectedGraphNodeId.value) {
        set.add(edge.source)
        set.add(edge.target)
      }
    })
  }
  return set
})

const handleNodeClick = (nodeId, { temporaryHighlight = false } = {}) => {
  console.log('handleNodeClick called with nodeId:', nodeId)
  if (!nodeId) {
    console.warn('handleNodeClick: nodeId is empty')
    return
  }
  
  // 检查节点是否存在
  const nodeExists = displayGraphNodes.value.some(n => n.id === nodeId)
  if (!nodeExists) {
    console.warn('handleNodeClick: node not found:', nodeId)
    return
  }
  
  if (selectedGraphNodeId.value === nodeId) {
    selectedGraphNodeId.value = ''
    highlightedEntity.value = ''
    console.log('Node deselected')
    return
  }
  selectedGraphNodeId.value = nodeId
  highlightedEntity.value = nodeId
  // Reset property description expansion when node changes
  isPropertyDescriptionExpanded.value = false
  console.log('Node selected:', nodeId, 'selectedGraphNode:', selectedGraphNode.value)
  
  // 更新图表以高亮选中的节点
  if (graphEchartsInstance.value) {
    updateEChartsGraph()
  }
  
  if (temporaryHighlight) {
    setTimeout(() => {
      if (selectedGraphNodeId.value === nodeId) {
        selectedGraphNodeId.value = ''
      }
      if (highlightedEntity.value === nodeId) {
        highlightedEntity.value = ''
      }
    }, 800)
  }
}



const formatNodeLabel = (node) => {
  const label = node.labels?.[0] || node.id || node.properties?.entity_type || 'entity'
  return label.length > 12 ? `${label.slice(0, 11)}…` : label
}

const formatNodeDetailValue = (value) => {
  if (value === null || value === undefined) {
    return ''
  }
  if (typeof value === 'string') {
    return value.replace(/<SEP>/gi, '\n')
  }
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value, null, 2)
    } catch (error) {
      return String(value)
    }
  }
  return String(value)
}



const buildNodeDetailCopyPayload = () => {
  if (!selectedGraphNode.value) {
    return ''
  }
  const node = selectedGraphNode.value
  const lines = []
  lines.push(`ID: ${formatNodeDetailValue(node.id) || '-'}`)
  if (node.labels?.length) {
    lines.push(`Labels: ${formatNodeDetailValue(node.labels.join(', '))}`)
  }
  if (node.properties?.entity_type) {
    lines.push(`Entity Type: ${formatNodeDetailValue(node.properties.entity_type)}`)
  }
  if (selectedNodeProperties.value.length) {
    lines.push('Properties:')
    selectedNodeProperties.value.forEach(([key, value]) => {
      lines.push(`  - ${key}: ${formatNodeDetailValue(value)}`)
    })
  }
  if (selectedNodeRelations.value.length) {
    lines.push('Relations:')
    selectedNodeRelations.value.forEach((relation) => {
      const indicator = relation.direction === 'outbound' ? '->' : '<-'
      lines.push(`  ${indicator} ${relation.neighborLabel || relation.neighbor}`)
    })
  }
  return lines.join('\n').trim()
}

const copySelectedNode = async () => {
  if (!selectedGraphNode.value) {
    toast.error(translateOr('incidents.detail.eventGraph.nodeDetail.copyUnavailable', 'Select a node to copy'), 'Error')
    return
  }
  const payload = buildNodeDetailCopyPayload()
  if (!payload) {
    toast.error(translateOr('incidents.detail.eventGraph.nodeDetail.copyUnavailable', 'Select a node to copy'), 'Error')
    return
  }
  let copied = false
  try {
    if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(payload)
      copied = true
    }
  } catch (error) {
    copied = false
  }

  if (!copied) {
    try {
      const textArea = document.createElement('textarea')
      textArea.value = payload
      textArea.style.position = 'fixed'
      textArea.style.opacity = '0'
      textArea.style.pointerEvents = 'none'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      copied = true
    } catch (fallbackError) {
      console.error('Failed to copy node detail', fallbackError)
    }
  }

  if (copied) {
    toast.success(translateOr('incidents.detail.eventGraph.nodeDetail.copySuccess', 'Node detail copied'), 'Success')
  } else {
    toast.error(translateOr('incidents.detail.eventGraph.nodeDetail.copyError', 'Unable to copy node detail'), 'Error')
  }
}

const pruneSelectedNode = () => {
  if (!selectedGraphNodeId.value) {
    return
  }
  const next = new Set(prunedNodeIds.value)
  next.add(selectedGraphNodeId.value)
  prunedNodeIds.value = next
  selectedGraphNodeId.value = ''
  highlightedEntity.value = ''
}

const clearSelectedNode = () => {
  selectedGraphNodeId.value = ''
  highlightedEntity.value = ''
}

const handleGraphContainerClick = (event) => {
  // 检查点击的目标
  const target = event.target
  // 如果点击的是 canvas 元素，说明可能是点击了背景
  // 延迟检查，确保 ECharts 的 click 事件先处理
  setTimeout(() => {
    // 如果此时还有选中状态，且点击的是 canvas（不是节点），则清除选中
    if (selectedGraphNodeId.value && target && target.tagName === 'CANVAS') {
      console.log('Graph container background clicked, clearing selection')
      clearSelectedNode()
      if (graphEchartsInstance.value) {
        updateEChartsGraph()
      }
    }
  }, 150)
}


const handleGraphBackgroundClick = (event) => {
  if (resizingNodeDetail.value) {
    return
  }
  // 检查点击的目标是否是 ECharts 容器内的节点
  // 如果是节点点击，不应该清除选中状态
  const target = event.target
  if (target && graphEchartsRef.value && graphEchartsRef.value.contains(target)) {
    // 检查是否是 ECharts 的节点元素
    // ECharts 的节点通常有特定的类名或属性
    const isEChartsNode = target.closest && (
      target.closest('[class*="echarts"]') || 
      target.closest('canvas')
    )
    if (isEChartsNode) {
      // 检查是否点击的是节点本身（通过检查事件参数）
      // 如果点击的是节点，ECharts 会触发节点点击事件，这里不应该清除
      // 只有当点击的是空白背景时才清除选中状态
      // 由于 ECharts 的节点点击事件已经处理，这里只需要处理背景点击
      // 延迟执行，让节点点击事件先处理
      setTimeout(() => {
        // 如果点击的不是节点，清除选中状态
        clearSelectedNode()
        if (graphEchartsInstance.value) {
          updateEChartsGraph()
        }
      }, 100)
      return
    }
  }
  // 点击空白处，清除选中状态
  clearSelectedNode()
  if (graphEchartsInstance.value) {
    updateEChartsGraph()
  }
}

const handleLegendClick = (key) => {
  if (!key) {
    return
  }
  legendFlashKey.value = key
  if (legendFlashTimer.value) {
    clearTimeout(legendFlashTimer.value)
  }
  legendFlashTimer.value = setTimeout(() => {
    legendFlashKey.value = ''
    legendFlashTimer.value = null
  }, 800)
}

const handleRelationClick = (neighborId) => {
  if (!neighborId) {
    return
  }
  handleNodeClick(neighborId)
}


const handleGraphZoomIn = () => {
  if (!graphEchartsInstance.value) return
  // 通过修改 roam 的 scale 来实现缩放
  graphEchartsInstance.value.dispatchAction({
    type: 'graphRoam',
    zoom: 1.2
  })
}

const handleGraphZoomOut = () => {
  if (!graphEchartsInstance.value) return
  graphEchartsInstance.value.dispatchAction({
    type: 'graphRoam',
    zoom: 0.8
  })
}

const handleGraphResetView = () => {
  selectedGraphNodeId.value = ''
  highlightedEntity.value = ''
  graphSearchQuery.value = ''
  if (graphEchartsInstance.value && hasGraphData.value) {
    // 重新初始化图表来重置视图
    updateEChartsGraph()
  }
}

const fullscreenEventNames = ['fullscreenchange', 'webkitfullscreenchange', 'mozfullscreenchange', 'MSFullscreenChange']

const syncGraphFullscreenState = () => {
  if (typeof document === 'undefined') {
    return
  }
  const fullscreenElement =
    document.fullscreenElement ||
    document.webkitFullscreenElement ||
    document.mozFullScreenElement ||
    document.msFullscreenElement
  isGraphFullscreen.value = fullscreenElement === graphContainerRef.value
}

const toggleGraphFullscreen = () => {
  const container = graphContainerRef.value
  if (!container || typeof document === 'undefined') {
    return
  }
  try {
    if (!isGraphFullscreen.value) {
      const request =
        container.requestFullscreen ||
        container.webkitRequestFullscreen ||
        container.mozRequestFullScreen ||
        container.msRequestFullscreen
      request?.call(container)
    } else {
      const exit =
        document.exitFullscreen ||
        document.webkitExitFullscreen ||
        document.mozCancelFullScreen ||
        document.msExitFullscreen
      exit?.call(document)
    }
  } catch (error) {
    console.error('Failed to toggle fullscreen', error)
  }
}

const handleGraphDownload = () => {
  if (!graphEchartsInstance.value || typeof document === 'undefined') {
    return
  }
  try {
    const url = graphEchartsInstance.value.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#0f172a'
    })
    const link = document.createElement('a')
    link.href = url
    const incidentId = incident.value?.id || incident.value?.eventId || 'incident'
    link.download = `incident-graph-${incidentId}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Failed to download graph', error)
  }
}


const startNodeDetailResize = (event) => {
  if (event.button !== 0) {
    return
  }
  event.preventDefault()
  resizingNodeDetail.value = true
  resizeStartX.value = event.clientX
  initialNodeDetailWidth.value = nodeDetailWidth.value
  window.addEventListener('pointermove', handleNodeDetailResize)
  window.addEventListener('pointerup', stopNodeDetailResize)
}

const handleNodeDetailResize = (event) => {
  if (!resizingNodeDetail.value) {
    return
  }
  const delta = resizeStartX.value - event.clientX
  nodeDetailWidth.value = Math.min(520, Math.max(260, initialNodeDetailWidth.value + delta))
}

const stopNodeDetailResize = () => {
  if (!resizingNodeDetail.value) {
    return
  }
  resizingNodeDetail.value = false
  window.removeEventListener('pointermove', handleNodeDetailResize)
  window.removeEventListener('pointerup', stopNodeDetailResize)
}

const nodeDetailPaneStyle = computed(() => ({
  width: '100%',
  maxWidth: `${Math.round(nodeDetailWidth.value)}px`
}))

onBeforeUnmount(() => {
  window.removeEventListener('pointermove', handlePointerMove)
  window.removeEventListener('pointerup', handlePointerUp)
  window.removeEventListener('pointermove', handleNodeDetailResize)
  window.removeEventListener('pointerup', stopNodeDetailResize)
  if (graphResizeHandler.value) {
    window.removeEventListener('resize', graphResizeHandler.value)
    graphResizeHandler.value = null
  }
  if (legendFlashTimer.value) {
    clearTimeout(legendFlashTimer.value)
  }
  if (dragTimeout.value) {
    clearTimeout(dragTimeout.value)
    dragTimeout.value = null
  }
  if (typeof document !== 'undefined') {
    fullscreenEventNames.forEach((eventName) => document.removeEventListener(eventName, syncGraphFullscreenState))
  }
  if (graphEchartsInstance.value) {
    graphEchartsInstance.value.dispose()
    graphEchartsInstance.value = null
  }
})

watch(
  [baseGraphNodes, displayGraphEdges, graphSearchQuery, selectedGraphNodeId],
  () => {
    if (graphEchartsInstance.value && hasGraphData.value && displayGraphNodes.value.length > 0) {
      updateEChartsGraph()
    }
  },
  { deep: true }
)

// 监听 hasGraphData 变化，当数据加载后初始化图表
watch(
  hasGraphData,
  (hasData) => {
    if (hasData && graphEchartsRef.value && !graphEchartsInstance.value && activeTab.value === 'eventGraph') {
      nextTick(() => {
        initEChartsGraph()
      })
    }
  },
  { immediate: true }
)

// 监听 activeTab 变化，切换到图表标签页时初始化
watch(
  activeTab,
  (newTab) => {
    if (newTab === 'eventGraph' && hasGraphData.value) {
      // 使用多次重试，确保 DOM 已渲染
      let retries = 0
      const maxRetries = 10
      const tryInit = () => {
        if (graphEchartsRef.value) {
          if (!graphEchartsInstance.value) {
            console.log('Initializing ECharts graph after tab switch...')
            initEChartsGraph()
          } else {
            // 如果图表已存在，确保它正确显示
            nextTick(() => {
              if (graphEchartsInstance.value) {
                graphEchartsInstance.value.resize()
              }
            })
          }
        } else if (retries < maxRetries) {
          retries++
          setTimeout(tryInit, 100)
        } else {
          console.warn('Cannot initialize graph after tab switch:', {
            hasRef: !!graphEchartsRef.value,
            hasData: hasGraphData.value
          })
        }
      }
      nextTick(() => {
        tryInit()
      })
    }
  }
)

watch(
  displayGraphNodes,
  (nodes) => {
    if (
      legendFlashKey.value &&
      !nodes.some((node) => (node.properties?.entity_type || 'entity').toLowerCase() === legendFlashKey.value)
    ) {
      legendFlashKey.value = ''
    }
    if (graphEchartsInstance.value && hasGraphData.value) {
      updateEChartsGraph()
    }
  },
  { immediate: true }
)

watch(highlightedEntity, (value) => {
  if (!value) {
    return
  }
  if (displayGraphNodes.value.some((node) => node.id === value)) {
    selectedGraphNodeId.value = value
  }
})

watch(graphSearchQuery, () => {
  if (
    selectedGraphNodeId.value &&
    !filteredNodeIds.value.has(selectedGraphNodeId.value) &&
    graphSearchQuery.value
  ) {
    selectedGraphNodeId.value = ''
  }
})

const tabs = [
  { key: 'overview', label: 'incidents.detail.tabs.overview' },
  { key: 'eventGraph', label: 'incidents.detail.tabs.eventGraph' },
  { key: 'comments', label: 'incidents.detail.tabs.comments' }
]

// 关联告警表格列配置
const associatedAlertsColumns = computed(() => [
  { key: 'createTime', label: t('alerts.list.createTime') },
  { key: 'alertTitle', label: t('alerts.list.alertTitle') },
  { key: 'riskLevel', label: t('alerts.list.riskLevel') },
  { key: 'status', label: t('alerts.list.status') },
  { key: 'owner', label: t('alerts.list.owner') }
])

// 关联告警表格默认列宽
const associatedAlertsDefaultWidths = {
  createTime: 180,
  alertTitle: 400,
  riskLevel: 120,
  status: 120,
  owner: 50
}

// 格式化关联告警数据，将事件详情的数据格式转换为告警管理页面的格式
const formattedAssociatedAlerts = computed(() => {
  if (!incident.value?.associatedAlerts) {
    return []
  }
  return incident.value.associatedAlerts.map(alert => {
    // 转换 severity 为 riskLevel (需要转换为小写)
    const severityMap = {
      'Critical': 'fatal',
      'High': 'high',
      'Medium': 'medium',
      'Low': 'low',
      'Tips': 'tips'
    }
    const riskLevel = alert.severity 
      ? (severityMap[alert.severity] || alert.severity.toLowerCase())
      : 'low'
    
    // 转换 handle_status 为 status (需要转换为小写)
    const statusMap = {
      'Open': 'open',
      'Block': 'block',
      'Closed': 'closed'
    }
    const status = alert.handle_status
      ? (statusMap[alert.handle_status] || alert.handle_status.toLowerCase())
      : 'open'
    
    return {
      id: alert.id,
      createTime: alert.create_time || alert.createTime || '-',
      title: alert.title || '-',
      riskLevel: riskLevel,
      status: status,
      owner: alert.owner || '-'
    }
  })
})

const loadIncidentDetail = async ({ silent = false } = {}) => {
  if (!silent) {
    loadingIncident.value = true
  }
  try {
    const incidentId = route.params.id
    const response = await getIncidentDetail(incidentId)
    const data = response.data
    const graphPayload = parseGraphData(data.graph_data)
    
    // 格式化数据，将后端字段映射到前端使用的字段
    incident.value = {
      id: data.id,
      eventId: data.id,
      name: data.title,
      title: data.title,
      createTime: data.create_time,
      updateTime: data.update_time,
      closeTime: data.close_time,
      status: data.handle_status,
      severity: data.severity,
      owner: data.owner,
      actor: data.actor,
      responsiblePerson: data.responsible_person || data.owner,
      responsibleDept: data.responsible_dept || '',
      creator: data.creator,
      labels: data.labels,
      closeReason: data.close_reason,
      closeComment: data.close_comment,
      isAutoClosed: data.is_auto_closed,
      ttd: data.ttd,
      arriveTime: data.arrive_time,
      description: data.description || data.title, // 如果没有description，使用title
      extendProperties: data.extend_properties,
      dataSourceProductName: data.data_source_product_name,
      // 格式化评论数据
      comments: formatComments(data.comments || []),
      // 从评论生成时间线
      timeline: generateTimeline(data),
      // 关联告警（如果有）
      associatedAlerts: data.associated_alerts || data.associatedAlerts || [],
      graphData: graphPayload,
      graphSummary: data.graph_summary || '',
      graphStatus: data.graph_status || (graphPayload.nodes.length ? 'ready' : 'missing')
    }
    loadGraphData(graphPayload)
  } catch (error) {
    console.error('Failed to load incident detail:', error)
    router.push('/incidents')
  } finally {
    if (!silent) {
      loadingIncident.value = false
    }
  }
}

/**
 * @brief 格式化评论数据
 */
const formatComments = (comments) => {
  if (!comments || !Array.isArray(comments)) {
    return []
  }
  
  return comments.map((comment, index) => {
    const author = comment.author || 'Unknown'
    const authorWords = author.trim().split(/\s+/)
    const authorInitials = authorWords.length > 1
      ? authorWords.slice(0, 3).map(word => word.charAt(0).toUpperCase()).join('')
      : author.charAt(0).toUpperCase()
    
    // 根据作者名称生成头像颜色
    let hash = 0
    for (let i = 0; i < author.length; i++) {
      hash = author.charCodeAt(i) + ((hash << 5) - hash)
    }
    const colors = ['bg-teal-500', 'bg-blue-500', 'bg-purple-500', 'bg-green-500', 'bg-orange-500']
    const avatarColor = colors[Math.abs(hash % colors.length)]
    
    return {
      id: comment.id || index,
      author: author,
      authorInitials: authorInitials,
      avatarColor: avatarColor,
      time: formatDateTime(comment.create_time),
      content: comment.content,
      create_time: comment.create_time,
      file: comment.file || null  // 保留文件信息
    }
  })
}

/**
 * @brief 从事件数据生成时间线
 */
const generateTimeline = (data) => {
  const timeline = []
  
  // 添加创建事件
  if (data.create_time) {
    timeline.push({
      time: formatDateTime(data.create_time),
      rawTime: data.create_time,
      title: t('incidents.detail.eventGraph.incidentCreated'),
      description: t('incidents.detail.eventGraph.incidentCreatedDesc'),
      icon: 'event',
      severity: data.severity?.toLowerCase() || 'low'
    })
  }
  
  // 从评论中提取重要事件
  if (data.comments && Array.isArray(data.comments)) {
    data.comments.forEach(comment => {
      const content = comment.content || ''
      
      // 检查是否是重要事件
      if (content.includes('transfer alert to incident')) {
        timeline.push({
          time: formatDateTime(comment.create_time),
          rawTime: comment.create_time,
          title: t('incidents.detail.eventGraph.alertConverted'),
          description: content,
          icon: 'transform',
          severity: 'medium'
        })
      } else if (content.includes('change severity')) {
        const severityMatch = content.match(/severity:(\w+)/i)
        timeline.push({
          time: formatDateTime(comment.create_time),
          rawTime: comment.create_time,
          title: t('incidents.detail.eventGraph.severityChanged'),
          description: content,
          icon: 'priority',
          severity: severityMatch ? severityMatch[1].toLowerCase() : 'low'
        })
      } else if (content.includes('change owner')) {
        timeline.push({
          time: formatDateTime(comment.create_time),
          rawTime: comment.create_time,
          title: t('incidents.detail.eventGraph.ownerChanged'),
          description: content,
          icon: 'person',
          severity: 'low'
        })
      } else if (content.includes('Resolved') || content.includes('Closed')) {
        timeline.push({
          time: formatDateTime(comment.create_time),
          rawTime: comment.create_time,
          title: t('incidents.detail.eventGraph.incidentClosed'),
          description: content,
          icon: 'archive',
          severity: 'low'
        })
      }
    })
  }
  
  // 添加关闭事件
  if (data.close_time) {
    timeline.push({
      time: formatDateTime(data.close_time),
      rawTime: data.close_time,
      title: t('incidents.detail.eventGraph.incidentClosed'),
      description: data.close_comment || t('incidents.detail.eventGraph.incidentClosedDesc'),
      icon: 'check_circle',
      severity: 'low'
    })
  }
  
  // 按时间排序（从旧到新），使用原始时间字段
  return timeline.sort((a, b) => {
    const timeA = a.rawTime ? new Date(a.rawTime) : new Date(a.time)
    const timeB = b.rawTime ? new Date(b.rawTime) : new Date(b.time)
    return timeA - timeB
  })
}

const openAlertDetail = (alertId) => {
  selectedAlertId.value = alertId
}

const openAlertDetailInNewWindow = (alertId) => {
  // 在新窗口打开告警详情
  const route = router.resolve({ path: `/alerts/${alertId}` })
  // 构建完整的 URL
  const url = window.location.origin + route.href
  window.open(url, '_blank')
}

const closeAlertDetail = () => {
  selectedAlertId.value = null
}

const handlePostComment = async ({ comment, files }) => {
  if (!incident.value?.id) {
    toast.error(t('incidents.detail.comments.postError') || '无法提交评论：事件ID不存在', '操作失败')
    return
  }
  
  try {
    const commentText = comment.trim()
    // 允许只有文件没有文本的情况
    if (!commentText && (!files || files.length === 0)) {
      return
    }
    
    // 调用 API 提交评论（包含文件）
    await postComment(incident.value.id, commentText, files || [])
    
    // 清空输入框（组件会自动清空）
    newComment.value = ''
    
    // 重新加载事件详情以获取最新评论
    await loadIncidentDetail()
    
    // 显示成功提示
    toast.success(t('incidents.detail.comments.postSuccess') || '评论提交成功', '操作成功')
  } catch (error) {
    console.error('Failed to post comment:', error)
    const errorMessage = error?.response?.data?.message || error?.message || t('incidents.detail.comments.postError') || '评论提交失败，请稍后重试'
    toast.error(errorMessage, '操作失败')
  }
}

const sanitizeHtml = (html) => {
  if (!html || typeof html !== 'string') return ''
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['br', 'strong', 'em', 'pre', 'code', 'b', 'i', 'u', 'p'],
    ALLOWED_ATTR: []
  })
}

// Note: File handling functions (getFileIcon, formatFileSize, openImageModal, downloadFile) 
// have been moved to CommentSection component

const formatLastModified = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) {
    return t('incidents.detail.overview.justNow')
  } else if (diffMins < 60) {
    return `${diffMins} ${t('incidents.detail.overview.minutesAgo')}`
  } else if (diffHours < 24) {
    return `${diffHours} ${t('incidents.detail.overview.hoursAgo')}`
  } else if (diffDays < 7) {
    return `${diffDays} ${t('incidents.detail.overview.daysAgo')}`
  } else {
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
}

const getAlertSeverityDotClass = (severity) => {
  const classes = {
    critical: 'bg-red-500',
    high: 'bg-amber-400',
    medium: 'bg-yellow-400',
    low: 'bg-blue-500'
  }
  return classes[severity] || classes.medium
}

const getAlertSeverityTextClass = (severity) => {
  const classes = {
    critical: 'text-red-400',
    high: 'text-amber-400',
    medium: 'text-yellow-400',
    low: 'text-blue-400'
  }
  return classes[severity] || classes.medium
}

const getAlertSeverityLabel = (severity) => {
  const labels = {
    critical: 'Critical',
    high: 'High',
    medium: 'Medium',
    low: 'Low'
  }
  return labels[severity] || severity
}

// 复用告警管理页面的样式函数
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

// 事件状态的样式函数（保留用于事件详情页面的其他部分）
const getIncidentStatusDotClass = (status) => {
  const statusLower = (status || '').toLowerCase()
  const classes = {
    open: 'bg-amber-400',
    block: 'bg-yellow-400',
    closed: 'bg-gray-400'
  }
  return classes[statusLower] || classes.open
}

/**
 * @brief 获取状态文本
 */
const getStatusText = (status) => {
  if (!status) return t('incidents.list.open')
  const statusLower = status.toLowerCase()
  const statusMap = {
    'open': t('incidents.list.open'),
    'block': t('incidents.list.block'),
    'closed': t('incidents.list.closed')
  }
  return statusMap[statusLower] || status
}

const getSeverityDotClass = (severity) => {
  const classes = {
    high: 'bg-red-500',
    medium: 'bg-orange-500',
    low: 'bg-blue-500'
  }
  return classes[severity] || classes.low
}

const getSeverityTextClass = (severity) => {
  const classes = {
    high: 'text-red-400',
    medium: 'text-orange-400',
    low: 'text-blue-400'
  }
  return classes[severity] || classes.low
}

const getTimelineIconBgClass = (severity) => {
  const classes = {
    high: 'bg-red-500/20 ring-1 ring-inset ring-red-500/30',
    medium: 'bg-amber-500/20 ring-1 ring-inset ring-amber-500/30',
    low: 'bg-slate-700'
  }
  return classes[severity] || classes.low
}

const getTimelineIconColorClass = (severity) => {
  const classes = {
    high: 'text-red-400',
    medium: 'text-amber-400',
    low: 'text-slate-300'
  }
  return classes[severity] || classes.low
}

/**
 * @brief 生成事件详情URL
 * @return {string} 事件的完整URL
 */
const getIncidentUrl = () => {
  const raw = import.meta.env.VITE_WEB_BASE_PATH
  let basePath = '/'
  if (raw && raw !== '/') {
    basePath = raw.startsWith('/') ? raw : `/${raw}`
    // Remove trailing slash if present
    basePath = basePath.replace(/\/$/, '')
  }
  const origin = window.location.origin
  const incidentId = route.params.id
  const path = basePath === '/' ? '/incidents' : `${basePath}/incidents`
  return `${origin}${path}/${incidentId}`
}

/**
 * @brief 分享事件（复制标题和链接到剪切板）
 */
const handleShare = async () => {
  if (!incident.value) return
  
  const title = incident.value.name || ''
  const url = getIncidentUrl()
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

/**
 * @brief 刷新事件详情
 */
const handleRefresh = async () => {
  await loadIncidentDetail()
}

const handleRefreshGraphStatus = async () => {
  if (isRefreshingGraph.value) {
    return
  }
  try {
    isRefreshingGraph.value = true
    await loadIncidentDetail({ silent: true })
  } catch (error) {
    console.error('Failed to refresh graph status:', error)
    const errorMessage =
      error?.response?.data?.message ||
      error?.message ||
      t('incidents.detail.eventGraph.refreshError') ||
      'Failed to refresh graph status'
    toast.error(errorMessage, 'Error')
  } finally {
    isRefreshingGraph.value = false
  }
}

const handleRegenerateGraph = async () => {
  if (isRegeneratingGraph.value) {
    return
  }
  try {
    isRegeneratingGraph.value = true
    await regenerateIncidentGraph(route.params.id)
    if (incident.value) {
      incident.value.graphStatus = 'processing'
      incident.value.graphSummary = ''
    }
    loadGraphData(createEmptyGraphData())
    toast.success(t('incidents.detail.eventGraph.regenerateSuccess') || 'Graph regeneration started', 'Success')
    await loadIncidentDetail({ silent: true })
  } catch (error) {
    console.error('Failed to regenerate graph:', error)
    const errorMessage =
      error?.response?.data?.error_message ||
      error?.response?.data?.message ||
      error?.message ||
      t('incidents.detail.eventGraph.regenerateError') ||
      'Failed to regenerate graph'
    toast.error(errorMessage, 'Error')
  } finally {
    isRegeneratingGraph.value = false
  }
}

const openCloseDialog = () => {
  showCloseDialog.value = true
}

const closeCloseDialog = () => {
  showCloseDialog.value = false
}

const handleCloseIncident = async (data) => {
  if (isClosingIncident.value) {
    return
  }

  try {
    isClosingIncident.value = true
    if (closeDialogRef.value) {
      closeDialogRef.value.setSubmitting(true)
    }
    
    // 构建请求体
    const body = {
      handle_status: 'Closed',
      close_reason: data.close_reason,
      close_comment: data.close_comment
    }

    // 调用 PUT /api/incidents/<incident_id> 接口
    const apiBaseURL = import.meta.env.VITE_API_BASE_URL || ''
    const url = apiBaseURL ? `${apiBaseURL}/incidents/${route.params.id}` : `/api/incidents/${route.params.id}`
    
    const headers = {
      'Content-Type': 'application/json'
    }
    if (authStore.token) {
      headers['Authorization'] = `Bearer ${authStore.token}`
    }
    
    await axios.put(url, body, { headers })
    
    // 显示成功提示
    toast.success(t('incidents.detail.closeSuccess') || '事件关闭成功', '操作成功')
    
    // 关闭对话框
    closeCloseDialog()
    
    // 重新加载事件详情
    await loadIncidentDetail()
  } catch (error) {
    console.error('Failed to close incident:', error)
    // 显示错误提示
    const errorMessage = error?.response?.data?.message || error?.message || t('incidents.detail.closeError') || '事件关闭失败，请稍后重试'
    toast.error(errorMessage, '操作失败')
  } finally {
    isClosingIncident.value = false
    if (closeDialogRef.value) {
      closeDialogRef.value.setSubmitting(false)
    }
  }
}

const openEditDialog = () => {
  if (!incident.value) {
    console.warn('Incident data not loaded')
    return
  }
  
  editIncidentInitialData.value = {
    title: incident.value.name || incident.value.title || '',
    category: incident.value.category || 'platform',
    status: incident.value.status || 'Open',
    occurrenceTime: incident.value.occurrenceTime 
      ? (incident.value.occurrenceTime instanceof Date 
          ? incident.value.occurrenceTime 
          : new Date(incident.value.occurrenceTime))
      : new Date(),
    responsiblePerson: incident.value.responsiblePerson || '',
    responsibleDepartment: incident.value.responsibleDept || '',
    actor: incident.value.actor || '',
    rootCause: incident.value.rootCause || '',
    severity: incident.value.severity || '',
    description: incident.value.description || ''
  }
  

  nextTick(() => {
    showEditDialog.value = true
  })
}

const closeEditDialog = () => {
  showEditDialog.value = false
  editIncidentInitialData.value = null
}

const handleIncidentUpdated = async () => {
  // 事件更新成功后，关闭对话框并重新加载详情
  closeEditDialog()
  await loadIncidentDetail()
}

onMounted(() => {
  loadIncidentDetail()
  if (typeof document !== 'undefined') {
    fullscreenEventNames.forEach((eventName) => document.addEventListener(eventName, syncGraphFullscreenState))
    syncGraphFullscreenState()
  }
  nextTick(() => {
    if (hasGraphData.value) {
      initEChartsGraph()
    }
  })
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 确保事件描述中的长链接能够自动换行，不会撑大页面 */
.event-description-text {
  word-break: break-all;
  overflow-wrap: anywhere;
  max-width: 100%;
}

.graph-control-btn {
  padding: 0.35rem;
  border-radius: 0.375rem;
  color: #cbd5f5;
  transition: background-color 0.2s ease, color 0.2s ease;
  min-height: 2.5rem;
  min-width: 2.5rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.graph-control-btn:hover {
  color: #fff;
  background-color: rgba(71, 85, 105, 0.6);
}

.graph-control-btn:disabled {
  opacity: 0.4;
  pointer-events: none;
}

.event-graph-svg .graph-edge {
  stroke: #64748b;
  stroke-opacity: 0.25;
  stroke-width: 1.4;
  transition: stroke 0.2s ease, stroke-width 0.2s ease, opacity 0.2s ease;
}

.event-graph-svg .graph-edge:hover {
  stroke-opacity: 0.9;
  stroke-width: 2.8;
}

.event-graph-svg .graph-edge--active {
  stroke: #38bdf8;
  stroke-opacity: 0.85;
  stroke-width: 2.6;
}

.event-graph-svg .graph-edge--related {
  stroke-opacity: 0.6;
}

.event-graph-svg .graph-edge--dimmed {
  opacity: 0.2;
}

.event-graph-svg .graph-node circle {
  stroke: rgba(148, 163, 184, 0.4);
  stroke-width: 1.5;
  transition: transform 0.2s ease, stroke 0.2s ease, fill-opacity 0.2s ease, opacity 0.2s ease;
}

.graph-node__label {
  fill: rgba(255, 255, 255, 0.85);
  font-size: 10px;
  pointer-events: none;
  text-transform: none;
}

.graph-node--active circle {
  stroke: #60a5fa;
  stroke-width: 2.4;
}

.graph-node--related circle {
  stroke: #fbbf24;
  stroke-width: 2;
}

.graph-node--dimmed {
  opacity: 0.35;
}

.graph-node:not(.graph-node--dimmed) circle:hover {
  transform: scale(1.08);
}

.neighbor-link {
  color: #60a5fa;
  font-weight: 600;
  text-decoration: underline;
  display: inline-block;
  padding: 0.1rem 0;
}

.neighbor-link:hover {
  color: #93c5fd;
}

.legend-entry {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.65rem;
  transition: color 0.2s ease;
}

.legend-entry__dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 9999px;
  display: inline-flex;
}

.legend-entry--active {
  color: #ffffff;
}

.legend-entry:hover {
  color: #e2e8f0;
}

.legend-entry__label {
  pointer-events: none;
}

.node-detail-resize-handle {
  width: 6px;
  cursor: col-resize;
  background: linear-gradient(to bottom, rgba(148, 163, 184, 0.2), rgba(148, 163, 184, 0.05));
  position: relative;
}

.node-detail-resize-handle::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 2px;
  height: 60px;
  background-color: rgba(148, 163, 184, 0.35);
  transform: translate(-50%, -50%);
}

.detail-action-btn {
  color: #94a3b8;
  padding: 0.4rem;
  border-radius: 0.35rem;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.detail-action-btn:hover:not(:disabled) {
  color: #fff;
  background-color: rgba(71, 85, 105, 0.6);
}

.detail-action-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.graph-status-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.9rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: background-color 0.2s ease, color 0.2s ease, opacity 0.2s ease;
}

.graph-status-btn:disabled {
  opacity: 0.9;
  cursor: not-allowed;
}

.graph-icon-btn {
  position: relative;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(148, 163, 184, 0.18);
  color: #e2e8f0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.25s ease, color 0.25s ease, border-color 0.25s ease, opacity 0.25s ease;
}

.graph-icon-btn:hover:not(:disabled) {
  border-color: rgba(148, 163, 184, 0.65);
  background: rgba(148, 163, 184, 0.32);
}

.graph-icon-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.graph-icon-btn--loading {
  animation: pulse 1.1s ease-in-out infinite;
}

.graph-regenerate-fab {
  position: absolute;
  right: 1.25rem;
  bottom: 1.25rem;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.55rem 1rem;
  border-radius: 9999px;
  border: 1px solid rgba(248, 113, 113, 0.6);
  background: rgba(248, 113, 113, 0.15);
  color: #fecaca;
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: background-color 0.25s ease, border-color 0.25s ease, color 0.25s ease, opacity 0.25s ease;
}

.graph-regenerate-fab:hover:not(:disabled) {
  border-color: rgba(248, 113, 113, 0.85);
  background: rgba(248, 113, 113, 0.3);
  color: #fee2e2;
}

.graph-regenerate-fab:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.graph-regenerate-fab--loading {
  animation: pulse 1.1s ease-in-out infinite;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.prose :deep(p) {
  margin-bottom: 0.5rem;
}

.prose :deep(ul) {
  list-style: disc;
  margin-left: 1.25rem;
}

@keyframes pulse {
  0% {
    opacity: 0.55;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.55;
  }
}
.graph-icon-btn {
  position: relative;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(148, 163, 184, 0.18);
  color: #e2e8f0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.25s ease, color 0.25s ease, border-color 0.25s ease, opacity 0.25s ease;
}

.graph-icon-btn:hover:not(:disabled) {
  border-color: rgba(148, 163, 184, 0.65);
  background: rgba(148, 163, 184, 0.32);
}

.graph-icon-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.graph-icon-btn--loading {
  animation: pulse 1.1s ease-in-out infinite;
}

.graph-icon-btn--regenerate {
  border-color: rgba(248, 113, 113, 0.6);
  background: rgba(248, 113, 113, 0.15);
  color: #fecaca;
}

.graph-icon-btn--regenerate:hover:not(:disabled) {
  border-color: rgba(248, 113, 113, 0.9);
  background: rgba(248, 113, 113, 0.3);
  color: #fee2e2;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.prose :deep(p) {
  margin-bottom: 0.5rem;
}

.prose :deep(ul) {
  list-style: disc;
  margin-left: 1.25rem;
}

@keyframes pulse {
  0% {
    opacity: 0.55;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.55;
  }
}
.prose :deep(p) {
  margin-bottom: 0.5rem;
}

.prose :deep(ul) {
  list-style: disc;
  margin-left: 1.25rem;
}

.summary-collapsed {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.property-description-collapsed {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.graph-regenerate-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.55rem 1rem;
  border-radius: 9999px;
  border: 1px solid rgba(248, 113, 113, 0.6);
  background: rgba(248, 113, 113, 0.15);
  color: #fecaca;
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: background-color 0.25s ease, border-color 0.25s ease, color 0.25s ease, opacity 0.25s ease;
}

.graph-regenerate-btn:hover:not(:disabled) {
  border-color: rgba(248, 113, 113, 0.85);
  background: rgba(248, 113, 113, 0.3);
  color: #fee2e2;
}

.graph-regenerate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.graph-regenerate-btn--loading {
  animation: pulse 1.1s ease-in-out infinite;
}
</style>

