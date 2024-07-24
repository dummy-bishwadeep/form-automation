import json
import openpyxl
import pandas as pd

from scripts.constants.app_constants import AppConstants
from scripts.constants.step_constants import StepConstants
from scripts.core.schemas.step_models import MenuPlacementDropdown, StepCategoryDropdown
from scripts.logging.logger import logger
from scripts.utils.common_utils import CommonUtils


class MetaData:

    def __init__(self, file_path):
        self.file_path = file_path
        with open("scripts/utils/component.json", 'r') as file:
            self.component_json = json.load(file)
        self.workbook = openpyxl.load_workbook(self.file_path, data_only=True)
        self.common_utils_obj = CommonUtils(workbook=self.workbook)

    def automate_step(self):
        try:
            # convert excel data into dataframe
            df, _, _ = self.common_utils_obj.convert_sheet_to_df(sheet_name=AppConstants.metadata_sheet)

            # group merged rows based on specific column (here grouping based on based 1st column if rows merged)
            merged_row_groups = self.common_utils_obj.group_merged_rows(df=df, merge_column=0)

            df = self.extract_step_data(merged_row_groups, df=df)
            dict_data = self.convert_data_to_dict(df)
            step_data = self.get_final_data(dict_data)
            final_data = self.get_meta_data(step_data)
            return final_data
        except Exception as e:
            logger.exception(f"Error while getting meta data {e}")

    def extract_step_data(self, merged_row_groups, df):
        try:
            group_df = ''
            for each in merged_row_groups:
                group_df = df.iloc[each].reset_index(drop=True)
                group_np = group_df.to_numpy()
                cell_value = group_np[0][0]
                step_data = False
                if 'step' in cell_value.lower():
                    step_data = True
                    # Drop the first column and reset the index
                    group_df = group_df.copy()
                    group_df = group_df.drop(group_df.columns[0], axis=1).reset_index(drop=True)
                if step_data:
                    group_df.dropna(how='all', inplace=True)
                    group_df.dropna(how='all', inplace=True, axis=1)
                    break
            return group_df
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
            menu_placement = step_meta_data["menu_placement"]
            step_category = step_meta_data["step_category"]
            step_meta_data["menu_placement"] = StepConstants.menu_placement_mapping[menu_placement]
            step_meta_data["step_category"] = StepConstants.step_category_mapping[step_category]
            return step_meta_data
        except Exception as e:
            logger.exception(f"Error while creating the json {e}")

