import json
import openpyxl

from scripts.constants.app_constants import AppConstants
from scripts.constants.step_constants import StepConstants
from scripts.logging.logger import logger
from scripts.utils.common_utils import CommonUtils


class MetaData:

    def __init__(self, file_path, component_json_path):
        self.file_path = file_path
        self.component_json_path = component_json_path
        with open(self.component_json_path, 'rb') as file:
            self.component_json = json.load(file)
        self.workbook = openpyxl.load_workbook(self.file_path, data_only=True)
        self.common_utils_obj = CommonUtils(workbook=self.workbook)

    def automate_step(self):
        try:
            # convert excel data into dataframe
            df, _, _ = self.common_utils_obj.convert_sheet_to_df(sheet_name=AppConstants.metadata_sheet)

            # group merged rows based on specific column (here grouping based on based 1st column if rows merged)
            merged_row_groups = self.common_utils_obj.group_merged_rows(df=df, merge_column=0)

            grouped_step_df = self.extract_step_data(merged_row_groups, df=df)
            step_data_list = []
            for each_df in grouped_step_df:
                dict_data = self.convert_data_to_dict(each_df)
                step_data = self.get_final_data(dict_data)
                final_data = self.get_meta_data(step_data)
                step_data_list.append(final_data)
            return step_data_list
        except Exception as e:
            logger.exception(f"Error while getting meta data {e}")

    def extract_step_data(self, merged_row_groups, df):
        try:
            grouped_step_df = []
            for each in merged_row_groups:
                group_df = df.iloc[each].reset_index(drop=True)
                group_np = group_df.to_numpy()
                cell_value = group_np[0][0]
                _group_df = group_df.copy()
                if 'step' in cell_value.lower():
                    # Drop the first column and reset the index
                    _group_df = _group_df.drop(_group_df.columns[0], axis=1).reset_index(drop=True)
                    _group_df.dropna(how='all', inplace=True)
                    _group_df.dropna(how='all', inplace=True, axis=1)
                    grouped_step_df.append(_group_df)
            return grouped_step_df
        except Exception as extraction_error:
            logger.error(extraction_error)
            raise extraction_error


    def get_meta_data(self, step_data):
        try:
            step_name = step_data["step_name"]
            display_title = step_data["display_title"]
            description = step_data["description"]
            step_sub_categroy = step_data["step_sub_category"]
            validate_form = step_data["validate_form"]
            auto_save = step_data["auto_save"]
            sheet_name = step_data["sheet"]
            menu_placement = step_data["menu_placement"]
            step_category = step_data["step_category"]
            step_header = step_data['header']

            step_meta_data = {
                'step_name': step_name,
                'display_title': display_title,
                'description': description,
                'step_category': step_category,
                'step_sub_category': step_sub_categroy if step_sub_categroy else None,
                'menu_placement': menu_placement,
                'validate_form': validate_form,
                'auto_save': auto_save,
                'sheet': sheet_name,
                'header': step_header
            }
            return step_meta_data
        except Exception as e:
            logger.exception(f"Error while creating the meta data: {e}")

    def convert_data_to_dict(self, df):
        try:
            step_meta_data = dict()
            table_no_rows, _ = df.shape
            arr = df.to_numpy()
            for row in range(0, table_no_rows):
                metadata_label = arr[row][0].lower()
                metadata_value = arr[row][1]
                if metadata_label in list(StepConstants.step_metadata_mapping.keys()):
                    step_meta_data.update({StepConstants.step_metadata_mapping[metadata_label]: metadata_value})
            return step_meta_data
        except Exception as e:
            logger.exception(f"Error while converting the Meta data to dict: {e}")

    def get_final_data(self, step_meta_data):
        try:
            menu_placement = step_meta_data["menu_placement"].lower()
            step_category = step_meta_data["step_category"].lower()
            step_meta_data["menu_placement"] = StepConstants.menu_placement_mapping[menu_placement]
            step_meta_data["step_category"] = StepConstants.step_category_mapping[step_category]
            return step_meta_data
        except Exception as e:
            logger.exception(f"Error while creating the json {e}")

