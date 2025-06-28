import logging
from typing import Dict, List, Union
import sys, os
from app.data_process import data_predefined

logger = logging.getLogger(__name__)

# Define status codes for this module
DATA_CODE_OK = 200
DATA_CODE_ALL_ERR = 400


def transform_data(llm_response: Dict[str, Union[str, int, Dict]], id_name_list: Dict[str, List[str]]) -> (
        Union[Dict, None], int):
    """
    Transform LLM response data into the target data format.

    :param llm_response: LLM response data containing name, path, type, and result information.
    :param id_name_list: Dictionary containing id_list and name_list for constructing certiPhotoData list.
    :return: Transformed data and status code.
    """
    try:
        # Extract necessary information from the original data
        name_ = llm_response.get('name')
        # path_ = llm_response.get('path')
        type_ = llm_response.get('type')
        result_ = llm_response.get('result')
        code_ = llm_response.get('resp_code')

        # Construct the target data format
        transformed_data = {
            "code": code_,
            "name": name_,
            # "path": os.path.basename(path_),
            "type": str(type_),
            "certiPhotoData": []
        }

        id_list = id_name_list['id_list']
        name_list = id_name_list['name_list']

        if len(id_list) != len(name_list):
            logger.error(
                f"The number of elements in id_list and name_list does not match. "
                f"Please check the data_predefined.py file. id_list: {id_list}, name_list: {name_list}")
            return None, DATA_CODE_ALL_ERR

        # Iterate through id_list and name_list to construct certiPhotoData list
        for i, (id_index, name_index) in enumerate(zip(id_list, name_list), start=1):
            certi_item = {
                "number": i,
                "id": id_index,
                "name": name_index,
                "value": str(result_.get(name_index, ""))  # Convert all data to string
            }
            transformed_data["certiPhotoData"].append(certi_item)

        return transformed_data, DATA_CODE_OK
    except KeyError as key_err:
        logger.error(f"KeyError in transform_data: {key_err}, llm_response: {llm_response}, id_name_list: {id_name_list}")
        return None, DATA_CODE_ALL_ERR
    except Exception as e:
        logger.error(f"Error in transform_data: {e}, llm_response: {llm_response}, id_name_list: {id_name_list}")
        return None, DATA_CODE_ALL_ERR


# Call the transform_data function with different certificate types
def llm_data_postprocess(cert_type_en: str, llm_response: Dict[str, Union[str, int, Dict]]) -> (
        Union[Dict, None], int):
    """
    Postprocess LLM response data based on the certificate type.

    :param cert_type_en: Certificate type.
    :param llm_response: LLM response data.
    :return: Processed result and status code.
    """
    try:
        id_name_list = data_predefined.certificate_id_name_predefined.get(cert_type_en)
        if id_name_list is None:
            logger.error(f"id_name_list not found for {cert_type_en}. Please check the data_predefined.py file.")
            return None, DATA_CODE_ALL_ERR
        logger.info(f"Processing certificate type: {cert_type_en}, llm_response: {llm_response}")
        result, state_code = transform_data(llm_response, id_name_list)
        logger.info(f"Processed result: {result}")
        return result, state_code
    except Exception as e:
        logger.error(f"Error in llm_data_postprocess: {e}, cert_type_en: {cert_type_en}, llm_response: {llm_response}")
        return None, DATA_CODE_ALL_ERR