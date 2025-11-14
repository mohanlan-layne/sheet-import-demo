# 开发提示（Codex Guide）

为了方便后续在本项目继续扩展，这里提供给智能助手 / Copilot 类工具的开发提示：

1. **保持 TypeScript 化**：所有新逻辑应优先放在 `.ts` 或 `<script setup lang="ts">` 中，保持类型定义与推导完整。
2. **API 层集中在 `src/services`**：如需对接真实后端，请在 `src/services` 目录下新增模块，统一封装请求、错误处理与数据映射。
3. **表格交互相关逻辑**：
   - 优先复用 `DataSheet.vue` 中封装的事件回调。
   - 避免直接操作 DOM，所有对 Jspreadsheet 的调用请通过 `instance` 引用。
   - 若需新增工具栏按钮，请保持样式与现有按钮一致，存放在 `toolbar-actions` 容器内。
4. **样式约定**：全局样式集中在 `src/styles/main.css`，组件局部样式请使用 `scoped`，并优先采用现代渐变 / 阴影风格，保持整体视觉统一。
5. **提交前检查**：运行 `npm run build` 确保构建通过，必要时可执行 `npm run type-check` 进行类型检查。

> 若需新增文档或指南，请将中文说明作为首选语言，以保证团队成员阅读体验一致。
