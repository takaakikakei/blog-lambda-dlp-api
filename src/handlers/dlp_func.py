import json
import os
from typing import Dict

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from google.cloud import dlp_v2
from google.cloud.dlp_v2 import DlpServiceClient
from google.oauth2 import service_account

logger = Logger()
tracer = Tracer()


def create_dlp_client() -> DlpServiceClient:
    cred = json.loads(os.environ["GCP_CREDENTIALS_JSON"])
    credentials = service_account.Credentials.from_service_account_info(cred)
    dlp_client = dlp_v2.DlpServiceClient(credentials=credentials)
    return dlp_client


def mask_text(dlp_client: DlpServiceClient, project_id: str, text: str) -> str:
    # APIリクエストの設定
    # see: https://cloud.google.com/dlp/docs/concepts-text-redaction?hl=ja
    # see: https://cloud.google.com/dlp/docs/high-sensitivity-infotypes-reference?hl=ja
    selected_info_types = [
        "PERSON_NAME",
        "EMAIL_ADDRESS",
        "AWS_CREDENTIALS",
    ]
    info_types = [{"name": info_type} for info_type in selected_info_types]
    inspect_config = {
        "info_types": info_types,
        "min_likelihood": "POSSIBLE",
    }

    # マスキングの設定
    # see: https://cloud.google.com/dlp/docs/transformations-reference?hl=ja#masking
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [
                {
                    "primitive_transformation": {
                        "character_mask_config": {
                            "characters_to_ignore": [
                                {"common_characters_to_ignore": None}
                            ],
                            "number_to_mask": 0,
                            "masking_character": "*",
                        }
                    }
                }
            ]
        }
    }

    # 入力内容
    item = {"value": text}

    # DLP APIリクエストを実行
    request = {
        "parent": f"projects/{project_id}",
        "inspect_config": inspect_config,
        "deidentify_config": deidentify_config,
        "item": item,
    }
    response = dlp_client.deidentify_content(request=request)

    # マスキングされたテキストを返す
    return response.item.value


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def handler(event: Dict, context: LambdaContext) -> Dict:
    """
    dlp_func のエントリーポイント

    event:
    {
        "input": {
            "question": "hoge 個人情報 fuga"
        },
        "execution": {
            ..snip..
        }
    }

    return:
    {
        "masked_question": "hoge **** fuga"
    }
    """
    try:
        text = event["input"]["text"]
        project_id = os.environ["GCP_PROJECT_ID"]
        dlp_client = create_dlp_client()
        masked_text = mask_text(dlp_client, project_id, text)
        return {"masked_text": masked_text}
    except Exception as e:
        logger.exception("throw exception in dlp_func")
        raise e
