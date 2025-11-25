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
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
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
            {{ severityToNumber(incident?.severity) || '-' }}
          </p>
        </div>
      </div>
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
        <p class="text-slate-300 text-sm font-medium leading-normal">
          {{ $t('incidents.detail.category') }}
        </p>
        <p class="text-white text-xl font-bold leading-tight">
          {{ $t(`incidents.create.category${incident?.category ? incident.category.charAt(0).toUpperCase() + incident.category.slice(1) : 'Platform'}`) }}
        </p>
      </div>
      <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-lg p-4 bg-slate-800/50 border border-slate-700">
        <p class="text-slate-300 text-sm font-medium leading-normal">
          {{ $t('incidents.detail.countOfAlarms') }}
        </p>
        <p class="text-white text-xl font-bold leading-tight">
          {{ alarmCount }}
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
            <div class="space-y-2">
              <h3 class="text-white font-bold text-lg">
                {{ $t('incidents.detail.eventGraph.summaryTitle') }}
              </h3>
              <p
                v-if="graphStatus === 'processing'"
                class="text-slate-400 text-sm"
              >
                {{ translateOr('incidents.detail.eventGraph.graphBuildingMessage', '图谱数据尚未准备完毕，已自动触发 LightRAG 构建，请稍后刷新查看。') }}
              </p>
              <p
                v-else-if="!isGraphReady"
                class="text-slate-400 text-sm"
              >
                {{ translateOr('incidents.detail.eventGraph.summaryUnavailable', '图谱摘要暂不可用') }}
              </p>
            </div>
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
          <template v-if="isGraphReady">
            <div class="space-y-2">
              <div
                v-if="incident?.graphSummary"
                ref="graphSummaryRef"
                class="text-slate-200 leading-relaxed prose prose-invert max-w-none summary-content"
                :class="{ 'summary-collapsed': !isSummaryExpanded }"
                v-html="graphSummaryHtml"
              ></div>
              <p v-else class="text-slate-400 text-sm">
                {{ $t('incidents.detail.eventGraph.summaryPlaceholder') }}
              </p>
              <button
                v-if="incident?.graphSummary && shouldShowSummaryExpand"
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
          </template>
          <div class="graph-status-hint">
            <div class="flex flex-col gap-y-1 text-slate-500 text-xs">
              <div class="flex flex-wrap items-center gap-x-3 gap-y-1">
                <span class="inline-flex items-center gap-1">
                  <span class="graph-status-dot" :class="graphStatusDotClass"></span>
                  <span>{{ graphStatusLabel }}</span>
                </span>
                <span>|</span>
                <span>{{ $t('incidents.detail.eventGraph.lastGenerationTime') }}：{{ graphLastGeneratedTime || '--' }}</span>
              </div>
              <template v-if="isGraphReady">
                <div class="text-slate-500 text-xs">
                  {{
                    $t('incidents.detail.eventGraph.summaryParagraph2', {
                      nodes: eventGraphStats.totalNodes,
                      edges: eventGraphStats.totalEdges,
                      alerts: eventGraphStats.alertNodes,
                      ips: eventGraphStats.ipNodes
                    })
                  }}
                </div>
              </template>
            </div>
          </div>
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
                    <button
                      type="button"
                      class="graph-control-btn"
                      :class="{ 'graph-control-btn--loading': isRefreshingGraph }"
                      :disabled="isRefreshingGraph"
                      :title="$t('incidents.detail.eventGraph.controls.refresh')"
                      @click="handleRefreshGraphStatus"
                    >
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
              <div class="w-full h-full" style="position: relative;" @click="handleGraphContainerClick">
                <div
                  ref="graphCanvasRef"
                  class="w-full h-full"
                  style="min-height: 600px; width: 100%; position: absolute; top: 0; left: 0; right: 0; bottom: 0;"
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
                        <p class="text-sm font-semibold text-white">{{ $t('incidents.detail.eventGraph.nodeDetail.id') }}</p>
                        <p class="text-sm text-slate-200 break-all whitespace-pre-wrap">
                          {{ formatNodeDetailValue(selectedGraphNode.id) }}
                        </p>
                      </div>
                      <div class="flex flex-col gap-1">
                        <p class="text-sm font-semibold text-white">
                          {{ translateOr('incidents.detail.eventGraph.nodeDetail.label', 'Label') }}
                        </p>
                        <p class="text-sm text-slate-200 whitespace-pre-wrap">
                          {{ formatNodeDetailValue(primaryNodeLabel) || '-' }}
                        </p>
                      </div>
                      <div class="flex flex-col gap-1">
                        <p class="text-sm font-semibold text-white">{{ $t('incidents.detail.eventGraph.nodeDetail.entityType') }}</p>
                        <p class="text-sm text-slate-200 whitespace-pre-wrap">
                          {{ formatNodeDetailValue(selectedGraphNode.properties?.entity_type) }}
                        </p>
                      </div>
                    </div>
                    <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-4 space-y-3">
                      <div class="flex flex-col gap-1">
                        <p class="text-sm font-semibold text-white">
                          {{ translateOr('incidents.detail.eventGraph.nodeDetail.propertyDescription', '属性描述') }}
                        </p>
                        <p
                          v-if="selectedNodeDescription"
                          ref="propertyDescriptionRef"
                          class="text-sm text-slate-200 whitespace-pre-wrap description-content"
                          :class="{ 'description-collapsed': !isPropertyDescriptionExpanded }"
                        >
                          {{ selectedNodeDescription }}
                        </p>
                        <p v-else class="text-sm text-slate-500">
                          {{ $t('common.noData') }}
                        </p>
                      </div>
                      <button
                        v-if="selectedNodeDescription && shouldShowPropertyDescriptionExpand"
                        type="button"
                        @click="isPropertyDescriptionExpanded = !isPropertyDescriptionExpanded"
                        class="text-primary hover:text-primary/80 text-sm font-medium flex items-center gap-1 transition-colors"
                      >
                        <span class="material-symbols-outlined text-base">
                          {{ isPropertyDescriptionExpanded ? 'expand_less' : 'expand_more' }}
                        </span>
                        <span>{{ isPropertyDescriptionExpanded ? $t('common.collapse') : $t('common.expand') }}</span>
                      </button>
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
          <div class="p-6 border-b border-[#324867] flex items-center justify-between">
            <h3 class="text-white font-bold text-lg">
              {{ $t('incidents.detail.overview.associatedAlerts') }}
            </h3>
            <button
              :disabled="selectedAlerts.length === 0"
              @click="openDisassociateDialog"
              class="flex items-center justify-center gap-2 rounded-lg h-10 bg-[#233348] text-white text-sm font-bold px-4 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#324867] transition-colors"
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

    <!-- 解关联确认对话框 -->
    <div
      v-if="showDisassociateDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="closeDisassociateDialog"
    >
      <div class="bg-[#111822] border border-[#324867] rounded-lg p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-white">
            {{ $t('incidents.detail.disassociateDialog.title') }}
          </h2>
          <button
            @click="closeDisassociateDialog"
            class="text-gray-400 hover:text-white transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
          </button>
        </div>

        <!-- Prompt message -->
        <div class="mb-6 p-3 bg-[#1e293b] rounded-md">
          <p class="text-sm text-gray-400">
            {{ $t('incidents.detail.disassociateDialog.confirmMessage', { count: selectedAlerts.length }) }}
          </p>
        </div>

        <!-- Action buttons -->
        <div class="flex items-center justify-end gap-3">
          <button
            @click="closeDisassociateDialog"
            class="px-4 py-2 text-sm text-gray-400 bg-[#1e293b] rounded-md hover:bg-primary/30 transition-colors"
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
const activeTab = ref('overview')
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
  const size = Math.min(26 + degree * 2, 48)
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

  const svg = d3
    .select(graphCanvasRef.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('class', 'event-graph-svg')
    .attr('viewBox', `0 0 ${width} ${height}`)
    .style('background', '#0f172a')

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
    .force('link', d3.forceLink().id((node) => node.id))
    .force('charge', d3.forceManyBody().strength(-180))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius((node) => (node.visual?.size || 30) / 2 + 12))

  simulation.on('tick', tickSimulation)
  d3SimulationRef.value = simulation

  setupGraphResizeObserver()
  updateD3Graph({ fitView: true })
}

const updateD3Graph = ({ fitView = false } = {}) => {
  if (!d3SimulationRef.value || !d3ZoomLayerRef.value) {
    if (activeTab.value === 'eventGraph' && hasGraphData.value) {
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

  const nodes = displayGraphNodes.value.map((node) => {
    const visual = buildNodeVisualMeta(node)
    const fixedPosition = fixedNodePositions.value.get(node.id)
    return {
      ...node,
      visual,
      fx: fixedPosition?.x ?? node.fx ?? null,
      fy: fixedPosition?.y ?? node.fy ?? null,
      x: fixedPosition?.x ?? node.x ?? null,
      y: fixedPosition?.y ?? node.y ?? null
    }
  })

  const links = displayGraphEdges.value.map((edge, index) => ({
    ...edge,
    id: edgeIdKey(edge, index)
  }))

  d3SimulationRef.value.nodes(nodes)
  const linkForce = d3SimulationRef.value.force('link')
  
  // 先设置链接，这样 D3 会将 source/target 转换为节点对象
  linkForce.links(links)
  
  // 然后设置距离函数，此时 edge.source 和 edge.target 已经是节点对象
  linkForce
    .distance((edge) => {
      const sourceId = typeof edge.source === 'object' ? edge.source.id : edge.source
      const targetId = typeof edge.target === 'object' ? edge.target.id : edge.target
      const degree =
        (nodeDegreeMap.value[sourceId] || 0) + (nodeDegreeMap.value[targetId] || 0)
      if (degree > 6) return 220
      if (degree > 3) return 160
      return 120
    })
    .strength(0.6)

  d3SimulationRef.value.force(
    'collision',
    d3.forceCollide().radius((node) => (node.visual?.size || 30) / 2 + 12)
  )

  d3SimulationRef.value.alpha(0.9).restart()

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

  nodeEnter
    .append('text')
    .attr('class', 'graph-node__label')
    .attr('x', (d) => (d.visual?.size || 30) / 2 + 6)
    .attr('dy', '0.32em')
    .attr('fill', '#e2e8f0')
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

  // 确保节点有初始位置
  d3NodeSelection.value.attr('transform', (d) => {
    if (d.x == null || d.y == null) {
      // 如果没有位置，设置一个随机初始位置
      d.x = d.x ?? (Math.random() * (getGraphSize().width - 100) + 50)
      d.y = d.y ?? (Math.random() * (getGraphSize().height - 100) + 50)
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
  
  // 如果当前在 Event Graph 标签页，初始化图表
  // 否则等待用户切换到该标签页时再初始化（通过 watch activeTab）
  if (activeTab.value === 'eventGraph') {
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
  if (isGraphFullscreen.value) {
    nextTick(() => {
      resizeD3Graph()
    })
  }
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
    if (hasData && graphCanvasRef.value && activeTab.value === 'eventGraph') {
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
    if (newTab === 'eventGraph' && hasGraphData.value) {
      // 使用多次重试，确保 DOM 已渲染
      let retries = 0
      const maxRetries = 10
      const tryInit = () => {
        if (graphCanvasRef.value) {
          if (!d3SvgRef.value) {
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
    if (newTab === 'eventGraph') {
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
  if (!severity) return 'bg-gray-500'
  const severityLower = String(severity).toLowerCase().trim()
  const classes = {
    fatal: 'bg-red-600',
    critical: 'bg-red-600',
    high: 'bg-red-500',
    medium: 'bg-orange-500',
    low: 'bg-blue-500',
    tips: 'bg-gray-400'
  }
  return classes[severityLower] || classes.low
}

const getSeverityTextClass = (severity) => {
  if (!severity) return 'text-gray-400'
  const severityLower = String(severity).toLowerCase().trim()
  const classes = {
    fatal: 'text-red-400',
    critical: 'text-red-400',
    high: 'text-red-400',
    medium: 'text-orange-400',
    low: 'text-blue-400',
    tips: 'text-gray-400'
  }
  return classes[severityLower] || classes.low
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
    if (hasGraphData.value && activeTab.value === 'eventGraph') {
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
  border-top: 1px dashed rgba(148, 163, 184, 0.25);
  padding-top: 0.6rem;
  margin-top: 0.5rem;
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


