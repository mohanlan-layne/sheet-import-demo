# 项目标准操作流程（SOP）

> 适用对象：Sheet 导入助手（FastAPI 后端 + Vue 3 前端）的研发、测试、运维团队。
> 所有命令默认在仓库根目录（`sheet-import-demo/`）执行，使用 Linux/macOS Shell 语法。

## 1. 项目克隆与初始化

### 1.1 克隆仓库
- **命令**：
  ```bash
  git clone git@your.git.server:import-team/sheet-import-demo.git
  cd sheet-import-demo
  ```
- **注意事项**：确保本地 Git 版本 ≥ 2.34；若使用 HTTPS，请在第一次推送前执行 `git config credential.helper store` 以避免反复输入凭据。
- **判断标准**：`git status` 输出 `On branch main` 且工作区干净。

### 1.2 初始化 Python 后端环境
- **命令**：
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  pip install pytest build
  ```
- **注意事项**：推荐使用 Python 3.11；激活虚拟环境后终端前缀应显示 `(.venv)`；`pytest`、`build` 作为开发工具需要额外安装。
- **判断标准**：执行 `python -c "import fastapi"` 无报错，`pip list | grep fastapi` 显示版本号。

### 1.3 初始化 Vue 3 前端环境
- **命令**：
  ```bash
  corepack enable
  npm install
  ```
- **注意事项**：需要 Node.js ≥ 18.18（Vite 5 依赖）；如网络受限，可添加 `--registry=https://registry.npmmirror.com`；`corepack enable` 仅需执行一次确保 pnpm/yarn 兼容。
- **判断标准**：出现 `added XX packages`，`node_modules/` 目录生成且 `npm run build -- --mode staging` 可成功执行（无需完成，仅验证配置）。

### 1.4 初始化数据库（SQLite）
- **命令**：
  ```bash
  source .venv/bin/activate
  python - <<'PY'
  from database import initialize_database, get_database_url
  initialize_database()
  print(f"Database initialised at {get_database_url()}")
  PY
  ```
- **注意事项**：默认数据库路径为 `sqlite:///./sheet_import.db`；如需要自定义路径，先导出 `export DATABASE_URL=sqlite:///./.data/sheet_import_dev.db` 再执行初始化命令。
- **判断标准**：命令输出 `Database initialised at ...`，且本地生成 `sheet_import.db` 文件。


## 2. 本地开发流程

### 2.1 后端服务运行（FastAPI + Uvicorn）
1. **环境变量准备**
   ```bash
   cat <<'ENV' > .env.backend.local
   APP_ENV=dev
   DATABASE_URL=sqlite:///./sheet_import.db
   CORS_ORIGINS=http://localhost:5173
   LOG_LEVEL=INFO
   ENV
   export $(grep -v '^#' .env.backend.local | xargs)
   ```
   - **注意事项**：`.env.backend.local` 已在 `.gitignore`；若需要跨域多个来源，以逗号分隔：`CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173`。
   - **判断标准**：执行 `echo "$APP_ENV"` 返回 `dev`。
2. **启动命令**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   - **注意事项**：`--reload` 需开发环境使用；如端口被占用，可替换 `--port 9000` 并同步更新前端环境变量。
   - **判断标准**：浏览器访问 `http://localhost:8000/health` 返回 `{ "status": "ok" }`。

### 2.2 前端服务运行（Vue 3 + Vite）
1. **环境变量准备**
   ```bash
   cat <<'ENV' > .env.development.local
   VITE_API_BASE_URL=http://localhost:8000
   VITE_FEATURE_FLAG_HISTORY=true
   ENV
   ```
   - **注意事项**：所有 `VITE_` 前缀会在构建时注入；请勿提交 `.env.*.local`。
   - **判断标准**：执行 `grep VITE_API_BASE_URL .env.development.local` 显示正确地址。
2. **启动命令**
   ```bash
   npm run dev
   ```
   - **注意事项**：默认监听 `http://localhost:5173`；如需局域网联调，使用 `npm run dev -- --host`。
   - **判断标准**：终端出现 `Local: http://localhost:5173/` 且界面可正常加载 Excel 导入页面。

### 2.3 后端调试
- **命令**：
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
  ```
- **注意事项**：当需要断点调试，可通过 `uvicorn --reload --reload-dir services` 指定监听目录。
- **判断标准**：终端实时显示请求日志，调试器能够命中断点。

### 2.4 前端调试
- **命令**：
  ```bash
  npm run dev -- --open
  ```
- **注意事项**：启用浏览器 DevTools 的 Network/XHR 监控；如需与本地 mock 交互，可将 `VITE_API_BASE_URL=http://localhost:8000` 调整为 mock 地址。
- **判断标准**：页面加载后能够选取 Excel 并调用后台 `/imports` 接口。

### 2.5 环境变量说明
| 名称 | 作用域 | 示例值 | 说明 |
| ---- | ------ | ------ | ---- |
| `APP_ENV` | 后端 | `dev` / `test` / `prod` | 控制日志级别、CORS 策略等环境差异 |
| `DATABASE_URL` | 后端 | `sqlite:///./sheet_import.db` | 支持任意 SQLite 文件路径或 `sqlite:///:memory:` |
| `CORS_ORIGINS` | 后端 | `http://localhost:5173` | 以逗号分隔的允许跨域来源 |
| `LOG_LEVEL` | 后端 | `INFO` / `DEBUG` | Uvicorn 日志级别 |
| `VITE_API_BASE_URL` | 前端 | `http://localhost:8000` | 前端请求后端 API 的根路径 |
| `VITE_FEATURE_FLAG_HISTORY` | 前端 | `true` / `false` | 控制历史导入模块显隐 |

- **注意事项**：所有生产环境变量需通过密钥管理系统（如 Kubernetes Secret）注入；禁止将真实凭据提交到仓库。
- **判断标准**：执行 `env | grep -E '(APP_ENV|DATABASE_URL)'` 输出符合目标环境。


## 3. 单元测试流程

### 3.1 Python 后端测试
- **命令**：
  ```bash
  source .venv/bin/activate
  pytest -q
  ```
- **注意事项**：测试使用临时 SQLite 数据库并自动清理；如需查看详细日志，追加 `-vv`；确保在执行前已初始化虚拟环境。
- **判断标准**：终端显示 `3 passed`（或相应数量），退出码为 0。

### 3.2 前端静态检查
- **命令**：
  ```bash
  npm run type-check
  ```
- **注意事项**：当前项目暂无单元测试框架，使用 TypeScript 类型检查保证基础质量；如后续引入 Vitest/Jest，应补充脚本。
- **判断标准**：命令输出 `No type errors found`。


## 4. 构建流程

### 4.1 构建 Python 后端发行包
- **命令**：
  ```bash
  source .venv/bin/activate
  python -m build
  ```
- **注意事项**：构建结果位于 `dist/` 目录（wheel 与 sdist）；如仅部署 Docker，可跳过此步骤。
- **判断标准**：`dist/` 下生成 `.whl` 与 `.tar.gz` 且命令退出码为 0。

### 4.2 构建前端静态资源
- **命令**：
  ```bash
  npm run build
  ```
- **注意事项**：构建输出位于 `dist/`；如需区分环境，可使用 `npm run build -- --mode staging` 并配置 `.env.staging`。
- **判断标准**：命令结束时显示 `✓ built in XXX ms`，`dist/` 下生成 `index.html`、`assets/`。

### 4.3 构建产物校验
- **命令**：
  ```bash
  ls dist
  ```
- **注意事项**：分别检查后端与前端的 `dist/` 目录；前端构建将覆盖同名目录，建议将后端构建产物另存或在 Docker 中直接引用源码。
- **判断标准**：列出预期文件（如 `sheet_import_demo-0.1.0-py3-none-any.whl`、`assets/index-*.js`）。


## 5. Docker 镜像构建与推送

### 5.1 后端镜像 Dockerfile 示例
```dockerfile
# docker/backend.Dockerfile
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY api/ api/
COPY services/ services/
COPY repositories/ repositories/
COPY migrations/ migrations/
COPY database.py main.py ./
ENV APP_ENV=prod \
    LOG_LEVEL=INFO
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.2 前端镜像 Dockerfile 示例
```dockerfile
# docker/frontend.Dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* .npmrc* ./
RUN npm install
COPY src/ src/
COPY public/ public/
COPY index.html tsconfig*.json vite.config.ts ./
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

FROM nginx:1.25-alpine
COPY --from=build /app/dist/ /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 5.3 构建 → 打标签 → 推送
- **命令**：
  ```bash
  # 后端
  docker build -f docker/backend.Dockerfile -t harbor.example.com/import/sheet-backend:1.0.0 .
  docker push harbor.example.com/import/sheet-backend:1.0.0
  
  # 前端
  docker build -f docker/frontend.Dockerfile \
    --build-arg VITE_API_BASE_URL=https://api.dev.example.com \
    -t harbor.example.com/import/sheet-frontend:1.0.0 .
  docker push harbor.example.com/import/sheet-frontend:1.0.0
  ```
- **注意事项**：构建前确保 `docker login harbor.example.com` 成功；版本号采用 `日期+流水号` 形式便于回滚，例如 `20240501-01`。
- **判断标准**：`docker images | grep sheet-backend` 可看到新标签；Harbor UI 显示镜像已上传。


## 6. 发布流程（Dev → Test → PreProd → Prod）

```mermaid
graph LR
  A[开发提交] --> B[Dev 环境部署]
  B --> C[自动化验证]
  C --> D[Test 环境部署]
  D --> E[集成测试]
  E --> F[PreProd 部署]
  F --> G[验证 / UAT]
  G --> H[Prod 部署]
  H --> I[监控与回归]
```

### 6.1 Dev 环境（快速迭代）
1. **更新镜像标签**：编辑 `k8s/dev/values.yaml` 中 `image.tag`。
   ```bash
   yq -i '.backend.image.tag = "1.0.0"' k8s/dev/values.yaml
   ```
   - 注意：若未安装 `yq`，可手动编辑。
   - 判断：`grep image.tag k8s/dev/values.yaml` 显示目标版本。
2. **部署**：
   ```bash
   kubectl apply -f k8s/dev/
   kubectl -n sheet-dev rollout status deploy/sheet-backend
   kubectl -n sheet-dev rollout status deploy/sheet-frontend
   ```
   - 注意：Dev 环境使用 `kubectl` 直接 `apply`，无需审批。
   - 判断：`rollout status` 返回 `successfully rolled out`。
3. **验证**：访问 `https://sheet-dev.example.com`，手动导入样例 Excel 并确认 `/imports/history` 正常返回数据。

### 6.2 Test 环境（功能联调）
1. **提交变更单**：在 CI 中触发 `deploy-test` pipeline，参数包含镜像标签、变更说明。
2. **执行命令**：
   ```bash
   kubectl apply -k k8s/test
   kubectl -n sheet-test get pods
   ```
3. **注意事项**：Test 环境数据库使用持久化 SQLite（PVC）；部署前备份 `sheet_import.db`。
4. **判断标准**：测试团队执行 Postman 集合全部通过；`kubectl get ingress` 显示 `ADDRESS` 已更新。

### 6.3 PreProd 环境（准生产）
1. **审批**：需要 Tech Lead + QA 双人审批；审批记录附部署编号。
2. **部署命令**：
   ```bash
   helm upgrade --install sheet-import k8s/chart \
     --namespace sheet-preprod \
     --values k8s/preprod/values.yaml \
     --set backend.image.tag=1.0.0 \
     --set frontend.image.tag=1.0.0
   ```
3. **注意事项**：启用 `--atomic` 可在失败时回滚：`helm upgrade ... --atomic`。
4. **判断标准**：执行 `helm status sheet-import -n sheet-preprod` 显示 `STATUS: deployed`；Smoke Test（导入 10 行数据）成功。

### 6.4 Prod 环境（生产）
1. **变更审批**：需完成 CAB（Change Advisory Board）审批并记录在变更系统，附上回滚方案。
2. **部署命令**：
   ```bash
   helm upgrade --install sheet-import k8s/chart \
     --namespace sheet-prod \
     --values k8s/prod/values.yaml \
     --set backend.image.tag=1.0.0 \
     --set frontend.image.tag=1.0.0 \
     --atomic --history-max 10
   ```
3. **验证**：
   - 访问 `/health`：`curl -fsS https://api.example.com/health` 输出 `{ "status": "ok" }`。
   - 合成监控：Grafana Dashboard 指标（请求成功率 ≥ 99%、P95 延迟 < 200ms）。
4. **注意事项**：部署窗口需提前 24 小时通知业务；部署完成后 30 分钟内保持待命。
5. **判断标准**：`helm history sheet-import -n sheet-prod` 显示最新版本 `DEPLOYED`；APM 未出现异常告警。


## 7. Kubernetes 部署说明

### 7.1 示例 deployment.yaml（后端）
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sheet-backend
  namespace: sheet-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sheet-backend
  template:
    metadata:
      labels:
        app: sheet-backend
    spec:
      containers:
        - name: backend
          image: harbor.example.com/import/sheet-backend:1.0.0
          ports:
            - containerPort: 8000
          env:
            - name: APP_ENV
              valueFrom:
                configMapKeyRef:
                  name: sheet-backend-config
                  key: APP_ENV
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: sheet-backend-secret
                  key: DATABASE_URL
            - name: CORS_ORIGINS
              valueFrom:
                configMapKeyRef:
                  name: sheet-backend-config
                  key: CORS_ORIGINS
          volumeMounts:
            - name: sheet-db
              mountPath: /data
      volumes:
        - name: sheet-db
          persistentVolumeClaim:
            claimName: sheet-db-pvc
```

### 7.2 ConfigMap 挂载
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: sheet-backend-config
  namespace: sheet-prod
data:
  APP_ENV: prod
  CORS_ORIGINS: https://sheet.example.com
  LOG_LEVEL: INFO
```
- **注意事项**：ConfigMap 更改后需执行 `kubectl rollout restart deploy/sheet-backend` 生效。
- **判断标准**：`kubectl get configmap sheet-backend-config -n sheet-prod -o yaml` 显示最新内容。

### 7.3 Secret 配置
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: sheet-backend-secret
  namespace: sheet-prod
type: Opaque
stringData:
  DATABASE_URL: sqlite:////data/sheet_import_prod.db
```
- **注意事项**：使用 `kubectl create secret generic sheet-backend-secret --from-literal=DATABASE_URL=...`；生产环境需启用密文管理（如 KMS + SealedSecret）。
- **判断标准**：`kubectl get secret sheet-backend-secret -n sheet-prod` 显示 `Opaque` 类型，`DATA` 字段数量正确。

### 7.4 NFS PVC/Volume 说明
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: sheet-db-pvc
  namespace: sheet-prod
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 5Gi
  storageClassName: nfs-client
```
- **注意事项**：Calico 网络需允许到 NFS 服务端的流量（TCP/2049）；首次挂载会在 Pod `/data` 下写入 SQLite 文件。
- **判断标准**：`kubectl get pvc sheet-db-pvc -n sheet-prod` 状态为 `Bound`。

### 7.5 常用命令
- 应用配置：
  ```bash
  kubectl apply -f k8s/prod/backend-deployment.yaml
  ```
- 重启滚动：
  ```bash
  kubectl -n sheet-prod rollout restart deploy/sheet-backend
  ```
- 查看状态：
  ```bash
  kubectl -n sheet-prod get pods -l app=sheet-backend
  ```
- **注意事项**：滚动重启会先创建新 Pod 后逐步终止旧 Pod；确保就绪探针通过后再终止旧实例。
- **判断标准**：`kubectl rollout status` 报告成功；`READY` 列显示 `1/1`。


## 8. Rancher 发布流程
1. **登录**：访问 Rancher 控制台 `https://rancher.example.com`，使用企业 SSO 登录。
2. **选择集群**：进入 `Import-Cluster` → `sheet-prod` 命名空间。
3. **升级工作负载**：
   - 找到 `sheet-backend` Deployment，点击 **Edit YAML**。
   - 更新 `image` 标签为新版本，保存。
4. **前端更新**：类似操作更新 `sheet-frontend` Deployment。
5. **观察滚动状态**：在 Rancher 的 **Workload** 界面查看新 Pod 是否 `Active`。
6. **验证**：使用内置 Shell 执行 `curl http://localhost:8000/health`。
7. **注意事项**：Rancher 编辑 YAML 会自动生成历史版本；若遇到冲突，可选择 `Rollback` 按钮恢复上一版本。
8. **判断标准**：工作负载状态栏显示 `Active` 且没有警告图标。


## 9. 数据库升级流程

### 9.1 使用项目内迁移脚本
- **命令**：
  ```bash
  source .venv/bin/activate
  python - <<'PY'
  from database import configure_database, initialize_database
  configure_database("sqlite:////data/sheet_import_prod.db")
  initialize_database()
  print("Migrations applied")
  PY
  ```
- **注意事项**：在 Kubernetes 中执行需通过 `kubectl exec deployment/sheet-backend -- bash` 进入 Pod；执行前备份 `/data/sheet_import_prod.db`。
- **判断标准**：日志输出 `Migrations applied`，数据库中出现新表结构（可使用 `sqlite3 /data/... .schema` 查看）。

### 9.2 手动执行 SQL（紧急情况）
1. **导出最新迁移脚本**：查看 `migrations/v0002_create_import_logs.py`，复制 `upgrade` 函数内 SQL。
2. **执行命令**：
   ```bash
   sqlite3 /data/sheet_import_prod.db < scripts/manual_patch.sql
   ```
3. **注意事项**：手工执行需在变更单中记录具体 SQL；操作后应立即运行自动化迁移，确保版本同步。
4. **判断标准**：`sqlite3 /data/sheet_import_prod.db '.tables'` 能看到新表；回归测试通过。


## 10. 回滚 SOP

### 10.1 Docker 镜像回滚
- **命令**：
  ```bash
  docker pull harbor.example.com/import/sheet-backend:0.9.5
  helm upgrade sheet-import k8s/chart \
    --namespace sheet-prod \
    --set backend.image.tag=0.9.5 \
    --reuse-values --atomic
  ```
- **注意事项**：确认旧版本仍在 Harbor；回滚后需运行冒烟测试。
- **判断标准**：`helm history sheet-import` 最新记录显示 `0.9.5` 且状态 `DEPLOYED`。

### 10.2 Kubernetes 回滚
- **命令**：
  ```bash
  kubectl -n sheet-prod rollout undo deploy/sheet-backend --to-revision=12
  ```
- **注意事项**：确保 revision ID 正确，可通过 `kubectl rollout history deploy/sheet-backend` 查看。
- **判断标准**：`rollout status` 返回成功，Pod 恢复旧镜像标签。

### 10.3 配置回滚
- **命令**：
  ```bash
  kubectl -n sheet-prod get configmap sheet-backend-config -o yaml > backup.yaml
  kubectl -n sheet-prod apply -f backup.yaml
  ```
- **注意事项**：建议启用 GitOps（如 Argo CD）管理 ConfigMap/Secret，直接恢复 Git 历史版本。
- **判断标准**：配置恢复后执行 `kubectl rollout restart`，服务恢复正常。

### 10.4 数据回滚风险说明
- SQLite 不支持多版本快照；建议依赖 NFS 快照或文件级备份。
- 回滚步骤：
  1. 暂停写入：`kubectl scale deploy/sheet-backend --replicas=0`。
  2. 恢复备份文件：运维团队从备份系统恢复 `/data/sheet_import_prod.db`。
  3. 重启服务：`kubectl scale deploy/sheet-backend --replicas=3`。
- **注意事项**：数据回滚会丢失备份后的所有变更，需业务方确认。
- **判断标准**：恢复后对比备份校验哈希值一致；业务验证通过。


## 11. 灰度发布流程
1. **创建金丝雀 Deployment**：
   ```bash
   kubectl apply -f k8s/prod/backend-canary.yaml
   ```
   示例：`replicas: 1`，镜像标签为新版本。
2. **设置流量权重**（使用 Ingress NGINX）：
   ```yaml
   nginx.ingress.kubernetes.io/canary: "true"
   nginx.ingress.kubernetes.io/canary-weight: "20"
   ```
3. **观察指标**：Prometheus 监控新旧版本的错误率、延迟。
4. **提升权重**：若 30 分钟内无异常，将 `canary-weight` 从 20 → 50 → 100。
5. **完成切换**：删除旧 Deployment，更新主 Deployment 镜像。
6. **注意事项**：灰度期间保持两套镜像并存，确保数据库兼容；若发现异常立即将 `canary-weight` 设为 0。
7. **判断标准**：Grafana 面板显示请求成功率稳定 ≥ 99%，日志无异常。


## 12. 生产环境监控流程（Prometheus/Grafana）
1. **Prometheus 抓取**：确认 `ServiceMonitor` 已配置 `sheet-backend` 指标端点（例如 `:8000/metrics`，可通过中间件输出）。
2. **Grafana Dashboard**：关键指标包括：
   - QPS：`sum(rate(fastapi_requests_total[1m]))`
   - 成功率：`sum(rate(fastapi_requests_total{status="success"}[5m])) / sum(rate(fastapi_requests_total[5m]))`
   - 响应时间：`histogram_quantile(0.95, rate(fastapi_request_duration_seconds_bucket[5m]))`
3. **命令**：
   ```bash
   kubectl -n monitoring port-forward svc/grafana 3000:80
   ```
4. **注意事项**：如需导出面板，使用 Grafana 的 `JSON Model` 备份；报警规则需同步到 GitOps 仓库。
5. **判断标准**：监控面板无告警；报警渠道（飞书/Slack）未触发红色告警。


## 13. 日志查看与排错流程

### 13.1 后端日志（kubectl）
- **命令**：
  ```bash
  kubectl -n sheet-prod logs deploy/sheet-backend -f
  ```
- **注意事项**：如需查看历史日志，添加 `--since=1h`；可结合 `stern sheet-backend -n sheet-prod` 做多 Pod 聚合。
- **判断标准**：日志包含请求路径、状态码；错误堆栈信息完整。

### 13.2 ELK 检索
1. **Kibana 查询**：索引前缀 `sheet-prod-*`。
2. **搜索语句**：
   ```
   kubernetes.labels.app:"sheet-backend" AND level:ERROR
   ```
3. **注意事项**：为保护隐私，禁止在 Kibana 中导出包含敏感数据的日志；可使用 `fields` 限制输出列。
4. **判断标准**：查询结果能准确定位报错时间与请求 ID。

### 13.3 前端排错
- **命令**：
  ```bash
  kubectl -n sheet-prod logs deploy/sheet-frontend -f
  ```
- **注意事项**：静态站点通常日志较少；若需诊断用户问题，请结合浏览器控制台网络请求与后端日志对照。
- **判断标准**：确认 Nginx 访问日志返回 `200`；静态资源加载成功。


## 14. 10 分钟速查版 SOP

| 步骤 | 关键命令 | 验证方式 | 注意事项 |
| ---- | -------- | -------- | -------- |
| 克隆仓库 | `git clone ... && cd sheet-import-demo` | `git status` | 需要 Git 凭据 |
| Python 初始化 | `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` | `python -c "import fastapi"` | Python 3.11，激活虚拟环境 |
| 前端依赖 | `npm install` | `node_modules/` 生成 | Node ≥18，必要时换源 |
| 启动后端 | `uvicorn main:app --reload` | `curl http://localhost:8000/health` | 需设置 `.env.backend.local` |
| 启动前端 | `npm run dev` | 浏览器访问 `:5173` | `.env.development.local` 配置 API 地址 |
| 运行测试 | `pytest -q` / `npm run type-check` | `3 passed` / `No type errors` | 确保虚拟环境激活 |
| 前端构建 | `npm run build` | `dist/` 生成资源 | `--mode` 切换环境 |
| 构建镜像 | `docker build -f docker/backend.Dockerfile -t ...` | `docker images` 有标签 | 提前 `docker login` |
| Dev 部署 | `kubectl apply -f k8s/dev/` | `rollout status` 成功 | 直接 `apply`，无需审批 |
| Prod 部署 | `helm upgrade --install ... --atomic` | `helm history` 显示 `DEPLOYED` | 需 CAB 审批与回滚方案 |
| 灰度 | `kubectl apply backend-canary.yaml` | Grafana 指标稳定 | 注意数据库兼容 |
| 日志查看 | `kubectl logs deploy/sheet-backend -f` | 日志实时输出 | 可配合 Kibana 深入分析 |

> 完整 SOP 详见上方章节，建议打印并随部署手册一并归档。
