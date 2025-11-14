<template>
  <aside class="panel">
    <header>
      <h2>智能搜索</h2>
      <p v-if="activeCell">当前单元格：{{ activeCell }}</p>
    </header>

    <div class="body">
      <p v-if="!query">选中单元格并输入内容以触发搜索。</p>
      <p v-else-if="isSearching">正在为“{{ query }}”搜索候选数据...</p>
      <template v-else>
        <ul v-if="suggestions.length" class="suggestion-list">
          <li v-for="item in suggestions" :key="item.id">
            <div class="summary">
              <strong>{{ item.label }}</strong>
              <small v-if="item.description">{{ item.description }}</small>
            </div>
            <button class="apply" type="button" @click="$emit('apply', item)">
              填入
            </button>
          </li>
        </ul>
        <p v-else>暂无匹配结果，可尝试调整关键词。</p>
      </template>
    </div>
  </aside>
</template>

<script setup lang="ts">
import type { Suggestion } from '@/types/sheet';

defineProps<{
  query: string;
  suggestions: Suggestion[];
  isSearching: boolean;
  activeCell: string;
}>();

defineEmits<{
  (e: 'apply', suggestion: Suggestion): void;
}>();
</script>

<style scoped>
.panel {
  background: rgba(15, 23, 42, 0.04);
  border-radius: 14px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-height: 320px;
}

header h2 {
  margin: 0 0 0.25rem;
  font-size: 1.1rem;
  color: #0f172a;
}

header p {
  margin: 0;
  color: #475569;
  font-size: 0.9rem;
}

.body {
  flex: 1;
  font-size: 0.95rem;
  color: #475569;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.suggestion-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.suggestion-list li {
  background: #fff;
  border-radius: 12px;
  padding: 0.85rem;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: flex-start;
}

.summary {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary strong {
  color: #0f172a;
}

.summary small {
  color: #64748b;
  font-size: 0.85rem;
}

button.apply {
  border: none;
  border-radius: 999px;
  padding: 0.45rem 1rem;
  background: linear-gradient(135deg, #f97316 0%, #fb7185 100%);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

button.apply:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(249, 115, 22, 0.25);
}
</style>
