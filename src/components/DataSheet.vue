<template>
  <section class="sheet-card">
    <div class="toolbar">
      <label class="upload-btn">
        <input
          ref="fileInput"
          type="file"
          accept=".xlsx,.xls,.csv"
          @change="handleFileChange"
        />
        <span>上传 Excel 文件</span>
      </label>
      <div class="toolbar-actions">
        <button class="ghost" @click="clearSheet" :disabled="!hasSheet">
          清空
        </button>
        <button class="primary" :disabled="!hasSheet || isSubmitting" @click="handleSubmit">
          {{ isSubmitting ? '提交中...' : '提交数据' }}
        </button>
      </div>
    </div>

    <div v-if="message" class="flash" :class="message.type">
      {{ message.text }}
    </div>

    <div class="content">
      <div class="spreadsheet" ref="sheetContainer"></div>
      <SuggestionPanel
        :active-cell="activeCellLabel"
        :is-searching="isSearching"
        :query="lastQuery"
        :suggestions="suggestions"
        @apply="applySuggestion"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { onBeforeUnmount, ref, computed } from 'vue';
import jspreadsheet, { JSpreadsheet } from 'jspreadsheet-ce';
import * as XLSX from 'xlsx';
import SuggestionPanel from './SuggestionPanel.vue';
import { searchRecords, submitSheet } from '@/services/api';
import type { Suggestion } from '@/types/sheet';

type Feedback = {
  type: 'success' | 'error';
  text: string;
};

const sheetContainer = ref<HTMLDivElement | null>(null);
const instance = ref<JSpreadsheet | null>(null);
const isSubmitting = ref(false);
const isSearching = ref(false);
const suggestions = ref<Suggestion[]>([]);
const lastQuery = ref('');
const activeCell = ref<{ x: number; y: number } | null>(null);
const message = ref<Feedback | null>(null);
let searchToken = 0;
let feedbackTimer: ReturnType<typeof setTimeout> | null = null;

const hasSheet = computed(() => instance.value !== null);
const activeCellLabel = computed(() => {
  if (!activeCell.value) return '';
  const column = toColumnLabel(activeCell.value.x);
  return `${column}${activeCell.value.y + 1}`;
});

function toColumnLabel(index: number): string {
  let label = '';
  let current = index;
  while (current >= 0) {
    label = String.fromCharCode((current % 26) + 65) + label;
    current = Math.floor(current / 26) - 1;
  }
  return label;
}

function showMessage(next: Feedback) {
  message.value = next;
  if (feedbackTimer) {
    clearTimeout(feedbackTimer);
  }
  feedbackTimer = setTimeout(() => {
    message.value = null;
    feedbackTimer = null;
  }, 3600);
}

function resetSheet() {
  if (instance.value) {
    instance.value.destroy();
    instance.value = null;
  }
  suggestions.value = [];
  lastQuery.value = '';
  activeCell.value = null;
  if (feedbackTimer) {
    clearTimeout(feedbackTimer);
    feedbackTimer = null;
  }
  message.value = null;
}

function clearSheet() {
  if (instance.value) {
    instance.value.setData([]);
  }
  suggestions.value = [];
  lastQuery.value = '';
  activeCell.value = null;
}

function createSheet(data: string[][]) {
  if (!sheetContainer.value) return;
  resetSheet();

  instance.value = jspreadsheet(sheetContainer.value, {
    data,
    tableOverflow: true,
    tableHeight: '520px',
    minDimensions: [Math.max(5, data[0]?.length ?? 1), Math.max(10, data.length)],
    onchange(_, __, x, y, value) {
      activeCell.value = { x, y };
      const text = value == null ? '' : String(value);
      handleSearch(text);
    },
    onselection(_, x1, y1) {
      activeCell.value = { x: x1, y: y1 };
      const value = instance.value?.getValueFromCoords(x1, y1) ?? '';
      handleSearch(value);
    }
  });
}

async function handleSearch(raw: string) {
  const query = raw.trim();
  lastQuery.value = query;
  if (!query) {
    suggestions.value = [];
    isSearching.value = false;
    return;
  }

  const token = ++searchToken;
  isSearching.value = true;
  try {
    const result = await searchRecords(query);
    if (token === searchToken) {
      suggestions.value = result;
    }
  } catch (error) {
    console.error('搜索失败', error);
    if (token === searchToken) {
      showMessage({
        type: 'error',
        text: '搜索服务暂不可用，请稍后重试'
      });
    }
  } finally {
    if (token === searchToken) {
      isSearching.value = false;
    }
  }
}

function applySuggestion(suggestion: Suggestion) {
  if (!instance.value || !activeCell.value) return;
  instance.value.setValueFromCoords(activeCell.value.x, activeCell.value.y, suggestion.value, true);
}

async function handleSubmit() {
  if (!instance.value) return;
  message.value = null;
  isSubmitting.value = true;
  try {
    const payload = instance.value.getData();
    const result = await submitSheet(payload);
    showMessage({
      type: 'success',
      text: result.message ?? '数据已提交并触发列表刷新'
    });
  } catch (error) {
    console.error('提交失败', error);
    showMessage({
      type: 'error',
      text: '提交失败，请检查网络或稍后再试'
    });
  } finally {
    isSubmitting.value = false;
  }
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const data = new Uint8Array(e.target?.result as ArrayBuffer);
    const workbook = XLSX.read(data, { type: 'array' });
    const worksheet = workbook.Sheets[workbook.SheetNames[0]];
    const rows = XLSX.utils.sheet_to_json<string[]>(worksheet, {
      header: 1,
      raw: false,
      blankrows: false,
      defval: ''
    }) as string[][];
    createSheet(rows);
  };
  reader.readAsArrayBuffer(file);
  target.value = '';
}

onBeforeUnmount(() => {
  resetSheet();
});
</script>

<style scoped>
.sheet-card {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.upload-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  border-radius: 999px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #fff;
  font-weight: 600;
  box-shadow: 0 10px 25px rgba(99, 102, 241, 0.3);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.upload-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 30px rgba(99, 102, 241, 0.35);
}

.upload-btn input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

button {
  border: none;
  border-radius: 999px;
  padding: 0.65rem 1.25rem;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

button.primary {
  background: linear-gradient(135deg, #14b8a6 0%, #0ea5e9 100%);
  color: #fff;
  box-shadow: 0 10px 25px rgba(14, 165, 233, 0.25);
}

button.primary:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 30px rgba(14, 165, 233, 0.3);
}

button.ghost {
  background: rgba(148, 163, 184, 0.15);
  color: #1f2937;
}

.flash {
  padding: 0.75rem 1rem;
  border-radius: 12px;
  font-weight: 500;
}

.flash.success {
  background: rgba(16, 185, 129, 0.15);
  color: #047857;
}

.flash.error {
  background: rgba(248, 113, 113, 0.15);
  color: #b91c1c;
}

.content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 1.25rem;
}

.spreadsheet {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.2);
}

@media (max-width: 1100px) {
  .content {
    grid-template-columns: 1fr;
  }
}
</style>
