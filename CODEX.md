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

---

## 全项目 Codex Prompt 模板

```
你是 sheet-import-demo 项目的智能结对程序员，请严格遵循以下步骤：
1. 阅读 README.md 与 docs 目录下资料，了解需求背景、知识库结构（见 `docs/knowledge-base-structure.md`）以及可复用 Prompt（见 `docs/prompt-library.md`）。
2. 在动手前梳理本次任务涉及的模块：
   - 前端页面与组件位于 `src/components`、`src/App.vue`。
   - 服务层与模拟接口位于 `src/services`。
   - 类型定义集中在 `src/types`。
3. 采用 Vue 3 + TypeScript 约定，保持组件内 `<script setup lang="ts">` 与组合式 API 风格。
4. 涉及 Excel 解析请优先复用 SheetJS 与 Jspreadsheet 现有封装，避免重复造轮子。
5. 实现完成后：
   - 更新必要的文档（优先中文），确保知识库结构同步。
   - 给出测试建议，默认执行 `npm run build`。
6. 输出最终答复时提供变更概览、受影响文件、测试情况，并附上相关代码片段或命令结果。
```
