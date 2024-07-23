import copy
import json

import requests
from fastapi import HTTPException, status
import urllib.parse
from scripts.constants import EnvironmentConstants
from scripts.constants.api_constants import UTCoreWorkflowAPI
from scripts.constants.app_constants import AppConstants, Secrets, AutomationConstants
from scripts.constants.workflow_constants import WorkflowConstants
from scripts.services.common_utils import CommonUtils
from scripts.logging.logger import logger
from scripts.utils.security_utils.jwt_util import JWT


class WorkflowHandler:
    def __init__(self, workbook, encrypt_payload, login_token, step_data, response_message):
        self.workbook = workbook
        self.encrypt_payload = encrypt_payload
        self.login_token = login_token
        self.common_utils_obj = CommonUtils(workbook=self.workbook)
        self.workflow_metadata = dict()
        self.step_data = step_data
        self.response_message = response_message

    def automate_workflow(self):
        try:
            logger.info("Initiated Workflow Automation!!")

            # convert excel data into dataframe
            df, _, _ = self.common_utils_obj.convert_sheet_to_df(sheet_name=AppConstants.metadata_sheet)
            df = self.extract_workflow_metadata(df=df)
            self.convert_workflow_metadata_to_dict(df)

            # check workflow data exists
            _, workflow_data = self.check_workflow_exists()

            # Update basic information of workflow
            logger.info("Initiated update for Workflow Basic Information!!")
            workflow_data = self.update_basic_info_workflow(workflow_data=workflow_data)

            logger.info("Completed update for Workflow Basic Information!!")

            # Update Steps
            logger.info("Initiated update for Workflow Steps!!")
            workflow_data = self.update_workflow_steps(workflow_id=workflow_data.get('workflow_id', ''),
                                                       workflow_version=workflow_data.get('workflow_version', 1),
                                                       workflow_name=workflow_data.get('data', {}).get('workflow_name', ''))

            logger.info("Completed update for Workflow Steps!!")

            # Update roles
            logger.info("Initiated update for Workflow Roles!!")
            workflow_data = self.update_workflow_roles(workflow_data=workflow_data)

            logger.info("Completed update for Workflow Roles!!")

            # Update permissions
            logger.info("Initiated update for Workflow Permissions!!")
            workflow_data = self.update_workflow_permissions(workflow_data=workflow_data)

            logger.info("Completed update for Workflow Permissions!!")

            # Updated Actions
            logger.info("Initiated update for Workflow Actions!!")
            # workflow_data = self.update_workflow_actions(workflow_data=workflow_data)

            logger.info("Completed update for Workflow Actions!!")
            return self.response_message
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
            dropdown_data = self.fetch_workflow_dropdown_data()
            self.workflow_metadata['dropdown_data'] = dropdown_data

            self.format_roles_data()
            self.format_sequence_data()
            self.format_permission_data()
        except Exception as metadata_error:
            logger.error(metadata_error)
            raise metadata_error

    def format_roles_data(self):
        try:
            dropdown_data = self.workflow_metadata.get('dropdown_data', {})
            roles = self.workflow_metadata.get('roles', '')
            roles_data = dropdown_data.get('roles', [])

            if not roles:
                self.response_message += 'Roles are required\n'
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Roles are required')

            if 'all' in roles.lower():
                roles = {}
                for each in roles_data:
                    roles[each['label'].lower()] = each['value']
                self.workflow_metadata['roles'] = roles
            else:
                roles_list = [each.strip().lower() for each in roles.split(',')]
                roles = {}
                for each in roles_data:
                    role_label = each['label'].lower()
                    role_id = each['value']
                    if role_label in roles_list:
                        roles[role_label] = role_id
                self.workflow_metadata['roles'] = roles
        except Exception as roles_error:
            logger.error(roles_error)
            raise roles_error

    def format_sequence_data(self):
        try:
            dropdown_data = self.workflow_metadata.get('dropdown_data', {})
            status_list = dropdown_data.get('status', [])
            sequence_data = {}
            for each in status_list:
                label = each['label'].lower()
                value = each['value']
                sequence_data[label] = value
            self.workflow_metadata['sequence'] = sequence_data
        except Exception as sequence_error:
            logger.error(sequence_error)
            raise sequence_error

    def format_permission_data(self):
        try:
            dropdown_data = self.workflow_metadata.get('dropdown_data', {})
            status_list = dropdown_data.get('permissions', [])
            permissions_data = {}
            for each in status_list:
                label = each['label'].lower()
                value = each['value']
                permissions_data[label] = value
            self.workflow_metadata['permissions'] = permissions_data
        except Exception as permission_error:
            logger.error(permission_error)
            raise permission_error

    def format_task_button_data(self):
        try:
            dropdown_data = self.workflow_metadata.get('dropdown_data', {})
            status_list = dropdown_data.get('task_button_view', [])
            task_button_data = {}
            for each in status_list:
                label = each['label'].lower()
                value = each['value']
                task_button_data[label] = value
            self.workflow_metadata['task_button_view'] = task_button_data
        except Exception as permission_error:
            logger.error(permission_error)
            raise permission_error

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
            payload = {
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

            _status, response = self.update_workflow(payload=payload,
                                            error_message='Failed to update basic information of workflow')
            if _status:
                self.response_message += 'Updated workflow basic info successfully\n'
            return response
        except Exception as update_error:
            logger.error(update_error)
            raise update_error


    def extract_step_details(self):
        try:
            step_id_list = []
            step_id_version_mapping = {}
            validation_mapping = {}
            disable_prev_edit_mapping = {}
            shift_details_mapping = {}
            for each in self.step_data:
                step_id = each.get('step_id')
                step_version = each.get('step_version', 1)

                step_id_list.append(step_id)
                step_id_version_mapping[step_id] = step_version
                validation_mapping[step_id] = False
                disable_prev_edit_mapping[step_id] = False
                shift_details_mapping[step_id] = None
            final_res = {
                'step_id_list': step_id_list,
                'version_mapping': step_id_version_mapping,
                'validation_mapping': validation_mapping,
                'disable_prev_mapping': disable_prev_edit_mapping,
                'shift_mapping': shift_details_mapping
            }
            self.workflow_metadata['steps'] = step_id_list
            return final_res
        except Exception as step_details_error:
            logger.error(step_details_error)
            raise step_details_error


    def update_workflow_steps(self, workflow_id, workflow_version, workflow_name):
        try:
            step_mapping_details = self.extract_step_details()
            steps_list = step_mapping_details.get('step_id_list', [])

            if not steps_list:
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Workflow Steps are required')

            payload = {
                "type": "steps",
                "workflow_id": workflow_id,
                "data": {
                    "steps": steps_list,
                    "validation": step_mapping_details.get('validation_mapping', {}),
                    "step_selected_version": step_mapping_details.get('version_mapping', {}),
                    "disable_prev_edit": step_mapping_details.get('disable_prev_mapping', {}),
                    "shift_details": step_mapping_details.get('shift_mapping', {}),
                    "workflow_name": workflow_name
                },
                "project_id": EnvironmentConstants.project_id,
                "project_type": AutomationConstants.project_type,
                "tz": EnvironmentConstants.tz,
                "language": AutomationConstants.language,
                "workflow_version": workflow_version,
                "disable_usage_tracking": True
            }

            _status, response = self.update_workflow(payload=payload,
                                            error_message='Failed to update Workflow Steps')
            if _status:
                self.response_message += 'Updated Workflow Steps successfully\n'
            return response
        except Exception as configure_error:
            logger.error(configure_error)
            raise configure_error

    def update_workflow(self, payload, error_message):
        try:
            decoded_payload = {}
            # save basic information of workflow
            url = f'{EnvironmentConstants.base_path}{UTCoreWorkflowAPI.save_workflow}'

            # encode payload int jwt
            if self.encrypt_payload:
                decoded_payload = copy.deepcopy(payload)
                payload = JWT().encode(payload=payload)
                response = requests.post(url, data=payload, headers=Secrets.headers, cookies=self.login_token)
            else:
                response = requests.post(url, json=payload, headers=Secrets.headers,
                                         cookies=self.login_token)
            if response.status_code != 200:
                self.response_message += f'{error_message}\n'
                return False, {'message': error_message}
            response = response.json()
            response = response.get('data', {})
            if self.encrypt_payload:
                decoded_payload.update(response)
                return False, decoded_payload
            payload.update(response)
            return True, payload
        except Exception as update_error:
            logger.error(update_error)
            raise update_error


    def update_workflow_roles(self, workflow_data):
        try:
            workflow_id = workflow_data.get('workflow_id', '')
            name = workflow_data.get('workflow_name', self.workflow_metadata.get('workflow_name', ''))
            workflow_version = workflow_data.get('workflow_version', 1)
            disable_usage_tracking = workflow_data.get('disable_usage_tracking', True)
            payload = {
                "type": "roles",
                "workflow_id": workflow_id,
                "data": {
                    "roles": list(self.workflow_metadata.get('roles', {}).values()),
                    "workflow_name": name
                },
                "workflow_version": workflow_version,
                "disable_usage_tracking": disable_usage_tracking,
            }
            payload.update(WorkflowConstants.workflow_dropdown_payload)

            _status, response = self.update_workflow(payload=payload,
                                            error_message='Failed to update Workflow Roles')
            if _status:
                self.response_message += 'Updated workflow roles successfully\n'
            return response
        except Exception as roles_error:
            logger.error(roles_error)
            raise roles_error


    def fetch_workflow_dropdown_data(self):
        try:
            payload = WorkflowConstants.workflow_dropdown_payload
            final_params = urllib.parse.urlencode({'params': json.dumps(payload)})

            # save basic information of workflow
            url = f'{EnvironmentConstants.base_path}{UTCoreWorkflowAPI.fetch_workflow_dropdowns}?{final_params}'

            response = requests.get(url, headers=Secrets.headers, cookies=self.login_token)
            if response.status_code != 200:
                self.response_message += f'Failed to fetch workflow dropdown data\n'
                return {'message': self.response_message}
            response = response.json()
            return response.get('data', {})
        except Exception as dropdown_error:
            logger.error(dropdown_error)
            raise dropdown_error


    def update_workflow_permissions(self, workflow_data):
        try:
            workflow_id = workflow_data.get('workflow_id', '')
            name = workflow_data.get('workflow_name', self.workflow_metadata.get('workflow_name', ''))
            workflow_version = workflow_data.get('workflow_version', 1)
            disable_usage_tracking = workflow_data.get('disable_usage_tracking', True)
            permissions_data = self.generate_workflow_permissions_data()
            if not permissions_data:
                self.response_message += 'Permissions are required\n'
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Permissions are required')

            payload = {
                "type": "permissions",
                "workflow_id": workflow_id,
                "data": {
                    "permissions": permissions_data,
                    "workflow_name": name
                },
                "workflow_version": workflow_version,
                "disable_usage_tracking": disable_usage_tracking,
                }
            payload.update(WorkflowConstants.workflow_dropdown_payload)

            _status, response = self.update_workflow(payload=payload,
                                                     error_message='Failed to update Workflow Permissions')
            if _status:
                self.response_message += 'Updated workflow permissions successfully\n'
            return response

        except Exception as permission_error:
            logger.error(permission_error)
            raise permission_error

    def generate_workflow_permissions_data(self):
        try:
            # convert excel data into dataframe
            df, _, _ = self.common_utils_obj.convert_sheet_to_df(sheet_name=AppConstants.permissions)
            table_no_rows, table_no_cols = df.shape
            arr = df.to_numpy()

            sequence_data = self.workflow_metadata.get('sequence', {})
            roles_data = self.workflow_metadata.get('roles', {})
            permissions_data = self.workflow_metadata.get('permissions', {})

            # extract sequences and its index
            sequence_index_mapping = {}
            for col in range(1, table_no_cols):
                cell_value = arr[0][col].lower()
                if cell_value in list(sequence_data.keys()):
                    sequence_index_mapping[col] = sequence_data.get(cell_value, '')

            # extract roles
            roles_index_mapping = {}
            for row in range(1, table_no_rows):
                cell_value = arr[row][0].lower()
                if cell_value in list(roles_data.keys()):
                    roles_index_mapping[row] = roles_data.get(cell_value, '')

            # iterate through roles and sequences
            final_permission_data = []

            for col in range(1, table_no_cols):
                sequence_id = sequence_index_mapping[col]
                role_with_permission = {}
                for row in range(1, table_no_rows):
                    role_id = roles_index_mapping[row]
                    configured_permission = arr[row][col]
                    configured_permission = [each.strip().lower() for each in configured_permission.split(',')]
                    final_permissions = []

                    # extracted permissions
                    for each in configured_permission:
                        if each in list(permissions_data.keys()):
                            final_permissions.append(permissions_data[each])
                    if final_permissions and role_id:
                        role_with_permission[role_id] = final_permissions

                steps_with_permission = {}
                for each_step in self.workflow_metadata.get('steps', []):
                    steps_with_permission[each_step] = role_with_permission

                permission_obj = {
                    'steps': steps_with_permission,
                    'sequence_no': col,
                    'workflow_status': sequence_id
                }
                final_permission_data.append(permission_obj)

            return final_permission_data
        except Exception as permission_error:
            logger.error(permission_error)
            raise permission_error
