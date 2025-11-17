# Video-AI 企业级部署完整指南

## 概述

本文档整合了Video-AI项目的完整部署方案，包括移动端应用架构、Docker容器化、Kubernetes编排、CI/CD流程、监控告警和运维指南。

---

## 📚 文档导航

### 核心文档

1. **移动端应用架构** (`docs/MOBILE_APP_ARCHITECTURE.md`)
   - 技术选型与推荐
   - Flutter开发工具链
   - UI/UX设计规范
   - API集成方案
   - 性能优化策略

2. **企业级部署方案** (`docs/ENTERPRISE_DEPLOYMENT.md`)
   - Docker容器化部署
   - Kubernetes编排配置
   - CI/CD自动化流程
   - 监控和日志系统
   - 安全配置指南

3. **扩展性设计** (`docs/SCALABILITY.md`)
   - 水平和垂直扩展
   - 负载均衡策略
   - 缓存架构
   - 数据库分片
   - 消息队列异步处理

4. **运维手册** (`docs/OPERATIONS_MANUAL.md`)
   - 安装和启动流程
   - 常见问题处理
   - 性能调优
   - 备份和恢复
   - 故障处理

### 配置文件

**Docker相关**
- `Dockerfile` - 应用镜像定义
- `docker-compose.yml` - 完整的容器编排配置
- `.env.example` - 环境变量示例

**Kubernetes相关** (`k8s/`)
- `namespace.yaml` - 命名空间配置
- `deployment.yaml` - 应用和Worker部署
- `service.yaml` - 服务暴露
- `hpa.yaml` - 自动扩缩容
- `pvc.yaml` - 持久化存储
- `configmap.yaml` - 配置管理

**CI/CD流程** (`.github/workflows/`)
- `deploy.yml` - 生产部署流程
- `test.yml` - 自动化测试

**监控和基础设施**
- `nginx.conf` - 反向代理配置
- `prometheus.yml` - 监控配置
- `rules/alerts.yml` - 告警规则

**数据库初始化** (`scripts/`)
- `init-db.sql` - PostgreSQL初始化
- `init-mongo.js` - MongoDB初始化

---

## 🚀 快速开始

### 方式1：使用Docker Compose (推荐用于开发和小型部署)

```bash
# 1. 克隆项目
git clone <repository-url>
cd video-ai

# 2. 配置环境变量
cp .env.example .env
nano .env  # 编辑必要的API密钥

# 3. 启动所有服务
docker-compose build
docker-compose up -d

# 4. 初始化数据库
docker-compose exec api python -m alembic upgrade head

# 5. 验证部署
curl http://localhost:8000/health
open http://localhost:8000/docs          # API文档
open http://localhost:3000                # Grafana (admin/admin)
open http://localhost:5601                # Kibana
```

### 方式2：使用Kubernetes (推荐用于生产)

```bash
# 1. 创建命名空间
kubectl apply -f k8s/namespace.yaml

# 2. 创建Secret（替换实际值）
kubectl create secret generic api-secrets \
  --from-literal=openai-key=sk-xxx \
  --from-literal=google-key=xxx \
  --from-literal=database-url=postgresql://... \
  -n video-ai

# 3. 部署应用
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# 4. 验证部署
kubectl get all -n video-ai
kubectl logs -f deployment/video-ai-api -n video-ai
```

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端层                                  │
│              Web | Mobile App | API Client                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
           ┌─────────────▼────────────────┐
           │    CDN & 负载均衡            │
           │  (Nginx / AWS ELB)           │
           └──────────────┬────────────────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
┌───▼──────┐      ┌──────▼─────┐      ┌──────▼──────┐
│ API      │      │ Celery     │      │ 静态资源    │
│ (3-10个) │      │ Workers    │      │ (CDN/S3)    │
└───┬──────┘      └──────┬─────┘      └─────────────┘
    │                    │
    │    ┌───────────────┼───────────────┐
    │    │               │               │
┌───▼────▼──┐      ┌─────▼──┐      ┌────▼─────┐
│ PostgreSQL │      │ Redis  │      │ MongoDB  │
│ (主从)    │      │ (缓存) │      │ (数据)   │
└───────────┘      └────────┘      └──────────┘
```

---

## 📊 部署清单

### 部署前检查

- [ ] API密钥已配置 (OpenAI, Google, Anthropic)
- [ ] 数据库密码已修改
- [ ] SSL/TLS证书已准备
- [ ] 备份策略已制定
- [ ] 监控告警已配置
- [ ] 日志聚合已启用

### Docker Compose部署

- [x] Dockerfile 已创建
- [x] docker-compose.yml 已配置
- [x] .env.example 已提供
- [x] nginx.conf 已配置
- [x] 初始化脚本已准备

### Kubernetes部署

- [x] namespace.yaml 已创建
- [x] deployment.yaml 已配置 (API + Workers)
- [x] service.yaml 已配置
- [x] hpa.yaml 已配置 (自动扩缩容)
- [x] pvc.yaml 已配置 (持久化存储)
- [x] configmap.yaml 已配置

### CI/CD流程

- [x] GitHub Actions deploy.yml 已配置
- [x] GitHub Actions test.yml 已配置
- [x] 自动化测试流程
- [x] 自动化构建和推送镜像
- [x] 自动化Kubernetes部署

### 监控和日志

- [x] Prometheus 配置已准备
- [x] Grafana 集成已配置
- [x] 告警规则已定义
- [x] Elasticsearch + Kibana 已集成
- [x] 日志聚合已配置

---

## 🔒 安全建议

### 必须配置

1. **SSL/TLS证书**
   ```bash
   # 使用Let's Encrypt获取免费证书
   certbot certonly --standalone -d api.video-ai.com
   ```

2. **API密钥管理**
   - 使用HashiCorp Vault存储密钥
   - 定期轮换密钥
   - 使用Kubernetes Secret管理

3. **网络隔离**
   - 配置Kubernetes Network Policy
   - 使用防火墙规则限制访问
   - 启用VPN访问

4. **访问控制**
   - 配置RBAC权限
   - 审计日志记录
   - 定期安全审计

### 定期维护

```bash
# 检查容器漏洞
docker scan video-ai:latest

# 检查依赖漏洞
pip-audit

# 检查代码静态分析
bandit -r src/

# 定期更新依赖
pip install --upgrade -r requirements.txt
```

---

## 📈 性能优化

### 关键指标

| 指标 | 目标 | 当前 |
|------|------|------|
| API响应时间 (p95) | < 1s | - |
| 错误率 | < 0.1% | - |
| CPU使用率 | < 70% | - |
| 内存使用率 | < 80% | - |
| 磁盘使用率 | < 90% | - |
| 视频处理成功率 | > 99% | - |

### 优化建议

1. **数据库优化**
   - 创建适当的索引
   - 启用查询缓存
   - 使用读写分离

2. **缓存优化**
   - 配置多层缓存 (L1内存, L2磁盘, L3网络)
   - 设置合理的过期时间
   - 实现缓存预热

3. **API优化**
   - 启用Gzip压缩
   - 使用连接池
   - 实现请求去重

4. **容器优化**
   - 调整资源限制
   - 配置自动扩缩容
   - 使用HPA based on metrics

---

## 🔄 升级流程

### 蓝绿部署

```bash
# 步骤1：部署新版本（不影响现有流量）
kubectl set image deployment/video-ai-api \
  api=video-ai:2.0.0 \
  --record

# 步骤2：验证新版本
kubectl rollout status deployment/video-ai-api

# 步骤3：如果出现问题，立即回滚
kubectl rollout undo deployment/video-ai-api
```

### 灰度部署

使用Istio VirtualService逐步切换流量：
- 第一阶段：5% → 新版本
- 第二阶段：50% → 新版本
- 第三阶段：100% → 新版本

---

## 🆘 故障处理

### 常见问题

#### API无法启动
```bash
# 查看详细日志
docker-compose logs api

# 检查数据库连接
docker-compose exec api python -c "from sqlalchemy import create_engine; engine = create_engine(os.getenv('DATABASE_URL'))"
```

#### 视频处理失败
```bash
# 检查Worker状态
docker-compose logs celery-worker-video

# 检查任务队列
docker-compose exec redis redis-cli LLEN celery
```

#### 磁盘空间不足
```bash
# 查看磁盘使用
df -h

# 清理过期数据
docker-compose exec postgres psql -U postgres -d video_ai -c "DELETE FROM videos WHERE created_at < NOW() - INTERVAL '30 days'"
```

---

## 📞 支持和反馈

- **文档**: 查看`docs/`目录下的完整文档
- **Issue**: 提交GitHub Issue报告问题
- **讨论**: 在GitHub Discussions中讨论功能
- **安全**: 通过安全漏洞报告流程上报安全问题

---

## 📋 部署完成清单

### 初始部署

- [ ] 环境变量配置完成
- [ ] 数据库初始化完成
- [ ] 应用成功启动
- [ ] API健康检查通过
- [ ] 监控系统工作正常
- [ ] 日志聚合启用

### 生产部署

- [ ] SSL/TLS证书已安装
- [ ] 负载均衡已配置
- [ ] 自动扩缩容已启用
- [ ] 备份策略已验证
- [ ] 灾难恢复计划已制定
- [ ] 团队培训已完成

### 持续运维

- [ ] 日志监控已启用
- [ ] 告警通知已配置
- [ ] 定期备份已执行
- [ ] 性能基准已建立
- [ ] 安全审计已完成
- [ ] 更新计划已制定

---

## 🎓 学习资源

### 核心技术

- **FastAPI**: https://fastapi.tiangolo.com/
- **Docker**: https://docs.docker.com/
- **Kubernetes**: https://kubernetes.io/docs/
- **Celery**: https://docs.celeryproject.io/

### 最佳实践

- **12 Factor App**: https://12factor.net/
- **Cloud Native**: https://www.cncf.io/
- **DevOps**: https://devops.com/

### 监控和日志

- **Prometheus**: https://prometheus.io/docs/
- **Grafana**: https://grafana.com/docs/grafana/
- **ELK Stack**: https://www.elastic.co/what-is/elk-stack

---

## 版本历史

- **v1.0** (2024-11-17) - 初始版本
  - 完整的Docker Compose部署方案
  - Kubernetes编排配置
  - CI/CD自动化流程
  - 监控告警系统
  - 完整的文档和指南

---

## 许可证

MIT License

---

**祝您部署成功！如有任何问题，请参考相关文档或提交Issue。**
