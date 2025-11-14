# 项目知识库结构设计

为便于后续沉淀和复用，本项目建议建立如下多层次知识库：

## 1. 代码知识库
- **源码快照**：按目录存储关键文件片段，如 `src/components/DataSheet.vue`、`src/services/api.ts`。
- **决策记录**：每次重要架构或交互调整的设计说明，命名格式为 `ADR-YYYYMMDD-主题.md`。
- **调试手册**：归档常见报错、调试 Prompt（参考 `docs/prompt-library.md`）以及排查流程。

## 2. 文档知识库
- **产品与交互文档**：包括业务流程、原型图链接、字段映射说明，放置于 `docs/product/`。
- **开发指南**：统一在 `README.md` 与 `CODEX.md` 中维护，补充扩展主题可在 `docs/guides/` 新增专题文章。
- **变更日志**：建议引入 `CHANGELOG.md` 记录版本演进。

## 3. API 知识库
- **接口规范**：在 `docs/api/` 下维护 `openapi.yaml` 或 `http.md`，描述参数、响应、示例。
- **模拟数据**：集中在 `src/services/__mocks__/`，便于前端联调与单元测试。
- **环境配置**：记录后端域名、鉴权方式，存于 `docs/api/environments.md`。

## 4. 知识库运营建议
- 采用统一标签体系（如 `frontend`, `api`, `infra`）提升检索效率。
- 建议配合企业知识库平台（如 Confluence、Notion）同步，保证跨团队共享。
- 定期（至少每月）回顾知识库结构，清理过期内容，维护最新最佳实践。
