# 使用 PaddleNLP 在 NPU 下跑通 llama2-13b 模型
PaddleNLP 在昇腾 NPU（[了解昇腾](https://www.hiascend.com/zh/ecosystem/industry)）上对 llama2-13B 模型进行了深度适配和优化，该套件实现了昇腾 NPU 和 GPU 的训推入口基本统一，达到了『无缝切换』的效果。
在技术领先性上：
- **训练策略完全适配** 支持4D 混合并行，灵活适应多种训练策略。
- **训练性能极致优化** 95%的通信被掩盖在计算中，软硬结合提供极致性能。
- **低门槛性能调优** 分布式策略自动寻优能力打通多硬件，完全屏蔽硬件复杂性的同时，使用户可以轻松挖掘算力极限。
- **推理成本极致压缩** 推理支持 Layer 级算子融合，且融合算子已支持动态插入功能

<!-- 性能图片占位 -->
<!-- <div align="center">
    <img width="800" alt="llm" src="https://github.com/PaddlePaddle/PaddleNLP/assets/63761690/da10e972-260c-4925-bf49-1e0aefd2a65c">
</div> -->

下图是在 NPU 上运行 llama2-13b 训推的模块依赖关系图，这将使您更清晰后续的安装步骤。
<!-- 训练性能图片占位 -->

##  🚀 快速开始 🚀

### （0）在开始之前，您需要有一台昇腾 NPU 机器，对此机器的系统要求如下：

 | 芯片类型 | 驱动版本 | CANN 版本 |
 | --- | --- | --- |
 | 昇腾910 | 23.0.3 | CANN 8.0.RC1 |

**注：本示例使用8卡机器，并通过微调训练+推理的流程演示运行方法**
**注：如果要验证您的机器是否为昇腾910B 芯片，只需系统环境下输入命令，看是否有输出：**
```
lspci | grep d802

#例如：$ lspci | grep d802 , 输出如下
28:00.0 Processing accelerators: Huawei Technologies Co., Ltd. Device d802 (rev 20)
29:00.0 Processing accelerators: Huawei Technologies Co., Ltd. Device d802 (rev 20)
38:00.0 Processing accelerators: Huawei Technologies Co., Ltd. Device d802 (rev 20)
39:00.0 Processing accelerators: Huawei Technologies Co., Ltd. Device d802 (rev 20)
48:00.0 Processing accelerators: Huawei Technologies Co., Ltd. Device d802 (rev 20)
49:00.0 Processing accelerators: Huawei Technologies Co., Ltd. Device d802 (rev 20)
59:00.0 Processing accelerators: Huawei Technologies Co., Ltd. Device d802 (rev 20)
5a:00.0 Processing accelerators: Huawei Technologies Co., Ltd. Device d802 (rev 20)
98:00.0 Processing accelerators: Huawei Technologies Co., Ltd. Device d802 (rev 20)
99:00.0 Processing accelerators: Huawei Technologies Co., Ltd. Device d802 (rev 20)
b8:00.0 Processing accelerators: Huawei Technologies Co., Ltd. Device d802 (rev 20)
b9:00.0 Processing accelerators: Huawei Technologies Co., Ltd. Device d802 (rev 20)
c8:00.0 Processing accelerators: Huawei Technologies Co., Ltd. Device d802 (rev 20)
c9:00.0 Processing accelerators: Huawei Technologies Co., Ltd. Device d802 (rev 20)
d9:00.0 Processing accelerators: Huawei Technologies Co., Ltd. Device d802 (rev 20)
da:00.0 Processing accelerators: Huawei Technologies Co., Ltd. Device d802 (rev 20)
```

### （1）环境准备：(这将花费您5～15min 时间)
1. 拉取镜像
```
# 注意此镜像仅为开发环境，镜像中不包含预编译的飞桨安装包
docker pull registry.baidubce.com/device/paddle-npu:cann80RC1-ubuntu20-x86_64-gcc84-py39
```
2. 参考如下命令启动容器，可以通过设置 ASCEND_RT_VISIBLE_DEVICES 指定容器可见的昇腾卡号
```
docker run -it --name paddle-npu-dev -v $(pwd):/work \
    --privileged --network=host --shm-size=128G -w=/work \
    -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -e ASCEND_RT_VISIBLE_DEVICES="0,1,2,3,4,5,6,7" \
    registry.baidubce.com/device/paddle-npu:cann80RC1-ubuntu20-x86_64-gcc84-py39 /bin/bash
```
3. 安装 paddle
```
# paddlepaddle『飞桨』深度学习框架，提供运算基础能力
python -m pip install paddlepaddle==3.0.0b0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
```
4. 安装 paddleCustomDevice
```
# paddleCustomDevice是paddlepaddle『飞桨』深度学习框架的自定义硬件接入实现，提供NPU的算子实现。
python -m pip install paddle-custom-npu==3.0.0b0 -i https://www.paddlepaddle.org.cn/packages/stable/npu/
# 如想源码编译安装，请参考https://github.com/PaddlePaddle/PaddleCustomDevice/blob/develop/backends/npu/README_cn.md
```
5. 克隆 PaddleNLP 仓库代码，并安装依赖
```
# PaddleNLP是基于paddlepaddle『飞桨』的自然语言处理和大语言模型(LLM)开发库，存放了基于『飞桨』框架实现的各种大模型，llama2-13B模型也包含其中。为了便于您更好地使用PaddleNLP，您需要clone整个仓库。
git clone https://github.com/PaddlePaddle/PaddleNLP.git
cd PaddleNLP
python -m pip install -r requirements.txt
python -m pip install -e .
```
6. 安装 paddlenlp_ops
```
# PaddleNLP仓库内置了部分昇腾专用的融合算子，以便用户享受到极致压缩的推理成本
cd csrc/npu
python setup.py build bdist_wheel
pip install dist/paddlenlp_ops-0.0.0-cp39-cp39-linux_x86_64.whl
cd -
```

### （2）数据准备：(这将花费您2～5min 时间)
sft 为精调策略，我们提供了广告生成数据集 demo 便于您调试使用
```
#精调：为了方便测试，我们也提供了广告生成数据集可以直接使用：
cd llm/devices/npu/llama
wget https://bj.bcebos.com/paddlenlp/datasets/examples/AdvertiseGen.tar.gz
tar -zxvf AdvertiseGen.tar.gz
```
我们支持的精调数据格式是每行包含一个字典的 json 文件，每个字典包含以下字段：
- `src`: `str, List(str)`，指模型的输入指令（instruction）、提示（prompt），模型应该执行的任务。
- `tgt`: `str, List(str)`，指模型的输出。
样例数据：
```
{"src": "类型#裙*颜色#蓝色*风格#清新*图案#蝴蝶结", "tgt": "裙身处采用立体蝴蝶结装饰辅以蓝色条带点缀，令衣身造型饱满富有层次的同时为其注入一丝甜美气息。将女孩清新娇俏的一面衬托而出。"}
...
#您可以根据此格式自行制作精调数据。
```

### （3）训练：(这将花费您约4小时的时间)
我们在本目录中提供了对应 Pretrain/SFT/LoRA 的三个入口脚本，并已经按照8张910芯片的训练资源优化了并行策略等配置供您参考。启动微调训练的详细步骤如下：
```
# 运行sft策略
bash llama_npu_sft_N1C8.sh
```
### （4）推理：(这将花费您10~15min 时间)
推理前需要准备推理用的配置文件，在 merge 好参数的路径下(本教程下路径为：`./output/sft_bf16_llama_N1C8`)将`config.json`更改为下面的内容：
```
{
  "architectures": [
    "LlamaForCausalLM"
  ],
  "bos_token_id": 1,
  "eos_token_id": 2,
  "hidden_act": "silu",
  "hidden_size": 5120,
  "initializer_range": 0.02,
  "intermediate_size": 13824,
  "max_position_embeddings": 4096,
  "model_type": "llama",
  "num_attention_heads": 40,
  "num_hidden_layers": 40,
  "num_key_value_heads": 40,
  "pad_token_id": 0,
  "pretraining_tp": 1,
  "rms_norm_eps": 1e-05,
  "rope_scaling": null,
  "tie_word_embeddings": false,
  "torch_dtype": "float16",
  "transformers_version": "4.31.0",
  "use_cache": false,
  "vocab_size": 32000
}
```
为了保障极致压缩的推理成本，我们使用了静态图实现。因此需要从训练产出的动态图模型中导出静态图模型，执行如下命令进行导出：
```
bash export_npu.sh ./output/sft_bf16_llama_N1C8/ ./inference
```
最终，我们通过静态图的模型执行推理：
```
# 执行推理代码
bash predict_npu.sh ./inference
```
成功运行后，可以查看到推理结果的生成，样例如下：
```
***********Source**********
解释一下“温故而知新”
***********Target**********

***********Output**********
 "温故而知新" (wēn gù er zhī xīn) is a Chinese idiom that means "to know the old and appreciate the new." It is often used to describe the idea of learning from the past and being open to new experiences and ideas.

The word "温" (wēn) in this idiom means "old" or "past," and "故" (gù) means "origin" or "beginning." The word "知" (zhī) means "to know" or "to understand," and "新" (xīn) means "new."

So, the idiom "温故而知新" can be translated as "to know the old and appreciate the new," or "to learn from the past and embrace the new." It suggests that by understanding the past, we can gain a deeper appreciation for the present and be more open to new ideas and experiences.

This idiom is often used in Chinese culture to encourage people to learn from their heritage and traditions, while also being open to new ideas and perspectives. It is a reminder that knowledge and understanding are not limited to the present, but can also be gained from the past, and that by combining the old and the new, we can gain a more complete and nuanced understanding of the world.
```

##  💪🏼 特性介绍 💪🏼

- 通信掩盖技术
当模型训练开启张量并行后，计算过程中会出现很多通信（AllReduce/ReduceScatter/AllGather）+ 矩阵乘（Matmul）的算子组合。910芯片提供了一种高效的并行机制来掩盖通信开销。
<!-- 原理图片占位 -->
通过设置 FLAGS_NPU_MC2=1开启通信计算的融合 pass，将绝大部分的张量并行通信开销掩藏在计算中，有效提升训练性能。
<!-- 性能图片占位 -->
<!-- profiling 图片占位 -->

- 自定义算子的统一抽象
在实践中，我们发现 fusion 算子对于大模型训练的性能影响往往很大。为了全面支持昇腾以及其他各种硬件的高性能算子，同时保持组网代码的简洁性，我们提供了统一的[自定义算子接口实现](https://github.com/PaddlePaddle/PaddleNLP/blob/develop/paddlenlp/transformers/llama/fusion_ops.py)。目前覆盖了 llama 中常见的`fusion_rope`、`fusion_rms_norm`、`fusion_flash_attention`在 NPU、GPU、XPU、GCU 的实现。

- Layer 级算子融合
Layer 级算子融合显著提升计算效率，同时融合算子支持动态插入功能，在执行推理的过程中可以看到如下日志：
```
--- Running IR pass [remove_residual_in_fused_bias_residual_layernorm]
--- Running IR pass [remove_residual_in_rms_norm]
--- Running IR pass [remove_blha_get_max_len]
--- Running IR pass [llama_fuse_attention_layer_begin]
--- Running IR pass [llama_fuse_attention_layer_end]
--- Running IR pass [llama_fuse_attention_layer]
--- Running IR pass [llama_fuse_lm_head_with_slice]
--- Running IR pass [llama_fuse_lm_head]
--- Running IR pass [llama_fuse_get_padding_offset]
```
