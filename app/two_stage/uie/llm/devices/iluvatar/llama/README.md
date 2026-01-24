# 使用 PaddleNLP 在天垓150下跑通 llama-13b 模型预训练

天垓150加速卡（[了解天数智芯](https://www.iluvatar.com/)）是基于天数智芯自研通用 GPU 的训推一体加速卡，具备广通用性、强灵活性、高性价比的显著优势，支持市场主流生态，可广泛应用于主流大模型的预训练、微调以及推理任务，以及通用计算、新算法研究等场景，赋能 AI 智能社会。

PaddleNLP 在天垓150上对 llama-13B 模型进行了深度适配和优化，基本实现了天垓150和 GPU 训推接口的统一，使用户可以在天垓150和 GPU 平台间轻松实现应用迁移。

## 🚀 快速开始 🚀

### （0）在开始之前，您需要有四台插有天垓150加速卡的机器，对此机器的系统要求如下：

| 芯片类型 | 驱动版本 | SDK 版本      |
| -------- | --------- | --------------- |
| 天垓 150 | ≥ 4.1.0  | ≥ 4.1.0 |

**注：如果需要验证您的机器是否插有天垓150，只需系统环境下输入以下命令，看是否有输出：**

```bash
ixsmi

#输出如下

Timestamp    Fri Dec 20 11:14:29 2024
+-----------------------------------------------------------------------------+
|  IX-ML: 4.1.0       Driver Version: 4.1.0       CUDA Version: 10.2          |
|-------------------------------+----------------------+----------------------|
| GPU  Name                     | Bus-Id               | Clock-SM  Clock-Mem  |
| Fan  Temp  Perf  Pwr:Usage/Cap|      Memory-Usage    | GPU-Util  Compute M. |
|===============================+======================+======================|
| 0    Iluvatar BI-V150         | 00000000:13:00.0     | 1500MHz   1600MHz    |
| 0%   32C   P0    N/A / N/A    | 116MiB / 32768MiB    | 0%        Default    |
+-------------------------------+----------------------+----------------------+
| 1    Iluvatar BI-V150         | 00000000:16:00.0     | 1500MHz   1600MHz    |
| 0%   30C   P0    93W / 350W   | 116MiB / 32768MiB    | 0%        Default    |
+-------------------------------+----------------------+----------------------+
| 2    Iluvatar BI-V150         | 00000000:1C:00.0     | 1500MHz   1600MHz    |
| 0%   31C   P0    N/A / N/A    | 116MiB / 32768MiB    | 0%        Default    |
+-------------------------------+----------------------+----------------------+
| 3    Iluvatar BI-V150         | 00000000:1F:00.0     | 1500MHz   1600MHz    |
| 0%   31C   P0    94W / 350W   | 116MiB / 32768MiB    | 0%        Default    |
+-------------------------------+----------------------+----------------------+
| 4    Iluvatar BI-V150         | 00000000:27:00.0     | 1500MHz   1600MHz    |
| 0%   30C   P0    N/A / N/A    | 116MiB / 32768MiB    | 0%        Default    |
+-------------------------------+----------------------+----------------------+
| 5    Iluvatar BI-V150         | 00000000:2A:00.0     | 1500MHz   1600MHz    |
| 0%   31C   P0    98W / 350W   | 116MiB / 32768MiB    | 0%        Default    |
+-------------------------------+----------------------+----------------------+
| 6    Iluvatar BI-V150         | 00000000:34:00.0     | 1500MHz   1600MHz    |
| 0%   31C   P0    N/A / N/A    | 116MiB / 32768MiB    | 0%        Default    |
+-------------------------------+----------------------+----------------------+
| 7    Iluvatar BI-V150         | 00000000:37:00.0     | 1500MHz   1600MHz    |
| 0%   31C   P0    95W / 350W   | 116MiB / 32768MiB    | 0%        Default    |
+-------------------------------+----------------------+----------------------+
| 8    Iluvatar BI-V150         | 00000000:3D:00.0     | 1500MHz   1600MHz    |
| 0%   32C   P0    N/A / N/A    | 116MiB / 32768MiB    | 0%        Default    |
+-------------------------------+----------------------+----------------------+
| 9    Iluvatar BI-V150         | 00000000:40:00.0     | 1500MHz   1600MHz    |
| 0%   32C   P0    95W / 350W   | 116MiB / 32768MiB    | 0%        Default    |
+-------------------------------+----------------------+----------------------+
| 10   Iluvatar BI-V150         | 00000000:48:00.0     | 1500MHz   1600MHz    |
| 0%   31C   P0    N/A / N/A    | 116MiB / 32768MiB    | 0%        Default    |
+-------------------------------+----------------------+----------------------+
| 11   Iluvatar BI-V150         | 00000000:4B:00.0     | 1500MHz   1600MHz    |
| 0%   31C   P0    94W / 350W   | 116MiB / 32768MiB    | 0%        Default    |
+-------------------------------+----------------------+----------------------+
| 12   Iluvatar BI-V150         | 00000000:54:00.0     | 1500MHz   1600MHz    |
| 0%   30C   P0    N/A / N/A    | 116MiB / 32768MiB    | 0%        Default    |
+-------------------------------+----------------------+----------------------+
| 13   Iluvatar BI-V150         | 00000000:57:00.0     | 1500MHz   1600MHz    |
| 0%   32C   P0    93W / 350W   | 116MiB / 32768MiB    | 0%        Default    |
+-------------------------------+----------------------+----------------------+
| 14   Iluvatar BI-V150         | 00000000:64:00.0     | 1500MHz   1600MHz    |
| 0%   30C   P0    N/A / N/A    | 116MiB / 32768MiB    | 0%        Default    |
+-------------------------------+----------------------+----------------------+
| 15   Iluvatar BI-V150         | 00000000:67:00.0     | 1500MHz   1600MHz    |
| 0%   30C   P0    94W / 350W   | 116MiB / 32768MiB    | 0%        Default    |
+-------------------------------+----------------------+----------------------+

+-----------------------------------------------------------------------------+
| Processes:                                                       GPU Memory |
|  GPU        PID      Process name                                Usage(MiB) |
|=============================================================================|
|  No running processes found                                                 |
+-----------------------------------------------------------------------------+
```

### （1）环境准备：(这将花费您5~55min 时间)
1. 拉取镜像
```bash
# 请联系天数智芯客户支持(services@iluvatar.com)获取SDK镜像

docker pull 10.150.9.98:80/sw_test/sw_home:4.1.0.20240528.110-x86_64-py3.10-bi150
```

2. 参考如下命令启动容器

```bash
docker run -e USER=`id -u -n` -e USER_ID=`id -u` --name paddle-corex-dev -it --privileged --cap-add=ALL --pid=host --network=host -v /data1:/data1 --mount type=volume,dst=/home/`id -u -n`/.local bdkw:paddle-corex /bin/bash
```

3. 安装 PaddlePaddle

①如果您已经通过 Iluvatar CoreX 获取了 PaddlePaddle 安装包(services@iluvatar.com)，您可以直接进行安装：

```bash
pip3 install paddlepaddle-2.5.2+corex*.whl
```
②您也可以通过源码自行编译 PaddlePaddle 安装包，请确保您已经正确安装 Iluvatar CoreX 软件栈。

```bash
# 1. 访问 Paddle4CoreX github仓库clone代码并切换至BDKW/2.5.2_corex分支.
git clone --recurse-submodules -b BDKW/2.5.2_corex https://github.com/PaddlePaddle/Paddle4CoreX.git
# 2. 执行编译脚本
bash build_paddle.sh
# 3. 等待编译完成后执行安装脚本
bash install_paddle.sh
```

4. 克隆 PaddleNLP 仓库代码，并安装依赖

```bash
# PaddleNLP是基于paddlepaddle『飞桨』的自然语言处理和大语言模型(LLM)开发库，存放了基于『飞桨』框架实现的各种大模型，llama-13B模型也包含其中。为了便于您更好地使用PaddleNLP，您需要clone整个仓库。
git clone -b sci/benchmark_iluvatar https://github.com/tianyuzhou668/PaddleNLP.git
# 编译自定义算子，可选
cd PaddleNLP
cd ./model_zoo/gpt-3/external_ops/ && python3 setup.py install && cd -
# 安装PaddleNLP
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

### （2）数据准备：(这将花费您2～5min 时间)
为了方便用户运行测试本模型，提供了处理好的100k 条 doc 的训练样本：
```bash
# llama 模型数据下载
cd ./llm
wget https://bj.bcebos.com/paddlenlp/models/transformers/llama/data/llama_openwebtext_100k.bin
wget https://bj.bcebos.com/paddlenlp/models/transformers/llama/data/llama_openwebtext_100k.idx
```
您也可以下载完整的数据集：
```bash
cd ./llm
wget https://paddlenlp.bj.bcebos.com/datasets/PDC_DATASETS/PRETRAIN/openwebtext2/llama/mmap/llama_mmap.bin
wget https://paddlenlp.bj.bcebos.com/datasets/PDC_DATASETS/PRETRAIN/openwebtext2/llama/mmap/llama_mmap.idx
```
将所有预处理得到的文件统一放入一个文件夹中，以备训练使用：
```bash
mkdir data
mv llama_openwebtext_100k_ids.npy ./data
mv llama_openwebtext_100k_idx.npz ./data
```

### （3）预训练：
我们在本目录中提供了对应四节点的预训练脚本，并已经按照32张 BI150芯片的训练资源优化了并行策略等配置供您参考。启动预训练的详细步骤如下：
```bash
# 您需要在脚本中将节点的ip地址更换为您实际节点的ip地址
bash run_node4.sh
```
我们默认会训练5000步，待5000步训练完毕后，模型会做 Evaluation 并得到最终的 checkpoint 文件，您可以基于该 checkpoint 进行微调任务或直接进行推理任务。
