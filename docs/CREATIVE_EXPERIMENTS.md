# Creative Experiments

Compare creatives grouped by a declared variant using the latest feedback snapshot rates.

## Experiment specification

```json
{
  "experiment_id": "hook-01",
  "hypothesis": "Finished-product reveal hooks may encourage more shares",
  "variable_tested": "hook",
  "status": "running",
  "variants": [
    {"name": "reveal", "creative_ids": ["reel-01", "reel-02"]},
    {"name": "question", "creative_ids": ["reel-03", "reel-04"]}
  ]
}
```

## CLI

```bash
genforge-marketing radar experiment-report --experiment experiments/hook-01.json --feedback output/creative-feedback-report.json --output output/hook-01-report.json
```

Results are descriptive. The tool reports per-variant means and observed metric leaders but does not infer causality or statistical significance.
