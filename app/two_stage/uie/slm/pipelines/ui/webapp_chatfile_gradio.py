# Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import io
import os
from pathlib import Path
from typing import NamedTuple

import gradio as gr
from utils import ChatFile, upload_chatfile

parser = argparse.ArgumentParser()
parser.add_argument("--serving_name", default="0.0.0.0", help="Serving ip.")
parser.add_argument("--serving_port", default=8893, type=int, help="Serving port.")
args = parser.parse_args()
DEFAULT_NUMBER_OF_ANSWERS = int(os.getenv("DEFAULT_NUMBER_OF_ANSWERS", "3"))
DEFAULT_DOCS_FROM_RETRIEVER = int(os.getenv("DEFAULT_DOCS_FROM_RETRIEVER", "30"))
# Labels for the evaluation
EVAL_LABELS = os.getenv("EVAL_FILE", str(Path(__file__).parent / "markdown_aistudio_example.csv"))
# Whether the file upload should be enabled or not
DISABLE_FILE_UPLOAD = bool(os.getenv("DISABLE_FILE_UPLOAD"))
sentence_embedding_method = ["max_tokens", "mean_tokens", "mean_sqrt_len_tokens", "cls_token"]
loaded_path = []


def clear_session():
    return "", None, None, None, None, []


def predict(
    query,
    data_files,
    filters,
    top_k_reader,
    top_k_retriever,
    chunk_size,
    pooling_mode,
    separator,
    api_key,
    secret_key,
    history=None,
):
    if filters is not None:
        filters = [sy for sy in filters.split(";") if sy != ""]
    if data_files is not None and len(data_files) != 0:
        upload(data_files, chunk_size=chunk_size, separator=separator, filters=filters)
    if history is None:
        history = []
    result = ChatFile(
        query,
        top_k_reader=top_k_reader,
        top_k_retriever=top_k_retriever,
        pooling_mode=pooling_mode,
        api_key=api_key,
        secret_key=secret_key,
    )
    history.append(["user: {}".format(query), "assistant: {}".format(result["result"])])

    return " ", history, history


class UploadedFileRec(NamedTuple):
    """Metadata and raw bytes for an uploaded file. Immutable."""

    id: int
    name: str
    type: str
    data: bytes


class UploadedFile(io.BytesIO):
    """A mutable uploaded file.

    This class extends BytesIO, which has copy-on-write semantics when
    initialized with `bytes`.
    """

    def __init__(self, record: UploadedFileRec):
        # BytesIO's copy-on-write semantics doesn't seem to be mentioned in
        # the Python docs - possibly because it's a CPython-only optimization
        # and not guaranteed to be in other Python runtimes. But it's detailed
        # here: https://hg.python.org/cpython/rev/79a5fbe2c78f
        super(UploadedFile, self).__init__(record.data)
        self.id = record.id
        self.name = record.name
        self.type = record.type
        self.size = len(record.data)


def upload(data_files, chunk_size, separator, filters):
    for index, data_file in enumerate(data_files):
        if data_file.name not in loaded_path:
            with open(data_file.name, "rb") as f:
                byte_data = bytes(f.read())
            data_file = UploadedFileRec(id=index, data=byte_data, name=data_file.name, type=str)
            # Upload file
            upload_chatfile(UploadedFile(data_file), chunk_size=chunk_size, separator=separator, filters=filters)
            loaded_path.append(data_file.name)


if __name__ == "__main__":
    block = gr.Blocks()
    with block as demo:
        gr.Markdown("""<h1><center>PaddleNLP Pipelines ChatFiles</center></h1>""")
        with gr.Row():
            with gr.Column(scale=1):
                model_choose = gr.Accordion("模型选择")
                with model_choose:
                    sentence_embedding = gr.Dropdown(
                        sentence_embedding_method, label="sentence_embedding method", value="mean_tokens"
                    )
                top_k_reader = gr.Slider(1, 30, value=6, step=1, label="最大的答案的数量", interactive=True)
                top_k_retriever = gr.Slider(1, 100, value=DEFAULT_DOCS_FROM_RETRIEVER, step=1, interactive=True)
                CHUNK_SIZE = gr.Slider(300, 5000, value=1000, step=100, label="检索器索引的数据长度", interactive=True)
                separator = gr.Textbox(label="请输入分隔符,例如\\n", value="\n", max_lines=1)
                file = gr.File(
                    label="请上传知识库文件夹, 文件夹内文件目前支持txt、pdf、md、docx、png、jpg格式",
                    file_types=[".txt", ".pdf", ".md", ".docx", ".html", ".png", ".jpg"],
                    file_count="directory",
                )
                filters = gr.Textbox(label="请输入要忽略特殊字符，每个字符用;分隔,例如\\n;\\t", value="\n", max_lines=1)
            with gr.Column(scale=4):
                chatbot = gr.Chatbot(label="ChatFile")
                message = gr.Textbox(label="请输入问题")
                api_key = gr.Textbox(label="The API Key.")
                secret_key = gr.Textbox(label="The secret key.")
                state = gr.State()
                with gr.Row():
                    clear_history = gr.Button("🧹 清除历史对话")
                    send = gr.Button("🚀 发送")
                    send.click(
                        predict,
                        inputs=[
                            message,
                            file,
                            filters,
                            top_k_reader,
                            top_k_retriever,
                            CHUNK_SIZE,
                            sentence_embedding,
                            separator,
                            api_key,
                            secret_key,
                            state,
                        ],
                        outputs=[message, chatbot, state],
                    )
                    clear_history.click(
                        fn=clear_session, inputs=[], outputs=[chatbot, state, file, separator, filters], queue=False
                    )

        gr.Markdown(
            """提醒：<br>
        1. 使用时请先上传自己的知识文件，并且文件中不含某些特殊字符，否则将返回error. <br>
        文本文件举例"""
        )
    demo.queue().launch(server_name="0.0.0.0", server_port=args.serving_port)
