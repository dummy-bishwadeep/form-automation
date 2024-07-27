import copy
import json
import re

import requests
from fastapi import HTTPException, status
import urllib.parse
from scripts.constants import EnvironmentConstants
from scripts.constants.api_constants import UTCoreWorkflowAPI
from scripts.constants.app_constants import AppConstants, Secrets, AutomationConstants
from scripts.constants.workflow_constants import WorkflowConstants
from scripts.utils.common_utils import CommonUtils
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
        self.response_message = copy.deepcopy(response_message)

    def automate_workflow(self):
        try:
            logger.info("Initiated Workflow Automation!!")

            # convert excel data into dataframe
            # df, _, _ = self.common_utils_obj.convert_sheet_to_df(sheet_name=AppConstants.metadata_sheet)

            # convert excel data into dataframe
            df, _, _ = self.common_utils_obj.convert_sheet_to_df(sheet_name=AppConstants.metadata_sheet)

            # group merged rows based on specific column (here grouping based on based 1st column if rows merged)
            merged_row_groups = self.common_utils_obj.group_merged_rows(df=df, merge_column=0)

            df = self.extract_workflow_data(merged_row_groups, df)
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
            workflow_data = self.update_workflow_actions(workflow_data=workflow_data)
            workflow_data.update({'workflow_id': self.workflow_metadata.get('workflow_name', '').strip()})

            logger.info("Completed update for Workflow Actions!!")
            return workflow_data, self.response_message
        except Exception as automation_error:
            logger.error(automation_error)
            raise automation_error

    def extract_workflow_data(self, merged_row_groups, df):
        try:
            group_df = ''
            for each in merged_row_groups:
                group_df = df.iloc[each].reset_index(drop=True)
                group_np = group_df.to_numpy()
                cell_value = group_np[0][0]
                workflow_data = False
                if 'workflow' in cell_value.lower():
                    workflow_data = True
                    # Drop the first column and reset the index
                    group_df = group_df.copy()
                    group_df = group_df.drop(group_df.columns[0], axis=1).reset_index(drop=True)
                if workflow_data:
                    group_df.dropna(how='all', inplace=True)
                    group_df.dropna(how='all', inplace=True, axis=1)
                    break
            return group_df
        except Exception as extraction_error:
            logger.error(extraction_error)
            raise extraction_error

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
            self.format_task_button_data()
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
                step_category = each.get('step_category' ,'')

                if step_category not in ['step_category_101', 'task creation step', 'Task Creation Step']:
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
                return True, decoded_payload
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
                _cell_value = [each.strip() for each in cell_value.split(',')]
                if all([each in list(roles_data.keys()) for each in _cell_value]):
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

    def update_workflow_actions(self, workflow_data):
        try:
            workflow_id = workflow_data.get('workflow_id', '')
            name = workflow_data.get('workflow_name', self.workflow_metadata.get('workflow_name', ''))
            workflow_version = workflow_data.get('workflow_version', 1)
            disable_usage_tracking = workflow_data.get('disable_usage_tracking', True)

            triggers = self.generate_worflow_actions(workflow_data=workflow_data)
            if not triggers:
                self.response_message += 'Trigger details are missing\n'
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Trigger details are missing')

            payload = {
                "workflow_version": workflow_version,
                "workflow_id": workflow_id,
                "triggers": triggers,
                "type": "actions",
                "disable_usage_tracking": disable_usage_tracking,
                "data": {
                    "workflow_name": name
                  }
            }
            payload.update(WorkflowConstants.workflow_dropdown_payload)

            _status, response = self.update_workflow(payload=payload,
                                                     error_message='Failed to update Workflow Actions')
            if _status:
                self.response_message += 'Updated workflow actions successfully\n'
            return response
        except Exception as actions_error:
            logger.error(actions_error)
            raise actions_error

    def generate_worflow_actions(self, workflow_data):
        try:
            # convert excel data into dataframe
            df, _, _ = self.common_utils_obj.convert_sheet_to_df(sheet_name=AppConstants.actions)

            user_init_trigger_temp_data = self.extract_user_init_action_trigger()
            trigger_type = user_init_trigger_temp_data.get('trigger_type', '')
            trigger_fields = user_init_trigger_temp_data.get('trigger_fields', [])
            action_templates = user_init_trigger_temp_data.get('action_templates', [])
            task_button_mapping = self.workflow_metadata.get('task_button_view', {})
            roles_data = self.workflow_metadata.get('roles', {})
            mapped_action_template = self.map_action_templates(action_templates)

            # remove header row
            _df = df.copy()
            _df = _df.drop(0).reset_index(drop=True)

            # group merged rows based on specific column (here grouping based on based 1st column if rows merged)
            merged_row_groups = self.common_utils_obj.group_merged_rows(df=_df, merge_column=0)

            # check if actions already exists and extract trigger id
            actions_exist, existing_action_data = self.check_actions_exist(workflow_data=workflow_data)
            if actions_exist:
                existing_action_data = self.map_actions_list(action_data=existing_action_data)

            # iterate through each of the merge row group
            triggers_list = []
            for each in merged_row_groups:
                group_df = _df.iloc[each].reset_index(drop=True)
                table_no_rows, _ = group_df.shape
                group_np = group_df.to_numpy()
                final_task_button_data = ''
                actions_list = []
                roles_list = []
                for row in range(0, table_no_rows):
                    task_button_data = group_np[row][0]
                    if task_button_data:
                        task_button_data = task_button_data.strip().lower()
                        final_task_button_data = task_button_mapping[task_button_data]

                    roles = group_np[row][1]
                    if roles:
                        roles = [each.strip().lower() for each in roles.split(',')]
                        roles_list = [roles_data[each_role] for each_role in roles]

                    action_type = group_np[row][2]
                    action_details = group_np[row][3]
                    if action_type:
                        action_type = action_type.strip().lower()
                        configured_action_template_data = mapped_action_template[action_type]

                        action_data = {}
                        action_type = configured_action_template_data.get('action_type', '')
                        if action_type == 'state_change' and action_details:
                            action_data = self.format_action_type_state_change(
                                action_template=configured_action_template_data,
                                action_details=action_details)
                        elif action_type == 'send_email' and action_details:
                            pass
                        elif action_type == 'mark_completed' and action_details:
                            action_data = {
                                'action_type': action_type
                            }
                        elif action_type == 'rest_api' and action_details:
                            action_data = self.format_action_type_rest_api(
                                action_template=configured_action_template_data,
                                action_details=action_details)
                        elif action_type == 'notification' and action_details:
                            action_data = self.format_action_type_notification(
                                action_template=configured_action_template_data,
                                action_details=action_details,
                                roles_data=roles_data)
                        elif action_type == 'event' and action_details:
                            pass
                        elif action_type == 'create_batch' and action_details:
                            pass
                        elif action_type == 'finish_batch' and action_details:
                            pass
                        elif action_type == 'rest_trigger' and action_details:
                            pass
                        elif action_type == 'send_request_email' and action_details:
                            pass
                        elif action_type == 'validate' and action_details:
                            pass

                        if action_data:
                            actions_list.append(action_data)

                _existing_action_data = existing_action_data.get(final_task_button_data, {})
                trigger_id = _existing_action_data.get('trigger_id', '')
                trigger_meta = {
                    'role': roles_list,
                    'on_click': final_task_button_data
                }

                trigger_data = {
                    'actions': actions_list,
                    'trigger_meta': trigger_meta,
                    'trigger_type': trigger_type,
                    'action_templates': action_templates,
                    'triggerFields': trigger_fields
                }
                if trigger_id:
                    trigger_data.update({'trigger_id': trigger_id})
                triggers_list.append(trigger_data)

            return triggers_list
        except Exception as actions_errors:
            logger.error(actions_errors)
            raise actions_errors

    def extract_user_init_action_trigger(self):
        try:
            dropdown_data = self.workflow_metadata.get('dropdown_data', {})
            trigger_templates = dropdown_data.get('trigger_templates', [])
            user_init_trigger_temp_data = {}
            for each in trigger_templates:
                if each['trigger_type'] == 'user_init':
                    user_init_trigger_temp_data = each
                    break
            return user_init_trigger_temp_data
        except Exception as trigger_error:
            logger.error(trigger_error)
            raise trigger_error

    @staticmethod
    def map_action_templates(action_template):
        try:
            templates = {}
            for each in action_template:
                label = each['action_label'].lower()
                templates[label] = each
            return templates
        except Exception as template_error:
            logger.error(template_error)
            raise template_error

    def format_action_type_state_change(self, action_template, action_details):
        try:
            action_details = [each.strip() for each in action_details.split(AutomationConstants.delimiter_symbol)]
            action_fields = action_template.get('action_fields', [])
            action_type = action_template.get('action_type', '')
            final_action_data = {
                'action_type': action_type
            }
            for index, each in enumerate(action_fields):
                value = each['value']
                final_action_data[value] = action_details[index]
            check_empty_value = any(each_ele in ['', None] for each_ele in list(final_action_data.values()))
            if check_empty_value:
                self.response_message += 'Action details are missing\n'
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Action details are missing')
            return final_action_data
        except Exception as format_error:
            logger.error(format_error)
            raise format_error

    def format_action_type_rest_api(self, action_template, action_details):
        try:
            action_fields = action_template.get('action_fields', [])
            action_type = action_template.get('action_type', '')

            request_method = re.findall(r'\{([^}]*)\}', action_details)
            request_method = request_method[0].upper() if request_method else ''

            request_url = re.findall(r'<([^>]*)>', action_details)
            request_url = request_url[0] if request_url else ''

            action_details = [request_method, request_url]
            final_action_data = {
                'action_type': action_type
            }

            for index, each in enumerate(action_fields):
                value = each['value']
                final_action_data[value] = action_details[index]
            check_empty_value = any(each_ele in ['', None] for each_ele in list(final_action_data.values()))
            if check_empty_value:
                self.response_message += 'Action details are missing\n'
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Action details are missing')
            return final_action_data
        except Exception as format_error:
            logger.error(format_error)
            raise format_error

    def format_action_type_notification(self, action_template, action_details, roles_data):
        try:
            action_fields = action_template.get('action_fields', [])
            action_type = action_template.get('action_type', '')

            roles_list = re.findall(r'\[([^\]]*)\]', action_details)
            roles_list = [roles_data[each.strip().lower()] for each in roles_list[0].split(',')] if roles_list else ''

            message = re.findall(r'\{([^}]*)\}', action_details)
            message = message[0].strip().lower() if message else ''

            action_details = [roles_list, message]
            final_action_data = {
                'action_type': action_type
            }

            for index, each in enumerate(action_fields):
                value = each['value']
                final_action_data[value] = action_details[index]
            check_empty_value = any(each_ele in ['', None] for each_ele in list(final_action_data.values()))
            if check_empty_value:
                self.response_message += 'Action details are missing\n'
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Action details are missing')
            return final_action_data
        except Exception as format_error:
            logger.error(format_error)
            raise format_error

    def check_actions_exist(self, workflow_data):
        try:
            workflow_id = workflow_data.get('workflow_id', '')
            name = workflow_data.get('workflow_name', self.workflow_metadata.get('workflow_name', ''))
            workflow_version = workflow_data.get('workflow_version', 1)

            payload = {
                "type": "actions",
                "workflow_id": workflow_id,
                "workflow_name": name,
                "workflow_version": workflow_version
            }
            payload.update(WorkflowConstants.workflow_dropdown_payload)

            final_params = urllib.parse.urlencode({'params': json.dumps(payload)})

            # fetch workflow actions
            url = f'{EnvironmentConstants.base_path}{UTCoreWorkflowAPI.fetch_params}?{final_params}'

            response = requests.get(url, headers=Secrets.headers, cookies=self.login_token)
            if response.status_code != 200:
                self.response_message += f'Failed to fetch workflow actions\n'
                return False, {'message': self.response_message}
            response = response.json()
            return True, response.get('data', {}).get('actions', [])
        except Exception as trigger_error:
            logger.error(trigger_error)
            raise trigger_error

    @staticmethod
    def map_actions_list(action_data):
        try:
            action_details = {}
            for each in action_data:
                on_click = each['trigger_meta']['on_click']
                action_details[on_click] = each
            return action_details
        except Exception as map_error:
            logger.error(map_error)
            raise map_error
