# 使用 PaddleNLP 在燧原 S60下运行 llama2-13b 模型

燧原 S60（[了解燧原](https://www.enflame-tech.com/)）是面向数据中心大规模部署的新一代人工智能推理加速卡，满足大语言模型、搜广推及传统模型的需求，具有模型覆盖面广、易用性强、易迁移易部署等特点，可广泛应用于图像及文本生成等应用、搜索与推荐、文本、图像及语音识别等主流推理场景。

PaddleNLP 在燧原 S60上对 llama2-13B 模型进行了深度适配和优化，实现了 GCU 推理入口和 GPU 的基本统一，仅需修改 device 即可完成推理任务的迁移。

## 🚀 快速开始 🚀

### 0. 机器准备。快速开始之前，您需要准备一台插有燧原 S60加速卡的机器，要求如下：

| 芯片类型 | 驱动版本 | TopsPlatform 版本 |
| :---: | :---: | :---: |
| 燧原 S60 | 1.0.5.1 | TopsPlatform_1.0.5.1-2c3111 |

**注：如果需要验证您的机器是否插有燧原 S60加速卡，只需系统环境下输入以下命令，看是否有输出：**
```bash
lspci | grep S60

# 例如：lspci | grep S60 , 输出如下
01:00.0 Processing accelerators: Shanghai Enflame Technology Co. Ltd S60 [Enflame] (rev 01)
09:00.0 Processing accelerators: Shanghai Enflame Technology Co. Ltd S60 [Enflame] (rev 01)
```
### 1. 环境准备：(这将花费您10～20min 时间)

1. 初始化环境，安装驱动<br/>
  **注：您可以联系燧原(Email: developer-enflame@enflame-tech.com)以获取软件驱动包和其他帮助**
```bash
# 假设安装包位于：/home/paddle_user/deps/， 名称为：TopsPlatform.tar.gz
cd /home/paddle_user/deps/ && tar -zxf TopsPlatform.tar.gz
cd TopsPlatform
./TopsPlatform_1.0.5.1-2c3111_deb_amd64.run --no-auto-load --driver -y
```
2. 拉取镜像
```bash
# 注意此镜像仅为paddle开发环境，镜像中不包含预编译的飞桨安装包、TopsPlatform安装包等
docker pull registry.baidubce.com/paddlepaddle/paddle:latest-dev
```
3. 参考如下命令启动容器
```bash
docker run --name paddle-gcu-test -v /home:/home --network=host --ipc=host -it --privileged registry.baidubce.com/paddlepaddle/paddle:latest-dev /bin/bash
```
4. 安装编译套件
```bash
# 安装cmake用于源码编译
cd /root
wget https://github.com/Kitware/CMake/releases/download/v3.23.4/cmake-3.23.4-linux-x86_64.tar.gz
tar -zxf ./cmake-3.23.4-linux-x86_64.tar.gz
ln -sf /root/cmake-3.23.4-linux-x86_64/bin/cmake /usr/bin/cmake && ln -sf /root/cmake-3.23.4-linux-x86_64/bin/ctest /usr/bin/ctest
```
5. 安装燧原软件栈
```bash
# 在paddle docker里安装燧原软件栈，编译执行会依赖sdk、runtime、eccl、aten、topstx(for profiler)
cd /home/paddle_user/deps/TopsPlatform
./TopsPlatform_1.0.5.1-2c3111_deb_amd64.run --no-auto-load -y
dpkg -i topsfactor_*.deb tops-sdk_*.deb eccl_*.deb topsaten_*.deb
```
6. 安装 PaddlePaddle
```bash
# PaddlePaddle『飞桨』深度学习框架，提供运算基础能力
python -m pip install paddlepaddle==3.0.0b0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
```
7. 编译安装 PaddleCustomDevice<br/>
  PaddleCustomDevice 是 PaddlePaddle『飞桨』深度学习框架的自定义硬件接入实现，提供 GCU 的设备管理及算子实现。<br/>
  **注：当前仍需源码编译 PaddleCustomDevice，paddle-custom-gcu 预编译版本待发布**
```bash
# 下载源码
mkdir -p /home/paddle_user/workspace && cd /home/paddle_user/workspace
git clone https://github.com/PaddlePaddle/PaddleCustomDevice.git
cd PaddleCustomDevice
# 切换到v3.0.0-beta1版本
git checkout -b v3.0-beta v3.0.0-beta1
# 依赖的算子库
cp /home/paddle_user/deps/TopsPlatform/libtopsop.a ./backends/gcu/kernels/topsflame/
# 开始编译，依赖的第三方库会在首次编译时按需下载。从github下载可能会比较慢
cd backends/gcu/ && mkdir -p build && cd build
export PADDLE_CUSTOM_PATH=`python -c "import re, paddle; print(re.compile('/__init__.py.*').sub('',paddle.__file__))"`
cmake .. -DWITH_TESTING=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DPY_VERSION=3.9
make -j64
# 编译产物在build/dist，使用pip安装
python -m pip install --force-reinstall -U dist/paddle_custom_gcu*.whl
```
8. 下载 PaddleNLP 仓库代码，并安装依赖
```bash
# PaddleNLP是基于PaddlePaddle『飞桨』的自然语言处理和大语言模型(LLM)开发库，存放了基于『飞桨』框架实现的各种大模型，llama2-13B模型也包含其中。为了便于您更好地使用PaddleNLP，您需要clone整个仓库。
cd /home/paddle_user/workspace
git clone https://github.com/PaddlePaddle/PaddleNLP.git
cd PaddleNLP
# 切换到v3.0.0-beta0版本
git checkout -b v3.0-beta v3.0.0-beta0
# 安装依赖库
python -m pip install -r requirements.txt
# 源码编译安装 paddlenlp v3.0.0-beta0
python setup.py bdist_wheel && python -m pip uninstall paddlenlp -y && python -m pip install dist/paddlenlp*
```
### 2. 数据准备：(这将花费您2～5min 时间)
使用训练好的模型，在 wikitext-103上评估
```bash
cd llm/devices/gcu/llama
wget https://paddlenlp.bj.bcebos.com/data/benchmark/wikitext-103.tar.gz
tar -zxf wikitext-103.tar.gz
```
### 3. 推理：(这将花费您15~30min 时间)
执行如下命令进行推理：
```bash
bash predict_llama_gcu.sh
```
首次推理将自动下载权重和配置，位于 ```/root/.paddlenlp/models/__internal_testing__/sci-benchmark-llama-13b-5k/```目录下。<br/>
**推荐在首次下载权重文件后更改推理配置文件，以获取更大的性能提升。**<br/>
将 ```/root/.paddlenlp/models/__internal_testing__/sci-benchmark-llama-13b-5k/config.json```更改为下面的内容：
```json
{
  "alibi": false,
  "architectures": [
    "LlamaForCausalLM"
  ],
  "attention_probs_dropout_prob": 0.1,
  "bos_token_id": 1,
  "dtype": "float16",
  "eos_token_id": 2,
  "hidden_dropout_prob": 0.1,
  "hidden_size": 5120,
  "initializer_range": 0.002,
  "intermediate_size": 13824,
  "max_position_embeddings": 2048,
  "model_type": "llama",
  "num_attention_heads": 40,
  "num_hidden_layers": 40,
  "num_key_value_heads": 40,
  "pad_token_id": 0,
  "paddlenlp_version": null,
  "rms_norm_eps": 1e-06,
  "rope_scaling_factor": 1.0,
  "rope_scaling_type": null,
  "tie_word_embeddings": false,
  "use_recompute": false,
  "virtual_pp_degree": 1,
  "vocab_size": 32000,
  "use_fused_rope": true,
  "use_fused_rms_norm": true,
  "use_flash_attention": true,
  "fuse_attention_qkv": true,
  "fuse_attention_ffn": true
}
```
成功运行后，可以查看到推理结果的困惑度指标(ppl)，最终评估结果 ppl: 12.785。
```bash
[2024-08-16 01:55:24,753] [    INFO] - step 2000, batch: 2000, loss: 2.323283, speed: 1.40 step/s
[2024-08-16 01:55:31,813] [    INFO] - step 2010, batch: 2010, loss: 2.341318, speed: 1.42 step/s
[2024-08-16 01:55:38,859] [    INFO] - step 2020, batch: 2020, loss: 2.357684, speed: 1.42 step/s
[2024-08-16 01:55:45,897] [    INFO] - step 2030, batch: 2030, loss: 2.371745, speed: 1.42 step/s
[2024-08-16 01:55:52,942] [    INFO] - step 2040, batch: 2040, loss: 2.386801, speed: 1.42 step/s
[2024-08-16 01:55:59,991] [    INFO] - step 2050, batch: 2050, loss: 2.399686, speed: 1.42 step/s
[2024-08-16 01:56:07,037] [    INFO] - step 2060, batch: 2060, loss: 2.410638, speed: 1.42 step/s
[2024-08-16 01:56:14,080] [    INFO] - step 2070, batch: 2070, loss: 2.421459, speed: 1.42 step/s
[2024-08-16 01:56:21,141] [    INFO] - step 2080, batch: 2080, loss: 2.431433, speed: 1.42 step/s
[2024-08-16 01:56:28,170] [    INFO] - step 2090, batch: 2090, loss: 2.443705, speed: 1.42 step/s
[2024-08-16 01:56:35,238] [    INFO] - step 2100, batch: 2100, loss: 2.454847, speed: 1.41 step/s
[2024-08-16 01:56:42,275] [    INFO] - step 2110, batch: 2110, loss: 2.464446, speed: 1.42 step/s
[2024-08-16 01:56:49,323] [    INFO] - step 2120, batch: 2120, loss: 2.475107, speed: 1.42 step/s
[2024-08-16 01:56:56,348] [    INFO] - step 2130, batch: 2130, loss: 2.487760, speed: 1.42 step/s
[2024-08-16 01:57:03,372] [    INFO] - step 2140, batch: 2140, loss: 2.501706, speed: 1.42 step/s
[2024-08-16 01:57:10,395] [    INFO] - step 2150, batch: 2150, loss: 2.513665, speed: 1.42 step/s
[2024-08-16 01:57:17,411] [    INFO] - step 2160, batch: 2160, loss: 2.524555, speed: 1.43 step/s
[2024-08-16 01:57:24,437] [    INFO] - step 2170, batch: 2170, loss: 2.536793, speed: 1.42 step/s
[2024-08-16 01:57:31,461] [    INFO] - step 2180, batch: 2180, loss: 2.547897, speed: 1.42 step/s
[2024-08-16 01:57:34,378] [    INFO] -  validation results on ./wikitext-103/wiki.valid.tokens | avg loss: 2.5483E+00 | ppl: 1.2785E+01 | adjusted ppl: 2.6434E+01 | token ratio: 1.285056584007609 |
'Original Tokens: 279682, Detokenized tokens: 217642'
'Original Tokens: 279682, Detokenized tokens: 217642'
I0816 01:57:34.386860 10925 runtime.cc:130] Backend GCU finalize device:0
I0816 01:57:34.386868 10925 runtime.cc:98] Backend GCU Finalize
```
