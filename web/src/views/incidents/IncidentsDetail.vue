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
        <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">{{ $t('common.loading') || 'Loading...' }}</p>
      </div>
    </div>
    <!-- 面包屑导航和操作按钮 -->
    <nav class="mb-5 flex items-center justify-between gap-4 flex-wrap">
      <ol class="flex items-center gap-2.5 text-sm">
        <li>
          <router-link
            to="/incidents"
            class="inline-flex items-center gap-1.5 text-gray-500 dark:text-gray-400 hover:text-primary dark:hover:text-primary transition-colors duration-200 font-medium"
          >
            <span class="material-symbols-outlined text-base">folder</span>
            <span>{{ $t('incidents.title') || 'Incidents' }}</span>
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
      <div class="flex gap-3 flex-wrap justify-end">
        <button
          @click="handleRefresh"
          :disabled="loadingIncident"
          class="btn-icon"
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
          @click="openEditDialog"
          class="btn-secondary"
        >
          <span class="material-symbols-outlined text-base">edit</span>
          <span class="truncate">{{ $t('incidents.detail.edit') }}</span>
        </button>
        <button
          @click="openCloseDialog"
          class="btn-primary"
        >
          <span class="material-symbols-outlined text-base">archive</span>
          <span class="truncate">{{ $t('incidents.detail.closeIncident') }}</span>
        </button>
        <button
          @click="handleShare"
          class="btn-icon"
          :title="$t('incidents.detail.share') || 'Share'"
        >
          <span class="material-symbols-outlined text-base">share</span>
        </button>
      </div>
    </nav>
    <!-- 页面标题 -->
    <header class="flex flex-col gap-2 mb-6">
      <h1 class="text-gray-900 dark:text-white text-xl font-bold leading-tight tracking-tight">
        {{ incident?.name }}
      </h1>
      <div class="flex flex-wrap items-center gap-x-4 gap-y-2 text-gray-600 dark:text-slate-400 text-sm">
        <div class="flex items-center gap-1.5">
          <span>{{ $t('incidents.detail.actor') }}:</span>
          <span class="text-gray-900 dark:text-white">{{ incident?.actor }}</span>
        </div>
        <span class="h-4 w-px bg-gray-300 dark:bg-slate-600/50"></span>
        <div class="flex items-center gap-1.5">
          <span>{{ $t('incidents.detail.createTime') }}:</span>
          <span class="text-gray-900 dark:text-white">{{ formatDateTime(incident?.createTime) }}</span>
        </div>
        <span class="h-4 w-px bg-gray-300 dark:bg-slate-600/50"></span>
        <div class="flex items-center gap-1.5">
          <span>{{ $t('incidents.detail.closeTime') }}:</span>
          <span class="text-gray-900 dark:text-white">{{ formatDateTime(incident?.closeTime || incident?.close_time) }}</span>
        </div>
        <span class="h-4 w-px bg-gray-300 dark:bg-slate-600/50"></span>
        <div class="flex items-center gap-1.5">
          <span>{{ $t('incidents.detail.updateTime') }}:</span>
          <span class="text-gray-900 dark:text-white">{{ formatDateTime(incident?.updateTime) }}</span>
        </div>
      </div>
    </header>

    <!-- 顶部统计卡片（已按需求移除） -->

    <!-- 标签页导航 -->
    <div class="mt-8 border-b border-gray-200 dark:border-slate-700">
      <nav aria-label="Tabs" class="flex -mb-px space-x-6">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            'whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === tab.key
              ? 'text-primary border-primary'
              : 'text-gray-500 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white border-transparent'
          ]"
        >
          {{ $t(tab.label) }}
        </button>
      </nav>
    </div>

    <!-- 标签页内容 -->
    <div class="mt-6 flex-grow">
      <!-- Alert story：事件沙盘 -->
      <div v-if="activeTab === 'alertStory'" class="space-y-4">
        <!-- 外层容器沿用 Alerts 模块的卡片风格，但内部线条尽量柔和 -->
        <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867]/70 rounded-xl overflow-hidden">
          <!-- 始终保留整体工作区结构（左右栏 + 中间区域），只根据状态切换中间区域内容 -->
          <!-- 这里使用固定视口高度，保证左侧边框线贯穿整个工作区，避免出现下半部分缺失的问题 -->
          <div
            ref="graphWorkspaceRef"
            class="flex min-h-[600px]"
            style="height: calc(100vh - 200px); max-height: calc(100vh - 200px);"
          >
            <!-- 左侧：告警时间线 / 任务管理 -->
            <aside
              v-if="!isLeftPaneCollapsed"
              class="w-80 flex-none border-r border-gray-200 dark:border-slate-800 bg-white dark:bg-[#111822] flex flex-col h-full"
            >
              <!-- 标签切换头部 -->
              <div class="px-4 py-3 border-b border-gray-200 dark:border-slate-800 bg-gray-50 dark:bg-[#111822]">
                <!-- 标签切换按钮作为标题 -->
                <div class="flex items-center justify-between gap-1">
                  <div class="flex gap-1 flex-1">
                    <button
                      @click="leftPaneActiveTab = 'taskManagement'"
                      :class="[
                        'px-3 py-1.5 text-sm font-semibold transition-colors border-b-2',
                        leftPaneActiveTab === 'taskManagement'
                          ? 'text-primary border-primary'
                          : 'text-gray-900 dark:text-slate-100 border-transparent hover:text-gray-700 dark:hover:text-slate-200'
                      ]"
                    >
                      {{ translateOr('incidents.detail.eventGraph.taskManagement', 'Task Management') }}
                    </button>
                    <button
                      @click="leftPaneActiveTab = 'timeline'"
                      :class="[
                        'px-3 py-1.5 text-sm font-semibold transition-colors border-b-2',
                        leftPaneActiveTab === 'timeline'
                          ? 'text-primary border-primary'
                          : 'text-gray-900 dark:text-slate-100 border-transparent hover:text-gray-700 dark:hover:text-slate-200'
                      ]"
                    >
                      {{ translateOr('incidents.detail.eventGraph.timelineTitle', 'Alert Timeline') }}
                      <span class="ml-1 text-xs text-gray-400 dark:text-slate-500">
                        ({{ associatedAlertsTimeline.length }})
                      </span>
                    </button>
                  </div>
                  <button
                    type="button"
                    class="p-1 rounded text-gray-400 hover:text-gray-700 dark:text-slate-500 dark:hover:text-slate-200 transition-colors"
                    :title="translateOr('incidents.detail.eventGraph.collapseLeftPane', 'Collapse panel')"
                    @click="isLeftPaneCollapsed = true"
                  >
                    <span class="material-symbols-outlined text-base">chevron_left</span>
                  </button>
                </div>
              </div>
              <!-- 内容区域 -->
              <div class="flex-1 overflow-y-auto" style="height: 0;">
                <!-- 任务管理内容 -->
                <div v-if="leftPaneActiveTab === 'taskManagement'" class="p-4 space-y-4">
                  <!-- Warroom选择器：
                       - 初次进入 / 未加载过详情时始终可见
                       - 点击铅笔进入编辑时可见
                       - 只有在已加载出任务详情且未处于编辑状态时才收起 -->
                  <div
                    v-if="isEditingTaskId || !taskDetailLoaded || selectedWarroomIds.length === 0 || loadingTaskDetail"
                    class="space-y-2"
                  >
                    <div class="flex items-center justify-between">
                      <label class="text-xs font-medium text-gray-700 dark:text-slate-300">
                        {{ translateOr('incidents.detail.eventGraph.selectWarroom', '选择Warroom') }}
                      </label>
                    </div>
                    <div class="relative" ref="taskIdDropdownRef">
                      <!-- 搜索输入框和已选标签容器 -->
                      <div
                        class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus-within:ring-2 focus-within:ring-primary/60 focus-within:border-primary/60 min-h-[2.5rem] flex items-center flex-wrap gap-1"
                        @click="toggleTaskIdDropdown"
                      >
                        <!-- 已选中的warroom标签 -->
                        <template v-if="selectedWarroomIds.length > 0">
                          <span
                            v-for="warroomId in selectedWarroomIds"
                            :key="warroomId"
                            class="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded text-xs"
                          >
                            {{ getWarroomName(warroomId) }}
                            <button
                              @click.stop="removeWarroom(warroomId)"
                              class="hover:text-blue-600 dark:hover:text-blue-200"
                            >
                              <span class="material-symbols-outlined text-xs">close</span>
                            </button>
                          </span>
                        </template>
                        <!-- 搜索输入框 -->
                        <input
                          v-if="showTaskIdDropdown"
                          v-model="warroomSearchKeyword"
                          @input="handleWarroomSearch"
                          @click.stop
                          @keydown.escape="showTaskIdDropdown = false"
                          type="text"
                          :placeholder="translateOr('incidents.detail.eventGraph.searchWarroomPlaceholder', '输入关键字搜索WR...')"
                          class="flex-1 min-w-[120px] outline-none bg-transparent text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500"
                        />
                        <!-- 未选中且未展开时的占位符 -->
                        <template v-else-if="selectedWarroomIds.length === 0">
                          <span class="text-gray-400 dark:text-slate-500">
                            {{ translateOr('incidents.detail.eventGraph.warroomPlaceholder', '请从下拉框选择') }}
                          </span>
                        </template>
                        <!-- 下拉箭头图标 -->
                        <span class="material-symbols-outlined text-sm text-gray-400 dark:text-slate-500 ml-auto">
                          {{ showTaskIdDropdown ? 'expand_less' : 'expand_more' }}
                        </span>
                      </div>
                      <!-- 下拉选择列表（多选） -->
                      <div
                        v-if="showTaskIdDropdown"
                        class="absolute z-10 w-full mt-1 bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-600 rounded-lg shadow-lg max-h-60 overflow-y-auto"
                        @mousedown.prevent
                      >
                        <!-- 加载状态 -->
                        <div v-if="loadingProjectList" class="px-3 py-4 text-center text-sm text-gray-500 dark:text-slate-400">
                          {{ translateOr('incidents.detail.eventGraph.loading', '加载中...') }}
                        </div>
                        <!-- 无结果提示 -->
                        <div v-else-if="!loadingProjectList && projectOptions.length === 0" class="px-3 py-4 text-center text-sm text-gray-500 dark:text-slate-400">
                          {{ translateOr('incidents.detail.eventGraph.noWarroomFound', '未找到匹配的WR') }}
                        </div>
                        <!-- 选项列表 -->
                        <div
                          v-for="option in projectOptions"
                          :key="option.value"
                          @click.stop="toggleWarroomSelection(option.value)"
                          :class="[
                            'px-3 py-2 text-sm text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-slate-700 cursor-pointer flex items-center gap-2',
                            isWarroomSelected(option.value) ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                          ]"
                        >
                          <span class="material-symbols-outlined text-sm" v-if="isWarroomSelected(option.value)">
                            check_circle
                          </span>
                          <span class="material-symbols-outlined text-sm text-transparent" v-else>
                            circle
                          </span>
                          {{ option.label }}
                        </div>
                      </div>
                    </div>
                    <button
                      @click="bindWarrooms"
                      :disabled="loadingTaskDetail || selectedWarroomIds.length === 0"
                      class="w-full px-4 py-2 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {{ loadingTaskDetail 
                        ? translateOr('incidents.detail.eventGraph.bindingWarroom', '绑定中...')
                        : translateOr('incidents.detail.eventGraph.bindWarroom', '绑定Warroom') }}
                    </button>
                  </div>
                  <!-- 任务详情（分组显示） -->
                  <div v-if="taskDetailLoaded && groupedTaskDetails && Object.keys(groupedTaskDetails).length > 0 && selectedWarroomIds.length > 0" class="-mt-4 space-y-4">
                    <div class="flex items-center justify-between mb-2 pb-2 border-b border-gray-200 dark:border-slate-700">
                      <div class="text-sm font-bold text-gray-900 dark:text-slate-100">
                        {{ translateOr('incidents.detail.eventGraph.taskDetailTitle', 'Task Detail') }}
                      </div>
                      <button
                        type="button"
                        class="p-0.5 rounded text-gray-400 hover:text-gray-700 dark:text-slate-500 dark:hover:text-slate-200 transition-colors"
                        :title="$t('common.edit')"
                        @click.stop="toggleTaskEdit"
                      >
                        <span class="material-symbols-outlined text-sm leading-none">edit</span>
                      </button>
                    </div>
                    <!-- 按warroom分组显示任务详情 -->
                    <div v-for="(warroomDetail, warroomId) in groupedTaskDetails" :key="warroomId" class="border border-gray-300 dark:border-slate-600 rounded-lg p-3 space-y-2 bg-gray-50 dark:bg-slate-800/50">
                      <!-- Warroom标题和解绑按钮 -->
                      <div class="flex items-center justify-between pb-2 border-b border-gray-300 dark:border-slate-600">
                        <div class="text-xs font-semibold text-gray-900 dark:text-slate-100">
                          {{ getWarroomName(warroomId) }}
                        </div>
                        <button
                          type="button"
                          @click="unbindWarroom(warroomId)"
                          class="px-2 py-1 text-xs text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
                          :title="translateOr('incidents.detail.eventGraph.unbindWarroom', '解绑')"
                        >
                          {{ translateOr('incidents.detail.eventGraph.unbind', '解绑') }}
                        </button>
                      </div>
                      <!-- 该warroom的任务列表 -->
                      <div class="space-y-0">
                        <template v-if="Array.isArray(warroomDetail) && warroomDetail.length > 0">
                          <div
                            v-for="(task, index) in warroomDetail"
                            :key="index"
                            :class="[
                              'py-3',
                              index !== warroomDetail.length - 1 ? 'border-b border-gray-200 dark:border-slate-700' : ''
                            ]"
                          >
                            <div class="space-y-2">
                              <div v-if="task.task_name" class="font-medium text-xs text-gray-900 dark:text-white">{{ task.task_name }}</div>
                              <div v-if="task.owner" class="text-xs text-gray-600 dark:text-slate-400">
                                {{ translateOr('incidents.detail.eventGraph.employeeAccount', 'Employee Account') }}: {{ task.owner }}
                              </div>
                              <div v-if="task.start_time" class="text-xs text-gray-600 dark:text-slate-400">
                                {{ translateOr('incidents.detail.eventGraph.startTime', 'Start Time') }}: {{ formatTaskDateTime(task.start_time) }}
                              </div>
                              <div v-if="task.end_time" class="text-xs text-gray-600 dark:text-slate-400">
                                {{ translateOr('incidents.detail.eventGraph.endTime', 'End Time') }}: {{ formatTaskDateTime(task.end_time) }}
                              </div>
                              <div v-if="task.priority !== undefined && task.priority !== null" class="text-xs text-gray-600 dark:text-slate-400 flex items-center gap-1">
                                <span>{{ translateOr('incidents.detail.eventGraph.priority', 'Priority') }}:</span>
                                <span v-if="getPriorityConfig(task.priority)" class="inline-flex items-center gap-0.5">
                                  <span 
                                    class="material-symbols-outlined text-xs flex-shrink-0"
                                    :class="getPriorityConfig(task.priority)?.iconClass"
                                    style="font-size: 12px;"
                                  >
                                    {{ getPriorityConfig(task.priority)?.icon }}
                                  </span>
                                  <span 
                                    :class="[
                                      'px-1.5 py-0.5 rounded text-xs',
                                      getPriorityConfig(task.priority)?.bgClass,
                                      getPriorityConfig(task.priority)?.textClass
                                    ]"
                                  >
                                    {{ getPriorityConfig(task.priority)?.label }}
                                  </span>
                                </span>
                                <span v-else>{{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.noPriority', '无') }}</span>
                              </div>
                              <div v-if="task.isDone !== undefined && task.isDone !== null" class="text-xs">
                                <span class="text-gray-600 dark:text-slate-400">{{ translateOr('incidents.detail.eventGraph.isDone', 'Status') }}: </span>
                                <span :class="task.isDone === 'true' || task.isDone === true ? 'text-green-600 dark:text-green-400' : 'text-gray-600 dark:text-slate-400'">
                                  {{ task.isDone === 'true' || task.isDone === true ? translateOr('incidents.detail.eventGraph.finished', 'Finished') : translateOr('incidents.detail.eventGraph.unfinished', 'Unfinished') }}
                                </span>
                              </div>
                              <div v-if="task.detail_url" class="mt-2">
                                <a :href="task.detail_url" target="_blank" rel="noopener noreferrer" class="text-xs text-primary hover:underline">
                                  {{ translateOr('incidents.detail.eventGraph.viewDetail', 'View Detail') }}
                                </a>
                              </div>
                            </div>
                          </div>
                        </template>
                        <template v-else-if="warroomDetail.task_list && Array.isArray(warroomDetail.task_list) && warroomDetail.task_list.length > 0">
                          <div
                            v-for="(task, index) in warroomDetail.task_list"
                            :key="index"
                            :class="[
                              'py-3',
                              index !== warroomDetail.task_list.length - 1 ? 'border-b border-gray-200 dark:border-slate-700' : ''
                            ]"
                          >
                            <div class="space-y-2">
                              <div v-if="task.task_name" class="font-medium text-xs text-gray-900 dark:text-white">{{ task.task_name }}</div>
                              <div v-if="task.owner" class="text-xs text-gray-600 dark:text-slate-400">
                                {{ translateOr('incidents.detail.eventGraph.employeeAccount', 'Employee Account') }}: {{ task.owner }}
                              </div>
                              <div v-if="task.start_time" class="text-xs text-gray-600 dark:text-slate-400">
                                {{ translateOr('incidents.detail.eventGraph.startTime', 'Start Time') }}: {{ formatTaskDateTime(task.start_time) }}
                              </div>
                              <div v-if="task.end_time" class="text-xs text-gray-600 dark:text-slate-400">
                                {{ translateOr('incidents.detail.eventGraph.endTime', 'End Time') }}: {{ formatTaskDateTime(task.end_time) }}
                              </div>
                              <div v-if="task.priority !== undefined && task.priority !== null" class="text-xs text-gray-600 dark:text-slate-400 flex items-center gap-1">
                                <span>{{ translateOr('incidents.detail.eventGraph.priority', 'Priority') }}:</span>
                                <span v-if="getPriorityConfig(task.priority)" class="inline-flex items-center gap-0.5">
                                  <span 
                                    class="material-symbols-outlined text-xs flex-shrink-0"
                                    :class="getPriorityConfig(task.priority)?.iconClass"
                                    style="font-size: 12px;"
                                  >
                                    {{ getPriorityConfig(task.priority)?.icon }}
                                  </span>
                                  <span 
                                    :class="[
                                      'px-1.5 py-0.5 rounded text-xs',
                                      getPriorityConfig(task.priority)?.bgClass,
                                      getPriorityConfig(task.priority)?.textClass
                                    ]"
                                  >
                                    {{ getPriorityConfig(task.priority)?.label }}
                                  </span>
                                </span>
                                <span v-else>{{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.noPriority', '无') }}</span>
                              </div>
                              <div v-if="task.isDone !== undefined && task.isDone !== null" class="text-xs">
                                <span class="text-gray-600 dark:text-slate-400">{{ translateOr('incidents.detail.eventGraph.isDone', 'Status') }}: </span>
                                <span :class="task.isDone === 'true' || task.isDone === true ? 'text-green-600 dark:text-green-400' : 'text-gray-600 dark:text-slate-400'">
                                  {{ task.isDone === 'true' || task.isDone === true ? translateOr('incidents.detail.eventGraph.finished', 'Finished') : translateOr('incidents.detail.eventGraph.unfinished', 'Unfinished') }}
                                </span>
                              </div>
                              <div v-if="task.detail_url" class="mt-2">
                                <a :href="task.detail_url" target="_blank" rel="noopener noreferrer" class="text-xs text-primary hover:underline">
                                  {{ translateOr('incidents.detail.eventGraph.viewDetail', 'View Detail') }}
                                </a>
                              </div>
                            </div>
                          </div>
                        </template>
                        <template v-else>
                          <div class="py-3 text-xs text-gray-500 dark:text-slate-400">
                            {{ translateOr('incidents.detail.eventGraph.noTaskData', '暂无任务数据') }}
                          </div>
                        </template>
                      </div>
                    </div>
                  </div>
                  <!-- 向后兼容：单个任务详情显示（当使用旧格式时） -->
                  <div v-else-if="taskDetailLoaded && taskDetail && selectedTaskId && (!groupedTaskDetails || Object.keys(groupedTaskDetails).length === 0) && selectedWarroomIds.length === 0" class="-mt-4 space-y-2">
                    <div class="flex items-center justify-between mb-2 pb-2 border-b border-gray-200 dark:border-slate-700">
                      <div class="text-sm font-bold text-gray-900 dark:text-slate-100">
                        {{ translateOr('incidents.detail.eventGraph.taskDetailTitle', 'Task Detail') }}
                      </div>
                      <button
                        type="button"
                        class="p-0.5 rounded text-gray-400 hover:text-gray-700 dark:text-slate-500 dark:hover:text-slate-200 transition-colors"
                        :title="$t('common.edit')"
                        @click.stop="toggleTaskEdit"
                      >
                        <span class="material-symbols-outlined text-sm leading-none">edit</span>
                      </button>
                    </div>
                    <div>
                      <template v-if="typeof taskDetail === 'object' && taskDetail !== null">
                        <!-- 如果任务详情是数组（task_list），显示所有任务 -->
                        <template v-if="Array.isArray(taskDetail)">
                          <div class="space-y-0">
                            <div
                              v-for="(task, index) in taskDetail"
                              :key="index"
                              :class="[
                                'py-3',
                                index !== taskDetail.length - 1 ? 'border-b border-gray-200 dark:border-slate-700' : ''
                              ]"
                            >
                              <div class="space-y-2">
                                <div v-if="task.task_name" class="font-medium text-xs text-gray-900 dark:text-white">{{ task.task_name }}</div>
                                <div v-if="task.stageName" class="text-xs">
                                  <span class="text-gray-600 dark:text-slate-400">{{ translateOr('incidents.detail.eventGraph.stageName', 'Stage') }}: </span>
                                  <span 
                                    :class="[
                                      'inline-block px-2 py-0.5 rounded text-xs',
                                      task.stageName === '待处理' || task.stageName === 'Pending' 
                                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                                        : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                                    ]"
                                  >
                                    {{ task.stageName }}
                                  </span>
                                </div>
                                <div v-if="task.owner" class="text-xs text-gray-600 dark:text-slate-400">
                                  {{ translateOr('incidents.detail.eventGraph.employeeAccount', 'Employee Account') }}: {{ task.owner }}
                                </div>
                                <div v-if="task.start_time" class="text-xs text-gray-600 dark:text-slate-400">
                                  {{ translateOr('incidents.detail.eventGraph.startTime', 'Start Time') }}: {{ formatTaskDateTime(task.start_time) }}
                                </div>
                                <div v-if="task.end_time" class="text-xs text-gray-600 dark:text-slate-400">
                                  {{ translateOr('incidents.detail.eventGraph.endTime', 'End Time') }}: {{ formatTaskDateTime(task.end_time) }}
                                </div>
                                <div v-if="task.priority !== undefined && task.priority !== null" class="text-xs text-gray-600 dark:text-slate-400">
                                  {{ translateOr('incidents.detail.eventGraph.priority', 'Priority') }}: {{ getPriorityLabel(task.priority) }}
                                </div>
                                <div v-if="task.isDone !== undefined && task.isDone !== null" class="text-xs">
                                  <span class="text-gray-600 dark:text-slate-400">{{ translateOr('incidents.detail.eventGraph.isDone', 'Is Done') }}: </span>
                                  <span :class="task.isDone === 'true' || task.isDone === true ? 'text-green-600 dark:text-green-400' : 'text-gray-600 dark:text-slate-400'">
                                    {{ task.isDone === 'true' || task.isDone === true ? translateOr('incidents.detail.eventGraph.yes', 'Yes') : translateOr('incidents.detail.eventGraph.no', 'No') }}
                                  </span>
                                </div>
                                <div v-if="task.detail_url" class="mt-2">
                                  <a :href="task.detail_url" target="_blank" rel="noopener noreferrer" class="text-xs text-primary hover:underline">
                                    {{ translateOr('incidents.detail.eventGraph.viewDetail', 'View Detail') }}
                                  </a>
                                </div>
                              </div>
                            </div>
                          </div>
                        </template>
                        <!-- 如果任务详情包含 task_list 数组 -->
                        <template v-else-if="taskDetail.task_list && Array.isArray(taskDetail.task_list)">
                          <div class="space-y-0">
                            <div
                              v-for="(task, index) in taskDetail.task_list"
                              :key="index"
                              :class="[
                                'py-3',
                                index !== taskDetail.task_list.length - 1 ? 'border-b border-gray-200 dark:border-slate-700' : ''
                              ]"
                            >
                              <div class="space-y-2">
                                <div v-if="task.task_name" class="font-medium text-xs text-gray-900 dark:text-white">{{ task.task_name }}</div>
                                <div v-if="task.stageName" class="text-xs">
                                  <span class="text-gray-600 dark:text-slate-400">{{ translateOr('incidents.detail.eventGraph.stageName', 'Stage') }}: </span>
                                  <span 
                                    :class="[
                                      'inline-block px-2 py-0.5 rounded text-xs',
                                      task.stageName === '待处理' || task.stageName === 'Pending' 
                                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                                        : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                                    ]"
                                  >
                                    {{ task.stageName }}
                                  </span>
                                </div>
                                <div v-if="task.owner" class="text-xs text-gray-600 dark:text-slate-400">
                                  {{ translateOr('incidents.detail.eventGraph.employeeAccount', 'Employee Account') }}: {{ task.owner }}
                                </div>
                                <div v-if="task.start_time" class="text-xs text-gray-600 dark:text-slate-400">
                                  {{ translateOr('incidents.detail.eventGraph.startTime', 'Start Time') }}: {{ formatTaskDateTime(task.start_time) }}
                                </div>
                                <div v-if="task.end_time" class="text-xs text-gray-600 dark:text-slate-400">
                                  {{ translateOr('incidents.detail.eventGraph.endTime', 'End Time') }}: {{ formatTaskDateTime(task.end_time) }}
                                </div>
                                <div v-if="task.priority !== undefined && task.priority !== null" class="text-xs text-gray-600 dark:text-slate-400">
                                  {{ translateOr('incidents.detail.eventGraph.priority', 'Priority') }}: {{ getPriorityLabel(task.priority) }}
                                </div>
                                <div v-if="task.isDone !== undefined && task.isDone !== null" class="text-xs">
                                  <span class="text-gray-600 dark:text-slate-400">{{ translateOr('incidents.detail.eventGraph.isDone', 'Is Done') }}: </span>
                                  <span :class="task.isDone === 'true' || task.isDone === true ? 'text-green-600 dark:text-green-400' : 'text-gray-600 dark:text-slate-400'">
                                    {{ task.isDone === 'true' || task.isDone === true ? translateOr('incidents.detail.eventGraph.yes', 'Yes') : translateOr('incidents.detail.eventGraph.no', 'No') }}
                                  </span>
                                </div>
                                <div v-if="task.detail_url" class="mt-2">
                                  <a :href="task.detail_url" target="_blank" rel="noopener noreferrer" class="text-xs text-primary hover:underline">
                                    {{ translateOr('incidents.detail.eventGraph.viewDetail', 'View Detail') }}
                                  </a>
                                </div>
                              </div>
                            </div>
                          </div>
                        </template>
                        <!-- 单个任务对象 -->
                        <template v-else>
                          <div class="space-y-0">
                            <!-- 任务名称 -->
                            <div v-if="taskDetail.task_name" class="py-2 border-b border-gray-200 dark:border-slate-700">
                              <div class="text-xs font-semibold text-gray-900 dark:text-white mb-1">
                                {{ translateOr('incidents.detail.eventGraph.taskName', 'Task Name') }}
                              </div>
                              <div class="text-xs text-gray-700 dark:text-slate-300 font-medium">
                                {{ taskDetail.task_name }}
                              </div>
                            </div>
                            <!-- 阶段名称 -->
                            <div v-if="taskDetail.stageName" class="py-2 border-b border-gray-200 dark:border-slate-700">
                              <div class="text-xs font-semibold text-gray-900 dark:text-white mb-1">
                                {{ translateOr('incidents.detail.eventGraph.stageName', 'Stage') }}
                              </div>
                              <span 
                                :class="[
                                  'inline-block px-2 py-0.5 rounded text-xs',
                                  taskDetail.stageName === '待处理' || taskDetail.stageName === 'Pending' 
                                    ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                                    : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                                ]"
                              >
                                {{ taskDetail.stageName }}
                              </span>
                            </div>
                            <!-- 员工账号 -->
                            <div v-if="taskDetail.owner" class="py-2 border-b border-gray-200 dark:border-slate-700">
                              <div class="text-xs font-semibold text-gray-900 dark:text-white mb-1">
                                {{ translateOr('incidents.detail.eventGraph.employeeAccount', 'Employee Account') }}
                              </div>
                              <div class="text-xs text-gray-700 dark:text-slate-300">
                                {{ taskDetail.owner }}
                              </div>
                            </div>
                            <!-- 开始时间 -->
                            <div v-if="taskDetail.start_time" class="py-2 border-b border-gray-200 dark:border-slate-700">
                              <div class="text-xs font-semibold text-gray-900 dark:text-white mb-1">
                                {{ translateOr('incidents.detail.eventGraph.startTime', 'Start Time') }}
                              </div>
                              <div class="text-xs text-gray-700 dark:text-slate-300">
                                {{ formatTaskDateTime(taskDetail.start_time) }}
                              </div>
                            </div>
                            <!-- 结束时间 -->
                            <div v-if="taskDetail.end_time" class="py-2 border-b border-gray-200 dark:border-slate-700">
                              <div class="text-xs font-semibold text-gray-900 dark:text-white mb-1">
                                {{ translateOr('incidents.detail.eventGraph.endTime', 'End Time') }}
                              </div>
                              <div class="text-xs text-gray-700 dark:text-slate-300">
                                {{ formatTaskDateTime(taskDetail.end_time) }}
                              </div>
                            </div>
                            <!-- 优先级 -->
                            <div v-if="taskDetail.priority !== undefined && taskDetail.priority !== null" class="py-2 border-b border-gray-200 dark:border-slate-700">
                              <div class="text-xs font-semibold text-gray-900 dark:text-white mb-1">
                                {{ translateOr('incidents.detail.eventGraph.priority', 'Priority') }}
                              </div>
                              <div v-if="getPriorityConfig(taskDetail.priority)" class="flex items-center">
                                <span 
                                  class="material-symbols-outlined text-sm flex-shrink-0 mr-1"
                                  :class="getPriorityConfig(taskDetail.priority)?.iconClass"
                                  style="font-size: 14px;"
                                >
                                  {{ getPriorityConfig(taskDetail.priority)?.icon }}
                                </span>
                                <span 
                                  :class="[
                                    'text-xs inline-flex items-center gap-1 px-2 py-0.5 rounded',
                                    getPriorityConfig(taskDetail.priority)?.bgClass,
                                    getPriorityConfig(taskDetail.priority)?.textClass
                                  ]"
                                >
                                  {{ getPriorityConfig(taskDetail.priority)?.label }}
                                </span>
                              </div>
                              <div v-else class="text-xs text-gray-700 dark:text-slate-300">
                                {{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.noPriority', '无') }}
                              </div>
                            </div>
                            <!-- 完成状态 -->
                            <div v-if="taskDetail.isDone !== undefined && taskDetail.isDone !== null" class="py-2 border-b border-gray-200 dark:border-slate-700">
                              <div class="text-xs font-semibold text-gray-900 dark:text-white mb-1">
                                {{ translateOr('incidents.detail.eventGraph.isDone', 'Status') }}
                              </div>
                              <span 
                                :class="[
                                  'inline-block px-2 py-0.5 rounded text-xs',
                                  taskDetail.isDone === 'true' || taskDetail.isDone === true
                                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                                    : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                                ]"
                              >
                                {{ taskDetail.isDone === 'true' || taskDetail.isDone === true 
                                  ? translateOr('incidents.detail.eventGraph.finished', 'Finished')
                                  : translateOr('incidents.detail.eventGraph.unfinished', 'Unfinished') }}
                              </span>
                            </div>
                            <!-- 详情链接 -->
                            <div v-if="taskDetail.detail_url" class="py-2">
                              <a
                                :href="taskDetail.detail_url"
                                target="_blank"
                                rel="noopener noreferrer"
                                class="text-xs text-primary hover:underline inline-flex items-center gap-1"
                              >
                                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                                {{ translateOr('incidents.detail.eventGraph.viewDetail', 'View Detail') }}
                              </a>
                            </div>
                          </div>
                        </template>
                      </template>
                      <template v-else>
                        <div class="text-xs text-gray-600 dark:text-slate-400 whitespace-pre-wrap break-words">
                          {{ taskDetail }}
                        </div>
                      </template>
                    </div>
                  </div>
                  <!-- 任务详情错误状态 -->
                  <div
                    v-if="taskDetailError"
                    class="mt-4 p-3 text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 rounded-lg"
                  >
                    {{ taskDetailError }}
                  </div>
                </div>
                <!-- 时间线内容 -->
                <div v-else class="px-4">
                  <div
                    v-for="item in associatedAlertsTimeline"
                    :key="item.id"
                    class="py-2.5 border-b border-gray-100 dark:border-slate-800/70 hover:bg-gray-50 dark:hover:bg-[#1e293b] transition-colors"
                  >
                    <div class="flex items-center gap-2 mb-1">
                      <span
                        :class="[
                          'text-[9px] px-1.5 py-0.5 rounded',
                          getRiskLevelClass(item.riskLevel)
                        ]"
                        :title="$t(`common.severity.${item.riskLevel}`)"
                      >
                        {{ $t(`common.severity.${item.riskLevel}`) }}
                      </span>
                      <span class="text-[11px] text-gray-500 dark:text-slate-400">
                        {{ formatDateTime(item.createTime) }}
                      </span>
                    </div>
                    <h4 class="text-[11px] leading-5 font-medium text-gray-900 dark:text-slate-100 break-words whitespace-normal">
                      <a
                        @click="openAlertDetail(item.id)"
                        class="text-primary hover:underline cursor-pointer"
                        :title="item.title || '-'"
                      >
                        {{ item.title || '-' }}
                      </a>
                    </h4>
                  </div>
                  <div
                    v-if="associatedAlertsTimeline.length === 0"
                    class="py-6 text-center text-xs text-gray-400 dark:text-slate-500"
                  >
                    {{ translateOr('incidents.detail.eventGraph.timelineEmpty', 'No associated alerts') }}
                  </div>
                </div>
              </div>
            </aside>
            <!-- 左侧收起后的小按钮 -->
            <button
              v-if="isLeftPaneCollapsed"
              type="button"
              class="flex items-center justify-center w-4 bg-gray-200 dark:bg-slate-900/70 hover:bg-gray-300 dark:hover:bg-slate-900 text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white transition-colors"
              :title="translateOr('incidents.detail.eventGraph.expandLeftPane', 'Expand alert list')"
              @click="isLeftPaneCollapsed = false"
            >
              <span class="material-symbols-outlined text-base">chevron_right</span>
            </button>

            <!-- 中间：事件沙盘 -->
            <div ref="graphContainerRef" class="flex-1 relative bg-gray-50 dark:bg-[#0f172a] min-h-[600px]">
              <div class="absolute top-4 left-4 right-4 z-10 pointer-events-none">
                <div class="flex flex-col xl:flex-row gap-3 items-start pointer-events-auto text-[13px]" @click.stop>
                  <div class="flex flex-col md:flex-row gap-2.5 flex-1 w-full">
                    <div class="relative w-full md:w-60 flex items-center bg-gray-100 dark:bg-slate-900/70 border border-gray-300 dark:border-slate-700 text-gray-900 dark:text-white rounded-lg pl-2.5 pr-2.5 h-9">
                      <span class="material-symbols-outlined text-gray-500 dark:text-slate-400 text-[18px] mr-1.5">search</span>
                      <input
                        v-model="graphSearchQuery"
                        type="text"
                        class="w-full bg-transparent text-[13px] focus:ring-0 focus:outline-none placeholder:text-gray-400 dark:placeholder:text-slate-500"
                        :placeholder="$t('incidents.detail.eventGraph.filterPlaceholder')"
                      />
                    </div>
                    <div class="relative w-full md:w-60">
                      <select
                        v-model="highlightedEntity"
                        class="w-full h-9 bg-gray-100 dark:bg-slate-900/70 border border-gray-300 dark:border-slate-700 text-gray-900 dark:text-white rounded-lg pl-3.5 pr-8 text-[13px] focus:ring-2 focus:ring-primary/60 focus:border-primary/60 appearance-none"
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
                      <span class="material-symbols-outlined absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-500 dark:text-slate-400 pointer-events-none text-[18px]">expand_more</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-1 bg-gray-100 dark:bg-slate-900/80 border border-gray-300 dark:border-slate-700 rounded-lg px-1 h-9">
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
              <div class="w-full h-full" style="position: relative;" @click="handleGraphContainerClick">
                <!-- 仅在重新生成图谱时遮罩中间图区域，不遮挡左右栏 -->
                <div
                  v-if="isRegeneratingGraph"
                  class="absolute inset-0 bg-white/75 dark:bg-[#111822]/75 backdrop-blur-sm z-20 flex items-center justify-center"
                >
                  <div class="flex flex-col items-center gap-3">
                    <div class="relative w-10 h-10">
                      <div class="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
                      <div class="absolute inset-0 border-4 border-transparent border-t-primary rounded-full animate-spin"></div>
                    </div>
                    <p class="text-gray-600 dark:text-gray-400 text-xs font-medium">
                      {{ translateOr('incidents.detail.eventGraph.regeneratingGraph', '正在重新生成图谱...') }}
                    </p>
                  </div>
                </div>
                <!-- 有图数据时渲染 D3 画布；否则在中间区域显示空状态，占位但保留左右栏 -->
                <div
                  v-if="hasGraphData"
                  ref="graphCanvasRef"
                  class="w-full h-full"
                  style="min-height: 600px; width: 100%; position: absolute; top: 0; left: 0; right: 0; bottom: 0;"
                ></div>
                <div
                  v-else
                  class="w-full h-full flex items-center justify-center p-10"
                >
                  <svg
                    class="w-24 h-24 text-gray-400 dark:text-slate-600/80"
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
              <div
                class="absolute bottom-0 left-0 right-0 bg-white dark:bg-[#111822] border-t border-l border-gray-200 dark:border-slate-800 px-4 py-2.5 text-[11px] text-gray-700 dark:text-slate-300 flex items-center gap-2 flex-wrap z-10"
              >
                <span class="graph-status-dot" :class="graphStatusDotClass"></span>
                <span class="font-semibold whitespace-nowrap">
                  {{ graphStatusLabel }}
                </span>
                <span class="text-gray-400 dark:text-slate-600">|</span>
                <span class="whitespace-nowrap">
                  {{ translateOr('incidents.detail.eventGraph.lastGenerationTime', '上次生成时间') }}: {{ graphLastGeneratedTime || '--' }}
                </span>
                <span class="whitespace-nowrap ml-auto">
                  {{ translateOr('incidents.detail.eventGraph.entityCount', '实体个数') }}: {{ eventGraphStats.totalNodes ?? 0 }}
                </span>
                <span class="text-gray-400 dark:text-slate-600">|</span>
                <span class="whitespace-nowrap">
                  {{ translateOr('incidents.detail.eventGraph.relationCount', '关系个数') }}: {{ eventGraphStats.totalEdges ?? 0 }}
                </span>
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
                  :title="translateOr('incidents.detail.eventGraph.collapseRightPane', 'Collapse information panel')"
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
                    class="bg-gray-50 dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl p-4 space-y-3 shadow-sm"
                  >
                    <div class="flex items-center justify-between mb-1">
                      <h4 class="text-xs font-bold text-gray-900 dark:text-slate-100 uppercase tracking-wide">
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
                        <p class="text-xs font-semibold text-gray-600 dark:text-slate-300">
                          {{ $t('incidents.detail.eventGraph.nodeDetail.id') }}
                        </p>
                        <p class="text-xs text-gray-900 dark:text-slate-100 break-all whitespace-pre-wrap">
                          {{ formatNodeDetailValue(selectedGraphNode.id) }}
                        </p>
                      </div>
                      <div class="flex flex-col gap-1">
                        <p class="text-xs font-semibold text-gray-600 dark:text-slate-300">
                          {{ translateOr('incidents.detail.eventGraph.nodeDetail.label', 'Label') }}
                        </p>
                        <p class="text-xs text-gray-900 dark:text-slate-100 whitespace-pre-wrap">
                          {{ formatNodeDetailValue(primaryNodeLabel) || '-' }}
                        </p>
                      </div>
                      <div class="flex flex-col gap-1">
                        <p class="text-xs font-semibold text-gray-600 dark:text-slate-300">
                          {{ $t('incidents.detail.eventGraph.nodeDetail.entityType') }}
                        </p>
                        <p class="text-xs text-gray-900 dark:text-slate-100 whitespace-pre-wrap">
                          {{ formatNodeDetailValue(selectedGraphNode.properties?.entity_type) }}
                        </p>
                      </div>
                      <div class="flex flex-col gap-1">
                        <p class="text-xs font-semibold text-gray-600 dark:text-slate-300">
                          {{ translateOr('incidents.detail.eventGraph.nodeDetail.propertyDescription', 'Property Description') }}
                        </p>
                        <p
                          v-if="selectedNodeDescription"
                          class="text-xs text-gray-900 dark:text-slate-100 whitespace-pre-wrap"
                        >
                          {{ selectedNodeDescription }}
                        </p>
                        <p
                          v-else
                          class="text-xs text-gray-500 dark:text-slate-500 italic whitespace-pre-wrap"
                        >
                          {{ translateOr('incidents.detail.eventGraph.nodeDetail.propertyDescriptionPlaceholder', 'No property description') }}
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
              v-if="isRightPaneCollapsed"
              type="button"
              class="flex items-center justify-center w-4 bg-gray-200 dark:bg-slate-900/70 hover:bg-gray-300 dark:hover:bg-slate-900 text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white transition-colors"
              :title="translateOr('incidents.detail.eventGraph.expandRightPane', 'Expand information panel')"
              @click="isRightPaneCollapsed = false"
            >
              <span class="material-symbols-outlined text-base">chevron_left</span>
            </button>
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
                  :title="$t('alerts.list.openInNewWindow') || 'Open in new window'"
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
            <template #cell-aiJudge="{ item }">
              <div class="flex items-center gap-2 flex-wrap">
                <span
                  v-if="item.verification_state === 'True_Positive'"
                  class="material-symbols-outlined text-red-500 flex-shrink-0"
                  style="font-size: 20px; font-variation-settings: 'FILL' 1, 'wght' 600, 'GRAD' 200, 'opsz' 24;"
                  :title="$t('alerts.list.aiJudge') + ': ' + $t('alerts.list.aiJudgeResult.truePositive')"
                >
                  Input_circle
                </span>
                <span
                  v-else-if="item.verification_state === 'False_Positive'"
                  class="material-symbols-outlined text-green-500 flex-shrink-0"
                  style="font-size: 20px; font-variation-settings: 'FILL' 1, 'wght' 600, 'GRAD' 200, 'opsz' 24;"
                  :title="$t('alerts.list.aiJudge') + ': ' + $t('alerts.list.aiJudgeResult.falsePositive')"
                >
                  output_circle
                </span>
                <span
                  v-else
                  class="material-symbols-outlined text-gray-400 flex-shrink-0"
                  style="font-size: 20px; font-variation-settings: 'FILL' 1, 'wght' 600, 'GRAD' 200, 'opsz' 24;"
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
            <template #cell-actor="{ value }">
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
              {{ translateOr('common.noData', 'No data') }}
            </div>
          </div>
        </div>
      </div>

      <!-- Evidence & Response 标签页：响应流程 -->
      <div v-else-if="activeTab === 'evidenceResponse'" class="flex-grow flex flex-col gap-6">
        <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-border-dark rounded-xl shadow-sm flex flex-col overflow-hidden">
          <!-- 顶部Header -->
          <header class="bg-white dark:bg-surface-dark border-b border-gray-200 dark:border-border-dark px-6 py-4 flex items-center justify-between sticky top-0 z-10">
            <h1 class="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <span class="material-symbols-outlined text-primary">analytics</span>
              {{ $t('incidents.detail.evidenceResponse.title') }}
            </h1>
            <div class="flex items-center gap-3">
              <button class="px-3 py-1.5 text-sm font-medium border border-gray-300 dark:border-border-dark rounded bg-white dark:bg-transparent hover:bg-gray-50 dark:hover:bg-surface-hover-dark text-slate-700 dark:text-slate-300 transition-colors">
                {{ $t('incidents.detail.evidenceResponse.welinkGroup') }}
              </button>
              <button class="px-3 py-1.5 text-sm font-medium border border-gray-300 dark:border-border-dark rounded bg-white dark:bg-transparent hover:bg-gray-50 dark:hover:bg-surface-hover-dark text-slate-700 dark:text-slate-300 transition-colors">
                {{ $t('incidents.detail.evidenceResponse.emergencyReport') }}
              </button>
              <div class="relative group">
                <button class="px-3 py-1.5 text-sm font-medium border border-gray-300 dark:border-border-dark rounded bg-gray-100 dark:bg-surface-hover-dark text-slate-500 dark:text-slate-400 cursor-not-allowed flex items-center gap-1">
                  {{ $t('incidents.detail.evidenceResponse.updateStatus') }}
                  <span class="material-symbols-outlined text-sm">refresh</span>
                </button>
              </div>
            </div>
          </header>

          <main class="flex-1 p-6 overflow-y-auto bg-white dark:bg-[#111822]">
          <!-- 响应指标区域 -->
          <div class="mb-8 pb-8 border-b border-gray-200 dark:border-border-dark">
            <h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-6">响应指标</h2>
            <!-- 指标卡片网格 -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <!-- 指标1: 平均攻击溯源时间 -->
              <div class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border border-blue-200 dark:border-blue-800/30 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                <div class="flex items-start justify-between mb-4">
                  <div class="flex-1">
                    <h3 class="font-bold text-lg text-primary dark:text-blue-400 mb-1">
                      {{ $t('incidents.detail.evidenceResponse.metrics.averageAttackTracingTime') }}
                    </h3>
                    <p class="text-sm text-slate-500 dark:text-slate-400">
                      {{ $t('incidents.detail.evidenceResponse.metrics.mttTracing') }}
                    </p>
                  </div>
                  <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-blue-500/10 dark:bg-blue-500/20">
                    <span class="material-symbols-outlined text-blue-600 dark:text-blue-400 text-2xl">search</span>
                  </div>
                </div>
                <div class="flex items-baseline gap-2">
                  <span class="text-3xl font-bold text-slate-900 dark:text-white">{{ metricsData.mttTracing || '--' }}</span>
                  <span class="text-sm text-slate-500 dark:text-slate-400">{{ $t('incidents.detail.evidenceResponse.metrics.unit') }}</span>
                </div>
              </div>

              <!-- 指标2: 平均攻击源拦截时间 -->
              <div class="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border border-green-200 dark:border-green-800/30 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                <div class="flex items-start justify-between mb-4">
                  <div class="flex-1">
                    <h3 class="font-bold text-lg text-emerald-700 dark:text-emerald-400 mb-1">
                      {{ $t('incidents.detail.evidenceResponse.metrics.averageAttackBlockingTime') }}
                    </h3>
                    <p class="text-sm text-slate-500 dark:text-slate-400">
                      {{ $t('incidents.detail.evidenceResponse.metrics.mttBlocking') }}
                    </p>
                  </div>
                  <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-green-500/10 dark:bg-green-500/20">
                    <span class="material-symbols-outlined text-green-600 dark:text-green-400 text-2xl">shield</span>
                  </div>
                </div>
                <div class="flex items-baseline gap-2">
                  <span class="text-3xl font-bold text-slate-900 dark:text-white">{{ metricsData.mttBlocking || '--' }}</span>
                  <span class="text-sm text-slate-500 dark:text-slate-400">{{ $t('incidents.detail.evidenceResponse.metrics.unit') }}</span>
                </div>
              </div>

              <!-- 指标3: 平均风险消减时间 -->
              <div class="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 border border-orange-200 dark:border-orange-800/30 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                <div class="flex items-start justify-between mb-4">
                  <div class="flex-1">
                    <h3 class="font-bold text-lg text-orange-700 dark:text-orange-400 mb-1">
                      {{ $t('incidents.detail.evidenceResponse.metrics.averageRiskMitigationTime') }}
                    </h3>
                    <p class="text-sm text-slate-500 dark:text-slate-400">
                      {{ $t('incidents.detail.evidenceResponse.metrics.mttr') }}
                    </p>
                  </div>
                  <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-orange-500/10 dark:bg-orange-500/20">
                    <span class="material-symbols-outlined text-orange-600 dark:text-orange-400 text-2xl">trending_down</span>
                  </div>
                </div>
                <div class="flex items-baseline gap-2">
                  <span class="text-3xl font-bold text-slate-900 dark:text-white">{{ metricsData.mttr || '--' }}</span>
                  <span class="text-sm text-slate-500 dark:text-slate-400">{{ $t('incidents.detail.evidenceResponse.metrics.unit') }}</span>
                </div>
              </div>

              <!-- 指标4: 平均漏洞入口定位时间 -->
              <div class="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border border-purple-200 dark:border-purple-800/30 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                <div class="flex items-start justify-between mb-4">
                  <div class="flex-1">
                    <h3 class="font-bold text-lg text-indigo-700 dark:text-indigo-400 mb-1">
                      {{ $t('incidents.detail.evidenceResponse.metrics.averageVulnerabilityEntryTime') }}
                    </h3>
                    <p class="text-sm text-slate-500 dark:text-slate-400">
                      {{ $t('incidents.detail.evidenceResponse.metrics.mttVulnerabilityEntry') }}
                    </p>
                  </div>
                  <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-purple-500/10 dark:bg-purple-500/20">
                    <span class="material-symbols-outlined text-purple-600 dark:text-purple-400 text-2xl">bug_report</span>
                  </div>
                </div>
                <div class="flex items-baseline gap-2">
                  <span class="text-3xl font-bold text-slate-900 dark:text-white">{{ metricsData.mttVulnerabilityEntry || '--' }}</span>
                  <span class="text-sm text-slate-500 dark:text-slate-400">{{ $t('incidents.detail.evidenceResponse.metrics.unit') }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 三个统计卡片 -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <!-- 影响服务卡片 -->
            <button 
              @click="activeCardTab = 'impactedServices'"
              :class="[
                'text-left rounded-lg p-5 relative group shadow-sm hover:shadow-md transition-all focus:outline-none cursor-pointer',
                activeCardTab === 'impactedServices'
                  ? 'bg-blue-50 dark:bg-blue-900/20 border border-primary'
                  : 'bg-white dark:bg-surface-dark border border-gray-200 dark:border-border-dark hover:border-slate-400 dark:hover:border-slate-500 hover:bg-gray-50 dark:hover:bg-surface-hover-dark'
              ]">
              <div class="flex items-start gap-4">
                <div class="p-3 bg-yellow-400/20 rounded-full text-yellow-600 dark:text-yellow-400 flex-shrink-0">
                  <span class="material-symbols-outlined text-2xl">warning</span>
                </div>
                <div>
                  <h3 :class="[
                    'font-bold text-lg',
                    activeCardTab === 'impactedServices' 
                      ? 'text-primary dark:text-blue-400' 
                      : 'text-slate-900 dark:text-white'
                  ]">{{ $t('incidents.detail.evidenceResponse.cards.impactedServices.title') }}</h3>
                  <p class="text-sm text-slate-600 dark:text-slate-400 mt-1">
                    改进措施个数 {{ impactedServicesStats.total }} | 已完成 {{ impactedServicesStats.completed }} | 未完成 {{ impactedServicesStats.uncompleted }}
                  </p>
                </div>
              </div>
              <div v-if="activeCardTab === 'impactedServices'" class="absolute -bottom-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-blue-50 dark:bg-[#152342] border-r border-b border-primary transform rotate-45"></div>
            </button>

            <!-- 进展同步卡片 -->
            <button 
              @click="activeCardTab = 'progressSync'"
              :class="[
                'text-left rounded-lg p-5 relative group shadow-sm hover:shadow-md transition-all focus:outline-none cursor-pointer',
                activeCardTab === 'progressSync'
                  ? 'bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-500'
                  : 'bg-white dark:bg-surface-dark border border-gray-200 dark:border-border-dark hover:border-slate-400 dark:hover:border-slate-500 hover:bg-gray-50 dark:hover:bg-surface-hover-dark'
              ]">
              <div class="flex items-start gap-4">
                <div class="p-3 bg-emerald-100 dark:bg-emerald-900/20 rounded-full text-emerald-600 dark:text-emerald-400 flex-shrink-0">
                  <span class="material-symbols-outlined text-2xl">sync</span>
                </div>
                <div>
                  <h3 :class="[
                    'font-bold text-lg',
                    activeCardTab === 'progressSync' 
                      ? 'text-emerald-700 dark:text-emerald-400' 
                      : 'text-slate-900 dark:text-white'
                  ]">{{ $t('incidents.detail.evidenceResponse.cards.progressSync.title') }}</h3>
                  <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
                    指令个数 {{ progressSyncMetrics.total }} | 已完成 {{ progressSyncMetrics.completed }} | 未完成 {{ progressSyncMetrics.uncompleted }}
                  </p>
                </div>
              </div>
              <div v-if="activeCardTab === 'progressSync'" class="absolute -bottom-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-emerald-50 dark:bg-[#152342] border-r border-b border-emerald-500 transform rotate-45"></div>
            </button>

            <!-- 事件简报卡片 -->
            <button 
              @click="activeCardTab = 'incidentBrief'"
              :class="[
                'text-left rounded-lg p-5 relative group shadow-sm hover:shadow-md transition-all focus:outline-none cursor-pointer',
                activeCardTab === 'incidentBrief'
                  ? 'bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-500'
                  : 'bg-white dark:bg-surface-dark border border-gray-200 dark:border-border-dark hover:border-slate-400 dark:hover:border-slate-500 hover:bg-gray-50 dark:hover:bg-surface-hover-dark'
              ]">
              <div class="flex items-start gap-4">
                <div class="p-3 bg-indigo-100 dark:bg-indigo-900/20 rounded-full text-indigo-600 dark:text-indigo-400 flex-shrink-0">
                  <span class="material-symbols-outlined text-2xl">article</span>
                </div>
                <div>
                  <h3 :class="[
                    'font-bold text-lg',
                    activeCardTab === 'incidentBrief' 
                      ? 'text-indigo-700 dark:text-indigo-400' 
                      : 'text-slate-900 dark:text-white'
                  ]">{{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.title') }}</h3>
                  <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
                    通报 {{ incidentBriefStats.notifications }} | 日报 {{ incidentBriefStats.dailyReports }}
                  </p>
                </div>
              </div>
              <div v-if="activeCardTab === 'incidentBrief'" class="absolute -bottom-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-indigo-50 dark:bg-[#152342] border-r border-b border-indigo-500 transform rotate-45"></div>
            </button>
          </div>

          <!-- 更新时间 -->
          <div class="flex items-center justify-end mb-4">
            <span class="text-xs text-slate-500 dark:text-slate-400">{{ $t('incidents.detail.evidenceResponse.services.updateTime') }}: {{ formatDateTime(incident?.updateTime) }}</span>
          </div>

          <!-- 影响服务内容 -->
          <template v-if="activeCardTab === 'impactedServices'">
            <!-- 操作按钮 -->
            <div class="flex gap-2 mb-4">
              <button 
                @click="showAddServiceDialog = true"
                class="px-4 py-1.5 text-sm bg-primary text-white rounded hover:bg-primary/90 transition-colors">
                {{ $t('incidents.detail.evidenceResponse.services.add') }}
              </button>
              <button class="px-4 py-1.5 text-sm bg-gray-100 dark:bg-surface-hover-dark text-slate-400 dark:text-slate-500 border border-gray-200 dark:border-border-dark rounded cursor-not-allowed">
                {{ $t('incidents.detail.evidenceResponse.services.batchAdd') }}
              </button>
            </div>

            <!-- 受影响服务表格 -->
            <div class="bg-white dark:bg-surface-dark border border-gray-200 dark:border-border-dark rounded-lg overflow-hidden shadow-sm mb-6">
              <div class="overflow-x-auto">
                <table class="w-full text-sm text-left">
                  <thead class="bg-gray-50 dark:bg-[#1e293b] text-slate-600 dark:text-slate-300 font-medium border-b border-gray-200 dark:border-border-dark">
                    <tr>
                      <th class="px-4 py-3">{{ $t('incidents.detail.evidenceResponse.services.columns.service') }}</th>
                      <th class="px-4 py-3">{{ $t('incidents.detail.evidenceResponse.services.columns.measure') }}</th>
                      <th class="px-4 py-3">{{ $t('incidents.detail.evidenceResponse.services.columns.sla') }}</th>
                      <th class="px-4 py-3">{{ $t('incidents.detail.evidenceResponse.services.columns.plannedCompletionTime') }}</th>
                      <th class="px-4 py-3">{{ $t('incidents.detail.evidenceResponse.services.columns.owner') }}</th>
                      <th class="px-4 py-3">{{ $t('incidents.detail.evidenceResponse.services.columns.progress') }}</th>
                      <th class="px-4 py-3">{{ $t('incidents.detail.evidenceResponse.services.columns.remark') }}</th>
                      <th class="px-4 py-3">操作</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200 dark:divide-border-dark">
                    <template v-if="impactedServices.length > 0">
                      <tr 
                        v-for="(service, index) in impactedServices" 
                        :key="index"
                        class="bg-white dark:bg-surface-dark hover:bg-gray-50 dark:hover:bg-surface-hover-dark/50 transition-colors">
                        <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">{{ service.service || '--' }}</td>
                        <td class="px-4 py-3 text-slate-500 dark:text-slate-400">{{ service.measure || '--' }}</td>
                        <td class="px-4 py-3 text-slate-500 dark:text-slate-400">{{ service.sla || '--' }}</td>
                        <td class="px-4 py-3 text-slate-500 dark:text-slate-400">
                          {{ formatServiceDateTime(service.plannedCompletionTime) }}
                        </td>
                        <td class="px-4 py-3 text-slate-500 dark:text-slate-400">{{ service.owner || '--' }}</td>
                        <td class="px-4 py-3">
                          <span 
                            :class="service.progress === '已完成' 
                              ? 'text-green-600 dark:text-green-400' 
                              : service.progress === '未完成'
                              ? 'text-orange-600 dark:text-orange-400'
                              : 'text-slate-500 dark:text-slate-400'">
                            {{ service.progress || '--' }}
                          </span>
                        </td>
                        <td class="px-4 py-3 text-slate-500 dark:text-slate-400">{{ service.remark || '--' }}</td>
                        <td class="px-4 py-3">
                          <div class="flex items-center gap-2">
                            <button
                              @click="editService(index)"
                              class="text-primary hover:text-primary-hover transition-colors"
                              title="编辑"
                            >
                              <span class="material-symbols-outlined text-base">edit</span>
                            </button>
                            <button
                              @click="deleteService(index)"
                              class="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 transition-colors"
                              :title="$t('common.delete')"
                            >
                              <span class="material-symbols-outlined text-base">delete</span>
                            </button>
                          </div>
                        </td>
                      </tr>
                    </template>
                    <tr v-else class="bg-white dark:bg-surface-dark">
                      <td colspan="8" class="px-4 py-8 text-center text-slate-500 dark:text-slate-400">
                        {{ $t('common.noData') }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </template>

          <!-- 进展同步内容 -->
          <template v-if="activeCardTab === 'progressSync'">
            <!-- 功能键 -->
            <div class="flex gap-2 mb-4 flex-wrap items-center">
              <button 
                @click="progressSyncFilterType = 'myCreated'"
                :class="[
                  'px-4 py-1.5 text-sm rounded transition-colors',
                  progressSyncFilterType === 'myCreated'
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 dark:bg-surface-hover-dark text-slate-700 dark:text-slate-300 border border-gray-200 dark:border-border-dark hover:bg-gray-200 dark:hover:bg-surface-hover-dark'
                ]">
                {{ translateOr('incidents.detail.evidenceResponse.progressSync.filters.myCreated', '我创建的指令') }}
              </button>
              <button 
                @click="progressSyncFilterType = 'myPending'"
                :class="[
                  'px-4 py-1.5 text-sm rounded transition-colors',
                  progressSyncFilterType === 'myPending'
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 dark:bg-surface-hover-dark text-slate-700 dark:text-slate-300 border border-gray-200 dark:border-border-dark hover:bg-gray-200 dark:hover:bg-surface-hover-dark'
                ]">
                {{ translateOr('incidents.detail.evidenceResponse.progressSync.filters.myPending', '待我处理的指令') }}
              </button>
              <button 
                @click="progressSyncFilterType = 'all'"
                :class="[
                  'px-4 py-1.5 text-sm rounded transition-colors',
                  progressSyncFilterType === 'all'
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 dark:bg-surface-hover-dark text-slate-700 dark:text-slate-300 border border-gray-200 dark:border-border-dark hover:bg-gray-200 dark:hover:bg-surface-hover-dark'
                ]">
                {{ translateOr('incidents.detail.evidenceResponse.progressSync.filters.all', '全部指令') }}
              </button>
              <!-- 标签过滤 -->
              <div class="flex items-center gap-2 ml-2">
                <span class="text-sm text-slate-600 dark:text-slate-400 whitespace-nowrap">{{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.tag', '标签') }}:</span>
                <select
                  v-model="progressSyncTagFilter"
                  class="px-3 py-1.5 text-sm border border-gray-300 dark:border-border-dark rounded focus:outline-none focus:ring-2 focus:ring-primary dark:bg-surface-dark dark:text-white"
                >
                  <option value="">{{ translateOr('incidents.detail.evidenceResponse.progressSync.filters.allTags', '全部标签') }}</option>
                  <option value="attackTracing">{{ $t('common.commentTypes.attackTracing', '攻击溯源') }}</option>
                  <option value="attackBlocking">{{ $t('common.commentTypes.attackBlocking', '攻击拦截') }}</option>
                  <option value="riskMitigation">{{ $t('common.commentTypes.riskMitigation', '风险消减') }}</option>
                  <option value="vulnerabilityIdentification">{{ $t('common.commentTypes.vulnerabilityIdentification', '漏洞定位') }}</option>
                </select>
              </div>
              <button 
                @click="createNewTask"
                class="px-4 py-1.5 text-sm bg-primary text-white rounded hover:bg-primary/90 transition-colors ml-auto">
                {{ translateOr('incidents.detail.evidenceResponse.progressSync.createInstruction', '创建指令') }}
              </button>
            </div>

            <!-- 进展同步表格 -->
            <div class="bg-white dark:bg-surface-dark border border-gray-200 dark:border-border-dark rounded-lg overflow-hidden shadow-sm mb-6">
              <div class="overflow-hidden">
                <table class="w-full text-sm text-left" style="table-layout: auto;">
                  <thead class="bg-gray-50 dark:bg-[#1e293b] text-slate-600 dark:text-slate-300 font-medium border-b border-gray-200 dark:border-border-dark">
                    <tr>
                      <th class="px-4 py-3 w-28">{{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.warroom', 'Warroom') }}</th>
                      <th class="px-4 py-3 max-w-[280px]">{{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.taskName', '任务名称') }}</th>
                      <th class="px-4 py-3 w-24">{{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.owner', '责任人') }}</th>
                      <th class="px-4 py-3 w-36">{{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.startTime', '开始时间') }}</th>
                      <th class="px-4 py-3 w-36">{{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.endTime', '结束时间') }}</th>
                      <th class="px-4 py-3 w-32">{{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.priority', '优先级') }}</th>
                      <th class="px-4 py-3 w-32">{{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.status', '状态') }}</th>
                      <th class="px-4 py-3 min-w-[120px]">{{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.tag', '标签') }}</th>
                      <th class="px-4 py-3 w-32 whitespace-nowrap">{{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.viewDetail', '查看详情') }}</th>
                      <th class="px-4 py-3 w-24 whitespace-nowrap">{{ $t('common.action') }}</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200 dark:divide-border-dark">
                    <template v-if="filteredProgressSyncTasks.length > 0">
                      <tr 
                        v-for="(task, index) in filteredProgressSyncTasks" 
                        :key="getTaskUniqueId(task, index)"
                        class="bg-white dark:bg-surface-dark hover:bg-gray-50 dark:hover:bg-surface-hover-dark/50 transition-colors">
                        <!-- WR名字 -->
                        <td class="px-4 py-3 text-slate-500 dark:text-slate-400">{{ task.warroomName || '--' }}</td>
                        <!-- 任务名称 -->
                        <td class="px-4 py-3 max-w-[280px]">
                          <span
                            @click="openTaskEditDialog(task, index)"
                            class="font-medium text-slate-900 dark:text-white cursor-pointer hover:text-primary break-words whitespace-normal block"
                            :title="task.task_name || '--'"
                          >{{ task.task_name || '--' }}</span>
                        </td>
                        <!-- 责任人 -->
                        <td class="px-4 py-3">
                          <span
                            @click="openTaskEditDialog(task, index)"
                            class="text-slate-500 dark:text-slate-400 cursor-pointer hover:text-primary"
                            :title="$t('common.edit')"
                          >{{ task.owner || '--' }}</span>
                        </td>
                        <!-- 开始时间 -->
                        <td class="px-4 py-3">
                          <span
                            @click="openTaskEditDialog(task, index)"
                            class="text-slate-500 dark:text-slate-400 cursor-pointer hover:text-primary"
                            :title="$t('common.edit')"
                          >{{ task.start_time ? formatTaskDateTime(task.start_time) : '--' }}</span>
                        </td>
                        <!-- 结束时间 -->
                        <td class="px-4 py-3">
                          <span
                            @click="openTaskEditDialog(task, index)"
                            class="text-slate-500 dark:text-slate-400 cursor-pointer hover:text-primary"
                            :title="$t('common.edit')"
                          >{{ task.end_time ? formatTaskDateTime(task.end_time) : '--' }}</span>
                        </td>
                        <!-- 优先级 -->
                        <td class="px-4 py-3 whitespace-nowrap">
                          <span
                            v-if="getPriorityConfig(task.priority)"
                            @click="openTaskEditDialog(task, index)"
                            :class="[
                              'inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs cursor-pointer hover:opacity-80',
                              getPriorityConfig(task.priority)?.bgClass,
                              getPriorityConfig(task.priority)?.textClass
                            ]"
                            :title="$t('common.edit')"
                          >
                            <span 
                              class="material-symbols-outlined text-sm flex-shrink-0"
                              :class="getPriorityConfig(task.priority)?.iconClass"
                              style="font-size: 14px;"
                            >
                              {{ getPriorityConfig(task.priority)?.icon }}
                            </span>
                            <span class="whitespace-nowrap">{{ getPriorityConfig(task.priority)?.label }}</span>
                          </span>
                          <span
                            v-else
                            @click="openTaskEditDialog(task, index)"
                            class="text-slate-500 dark:text-slate-400 cursor-pointer hover:text-primary whitespace-nowrap"
                            :title="$t('common.edit')"
                          >--</span>
                        </td>
                        <!-- 状态 -->
                        <td class="px-4 py-3 whitespace-nowrap">
                          <span
                            @click="openTaskEditDialog(task, index)"
                            :class="[
                              'inline-block px-2 py-0.5 rounded text-xs cursor-pointer hover:opacity-80 whitespace-nowrap',
                              isTaskCompleted(task)
                                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                                : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                            ]"
                            :title="$t('common.edit')"
                          >
                            {{ isTaskCompleted(task)
                              ? $t('incidents.detail.evidenceResponse.progressSync.status.finished', '已完成') 
                              : $t('incidents.detail.evidenceResponse.progressSync.status.unfinished', '未完成') }}
                          </span>
                        </td>
                        <!-- 标签（可编辑） -->
                        <td class="px-4 py-3 whitespace-nowrap min-w-[120px]">
                          <select
                            v-model="task.tag"
                            @change="saveTaskField(getTaskUniqueId(task, index), 'tag', task.tag)"
                            class="w-full px-2 py-1 text-xs border border-gray-300 dark:border-border-dark rounded focus:outline-none focus:ring-2 focus:ring-primary dark:bg-surface-dark dark:text-white whitespace-nowrap"
                            :title="task.tag ? $t(`common.commentTypes.${task.tag}`, task.tag) : $t('incidents.detail.evidenceResponse.progressSync.columns.noTag', '无标签')"
                          >
                            <option value="">{{ $t('incidents.detail.evidenceResponse.progressSync.columns.noTag', '无标签') }}</option>
                            <option value="attackTracing">{{ $t('common.commentTypes.attackTracing', '攻击溯源') }}</option>
                            <option value="attackBlocking">{{ $t('common.commentTypes.attackBlocking', '攻击拦截') }}</option>
                            <option value="riskMitigation">{{ $t('common.commentTypes.riskMitigation', '风险消减') }}</option>
                            <option value="vulnerabilityIdentification">{{ $t('common.commentTypes.vulnerabilityIdentification', '漏洞定位') }}</option>
                          </select>
                        </td>
                        <!-- 查看详情 -->
                        <td class="px-4 py-3 whitespace-nowrap">
                          <a
                            v-if="task.detail_url"
                            :href="task.detail_url"
                            target="_blank"
                            rel="noopener noreferrer"
                            class="text-primary hover:text-primary/80 hover:underline inline-flex items-center gap-1 text-xs whitespace-nowrap"
                          >
                            <span class="material-symbols-outlined text-sm flex-shrink-0">open_in_new</span>
                            <span class="whitespace-nowrap">{{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.viewDetail', '查看详情') }}</span>
                          </a>
                          <span v-else class="text-slate-400 dark:text-slate-500 text-xs whitespace-nowrap">--</span>
                        </td>
                        <!-- 操作 -->
                        <td class="px-4 py-3 whitespace-nowrap">
                          <div class="flex items-center gap-2">
                            <button
                              @click="openTaskEditDialog(task, index)"
                              class="text-primary hover:text-primary/80 transition-colors whitespace-nowrap"
                              :title="$t('common.edit')"
                            >
                              <span class="material-symbols-outlined text-sm">edit</span>
                            </button>
                            <button
                              @click="deleteProgressSyncTask(task, index)"
                              class="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 transition-colors"
                              :title="$t('common.delete')"
                            >
                              <span class="material-symbols-outlined text-sm">delete</span>
                            </button>
                          </div>
                        </td>
                      </tr>
                    </template>
                    <tr v-else class="bg-white dark:bg-surface-dark">
                      <td colspan="10" class="px-4 py-8 text-center text-slate-500 dark:text-slate-400">
                        {{ $t('common.noData') }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </template>

          <!-- 事件简报内容 -->
          <template v-if="activeCardTab === 'incidentBrief'">
            <!-- 操作按钮 -->
            <div class="flex gap-2 mb-4">
              <button 
                @click="showAddNotificationDialog = true"
                class="px-4 py-1.5 text-sm bg-primary text-white rounded hover:bg-primary/90 transition-colors">
                {{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.addNotification') }}
              </button>
            </div>

            <!-- 事件通报/简报表格 -->
            <div class="bg-white dark:bg-surface-dark border border-gray-200 dark:border-border-dark rounded-lg overflow-hidden shadow-sm mb-6">
              <div class="overflow-x-auto">
                <table class="w-full text-sm text-left">
                  <thead class="bg-gray-50 dark:bg-[#1e293b] text-slate-600 dark:text-slate-300 font-medium border-b border-gray-200 dark:border-border-dark">
                    <tr>
                      <th class="px-4 py-3">{{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.notificationEvent') }}</th>
                      <th class="px-4 py-3">{{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.notificationType') }}</th>
                      <th class="px-4 py-3">{{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.owner') }}</th>
                      <th class="px-4 py-3">{{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.progress') }}</th>
                      <th class="px-4 py-3">{{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.nextPlan') }}</th>
                      <th class="px-4 py-3">{{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.remark') }}</th>
                      <th class="px-4 py-3 w-24">操作</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200 dark:divide-border-dark">
                    <template v-if="incidentNotifications.length > 0">
                      <tr 
                        v-for="(notification, index) in incidentNotifications" 
                        :key="index"
                        class="bg-white dark:bg-surface-dark hover:bg-gray-50 dark:hover:bg-surface-hover-dark/50 transition-colors">
                        <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">{{ notification.event || '--' }}</td>
                        <td class="px-4 py-3">
                          <span 
                            :class="[
                              'inline-block px-2 py-0.5 rounded text-xs',
                              notification.type === 'firstNotification' 
                                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                                : notification.type === 'closeNotification'
                                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                                : notification.type === 'networkProtectionDaily'
                                ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300'
                                : 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300'
                            ]">
                            {{ getNotificationTypeLabel(notification.type) }}
                          </span>
                        </td>
                        <td class="px-4 py-3 text-slate-500 dark:text-slate-400">{{ notification.owner || '--' }}</td>
                        <td class="px-4 py-3 text-slate-500 dark:text-slate-400">{{ notification.progress || '--' }}</td>
                        <td class="px-4 py-3 text-slate-500 dark:text-slate-400">{{ notification.nextPlan || '--' }}</td>
                        <td class="px-4 py-3 text-slate-500 dark:text-slate-400">{{ notification.remark || '--' }}</td>
                        <td class="px-4 py-3">
                          <div class="flex items-center gap-2">
                            <button 
                              @click="editNotification(index)"
                              class="text-primary hover:text-primary-hover transition-colors"
                              :title="$t('common.edit')">
                              <span class="material-symbols-outlined text-base">edit</span>
                            </button>
                            <button 
                              @click="deleteNotification(index)"
                              class="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 transition-colors"
                              :title="$t('common.delete')">
                              <span class="material-symbols-outlined text-base">delete</span>
                            </button>
                          </div>
                        </td>
                      </tr>
                    </template>
                    <tr v-else class="bg-white dark:bg-surface-dark">
                      <td colspan="7" class="px-4 py-8 text-center text-slate-500 dark:text-slate-400">
                        {{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.noData') }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </template>

          </main>
        </div>

        <!-- 评论区域（保留原有功能），独立容器 -->
        <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867]/70 rounded-xl shadow-sm">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-[#324867]/70">
            <h2 class="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
              <span class="material-symbols-outlined text-primary text-xl">comment</span>
              {{ $t('incidents.detail.comments.title') }}
            </h2>
          </div>
          <div class="p-6 pt-4 overflow-x-hidden">
            <CommentSection
              :comments="incident?.comments || []"
              :enable-comment-type="true"
              @submit="handlePostComment"
              @update="handleUpdateComment"
              @delete="handleDeleteComment"
            />
          </div>
        </div>
      </div>

    </div>

    <!-- 告警详情抽屉 -->
    <AlertDetail
      v-if="selectedAlertId"
      :alert-id="selectedAlertId"
      :prevent-auto-open-ai="true"
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

    <!-- 任务编辑对话框 -->
    <div
      v-if="showTaskEditDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="closeTaskEditDialog"
    >
      <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">
            {{ editingTask ? translateOr('incidents.detail.evidenceResponse.progressSync.editTask', '编辑任务') : translateOr('incidents.detail.evidenceResponse.progressSync.createTask', '创建任务') }}
          </h3>
          <button
            @click="closeTaskEditDialog"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
          >
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        
        <div class="space-y-4">
          <!-- 任务名称 -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.taskName', '任务名称') }}
            </label>
            <input
              v-model="taskEditForm.task_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-surface-dark dark:text-white"
              :placeholder="translateOr('incidents.detail.evidenceResponse.progressSync.columns.taskName', '任务名称')"
            />
          </div>
          
          <!-- 责任人 -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.owner', '责任人') }}
            </label>
            <input
              v-model="taskEditForm.owner"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-surface-dark dark:text-white"
              :placeholder="translateOr('incidents.detail.evidenceResponse.progressSync.columns.owner', '责任人')"
            />
          </div>
          
          <!-- 开始时间 -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.startTime', '开始时间') }}
            </label>
            <input
              v-model="taskEditForm.start_time"
              type="datetime-local"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-surface-dark dark:text-white"
            />
          </div>
          
          <!-- 结束时间 -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.endTime', '结束时间') }}
            </label>
            <input
              v-model="taskEditForm.end_time"
              type="datetime-local"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-surface-dark dark:text-white"
            />
          </div>
          
          <!-- 优先级 -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.priority', '优先级') }}
            </label>
            <select
              v-model="taskEditForm.priority"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-surface-dark dark:text-white"
            >
              <option value="">{{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.noPriority', '无') }}</option>
              <option :value="0">{{ translateOr('incidents.detail.evidenceResponse.progressSync.priority.normal', '普通') }}</option>
              <option :value="1">{{ translateOr('incidents.detail.evidenceResponse.progressSync.priority.urgent', '紧急') }}</option>
              <option :value="2">{{ translateOr('incidents.detail.evidenceResponse.progressSync.priority.veryUrgent', '非常紧急') }}</option>
            </select>
          </div>
          
          <!-- 完成状态 -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.status', '状态') }}
            </label>
            <select
              v-model="taskEditForm.isDone"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-surface-dark dark:text-white"
            >
              <option :value="false">{{ $t('incidents.detail.evidenceResponse.progressSync.status.unfinished', '未完成') }}</option>
              <option :value="true">{{ $t('incidents.detail.evidenceResponse.progressSync.status.finished', '已完成') }}</option>
            </select>
          </div>
          
          <!-- 备注（仅在进展同步中显示） -->
          <div v-if="activeCardTab === 'progressSync'">
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              {{ translateOr('incidents.detail.evidenceResponse.progressSync.columns.note', '备注') }}
            </label>
            <textarea
              v-model="taskEditForm.note"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-surface-dark dark:text-white"
              :placeholder="translateOr('incidents.detail.evidenceResponse.progressSync.columns.notePlaceholder', '请输入备注')"
            ></textarea>
          </div>
        </div>
        
        <div class="flex justify-end gap-3 mt-6">
          <button
            @click="closeTaskEditDialog"
            class="px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 bg-gray-100 dark:bg-surface-hover-dark rounded-lg hover:bg-gray-200 dark:hover:bg-surface-hover-dark transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="saveTaskEdit"
            class="px-4 py-2 text-sm font-medium text-white bg-primary rounded-lg hover:bg-primary/90 transition-colors"
          >
            {{ $t('common.save') }}
          </button>
        </div>
      </div>
    </div>

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

    <!-- 删除影响服务确认对话框 -->
    <div
      v-if="showDeleteServiceDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="cancelDeleteService"
    >
      <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-lg p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ $t('common.warning') }}
          </h2>
          <button
            @click="cancelDeleteService"
            class="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
          </button>
        </div>

        <!-- Prompt message -->
        <div class="mb-6 p-3 bg-gray-100 dark:bg-[#1e293b] rounded-md">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            确认删除任务项？
          </p>
        </div>

        <!-- Action buttons -->
        <div class="flex items-center justify-end gap-3">
          <button
            @click="cancelDeleteService"
            class="px-4 py-2 text-sm text-gray-700 dark:text-gray-400 bg-gray-100 dark:bg-[#1e293b] rounded-md hover:bg-gray-200 dark:hover:bg-primary/30 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="confirmDeleteService"
            :disabled="isDeletingService"
            class="px-4 py-2 text-sm text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span v-if="isDeletingService" class="material-symbols-outlined animate-spin text-base">sync</span>
            {{ $t('common.delete') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除事件通报确认对话框 -->
    <div
      v-if="showDeleteNotificationDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="cancelDeleteNotification"
    >
      <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-lg p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ $t('common.warning') }}
          </h2>
          <button
            @click="cancelDeleteNotification"
            class="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
          </button>
        </div>

        <!-- Prompt message -->
        <div class="mb-6 p-3 bg-gray-100 dark:bg-[#1e293b] rounded-md">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            确认删除任务项？
          </p>
        </div>

        <!-- Action buttons -->
        <div class="flex items-center justify-end gap-3">
          <button
            @click="cancelDeleteNotification"
            class="px-4 py-2 text-sm text-gray-700 dark:text-gray-400 bg-gray-100 dark:bg-[#1e293b] rounded-md hover:bg-gray-200 dark:hover:bg-primary/30 transition-colors"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="confirmDeleteNotification"
            :disabled="isDeletingNotification"
            class="px-4 py-2 text-sm text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span v-if="isDeletingNotification" class="material-symbols-outlined animate-spin text-base">sync</span>
            {{ $t('common.delete') }}
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
        <span class="text-sm">{{ $t('incidents.detail.shareSuccess') || 'Copied to clipboard' }}</span>
      </div>
    </Transition>

    <!-- AI Sidebar -->
    <AISidebar
      :visible="showAISidebar"
      :alert-title="currentTitle"
      :finding-summary="findingSummary"
      :show-finding-summary="true"
      :alert-id="route.params.id"
      @close="showAISidebar = false"
    />

    <!-- 新增/编辑影响服务对话框 -->
    <div
      v-if="showAddServiceDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="cancelService"
    >
      <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-lg p-6 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ editingServiceIndex >= 0 ? $t('common.edit') : $t('incidents.detail.evidenceResponse.services.add') }}
          </h2>
          <button
            @click="cancelService"
            class="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
          </button>
        </div>

        <form @submit.prevent="saveService" class="space-y-4">
          <!-- 服务 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('incidents.detail.evidenceResponse.services.columns.service') }}
              <span class="text-red-500">*</span>
            </label>
            <input
              v-model="serviceForm.service"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-md bg-white dark:bg-surface-dark text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary"
              :placeholder="$t('incidents.detail.evidenceResponse.services.columns.service')"
            />
          </div>

          <!-- 措施 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('incidents.detail.evidenceResponse.services.columns.measure') }}
            </label>
            <textarea
              v-model="serviceForm.measure"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-md bg-white dark:bg-surface-dark text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              :placeholder="$t('incidents.detail.evidenceResponse.services.columns.measure')"
            ></textarea>
          </div>

          <!-- SLA -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('incidents.detail.evidenceResponse.services.columns.sla') }}
            </label>
            <input
              v-model="serviceForm.sla"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-md bg-white dark:bg-surface-dark text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="例如: 4h, 24h"
            />
          </div>

          <!-- 计划完成时间 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('incidents.detail.evidenceResponse.services.columns.plannedCompletionTime') }}
            </label>
            <input
              v-model="serviceForm.plannedCompletionTime"
              type="datetime-local"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-md bg-white dark:bg-surface-dark text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary [&::-webkit-calendar-picker-indicator]:cursor-pointer [&::-webkit-calendar-picker-indicator]:opacity-100 dark:[&::-webkit-calendar-picker-indicator]:invert"
            />
          </div>

          <!-- 责任人 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('incidents.detail.evidenceResponse.services.columns.owner') }}
            </label>
            <input
              v-model="serviceForm.owner"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-md bg-white dark:bg-surface-dark text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary"
              :placeholder="$t('incidents.detail.evidenceResponse.services.columns.owner')"
            />
          </div>

          <!-- 进展 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('incidents.detail.evidenceResponse.services.columns.progress') }}
            </label>
            <select
              v-model="serviceForm.progress"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-md bg-white dark:bg-surface-dark text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">请选择</option>
              <option value="已完成">已完成</option>
              <option value="未完成">未完成</option>
            </select>
          </div>

          <!-- 备注 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('incidents.detail.evidenceResponse.services.columns.remark') }}
            </label>
            <textarea
              v-model="serviceForm.remark"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-md bg-white dark:bg-surface-dark text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              :placeholder="$t('incidents.detail.evidenceResponse.services.columns.remark')"
            ></textarea>
          </div>

          <!-- 操作按钮 -->
          <div class="flex items-center justify-end gap-3 pt-4 border-t border-gray-200 dark:border-border-dark">
            <button
              type="button"
              @click="cancelService"
              class="px-4 py-2 text-sm text-gray-700 dark:text-gray-400 bg-gray-100 dark:bg-[#1e293b] rounded-md hover:bg-gray-200 dark:hover:bg-primary/30 transition-colors"
            >
              {{ $t('common.cancel') }}
            </button>
            <button
              type="submit"
              class="px-4 py-2 text-sm text-white bg-primary rounded-md hover:bg-primary-hover transition-colors"
            >
              {{ $t('common.save') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 新增/编辑通报对话框 -->
    <div
      v-if="showAddNotificationDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="cancelNotification"
    >
      <div class="bg-white dark:bg-[#111822] border border-gray-200 dark:border-[#324867] rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ editingNotificationIndex >= 0 ? $t('common.edit') : $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.addNotification') }}
          </h2>
          <button
            @click="cancelNotification"
            class="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <span class="material-symbols-outlined text-base">close</span>
          </button>
        </div>

        <form @submit.prevent="saveNotification" class="space-y-4">
          <!-- 通报事件 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.notificationEvent') }}
              <span class="text-red-500">*</span>
            </label>
            <input
              v-model="notificationForm.event"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-md bg-white dark:bg-surface-dark text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary"
              :placeholder="$t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.notificationEvent')"
            />
          </div>

          <!-- 通报类型 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.notificationType') }}
            </label>
            <select
              v-model="notificationForm.type"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-md bg-white dark:bg-surface-dark text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="firstNotification">{{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.types.firstNotification') }}</option>
              <option value="closeNotification">{{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.types.closeNotification') }}</option>
              <option value="networkProtectionDaily">{{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.types.networkProtectionDaily') }}</option>
              <option value="other">{{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.types.other') }}</option>
            </select>
          </div>

          <!-- 责任人 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.owner') }}
            </label>
            <input
              v-model="notificationForm.owner"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-md bg-white dark:bg-surface-dark text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary"
              :placeholder="$t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.owner')"
            />
          </div>

          <!-- 进展 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.progress') }}
            </label>
            <textarea
              v-model="notificationForm.progress"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-md bg-white dark:bg-surface-dark text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              :placeholder="$t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.progress')"
            ></textarea>
          </div>

          <!-- 下一步计划 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.nextPlan') }}
            </label>
            <textarea
              v-model="notificationForm.nextPlan"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-md bg-white dark:bg-surface-dark text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              :placeholder="$t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.nextPlan')"
            ></textarea>
          </div>

          <!-- 备注 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.remark') }}
            </label>
            <textarea
              v-model="notificationForm.remark"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 dark:border-border-dark rounded-md bg-white dark:bg-surface-dark text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              :placeholder="$t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.remark')"
            ></textarea>
          </div>

          <!-- 操作按钮 -->
          <div class="flex items-center justify-end gap-3 pt-4 border-t border-gray-200 dark:border-border-dark">
            <button
              type="button"
              @click="cancelNotification"
              class="px-4 py-2 text-sm text-gray-700 dark:text-gray-400 bg-gray-100 dark:bg-[#1e293b] rounded-md hover:bg-gray-200 dark:hover:bg-primary/30 transition-colors"
            >
              {{ $t('common.cancel') }}
            </button>
            <button
              type="submit"
              class="px-4 py-2 text-sm text-white bg-primary rounded-md hover:bg-primary-hover transition-colors"
            >
              {{ $t('common.save') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { getIncidentDetail, postComment, regenerateIncidentGraph, disassociateAlertsFromIncident, updateIncidentTask, getImpactedServices, createImpactedService, updateImpactedService, deleteImpactedService, getIncidentBriefs, createIncidentBrief, updateIncidentBrief, deleteIncidentBrief } from '@/api/incidents'
import { updateComment, deleteComment, getComments } from '@/api/comments'
import { getProjectList, getTaskDetail, createGroup, modifyTask } from '@/api/securityAgent'
import AlertDetail from '@/components/alerts/AlertDetail.vue'
import EditIncidentDialog from '@/components/incidents/EditIncidentDialog.vue'
import CloseIncidentDialog from '@/components/incidents/CloseIncidentDialog.vue'
import DataTable from '@/components/common/DataTable.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import CommentSection from '@/components/common/CommentSection.vue'
import AISidebar from '@/components/common/AISidebar.vue'
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

// Light模式下的颜色配置 - 使用更深的颜色提高对比度
const ENTITY_COLOR_SOLID_LIGHT = {
  host: '#dc2626',      // 更深的红色
  ip: '#0284c7',        // 更深的青色
  domain: '#059669',    // 更深的绿色
  domainname: '#059669',
  url: '#059669',
  operation: '#d97706', // 更深的黄色
  user: '#7c3aed',      // 更深的紫色
  tenant: '#7c3aed',
  alert: '#dc2626',
  service: '#059669',
  api: '#0369a1',       // 更深的蓝色
  malware: '#b91c1c',   // 更深的红色
  other: '#2563eb'      // 更深的蓝色
}

// Dark模式下的颜色配置 - 保持原有较亮的颜色
const ENTITY_COLOR_SOLID_DARK = {
  host: '#fda4af',
  ip: '#67e8f9',
  domain: '#6ee7b7',
  domainname: '#6ee7b7',
  url: '#6ee7b7',
  operation: '#fcd34d',
  user: '#c4b5fd',
  tenant: '#c4b5fd',
  alert: '#fda4af',
  service: '#6ee7b7',
  api: '#7dd3fc',
  malware: '#ef4444',
  other: '#60a5fa'
}

const ENTITY_COLOR_SOLID = ENTITY_COLOR_SOLID_LIGHT

const ENTITY_TYPE_ALIAS = {
  domainname: 'domain',
  fqdn: 'domain',
  url: 'url',
  service: 'api',
  userid: 'user'
}

const normalizeEntityType = (type) => ENTITY_TYPE_ALIAS[type] || type

const ENTITY_ICON_PATHS = {
  // IP地址图标 - 使用 Material Symbols bring_your_own_ip
  ip: {
    icon: 'bring_your_own_ip'
  },
  // 域名图标 - 地球/全球网络图标
  domain: {
    icon: 'public'
  },
  // 主机图标 - 使用 Material Symbols host
  host: {
    icon: 'host'
  },
  // API图标 - 使用 Material Symbols api
  api: {
    icon: 'api'
  },
  // URL图标 - 使用 Material Symbols link
  url: {
    icon: 'link'
  },
  // 告警图标 - 警告三角形
  alert: {
    icon: 'warning'
  },
  // 用户图标 - 使用 Material Symbols person
  user: {
    icon: 'person'
  },
  // 租户图标 - 群组/组织图标
  tenant: {
    icon: 'groups'
  },
  // 服务图标 - 齿轮/设置图标
  service: {
    icon: 'settings'
  },
  // 操作图标 - 操作/动作图标
  operation: {
    icon: 'add'
  },
  // 事件图标 - 事件/日志图标
  event: {
    icon: 'event'
  },
  // 恶意软件图标 - 使用 Material Symbols skull
  malware: {
    icon: 'skull'
  },
  // 其他类型 - 使用圆形图标
  other: {
    icon: 'circle'
  }
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
// 仅刷新评论列表和时间线，避免刷新其他数据块
/**
 * @brief 将云脑原始评论格式转换为前端期望的格式
 */
const transformCloudBrainComments = (cloudBrainData) => {
  if (!cloudBrainData || !cloudBrainData.data || !Array.isArray(cloudBrainData.data)) {
    return []
  }
  
  return cloudBrainData.data.map((item) => {
    const rawContent = item.content || {}
    const contentValue = rawContent.value || ''
    
    // 从内容中提取 owner（格式：【@owner】: content）
    let author = rawContent.come_from || 'Unknown'
    const ownerMatch = contentValue.match(/【@([^】]+)】/)
    if (ownerMatch) {
      author = ownerMatch[1].trim()
    }
    
    // 提取实际评论内容（去掉【@owner】前缀）
    let content = contentValue
    if (ownerMatch) {
      content = contentValue.replace(/【@[^】]+】:\s*/, '').trim()
    }
    
    return {
      id: item.id,
      comment_id: item.id,
      author: author,
      create_time: rawContent.occurred_time,
      content: content,
      type: item.note_type,
      note_type: item.note_type,
      file: null, // 文件信息需要单独查询，这里先设为 null
      exists_in_db: true
    }
  })
}

const loadComments = async () => {
  const incidentId = route.params.id
  if (!incidentId) return
  try {
    const resp = await getComments(incidentId)
    // 云脑返回的原始格式需要先转换
    const rawData = resp.data?.data || resp.data || {}
    const rawComments = Array.isArray(rawData) ? rawData : (rawData.data || [])
    const transformedComments = Array.isArray(rawComments) && rawComments.length > 0 && rawComments[0].content
      ? transformCloudBrainComments({ data: rawComments })
      : rawComments
    const comments = formatComments(transformedComments)
    if (!incident.value) {
      incident.value = { comments, timeline: [] }
    } else {
      incident.value.comments = comments
      incident.value.timeline = generateTimeline({
        ...(incident.value || {}),
        comments
      })
    }
  } catch (error) {
    console.error('Failed to load comments:', error)
  }
}

const loadingIncident = ref(false)
// 默认进入 Alert story 视图
const activeTab = ref('alertStory')
// 响应指标数据
const metricsData = ref({
  mttTracing: null, // 平均攻击溯源时间
  mttBlocking: null, // 平均攻击源拦截时间
  mttr: null, // 平均风险消减时间
  mttVulnerabilityEntry: null // 平均漏洞入口定位时间
})
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
const showAISidebar = ref(false)
const currentTitle = ref('')
const findingSummary = ref('')

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

const getNodeType = (node) => normalizeEntityType((node.properties?.entity_type || 'other').toLowerCase())

const getNodeIconMeta = (node) => {
  const type = getNodeType(node)
  return ENTITY_ICON_PATHS[type] || ENTITY_ICON_PATHS.other
}

const getNodeIconSize = (node) => {
  const size = node.visual?.size || 30
  // 增大图标尺寸，使用3.0倍节点大小，最大尺寸增加到72，并确保最小尺寸
  const calculatedSize = Math.max(size * 3.0, 36)
  return Math.min(calculatedSize, 72)
}

const getNodeIconStrokeColor = (node) => {
  const type = getNodeType(node)
  const isDark = document.documentElement.classList.contains('dark')
  const colorMap = isDark ? ENTITY_COLOR_SOLID_DARK : ENTITY_COLOR_SOLID_LIGHT
  return colorMap[type] || colorMap.other
}

const getGraphTextColor = () => {
  const svgElement = d3SvgRef.value?.node?.()
  if (svgElement) {
    const dataColor = svgElement.getAttribute('data-text-color')
    if (dataColor) return dataColor
  }
  const isDark = document.documentElement.classList.contains('dark')
  // Light模式下使用更深的颜色提高可读性
  return isDark ? '#e2e8f0' : '#1e293b'
}

const buildNodeVisualMeta = (node) => {
  const type = getNodeType(node)
  const isDark = document.documentElement.classList.contains('dark')
  const colorMap = isDark ? ENTITY_COLOR_SOLID_DARK : ENTITY_COLOR_SOLID_LIGHT
  const color = colorMap[type] || colorMap.other
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

  // 只保留中间的图标，不再绘制外围圆点 - 使用 Material Symbols
  nodeEnter
    .append('text')
    .attr('class', 'graph-node__icon material-symbols-outlined')
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'central')
    .attr('font-size', (d) => `${getNodeIconSize(d)}px`)
    .attr('fill', (d) => getNodeIconStrokeColor(d))
    .text((d) => getNodeIconMeta(d).icon)

  // 获取文字颜色（从 SVG 的 data 属性或检测主题）
  const getTextColor = () => {
    const svgElement = d3SvgRef.value?.node()
    if (svgElement) {
      const dataColor = svgElement.getAttribute('data-text-color')
      if (dataColor) return dataColor
    }
    const isDark = document.documentElement.classList.contains('dark')
    // Light模式下使用更深的颜色提高可读性
    return isDark ? '#e2e8f0' : '#1e293b'
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
    // Light模式下使用更深的颜色提高可读性
    return isDark ? '#e2e8f0' : '#1e293b'
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

  d3NodeSelection.value
    .select('text.graph-node__icon')
    .text((node) => getNodeIconMeta(node).icon)
    .attr('font-size', (node) => `${getNodeIconSize(node)}px`)
    .attr('fill', (node) => getNodeIconStrokeColor(node))
    .attr('opacity', (node) => {
      if (selectedId) {
        return node.id === selectedId || relations.has(node.id) ? 0.95 : 0.2
      }
      if (searchActive) {
        return highlightSet.has(node.id) ? 0.95 : 0.25
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

  // 如果当前没有任何节点（如重新生成图谱时清空画布），主动销毁并清空中间图区域，
  // 但保留左右栏（通过模板中的 hasGraphData || isRegeneratingGraph 控制）
  if (!parsed.nodes || parsed.nodes.length === 0) {
    destroyD3Graph()
    if (graphCanvasRef.value) {
      graphCanvasRef.value.innerHTML = ''
    }
  }
  
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

// 影响服务统计数据
const impactedServicesStats = computed(() => {
  const total = impactedServices.value.length
  const completed = impactedServices.value.filter(service => service.progress === '已完成').length
  const uncompleted = impactedServices.value.filter(service => service.progress === '未完成').length
  return {
    total,
    completed,
    uncompleted
  }
})

// 事件简报统计数据
const incidentBriefStats = computed(() => {
  const notifications = incidentNotifications.value.filter(
    notification => notification.type === 'firstNotification' || notification.type === 'closeNotification'
  ).length
  const dailyReports = incidentNotifications.value.filter(
    notification => notification.type === 'networkProtectionDaily'
  ).length
  return {
    notifications,
    dailyReports
  }
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
    map[node.id] = getNodeType(node)
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
  const isDark = document.documentElement.classList.contains('dark')
  const colorMap = isDark ? ENTITY_COLOR_SOLID_DARK : ENTITY_COLOR_SOLID_LIGHT
  displayGraphNodes.value.forEach((node) => {
    const type = getNodeType(node)
    if (seen.has(type)) {
      return
    }
    seen.add(type)
    entries.push({
      key: type,
      label: t(`incidents.detail.eventGraph.legendLabels.${type}`, type),
      color: colorMap[type] || colorMap.other
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

const handleOpenAISidebar = () => {
  if (incident.value) {
    currentTitle.value = incident.value.title || incident.value.name || ''
    findingSummary.value = incident.value.graphSummary || ''
  } else {
    currentTitle.value = ''
    findingSummary.value = ''
  }
  showAISidebar.value = true
}

onBeforeUnmount(() => {
  window.removeEventListener('pointermove', handleNodeDetailResize)
  window.removeEventListener('pointerup', stopNodeDetailResize)
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', handleWindowResize)
  }
  if (legendFlashTimer.value) {
    clearTimeout(legendFlashTimer.value)
  }
  // 清理WR搜索防抖定时器
  if (warroomSearchTimer.value) {
    clearTimeout(warroomSearchTimer.value)
  }
  if (typeof document !== 'undefined') {
    fullscreenEventNames.forEach((eventName) => document.removeEventListener(eventName, syncGraphFullscreenState))
    // 移除点击外部区域关闭下拉框的事件监听
    document.removeEventListener('click', closeTaskIdDropdown)
  }
  window.removeEventListener('open-ai-sidebar', handleOpenAISidebar)
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

const associatedAlertsColumns = computed(() => [
  { key: 'createTime', label: t('alerts.list.createTime') },
  { key: 'alertTitle', label: t('alerts.list.alertTitle') },
  { key: 'riskLevel', label: t('alerts.list.riskLevel') },
  { key: 'aiJudge', label: t('alerts.list.aiJudge') },
  { key: 'status', label: t('alerts.list.status') },
  { key: 'actor', label: t('alerts.list.actor') }
])

// 关联告警表格默认列宽
const associatedAlertsDefaultWidths = {
  createTime: 180,
  alertTitle: 400,
  riskLevel: 120,
  aiJudge: 120,
  status: 120,
  actor: 50
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
      actor: alert.actor || '-',
      verification_state: alert.verification_state || alert.verificationState || 'Unknown'
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
// 左侧面板标签切换：默认显示任务管理
const leftPaneActiveTab = ref('taskManagement')
// 证据与响应卡片切换：默认显示影响服务
const activeCardTab = ref('impactedServices')
// 进展同步指令筛选类型
const progressSyncFilterType = ref('all') // 'myCreated', 'myPending', 'all'
// 进展同步标签筛选
const progressSyncTagFilter = ref('') // ''表示全部，'attackTracing', 'attackBlocking', 'riskMitigation', 'vulnerabilityIdentification'
// 任务编辑相关状态
const editingTaskIndex = ref(null) // 正在编辑的任务唯一ID
const editingTaskField = ref(null) // 正在编辑的字段名
const editingTaskValue = ref('') // 正在编辑的字段值
// 任务标签映射（用于存储每个任务的标签）
const taskTags = ref({}) // { taskUniqueId: tag }
// 任务编辑弹窗状态
const showTaskEditDialog = ref(false)
const editingTask = ref(null)
const editingTaskIdx = ref(-1)
const taskEditForm = ref({
  task_name: '',
  owner: '',
  start_time: '',
  end_time: '',
  priority: '',
  isDone: false,
  note: '' // 备注字段（仅在进展同步中使用）
})
// 事件通报/简报相关状态
const incidentNotifications = ref([]) // 事件通报列表
const showAddNotificationDialog = ref(false) // 显示新增通报对话框
const editingNotificationIndex = ref(-1) // 正在编辑的通报索引，-1表示新增
const editingNotificationId = ref(null) // 正在编辑的通报ID（用于更新API调用）
const showDeleteNotificationDialog = ref(false) // 显示删除事件通报确认对话框
const deletingNotificationIndex = ref(-1) // 要删除的事件通报索引
const isDeletingNotification = ref(false) // 正在删除事件通报
const notificationForm = ref({
  event: '',
  type: 'firstNotification',
  owner: '',
  progress: '',
  nextPlan: '',
  remark: ''
})
// 影响服务相关状态
const impactedServices = ref([]) // 影响服务列表
const showAddServiceDialog = ref(false) // 显示新增影响服务对话框
const editingServiceIndex = ref(-1) // 正在编辑的服务索引，-1表示新增
const editingServiceId = ref(null) // 正在编辑的服务ID（用于更新API调用）
const showDeleteServiceDialog = ref(false) // 显示删除影响服务确认对话框
const deletingServiceIndex = ref(-1) // 要删除的影响服务索引
const isDeletingService = ref(false) // 正在删除影响服务
const serviceForm = ref({
  service: '',
  measure: '',
  sla: '',
  plannedCompletionTime: '',
  owner: '',
  progress: '',
  remark: ''
})
// 任务管理相关状态
const selectedTaskId = ref('') // 保留用于向后兼容
const selectedWarroomIds = ref([]) // 选中的warroom ID数组
const projectOptions = ref([]) // 项目选项列表，格式：{ label: "project_name", value: "project_uuid" }
const loadingProjectList = ref(false)
const taskDetail = ref(null) // 保留用于向后兼容
const groupedTaskDetails = ref({}) // 按warroom ID分组存储的任务详情 { warroomId: taskDetail }
const loadingTaskDetail = ref(false)
const taskDetailError = ref('')
const taskDetailLoaded = ref(false)
const showTaskIdDropdown = ref(false)
const isEditingTaskId = ref(false)
const isRightPaneCollapsed = ref(false)
const taskIdDropdownRef = ref(null)
const warroomSearchKeyword = ref('') // WR搜索关键字
const warroomSearchTimer = ref(null) // 防抖定时器

// 根据选中的 taskId 获取对应的 project_name 用于显示（向后兼容）
const selectedTaskName = computed(() => {
  if (!selectedTaskId.value || !projectOptions.value.length) {
    return ''
  }
  const selectedOption = projectOptions.value.find(option => option.value === selectedTaskId.value)
  return selectedOption ? selectedOption.label : ''
})

// 从 groupedTaskDetails 中提取所有任务项，用于进展同步表格
const allProgressSyncTasks = computed(() => {
  const tasks = []
  if (!groupedTaskDetails.value || Object.keys(groupedTaskDetails.value).length === 0) {
    return tasks
  }
  
  // 遍历所有 warroom
  Object.keys(groupedTaskDetails.value).forEach(warroomId => {
    const warroomDetail = groupedTaskDetails.value[warroomId]
    const warroomName = getWarroomName(warroomId)
    
    // 处理数组格式的任务列表
    if (Array.isArray(warroomDetail)) {
      warroomDetail.forEach((task, index) => {
        const uniqueId = getTaskUniqueId({ ...task, warroomId }, index)
        // 优先使用taskTags中存储的tag，其次从group_name转换，最后使用task.tag
        const tag = taskTags.value[uniqueId] || (task.group_name ? getGroupNameTag(task.group_name) : '') || task.tag || ''
        tasks.push({
          ...task,
          warroomId: warroomId,
          warroomName: warroomName,
          tag: tag
        })
      })
    } 
    // 处理对象格式，包含 task_list 数组
    else if (warroomDetail && Array.isArray(warroomDetail.task_list)) {
      warroomDetail.task_list.forEach((task, index) => {
        const uniqueId = getTaskUniqueId({ ...task, warroomId }, index)
        // 优先使用taskTags中存储的tag，其次从group_name转换，最后使用task.tag
        const tag = taskTags.value[uniqueId] || (task.group_name ? getGroupNameTag(task.group_name) : '') || task.tag || ''
        tasks.push({
          ...task,
          warroomId: warroomId,
          warroomName: warroomName,
          tag: tag
        })
      })
    }
  })
  
  return tasks
})

// 根据筛选类型过滤任务
const filteredProgressSyncTasks = computed(() => {
  const tasks = allProgressSyncTasks.value
  if (!tasks.length) return []
  
  // 为每个任务添加标签和唯一ID
  const tasksWithTags = tasks.map((task, index) => {
    const uniqueId = getTaskUniqueId(task, index)
    // 优先使用taskTags中存储的tag，其次使用task.tag，最后从group_name转换
    const tag = taskTags.value[uniqueId] || task.tag || (task.group_name ? getGroupNameTag(task.group_name) : '') || ''
    return {
      ...task,
      uniqueId: uniqueId,
      tag: tag
    }
  })
  
  // 获取当前用户信息
  const currentUser = authStore.user?.username || authStore.user?.cn || authStore.user?.name || ''
  
  let filtered = []
  switch (progressSyncFilterType.value) {
    case 'myCreated':
      // 我创建的指令：根据创建者字段筛选（需要根据实际数据结构调整）
      filtered = tasksWithTags.filter(task => {
        const creator = task.creator || task.create_by || task.created_by
        return creator === currentUser
      })
      break
    case 'myPending':
      // 待我处理的指令：状态为待处理且责任人为当前用户
      filtered = tasksWithTags.filter(task => {
        const isPending = task.stageName === '待处理' || task.stageName === 'Pending'
        const owner = task.owner || task.employeeAccount || task.assignee
        const isMyTask = owner === currentUser
        return isPending && isMyTask
      })
      break
    case 'all':
      // 全部指令
      filtered = tasksWithTags
      break
    default:
      filtered = tasksWithTags
  }
  
  // 根据标签过滤
  if (progressSyncTagFilter.value) {
    filtered = filtered.filter(task => task.tag === progressSyncTagFilter.value)
  }
  
  return filtered
})

// 根据任务标签计算指标
const calculateMetricsFromTasks = (tasks) => {
  // 初始化指标数据
  const metrics = {
    mttTracing: null,
    mttBlocking: null,
    mttr: null,
    mttVulnerabilityEntry: null
  }
  
  // 按标签分组任务
  const tracingTasks = tasks.filter(t => t.tag === 'attackTracing' && t.start_time && t.end_time)
  const blockingTasks = tasks.filter(t => t.tag === 'attackBlocking' && t.start_time && t.end_time)
  const mitigationTasks = tasks.filter(t => t.tag === 'riskMitigation' && t.start_time && t.end_time)
  const vulnerabilityTasks = tasks.filter(t => t.tag === 'vulnerabilityIdentification' && t.start_time && t.end_time)
  
  // 计算平均时间（小时）
  const calculateAverageTime = (taskList) => {
    if (!taskList || taskList.length === 0) return null
    
    const totalHours = taskList.reduce((sum, task) => {
      const start = new Date(task.start_time).getTime()
      const end = new Date(task.end_time).getTime()
      if (isNaN(start) || isNaN(end) || end <= start) return sum
      const hours = (end - start) / (1000 * 60 * 60) // 转换为小时
      return sum + hours
    }, 0)
    
    const average = totalHours / taskList.length
    return Math.round(average * 100) / 100 // 保留两位小数
  }
  
  metrics.mttTracing = calculateAverageTime(tracingTasks)
  metrics.mttBlocking = calculateAverageTime(blockingTasks)
  metrics.mttr = calculateAverageTime(mitigationTasks)
  metrics.mttVulnerabilityEntry = calculateAverageTime(vulnerabilityTasks)
  
  // 更新指标数据
  metricsData.value = metrics
}

// 监听任务变化，自动计算指标
watch([filteredProgressSyncTasks, taskTags], () => {
  calculateMetricsFromTasks(filteredProgressSyncTasks.value)
}, { deep: true, immediate: true })

// 进展同步卡片指标
const progressSyncMetrics = computed(() => {
  const tasks = allProgressSyncTasks.value
  const total = tasks.length
  const completed = tasks.filter(task => isTaskCompleted(task)).length
  const uncompleted = total - completed
  
  return {
    total,
    completed,
    uncompleted
  }
})

// 获取任务唯一ID
const getTaskUniqueId = (task, index) => {
  // 使用warroomId + task_name + index 作为唯一标识
  return `${task.warroomId || 'unknown'}_${task.task_name || 'task'}_${index}`
}

// 判断任务是否已完成（支持多种状态字段和格式）
const isTaskCompleted = (task) => {
  if (!task) return false
  
  // 检查 isDone 字段（支持多种格式）
  if (task.isDone === true || task.isDone === 1 || task.isDone === '1' || 
      task.isDone === '已完成' || task.isDone === 'Completed' || 
      task.isDone === 'completed' || task.isDone === 'true') {
    return true
  }
  
  // 检查 status 字段
  if (task.status) {
    const status = String(task.status).toLowerCase()
    if (status === 'completed' || status === '已完成' || status === 'finished' || 
        status === 'done' || status === 'closed' || status === '已关闭') {
      return true
    }
  }
  
  // 检查 stageName 字段
  if (task.stageName) {
    const stage = String(task.stageName).toLowerCase()
    if (stage === '已完成' || stage === 'completed' || stage === 'finished' || 
        stage === 'done' || stage === '已关闭' || stage === 'closed') {
      return true
    }
  }
  
  // 检查 stage 字段
  if (task.stage) {
    const stage = String(task.stage).toLowerCase()
    if (stage === '已完成' || stage === 'completed' || stage === 'finished' || 
        stage === 'done' || stage === '已关闭' || stage === 'closed') {
      return true
    }
  }
  
  return false
}

// 开始编辑任务字段
const startEditTask = (taskUniqueId, field, currentValue) => {
  editingTaskIndex.value = taskUniqueId
  editingTaskField.value = field
  if (field === 'isDone') {
    editingTaskValue.value = currentValue === true || currentValue === 1 || currentValue === '已完成' || currentValue === 'Completed'
  } else {
    editingTaskValue.value = currentValue
  }
}

// 取消编辑
const cancelEditTask = () => {
  editingTaskIndex.value = null
  editingTaskField.value = null
  editingTaskValue.value = ''
}

// 标签值到中文名称的映射
const getTagGroupName = (tagValue) => {
  const tagMap = {
    'attackTracing': '攻击溯源',
    'attackBlocking': '攻击拦截',
    'riskMitigation': '风险消减',
    'vulnerabilityIdentification': '漏洞定位'
  }
  return tagMap[tagValue] || tagValue
}

// 中文名称到标签值的反向映射（用于从group_name转换为tag）
const getGroupNameTag = (groupName) => {
  if (!groupName) return ''
  const groupNameMap = {
    '攻击溯源': 'attackTracing',
    '攻击拦截': 'attackBlocking',
    '风险消减': 'riskMitigation',
    '漏洞定位': 'vulnerabilityIdentification',
    '默认分组': '' // 默认分组对应空标签
  }
  return groupNameMap[groupName] || ''
}

// 保存任务字段
const saveTaskField = async (taskUniqueId, field, value) => {
  // 找到对应的任务并更新
  const taskIndex = filteredProgressSyncTasks.value.findIndex(task => task.uniqueId === taskUniqueId)
  if (taskIndex === -1) return
  
  const task = filteredProgressSyncTasks.value[taskIndex]
  
  // 更新任务数据
  if (field === 'isDone') {
    task.isDone = value === true || value === 'true' || value === 1
  } else if (field === 'start_time' || field === 'end_time') {
    // 将datetime-local格式转换为ISO格式
    if (value) {
      const date = new Date(value)
      task[field] = date.toISOString()
    } else {
      task[field] = null
    }
  } else if (field === 'tag') {
    // 保存标签
    taskTags.value[taskUniqueId] = value || ''
    task.tag = value || ''
    // 重新计算指标
    calculateMetricsFromTasks(filteredProgressSyncTasks.value)
    
    // 如果是在进展同步中修改标签，需要调用dify API
    if (activeCardTab.value === 'progressSync' && task.warroomId && task.task_id) {
      try {
        // 如果标签不为空，先创建group
        if (value) {
          const groupName = getTagGroupName(value)
          const createGroupResult = await createGroup({
            project_uuid: task.warroomId,
            group_name: groupName
          })
          
          // 创建group成功后，调用modifyTask修改task的group_name
          if (createGroupResult && createGroupResult.status === 'success') {
            await modifyTask({
              project_uuid: task.warroomId,
              task_id: task.task_id,
              group_name: groupName
            })
          }
        } else {
          // 如果标签为空，设置group_name为"默认分组"
          await modifyTask({
            project_uuid: task.warroomId,
            task_id: task.task_id,
            group_name: '默认分组'
          })
        }
      } catch (error) {
        console.error('Failed to update task tag via dify API:', error)
        toast.error(translateOr('incidents.detail.evidenceResponse.progressSync.updateTagError', '更新任务标签失败') + ': ' + (error?.message || 'Unknown error'))
      }
    }
  } else {
    task[field] = value
  }
  
  // 如果修改了其他字段（非标签），且是在进展同步中，调用modifyTask
  if (field !== 'tag' && activeCardTab.value === 'progressSync' && task.warroomId && task.task_id) {
    try {
      const modifyParams = {
        project_uuid: task.warroomId,
        task_id: task.task_id
      }
      
      // 根据字段类型添加相应的参数
      if (field === 'task_name') {
        modifyParams.task_name = value
      } else if (field === 'owner') {
        modifyParams.owner = value
      } else if (field === 'priority') {
        modifyParams.priority = value !== '' ? value : null
      } else if (field === 'isDone') {
        modifyParams.status = value ? '已完成' : '待处理'
      } else if (field === 'start_time') {
        modifyParams.start_time = value
      } else if (field === 'end_time') {
        modifyParams.end_time = value
      }
      
      await modifyTask(modifyParams)
    } catch (error) {
      console.error('Failed to update task field via dify API:', error)
      toast.error(translateOr('incidents.detail.evidenceResponse.progressSync.updateTaskError', '更新任务失败') + ': ' + (error?.message || 'Unknown error'))
    }
  }
  
  // 同步更新到groupedTaskDetails
  updateTaskInGroupedDetails(task)
  
  // 取消编辑状态
  cancelEditTask()
}

// 更新groupedTaskDetails中的任务数据
const updateTaskInGroupedDetails = (updatedTask) => {
  if (!groupedTaskDetails.value || !updatedTask.warroomId) return
  
  const warroomDetail = groupedTaskDetails.value[updatedTask.warroomId]
  if (!warroomDetail) return
  
  // 处理数组格式
  if (Array.isArray(warroomDetail)) {
    const taskIndex = warroomDetail.findIndex(t => 
      t.task_name === updatedTask.task_name || 
      (t.task_name === updatedTask.task_name && t.owner === updatedTask.owner)
    )
    if (taskIndex !== -1) {
      warroomDetail[taskIndex] = { ...warroomDetail[taskIndex], ...updatedTask }
    }
  } 
  // 处理对象格式，包含task_list数组
  else if (warroomDetail.task_list && Array.isArray(warroomDetail.task_list)) {
    const taskIndex = warroomDetail.task_list.findIndex(t => 
      t.task_name === updatedTask.task_name || 
      (t.task_name === updatedTask.task_name && t.owner === updatedTask.owner)
    )
    if (taskIndex !== -1) {
      warroomDetail.task_list[taskIndex] = { ...warroomDetail.task_list[taskIndex], ...updatedTask }
    }
  }
}

// 格式化时间为datetime-local输入格式
const formatTaskDateTimeForInput = (dateTime) => {
  if (!dateTime) return ''
  const date = new Date(dateTime)
  if (isNaN(date.getTime())) return ''
  // 转换为本地时间，格式为 YYYY-MM-DDTHH:mm
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

// 打开任务编辑对话框
const openTaskEditDialog = (task, index) => {
  if (!task) return
  
  editingTask.value = task
  editingTaskIdx.value = index
  
  // 转换优先级为数字值（0=普通，1=紧急，2=非常紧急）
  let priorityValue = ''
  if (task.priority !== null && task.priority !== undefined && task.priority !== '') {
    // 如果是数字，直接使用
    if (typeof task.priority === 'number' && task.priority >= 0 && task.priority <= 2) {
      priorityValue = task.priority
    } else {
      // 尝试解析为数字
      const num = parseInt(task.priority, 10)
      if (!isNaN(num) && num >= 0 && num <= 2) {
        priorityValue = num
      } else {
        // 根据文本内容判断
        const priorityStr = String(task.priority).toLowerCase()
        if (priorityStr === '普通' || priorityStr === 'normal' || priorityStr === 'low') {
          priorityValue = 0
        } else if (priorityStr === '紧急' || priorityStr === 'urgent' || priorityStr === 'high') {
          priorityValue = 1
        } else if (priorityStr === '非常紧急' || priorityStr === 'very urgent' || priorityStr === 'critical') {
          priorityValue = 2
        }
      }
    }
  }
  
  // 填充表单数据
  taskEditForm.value = {
    task_name: task.task_name || '',
    owner: task.owner || '',
    start_time: formatTaskDateTimeForInput(task.start_time),
    end_time: formatTaskDateTimeForInput(task.end_time),
    priority: priorityValue,
    isDone: isTaskCompleted(task),
    note: task.note || task.notes || '' // 备注字段
  }
  
  showTaskEditDialog.value = true
}

// 关闭任务编辑对话框
const closeTaskEditDialog = () => {
  showTaskEditDialog.value = false
  editingTask.value = null
  editingTaskIdx.value = -1
  taskEditForm.value = {
    task_name: '',
    owner: '',
    start_time: '',
    end_time: '',
    priority: '',
    isDone: false,
    note: ''
  }
}

// 创建新任务
const createNewTask = () => {
  editingTask.value = null
  editingTaskIdx.value = -1
  taskEditForm.value = {
    task_name: '',
    owner: '',
    start_time: '',
    end_time: '',
    priority: '',
    isDone: false,
    note: ''
  }
  showTaskEditDialog.value = true
}

// 保存任务编辑
const saveTaskEdit = async () => {
  if (!taskEditForm.value.task_name) {
    toast.error(translateOr('incidents.detail.evidenceResponse.progressSync.columns.taskName', '任务名称') + ' ' + t('common.warning'))
    return
  }
  
  // 构建任务数据
  const taskData = {
    task_name: taskEditForm.value.task_name,
    owner: taskEditForm.value.owner || '',
    start_time: taskEditForm.value.start_time ? new Date(taskEditForm.value.start_time).toISOString() : null,
    end_time: taskEditForm.value.end_time ? new Date(taskEditForm.value.end_time).toISOString() : null,
    priority: taskEditForm.value.priority !== '' ? taskEditForm.value.priority : null,
    isDone: taskEditForm.value.isDone || false
  }
  
  // 如果是进展同步，添加note字段
  if (activeCardTab.value === 'progressSync') {
    taskData.note = taskEditForm.value.note || ''
  }
  
  if (editingTask.value) {
    // 编辑现有任务
    const taskUniqueId = getTaskUniqueId(editingTask.value, editingTaskIdx.value)
    
    // 更新任务数据
    const updatedTask = {
      ...editingTask.value,
      ...taskData
    }
    
    // 更新到 filteredProgressSyncTasks（这会触发响应式更新）
    const taskIndex = filteredProgressSyncTasks.value.findIndex(task => task.uniqueId === taskUniqueId)
    if (taskIndex !== -1) {
      Object.assign(filteredProgressSyncTasks.value[taskIndex], updatedTask)
    }
    
    // 同步更新到groupedTaskDetails
    updateTaskInGroupedDetails(updatedTask)
    
    // 如果是在进展同步中编辑任务，且任务有warroomId和task_id，调用modifyTask
    if (activeCardTab.value === 'progressSync' && updatedTask.warroomId && updatedTask.task_id) {
      try {
        const modifyParams = {
          project_uuid: updatedTask.warroomId,
          task_id: updatedTask.task_id,
          task_name: updatedTask.task_name,
          owner: updatedTask.owner || '',
          priority: updatedTask.priority !== null && updatedTask.priority !== undefined ? updatedTask.priority : null,
          status: updatedTask.isDone ? '已完成' : '待处理',
          start_time: updatedTask.start_time || null,
          end_time: updatedTask.end_time || null,
          notes: updatedTask.note || '' // 进展同步里加上note
        }
        
        await modifyTask(modifyParams)
        toast.success(translateOr('incidents.detail.evidenceResponse.progressSync.updateTaskSuccess', '任务更新成功'))
      } catch (error) {
        console.error('Failed to update task via dify API:', error)
        toast.error(translateOr('incidents.detail.evidenceResponse.progressSync.updateTaskError', '更新任务失败') + ': ' + (error?.message || 'Unknown error'))
      }
    }
    // 如果是在WR管理中编辑任务，且任务有warroomId和task_id，调用modifyTask（不加note）
    else if (leftPaneActiveTab.value === 'taskManagement' && updatedTask.warroomId && updatedTask.task_id) {
      try {
        const modifyParams = {
          project_uuid: updatedTask.warroomId,
          task_id: updatedTask.task_id,
          task_name: updatedTask.task_name,
          owner: updatedTask.owner || '',
          priority: updatedTask.priority !== null && updatedTask.priority !== undefined ? updatedTask.priority : null,
          status: updatedTask.isDone ? '已完成' : '待处理',
          start_time: updatedTask.start_time || null,
          end_time: updatedTask.end_time || null
          // WR管理task详情不用加note
        }
        
        await modifyTask(modifyParams)
        toast.success(translateOr('incidents.detail.eventGraph.updateTaskSuccess', '任务更新成功'))
      } catch (error) {
        console.error('Failed to update task via dify API:', error)
        toast.error(translateOr('incidents.detail.eventGraph.updateTaskError', '更新任务失败') + ': ' + (error?.message || 'Unknown error'))
      }
    }
  } else {
    // 创建新任务
    // 获取第一个 warroom 或默认 warroom
    const warroomIds = Object.keys(groupedTaskDetails.value)
    if (warroomIds.length === 0) {
      toast.error('请先绑定 Warroom')
      return
    }
    
    const defaultWarroomId = warroomIds[0]
    const warroomName = getWarroomName(defaultWarroomId)
    
    // 创建新任务对象
    const newTask = {
      ...taskData,
      warroomId: defaultWarroomId,
      warroomName: warroomName,
      uniqueId: `new_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    }
    
    // 添加到 filteredProgressSyncTasks
    filteredProgressSyncTasks.value.push(newTask)
    
    // 添加到 groupedTaskDetails
    if (!groupedTaskDetails.value[defaultWarroomId]) {
      groupedTaskDetails.value[defaultWarroomId] = []
    }
    
    const warroomDetail = groupedTaskDetails.value[defaultWarroomId]
    if (Array.isArray(warroomDetail)) {
      warroomDetail.push(newTask)
    } else if (warroomDetail && Array.isArray(warroomDetail.task_list)) {
      warroomDetail.task_list.push(newTask)
    } else {
      groupedTaskDetails.value[defaultWarroomId] = [newTask]
    }
    
    toast.success(t('common.operationSuccess'))
    // TODO: 调用后端API创建
  }
  
  // 重新计算指标
  calculateMetricsFromTasks(filteredProgressSyncTasks.value)
  
  // 关闭对话框
  closeTaskEditDialog()
}

// 删除进展同步任务
const deleteProgressSyncTask = (task, index) => {
  if (!task) return
  
  if (window.confirm(t('common.warning') + ': ' + t('common.delete') + '?')) {
    const taskUniqueId = getTaskUniqueId(task, index)
    
    // 从 filteredProgressSyncTasks 中删除
    const taskIndex = filteredProgressSyncTasks.value.findIndex(t => {
      const tId = getTaskUniqueId(t, filteredProgressSyncTasks.value.indexOf(t))
      return tId === taskUniqueId
    })
    if (taskIndex !== -1) {
      filteredProgressSyncTasks.value.splice(taskIndex, 1)
    }
    
    // 从 groupedTaskDetails 中删除
    if (task.warroomId && groupedTaskDetails.value[task.warroomId]) {
      const warroomDetail = groupedTaskDetails.value[task.warroomId]
      
      // 处理数组格式
      if (Array.isArray(warroomDetail)) {
        const indexInWarroom = warroomDetail.findIndex(t => {
          const tId = getTaskUniqueId(t, warroomDetail.indexOf(t))
          return tId === taskUniqueId
        })
        if (indexInWarroom !== -1) {
          warroomDetail.splice(indexInWarroom, 1)
        }
      }
      // 处理对象格式，包含 task_list 数组
      else if (warroomDetail && Array.isArray(warroomDetail.task_list)) {
        const indexInWarroom = warroomDetail.task_list.findIndex(t => {
          const tId = getTaskUniqueId(t, warroomDetail.task_list.indexOf(t))
          return tId === taskUniqueId
        })
        if (indexInWarroom !== -1) {
          warroomDetail.task_list.splice(indexInWarroom, 1)
        }
      }
    }
    
    // 重新计算指标
    calculateMetricsFromTasks(filteredProgressSyncTasks.value)
    
    toast.success(t('common.operationSuccess'))
    // TODO: 调用后端API删除
  }
}

// 获取warroom名称
const getWarroomName = (warroomId) => {
  if (!warroomId || !projectOptions.value.length) {
    return warroomId || ''
  }
  const option = projectOptions.value.find(opt => opt.value === String(warroomId))
  return option ? option.label : warroomId
}

// 检查warroom是否已选中
const isWarroomSelected = (warroomId) => {
  return selectedWarroomIds.value.includes(String(warroomId))
}

// 切换warroom选择状态
const toggleWarroomSelection = (warroomId) => {
  const id = String(warroomId)
  const index = selectedWarroomIds.value.indexOf(id)
  if (index > -1) {
    selectedWarroomIds.value.splice(index, 1)
  } else {
    selectedWarroomIds.value.push(id)
  }
}

// 移除warroom（从选中列表中移除，并执行解绑操作）
const removeWarroom = async (warroomId) => {
  const id = String(warroomId)
  const index = selectedWarroomIds.value.indexOf(id)
  if (index === -1) {
    return // 如果不在选中列表中，直接返回
  }

  // 如果事件ID不存在，只从本地状态移除（用于未保存的情况）
  if (!incident.value?.id) {
    selectedWarroomIds.value.splice(index, 1)
    const newGrouped = { ...groupedTaskDetails.value }
    delete newGrouped[id]
    groupedTaskDetails.value = newGrouped
    if (selectedWarroomIds.value.length === 0) {
      taskDetailLoaded.value = false
    }
    return
  }

  try {
    // 1. 从选中列表中移除
    selectedWarroomIds.value.splice(index, 1)

    // 2. 从分组任务详情中移除
    const newGrouped = { ...groupedTaskDetails.value }
    delete newGrouped[id]
    groupedTaskDetails.value = newGrouped

    // 3. 更新数据库
    await saveWarroomIdsForIncident(selectedWarroomIds.value)

    // 如果所有warroom都解绑了，重置状态
    if (selectedWarroomIds.value.length === 0) {
      taskDetailLoaded.value = false
    }
  } catch (error) {
    console.error('Failed to remove warroom:', error)
    // 如果操作失败，恢复选中状态
    if (!selectedWarroomIds.value.includes(id)) {
      selectedWarroomIds.value.push(id)
    }
    // 显示错误提示
    toast.error(error?.message || translateOr('incidents.detail.eventGraph.unbindError', '解绑失败'), 'Error')
  }
}

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
    // 自动获取项目列表（后台静默调用，不显示加载提示）
    loadProjectList().catch((err) => {
      console.error('Failed to auto load project list:', err)
    })
    // 如果后端已存储 project_uuid 或 warroom_ids，则自动填充并尝试加载任务详情
    // 兼容旧字段名task_id（向后兼容）
    const projectUuid = data.project_uuid || data.task_id
    if (projectUuid) {
      // 兼容旧格式：单个project_uuid
      if (typeof projectUuid === 'string') {
        selectedTaskId.value = projectUuid
        selectedWarroomIds.value = [projectUuid]
        // 初次进入时默认不展开编辑区域
        isEditingTaskId.value = false
        // 异步加载任务详情（失败时只在控制台打印）
        loadTaskDetail().catch((err) => {
          console.error('Failed to auto load task detail:', err)
        })
      } else if (Array.isArray(projectUuid) && projectUuid.length > 0) {
        // 新格式：多个project UUIDs
        selectedWarroomIds.value = projectUuid.map(id => String(id))
        // 初次进入时默认不展开编辑区域
        isEditingTaskId.value = false
        // 自动加载所有warroom的任务详情（不保存到数据库，因为已经保存过了）
        // 使用 nextTick 确保 DOM 更新后再加载
        nextTick(() => {
          loadWarroomDetailsOnly().catch((err) => {
            console.error('Failed to auto load warroom task details:', err)
          })
        })
      }
    }
    loadGraphData(graphPayload)
    
    // 加载影响服务数据（异步加载，不阻塞主流程）
    loadImpactedServices().catch((err) => {
      console.error('Failed to load impacted services:', err)
    })
    
    // 加载事件简报数据（异步加载，不阻塞主流程）
    loadIncidentBriefs().catch((err) => {
      console.error('Failed to load incident briefs:', err)
    })
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
      id: comment.id || comment.comment_id || index,
      comment_id: comment.comment_id || comment.id || index,
      author: author,
      authorInitials: authorInitials,
      avatarColor: avatarColor,
      time: formatDateTime(comment.create_time),
      content: comment.content || comment.message,
      create_time: comment.create_time,
      file: comment.file || null,  // 保留文件信息
      // note_type 是后端返回的动作类型；兼容旧字段 type
      type: comment.note_type || comment.type || null,
      note_type: comment.note_type || comment.type || null,
      // 标记评论是否存在于数据库中
      exists_in_db: comment.exists_in_db !== false  // 默认为true，如果明确标记为false则为false
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

const handlePostComment = async ({ comment, files, type }) => {
  if (!incident.value?.id) {
    toast.error(t('incidents.detail.comments.postError') || 'Failed to post comment: Incident ID does not exist', 'ERROR')
    return
  }
  
  try {
    const commentText = comment.trim()
    // 允许只有文件没有文本的情况
    if (!commentText && (!files || files.length === 0)) {
      return
    }
    
    // 调用 API 提交评论（包含文件）
    // 只有在成功后才刷新和清空，如果失败则不刷新，避免显示不存在的评论
    await postComment(incident.value.id, commentText, files || [], null, type || 'comment')
    
    // 清空输入框（组件会自动清空）
    newComment.value = ''
    
    // 仅刷新评论列表和时间线，避免触发其他接口
    await loadComments()
    
    // 显示成功提示
    toast.success(t('incidents.detail.comments.postSuccess') || 'Comment posted successfully', 'SUCCESS')
  } catch (error) {
    console.error('Failed to post comment:', error)
    const errorMessage = error?.response?.data?.error_message || error?.response?.data?.message || error?.message || t('incidents.detail.comments.postError') || 'Failed to post comment, please try again later'
    toast.error(errorMessage, 'ERROR')
    // 不刷新页面，避免显示后端创建失败的评论
  }
}

const handleUpdateComment = async ({ commentId, comment, noteType }) => {
  if (!incident.value?.id) {
    toast.error(t('incidents.detail.comments.updateError') || 'Failed to update comment: Incident ID does not exist', 'ERROR')
    return
  }
  
  try {
    await updateComment(incident.value.id, commentId, comment, noteType)
    
    // 仅刷新评论列表和时间线
    await loadComments()
    
    // 显示成功提示
    toast.success(t('incidents.detail.comments.updateSuccess') || 'Comment updated successfully', 'SUCCESS')
  } catch (error) {
    console.error('Failed to update comment:', error)
    const errorMessage = error?.response?.data?.error_message || error?.response?.data?.message || error?.message || t('incidents.detail.comments.updateError') || 'Failed to update comment, please try again later'
    toast.error(errorMessage, 'ERROR')
  }
}

// 处理删除评论（统一处理，根据 existsInDatabase 标志决定是否调用API）
const handleDeleteComment = async ({ commentId, existsInDatabase }) => {
  // 如果评论不存在于数据库中，直接从前端移除
  if (!existsInDatabase) {
    if (!incident.value?.comments) {
      return
    }
    incident.value.comments = incident.value.comments.filter(
      comment => (comment.id || comment.comment_id) !== commentId
    )
    toast.success(t('incidents.detail.comments.removeSuccess') || '评论已从列表中移除', 'SUCCESS')
    return
  }

  // 评论存在于数据库中，需要调用后端API删除
  if (!incident.value?.id) {
    toast.error(t('incidents.detail.comments.deleteError') || 'Failed to delete comment: Incident ID does not exist', 'ERROR')
    return
  }
  
  try {
    await deleteComment(incident.value.id, commentId)
    
    // 仅刷新评论列表和时间线
    await loadComments()
    
    // 显示成功提示
    toast.success(t('incidents.detail.comments.deleteSuccess') || 'Comment deleted successfully', 'SUCCESS')
  } catch (error) {
    console.error('Failed to delete comment:', error)
    const errorMessage = error?.response?.data?.error_message || error?.response?.data?.message || error?.message || t('incidents.detail.comments.deleteError') || 'Failed to delete comment, please try again later'
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

// 格式化任务日期时间
const formatServiceDateTime = (dateTimeString) => {
  if (!dateTimeString) return '--'
  // 尝试解析日期时间字符串，支持 ISO 格式和 "2026-01-31 03:11:19" 格式
  try {
    const date = parseToDate(dateTimeString)
    if (date) {
      return formatDateTime(date)
    }
  } catch (e) {
    // 如果解析失败，返回原始字符串
  }
  return dateTimeString || '--'
}

const formatTaskDateTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  // 尝试解析日期时间字符串，支持 "2026-01-31 03:11:19" 格式
  try {
    const date = parseToDate(dateTimeString)
    if (date) {
      return formatDateTime(date)
    }
  } catch (e) {
    // 如果解析失败，返回原始字符串
  }
}

// 获取通报类型标签
const getNotificationTypeLabel = (type) => {
  const typeMap = {
    'firstNotification': t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.types.firstNotification'),
    'closeNotification': t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.types.closeNotification'),
    'networkProtectionDaily': t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.types.networkProtectionDaily'),
    'other': t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.types.other')
  }
  return typeMap[type] || type
}

// 编辑通报
const editNotification = (index) => {
  if (index < 0 || index >= incidentNotifications.value.length) return
  
  const notification = incidentNotifications.value[index]
  editingNotificationIndex.value = index
  editingNotificationId.value = notification.id || null
  
  notificationForm.value = {
    event: notification.event || '',
    type: notification.type || 'firstNotification',
    owner: notification.owner || '',
    progress: notification.progress || '',
    nextPlan: notification.nextPlan || '',
    remark: notification.remark || ''
  }
  showAddNotificationDialog.value = true
}

// 删除通报
const deleteNotification = async (index) => {
  if (index < 0 || index >= incidentNotifications.value.length) return
  
  const notification = incidentNotifications.value[index]
  const notificationId = notification.id
  
  if (!notificationId) {
    // 如果没有ID，说明是本地数据，直接删除
    incidentNotifications.value.splice(index, 1)
    toast.success(t('common.operationSuccess'))
    return
  }
  
  // 打开删除确认对话框
  deletingNotificationIndex.value = index
  showDeleteNotificationDialog.value = true
}

// 确认删除事件通报
const confirmDeleteNotification = async () => {
  const index = deletingNotificationIndex.value
  if (index < 0 || index >= incidentNotifications.value.length) {
    showDeleteNotificationDialog.value = false
    return
  }
  
  const notification = incidentNotifications.value[index]
  const notificationId = notification.id
  
  if (!notificationId) {
    showDeleteNotificationDialog.value = false
    return
  }
  
  const incidentId = route.params.id
  if (!incidentId) {
    toast.error('事件ID不存在')
    showDeleteNotificationDialog.value = false
    return
  }
  
  isDeletingNotification.value = true
  try {
    await deleteIncidentBrief(incidentId, notificationId)
    incidentNotifications.value.splice(index, 1)
    toast.success(t('common.operationSuccess'))
    showDeleteNotificationDialog.value = false
    deletingNotificationIndex.value = -1
  } catch (error) {
    console.error('Failed to delete notification:', error)
    const errorMessage = error?.response?.data?.error_message || 
                        error?.response?.data?.message || 
                        error?.message || 
                        '删除失败，请重试'
    toast.error(errorMessage)
  } finally {
    isDeletingNotification.value = false
  }
}

// 取消删除事件通报
const cancelDeleteNotification = () => {
  showDeleteNotificationDialog.value = false
  deletingNotificationIndex.value = -1
}

// 保存通报（新增或编辑）
const saveNotification = async () => {
  if (!notificationForm.value.event) {
    toast.error(t('incidents.detail.evidenceResponse.cards.incidentBrief.notificationTable.columns.notificationEvent') + ' ' + t('common.warning'))
    return
  }
  
  const incidentId = route.params.id
  if (!incidentId) {
    toast.error('事件ID不存在')
    return
  }
  
  const notificationData = { ...notificationForm.value }
  
  try {
    let savedNotification
    if (editingNotificationId.value) {
      // 更新现有通报
      const response = await updateIncidentBrief(incidentId, editingNotificationId.value, notificationData)
      savedNotification = response.data
      // 更新本地列表
      const index = incidentNotifications.value.findIndex(n => n.id === editingNotificationId.value)
      if (index >= 0) {
        incidentNotifications.value[index] = savedNotification
      }
    } else {
      // 创建新通报
      const response = await createIncidentBrief(incidentId, notificationData)
      savedNotification = response.data
      // 添加到本地列表
      incidentNotifications.value.push(savedNotification)
    }
    
    // 重置表单
    resetNotificationForm()
    showAddNotificationDialog.value = false
    toast.success(t('common.operationSuccess'))
  } catch (error) {
    console.error('Failed to save notification:', error)
    const errorMessage = error?.response?.data?.error_message || 
                        error?.response?.data?.message || 
                        error?.message || 
                        '保存失败，请重试'
    toast.error(errorMessage)
  }
}

// 重置通报表单
const resetNotificationForm = () => {
  notificationForm.value = {
    event: '',
    type: 'firstNotification',
    owner: '',
    progress: '',
    nextPlan: '',
    remark: ''
  }
  editingNotificationIndex.value = -1
  editingNotificationId.value = null
}

// 取消新增/编辑通报
const cancelNotification = () => {
  resetNotificationForm()
  showAddNotificationDialog.value = false
}

// 保存影响服务（新增或编辑）
const saveService = async () => {
  if (!serviceForm.value.service) {
    toast.error(t('incidents.detail.evidenceResponse.services.columns.service') + ' ' + t('common.warning'))
    return
  }
  
  const incidentId = route.params.id
  if (!incidentId) {
    toast.error('事件ID不存在')
    return
  }
  
  const serviceData = { ...serviceForm.value }
  
  // 如果计划完成时间是datetime-local格式，转换为标准格式
  if (serviceData.plannedCompletionTime) {
    try {
      // 检查是否是datetime-local格式 (YYYY-MM-DDTHH:mm)
      if (serviceData.plannedCompletionTime.includes('T')) {
        const date = new Date(serviceData.plannedCompletionTime)
        if (!isNaN(date.getTime())) {
          serviceData.plannedCompletionTime = date.toISOString()
        }
      }
    } catch (e) {
      // 如果转换失败，保持原值
    }
  }
  
  try {
    let savedService
    if (editingServiceId.value) {
      // 更新现有服务
      const response = await updateImpactedService(incidentId, editingServiceId.value, serviceData)
      savedService = response.data
      // 更新本地列表
      const index = impactedServices.value.findIndex(s => s.id === editingServiceId.value)
      if (index >= 0) {
        impactedServices.value[index] = savedService
      }
    } else {
      // 创建新服务
      const response = await createImpactedService(incidentId, serviceData)
      savedService = response.data
      // 添加到本地列表
      impactedServices.value.push(savedService)
    }
    
    // 重置表单
    resetServiceForm()
    showAddServiceDialog.value = false
    toast.success(t('common.operationSuccess'))
  } catch (error) {
    console.error('Failed to save impacted service:', error)
    const errorMessage = error?.response?.data?.error_message || 
                        error?.response?.data?.message || 
                        error?.message || 
                        '保存失败，请重试'
    toast.error(errorMessage)
  }
}

// 重置影响服务表单
const resetServiceForm = () => {
  serviceForm.value = {
    service: '',
    measure: '',
    sla: '',
    plannedCompletionTime: '',
    owner: '',
    progress: '',
    remark: ''
  }
  editingServiceIndex.value = -1
  editingServiceId.value = null
}

// 编辑影响服务
const editService = (index) => {
  if (index < 0 || index >= impactedServices.value.length) return
  
  const service = impactedServices.value[index]
  editingServiceIndex.value = index
  editingServiceId.value = service.id || null
  
  // 格式化计划完成时间为datetime-local格式
  let formattedTime = ''
  if (service.plannedCompletionTime) {
    try {
      const date = new Date(service.plannedCompletionTime)
      if (!isNaN(date.getTime())) {
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')
        formattedTime = `${year}-${month}-${day}T${hours}:${minutes}`
      }
    } catch (e) {
      // 如果已经是正确格式，直接使用
      formattedTime = service.plannedCompletionTime
    }
  }
  
  serviceForm.value = {
    service: service.service || '',
    measure: service.measure || '',
    sla: service.sla || '',
    plannedCompletionTime: formattedTime,
    owner: service.owner || '',
    progress: service.progress || '',
    remark: service.remark || ''
  }
  
  showAddServiceDialog.value = true
}

// 加载影响服务列表
const loadImpactedServices = async () => {
  const incidentId = route.params.id
  if (!incidentId) {
    return
  }
  
  try {
    const response = await getImpactedServices(incidentId)
    // 响应拦截器已经返回了 response.data，所以这里直接使用 response.data
    impactedServices.value = response.data || []
  } catch (error) {
    console.error('Failed to load impacted services:', error)
    // 如果加载失败，不影响页面显示，只打印错误
    impactedServices.value = []
  }
}

// 加载事件简报列表
const loadIncidentBriefs = async () => {
  const incidentId = route.params.id
  if (!incidentId) {
    return
  }
  
  try {
    const response = await getIncidentBriefs(incidentId)
    // 响应拦截器已经返回了 response.data，所以这里直接使用 response.data
    incidentNotifications.value = response.data || []
  } catch (error) {
    console.error('Failed to load incident briefs:', error)
    // 如果加载失败，不影响页面显示，只打印错误
    incidentNotifications.value = []
  }
}

// 删除影响服务
const deleteService = async (index) => {
  if (index < 0 || index >= impactedServices.value.length) return
  
  const service = impactedServices.value[index]
  const serviceId = service.id
  
  if (!serviceId) {
    // 如果没有ID，说明是本地数据，直接删除
    impactedServices.value.splice(index, 1)
    toast.success(t('common.operationSuccess'))
    return
  }
  
  // 打开删除确认对话框
  deletingServiceIndex.value = index
  showDeleteServiceDialog.value = true
}

// 确认删除影响服务
const confirmDeleteService = async () => {
  const index = deletingServiceIndex.value
  if (index < 0 || index >= impactedServices.value.length) {
    showDeleteServiceDialog.value = false
    return
  }
  
  const service = impactedServices.value[index]
  const serviceId = service.id
  
  if (!serviceId) {
    showDeleteServiceDialog.value = false
    return
  }
  
  const incidentId = route.params.id
  if (!incidentId) {
    toast.error('事件ID不存在')
    showDeleteServiceDialog.value = false
    return
  }
  
  isDeletingService.value = true
  try {
    await deleteImpactedService(incidentId, serviceId)
    impactedServices.value.splice(index, 1)
    toast.success(t('common.operationSuccess'))
    showDeleteServiceDialog.value = false
    deletingServiceIndex.value = -1
  } catch (error) {
    console.error('Failed to delete impacted service:', error)
    const errorMessage = error?.response?.data?.error_message || 
                        error?.response?.data?.message || 
                        error?.message || 
                        '删除失败，请重试'
    toast.error(errorMessage)
  } finally {
    isDeletingService.value = false
  }
}

// 取消删除影响服务
const cancelDeleteService = () => {
  showDeleteServiceDialog.value = false
  deletingServiceIndex.value = -1
}

// 取消新增/编辑影响服务
const cancelService = () => {
  resetServiceForm()
  showAddServiceDialog.value = false
}

// 获取优先级标签
const getPriorityLabel = (priority) => {
  if (priority === undefined || priority === null) return ''
  const priorityMap = {
    0: translateOr('incidents.detail.eventGraph.priorityLow', 'Low'),
    1: translateOr('incidents.detail.eventGraph.priorityMedium', 'Medium'),
    2: translateOr('incidents.detail.eventGraph.priorityHigh', 'High'),
    3: translateOr('incidents.detail.eventGraph.priorityUrgent', 'Urgent')
  }
  return priorityMap[priority] || String(priority)
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

// 获取优先级配置（数字值：0=普通，1=紧急，2=非常紧急）
const getPriorityConfig = (priority) => {
  // 将优先级转换为数字
  let priorityNum = null
  
  // 明确检查 null、undefined 和空字符串
  if (priority === null || priority === undefined || priority === '') {
    return null
  }
  
  // 如果是数字（包括0）
  if (typeof priority === 'number') {
    priorityNum = priority
  } else if (typeof priority === 'string') {
    // 尝试解析数字（包括'0'）
    const num = parseInt(priority, 10)
    if (!isNaN(num) && num >= 0 && num <= 2) {
      priorityNum = num
    } else {
      // 处理文本格式的优先级
      const lowerPriority = priority.toLowerCase().trim()
      if (lowerPriority === '普通' || lowerPriority === 'normal' || lowerPriority === 'low') {
        priorityNum = 0
      } else if (lowerPriority === '紧急' || lowerPriority === 'urgent' || lowerPriority === 'high') {
        priorityNum = 1
      } else if (lowerPriority === '非常紧急' || lowerPriority === 'very urgent' || lowerPriority === 'critical') {
        priorityNum = 2
      }
    }
  }
  
  // 如果无法确定优先级值，返回null
  if (priorityNum === null || priorityNum < 0 || priorityNum > 2) {
    return null
  }
  
  const configs = {
    0: {
      label: t('incidents.detail.evidenceResponse.progressSync.priority.normal', '普通'),
      icon: 'circle',
      iconClass: 'text-blue-500 dark:text-blue-400',
      bgClass: 'bg-blue-50 dark:bg-blue-900/20',
      textClass: 'text-blue-700 dark:text-blue-300'
    },
    1: {
      label: t('incidents.detail.evidenceResponse.progressSync.priority.urgent', '紧急'),
      icon: 'flag',
      iconClass: 'text-orange-500 dark:text-orange-400',
      bgClass: 'bg-orange-50 dark:bg-orange-900/20',
      textClass: 'text-orange-700 dark:text-orange-300'
    },
    2: {
      label: t('incidents.detail.evidenceResponse.progressSync.priority.veryUrgent', '非常紧急'),
      icon: 'flag',
      iconClass: 'text-red-500 dark:text-red-400',
      bgClass: 'bg-red-50 dark:bg-red-900/20',
      textClass: 'text-red-700 dark:text-red-300'
    }
  }
  
  return configs[priorityNum] || null
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
    high: 'bg-red-500/20 dark:bg-red-500/20 ring-1 ring-inset ring-red-500/30 dark:ring-red-500/30',
    medium: 'bg-amber-500/20 dark:bg-amber-500/20 ring-1 ring-inset ring-amber-500/30 dark:ring-amber-500/30',
    low: 'bg-gray-300 dark:bg-slate-700'
  }
  return classes[severity] || classes.low
}

const getTimelineIconColorClass = (severity) => {
  const classes = {
    high: 'text-red-600 dark:text-red-400',
    medium: 'text-amber-600 dark:text-amber-400',
    low: 'text-gray-600 dark:text-slate-300'
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

const loadProjectList = async (keyword = '') => {
  loadingProjectList.value = true
  try {
    // 如果有关键字，使用关键字作为project_name进行模糊搜索；否则使用默认值'warroom'
    const project_name = keyword.trim() || 'warroom'
    const projectList = await getProjectList({ project_name })
    
    if (!Array.isArray(projectList)) {
      projectOptions.value = []
      return
    }
    
    projectOptions.value = projectList
      .map(item => ({
        label: item.projectName || item.projectUuid,
        value: item.projectUuid
      }))
      .filter(item => item.value)
  } catch (error) {
    console.error('Failed to load project list:', error)
    projectOptions.value = []
  } finally {
    loadingProjectList.value = false
  }
}

// 处理WR搜索输入（带防抖）
const handleWarroomSearch = () => {
  // 清除之前的定时器
  if (warroomSearchTimer.value) {
    clearTimeout(warroomSearchTimer.value)
  }
  
  // 设置新的防抖定时器（500ms）
  warroomSearchTimer.value = setTimeout(() => {
    const keyword = warroomSearchKeyword.value.trim()
    loadProjectList(keyword)
  }, 500)
}

// 选择任务ID（向后兼容）
const selectTaskId = (taskId) => {
  selectedTaskId.value = taskId
  showTaskIdDropdown.value = false
}

const toggleTaskIdDropdown = () => {
  showTaskIdDropdown.value = !showTaskIdDropdown.value
  // 当打开下拉框时，如果没有选项，加载默认列表
  if (showTaskIdDropdown.value) {
    if (projectOptions.value.length === 0) {
      // 如果没有选项，重置搜索关键字并加载默认列表
      warroomSearchKeyword.value = ''
      loadProjectList()
    } else if (warroomSearchKeyword.value.trim()) {
      // 如果有关键字，使用关键字重新搜索
      loadProjectList(warroomSearchKeyword.value.trim())
    }
  } else {
    // 关闭下拉框时，清空搜索关键字
    warroomSearchKeyword.value = ''
  }
}

// 关闭任务ID下拉框
const closeTaskIdDropdown = (event) => {
  // 如果点击的是下拉框内部，不关闭
  if (taskIdDropdownRef.value && taskIdDropdownRef.value.contains(event.target)) {
    return
  }
  showTaskIdDropdown.value = false
  // 关闭下拉框时，清空搜索关键字
  warroomSearchKeyword.value = ''
}

// 将当前warroom IDs写入本地数据库（与事件绑定）
const saveWarroomIdsForIncident = async (warroomIds) => {
  if (!incident.value?.id) {
    return
  }
  try {
    // 支持传入数组或单个值
    const ids = Array.isArray(warroomIds) ? warroomIds : (warroomIds ? [warroomIds] : [])
    await updateIncidentTask(incident.value.id, { warroom_ids: ids.length > 0 ? ids : null })
  } catch (error) {
    console.error('Failed to save warroom ids for incident:', error)
    throw error
  }
}

// 将当前任务 ID 写入本地数据库（与事件绑定）- 向后兼容函数
const saveTaskIdForIncident = async (taskId) => {
  if (!incident.value?.id) {
    return
  }
  try {
    await updateIncidentTask(incident.value.id, { task_id: taskId || null })
  } catch (error) {
    console.error('Failed to save task id for incident:', error)
  }
}

// 仅加载warroom任务详情（不保存到数据库，用于页面加载时恢复）
const loadWarroomDetailsOnly = async () => {
  if (selectedWarroomIds.value.length === 0) {
    return
  }

  loadingTaskDetail.value = true
  taskDetailError.value = ''
  taskDetailLoaded.value = false

  try {
    // 并行获取所有warroom的任务详情
    const taskDetailPromises = selectedWarroomIds.value.map(async (warroomId) => {
      try {
        // 使用project_uuid作为参数
        const result = await getTaskDetail({ project_uuid: String(warroomId).trim() })
        return { warroomId, taskDetail: result }
      } catch (error) {
        console.error(`Failed to load task detail for warroom ${warroomId}:`, error)
        return { warroomId, taskDetail: null, error: error?.message }
      }
    })

    const results = await Promise.all(taskDetailPromises)
    
    // 调试日志
    console.log('getTaskDetail results:', results)
    
    // 按warroom ID分组存储任务详情
    const grouped = {}
    results.forEach(({ warroomId, taskDetail, error }) => {
      if (error) {
        grouped[warroomId] = { error }
      } else {
        console.log(`Task detail for warroom ${warroomId}:`, taskDetail)
        grouped[warroomId] = taskDetail
      }
    })

    console.log('groupedTaskDetails:', grouped)
    groupedTaskDetails.value = grouped
    
    // 处理任务中的group_name，将其转换为tag并设置到taskTags中
    Object.keys(grouped).forEach(warroomId => {
      const warroomDetail = grouped[warroomId]
      if (!warroomDetail || warroomDetail.error) return
      
      // 处理数组格式的任务列表
      if (Array.isArray(warroomDetail)) {
        warroomDetail.forEach((task, index) => {
          if (task.group_name) {
            const uniqueId = getTaskUniqueId({ ...task, warroomId }, index)
            const tag = getGroupNameTag(task.group_name)
            if (tag !== undefined) {
              taskTags.value[uniqueId] = tag
            }
          }
        })
      }
      // 处理对象格式，包含 task_list 数组
      else if (warroomDetail.task_list && Array.isArray(warroomDetail.task_list)) {
        warroomDetail.task_list.forEach((task, index) => {
          if (task.group_name) {
            const uniqueId = getTaskUniqueId({ ...task, warroomId }, index)
            const tag = getGroupNameTag(task.group_name)
            if (tag !== undefined) {
              taskTags.value[uniqueId] = tag
            }
          }
        })
      }
    })
    
    taskDetailLoaded.value = true
  } catch (error) {
    console.error('Failed to load warroom task details:', error)
    taskDetailError.value = error?.message || translateOr('incidents.detail.eventGraph.bindWarroomError', '加载Warroom任务详情失败')
    taskDetailLoaded.value = true
  } finally {
    loadingTaskDetail.value = false
  }
}

// 绑定warroom：保存到数据库并加载任务详情
const bindWarrooms = async () => {
  if (selectedWarroomIds.value.length === 0) {
    taskDetailError.value = translateOr('incidents.detail.eventGraph.warroomRequired', '请至少选择一个Warroom')
    return
  }

  loadingTaskDetail.value = true
  taskDetailError.value = ''
  taskDetailLoaded.value = false

  try {
    // 1. 先保存到数据库
    await saveWarroomIdsForIncident(selectedWarroomIds.value)

    // 2. 加载任务详情
    await loadWarroomDetailsOnly()

    // 关闭下拉框
    showTaskIdDropdown.value = false
  } catch (error) {
    console.error('Failed to bind warrooms:', error)
    taskDetailError.value = error?.message || translateOr('incidents.detail.eventGraph.bindWarroomError', '绑定Warroom失败')
    taskDetailLoaded.value = true
  } finally {
    loadingTaskDetail.value = false
  }
}

// 解绑warroom：从数据库和本地状态中移除（调用removeWarroom执行完整解绑操作）
const unbindWarroom = async (warroomId) => {
  await removeWarroom(warroomId)
}

// 加载任务详情（向后兼容，保留原有逻辑）
const loadTaskDetail = async () => {
  if (!selectedTaskId.value || !selectedTaskId.value.trim()) {
    taskDetailError.value = translateOr('incidents.detail.eventGraph.taskIdRequired', 'Please select a task ID first')
    return
  }

  loadingTaskDetail.value = true
  taskDetailError.value = ''
  taskDetailLoaded.value = false
  taskDetail.value = null

  try {
    // 使用project_uuid作为参数
    const result = await getTaskDetail({ project_uuid: selectedTaskId.value.trim() })
    
    // 处理返回结果
    taskDetail.value = result
    taskDetailLoaded.value = true

    // 同步保存当前任务 ID 到本地数据库
    await saveTaskIdForIncident(selectedTaskId.value.trim())
  } catch (error) {
    console.error('Failed to load task detail:', error)
    taskDetailError.value = error?.message || translateOr('incidents.detail.eventGraph.taskDetailError', 'Failed to load task detail')
    taskDetail.value = null
    taskDetailLoaded.value = true
  } finally {
    loadingTaskDetail.value = false
  }
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

const toggleTaskEdit = () => {
  isEditingTaskId.value = !isEditingTaskId.value
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
      action: 'close',
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
    toast.success(t('incidents.detail.closeSuccess') || 'Incident closed successfully', 'SUCCESS')
    
    // 关闭对话框
    closeCloseDialog()
    
    // 重新加载事件详情
    await loadIncidentDetail()
  } catch (error) {
    console.error('Failed to close incident:', error)
    // 显示错误提示
    const errorMessage = error?.response?.data?.message || error?.message || t('incidents.detail.closeError') || 'Failed to close incident, please try again later'
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
    // 添加点击外部区域关闭下拉框的事件监听
    document.addEventListener('click', closeTaskIdDropdown)
  }
  // 监听Header发出的打开AI侧边栏事件
  window.addEventListener('open-ai-sidebar', handleOpenAISidebar)
  nextTick(() => {
    if (hasGraphData.value && activeTab.value === 'alertStory') {
      initD3Graph()
    }
  })
})
</script>

<style scoped>
/* 按钮样式 */
.btn-secondary,
.btn-primary,
.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  height: 2.5rem;
  padding: 0 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
}

.btn-secondary {
  min-width: 84px;
  background-color: rgb(229 231 235);
  color: rgb(55 65 81);
  font-weight: 700;
  letter-spacing: 0.015em;
}

.dark .btn-secondary {
  background-color: rgb(51 65 85);
  color: white;
}

.btn-secondary:hover {
  background-color: rgb(209 213 219);
}

.dark .btn-secondary:hover {
  background-color: rgb(71 85 105);
}

.btn-primary {
  min-width: 84px;
  background-color: #2b7cee;
  color: white;
  font-weight: 700;
  letter-spacing: 0.015em;
}

.btn-primary:hover {
  background-color: rgba(43, 124, 238, 0.9);
}

.btn-icon {
  background-color: rgb(229 231 235);
  color: rgb(55 65 81);
}

.dark .btn-icon {
  background-color: #2a3546;
  color: white;
}

.btn-icon:hover {
  background-color: rgb(209 213 219);
}

.dark .btn-icon:hover {
  background-color: #3c4a60;
}

.btn-icon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon:disabled:hover {
  background-color: rgb(229 231 235);
}

.dark .btn-icon:disabled:hover {
  background-color: #2a3546;
}

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
  color: #475569;
  transition: background-color 0.2s ease, color 0.2s ease;
  min-height: 2.25rem;
  min-width: 2.25rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.dark .graph-control-btn {
  color: #cbd5f5;
}

.graph-control-btn:hover {
  color: #1e293b;
  background-color: rgba(71, 85, 105, 0.2);
}

.dark .graph-control-btn:hover {
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
  stroke: #64748b;
  stroke-width: 1.4px;
  stroke-opacity: 0.5;
  transition: stroke 0.2s ease, stroke-width 0.2s ease, opacity 0.2s ease;
}

.dark .graph-link {
  stroke: #475569;
  stroke-opacity: 0.35;
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

.graph-node__icon {
  pointer-events: none;
  font-family: 'Material Symbols Outlined', sans-serif;
  font-weight: normal;
  font-style: normal;
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 48;
  user-select: none;
}

.graph-node__label {
  fill: #1e293b;
  font-size: 10px;
  font-weight: 500;
  pointer-events: none;
  text-transform: none;
}

.dark .graph-node__label {
  fill: rgba(255, 255, 255, 0.85);
  font-weight: normal;
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
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.65rem;
  transition: color 0.2s ease;
}

.dark .legend-entry {
  color: #94a3b8;
}

.legend-entry__dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 9999px;
  display: inline-flex;
}

.legend-entry--active {
  color: #1e293b;
}

.dark .legend-entry--active {
  color: #ffffff;
}

.legend-entry:hover {
  color: #334155;
}

.dark .legend-entry:hover {
  color: #e2e8f0;
}

.legend-entry__label {
  pointer-events: none;
}

.node-detail-resize-handle {
  width: 6px;
  cursor: col-resize;
  background: linear-gradient(to bottom, rgba(100, 116, 139, 0.2), rgba(100, 116, 139, 0.05));
  position: relative;
}

.dark .node-detail-resize-handle {
  background: linear-gradient(to bottom, rgba(148, 163, 184, 0.2), rgba(148, 163, 184, 0.05));
}

.node-detail-resize-handle::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 2px;
  height: 60px;
  background-color: rgba(100, 116, 139, 0.35);
  transform: translate(-50%, -50%);
}

.dark .node-detail-resize-handle::after {
  background-color: rgba(148, 163, 184, 0.35);
}

.detail-action-btn {
  color: #64748b;
  padding: 0.4rem;
  border-radius: 0.35rem;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.dark .detail-action-btn {
  color: #94a3b8;
}

.detail-action-btn:hover:not(:disabled) {
  color: #1e293b;
  background-color: rgba(71, 85, 105, 0.2);
}

.dark .detail-action-btn:hover:not(:disabled) {
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


