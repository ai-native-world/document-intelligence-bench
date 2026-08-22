# 2026-08-22 市场模型 Canary

这是一轮机制验证和候选初筛，不是生产选型结论。

## 运行条件

- 语料：4 份仓库内合成中文图片，分别覆盖订单、巡检表、柱状图和分支流程图；
- 调用：6 个候选，每个案例调用一次，共 24 次真实 API 调用；
- 评分：事实准确性 45%、完整性 20%、证据可追溯性 25%、Schema 合规性 10%；
- 运行环境：Simi 主机直接调用厂商 API；没有修改 Simi 配置、模型路由或服务进程；
- 报告：[`report.json`](report.json) 不包含图片、密钥或模型原始输出；
- 成本：本轮没有锁定所有渠道的可比价格快照，因此报告为未知，而不是免费。

## 结果

| 候选 | 质量分 | 四例总时延 | 平均时延 | 失败 |
|---|---:|---:|---:|---:|
| Gemini 3.5 Flash | 100.00 | 32.59 s | 8.15 s | 0 |
| Kimi K2.5 via Model Studio | 100.00 | 22.55 s | 5.64 s | 0 |
| Qwen3.5 Plus | 100.00 | 86.08 s | 21.52 s | 0 |
| Qwen3.6 Plus | 100.00 | 59.32 s | 14.83 s | 0 |
| Qwen3-VL-Plus | 94.17 | 20.54 s | 5.14 s | 0 |
| DeepSeek V4 Flash Vision Exp | 88.75 | 15.88 s | 3.97 s | 0 |

质量第一名是四方并列，不存在唯一冠军。并列组中 Kimi K2.5 的本轮时延最低，但样本量只有 4，且每项只跑了一次。

Qwen3-VL-Plus 在流程图中把异常触发条件输出为带问号的原图文字，严格字段值校验未通过。DeepSeek 实验版在同一流程图中还把责任人和动作合并为“业务顾问补录”，并有一项图表证据引文不满足已锁定证据合同。所有候选在订单和巡检表案例均为 100 分。

## 能得出的结论

1. 这套方法能测出具体工作流差异，也能暴露评分器自身的问题。首轮因事实合同不完整而作废；第二轮原始输出经过修正后的确定性规则离线重评分，避免重复调用。
2. 这轮不支持把 Simi 的 `qwen3-vl-plus` 直接替换成 DeepSeek 实验版；DeepSeek 更快，但质量没有达到并列领先组。
3. Kimi K2.5 值得进入真实材料 shadow canary。生产切换前应使用获批、脱敏的客户材料，覆盖多页 PDF、低清扫描、复杂表格、手写批注和缺失字段，并至少重复三次测稳定性。
4. 下一轮应把“原生多模态”和“OCR/版面分析 → 文本模型”的完整链路作为不同候选，而不是只比较单模型。

## 可复核来源

- [DeepSeek API 更新记录](https://api-docs.deepseek.com/updates/)
- [DeepSeek API 价格说明](https://api-docs.deepseek.com/quick_start/pricing/)
- [Gemini 3.5 Flash 官方模型页](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash)
- [阿里云百炼模型列表](https://help.aliyun.com/zh/model-studio/models)
- [阿里云视觉理解文档](https://help.aliyun.com/zh/model-studio/vision)
