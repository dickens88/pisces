<template>
  <div class="w-full relative overflow-x-hidden">
    <!-- 加载遮罩层 -->
    <div
      v-if="loadingIncident"
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
    <!-- 面包屑导航 -->
    <nav class="mb-5">
      <ol class="flex items-center gap-2.5 text-sm">
        <li>
          <router-link
            to="/incidents"
            class="inline-flex items-center gap-1.5 text-gray-500 dark:text-gray-400 hover:text-primary dark:hover:text-primary transition-colors duration-200 font-medium"
          >
            <span class="material-symbols-outlined text-base">folder</span>
            <span>{{ $t('incidents.title') || '事件管理' }}</span>
          </router-link>
        </li>
        <li class="flex items-center text-gray-300 dark:text-gray-600">
          <span class="material-symbols-outlined text-lg">chevron_right</span>
        </li>
        <li class="flex items-center gap-2">
          <span class="text-gray-400 dark:text-gray-500 font-medium">ID:</span>
          <span class="text-gray-900 dark:text-white font-semibold font-mono text-sm bg-gray-100 dark:bg-slate-700/50 px-2.5 py-1 rounded-md border border-gray-200 dark:border-slate-600">
            {{ route.params.id || '--' }}
          </span>
        </li>
      </ol>
    </nav>
    <!-- 页面标题和操作 -->
    <header class="flex flex-wrap justify-between items-start gap-4 mb-6">
      <div class="flex flex-col gap-2">
        <h1 class="text-gray-900 dark:text-white text-xl font-bold leading-tight tracking-tight">
          {{ incident?.name }}
        </h1>
        <div class="flex flex-wrap items-center gap-x-4 gap-y-2 text-gray-600 dark:text-slate-400 text-sm font-normal leading-normal">
          <div class="flex items-center gap-1.5">
            <span>{{ $t('incidents.detail.actor') }}:</span>
            <span class="text-gray-900 dark:text-white">{{ incident?.actor }}</span>
          </div>
          <div class="h-4 w-px bg-slate-600/50"></div>
          <div class="flex items-center gap-1.5">
            <span>{{ $t('incidents.detail.createTime') }}:</span>
            <span class="text-gray-900 dark:text-white">{{ formatDateTime(incident?.createTime) }}</span>
          </div>
          <div class="h-4 w-px bg-slate-600/50"></div>
          <div class="flex items-center gap-1.5">
            <span>{{ $t('incidents.detail.closeTime') }}:</span>
            <span class="text-gray-900 dark:text-white">{{ formatDateTime(incident?.closeTime || incident?.close_time) }}</span>
          </div>
          <div class="h-4 w-px bg-slate-600/50"></div>
          <div class="flex items-center gap-1.5">
            <span>{{ $t('incidents.detail.updateTime') }}:</span>
            <span class="text-gray-900 dark:text-white">{{ formatDateTime(incident?.updateTime) }}</span>
          </div>
        </div>
      </div>
      <div class="flex flex-1 gap-3 flex-wrap justify-start sm:justify-end min-w-max">
        <button
          @click="openEditDialog"
          class="flex min-w-[84px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-10 px-4 bg-gray-200 dark:bg-slate-700 hover:bg-gray-300 dark:hover:bg-slate-600 text-gray-700 dark:text-white text-sm font-bold leading-normal tracking-[0.015em] transition-colors"
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
          class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-200 dark:disabled:hover:bg-[#2a3546] h-10"
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
          class="bg-gray-200 dark:bg-[#2a3546] hover:bg-gray-300 dark:hover:bg-[#3c4a60] text-sm font-medium text-gray-700 dark:text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center h-10"
          :title="$t('incidents.detail.share') || 'Share'"
        >
          <span class="material-symbols-outlined text-base">share</span>
        </button>
      </div>
    </header>

    <!-- 顶部统计卡片（已按需求移除） -->

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
      <!-- Alert story：事件图谱 -->
      <div v-if="activeTab === 'alertStory'" class="space-y-4">
        <!-- 外层容器沿用 Alerts 模块的卡片风格，但内部线条尽量柔和 -->
        <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867]/70 rounded-xl overflow-hidden">
          <div v-if="hasGraphData" ref="graphWorkspaceRef" class="flex min-h-[600px]">
            <!-- 左侧：告警时间线 -->
            <aside
              v-if="!isLeftPaneCollapsed"
              class="w-80 flex-none border-r border-gray-200 dark:border-slate-800 bg-white dark:bg-[#111822] flex flex-col"
            >
              <div class="px-4 py-3 border-b border-gray-200 dark:border-slate-800 flex items-center justify-between bg-gray-50 dark:bg-[#111822]">
                <div class="flex items-center gap-2">
                  <h3 class="text-sm font-semibold text-gray-800 dark:text-slate-100">
                    {{ translateOr('incidents.detail.eventGraph.timelineTitle', 'Alert timeline') }}
                  </h3>
                  <span class="text-xs text-gray-400 dark:text-slate-500">
                    {{ associatedAlertsTimeline.length }}
                  </span>
                </div>
                <button
                  type="button"
                  class="p-1 rounded text-gray-400 hover:text-gray-700 dark:text-slate-500 dark:hover:text-slate-200 transition-colors"
                  :title="translateOr('incidents.detail.eventGraph.collapseLeftPane', '收起告警列表')"
                  @click="isLeftPaneCollapsed = true"
                >
                  <span class="material-symbols-outlined text-base">chevron_left</span>
                </button>
              </div>
              <div class="flex-1 overflow-y-auto">
                <div
                  v-for="item in paginatedAssociatedAlertsTimeline"
                  :key="item.id"
                  class="px-4 py-2.5 border-b border-gray-100 dark:border-slate-800/70 hover:bg-gray-50 dark:hover:bg-[#1e293b] transition-colors cursor-default"
                >
                  <div class="flex items-center justify-between mb-1">
                    <div class="flex items-center space-x-2">
                      <span
                        :class="[
                          'w-2 h-2 rounded-full',
                          item.severity === 'high'
                            ? 'bg-red-500'
                            : item.severity === 'medium'
                              ? 'bg-orange-500'
                              : 'bg-emerald-500'
                        ]"
                      ></span>
                      <span class="text-[11px] text-gray-500 dark:text-slate-400">
                        {{ formatDateTime(item.createTime) }}
                      </span>
                    </div>
                    <span class="text-[9px] px-1.5 py-0.5 rounded bg-gray-100 dark:bg-[#1e293b] text-gray-600 dark:text-slate-300">
                      {{ $t(`alerts.list.${item.status}`) }}
                    </span>
                  </div>
                  <h4 class="text-[11px] leading-5 font-medium text-gray-900 dark:text-slate-100 break-words whitespace-normal">
                    <span :title="item.title || '-'">
                      {{ item.title || '-' }}
                    </span>
                  </h4>
                  <p class="mt-1 text-[10px] text-gray-500 dark:text-slate-400 line-clamp-2" :title="item.owner || '-'">
                    {{ item.owner || '-' }}
                  </p>
                </div>
                <div
                  v-if="associatedAlertsTimeline.length === 0"
                  class="px-4 py-6 text-center text-xs text-gray-400 dark:text-slate-500"
                >
                  {{ translateOr('incidents.detail.eventGraph.timelineEmpty', '暂无关联告警') }}
                </div>
              </div>
              <div
                v-if="timelineTotalPages > 0"
                class="px-2.5 py-1.5 border-t border-gray-100 dark:border-slate-800/70 flex items-center justify-between text-[10px] text-gray-500 dark:text-slate-400"
              >
                <div class="flex items-center gap-[2px]">
                  <button
                    type="button"
                    class="p-0.5 rounded hover:bg-gray-100 dark:hover:bg-[#1e293b] disabled:opacity-40 disabled:cursor-not-allowed"
                    :disabled="timelineCurrentPage === 1"
                    @click="timelineCurrentPage = Math.max(1, timelineCurrentPage - 1)"
                  >
                    <span class="material-symbols-outlined text-[14px]">chevron_left</span>
                  </button>
                  <span class="text-center">{{ timelineCurrentPage }}/{{ timelineTotalPages }}</span>
                  <button
                    type="button"
                    class="p-0.5 rounded hover:bg-gray-100 dark:hover:bg-[#1e293b] disabled:opacity-40 disabled:cursor-not-allowed"
                    :disabled="timelineCurrentPage === timelineTotalPages"
                    @click="timelineCurrentPage = Math.min(timelineTotalPages, timelineCurrentPage + 1)"
                  >
                    <span class="material-symbols-outlined text-[14px]">chevron_right</span>
                  </button>
                </div>
                <div class="flex items-center gap-0.5">
                  <select
                    v-model.number="timelinePageSize"
                    class="h-5 rounded border border-gray-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] px-1 text-[10px] focus:outline-none focus:ring-1 focus:ring-primary/60 focus:border-primary/60"
                    :title="translateOr('incidents.detail.eventGraph.perPageTooltip', '每页条数')"
                  >
                    <option v-for="size in timelinePageSizeOptions" :key="size" :value="size">
                      {{ size }}
                    </option>
                  </select>
                  <span class="text-[9px] text-gray-400 dark:text-slate-500">
                    /{{ translateOr('incidents.detail.eventGraph.perPageUnit', '页') }}
                  </span>
                </div>
              </div>
            </aside>
            <!-- 左侧收起后的小按钮 -->
            <button
              v-else
              type="button"
              class="flex items-center justify-center w-4 bg-slate-900/70 hover:bg-slate-900 text-slate-400 hover:text-white transition-colors"
              :title="translateOr('incidents.detail.eventGraph.expandLeftPane', '展开告警列表')"
              @click="isLeftPaneCollapsed = false"
            >
              <span class="material-symbols-outlined text-base">chevron_right</span>
            </button>

            <!-- 中间：事件图谱 -->
            <div ref="graphContainerRef" class="flex-1 relative bg-gray-50 dark:bg-[#0f172a] min-h-[600px]">
              <div class="absolute top-4 left-4 right-4 z-10 pointer-events-none">
                <div class="flex flex-col xl:flex-row gap-3 items-start pointer-events-auto text-[13px]" @click.stop>
                  <div class="flex flex-col md:flex-row gap-2.5 flex-1 w-full">
                    <div class="relative w-full md:w-60 flex items-center bg-slate-900/70 border border-slate-700 text-white rounded-lg pl-2.5 pr-2.5 h-9">
                      <span class="material-symbols-outlined text-slate-400 text-[18px] mr-1.5">search</span>
                      <input
                        v-model="graphSearchQuery"
                        type="text"
                        class="w-full bg-transparent text-[13px] focus:ring-0 focus:outline-none placeholder:text-slate-500"
                        :placeholder="$t('incidents.detail.eventGraph.filterPlaceholder')"
                      />
                    </div>
                    <div class="relative w-full md:w-60">
                      <select
                        v-model="highlightedEntity"
                        class="w-full h-9 bg-slate-900/70 border border-slate-700 text-white rounded-lg pl-3.5 pr-8 text-[13px] focus:ring-2 focus:ring-primary/60 focus:border-primary/60 appearance-none"
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
                      <span class="material-symbols-outlined absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none text-[18px]">expand_more</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-1 bg-slate-900/80 border border-slate-700 rounded-lg px-1 h-9">
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
                    <button
                      type="button"
                      class="graph-control-btn"
                      :class="{ 'graph-control-btn--loading': isRefreshingGraph }"
                      :disabled="isRefreshingGraph"
                      :title="$t('incidents.detail.eventGraph.controls.refresh')"
                      @click="handleRefreshGraphStatus"
                    >
                      <span class="material-symbols-outlined text-[18px]">refresh</span>
                    </button>
                    <button
                      type="button"
                      class="graph-control-btn ml-0.5"
                      :class="{ 'graph-control-btn--loading': isRegeneratingGraph }"
                      :disabled="isRegeneratingGraph"
                      :title="$t('incidents.detail.eventGraph.regenerateGraph')"
                      @click="handleRegenerateGraph"
                    >
                      <span class="material-symbols-outlined text-[18px]">
                        {{ isRegeneratingGraph ? 'progress_activity' : 'auto_fix_high' }}
                      </span>
                    </button>
                  </div>
                </div>
              </div>
              <div class="absolute bottom-12 left-4 z-10 pointer-events-none">
                <div class="pointer-events-auto" @click.stop>
                  <div class="bg-slate-900/80 border border-slate-700 rounded-lg px-2.5 py-1.5 shadow-lg">
                    <div class="flex flex-col gap-1 text-[11px] uppercase tracking-wide">
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
              </div>
              <div class="w-full h-full" style="position: relative;" @click="handleGraphContainerClick">
                <div
                  ref="graphCanvasRef"
                  class="w-full h-full"
                  style="min-height: 600px; width: 100%; position: absolute; top: 0; left: 0; right: 0; bottom: 0;"
                ></div>
              </div>
              <div
                class="absolute bottom-0 left-0 right-0 bg-slate-900/80 border-t border-slate-800 px-4 py-2 text-[11px] text-slate-300 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-3 z-10"
              >
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="graph-status-dot" :class="graphStatusDotClass"></span>
                  <span class="font-semibold">{{ graphStatusLabel }}</span>
                  <span class="text-slate-600">|</span>
                  <span class="whitespace-nowrap">
                    {{ translateOr('incidents.detail.eventGraph.lastGenerationTime', 'Last generation time') }}：{{ graphLastGeneratedTime || '--' }}
                  </span>
                </div>
                <div class="flex items-center gap-2 text-[11px] sm:ml-auto">
                  <span class="whitespace-nowrap">
                    {{ translateOr('incidents.detail.eventGraph.entityCount', 'Entities') }}：{{ eventGraphStats.totalNodes ?? 0 }}
                  </span>
                  <span class="text-slate-600">|</span>
                  <span class="whitespace-nowrap">
                    {{ translateOr('incidents.detail.eventGraph.relationCount', 'Relations') }}：{{ eventGraphStats.totalEdges ?? 0 }}
                  </span>
                </div>
              </div>
            </div>

            <!-- 右侧：事件关键信息 + 节点详情 -->
            <aside
              v-if="!isRightPaneCollapsed"
              class="w-80 flex-none border-l border-gray-200 dark:border-slate-800 bg-white dark:bg-[#111822] flex flex-col overflow-y-auto"
            >
              <div class="px-3 py-3 border-b border-gray-200 dark:border-slate-800 flex items-center gap-2 bg-gray-50 dark:bg-[#111822]">
                <button
                  type="button"
                  class="p-1 rounded text-gray-400 hover:text-gray-700 dark:text-slate-500 dark:hover:text-slate-200 transition-colors"
                  :title="translateOr('incidents.detail.eventGraph.collapseRightPane', '收起信息面板')"
                  @click="isRightPaneCollapsed = true"
                >
                  <span class="material-symbols-outlined text-base">chevron_right</span>
                </button>
                <h3 class="text-sm font-semibold text-gray-900 dark:text-slate-100">
                  {{ translateOr('incidents.detail.eventGraph.informationTitle', 'Information') }}
                </h3>
              </div>

              <div class="p-4 space-y-5">
                <!-- 节点详情（如果选中节点） -->
                <Transition name="fade">
                  <div
                    v-if="selectedGraphNode"
                    class="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-3 shadow-sm"
                  >
                    <div class="flex items-center justify-between mb-1">
                      <h4 class="text-xs font-bold text-slate-100 uppercase tracking-wide">
                        {{ $t('incidents.detail.eventGraph.nodeDetail.title') }}
                      </h4>
                      <div class="flex items-center space-x-1">
                        <button
                          class="detail-action-btn"
                          :title="$t('incidents.detail.eventGraph.nodeDetail.copy')"
                          @click="copySelectedNode"
                        >
                          <span class="material-symbols-outlined text-sm">content_copy</span>
                        </button>
                        <button
                          class="detail-action-btn"
                          :title="$t('incidents.detail.eventGraph.nodeDetail.prune')"
                          @click="pruneSelectedNode"
                        >
                          <span class="material-symbols-outlined text-sm">content_cut</span>
                        </button>
                        <button
                          class="detail-action-btn"
                          :title="$t('incidents.detail.eventGraph.nodeDetail.close')"
                          @click="clearSelectedNode"
                        >
                          <span class="material-symbols-outlined text-sm">close</span>
                        </button>
                      </div>
                    </div>
                    <div class="space-y-3">
                      <div class="flex flex-col gap-1">
                        <p class="text-xs font-semibold text-slate-300">
                          {{ $t('incidents.detail.eventGraph.nodeDetail.id') }}
                        </p>
                        <p class="text-xs text-slate-100 break-all whitespace-pre-wrap">
                          {{ formatNodeDetailValue(selectedGraphNode.id) }}
                        </p>
                      </div>
                      <div class="flex flex-col gap-1">
                        <p class="text-xs font-semibold text-slate-300">
                          {{ translateOr('incidents.detail.eventGraph.nodeDetail.label', 'Label') }}
                        </p>
                        <p class="text-xs text-slate-100 whitespace-pre-wrap">
                          {{ formatNodeDetailValue(primaryNodeLabel) || '-' }}
                        </p>
                      </div>
                      <div class="flex flex-col gap-1">
                        <p class="text-xs font-semibold text-slate-300">
                          {{ $t('incidents.detail.eventGraph.nodeDetail.entityType') }}
                        </p>
                        <p class="text-xs text-slate-100 whitespace-pre-wrap">
                          {{ formatNodeDetailValue(selectedGraphNode.properties?.entity_type) }}
                        </p>
                      </div>
                      <div class="flex flex-col gap-1">
                        <p class="text-xs font-semibold text-slate-300">
                          {{ translateOr('incidents.detail.eventGraph.nodeDetail.propertyDescription', '属性描述') }}
                        </p>
                        <p
                          v-if="selectedNodeDescription"
                          class="text-xs text-slate-100 whitespace-pre-wrap"
                        >
                          {{ selectedNodeDescription }}
                        </p>
                        <p
                          v-else
                          class="text-xs text-slate-500 italic whitespace-pre-wrap"
                        >
                          {{ translateOr('incidents.detail.eventGraph.nodeDetail.propertyDescriptionPlaceholder', '暂无属性描述') }}
                        </p>
                      </div>
                    </div>
                  </div>
                </Transition>

                <!-- 事件详情信息 -->
                <div>
                  <h4 class="text-[11px] font-bold text-gray-900 dark:text-slate-100 uppercase tracking-wide mb-2">
                    {{ translateOr('incidents.detail.eventGraph.incidentInfoTitle', 'Incident details') }}
                  </h4>
                  <div class="space-y-2 text-xs">
                    <div class="grid grid-cols-3 gap-2">
                      <span class="text-gray-500 dark:text-slate-400 col-span-1">
                        {{ $t('incidents.detail.status') }}
                      </span>
                      <span class="col-span-2 flex items-center text-gray-900 dark:text-slate-100 font-medium">
                        <span
                          class="w-2 h-2 rounded-full mr-2"
                          :class="getIncidentStatusDotClass(incident?.status)"
                        ></span>
                        {{ getStatusText(incident?.status) }}
                      </span>
                    </div>
                    <div class="grid grid-cols-3 gap-2">
                      <span class="text-gray-500 dark:text-slate-400 col-span-1">
                        {{ $t('incidents.detail.severity') }}
                      </span>
                      <span class="col-span-2 flex items-center font-medium text-gray-900 dark:text-slate-100">
                        <span
                          v-if="incident?.severity"
                          :class="[
                            'text-xs font-medium px-2.5 py-0.5 rounded-full inline-flex items-center justify-center',
                            getRiskLevelClass(getIncidentRiskLevel(incident.severity))
                          ]"
                          :title="$t(`common.severity.${getIncidentRiskLevel(incident.severity)}`)"
                        >
                          {{ $t(`common.severity.${getIncidentRiskLevel(incident.severity)}`) }}
                        </span>
                        <span v-else>-</span>
                      </span>
                    </div>
                    <div class="grid grid-cols-3 gap-2">
                      <span class="text-gray-500 dark:text-slate-400 col-span-1">
                        {{ $t('incidents.detail.responsiblePerson') }}
                      </span>
                      <span class="col-span-2 text-gray-900 dark:text-slate-100 truncate">
                        {{ incident?.owner || incident?.responsiblePerson || '-' }}
                      </span>
                    </div>
                    <div class="grid grid-cols-3 gap-2">
                      <span class="text-gray-500 dark:text-slate-400 col-span-1">
                        {{ $t('incidents.detail.responsibleDepartment') }}
                      </span>
                      <span class="col-span-2 text-gray-900 dark:text-slate-100 truncate">
                        {{ incident?.responsibleDept || '-' }}
                      </span>
                    </div>
                    <div class="grid grid-cols-3 gap-2">
                      <span class="text-gray-500 dark:text-slate-400 col-span-1">
                        {{ $t('incidents.detail.category') }}
                      </span>
                      <span class="col-span-2 text-gray-900 dark:text-slate-100 truncate">
                        {{
                          $t(
                            `incidents.create.category${
                              incident?.category
                                ? incident.category.charAt(0).toUpperCase() + incident.category.slice(1)
                                : 'Platform'
                            }`
                          )
                        }}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- 分割线：事件详情 与 受影响资产 之间（略微减弱暗色边框） -->
                <div
                  v-if="topImpactedEntities.length"
                  class="my-3 border-t border-gray-200 dark:border-slate-700/60"
                ></div>

                <!-- 受影响资产：图谱中关联度最高的实体 Top 5 -->
                <div v-if="topImpactedEntities.length">
                  <h4 class="text-[11px] font-bold text-gray-900 dark:text-slate-100 uppercase tracking-wide mb-2">
                    {{ translateOr('incidents.detail.eventGraph.impactedAssetsTitle', 'Impacted assets') }}
                  </h4>
                  <ul class="space-y-1.5 text-xs">
                    <li
                      v-for="item in topImpactedEntities"
                      :key="item.id"
                      class="flex items-center justify-between text-gray-900 dark:text-slate-100"
                    >
                      <div class="flex flex-col max-w-[150px]">
                        <span class="truncate font-medium">
                          {{ item.label }}
                        </span>
                        <span class="text-[10px] text-gray-400 dark:text-slate-500 truncate">
                          {{ item.type }}
                        </span>
                      </div>
                      <span class="text-[10px] text-gray-500 dark:text-slate-400">
                        {{ translateOr('incidents.detail.eventGraph.degreeLabel', 'Relations') }}: {{ item.degree }}
                      </span>
                    </li>
                  </ul>
                </div>

                <!-- 分割线：受影响资产 与 描述 之间 -->
                <div
                  v-if="incident?.description"
                  class="my-3 border-t border-gray-200 dark:border-slate-700/60"
                ></div>

                <!-- 描述 -->
                <div v-if="incident?.description">
                  <h4 class="text-[11px] font-bold text-gray-900 dark:text-slate-100 uppercase tracking-wide mb-2">
                    {{ translateOr('incidents.detail.eventGraph.descriptionTitle', 'Description') }}
                  </h4>
                  <p class="text-xs text-gray-600 dark:text-slate-300 leading-relaxed">
                    {{ incident.description }}
                  </p>
                </div>

                <!-- 标签 -->
                <!-- Tags 区域按需求移除 -->
              </div>
            </aside>
            <!-- 右侧收起后的小按钮 -->
            <button
              v-else
              type="button"
              class="flex items-center justify-center w-4 bg-slate-900/70 hover:bg-slate-900 text-slate-400 hover:text-white transition-colors"
              :title="translateOr('incidents.detail.eventGraph.expandRightPane', '展开信息面板')"
              @click="isRightPaneCollapsed = false"
            >
              <span class="material-symbols-outlined text-base">chevron_left</span>
            </button>
          </div>
          <div
            v-else
            class="min-h-[420px] flex items-center justify-center p-10"
          >
            <svg
              class="w-24 h-24 text-slate-600/80"
              viewBox="0 0 120 120"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle cx="24" cy="60" r="10" stroke="currentColor" stroke-width="3" fill="none" />
              <circle cx="60" cy="24" r="12" stroke="currentColor" stroke-width="3" fill="none" />
              <circle cx="96" cy="60" r="10" stroke="currentColor" stroke-width="3" fill="none" />
              <circle cx="60" cy="96" r="12" stroke="currentColor" stroke-width="3" fill="none" />
              <path d="M33 53 L51 35" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
              <path d="M69 35 L87 53" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
              <path d="M51 85 L33 67" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
              <path d="M87 67 L69 85" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Alerts 标签页：关联告警列表 -->
      <div v-else-if="activeTab === 'alerts'" class="flex flex-col gap-6">
        <!-- 关联告警 -->
        <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-xl">
          <div class="p-6 border-b border-gray-200 dark:border-[#324867] flex items-center justify-between">
            <h3 class="text-gray-900 dark:text-white font-bold text-lg">
              {{ $t('incidents.detail.overview.associatedAlerts') }}
            </h3>
            <button
              :disabled="selectedAlerts.length === 0"
              @click="openDisassociateDialog"
              class="flex items-center justify-center gap-2 rounded-lg h-10 bg-gray-200 dark:bg-[#233348] text-gray-700 dark:text-white text-sm font-bold px-4 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300 dark:hover:bg-[#324867] transition-colors"
            >
              <span class="material-symbols-outlined text-base">link_off</span>
              <span>{{ $t('incidents.detail.disassociate') }}</span>
            </button>
          </div>
          <DataTable
            ref="associatedAlertsTableRef"
            :columns="associatedAlertsColumns"
            :items="formattedAssociatedAlerts"
            :selectable="true"
            :resizable="true"
            storage-key="incident-associated-alerts-table-columns"
            :default-widths="associatedAlertsDefaultWidths"
            :pagination="false"
            @select="handleSelectAlerts"
            @select-all="handleSelectAlerts"
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

      <!-- Assets 标签页：受影响资产 -->
      <div v-else-if="activeTab === 'assets'" class="flex flex-col gap-6">
        <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867]/70 rounded-xl">
          <div class="p-6 border-b border-gray-200 dark:border-slate-800">
            <h3 class="text-gray-900 dark:text-white font-bold text-lg">
              {{ translateOr('incidents.detail.eventGraph.impactedAssetsTitle', 'Impacted assets') }}
            </h3>
          </div>
          <div class="p-6">
            <div v-if="topImpactedEntities.length > 0" class="space-y-3">
              <div
                v-for="item in topImpactedEntities"
                :key="item.id"
                class="flex items-center justify-between p-4 border border-gray-200 dark:border-slate-700/60 rounded-lg hover:bg-gray-50 dark:hover:bg-[#1e293b] transition-colors"
              >
                <div class="flex flex-col flex-1 min-w-0">
                  <span class="text-gray-900 dark:text-white font-medium truncate">
                    {{ item.label }}
                  </span>
                  <span class="text-sm text-gray-500 dark:text-slate-400 truncate mt-1">
                    {{ item.type }}
                  </span>
                </div>
                <span class="text-sm text-gray-600 dark:text-slate-300 ml-4 whitespace-nowrap">
                  {{ translateOr('incidents.detail.eventGraph.degreeLabel', 'Relations') }}: {{ item.degree }}
                </span>
              </div>
            </div>
            <div v-else class="text-center py-12 text-gray-400 dark:text-slate-500">
              {{ translateOr('common.noData', '暂无数据') }}
            </div>
          </div>
        </div>
      </div>

      <!-- Evidence & Response 标签页：评论 / 证据 -->
      <div v-else-if="activeTab === 'evidenceResponse'" class="flex-grow">
        <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867]/70 rounded-xl flex flex-col">
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

    <!-- 解关联确认对话框 -->
    <div
      v-if="showDisassociateDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="closeDisassociateDialog"
    >
      <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-lg p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ $t('incidents.detail.disassociateDialog.title') }}
          </h2>
          <button
            @click="closeDisassociateDialog"
            class="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
          </button>
        </div>

        <!-- Prompt message -->
        <div class="mb-6 p-3 bg-gray-100 dark:bg-[#1e293b] rounded-md">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ $t('incidents.detail.disassociateDialog.confirmMessage', { count: selectedAlerts.length }) }}
          </p>
        </div>

        <!-- Action buttons -->
        <div class="flex items-center justify-end gap-3">
          <button
            @click="closeDisassociateDialog"
            class="px-4 py-2 text-sm text-gray-700 dark:text-gray-400 bg-gray-100 dark:bg-[#1e293b] rounded-md hover:bg-gray-200 dark:hover:bg-primary/30 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="handleDisassociate"
            :disabled="isDisassociating"
            class="px-4 py-2 text-sm text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span v-if="isDisassociating" class="material-symbols-outlined animate-spin text-base">sync</span>
            {{ $t('incidents.detail.disassociate') }}
          </button>
        </div>
      </div>
    </div>

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
import { getIncidentDetail, postComment, regenerateIncidentGraph, disassociateAlertsFromIncident } from '@/api/incidents'
import AlertDetail from '@/components/alerts/AlertDetail.vue'
import EditIncidentDialog from '@/components/incidents/EditIncidentDialog.vue'
import CloseIncidentDialog from '@/components/incidents/CloseIncidentDialog.vue'
import DataTable from '@/components/common/DataTable.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import CommentSection from '@/components/common/CommentSection.vue'
import { formatDateTime, parseToDate } from '@/utils/dateTime'
import { useToast } from '@/composables/useToast'
import { severityToNumber } from '@/utils/severity'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import * as d3 from 'd3'

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
// 默认进入 Alert story 视图
const activeTab = ref('alertStory')
const newComment = ref('')
const selectedAlertId = ref(null)
const showShareSuccess = ref(false)
const showCloseDialog = ref(false)
const isClosingIncident = ref(false)
const closeDialogRef = ref(null)
const showEditDialog = ref(false)
const editIncidentInitialData = ref(null)
const selectedAlerts = ref([])
const associatedAlertsTableRef = ref(null)
const showDisassociateDialog = ref(false)
const isDisassociating = ref(false)

const createEmptyGraphData = () => ({
  nodes: [],
  edges: []
})
const eventGraphData = ref(createEmptyGraphData())
const graphSearchQuery = ref('')
const highlightedEntity = ref('')
const selectedGraphNodeId = ref('')
const prunedNodeIds = ref(new Set())
const graphCanvasRef = ref(null)
const graphContainerRef = ref(null)
const graphWorkspaceRef = ref(null)
const d3SvgRef = ref(null)
const d3ZoomLayerRef = ref(null)
const d3LinkSelection = ref(null)
const d3NodeSelection = ref(null)
const d3SimulationRef = ref(null)
const d3ZoomBehaviorRef = ref(null)
const d3CurrentTransform = ref(d3.zoomIdentity)
const graphResizeObserver = ref(null)
const legendFlashKey = ref('')
const legendFlashTimer = ref(null)
const nodeDetailWidth = ref(320)
const resizingNodeDetail = ref(false)
const resizeStartX = ref(0)
const initialNodeDetailWidth = ref(320)
const isRefreshingGraph = ref(false)
const isRegeneratingGraph = ref(false)
const isGraphFullscreen = ref(false)
const isSummaryExpanded = ref(false)
const isPropertyDescriptionExpanded = ref(false)
const graphSummaryRef = ref(null)
const propertyDescriptionRef = ref(null)
const summaryNeedsTruncate = ref(false)
const propertyDescriptionNeedsTruncate = ref(false)
const fixedNodePositions = ref(new Map())
const edgeIdKey = (edge, index) => `${edge.source}-${edge.target}-${index}`

const getNodeId = (nodeRef) => (typeof nodeRef === 'object' && nodeRef !== null ? nodeRef.id : nodeRef)

const buildNodeVisualMeta = (node) => {
  const type = (node.properties?.entity_type || 'other').toLowerCase()
  const color = ENTITY_COLOR_SOLID[type] || ENTITY_COLOR_SOLID.other
  const degree = nodeDegreeMap?.value?.[node.id] || 0
  // 节点整体缩小，避免在视图里挤成一团
  const size = Math.min(20 + degree * 1.5, 40)
  return { type, color, size }
}

const destroyD3Graph = () => {
  if (graphResizeObserver.value) {
    graphResizeObserver.value.disconnect()
    graphResizeObserver.value = null
  }
  if (d3SimulationRef.value) {
    d3SimulationRef.value.on('tick', null)
    d3SimulationRef.value.stop()
    d3SimulationRef.value = null
  }
  if (d3SvgRef.value) {
    d3SvgRef.value.on('.zoom', null)
    d3SvgRef.value.remove()
    d3SvgRef.value = null
  }
  d3ZoomLayerRef.value = null
  d3LinkSelection.value = null
  d3NodeSelection.value = null
  d3ZoomBehaviorRef.value = null
  d3CurrentTransform.value = d3.zoomIdentity
}

const isGraphSvgAttached = () => {
  if (!graphCanvasRef.value || !d3SvgRef.value || typeof d3SvgRef.value.node !== 'function') {
    return false
  }
  const svgNode = d3SvgRef.value.node()
  if (!svgNode) {
    return false
  }
  return graphCanvasRef.value.contains(svgNode)
}

const tickSimulation = () => {
  if (!d3LinkSelection.value || !d3NodeSelection.value) {
    return
  }
  // 更新链接位置
  d3LinkSelection.value
    .attr('x1', (d) => {
      const source = typeof d.source === 'object' ? d.source : d.source
      return source?.x ?? 0
    })
    .attr('y1', (d) => {
      const source = typeof d.source === 'object' ? d.source : d.source
      return source?.y ?? 0
    })
    .attr('x2', (d) => {
      const target = typeof d.target === 'object' ? d.target : d.target
      return target?.x ?? 0
    })
    .attr('y2', (d) => {
      const target = typeof d.target === 'object' ? d.target : d.target
      return target?.y ?? 0
    })
  // 更新节点位置
  d3NodeSelection.value.attr('transform', (d) => {
    if (d.x == null || d.y == null) return 'translate(0, 0)'
    return `translate(${d.x}, ${d.y})`
  })
}

const dragStarted = (event, node) => {
  event.sourceEvent?.stopPropagation?.()
  if (!event.active && d3SimulationRef.value) {
    d3SimulationRef.value.alphaTarget(0.3).restart()
  }
  node.fx = node.x
  node.fy = node.y
}

const dragged = (event, node) => {
  node.fx = event.x
  node.fy = event.y
}

const dragEnded = (event, node) => {
  event.sourceEvent?.stopPropagation?.()
  if (!event.active && d3SimulationRef.value) {
    d3SimulationRef.value.alphaTarget(0)
  }
  node.fx = event.x
  node.fy = event.y
  if (node.id) {
    const next = new Map(fixedNodePositions.value)
    next.set(node.id, { x: node.fx, y: node.fy })
    fixedNodePositions.value = next
  }
}

const initD3Graph = () => {
  if (!graphCanvasRef.value || !hasGraphData.value || displayGraphNodes.value.length === 0) {
    console.log('Cannot init D3 graph:', {
      hasRef: !!graphCanvasRef.value,
      hasData: hasGraphData.value,
      nodesCount: displayGraphNodes.value.length
    })
    destroyD3Graph()
    return
  }

  console.log('Initializing D3 graph...')
  graphCanvasRef.value.innerHTML = ''
  const { width, height } = getGraphSize()
  console.log('Graph size:', { width, height })

  // 检测当前主题模式
  const isDarkMode = document.documentElement.classList.contains('dark')
  const graphBackgroundColor = isDarkMode ? '#0f172a' : '#f9fafb'
  const graphTextColor = isDarkMode ? '#e2e8f0' : '#374151'

  const svg = d3
    .select(graphCanvasRef.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('class', 'event-graph-svg')
    .attr('viewBox', `0 0 ${width} ${height}`)
    .style('background', graphBackgroundColor)
    .attr('data-text-color', graphTextColor)

  const zoomLayer = svg.append('g').attr('class', 'graph-zoom-layer')
  const linkGroup = zoomLayer.append('g').attr('class', 'graph-links')
  const nodeGroup = zoomLayer.append('g').attr('class', 'graph-nodes')

  const zoomBehavior = d3
    .zoom()
    .scaleExtent([GRAPH_MIN_ZOOM, GRAPH_MAX_ZOOM])
    .on('zoom', (event) => {
      zoomLayer.attr('transform', event.transform)
      d3CurrentTransform.value = event.transform
    })

  svg.call(zoomBehavior)
  svg.on('click', (event) => {
    if (event.target === svg.node()) {
      handleGraphBackgroundClick()
    }
  })

  d3SvgRef.value = svg
  d3ZoomLayerRef.value = zoomLayer
  d3LinkSelection.value = linkGroup.selectAll('line')
  d3NodeSelection.value = nodeGroup.selectAll('g.graph-node')
  d3ZoomBehaviorRef.value = zoomBehavior

  const simulation = d3
    .forceSimulation()
    .alphaDecay(0.02)
    .velocityDecay(0.4)
    .force('link', d3.forceLink().id((node) => node.id))
    .force(
      'charge',
      d3
        .forceManyBody()
        .strength((node) => {
          const degree = nodeDegreeMap.value[node.id] || 0
          if (degree === 0) return -1200
          if (degree === 1) return -700
          return -350
        })
        .distanceMax(700)
    )
    .force('center', d3.forceCenter(width / 2, height / 2))
    // 碰撞半径减小，让图在保持不重叠的前提下更松散
    .force('collision', d3.forceCollide().radius((node) => (node.visual?.size || 24) / 2 + 36))

  simulation.on('tick', tickSimulation)
  d3SimulationRef.value = simulation

  setupGraphResizeObserver()
  updateD3Graph({ fitView: true })
}

const updateD3Graph = ({ fitView = false } = {}) => {
  if (!d3SimulationRef.value || !d3ZoomLayerRef.value) {
    if (activeTab.value === 'alertStory' && hasGraphData.value) {
      nextTick(() => initD3Graph())
    }
    return
  }

  if (!hasGraphData.value || displayGraphNodes.value.length === 0) {
    destroyD3Graph()
    return
  }

  console.log('Updating D3 graph:', {
    nodesCount: displayGraphNodes.value.length,
    edgesCount: displayGraphEdges.value.length,
    hasSimulation: !!d3SimulationRef.value,
    hasZoomLayer: !!d3ZoomLayerRef.value
  })

  pruneInvalidFixedPositions()

  const { width, height } = getGraphSize()
  const centerX = width / 2
  const centerY = height / 2
  const radius = Math.min(width, height) * 0.42
  const nodeCount = displayGraphNodes.value.length
  const angleStep = (2 * Math.PI) / Math.max(nodeCount, 1)

  const nodes = displayGraphNodes.value.map((node, index) => {
    const visual = buildNodeVisualMeta(node)
    const fixedPosition = fixedNodePositions.value.get(node.id)
    let initialX = fixedPosition?.x ?? node.x
    let initialY = fixedPosition?.y ?? node.y
    
    if (initialX == null || initialY == null) {
      const angle = index * angleStep
      const r = radius * (0.7 + Math.random() * 0.3)
      initialX = centerX + r * Math.cos(angle)
      initialY = centerY + r * Math.sin(angle)
    }
    
    return {
      ...node,
      visual,
      fx: fixedPosition?.x ?? node.fx ?? null,
      fy: fixedPosition?.y ?? node.fy ?? null,
      x: initialX,
      y: initialY
    }
  })

  const links = displayGraphEdges.value.map((edge, index) => ({
    ...edge,
    id: edgeIdKey(edge, index)
  }))

  d3SimulationRef.value.nodes(nodes)
  const linkForce = d3SimulationRef.value.force('link')
  linkForce.links(links)
  
  linkForce
    .distance((edge) => {
      const sourceId = typeof edge.source === 'object' ? edge.source.id : edge.source
      const targetId = typeof edge.target === 'object' ? edge.target.id : edge.target
      const totalDegree = (nodeDegreeMap.value[sourceId] || 0) + (nodeDegreeMap.value[targetId] || 0)
      if (totalDegree > 6) return 200
      if (totalDegree > 3) return 150
      return 120
    })
    .strength(0.8)

  d3SimulationRef.value.force(
    'charge',
    d3
      .forceManyBody()
      .strength((node) => {
        const degree = nodeDegreeMap.value[node.id] || 0
        if (degree === 0) return -1200
        if (degree === 1) return -700
        return -350
      })
      .distanceMax(700)
  )

  d3SimulationRef.value.force(
    'collision',
    d3.forceCollide().radius((node) => (node.visual?.size || 24) / 2 + 36)
  )

  d3SimulationRef.value
    .alpha(1.0)
    .alphaDecay(0.02)
    .velocityDecay(0.4)
    .restart()

  // 从正确的父元素获取选择器
  const linkGroup = d3ZoomLayerRef.value?.select('.graph-links')
  const nodeGroup = d3ZoomLayerRef.value?.select('.graph-nodes')
  
  if (!linkGroup || !nodeGroup) {
    console.warn('Graph groups not found, reinitializing...')
    nextTick(() => initD3Graph())
    return
  }

  const linkSelection = linkGroup.selectAll('line.graph-link').data(links, (d) => d.id)
  linkSelection.exit().remove()

  const linkEnter = linkSelection
    .enter()
    .append('line')
    .attr('class', 'graph-link')

  d3LinkSelection.value = linkEnter
    .merge(linkSelection)
    .attr('stroke', '#475569')
    .attr('stroke-width', 1.2)
    .attr('stroke-opacity', 0.35)

  const nodeSelection = nodeGroup.selectAll('g.graph-node').data(nodes, (d) => d.id)
  nodeSelection.exit().remove()

  const nodeEnter = nodeSelection
    .enter()
    .append('g')
    .attr('class', 'graph-node')

  nodeEnter
    .append('circle')
    .attr('r', (d) => (d.visual?.size || 30) / 2)
    .attr('fill', (d) => d.visual?.color || ENTITY_COLOR_SOLID.other)
    .attr('stroke', '#94a3b8')
    .attr('stroke-width', 1.2)
    .attr('fill-opacity', 0.9)

  // 获取文字颜色（从 SVG 的 data 属性或检测主题）
  const getTextColor = () => {
    const svgElement = d3SvgRef.value?.node()
    if (svgElement) {
      const dataColor = svgElement.getAttribute('data-text-color')
      if (dataColor) return dataColor
    }
    const isDark = document.documentElement.classList.contains('dark')
    return isDark ? '#e2e8f0' : '#374151'
  }

  nodeEnter
    .append('text')
    .attr('class', 'graph-node__label')
    .attr('x', (d) => (d.visual?.size || 30) / 2 + 6)
    .attr('dy', '0.32em')
    .attr('fill', getTextColor())
    .text((d) => formatNodeLabel(d))

  nodeEnter
    .on('click', (event, datum) => {
      event.stopPropagation()
      if (datum?.id) {
        handleNodeClick(datum.id)
        nextTick(() => updateNodeStyles())
      }
    })
    .on('dblclick', (event, datum) => {
      event.stopPropagation()
      if (!datum?.id) {
        return
      }
      releaseNodeFixedPosition(datum.id)
      datum.fx = null
      datum.fy = null
      d3SimulationRef.value?.alpha(0.5).restart()
      nextTick(() => updateNodeStyles())
    })

  const dragBehavior = d3.drag().on('start', dragStarted).on('drag', dragged).on('end', dragEnded)
  nodeEnter.call(dragBehavior)
  nodeSelection.call(dragBehavior)

  d3NodeSelection.value = nodeEnter.merge(nodeSelection)

  // 更新所有节点的文字颜色（包括新创建的和已存在的）
  d3NodeSelection.value
    .select('text')
    .attr('fill', getTextColor())

  d3NodeSelection.value.attr('transform', (d) => {
    if (d.x == null || d.y == null) {
      const { width, height } = getGraphSize()
      d.x = width / 2
      d.y = height / 2
    }
    return `translate(${d.x}, ${d.y})`
  })

  console.log('D3 graph updated:', {
    linksCount: d3LinkSelection.value.size(),
    nodesCount: d3NodeSelection.value.size(),
    simulationNodes: d3SimulationRef.value.nodes().length
  })

  updateNodeStyles()

  if (fitView) {
    resetGraphZoom()
  }
}

const updateNodeStyles = () => {
  if (!d3NodeSelection.value || !d3LinkSelection.value) {
    return
  }
  const selectedId = selectedGraphNodeId.value
  const searchActive = !!graphSearchQuery.value.trim()
  const highlightSet = filteredNodeIds.value
  const relations = relatedNodeIds.value

  d3NodeSelection.value
    .classed('graph-node--selected', (node) => !!selectedId && node.id === selectedId)
    .classed(
      'graph-node--related',
      (node) => !!selectedId && node.id !== selectedId && relations.has(node.id)
    )
    .classed('graph-node--dimmed', (node) => {
      if (selectedId) {
        return node.id !== selectedId && !relations.has(node.id)
      }
      if (searchActive) {
        return !highlightSet.has(node.id)
      }
      return false
    })
    .classed(
      'graph-node--search-hit',
      (node) => !selectedId && searchActive && highlightSet.has(node.id)
    )

  // 获取文字颜色
  const getTextColor = () => {
    const svgElement = d3SvgRef.value?.node()
    if (svgElement) {
      const dataColor = svgElement.getAttribute('data-text-color')
      if (dataColor) return dataColor
    }
    const isDark = document.documentElement.classList.contains('dark')
    return isDark ? '#e2e8f0' : '#374151'
  }

  d3NodeSelection.value
    .select('circle')
    .attr('stroke', (node) => (selectedId === node.id ? '#60a5fa' : '#94a3b8'))
    .attr('stroke-width', (node) => (selectedId === node.id ? 2.4 : 1.2))
    .attr('opacity', (node) => {
      if (selectedId) {
        return node.id === selectedId || relations.has(node.id) ? 0.95 : 0.15
      }
      if (searchActive) {
        return highlightSet.has(node.id) ? 0.95 : 0.2
      }
      return 0.9
    })

  // 更新文字颜色
  d3NodeSelection.value
    .select('text')
    .attr('fill', getTextColor())

  const isEdgeRelated = (edge) => {
    const sourceId = getNodeId(edge.source)
    const targetId = getNodeId(edge.target)
    if (!selectedId) {
      return false
    }
    return (
      sourceId === selectedId ||
      targetId === selectedId ||
      (relations.has(sourceId) && relations.has(targetId))
    )
  }

  d3LinkSelection.value
    .classed('graph-link--related', (edge) => {
      if (selectedId) {
        return isEdgeRelated(edge)
      }
      if (searchActive) {
        const sourceId = getNodeId(edge.source)
        const targetId = getNodeId(edge.target)
        return highlightSet.has(sourceId) || highlightSet.has(targetId)
      }
      return false
    })
    .classed('graph-link--dimmed', (edge) => {
      if (selectedId) {
        return !isEdgeRelated(edge)
      }
      if (searchActive) {
        const sourceId = getNodeId(edge.source)
        const targetId = getNodeId(edge.target)
        return !highlightSet.has(sourceId) && !highlightSet.has(targetId)
      }
      return false
    })
}

const resetGraphZoom = () => {
  if (!d3SvgRef.value || !d3ZoomBehaviorRef.value) {
    return
  }
  d3SvgRef.value
    .transition()
    .duration(300)
    .call(d3ZoomBehaviorRef.value.transform, d3.zoomIdentity)
  d3CurrentTransform.value = d3.zoomIdentity
}

const resizeD3Graph = () => {
  if (!d3SvgRef.value) {
    return
  }
  const { width, height } = getGraphSize()
  d3SvgRef.value.attr('width', width).attr('height', height).attr('viewBox', `0 0 ${width} ${height}`)
  if (d3SimulationRef.value) {
    d3SimulationRef.value.force('center', d3.forceCenter(width / 2, height / 2))
    d3SimulationRef.value.alpha(0.3).restart()
  }
}

const downloadGraphSnapshot = () => {
  if (!d3SvgRef.value) {
    return
  }
  try {
    const svgNode = d3SvgRef.value.node()
    if (!svgNode) {
      return
    }
    const serializer = new XMLSerializer()
    let source = serializer.serializeToString(svgNode)
    if (!source.match(/^<svg[^>]+xmlns=/)) {
      source = source.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')
    }
    if (!source.match(/xmlns:xlink=/)) {
      source = source.replace('<svg', '<svg xmlns:xlink="http://www.w3.org/1999/xlink"')
    }
    const svgBlob = new Blob([source], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(svgBlob)
    const image = new Image()
    image.crossOrigin = 'anonymous'
    image.onload = () => {
      const { width, height } = getGraphSize()
      const canvas = document.createElement('canvas')
      canvas.width = width
      canvas.height = height
      const context = canvas.getContext('2d')
      context.fillStyle = '#0f172a'
      context.fillRect(0, 0, width, height)
      context.drawImage(image, 0, 0, width, height)
      URL.revokeObjectURL(url)
      const incidentId = incident.value?.id || incident.value?.eventId || 'incident'
      const link = document.createElement('a')
      link.download = `incident-graph-${incidentId}.png`
      link.href = canvas.toDataURL('image/png')
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
    image.onerror = () => {
      URL.revokeObjectURL(url)
    }
    image.src = url
  } catch (error) {
    console.error('Failed to export graph snapshot', error)
  }
}

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
  clearAllFixedPositions()
  selectedGraphNodeId.value = ''
  highlightedEntity.value = ''
  prunedNodeIds.value = new Set()
  
  // 如果当前在 Alert story（图谱）标签页，初始化图表
  // 否则等待用户切换到该标签页时再初始化（通过 watch activeTab）
  if (activeTab.value === 'alertStory') {
    nextTick(() => {
      let retries = 0
      const maxRetries = 10
      const tryInit = () => {
        if (graphCanvasRef.value && hasGraphData.value) {
          initD3Graph()
        } else if (retries < maxRetries) {
          retries++
          setTimeout(tryInit, 100)
        } else {
          console.warn('Cannot initialize graph after retries:', {
            hasRef: !!graphCanvasRef.value,
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

const primaryNodeLabel = computed(() => {
  if (!selectedGraphNode.value) {
    return ''
  }
  const labels = selectedGraphNode.value.labels || []
  if (labels.length > 0) {
    return labels[0]
  }
  return selectedGraphNode.value.properties?.entity_id || selectedGraphNode.value.id || ''
})

const pruneInvalidFixedPositions = () => {
  if (!fixedNodePositions.value.size) {
      return
    }
  const validIds = new Set(displayGraphNodes.value.map((node) => node.id))
  let changed = false
  const next = new Map()
  fixedNodePositions.value.forEach((pos, nodeId) => {
    if (validIds.has(nodeId)) {
      next.set(nodeId, pos)
    } else {
      changed = true
    }
  })
  if (changed) {
    fixedNodePositions.value = next
  }
}

const clearAllFixedPositions = () => {
  if (!fixedNodePositions.value.size) {
    return
  }
  fixedNodePositions.value = new Map()
  if (d3SimulationRef.value) {
    d3SimulationRef.value.nodes().forEach((node) => {
      node.fx = null
      node.fy = null
    })
    d3SimulationRef.value.alpha(0.5).restart()
  }
}

const releaseNodeFixedPosition = (nodeId) => {
  if (!nodeId || !fixedNodePositions.value.size) {
    return
  }
  if (!fixedNodePositions.value.has(nodeId)) {
    return
  }
  const next = new Map(fixedNodePositions.value)
  next.delete(nodeId)
  fixedNodePositions.value = next
  if (d3SimulationRef.value) {
    const node = d3SimulationRef.value.nodes().find((item) => item.id === nodeId)
    if (node) {
      node.fx = null
      node.fy = null
    }
    d3SimulationRef.value.alpha(0.4).restart()
  }
}

const getGraphSize = () => {
  if (!graphCanvasRef.value) {
    return { width: 800, height: 600 }
  }
    return {
    width: graphCanvasRef.value.clientWidth || graphCanvasRef.value.offsetWidth || 800,
    height: graphCanvasRef.value.clientHeight || graphCanvasRef.value.offsetHeight || 600
  }
}

const setupGraphResizeObserver = () => {
  if (typeof ResizeObserver === 'undefined' || !graphCanvasRef.value) {
    return
  }
  if (graphResizeObserver.value) {
    graphResizeObserver.value.disconnect()
  }
  graphResizeObserver.value = new ResizeObserver(() => {
    resizeD3Graph()
  })
  graphResizeObserver.value.observe(graphCanvasRef.value)
}

const canZoomIn = computed(() => !!d3SvgRef.value)
const canZoomOut = computed(() => !!d3SvgRef.value)
const graphFullscreenIcon = computed(() => (isGraphFullscreen.value ? 'fullscreen_exit' : 'fullscreen'))

const graphEntityOptions = computed(() =>
  displayGraphNodes.value.map((node) => ({
    id: node.id,
    label: `${(node.properties?.entity_type || 'entity').toUpperCase()} • ${node.id}`
  }))
)

const hasGraphData = computed(() => (eventGraphData.value.nodes || []).length > 0)
const graphStatus = computed(() => incident.value?.graphStatus || 'missing')
const isGraphReady = computed(() => graphStatus.value === 'ready' && hasGraphData.value)
const graphStatusLabel = computed(() =>
  t(`incidents.detail.eventGraph.graphStatus.${graphStatus.value}`, graphStatus.value)
)
const graphStatusDotClass = computed(() => {
  if (graphStatus.value === 'ready') {
    return 'bg-emerald-400'
  }
  if (graphStatus.value === 'processing') {
    return 'bg-sky-400'
  }
  if (graphStatus.value === 'error') {
    return 'bg-red-400'
  }
  if (graphStatus.value === 'disabled') {
    return 'bg-slate-500'
  }
  return 'bg-amber-400'
})

const graphLastGeneratedTime = computed(() => {
  // Use last_update_time from incident as per requirement
  const time = incident.value?.lastUpdateTime || incident.value?.graphGeneratedAt
  if (!time) {
    return ''
  }
  return formatDateTime(time)
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

const shouldShowSummaryExpand = computed(() => summaryNeedsTruncate.value)

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

// 图谱中关联度最高的实体 Top 5（用于 impacted assets）
const topImpactedEntities = computed(() => {
  const nodes = eventGraphData.value.nodes || []
  if (!nodes.length) {
    return []
  }
  return nodes
    .map((node) => {
      const id = node.id
      return {
        id,
        label: nodeLabelMap.value[id] || id,
        type: nodeTypeMap.value[id] || (node.properties?.entity_type || 'entity').toLowerCase(),
        degree: nodeDegreeMap.value[id] || 0
      }
    })
    .filter((item) => item.degree > 0)
    .sort((a, b) => b.degree - a.degree)
    .slice(0, 5)
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

const selectedNodeDescription = computed(() => {
  if (!selectedGraphNode.value?.properties?.description) {
    return ''
  }
  return formatNodeDetailValue(selectedGraphNode.value.properties.description)
})

const shouldShowPropertyDescriptionExpand = computed(() => propertyDescriptionNeedsTruncate.value)

const measureSummaryOverflow = () => {
  if (!graphSummaryRef.value || !incident.value?.graphSummary || !isGraphReady.value) {
    summaryNeedsTruncate.value = false
    return
  }
  if (isSummaryExpanded.value) {
    return
  }
  const el = graphSummaryRef.value
  summaryNeedsTruncate.value = el.scrollHeight - el.clientHeight > 2
}

const measurePropertyDescriptionOverflow = () => {
  if (!propertyDescriptionRef.value || !selectedNodeDescription.value) {
    propertyDescriptionNeedsTruncate.value = false
    return
  }
  if (isPropertyDescriptionExpanded.value) {
    return
  }
  const el = propertyDescriptionRef.value
  propertyDescriptionNeedsTruncate.value = el.scrollHeight - el.clientHeight > 2
}

const handleWindowResize = () => {
  measureSummaryOverflow()
  measurePropertyDescriptionOverflow()
  resizeD3Graph()
}



const buildNodeDetailCopyPayload = () => {
  if (!selectedGraphNode.value) {
    return ''
  }
  const node = selectedGraphNode.value
  const lines = []
  lines.push(`ID: ${formatNodeDetailValue(node.id) || '-'}`)
  if (primaryNodeLabel.value) {
    lines.push(`Label: ${formatNodeDetailValue(primaryNodeLabel.value)}`)
  }
  if (node.properties?.entity_type) {
    lines.push(`Entity Type: ${formatNodeDetailValue(node.properties.entity_type)}`)
  }
  if (selectedNodeDescription.value) {
    lines.push(`Description: ${selectedNodeDescription.value}`)
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
  
  // Find all nodes that should be pruned (selected node + all child nodes recursively)
  const nodesToPrune = new Set([selectedGraphNodeId.value])
  const edges = eventGraphData.value.edges || []
  const nodes = baseGraphNodes.value
  
  // Build child adjacency list (only outgoing edges: source -> target)
  const childAdjacencyList = new Map()
  nodes.forEach(node => {
    childAdjacencyList.set(node.id, new Set())
  })
  edges.forEach(edge => {
    const sourceId = typeof edge.source === 'object' ? edge.source.id : edge.source
    const targetId = typeof edge.target === 'object' ? edge.target.id : edge.target
    if (childAdjacencyList.has(sourceId) && childAdjacencyList.has(targetId)) {
      childAdjacencyList.get(sourceId).add(targetId)
    }
  })
  
  // BFS to find all child nodes recursively
  const queue = [selectedGraphNodeId.value]
  const visited = new Set([selectedGraphNodeId.value])
  
  while (queue.length > 0) {
    const currentNodeId = queue.shift()
    const children = childAdjacencyList.get(currentNodeId) || new Set()
    
    for (const childId of children) {
      if (!visited.has(childId) && !prunedNodeIds.value.has(childId)) {
        visited.add(childId)
        nodesToPrune.add(childId)
        queue.push(childId)
      }
    }
  }
  
  // Add all nodes to prune to the pruned set
  const next = new Set(prunedNodeIds.value)
  nodesToPrune.forEach(nodeId => {
    next.add(nodeId)
  })
  prunedNodeIds.value = next
  selectedGraphNodeId.value = ''
  highlightedEntity.value = ''
}

const clearSelectedNode = () => {
  selectedGraphNodeId.value = ''
  highlightedEntity.value = ''
}

const handleGraphContainerClick = (event) => {
  const target = event.target
  setTimeout(() => {
    if (
      selectedGraphNodeId.value &&
      target &&
      (target.tagName === 'CANVAS' || target.tagName === 'svg' || target.tagName === 'SVG')
    ) {
      clearSelectedNode()
      nextTick(() => {
        updateNodeStyles()
      })
    }
  }, 150)
}


const handleGraphBackgroundClick = () => {
  if (resizingNodeDetail.value) {
    return
  }
  clearSelectedNode()
  nextTick(() => {
    updateNodeStyles()
  })
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


const getGraphCenterPoint = () => {
  if (!graphCanvasRef.value) {
    return { x: 0, y: 0 }
  }
  return {
    x: graphCanvasRef.value.clientWidth / 2,
    y: graphCanvasRef.value.clientHeight / 2
  }
}

const zoomGraphByFactor = (factor) => {
  if (!d3SvgRef.value || !d3ZoomBehaviorRef.value) {
    return
  }
  const center = getGraphCenterPoint()
  d3SvgRef.value
    .transition()
    .duration(200)
    .call(d3ZoomBehaviorRef.value.scaleBy, factor, [center.x, center.y])
}

const handleGraphZoomIn = () => {
  zoomGraphByFactor(1 + GRAPH_ZOOM_STEP)
}

const handleGraphZoomOut = () => {
  zoomGraphByFactor(1 / (1 + GRAPH_ZOOM_STEP))
}

const handleGraphResetView = () => {
  selectedGraphNodeId.value = ''
  highlightedEntity.value = ''
  graphSearchQuery.value = ''
  clearAllFixedPositions()
  resetGraphZoom()
  nextTick(() => {
    updateNodeStyles()
  })
}

const fullscreenEventNames = ['fullscreenchange', 'webkitfullscreenchange', 'mozfullscreenchange', 'MSFullscreenChange']
const getGraphFullscreenTarget = () => graphWorkspaceRef.value || graphContainerRef.value

const syncGraphFullscreenState = () => {
  if (typeof document === 'undefined') {
    return
  }
  const fullscreenElement =
    document.fullscreenElement ||
    document.webkitFullscreenElement ||
    document.mozFullScreenElement ||
    document.msFullscreenElement
  const fullscreenTarget = getGraphFullscreenTarget()
  isGraphFullscreen.value = fullscreenTarget ? fullscreenElement === fullscreenTarget : false
  if (isGraphFullscreen.value) {
    nextTick(() => {
      resizeD3Graph()
    })
  }
}

const toggleGraphFullscreen = () => {
  const target = getGraphFullscreenTarget()
  if (!target || typeof document === 'undefined') {
    return
  }
  try {
    if (!isGraphFullscreen.value) {
      const request =
        target.requestFullscreen ||
        target.webkitRequestFullscreen ||
        target.mozRequestFullScreen ||
        target.msRequestFullscreen
      request?.call(target)
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
  downloadGraphSnapshot()
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
  window.removeEventListener('pointermove', handleNodeDetailResize)
  window.removeEventListener('pointerup', stopNodeDetailResize)
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', handleWindowResize)
  }
  if (legendFlashTimer.value) {
    clearTimeout(legendFlashTimer.value)
  }
  if (typeof document !== 'undefined') {
    fullscreenEventNames.forEach((eventName) => document.removeEventListener(eventName, syncGraphFullscreenState))
  }
  destroyD3Graph()
})

watch(
  () => incident.value?.graphSummary,
  () => {
    isSummaryExpanded.value = false
    nextTick(() => {
      measureSummaryOverflow()
    })
  }
)

watch(isSummaryExpanded, (expanded) => {
  if (!expanded) {
    nextTick(() => {
      measureSummaryOverflow()
    })
  }
})

watch(
  selectedNodeDescription,
  () => {
    if (!selectedNodeDescription.value) {
      propertyDescriptionNeedsTruncate.value = false
      return
    }
    nextTick(() => {
      if (!isPropertyDescriptionExpanded.value) {
        measurePropertyDescriptionOverflow()
      }
    })
  }
)

watch(selectedGraphNodeId, () => {
  isPropertyDescriptionExpanded.value = false
  nextTick(() => {
    measurePropertyDescriptionOverflow()
  })
})

watch(isPropertyDescriptionExpanded, (expanded) => {
  if (!expanded) {
    nextTick(() => {
      measurePropertyDescriptionOverflow()
    })
  }
})

watch(
  [() => eventGraphData.value, () => prunedNodeIds.value],
  () => {
    if (hasGraphData.value && displayGraphNodes.value.length > 0) {
      nextTick(() => updateD3Graph())
    } else {
      destroyD3Graph()
    }
  },
  { immediate: true, deep: true }
)

watch(
  hasGraphData,
  (hasData) => {
    if (hasData && graphCanvasRef.value && activeTab.value === 'alertStory') {
      nextTick(() => {
        initD3Graph()
      })
    } else if (!hasData) {
      destroyD3Graph()
    }
  },
  { immediate: true }
)

watch(
  [graphSearchQuery, selectedGraphNodeId],
  () => {
    nextTick(() => {
      updateNodeStyles()
    })
  }
)

// 监听 activeTab 变化，切换到图表标签页时初始化
watch(
  activeTab,
  (newTab) => {
    if (newTab === 'alertStory' && hasGraphData.value) {
      // 使用多次重试，确保 DOM 已渲染
      let retries = 0
      const maxRetries = 10
      const tryInit = () => {
        if (graphCanvasRef.value) {
          const shouldRecreate = !d3SvgRef.value || !isGraphSvgAttached()
          if (shouldRecreate) {
            initD3Graph()
          } else {
            nextTick(() => {
              resizeD3Graph()
            })
          }
        } else if (retries < maxRetries) {
          retries++
          setTimeout(tryInit, 100)
        } else {
          console.warn('Cannot initialize graph after tab switch:', {
            hasRef: !!graphCanvasRef.value,
            hasData: hasGraphData.value
          })
        }
      }
      nextTick(() => {
        tryInit()
      })
    }
    if (newTab === 'alertStory') {
      nextTick(() => {
        measureSummaryOverflow()
        measurePropertyDescriptionOverflow()
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
    if (hasGraphData.value) {
      nextTick(() => updateD3Graph())
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
  { key: 'alertStory', label: 'incidents.detail.tabs.alertStory' },
  { key: 'alerts', label: 'incidents.detail.tabs.alerts' },
  { key: 'assets', label: 'incidents.detail.tabs.assets' },
  { key: 'evidenceResponse', label: 'incidents.detail.tabs.evidenceResponse' }
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

// 按时间排序的关联告警列表（用于 Alert story 左侧时间线）
const associatedAlertsTimeline = computed(() => {
  const list = [...formattedAssociatedAlerts.value]
  list.sort((a, b) => {
    const ta = a.createTime ? new Date(a.createTime).getTime() : 0
    const tb = b.createTime ? new Date(b.createTime).getTime() : 0
    return ta - tb
  })
  return list.map((item) => {
    let severity = 'low'
    if (item.riskLevel === 'fatal' || item.riskLevel === 'high') {
      severity = 'high'
    } else if (item.riskLevel === 'medium') {
      severity = 'medium'
    }
    return {
      ...item,
      severity
    }
  })
})

// Alert timeline 左侧分页（每页默认 5 条，用户可调整）
const timelinePageSizeOptions = [5, 10, 20]
const timelinePageSize = ref(5)
const timelineCurrentPage = ref(1)
const timelineTotalPages = computed(() => {
  const size = timelinePageSize.value || 5
  const total = associatedAlertsTimeline.value.length
  return total > 0 ? Math.ceil(total / size) : 0
})
const paginatedAssociatedAlertsTimeline = computed(() => {
  const size = timelinePageSize.value || 5
  if (!associatedAlertsTimeline.value.length) return []
  const totalPages = timelineTotalPages.value || 1
  const page = Math.min(Math.max(timelineCurrentPage.value, 1), totalPages)
  const start = (page - 1) * size
  const end = start + size
  return associatedAlertsTimeline.value.slice(start, end)
})

// 当页大小或列表长度变化时，自动纠正当前页
watch([timelinePageSize, associatedAlertsTimeline], () => {
  timelineCurrentPage.value = 1
})

// 左右侧面板收起状态（Alert story 布局）
const isLeftPaneCollapsed = ref(false)
const isRightPaneCollapsed = ref(false)

const alarmCount = computed(() => {
  return incident.value?.alarmCount ?? incident.value?.associatedAlerts?.length ?? 0
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
    const graphGeneratedAt =
      data.graph_generated_at ||
      data.graph_last_generated_at ||
      data.graph_generated_time ||
      data.graph_last_generated_time ||
      data.graph_summary_updated_at ||
      data.graph_summary_update_time ||
      data.graph_update_time ||
      data.graph_updated_at ||
      data.graph_last_run_at ||
      data.graph_last_build_time ||
      data.graph_last_refresh_time ||
      data.last_update_time ||
      data.update_time
    const associatedAlerts = data.associated_alerts || data.associatedAlerts || []
    
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
      category: data.category || 'platform',
      rootCause: data.root_cause || '',
      resource_list: data.resource_list || data.resourceList || [],
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
      associatedAlerts,
      alarmCount: associatedAlerts.length,
      graphData: graphPayload,
      graphSummary: data.graph_summary || '',
      graphStatus: data.graph_status || (graphPayload.nodes.length ? 'ready' : 'missing'),
      graphGeneratedAt,
      lastUpdateTime: data.last_update_time || data.update_time
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
    toast.error(t('incidents.detail.comments.postError') || '无法提交评论：事件ID不存在', 'ERROR')
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
    toast.success(t('incidents.detail.comments.postSuccess') || '评论提交成功', 'SUCCESS')
  } catch (error) {
    console.error('Failed to post comment:', error)
    const errorMessage = error?.response?.data?.message || error?.message || t('incidents.detail.comments.postError') || '评论提交失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
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
    fatal: 'bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-200',
    high: 'bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-300',
    medium: 'bg-orange-100 dark:bg-orange-900 text-orange-600 dark:text-orange-300',
    low: 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300',
    tips: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
  }
  return classes[level] || classes.low
}

// 将事件 severity 映射为告警的 risk level（用于复用颜色样式）
const getIncidentRiskLevel = (severity) => {
  if (!severity) return 'low'
  const severityLower = String(severity).toLowerCase().trim()
  const map = {
    fatal: 'fatal',
    critical: 'fatal',
    high: 'high',
    medium: 'medium',
    low: 'low',
    tips: 'tips'
  }
  return map[severityLower] || severityLower
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
      incident.value.graphGeneratedAt = null
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
    toast.success(t('incidents.detail.closeSuccess') || '事件关闭成功', 'SUCCESS')
    
    // 关闭对话框
    closeCloseDialog()
    
    // 重新加载事件详情
    await loadIncidentDetail()
  } catch (error) {
    console.error('Failed to close incident:', error)
    // 显示错误提示
    const errorMessage = error?.response?.data?.message || error?.message || t('incidents.detail.closeError') || '事件关闭失败，请稍后重试'
    toast.error(errorMessage, 'ERROR')
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
  
  const createTime =
    parseToDate(incident.value?.createTime)
    || parseToDate(incident.value?.create_time)
    || parseToDate(incident.value?.occurrenceTime)
    || new Date()

  editIncidentInitialData.value = {
    title: incident.value.name || incident.value.title || '',
    category: incident.value.category || 'platform',
    status: incident.value.status || 'Open',
    createTime,
    close_time: incident.value.closeTime || incident.value.close_time || null,
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

// 处理选中告警（单选和全选使用相同逻辑）
const handleSelectAlerts = (items) => {
  selectedAlerts.value = items.map(alert => alert.id)
}

// 打开解关联对话框
const openDisassociateDialog = () => {
  showDisassociateDialog.value = true
}

// 关闭解关联对话框
const closeDisassociateDialog = () => {
  showDisassociateDialog.value = false
}

// 处理解关联
const handleDisassociate = async () => {
  if (selectedAlerts.value.length === 0 || isDisassociating.value) {
    return
  }

  try {
    isDisassociating.value = true
    
    // 调用解关联接口
    await disassociateAlertsFromIncident(route.params.id, selectedAlerts.value)
    
    toast.success(
      t('incidents.detail.disassociateSuccess', { count: selectedAlerts.value.length }),
      'SUCCESS'
    )
    
    closeDisassociateDialog()
    selectedAlerts.value = []
    associatedAlertsTableRef.value?.clearSelection()
    await loadIncidentDetail()
  } catch (error) {
    console.error('Failed to disassociate alerts:', error)
    const errorMessage = error?.response?.data?.message || 
                        error?.response?.data?.error_message || 
                        error?.message || 
                        t('incidents.detail.disassociateError')
    toast.error(errorMessage, 'ERROR')
  } finally {
    isDisassociating.value = false
  }
}

onMounted(() => {
  loadIncidentDetail()
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', handleWindowResize)
  }
  if (typeof document !== 'undefined') {
    fullscreenEventNames.forEach((eventName) => document.addEventListener(eventName, syncGraphFullscreenState))
    syncGraphFullscreenState()
  }
  nextTick(() => {
    if (hasGraphData.value && activeTab.value === 'alertStory') {
      initD3Graph()
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
  padding: 0.25rem;
  border-radius: 0.375rem;
  color: #cbd5f5;
  transition: background-color 0.2s ease, color 0.2s ease;
  min-height: 2.25rem;
  min-width: 2.25rem;
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

.event-graph-svg {
  width: 100%;
  height: 100%;
  touch-action: none;
  user-select: none;
}

.graph-link {
  stroke: #475569;
  stroke-width: 1.2px;
  stroke-opacity: 0.35;
  transition: stroke 0.2s ease, stroke-width 0.2s ease, opacity 0.2s ease;
}

.graph-link--related {
  stroke: #38bdf8;
  stroke-width: 2px;
  stroke-opacity: 0.9;
}

.graph-link--dimmed {
  opacity: 0.12;
}

.graph-node {
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.graph-node--dimmed {
  opacity: 0.2;
}

.graph-node__label {
  fill: rgba(255, 255, 255, 0.85);
  font-size: 10px;
  pointer-events: none;
  text-transform: none;
}

.graph-node--selected circle {
  stroke: #60a5fa;
  stroke-width: 2.4px;
  filter: drop-shadow(0 0 8px rgba(96, 165, 250, 0.45));
}

.graph-node--related circle {
  stroke: #fbbf24;
  stroke-width: 2px;
}

.graph-node--search-hit circle {
  stroke: #38bdf8;
  stroke-width: 2px;
}

.graph-node:not(.graph-node--dimmed) circle {
  transition: transform 0.2s ease, stroke 0.2s ease, fill-opacity 0.2s ease, opacity 0.2s ease;
}

.graph-node:not(.graph-node--dimmed):hover circle {
  transform: scale(1.06);
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

.graph-regenerate-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1.15rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(248, 113, 113, 0.6);
  background: rgba(248, 113, 113, 0.12);
  color: #fecaca;
  font-size: 0.85rem;
  font-weight: 600;
  transition: background-color 0.25s ease, border-color 0.25s ease, color 0.25s ease, opacity 0.25s ease;
}

.graph-regenerate-btn:hover:not(:disabled) {
  border-color: rgba(248, 113, 113, 0.9);
  background: rgba(248, 113, 113, 0.25);
  color: #fee2e2;
}

.graph-regenerate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.graph-regenerate-btn--loading {
  animation: pulse 1.1s ease-in-out infinite;
}

.graph-status-dot {
  width: 0.4rem;
  height: 0.4rem;
  border-radius: 9999px;
  display: inline-flex;
}

.graph-status-hint {
  /* 顶部分隔线在模板中单独渲染，这里不再设置 border，避免出现“两行虚线”视觉效果 */
  border-top: none;
  padding-top: 0;
  margin-top: 0;
}

.summary-content,
.description-content {
  position: relative;
}

.summary-collapsed {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.description-collapsed {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
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
</style>


