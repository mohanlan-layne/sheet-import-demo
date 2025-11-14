# Sheet 导入助手

一个基于 Vue 3 + Vite 的前端示例，展示如何将 Excel 数据导入、渲染到 Jspreadsheet CE，同时结合 API 搜索与数据提交的工作流，从而改善“手动查数 + Excel 批量导入”带来的效率与体验问题。

## 背景痛点

- Excel 中的多列数据需要人工逐条从后台系统查询再复制，效率极低。
- 传统“整表导入”在后端处理时，任意一行出错都会导致整次导入失败，用户体验差。

## 核心能力

1. **Excel 解析与展示**：使用 [SheetJS](https://sheetjs.com/) 读取本地 Excel/CSV 文件，将数据渲染到 [Jspreadsheet CE](https://jspreadsheet.com/) 生成的在线表格中，实现前端实时预览与编辑。
2. **单元格级别的智能搜索**：在单元格输入内容即刻触发模拟 API 搜索，给出候选记录，并支持一键填充以提升数据准确性。
3. **前端提交与反馈**：构造导入表格的 JSON 数据并发送至模拟的提交接口，提交成功后给出提示，可在真实业务中调用后端刷新列表。

## 技术栈

- [Vue 3](https://vuejs.org/) + [Vite](https://vitejs.dev/)
- [Jspreadsheet CE](https://jspreadsheet.com/) 与 [jsuites](https://jsuites.net/) 作为在线表格组件
- [SheetJS/xlsx](https://github.com/SheetJS/sheetjs) 解析 Excel 文件
- TypeScript 构建强类型开发体验

## 快速开始

```bash
# 安装依赖
npm install

# 本地开发
npm run dev

# 构建生产包
npm run build

# （可选）类型检查
npm run type-check
```

开发服务器默认监听 `http://localhost:5173`。

## 使用流程

1. 点击「上传 Excel 文件」选择本地数据文件（支持 `.xlsx`、`.xls`、`.csv`）。
2. 表格内容会被即时渲染到页面，可直接在单元格中编辑。
3. 选中任意单元格并输入关键字，右侧「智能搜索」面板会通过模拟接口返回候选数据，点击「填入」自动覆盖当前单元格。
4. 处理完成后点击「提交数据」，前端会调用模拟提交接口，并给出反馈提示；可在真实项目中替换为业务 API 并刷新列表页。

> **提示**：本项目提供的搜索与提交 API 位于 `src/services/api.ts`，为纯前端模拟实现，方便自定义对接实际后端。

## 目录结构

```
.
├── index.html
├── package.json
├── src
│   ├── App.vue
│   ├── components
│   │   ├── DataSheet.vue
│   │   └── SuggestionPanel.vue
│   ├── main.ts
│   ├── services
│   │   └── api.ts
│   ├── styles
│   │   └── main.css
│   └── types
│       └── sheet.ts
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

## TODO / 可扩展方向

- 接入真实的后台搜索与导入 API，并结合鉴权与错误处理策略。
- 根据业务字段定义数据模型与校验规则（必填项、格式校验、行级提示等）。
- 将导入成功后的数据写入本地缓存或草稿箱，以支持后续继续编辑。
- 引入单元格级别的批量操作，例如批量填充、粘贴多列等高级功能。

欢迎在此基础上拓展更多符合实际业务场景的功能。
