<template>
  <div class="app-shell">
    <header class="app-header">
      <h1>Sheet 导入助手</h1>
      <p>
        通过 Excel 导入、在线校验和 API 搜索提升数据录入效率。
      </p>
    </header>
    <main>
      <DataSheet />
    </main>
    <footer class="app-footer">
      <small>构建于 Vue 3 · Vite · Jspreadsheet CE · SheetJS</small>
    </footer>
  </div>
</template>

<script setup lang="ts">
import DataSheet from '@/components/DataSheet.vue';
</script>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.app-header {
  text-align: center;
  background-color: #ffffffcc;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}

.app-header h1 {
  margin-bottom: 0.5rem;
  font-size: 2rem;
}

.app-header p {
  margin: 0 auto;
  max-width: 640px;
  color: #475569;
}

main {
  background-color: #ffffffcc;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.1);
}

.app-footer {
  text-align: center;
  color: #64748b;
}
</style>
