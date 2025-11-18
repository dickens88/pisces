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
            <span>{{ $t('incidents.detail.owner') }}:</span>
            <span class="text-white">{{ incident?.owner }}</span>
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
        <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-6 space-y-3">
          <h3 class="text-white font-bold text-lg">
            {{ $t('incidents.detail.eventGraph.summaryTitle') }}
          </h3>
          <p class="text-slate-300 leading-relaxed">
            {{ $t('incidents.detail.eventGraph.summaryParagraph1') }}
          </p>
          <p class="text-slate-300 leading-relaxed">
            {{
              $t('incidents.detail.eventGraph.summaryParagraph2', {
                nodes: eventGraphStats.totalNodes,
                edges: eventGraphStats.totalEdges,
                alerts: eventGraphStats.alertNodes,
                ips: eventGraphStats.ipNodes
              })
            }}
          </p>
        </div>
        <div class="bg-slate-900/60 border border-slate-700 rounded-2xl overflow-hidden">
          <div class="flex flex-col lg:flex-row min-h-[640px]">
            <div class="flex-1 relative bg-[#0f172a]">
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
                    <button type="button" class="graph-control-btn" :title="$t('incidents.detail.eventGraph.controls.zoomIn')">
                      <span class="material-symbols-outlined text-base">zoom_in</span>
                    </button>
                    <button type="button" class="graph-control-btn" :title="$t('incidents.detail.eventGraph.controls.zoomOut')">
                      <span class="material-symbols-outlined text-base">zoom_out</span>
                    </button>
                    <button type="button" class="graph-control-btn" :title="$t('incidents.detail.eventGraph.controls.reset')">
                      <span class="material-symbols-outlined text-base">center_focus_strong</span>
                    </button>
                    <button type="button" class="graph-control-btn" :title="$t('incidents.detail.eventGraph.controls.fullscreen')">
                      <span class="material-symbols-outlined text-base">fullscreen</span>
                    </button>
                    <button type="button" class="graph-control-btn" :title="$t('incidents.detail.eventGraph.controls.download')">
                      <span class="material-symbols-outlined text-base">download</span>
                    </button>
                    <button type="button" class="graph-control-btn" :title="$t('incidents.detail.eventGraph.controls.refresh')">
                      <span class="material-symbols-outlined text-base">refresh</span>
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
              <div class="w-full h-full" @click="handleGraphBackgroundClick">
                <svg ref="graphSvgRef" class="w-full h-full event-graph-svg" viewBox="0 0 1000 640">
                  <defs>
                    <radialGradient id="grad-rose">
                      <stop offset="0%" stop-color="#fda4af" stop-opacity="0.45" />
                      <stop offset="100%" stop-color="#f43f5e" stop-opacity="0.12" />
                    </radialGradient>
                    <radialGradient id="grad-cyan">
                      <stop offset="0%" stop-color="#67e8f9" stop-opacity="0.45" />
                      <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.12" />
                    </radialGradient>
                    <radialGradient id="grad-emerald">
                      <stop offset="0%" stop-color="#6ee7b7" stop-opacity="0.45" />
                      <stop offset="100%" stop-color="#10b981" stop-opacity="0.12" />
                    </radialGradient>
                    <radialGradient id="grad-amber">
                      <stop offset="0%" stop-color="#fcd34d" stop-opacity="0.45" />
                      <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.12" />
                    </radialGradient>
                    <radialGradient id="grad-violet">
                      <stop offset="0%" stop-color="#c4b5fd" stop-opacity="0.45" />
                      <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.12" />
                    </radialGradient>
                  </defs>
                  <g>
                    <path
                      v-for="edge in displayGraphEdges"
                      :key="edge.id"
                      :d="edge.path"
                      :class="[
                        'graph-edge',
                        {
                          'graph-edge--active': isEdgeActive(edge),
                          'graph-edge--related': isEdgeRelated(edge),
                          'graph-edge--dimmed': isEdgeDimmed(edge)
                        }
                      ]"
                      @click.stop
                      @mouseenter.stop="handleEdgeHover(edge.id)"
                      @mouseleave.stop="handleEdgeHover('')"
                    />
                  </g>
                  <g>
                    <g
                      v-for="node in displayGraphNodes"
                      :key="node.id"
                      :transform="`translate(${node.x}, ${node.y})`"
                      :class="[
                        'graph-node cursor-pointer',
                        {
                          'graph-node--active': isNodeActive(node.id),
                          'graph-node--related': isNodeRelated(node.id),
                          'graph-node--dimmed': isNodeDimmed(node.id)
                        }
                      ]"
                      role="button"
                      tabindex="0"
                      @click.stop="handleNodeClick(node.id)"
                      @keyup.enter.stop="handleNodeClick(node.id)"
                      @mouseenter.stop="handleNodeHover(node.id)"
                      @mouseleave.stop="handleNodeHover('')"
                      @pointerdown.stop="(event) => handleNodePointerDown(event, node)"
                    >
                      <circle :r="getNodeRadius(node)" :fill="getNodeFill(node)" />
                      <text class="graph-node__label" dominant-baseline="middle" text-anchor="middle">
                        {{ formatNodeLabel(node) }}
                      </text>
                    </g>
                  </g>
                </svg>
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
                        <p class="text-sm text-slate-200 break-all">{{ selectedGraphNode.id }}</p>
                      </div>
                      <div class="flex flex-col gap-1">
                        <p class="text-xs text-slate-400 uppercase tracking-wide">{{ $t('incidents.detail.eventGraph.nodeDetail.labels') }}</p>
                        <p class="text-sm text-slate-200">{{ selectedGraphNode.labels?.join(', ') }}</p>
                      </div>
                      <div class="flex flex-col gap-1">
                        <p class="text-xs text-slate-400 uppercase tracking-wide">{{ $t('incidents.detail.eventGraph.nodeDetail.entityType') }}</p>
                        <p class="text-sm text-slate-200">{{ selectedGraphNode.properties?.entity_type }}</p>
                      </div>
                    </div>
                    <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                      <h3 class="text-sm font-semibold text-white mb-3">{{ $t('incidents.detail.eventGraph.nodeDetail.properties') }}</h3>
                      <div v-if="selectedNodeProperties.length" class="space-y-3 text-sm text-slate-200">
                        <div
                          v-for="([key, value], index) in selectedNodeProperties"
                          :key="`${key}-${index}`"
                          class="flex flex-col gap-0.5"
                        >
                          <p class="text-xs uppercase text-slate-500 tracking-wide">{{ key }}</p>
                          <p class="font-mono text-slate-200 break-all">{{ value }}</p>
                        </div>
                      </div>
                      <p v-else class="text-xs text-slate-500">
                        {{ $t('common.noData') || 'No data available' }}
                      </p>
                    </div>
                    <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                      <h3 class="text-sm font-semibold text-white mb-3">{{ $t('incidents.detail.eventGraph.nodeDetail.relations') }}</h3>
                      <div v-if="selectedNodeRelations.length" class="space-y-2">
                      <button
                        v-for="relation in selectedNodeRelations"
                        :key="`${relation.direction}-${relation.neighbor}`"
                        type="button"
                        class="text-sm text-slate-200 text-left"
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
import { getIncidentDetail, postComment } from '@/api/incidents'
import AlertDetail from '@/components/alerts/AlertDetail.vue'
import EditIncidentDialog from '@/components/incidents/EditIncidentDialog.vue'
import CloseIncidentDialog from '@/components/incidents/CloseIncidentDialog.vue'
import DataTable from '@/components/common/DataTable.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import CommentSection from '@/components/common/CommentSection.vue'
import { formatDateTime } from '@/utils/dateTime'
import { useToast } from '@/composables/useToast'
import DOMPurify from 'dompurify'
import eventGraphSample from '@/data/eventGraphSample.json'

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

const eventGraphData = ref({
  nodes: eventGraphSample?.nodes || [],
  edges: eventGraphSample?.edges || []
})
const graphSearchQuery = ref('')
const highlightedEntity = ref('')
const selectedGraphNodeId = ref('')
const hoveredNodeId = ref('')
const hoveredEdgeId = ref('')
const prunedNodeIds = ref(new Set())
const nodePositions = ref({})
const draggingNodeId = ref('')
const dragOffset = ref({ x: 0, y: 0 })
const graphSvgRef = ref(null)
const legendFlashKey = ref('')
const legendFlashTimer = ref(null)
const nodeDetailWidth = ref(320)
const resizingNodeDetail = ref(false)
const resizeStartX = ref(0)
const initialNodeDetailWidth = ref(320)

const baseGraphNodes = computed(() => {
  const availableNodes = (eventGraphData.value.nodes || []).filter((node) => !prunedNodeIds.value.has(node.id))
  const count = Math.min(availableNodes.length, 14)
  if (!count) {
    return []
  }
  const radiusX = 280
  const radiusY = 200
  return availableNodes.slice(0, count).map((node, index) => {
    const angle = (index / count) * Math.PI * 2 - Math.PI / 2
    return {
      ...node,
      x: 500 + Math.cos(angle) * radiusX,
      y: 320 + Math.sin(angle) * radiusY
    }
  })
})

const displayGraphNodes = computed(() => {
  const overrides = nodePositions.value || {}
  return baseGraphNodes.value.map((node) => {
    const override = overrides[node.id]
    if (!override) {
      return node
    }
    return {
      ...node,
      x: override.x,
      y: override.y
    }
  })
})

const displayGraphEdges = computed(() => {
  const nodesById = Object.fromEntries(displayGraphNodes.value.map((node) => [node.id, node]))
  return (eventGraphData.value.edges || [])
    .filter((edge) => nodesById[edge.source] && nodesById[edge.target])
    .slice(0, 24)
    .map((edge) => {
      const positioned = {
        ...edge,
        id: edge.id || `${edge.source}-${edge.target}`,
        x1: nodesById[edge.source].x,
        y1: nodesById[edge.source].y,
        x2: nodesById[edge.target].x,
        y2: nodesById[edge.target].y
      }
      return {
        ...positioned,
        path: buildEdgePath(positioned)
      }
    })
})

const selectedGraphNode = computed(() => {
  if (!selectedGraphNodeId.value) {
    return null
  }
  return displayGraphNodes.value.find((node) => node.id === selectedGraphNodeId.value) || null
})

const graphEntityOptions = computed(() =>
  displayGraphNodes.value.map((node) => ({
    id: node.id,
    label: `${(node.properties?.entity_type || 'entity').toUpperCase()} • ${node.id}`
  }))
)

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
  if (selectedGraphNodeId.value === nodeId) {
    selectedGraphNodeId.value = ''
    return
  }
  selectedGraphNodeId.value = nodeId
  highlightedEntity.value = nodeId
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

const handleNodeHover = (nodeId) => {
  hoveredNodeId.value = nodeId
}

const getNodeFill = (node) => {
  const type = (node.properties?.entity_type || 'other').toLowerCase()
  return `url(#${ENTITY_COLOR_GRADIENT[type] || ENTITY_COLOR_GRADIENT.other})`
}

const getNodeRadius = (node) => {
  const type = node.properties?.entity_type
  if (type === 'ip') return 22
  if (type === 'tenant' || type === 'service') return 20
  if (type === 'alert') return 18
  return 16
}

const formatNodeLabel = (node) => {
  const label = node.labels?.[0] || node.id || node.properties?.entity_type || 'entity'
  return label.length > 12 ? `${label.slice(0, 11)}…` : label
}

const hoveredEdgeNodes = computed(() => {
  if (!hoveredEdgeId.value) {
    return new Set()
  }
  const edge = displayGraphEdges.value.find((edgeItem) => edgeItem.id === hoveredEdgeId.value)
  if (!edge) {
    return new Set()
  }
  return new Set([edge.source, edge.target])
})

const isNodeActive = (nodeId) => selectedGraphNodeId.value === nodeId
const isNodeRelated = (nodeId) => {
  if (legendFlashKey.value && nodeTypeMap.value[nodeId] === legendFlashKey.value) {
    return true
  }
  if (hoveredEdgeNodes.value.has(nodeId) || hoveredNodeId.value === nodeId) {
    return true
  }
  return relatedNodeIds.value.has(nodeId)
}
const isNodeDimmed = (nodeId) => {
  const searchActive = !!graphSearchQuery.value.trim()
  const selectionActive = !!selectedGraphNodeId.value
  const dimBySearch = searchActive && !filteredNodeIds.value.has(nodeId)
  const dimBySelection = selectionActive && !relatedNodeIds.value.has(nodeId)
  const dimByHover =
    !selectionActive &&
    hoveredEdgeNodes.value.size &&
    !hoveredEdgeNodes.value.has(nodeId) &&
    hoveredNodeId.value !== nodeId
  const dimByLegend =
    legendFlashKey.value &&
    nodeTypeMap.value[nodeId] !== legendFlashKey.value
  return dimBySearch || dimBySelection || dimByHover || dimByLegend
}

const isEdgeActive = (edge) =>
  !!selectedGraphNodeId.value &&
  (edge.source === selectedGraphNodeId.value || edge.target === selectedGraphNodeId.value)

const isEdgeRelated = (edge) => {
  if (
    legendFlashKey.value &&
    (nodeTypeMap.value[edge.source] === legendFlashKey.value ||
      nodeTypeMap.value[edge.target] === legendFlashKey.value)
  ) {
    return true
  }
  if (hoveredEdgeId.value && edge.id === hoveredEdgeId.value) {
    return true
  }
  if (hoveredNodeId.value) {
    return edge.source === hoveredNodeId.value || edge.target === hoveredNodeId.value
  }
  if (selectedGraphNodeId.value) {
    return edge.source === selectedGraphNodeId.value || edge.target === selectedGraphNodeId.value
  }
  return false
}

const isEdgeDimmed = (edge) => {
  const searchActive = !!graphSearchQuery.value.trim()
  const selectionActive = !!selectedGraphNodeId.value
  const dimBySearch =
    searchActive && !filteredNodeIds.value.has(edge.source) && !filteredNodeIds.value.has(edge.target)
  const dimBySelection =
    selectionActive &&
    edge.source !== selectedGraphNodeId.value &&
    edge.target !== selectedGraphNodeId.value &&
    (!hoveredNodeId.value || (edge.source !== hoveredNodeId.value && edge.target !== hoveredNodeId.value))
  const dimByHover =
    !selectionActive &&
    hoveredEdgeNodes.value.size &&
    !hoveredEdgeNodes.value.has(edge.source) &&
    !hoveredEdgeNodes.value.has(edge.target) &&
    hoveredEdgeId.value !== edge.id &&
    (!hoveredNodeId.value || (edge.source !== hoveredNodeId.value && edge.target !== hoveredNodeId.value))
  const dimByLegend =
    legendFlashKey.value &&
    nodeTypeMap.value[edge.source] !== legendFlashKey.value &&
    nodeTypeMap.value[edge.target] !== legendFlashKey.value
  return dimBySearch || dimBySelection || dimByHover || dimByLegend
}

const copySelectedNode = async () => {
  if (!selectedGraphNode.value || typeof navigator === 'undefined' || !navigator.clipboard) {
    return
  }
  try {
    await navigator.clipboard.writeText(JSON.stringify(selectedGraphNode.value, null, 2))
  } catch (error) {
    console.error('Failed to copy node detail', error)
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
  hoveredNodeId.value = ''
  hoveredEdgeId.value = ''
}

function buildEdgePath({ x1, y1, x2, y2 }) {
  const dx = x2 - x1
  const dy = y2 - y1
  const bend = Math.max(-120, Math.min(120, dx * 0.4))
  const cx1 = x1 + dx * 0.33
  const cy1 = y1 + dy * 0.33 - bend
  const cx2 = x1 + dx * 0.66
  const cy2 = y1 + dy * 0.66 + bend
  return `M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}`
}

const handleEdgeHover = (edgeId) => {
  hoveredEdgeId.value = edgeId
}

const handleGraphBackgroundClick = () => {
  if (draggingNodeId.value || resizingNodeDetail.value) {
    return
  }
  clearSelectedNode()
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

const getSvgCoordinates = (event) => {
  const svg = graphSvgRef.value
  if (!svg) {
    return { x: 0, y: 0 }
  }
  const rect = svg.getBoundingClientRect()
  const viewBox = svg.viewBox.baseVal
  const scaleX = viewBox.width / rect.width
  const scaleY = viewBox.height / rect.height
  return {
    x: (event.clientX - rect.left) * scaleX + viewBox.x,
    y: (event.clientY - rect.top) * scaleY + viewBox.y
  }
}

const handleNodePointerDown = (event, node) => {
  if (event.button !== 0) {
    return
  }
  event.preventDefault()
  const coords = getSvgCoordinates(event)
  draggingNodeId.value = node.id
  dragOffset.value = {
    x: coords.x - node.x,
    y: coords.y - node.y
  }
  window.addEventListener('pointermove', handlePointerMove)
  window.addEventListener('pointerup', handlePointerUp)
}

const handlePointerMove = (event) => {
  if (!draggingNodeId.value) {
    return
  }
  event.preventDefault()
  const coords = getSvgCoordinates(event)
  nodePositions.value = {
    ...nodePositions.value,
    [draggingNodeId.value]: {
      x: coords.x - dragOffset.value.x,
      y: coords.y - dragOffset.value.y
    }
  }
}

const handlePointerUp = () => {
  draggingNodeId.value = ''
  dragOffset.value = { x: 0, y: 0 }
  window.removeEventListener('pointermove', handlePointerMove)
  window.removeEventListener('pointerup', handlePointerUp)
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
  if (legendFlashTimer.value) {
    clearTimeout(legendFlashTimer.value)
  }
})

watch(
  baseGraphNodes,
  (nodes) => {
    if (!nodes.length) {
      selectedGraphNodeId.value = ''
      highlightedEntity.value = ''
      nodePositions.value = {}
      return
    }
    if (!nodes.some((node) => node.id === selectedGraphNodeId.value)) {
      selectedGraphNodeId.value = ''
    }
    const validIds = new Set(nodes.map((node) => node.id))
    const nextPositions = { ...nodePositions.value }
    Object.keys(nextPositions).forEach((id) => {
      if (!validIds.has(id)) {
        delete nextPositions[id]
      }
    })
    nodePositions.value = nextPositions
  },
  { immediate: true }
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

const loadIncidentDetail = async () => {
  loadingIncident.value = true
  try {
    const incidentId = route.params.id
    const response = await getIncidentDetail(incidentId)
    const data = response.data
    
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
      associatedAlerts: data.associated_alerts || data.associatedAlerts || []
    }
  } catch (error) {
    console.error('Failed to load incident detail:', error)
    router.push('/incidents')
  } finally {
    loadingIncident.value = false
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
  const baseUrl = window.location.origin
  const incidentId = route.params.id
  return `${baseUrl}/incidents/${incidentId}`
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
  transition: all 0.2s ease;
}

.event-graph-svg .graph-edge:hover {
  stroke-opacity: 0.9;
  stroke-width: 3.2;
}

.event-graph-svg .graph-edge--active {
  stroke: #38bdf8;
  stroke-opacity: 0.85;
  stroke-width: 3;
}

.event-graph-svg .graph-edge--related {
  stroke-opacity: 0.6;
}

.event-graph-svg .graph-edge--dimmed {
  opacity: 0.18;
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
</style>

