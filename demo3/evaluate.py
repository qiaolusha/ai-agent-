"""
离线 RAG 评估脚本
输入: eval/qa_samples.json (20条 QA 样本)
输出: eval/report.csv + 控制台打印汇总指标

RAGAS 四大指标:
  - faithfulness:     回答是否完全基于检索到的 context（衡量幻觉）
  - answer_relevancy: 回答是否真正回答了问题
  - context_precision: 检索到的 context 有多少是有用的
  - context_recall:   有多少 ground_truth 信息被检索到
"""
import json
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from query import rag_query


def load_qa_samples(path: str = "eval/qa_samples.json") -> list[dict]:
    """
    样本格式:
    [
      {
        "question": "XXX 是什么？",
        "ground_truth": "标准参考答案..."
      },
      ...
    ]
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def collect_rag_outputs(samples: list[dict]) -> list[dict]:
    """对每个问题跑 RAG，收集回答和检索到的 contexts"""
    results = []
    for i, sample in enumerate(samples):
        print(f"[{i+1}/{len(samples)}] 正在处理: {sample['question'][:50]}...")
        try:
            output = rag_query(sample["question"])
            results.append({
                "question":     sample["question"],
                "answer":       output["answer"],
                "contexts":     output["contexts"],     # list[str]
                "ground_truth": sample["ground_truth"],
            })
        except Exception as e:
            print(f"  ⚠️ 跳过，错误: {e}")
    return results


def run_evaluation(output_path: str = "eval/report.csv"):
    """主评估函数"""
    # 1. 加载样本
    samples = load_qa_samples()
    print(f"[evaluate] 加载 {len(samples)} 条 QA 样本")

    # 2. 跑 RAG 收集输出
    rag_outputs = collect_rag_outputs(samples)
    print(f"[evaluate] RAG 推理完成，有效样本: {len(rag_outputs)} 条")

    # 3. 构建 RAGAS Dataset
    dataset = Dataset.from_list(rag_outputs)

    # 4. 运行评估（RAGAS 用 LLM 作为评估 judge）
    print("[evaluate] 开始 RAGAS 评估...")
    result = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,        # 忠实度：有无幻觉
            answer_relevancy,    # 答案相关性
            context_precision,   # 检索精度
            context_recall,      # 检索召回
        ],
    )

    # 5. 输出结果
    df = result.to_pandas()

    # 汇总指标
    print("\n" + "="*50)
    print("📊 RAGAS 评估报告汇总")
    print("="*50)
    summary_cols = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
    for col in summary_cols:
        if col in df.columns:
            print(f"  {col:25s}: {df[col].mean():.4f}")
    print("="*50)

    # 保存 CSV
    import os
    os.makedirs("eval", exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n✅ 详细报告已保存至: {output_path}")

    return df


if __name__ == "__main__":
    run_evaluation()
