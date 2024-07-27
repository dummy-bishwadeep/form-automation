import copy
import json
import re

import requests
import urllib.parse
from fastapi import HTTPException, status
from scripts.constants import EnvironmentConstants
from scripts.constants.api_constants import UTCoreLogbooksAPI
from scripts.constants.app_constants import AppConstants, Secrets, AutomationConstants
from scripts.constants.logbook_constants import LogbookConstants
from scripts.logging.logger import logger
from scripts.utils.common_utils import CommonUtils
from scripts.utils.security_utils.jwt_util import JWT


class LogbookHandler:
    def __init__(self, workbook, encrypt_payload, login_token, workflow_data, response_message):
        self.workbook = workbook
        self.encrypt_payload = encrypt_payload
        self.login_token = login_token
        self.common_utils_obj = CommonUtils(workbook=self.workbook)
        self.logbook_metadata = dict()
        self.workflow_data = workflow_data
        self.response_message = copy.deepcopy(response_message)

    def automate_logbook(self):
        try:
            logger.info("Initiated Logbook Automation!!")

            # convert excel data into dataframe
            df, _, _ = self.common_utils_obj.convert_sheet_to_df(sheet_name=AppConstants.metadata_sheet)

            # group merged rows based on specific column (here grouping based on based 1st column if rows merged)
            merged_row_groups = self.common_utils_obj.group_merged_rows(df=df, merge_column=0)

            df = self.extract_logbook_data(merged_row_groups, df)
            self.convert_logbook_metadata_to_dict(df)

            # check logbook_data data exists
            _, logbook_data = self.check_logbook_exists()

            self.update_logbook(logbook_data=logbook_data)

            return self.response_message
        except Exception as automate_logbook:
            logger.error(automate_logbook)
            raise automate_logbook

    def extract_logbook_data(self, merged_row_groups, df):
        try:
            group_df = ''
            for each in merged_row_groups:
                group_df = df.iloc[each].reset_index(drop=True)
                group_np = group_df.to_numpy()
                cell_value = group_np[0][0]
                workflow_data = False
                if 'logbook' in cell_value.lower():
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

    def check_logbook_exists(self):
        try:
            # prepare payload
            payload = copy.deepcopy(LogbookConstants.fetch_logbooks_payload)
            filter_data = copy.deepcopy(LogbookConstants.logbook_filter_model)
            filter_data['logbook_name']['filter'] = self.logbook_metadata.get('logbook_name', '').strip()
            payload['filters']['filterModel'] = filter_data

            # trigger fetch workflow data api
            url = f'{EnvironmentConstants.base_path}{UTCoreLogbooksAPI.fetch_logbooks}'

            # encode payload int jwt
            if self.encrypt_payload:
                payload = JWT().encode(payload=payload)
                response = requests.post(url, data=payload, headers=Secrets.headers, cookies=self.login_token)
            else:
                response = requests.post(url, json=payload, headers=Secrets.headers, cookies=self.login_token)

            if response.status_code != 200:
                self.response_message += 'Failed to fetch logbook data\n'
                return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Failed to fetch logbook data')
            response = response.json()

            # extract logbook data
            logbook_data = response.get('data', {}).get('bodyContent', [])
            if logbook_data:
                return True, logbook_data[0]
            return False, {}
        except Exception as workflow_exists_error:
            logger.error(workflow_exists_error)
            raise workflow_exists_error

    def fetch_logbook_trigger_data(self):
        try:
            payload = copy.deepcopy(LogbookConstants.fetch_categories_payload)
            final_params = urllib.parse.urlencode({'params': json.dumps(payload)})

            # fetch logbook trigger details
            url = f'{EnvironmentConstants.base_path}{UTCoreLogbooksAPI.fetch_logbook_trigger}?{final_params}'
            response = requests.get(url, headers=Secrets.headers, cookies=self.login_token)

            if response.status_code != 200:
                self.response_message += 'Failed to fetch logbook trigger data\n'
                return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Failed to fetch logbook trigger data')
            response = response.json()
            return response.get('data', {})
        except Exception as trigger_error:
            logger.error(trigger_error)
            raise trigger_error

    def fetch_project_template_data(self):
        try:
            payload = LogbookConstants.fetch_project_templates_payload
            final_params = urllib.parse.urlencode({'params': json.dumps(payload)})

            # fetch project templates details
            url = f'{EnvironmentConstants.base_path}{UTCoreLogbooksAPI.fetch_templates}?{final_params}'
            response = requests.get(url, headers=Secrets.headers, cookies=self.login_token)

            if response.status_code != 200:
                self.response_message += 'Failed to fetch project templates data\n'
                return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Failed to fetch project templates data')
            response = response.json()
            return response.get('data', {})
        except Exception as trigger_error:
            logger.error(trigger_error)
            raise trigger_error

    def convert_logbook_metadata_to_dict(self, df):
        try:
            trigger_data = self.fetch_logbook_trigger_data()
            template_data = self.fetch_project_template_data()
            self.logbook_metadata['templates'] = template_data
            self.logbook_metadata['trigger_data'] = trigger_data
            self.format_roles_data(trigger_data=trigger_data)
            self.format_action_button_data(trigger_data=trigger_data)
            self.format_hierarchy_label_data()

            configured_roles = self.logbook_metadata.get('roles', {})
            skip_rows = None
            table_no_rows, _ = df.shape
            arr = df.to_numpy()
            for row in range(0, table_no_rows):
                if skip_rows and row < skip_rows:
                    continue
                metadata_label = arr[row][0]
                metadata_value = arr[row][1]
                metadata_label = LogbookConstants.logbook_mapping.get(metadata_label.lower() if metadata_label else '', '')
                if metadata_label == 'siteHierarchyLevel':
                    skip_rows = self.common_utils_obj.find_next_non_none_row(df, (row, 0))
                    hierarchy_df = (df.iloc[row:skip_rows]).reset_index(drop=True)
                    self.extract_hierarchy_data(hierarchy_df=hierarchy_df)
                elif metadata_label == 'reviewers':
                    roles = [configured_roles[each.strip().lower()] for each in metadata_value.split(',')]
                    self.logbook_metadata.update({metadata_label: roles})
                elif metadata_label == 'business_process_tags':
                    tags = [each.strip() for each in metadata_value.split(',')]
                    self.logbook_metadata.update({metadata_label: tags})
                elif metadata_label in ['step_id', 'workflow']:
                    self.logbook_metadata.update({metadata_label: metadata_value})
                elif metadata_label:
                    self.logbook_metadata.update({metadata_label: metadata_value if isinstance(metadata_value, bool) else metadata_value.strip()})
        except Exception as conversion_error:
            logger.error(conversion_error)
            raise conversion_error

    def extract_hierarchy_data(self, hierarchy_df):
        try:
            hierarchy_level = (hierarchy_df.to_numpy())[0][1]
            hierarchy_mapping = self.logbook_metadata.get('hierarchy_level', {})
            hierarchy_level = hierarchy_mapping[hierarchy_level.strip().lower()]
            self.logbook_metadata['siteHierarchyLevel'] = hierarchy_level

            # Drop the first and second columns
            hierarchy_df = hierarchy_df.copy()
            hierarchy_df = hierarchy_df.drop(hierarchy_df.columns[[0, 1]], axis=1).reset_index(drop=True)
            table_no_rows, _ = hierarchy_df.shape
            arr = hierarchy_df.to_numpy()

            # fetching site level data
            hierarchy_dropdown_data = self.fetch_hierarchy_dropdown_data()
            for row in range(0, table_no_rows):
                hierarchy_label = ''

                # fetching next hierarchy
                if row + 1 <= table_no_rows-1:
                    hierarchy_label = arr[row + 1][0].strip().lower()
                    hierarchy_label = hierarchy_mapping[hierarchy_label]

                hierarchy_value = arr[row][1].lower()

                for each in hierarchy_dropdown_data:
                    label = each['label'].lower()
                    value = each['value']
                    category = each['category']

                    if hierarchy_value == label:
                        self.logbook_metadata.update({category: value})

                        # fetching next hierarchy dropdown data
                        if hierarchy_label:
                            _hierarchy_dropdown_data = self.fetch_hierarchy_dropdown_data(node_id=value,
                                                                                          type=hierarchy_label)
                            hierarchy_dropdown_data = copy.deepcopy(_hierarchy_dropdown_data)
                        break
        except Exception as hierarchy_error:
            logger.error(hierarchy_error)
            raise hierarchy_error

    def format_roles_data(self, trigger_data):
        try:
            roles_data = {}
            roles = trigger_data.get('roles', [])
            for each in roles:
                label = each['label'].lower()
                value = each['value']
                roles_data[label] = value
            self.logbook_metadata['roles'] = roles_data
        except Exception as roles_error:
            logger.error(roles_error)
            raise roles_error

    def format_action_button_data(self, trigger_data):
        try:
            action_data = {}
            action_buttons = trigger_data.get('action_buttons', [])
            for each in action_buttons:
                label = each['button_label'].lower()
                value = each['action']
                action_data[label] = value
            self.logbook_metadata['action_buttons'] = action_data
        except Exception as roles_error:
            logger.error(roles_error)
            raise roles_error

    def format_hierarchy_label_data(self):
        try:
            hierarchy_mapping = {}
            project_template = self.logbook_metadata.get('templates', {})
            hierarchy_data = project_template.get('dropdown_data', [])
            for each in hierarchy_data:
                label = each['label'].lower()
                value = each['value']
                hierarchy_mapping[label] = value
            self.logbook_metadata['hierarchy_level'] = hierarchy_mapping
        except Exception as hierarchy_error:
            logger.error(hierarchy_error)
            raise hierarchy_error


    def fetch_hierarchy_dropdown_data(self, node_id=None, type=None):
        try:
            payload = copy.deepcopy(LogbookConstants.fetch_categories_payload)
            if node_id:
                payload.update({'node_id': node_id})
            if type:
                payload.update({"type": type})

            # trigger fetch workflow data api
            url = f'{EnvironmentConstants.base_path}{UTCoreLogbooksAPI.fetch_hierarchy_dropdown}'

            # encode payload int jwt
            if self.encrypt_payload:
                payload = JWT().encode(payload=payload)
                response = requests.post(url, data=payload, headers=Secrets.headers, cookies=self.login_token)
            else:
                response = requests.post(url, json=payload, headers=Secrets.headers, cookies=self.login_token)

            if response.status_code != 200:
                self.response_message += 'Failed to fetch hierarchy dropdown data\n'
                return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Failed to fetch hierarchy dropdown data')
            response = response.json()
            return response.get('data', [])
        except Exception as hierarchy_error:
            logger.error(hierarchy_error)
            raise hierarchy_error

    def update_logbook(self, logbook_data):
        try:
            payload = self.generate_logbook_data(logbook_data=logbook_data)

            logger.info('Initiated Logbook Update')

            # save basic information of workflow
            url = f'{EnvironmentConstants.base_path}{UTCoreLogbooksAPI.save_logbook}'

            # encode payload int jwt
            if self.encrypt_payload:
                payload = JWT().encode(payload=payload)
                response = requests.post(url, data=payload, headers=Secrets.headers, cookies=self.login_token)
            else:
                response = requests.post(url, json=payload, headers=Secrets.headers,
                                         cookies=self.login_token)
            if response.status_code != 200:
                self.response_message += 'Failed to update logbook\n'
                return {'message': 'Failed to update logbook\n'}
            response = response.json()
            self.response_message += 'Updated Logbook successfully\n'
            logger.info('Completed Logbook Update')
            return response
        except Exception as update_error:
            logger.error(update_error)
            raise update_error

    def generate_logbook_data(self, logbook_data):
        try:
            logbook_id = self.logbook_metadata.get('logbook_id', logbook_data.get('logbook_id', ''))
            specification_data = self.fetch_specification_data()

            logger.info('Initiated Logbook General Data')
            general_data = self.generate_logbook_general_data(specification_data=specification_data, logbook_data=logbook_data)
            logger.info('Completed Logbook General Data')

            logger.info('Initiated Logbook Association Data')
            association_data = self.generate_logbook_association_data(specification_data=specification_data)
            logger.info('Completed Logbook Association Data')

            selected_filters = self.generate_selected_filters_data()

            logbook_version = general_data.get('logbook_version', 1)
            logbook_name = self.logbook_metadata.get('logbook_name', logbook_data.get('logbook_name', ''))


            logger.info('Initiated Logbook Approval Data Data')
            approval_data = self.generate_approver_data(logbook_id=logbook_id,
                                                        logbook_version=logbook_version,
                                                        logbook_name=logbook_name)
            payload = {
                "general": general_data,
                "association": association_data,
                "external_links": {"bodyContent": []},
                "approval": approval_data,
                "logbook_id": logbook_id,
                "selectedFilters": selected_filters,
            }
            payload.update(LogbookConstants.fetch_categories_payload)
            payload.pop('node_id', None)
            payload.pop('type', None)
            logger.info('Completed Logbook Approval Data')
            return payload
        except Exception as general_error:
            logger.error(general_error)
            raise general_error


    def generate_logbook_general_data(self, specification_data, logbook_data):
        try:
            tags = self.logbook_metadata.get('business_process_tags', [])
            logbook_name = self.logbook_metadata.get('logbook_name', '')
            description = self.logbook_metadata.get('description', '')
            card_color = self.logbook_metadata.get('card_color', '')
            logbook_category = self.logbook_metadata.get('logbook_category', '')
            logbook_version = logbook_data.get('logbook_version', self.logbook_metadata.get('logbook_version', 1))

            # extract card color data
            for each in specification_data.get('cardColors', []):
                color_code = each['color']
                if color_code == card_color:
                    card_color = copy.deepcopy(each)
                    break

            # validate card color
            if not card_color:
                self.response_message += 'Card Color is required\n'
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Card Color is required')

            # extract logbook category
            categories = self.fetch_categories_data()
            categories = categories.get('data', [])
            for each in categories:
                label = each['label'].lower()
                if logbook_category == label:
                    logbook_category = each['value']
                    break

            # prepare general data
            general_data = {
                "logbook_name": logbook_name,
                "description": description,
                "business_process_tags": tags,
                "card_color": card_color,
                "logbook_category": logbook_category,
                "timeGapConf": {},
                "enableTimeConfiguration": False,
                "logbook_version": logbook_version
            }
            return general_data
        except Exception as general_error:
            logger.error(general_error)
            raise general_error

    def fetch_specification_data(self):
        try:
            payload = LogbookConstants.fetch_specifications_payload

            # trigger fetch logbook specification data api
            url = f'{EnvironmentConstants.base_path}{UTCoreLogbooksAPI.fetch_specifications}'

            # encode payload into jwt
            if self.encrypt_payload:
                payload = JWT().encode(payload=payload)
                response = requests.post(url, data=payload, headers=Secrets.headers, cookies=self.login_token)
            else:
                response = requests.post(url, json=payload, headers=Secrets.headers, cookies=self.login_token)

            if response.status_code != 200:
                self.response_message += 'Failed to fetch logbook specification data\n'
                return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                                     detail='Failed to fetch logbook specification data')
            response = response.json()
            return response.get('data', [])
        except Exception as workflow_error:
            logger.error(workflow_error)
            raise workflow_error

    def fetch_categories_data(self):
        try:
            payload = copy.deepcopy(LogbookConstants.fetch_categories_payload)

            # trigger fetch logbook categories api
            url = f'{EnvironmentConstants.base_path}{UTCoreLogbooksAPI.fetch_categories}'

            # encode payload into jwt
            if self.encrypt_payload:
                payload = JWT().encode(payload=payload)
                response = requests.post(url, data=payload, headers=Secrets.headers, cookies=self.login_token)
            else:
                response = requests.post(url, json=payload, headers=Secrets.headers, cookies=self.login_token)

            if response.status_code != 200:
                self.response_message += 'Failed to fetch logbook categories data\n'
                return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                                     detail='Failed to fetch logbook categories data')
            response = response.json()
            return response.get('data', [])
        except Exception as categories_error:
            logger.error(categories_error)
            raise categories_error

    def generate_logbook_association_data(self, specification_data):
        try:
            workflow = self.workflow_data.get('workflow_id', self.logbook_metadata.get('workflow', ''))
            step_id = self.workflow_data.get('step_id', self.logbook_metadata.get('step_id', ''))
            selected_step_version = self.workflow_data.get('step_version', self.logbook_metadata.get('step_version', ''))
            associate_hierarchy = self.logbook_metadata.get('associate_hierarchy', '')
            site_hierarchy_level = self.logbook_metadata.get('siteHierarchyLevel', '')

            # extract workflow id
            for each_workflow in specification_data.get('workflows', []):
                workflow_label = each_workflow.get('label', '')
                if not workflow_label:
                    continue
                workflow_label = workflow_label.lower()
                workflow_value = each_workflow['value']
                if workflow_label == workflow.lower():
                    workflow = workflow_value
                    break

            if not all([step_id, selected_step_version]):
                # extract step id
                selected_step_version = ''
                for each_step in specification_data.get('steps', []):
                    step_label = each_step['label'].lower()
                    step_value = each_step['value']
                    step_version = each_step['step_version']
                    _step_version = float(step_version)

                    if step_id.lower() == step_label or f'{step_id.lower()} ({_step_version})' == step_label:
                        step_id = step_value
                        selected_step_version = step_version
                        break

            # prepare association data
            association_data = {
                "workflow": workflow,
                "step_id": step_id,
                "associate_hierarchy": associate_hierarchy.lower(),
                "siteHierarchyLevel": site_hierarchy_level,
                "step_selected_version": selected_step_version
                }

            return association_data
        except Exception as association_error:
            logger.error(association_error)
            raise association_error

    def generate_selected_filters_data(self):
        try:
            selected_filters = {}
            project_template = self.logbook_metadata.get('templates', {})
            templates = project_template.get('project_template', [])
            for each in templates:
                data = self.logbook_metadata.get(each, '')
                if data:
                    selected_filters[each] = data

            hierarchy_level = []
            for each_dropdown in project_template.get('dropdown_data', []):
                key = each_dropdown['value']
                hierarchy_level.append(key)
            # check_all_level_exists = [each_filter in selected_filters.keys() for each_filter in hierarchy_level]
            # check_all_level_exists = all(check_all_level_exists)
            # if not check_all_level_exists:
            #     self.response_message += 'Failed to fetch hierarchy data\n'
            selected_filters['ast'] = None
            return selected_filters
        except Exception as filters_error:
            logger.error(filters_error)
            raise filters_error


    def generate_approver_data(self, logbook_id, logbook_version, logbook_name):
        try:
            esign = self.logbook_metadata.get('e_sign', False)
            reviewers = self.logbook_metadata.get('reviewers', [])
            trigger_data = self.extract_and_generate_approval_data(logbook_id, logbook_version, logbook_name)
            approver_data = {
                "e_sign": esign,
                "triggers": trigger_data,
                "reviewers": reviewers
            }
            return approver_data
        except Exception as approver_error:
            logger.error(approver_error)
            raise approver_error


    def extract_and_generate_approval_data(self, logbook_id, logbook_version, logbook_name):
        try:
            # convert excel data into dataframe
            df, _, _ = self.common_utils_obj.convert_sheet_to_df(sheet_name=AppConstants.approval)
            df = df.copy()
            df = df.drop(index=0).reset_index(drop=True)
            table_no_rows, _ = df.shape
            arr = df.to_numpy()

            roles_mapping = self.logbook_metadata.get('roles', {})
            action_buttons_mapping = self.logbook_metadata.get('action_buttons', {})
            trigger_data = []

            # existing_approval_details = []
            existing_trigger_id_sequence = []
            if all([logbook_id, logbook_version, logbook_name]):
                existing_approval_details = self.fetch_logbook_details(logbook_id, logbook_version, logbook_name)
                existing_trigger_data = existing_approval_details.get('triggers', [])
                for each_trigger in existing_trigger_data:
                    existing_trigger_id = each_trigger['trigger_id']
                    if existing_trigger_id:
                        existing_trigger_id_sequence.append(existing_trigger_id)

            for row in range(0, table_no_rows):
                roles = arr[row][0]
                operation = arr[row][1]
                action_details = arr[row][2]

                roles = [roles_mapping[each.strip().lower()] for each in roles.split(',')]
                operation = action_buttons_mapping[operation.lower()]

                trigger_metadata = {
                    "role": roles,
                    "on_click": operation
                }

                action_templates_data, trigger_type, triggered_fields, action_data = self.extract_action_details(action_details)

                trigger_id = ''
                if row < len(existing_trigger_id_sequence):
                    trigger_id = existing_trigger_id_sequence[row]

                trigger_details = {
                    "actions": [action_data],
                    "trigger_meta": trigger_metadata,
                    "trigger_type": trigger_type,
                    "action_templates": action_templates_data,
                    "triggerFields": triggered_fields,
                    'trigger_id': trigger_id,
                    'logbook_id': logbook_id,
                    'logbook_version': logbook_version
                    }
                trigger_data.append(trigger_details)
            return trigger_data
        except Exception as approval_error:
            logger.error(approval_error)
            raise approval_error

    def extract_action_details(self, action_details):
        try:
            # status_data = re.findall(r'\{([^}]*)\}', action_details)
            status_data = action_details.split('{')
            status_data = status_data[0].strip().lower() if status_data else ''

            action_field_status = re.findall(r'\{([^}]*)\}', action_details)
            action_field_status = action_field_status[0] if action_field_status else ''
            action_field_status = [each.strip().lower() for each in action_field_status.split(AutomationConstants.delimiter_symbol)]

            trigger_template_data = self.logbook_metadata.get('trigger_data', {})
            action_templates_data = trigger_template_data.get('action_templates', [])
            trigger_templates = trigger_template_data.get('trigger_templates', [])
            action_template = {}
            trigger_type = ''
            triggered_fields = []
            for each in action_templates_data:
                action_label = each['action_label']
                if status_data.lower() == action_label.lower():
                    action_template = each
                    trigger_type = each['trigger_type']
                    break

            for each_trigger in trigger_templates:
                _trigger_type = each_trigger['trigger_type']
                if trigger_type == _trigger_type:
                    triggered_fields = each_trigger['trigger_fields']
                    break

            action_key_list = {}
            action_data = {}
            if action_template:
                action_type = action_template['action_type']
                action_data = {
                    'show': True,
                    'action_type': action_type
                }
                action_fields = action_template['action_fields']
                for each_action_field in action_fields:
                    action_options = each_action_field['options']
                    action_value = each_action_field['value']
                    action_key_list.update({action_value: action_options})

                for index, each_action_key in enumerate(action_key_list.keys()):
                    each_action_value = action_key_list[each_action_key]
                    action_status_data = trigger_template_data[each_action_value]
                    for each_action_field_status in action_status_data:
                        action_status_label = each_action_field_status['label']
                        action_status_value = each_action_field_status['value']
                        if action_status_label.lower() == action_field_status[index]:
                            action_data.update({each_action_key: action_status_value})
                            break

            return action_templates_data, trigger_type, triggered_fields, action_data

        except Exception as action_error:
            logger.error(action_error)
            raise action_error

    def fetch_logbook_details(self, logbook_id, logbook_version, logbook_name):
        try:
            # prepare payload
            payload = copy.deepcopy(LogbookConstants.fetch_logbook_details_payload)
            payload.update({'logbook_id': logbook_id,
                            'logbook_name': logbook_name,
                            'logbook_version': logbook_version})

            # trigger fetch workflow data api
            url = f'{EnvironmentConstants.base_path}{UTCoreLogbooksAPI.fetch_logbook_details}'

            # encode payload int jwt
            if self.encrypt_payload:
                payload = JWT().encode(payload=payload)
                response = requests.post(url, data=payload, headers=Secrets.headers, cookies=self.login_token)
            else:
                response = requests.post(url, json=payload, headers=Secrets.headers, cookies=self.login_token)

            if response.status_code != 200:
                self.response_message += 'Failed to fetch logbook data\n'
                return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Failed to fetch logbook data')
            response = response.json()
            return response.get('data', {}).get('mainData', {}).get('approval', {})
        except Exception as logbook_error:
            logger.error(logbook_error)
            raise logbook_error