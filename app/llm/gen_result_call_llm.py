import logging
import uuid
import time
import hashlib
import os
import re
import requests
import json
import base64
import sys
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Status codes
LLM_CODE_OK = 200  # Success
LLM_CODE_TIMEOUT = 101  # Timeout
LLM_CODE_SER_ERR = 102  # Service error
LLM_CODE_FORMAT_ERR = 103  # Format error
LLM_CODE_ALL_ERR = 400  # Other errors

# Retry configuration
MAX_RETRIES = 5


def encode_base64(raw_text: str) -> str:
    return str(base64.b64encode(json.dumps(raw_text, sort_keys=True).encode('utf-8')), encoding="utf8")


def decode_base64(raw_text: str) -> str:
    return str(base64.b64decode(raw_text), "utf-8")


def cal_md5(raw_text_list: str) -> str:
    return hashlib.md5(bytes(raw_text_list, encoding="utf8")).hexdigest()


def get_capability_name_24(raw_capabilityname: str) -> str:
    """Ensure capability name is 24 characters"""
    return raw_capabilityname.ljust(24, '0')


def extract_json(data: Dict[str, str]) -> Optional[Dict]:
    """
    Extract and parse JSON from LLM response.
    Handles markdown-wrapped JSON and common formatting issues.
    """
    content = data.get('content')
    if not content:
        logger.error(f"Missing 'content' in data: {data}")
        return None

    # Remove markdown tags if present
    if content.startswith('```json\n') and content.endswith('\n```'):
        content = re.sub(r'^```json\n|\n```$', '', content)

    try:
        # Parse JSON array or object
        return json.loads(content)[0] if content.startswith('[') else json.loads(content)
    except json.JSONDecodeError:
        try:
            # Handle malformed JSON
            obj_str = '{' + content[1:-1] + '}'
            return json.loads(obj_str)
        except json.JSONDecodeError:
            obj_str = obj_str.rstrip(',}') + '}'
            try:
                return json.loads(obj_str)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON format: {data}")
                raise


def gen_request_headers(appkey: str, appid: str, capabilityname: str) -> Dict[str, str]:
    """Generate authentication headers for LLM API request"""
    _uuid = "".join(str(uuid.uuid4()).split('-'))
    capabilityname = get_capability_name_24(capabilityname)
    X_Server_Param = {
        "appid": appid,
        "csid": f"{appid}{capabilityname}{_uuid}",
    }
    encoded_param = encode_base64(X_Server_Param)
    timestamp = str(int(time.time()))
    return {
        "Content-Type": "application/json; charset=utf-8",
        "X-Server-Param": encoded_param,
        "X-CurTime": timestamp,
        "X-CheckSum": cal_md5(appkey + timestamp + encoded_param),
    }


def gen_request_body(base64_image: str, user_text: str, sys_text: str) -> dict:
    """Construct request body with image and prompts"""
    return {
        "messages": [
            {"role": "system", "content": sys_text},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": base64_image}},
                    {"type": "text", "text": user_text},
                ]
            }
        ],
        "max_tokens": 2024,
        "temperature": 0
    }


def gen_result(base64_image: str, user_text: str, sys_text: str) -> Tuple[Optional[Dict], int]:
    """
    Send request to LLM with retry logic.
    Returns (response_data, status_code) tuple.
    """
    url = ""
    appkey = ""
    appid = ""
    capabilityname = ""

    headers = gen_request_headers(appkey, appid, capabilityname)
    body = gen_request_body(base64_image, user_text, sys_text)

    for retry in range(MAX_RETRIES):
        try:
            logger.info(f"Sending LLM request (attempt {retry + 1}/{MAX_RETRIES})")
            res = requests.post(url, json=body, headers=headers, timeout=80.0)
            res.raise_for_status()

            if res.status_code == 200:
                try:
                    return extract_json(res.json()), res.status_code
                except ValueError:
                    logger.warning(f"Invalid JSON response, retrying")
            else:
                logger.error(f"API error {res.status_code}: {res.text}")
                return None, LLM_CODE_SER_ERR

        except requests.exceptions.Timeout:
            logger.error(f"Request timed out")
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        time.sleep(1)  # Wait before retry

    logger.error(f"Failed after {MAX_RETRIES} retries")
    return None, LLM_CODE_ALL_ERR