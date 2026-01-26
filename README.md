# Multi-VIE
## Title
Visual Information Extraction from Documents via Classification-Guided Large Vision-Language Models
## Author
Huafu Li, Liming Li, Jia Xia, Wei Du
## Abstract
Visual information extraction (VIE), which converts unstructured document image data into structured text, has gained increasing attention in recent research. Prevailing methodologies typically adopt either sequential pipelines involving text recognition followed by information extraction or end-to-end trainable multimodal architectures that jointly process visual and textual information. However, both approaches generally require extensive annotated datasets and bespoke models tailored to specific layouts, limiting their generalizability for real-world images with high layout variability.  In this paper, we propose a robust VIE framework that leverages a classification-guided large vision–language model to extract key information from document images with arbitrary layouts. By proposing a coarse-to-fine multi-classification strategy together with carefully designed knowledge injection, the proposed framework achieves high accuracy and strong generalization for multi-VIE tasks.  Experimental results on a real-world bidding system demonstrate that, for arbitrary input images, our method outperforms baseline approaches by an average of 25.57\% in F1-score and 0.26 in average normalized edit distance. The proposed approach strikes an excellent balance between efficiency and performance, and exhibits substantial potential for complex document processing scenarios such as office automation and document understanding. The source code is publicly available on GitHub at https://github.com/FairmeHIT/Multi-VIE, and the fine-tuned models can be accessed via Hugging Face at https://huggingface.co/fairme/Qwen2.5-VL-7B-SFT.

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