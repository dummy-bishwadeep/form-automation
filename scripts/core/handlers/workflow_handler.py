import copy
import logging

import requests
from fastapi import HTTPException, status

from scripts.constants import EnvironmentConstants
from scripts.constants.api_constants import UTCoreWorkflowAPI
from scripts.constants.app_constants import AppConstants, Secrets, AutomationConstants
from scripts.constants.workflow_constants import WorkflowConstants
from scripts.services.common_utils import CommonUtils
from scripts.logging.logger import logger
from scripts.utils.security_utils.jwt_util import JWT


class WorkflowHandler:
    def __init__(self, workbook, encrypt_payload, login_token):
        self.workbook = workbook
        self.encrypt_payload = encrypt_payload
        self.login_token = login_token
        self.common_utils_obj = CommonUtils(workbook=self.workbook)
        self.workflow_metadata = dict()

    def automate_workflow(self):
        try:
            # convert excel data into dataframe
            df, _, _ = self.common_utils_obj.convert_sheet_to_df(sheet_name=AppConstants.metadata_sheet)
            df = self.extract_workflow_metadata(df=df)
            self.convert_workflow_metadata_to_dict(df)

            # check workflow data exists
            _, workflow_data = self.check_workflow_exists()

            # Update basic information of workflow
            self.update_basic_info_workflow(workflow_data=workflow_data)

            return {'message': 'Updated workflow basic information successfully'}
        except Exception as automation_error:
            logger.error(automation_error)
            raise automation_error

    def extract_workflow_metadata(self, df):
        try:
            df = df.copy()
            # Get the name of the first column
            first_column = df.columns[0]

            # Find the index where the value is 'Workflow' in the first column (case insensitive)
            index_to_extract = df[first_column].str.lower().eq('workflow').idxmax()

            # Find the next row with a non-None value in the specified column
            next_non_none_row = self.common_utils_obj.find_next_non_none_row(df, (index_to_extract, 0))

            # Extract all the workflow metadata rows
            df = df.iloc[index_to_extract+1:next_non_none_row]

            # delete all empty rows & columns
            df.dropna(how='all', inplace=True)
            df.dropna(how='all', inplace=True, axis=1)

            return df
        except Exception as metadata_error:
            logger.error(metadata_error)
            raise metadata_error

    def convert_workflow_metadata_to_dict(self, df):
        try:
            table_no_rows, _ = df.shape
            arr = df.to_numpy()
            for row in range(0, table_no_rows):
                metadata_label = arr[row][0]
                metadata_value = arr[row][1]
                metadata_label = WorkflowConstants.workflow_mapping.get(metadata_label.lower(), '')
                if metadata_label:
                    self.workflow_metadata.update({metadata_label: metadata_value.strip()})
        except Exception as metadata_error:
            logger.error(metadata_error)
            raise metadata_error

    def check_workflow_exists(self):
        try:
            # prepare payload
            payload = copy.deepcopy(WorkflowConstants.fetch_workflow_data_payload)
            filter_data = copy.deepcopy(WorkflowConstants.fetch_workflow_filter_model)
            filter_data['workflow_name']['filter'] = self.workflow_metadata.get('workflow_name', '').strip()
            payload['filters']['filterModel'] = filter_data

            # trigger fetch workflow data api
            url = f'{EnvironmentConstants.base_path}{UTCoreWorkflowAPI.fetch_workflow}'

            # encode payload int jwt
            if self.encrypt_payload:
                payload = JWT().encode(payload=payload)
                response = requests.post(url, data=payload, headers=Secrets.headers, cookies=self.login_token)
            else:
                response = requests.post(url, json=payload, headers=Secrets.headers, cookies=self.login_token)

            if response.status_code != 200:
                response = {'message': 'Failed to fetch workflow data'}
            response = response.json()

            # extract workflow data
            workflow_data = response.get('data', {}).get('bodyContent', [])
            if workflow_data:
                return True, workflow_data[0]
            return False, {}
        except Exception as workflow_exists_error:
            logger.error(workflow_exists_error)
            raise workflow_exists_error

    def update_basic_info_workflow(self, workflow_data):
        try:
            workflow_id = workflow_data.get('workflow_id', '')
            name = workflow_data.get('workflow_name', self.workflow_metadata.get('workflow_name', ''))
            if not name:
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Workflow Name is missing')

            description = self.workflow_metadata.get('description', '')
            shift_enabled = workflow_data.get('shift_enabled', self.workflow_metadata.get('shift_enabled', False))
            workflow_version = workflow_data.get('workflow_version', 1)
            _tags = self.workflow_metadata.get('tags', '')
            tags = workflow_data.get('tags', []) or list(map(str.strip, _tags.split(','))) if _tags else []
            update_workflow_data = {
                "type": "basicInfo",
                "workflow_id": workflow_id,
                "data": {
                    "workflow_name": name,
                    "description": description,
                    "tags": tags,
                    "increment_version": False,
                    "shift_enabled": shift_enabled
                },
                "project_id": EnvironmentConstants.project_id,
                "project_type": AutomationConstants.project_type,
                "tz": EnvironmentConstants.tz,
                "language": AutomationConstants.language,
                "workflow_version": workflow_version,
            }

            # save basic information of workflow
            url = f'{EnvironmentConstants.base_path}{UTCoreWorkflowAPI.save_workflow}'

            # encode payload int jwt
            if self.encrypt_payload:
                payload = JWT().encode(payload=update_workflow_data)
                response = requests.post(url, data=payload, headers=Secrets.headers, cookies=self.login_token)
            else:
                response = requests.post(url, json=update_workflow_data, headers=Secrets.headers, cookies=self.login_token)
            if response.status_code != 200:
                return {'message': "Failed to update basic information of workflow"}
            response = response.json()
            response = response.get('data', {})
            update_workflow_data.update(response)
        except Exception as update_error:
            logger.error(update_error)
            raise update_error