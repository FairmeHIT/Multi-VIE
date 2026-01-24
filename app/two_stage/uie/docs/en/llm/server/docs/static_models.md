## Static Graph Model Download Support

* Static graph models now support DeepSeek series, Qwen series, llama series, etc. The detailed supported list is as follows:

### DeepSeekV2

| Model Name | Static Graph Download model_name |
|:-----------|:---------------------------------:|
| deepseek-ai/DeepSeek-V2-Chat              | 🚧 |
| deepseek-ai/DeepSeek-V2-Lite-Chat         | 🚧 |

### DeepSeekV3

| Model Name | Static Graph Download model_name |
|:-----------|:---------------------------------:|
| deepseek-ai/DeepSeek-V3                   | 🚧 |

### DeepSeekR1
Deployment Hardware Requirements:
- Except MTP models and Fp8 models, the minimum supported architecture is SM80 (Machines: A100/A800) requiring CUDA 11.8+
- DeepSeek-R1-MTP and Fp8 models require SM90 (Machines: H800) and CUDA 12.4+

| Model Name | Precision | MTP | Nodes | Static Graph Download model_name |
|:-----------|:---------:|:---:|:-----:|:---------------------------------:|
| deepseek-ai/DeepSeek-R1  |weight_only_int4|No|1| deepseek-ai/DeepSeek-R1/weight_only_int4 |
| deepseek-ai/DeepSeek-R1  |weight_only_int4|Yes|1| deepseek-ai/DeepSeek-R1-MTP/weight_only_int4 |
| deepseek-ai/DeepSeek-R1  |weight_only_int8|No|2| deepseek-ai/DeepSeek-R1-2nodes/weight_only_int8 |
| deepseek-ai/DeepSeek-R1  |weight_only_int8|Yes|2| deepseek-ai/DeepSeek-R1-MTP-2nodes/weight_only_int8 |
| deepseek-ai/DeepSeek-R1  |a8w8_fp8|No|2| deepseek-ai/DeepSeek-R1-2nodes/a8w8_fp8|
| deepseek-ai/DeepSeek-R1  |a8w8_fp8|Yes|2| deepseek-ai/DeepSeek-R1-MTP-2nodes/a8w8_fp8|
| deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B |weight_only_int8|-|-| deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B/weight_only_int8 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-7B   |weight_only_int8|-|-|deepseek-ai/DeepSeek-R1-Distill-Qwen-7B/weight_only_int8 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-14B  |weight_only_int8|-|-|deepseek-ai/DeepSeek-R1-Distill-Qwen-14B/weight_only_int8 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-32B  |weight_only_int8|-|-|deepseek-ai/DeepSeek-R1-Distill-Qwen-32B/weight_only_int8 |
| deepseek-ai/DeepSeek-R1-Distill-Llama-8B  |weight_only_int8|-|-|deepseek-ai/DeepSeek-R1-Distill-Llama-8B/weight_only_int8 |
| deepseek-ai/DeepSeek-R1-Distill-Llama-70B |weight_only_int8|-|-|deepseek-ai/DeepSeek-R1-Distill-Llama-70B/weight_only_int8 |


### LLaMA

| Model Name | Static Graph Download model_name |
|:-----------|:---------------------------------:|
| facebook/llama-7b | 🚧 |
| facebook/llama-13b | 🚧 |
| facebook/llama-30b | 🚧 |
| facebook/llama-65b | 🚧 |

### Llama2

| Model Name | Static Graph Download model_name |
|:-----------|:---------------------------------:|
| meta-llama/Llama-2-7b | 🚧 |
| meta-llama/Llama-2-7b-chat | 🚧 |
| meta-llama/Llama-2-13b | 🚧 |
| meta-llama/Llama-2-13b-chat | 🚧 |
| meta-llama/Llama-2-70b | 🚧 |
| meta-llama/Llama-2-70b-chat | 🚧 |

### Llama3
Deployment Hardware Requirements:
- Append-Attn:
  - Minimum supported architecture: SM80 (A100/A800)
  - Requires CUDA 11.8+
- Block-Attn:
  - Minimum supported architecture: SM70 (V100)
  - Requires CUDA 11.8+


| Model Name | Static Graph Download model_name |
|:-----------|:---------------------------------:|
| meta-llama/Meta-Llama-3-8B | 🚧 |
| meta-llama/Meta-Llama-3-8B-Instruct |meta-llama/Meta-Llama-3-8B-Instruct-Append-Attn/bfloat16,meta-llama/Meta-Llama-3-8B-Instruct-Block-Attn/float16|
| meta-llama/Meta-Llama-3-70B | 🚧 |
| meta-llama/Meta-Llama-3-70B-Instruct | 🚧 |

### Llama3.1

| Model Name | Static Graph Download model_name |
|:-----------|:---------------------------------:|
| meta-llama/Meta-Llama-3.1-8B | 🚧 |
| meta-llama/Meta-Llama-3.1-8B-Instruct | 🚧 |
| meta-llama/Meta-Llama-3.1-70B | 🚧 |
| meta-llama/Meta-Llama-3.1-70B-Instruct | 🚧 |
| meta-llama/Meta-Llama-3.1-405B | 🚧 |
| meta-llama/Meta-Llama-3.1-405B-Instruct | 🚧 |
| meta-llama/Llama-Guard-3-8B | 🚧 |

### Llama3.2

| Model Name | Static Graph Download model_name |
|:-----------|:---------------------------------:|
| meta-llama/Llama-3.2-1B | 🚧 |
| meta-llama/Llama-3.2-1B-Instruct | 🚧 |
| meta-llama/Llama-3.2-3B | 🚧 |
| meta-llama/Llama-3.2-3B-Instruct | 🚧 |
| meta-llama/Llama-Guard-3-1B | 🚧 |

### Llama3.3

| Model Name | Static Graph Download model_name |
|:-----------|:---------------------------------:|
| meta-llama/Llama-3.3-70B-Instruct | 🚧 |


### Mixtral

| Model Name | Static Graph Download model_name |
|:-----------|:---------------------------------:|
| mistralai/Mixtral-8x7B-Instruct-v0.1 | 🚧 |

### Qwen

| Model Name | Static Graph Download model_name |
|:-----------|:---------------------------------:|
| qwen/qwen-7b | 🚧 |
| qwen/qwen-7b-chat | 🚧 |
| qwen/qwen-14b | 🚧 |
| qwen/qwen-14b-chat | 🚧 |
| qwen/qwen-72b | 🚧 |
| qwen/qwen-72b-chat | 🚧 |

### Qwen1.5
Deployment Hardware Requirements:
- Block-Attn:
  - Minimum supported architecture: SM70 (V100)
  - Requires CUDA 11.8+

| Model Name | Static Graph Download model_name |
|:-----------|:---------------------------------:|
| Qwen/Qwen1.5-0.5B | Qwen/Qwen1.5-0.5B-Block-Attn/bfloat16,Qwen/Qwen1.5-0.5B-Block-Attn/float16 |
| Qwen/Qwen1.5-0.5B-Chat | 🚧 |
| Qwen/Qwen1.5-1.8B | 🚧 |
| Qwen/Qwen1.5-1.8B-Chat | 🚧 |
| Qwen/Qwen1.5-4B | 🚧 |
| Qwen/Qwen1.5-4B-Chat | 🚧 |
| Qwen/Qwen1.5-7B | 🚧 |
| Qwen/Qwen1.5-7B-Chat | 🚧 |
| Qwen/Qwen1.5-14B | 🚧 |
| Qwen/Qwen1.5-14B-Chat | 🚧 |
| Qwen/Qwen1.5-32B | 🚧 |
| Qwen/Qwen1.5-32B-Chat | 🚧 |
| Qwen/Qwen1.5-72B | 🚧 |
| Qwen/Qwen1.5-72B-Chat | 🚧 |
| Qwen/Qwen1.5-110B | 🚧 |
| Qwen/Qwen1.5-110B-Chat | 🚧 |
| Qwen/Qwen1.5-MoE-A2.7B | 🚧 |
| Qwen/Qwen1.5-MoE-A2.7B-Chat | 🚧 |

### Qwen2
Deployment Hardware Requirements:
- Append-Attn:
  - Minimum supported architecture: SM80 (A100/A800)
  - Requires CUDA 11.8+
- Block-Attn:
  - Minimum supported architecture: SM70 (V100)
  - Requires CUDA 11.8+

| Model Name | Static Graph Download model_name |
|:-----------|:---------------------------------:|
| Qwen/Qwen2-0.5B | 🚧 |
| Qwen/Qwen2-0.5B-Instruct | 🚧 |
| Qwen/Qwen2-1.5B | 🚧 |
| Qwen/Qwen2-1.5B-Instruct | Qwen/Qwen2-1.5B-Instruct-Append-Attn/bfloat16, Qwen/Qwen2-1.5B-Instruct-Block-Attn/float16|
| Qwen/Qwen2-7B | 🚧 |
| Qwen/Qwen2-7B-Instruct | 🚧 |
| Qwen/Qwen2-72B | 🚧 |
| Qwen/Qwen2-72B-Instruct | 🚧 |
| Qwen/Qwen2-57B-A14B | 🚧 |
| Qwen/Qwen2-57B-A14B-Instruct | 🚧 |

### Qwen2-Math

| Model Name | Static Graph Download model_name |
|:-----------|:---------------------------------:|
| Qwen/Qwen2-Math-1.5B | 🚧 |
| Qwen/Qwen2-Math-1.5B-Instruct | 🚧 |
| Qwen/Qwen2-Math-7B | 🚧 |
| Qwen/Qwen2-Math-7B-Instruct | 🚧 |
| Qwen/Qwen2-Math-72B | 🚧 |
| Qwen/Qwen2-Math-72B-Instruct | 🚧 |
| Qwen/Qwen2-Math-RM-72B | 🚧 |

### Qwen2.5

| Model Name | Static Graph Download model_name |
|:-----------|:---------------------------------:|
| Qwen/Qwen2.5-0.5B | 🚧 |
| Qwen/Qwen2.5-0.5B-Instruct | 🚧 |
| Qwen/Qwen2.5-1.5B | 🚧 |
| Qwen/Qwen2.5-1.5B-Instruct | 🚧 |
| Qwen/Qwen2.5-3B | 🚧 |
| Qwen/Qwen2.5-3B-Instruct | 🚧 |
| Qwen/Qwen2.5-7B | 🚧 |
| Qwen/Qwen2.5-7B-Instruct | 🚧 |
| Qwen/Qwen2.5-14B | 🚧 |
| Qwen/Qwen2.5-14B-Instruct | 🚧 |
| Qwen/Qwen2.5-32B | 🚧 |
| Qwen/Qwen2.5-32B-Instruct | 🚧 |
| Qwen/Qwen2.5-72B | 🚧 |
| Qwen/Qwen2.5-72B-Instruct | 🚧 |

### Qwen2.5-Math

| Model Name | Static Graph Download model_name |
|:-----------|:---------------------------------:|
| Qwen/Qwen2.5-Math-1.5B | 🚧 |
| Qwen/Qwen2.5-Math-1.5B-Instruct | 🚧 |
| Qwen/Qwen2.5-Math-7B | 🚧 |
| Qwen/Qwen2.5-Math-7B-Instruct | 🚧 |
| Qwen/Qwen2.5-Math-72B | 🚧 |
| Qwen/Qwen2.5-Math-72B-Instruct | 🚧 |
| Qwen/Qwen2.5-Math-RM-72B | 🚧 |

### Qwen2.5-Coder

| Model Name | Static Graph Download model_name |
|:-----------|:---------------------------------:|
| Qwen/Qwen2.5-Coder-1.5B | 🚧 |
| Qwen/Qwen2.5-Coder-1.5B-Instruct | 🚧 |
| Qwen/Qwen2.5-Coder-7B | 🚧 |
| Qwen/Qwen2.5-Coder-7B-Instruct | 🚧 |
