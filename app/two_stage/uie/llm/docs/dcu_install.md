## 🚣‍♂️ 使用PaddleNLP在DCU(K100_AI)下跑通llama2-7b模型 🚣
PaddleNLP在海光 DCU-K100AI 芯片上对llama系列模型进行了深度适配和优化，此文档用于说明在DCU-K100_AI上使用PaddleNLP进行llama系列模型进行高性能推理的流程。

### 检查硬件：

 | 芯片类型 | 驱动版本 |
 | --- | --- |
 | K100_AI | 6.2.17a |

**注：如果要验证您的机器是否为海光K100-AI芯片，只需系统环境下输入命令，看是否有输出：**
```
lspci | grep -i -E "disp|co-pro"

# 显示如下结果 - 
37:00.0 Co-processor: Chengdu Haiguang IC Design Co., Ltd. Device 6210 (rev 01)
3a:00.0 Co-processor: Chengdu Haiguang IC Design Co., Ltd. Device 6210 (rev 01)
```

### 环境准备：
注意：K100_AI 芯片需要安装DTK 24.04 及以上版本，请按照下面步骤进行
1. 拉取镜像
```
# 注意此镜像仅为开发环境，镜像中不包含预编译的飞桨安装包
docker pull registry.baidubce.com/device/paddle-dcu:dtk24.04.1-kylinv10-gcc73-py310
```
2. 参考如下命令启动容器
```
docker run -it --name paddle-dcu-dev -v `pwd`:/work \
  -w=/work --shm-size=128G --network=host --privileged  \
  --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
  registry.baidubce.com/device/paddle-dcu:dtk24.04.1-kylinv10-gcc73-py310 /bin/bash
```
3. 安装paddle
```
# paddlepaddle『飞桨』深度学习框架，提供运算基础能力
git clone https://github.com/PaddlePaddle/Paddle.git
cd Paddle && mkdir build && cd build 

cmake .. -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_CXX_FLAGS="-Wno-error -w" \
  -DPY_VERSION=3.10 -DPYTHON_EXECUTABLE=`which python3` -DWITH_CUSTOM_DEVICE=OFF \
  -DWITH_TESTING=OFF -DON_INFER=ON -DWITH_DISTRIBUTE=ON -DWITH_MKL=ON \
  -DWITH_ROCM=ON -DWITH_RCCL=ON

make -j128 
pip install -U python/dist/paddlepaddle_rocm-0.0.0-cp310-cp310-linux_x86_64.whl

# 检查是否安装正常
python -c "import paddle; paddle.version.show()"
python -c "import paddle; paddle.utils.run_check()"

```
4. 克隆PaddleNLP仓库代码，并安装依赖
```
# PaddleNLP是基于paddlepaddle『飞桨』的自然语言处理和大语言模型(LLM)开发库，存放了基于『飞桨』框架实现的各种大模型，llama系列模型也包含其中。为了便于您更好地使用PaddleNLP，您需要clone整个仓库。
pip install --pre --upgrade paddlenlp -f https://www.paddlepaddle.org.cn/whl/paddlenlp.html
```
5. 安装 paddlenlp_ops
```
# PaddleNLP仓库内置了专用的融合算子，以便用户享受到极致压缩的推理成本
git clone https://github.com/PaddlePaddle/PaddleNLP.git
cd PaddleNLP/csrc/
python setup_hip.py install
cd -
```

### 高性能推理：
海光的推理命令与GPU推理命令一致，请参考[大模型推理教程](https://github.com/PaddlePaddle/PaddleNLP/blob/develop/llm/docs/predict/inference.md).