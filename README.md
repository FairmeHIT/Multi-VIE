# Multi-VIE
## Title
Visual Information Extraction from Documents via Classification-Guided Large Vision-Language Models
## Author
Huafu Li, Guo Chen, Jia Xia, LeiWang, Wei Du, YunYao, Weijun Peng & Liming Li
## Abstract
Visual information extraction (VIE) from visually rich documents remains challenging due to high layout variability and real-world impairments. Existing methods typically rely on sequential OCR pipelines or end-to-end models requiring extensive labeled data and layout-specific training, limiting their scalability. We propose a classification-guided large vision-language model (LVLM) framework for multi-type VIE that achieves high accuracy with minimal supervision. The approach decouples document-type classification from content extraction and employs in-context learning (ICL)-based dynamic prompt engineering to inject task-specific knowledge, enabling robust zero-shot inference across diverse layouts. From a theoretical perspective, the proposed method can be viewed as a form of conditional computation that reduces task uncertainty and improves information efficiency during prompt-based inference. Evaluated on a real-world bidding dataset with 16 certificate types, our zero-shot method (based on Qwen2.5-VL-7B) outperforms a strong supervised baseline by 18.35 percentage points in F1-score (86.43% vs. 68.08%) and 0.23 in normalized edit distance (0.90 vs. 0.67). Optional domain-specific fine-tuning further improves performance to 93.65% F1 and 0.93 NED, demonstrating superior robustness against seals, watermarks, and low contrast. The framework offers an efficient, scalable solution for complex document understanding in office automation. Code is available at https://github.com/FairmeHIT/Multi-VIE, and fine-tuned models at https://huggingface.co/fairme/Qwen2.5-VL-7B-SFT.

# Environment Setup
```
conda create -n multi_vie python==3.10 -y
conda activate multi_vie
pip install -r requirements.txt  
# For SFT 
cd app/sft/ 
pip install -r requirements.txt  
```

# Project File Description (Each file contains detailed annotations)
- app/data (Target images)
- app/data_process (Inference preprocessing)
- app/figure_classification (Image classification)
- app/llm (LVLM configuration and call interface)
- app/sft (LVLM fine-tuning data processing and fine-tuning)
- app/two_stage (OCR & UIE pipeline)
- config (Service configuration)