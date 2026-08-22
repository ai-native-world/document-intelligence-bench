# Enterprise workload v1

这是用于校验评测机制的脱敏合成语料，不是模型排行榜，也不包含客户材料。

## 工作负载合同

总分不是 12 个案例的简单平均，而是先计算各业务场景分数，再按固定权重汇总：

| 场景 | 权重 | 案例数 |
|---|---:|---:|
| 文档、表格与文字抽取 | 50% | 5 |
| 图表、流程与架构理解 | 12% | 2 |
| PPT / 营销视觉审查 | 10% | 1 |
| UI 视觉验收 | 10% | 1 |
| 一般图片理解 | 5% | 1 |
| 产品与现场照片 | 5% | 1 |
| 歧义识别与人工升级 | 8% | 1 |

覆盖门禁要求 PDF 案例不少于 25%、多资产案例不少于 33%、双语不少于 33%、低清不少于 16%、视觉审查不少于 25%，且所有案例都必须要求证据。

## 怎么使用

```bash
docbench benchmarks/enterprise-workload-v1/suite.yaml --validate-only
docbench benchmarks/enterprise-workload-v1/suite.yaml --output reports/workload-v1.json
```

第二条命令运行两条 fixture 链路，用来证明评分机制能识别针对关键场景的退化。`reference-pipeline` 的 100 分不是模型成绩，只是标准响应回放。

接入真实候选时，用不可变版本的 pipeline adapter 替换 `candidates`。完整链路应包含附件下载、格式识别、PDF 原生解析或拆页、模型推理、结构化校验和证据返回；不要只测模型接口。

## 决策边界

这个套件始终返回 `selection_ready: false`。要形成生产选型结论，还必须：

- 用经过授权、脱敏且能代表实际工作的材料进行影子评测；
- 至少做多轮独立重复，报告均值、方差与失败重试；
- 对 PPT、UI、产品照片和歧义场景进行匿名人类成对复核；
- 单独验证生产链路的附件摄取成功率、超时、路由和成本。

生成器是 [generate_workload_v1.py](../../scripts/generate_workload_v1.py)。需要 Pillow、ReportLab 与系统 Arial Unicode 字体；已生成资产随仓库提交，普通使用者无需运行生成器。
