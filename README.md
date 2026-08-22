# Document Intelligence Bench

一个面向真实工作流的多模态文档评测器。它比较的不是厂商榜单，而是同一批锁定材料经过模型、OCR 或组合链路后，业务事实是否准确、完整、可追溯，以及需要多少时间和成本。

## 为什么需要它

一次截图小测只能说明一个样本。可靠选型至少要固定五件事：

1. 同一份版本化语料；
2. 同一份输出 Schema；
3. 人工确认的标准事实与原文证据；
4. 确定性质量评分；
5. 模型版本、时延、Token 和成本证据。

本项目把事实准确性、完整性、证据定位和结构合规作为主分。AI 裁判是可选项、匿名化，且权重不得超过 25%。成本和时延不混入质量分：先过质量门槛，再比较效率。

## 快速开始

需要 Python 3.11+。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
docbench examples/material-analysis/suite.yaml --output reports/demo.json
```

仓库自带的是脱敏合成材料和已捕获响应，用来验证评测机制，不代表任何真实模型的能力。

## 接入真实模型

候选可使用 OpenAI Chat Completions 兼容接口。密钥只从环境变量读取：

```yaml
candidates:
  - id: qwen-vl
    name: 千问视觉方案
    version: qwen3-vl-plus@2026-08-22
    endpoint: openai://dashscope
    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    api_key_env: DASHSCOPE_API_KEY
    model: qwen3-vl-plus
    accepted_observed_models: [qwen3-vl-plus]
    response_format: json_object
    max_tokens: 4096
    timeout_seconds: 120
```

```bash
export DASHSCOPE_API_KEY='...'
docbench path/to/live-suite.yaml --output reports/live.json
```

CLI 会逐项打印 `case × candidate` 进度。报告默认不含模型原文；仅在脱敏调试语料上使用 `--include-outputs`，真实客户材料不要默认开启。

评分规则调整后，不必重新消耗模型调用。只要首次运行是在获批的脱敏语料上保留了输出，就可以离线重评分：

```bash
docbench path/to/live-suite.yaml \
  --rescore-report reports/live-with-outputs.json \
  --output reports/live-rescored.json
```

离线重评分只支持确定性评分套件；包含 AI 裁判的套件必须完整重跑。

也可以把复杂的 OCR、版面分析、PDF 拆页或多模型组合封装成内部 HTTP Adapter。Adapter 接收统一材料包，返回：

```json
{
  "model_version": "pipeline-name@immutable-version",
  "output": {
    "fields": {},
    "evidence": [],
    "uncertainties": []
  },
  "usage": {
    "input_tokens": 0,
    "output_tokens": 0,
    "cost_usd": 0
  },
  "latency_ms": 0
}
```

## 评测合同

- `suite.yaml`：案例、候选、权重和可选裁判；
- `output.schema.json`：所有候选必须遵守的输出结构；
- `facts`：字段路径、标准值、允许误差、证据页和证据文本；
- `version`：候选链路的不可变版本；
- `suite_digest / input_digest / output_digest`：防止不同语料或输出被混为一轮；
- 报告默认不保存原图和模型原文，只保存评分与摘要证据。

推荐至少覆盖清晰表格、复杂版面、多页材料、图表、流程图、低清扫描、手写批注、歧义和缺失字段。关键字段应设为零容忍 Gate；不要用一个总平均分掩盖致命错误。

## 安全边界

运行 live suite 会把每个案例发送给所有候选端点，并可能把标准事实及候选输出发送给 AI 裁判。请先确认材料分类和端点授权。详细要求见 [SECURITY.md](SECURITY.md)。

## 当前边界

- 当前内建 live adapter 处理单张图片；PDF 最佳实践是将“原生 PDF”与“统一拆页成图片”作为两个不同候选链路评测。
- 合成样本只验证机制；真实选型需要客户授权语料、人类标准答案和复核一致性。
- 本项目不给模型厂商做静态排名，结论只对具体 suite、模型版本和调用参数有效。

2026-08-22 的首轮市场 canary 使用 4 份合成中文材料，比较 6 个多模态模型与 1 条 OCR+文本模型链路，共 28 次真实 API 调用。四个候选质量并列，不能据此直接替换生产模型；完整结果和限制见 [benchmark results](benchmarks/2026-08-market-canary/RESULTS.md)。

## License

Apache-2.0
