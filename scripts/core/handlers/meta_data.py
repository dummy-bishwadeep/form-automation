import json
import openpyxl
import pandas as pd

from scripts.constants.step_constants import StepConstants
from scripts.core.schemas.step_models import MenuPlacementDropdown, StepCategoryDropdown
from scripts.logging.logger import logger


class MetaData:

    def __init__(self, file_path, sheet_name, current_ts):
        self.file_path = file_path
        self.sheet_name = sheet_name
        with open("scripts/utils/component.json", 'r') as file:
            self.component_json = json.load(file)
        self.workbook = openpyxl.load_workbook(self.file_path, data_only=True)
        self.unique_key_counter = {}
        self.current_ts = current_ts
        self.date_keys = []
        self.field_props = {}
        self.property_names = []

    def get_meta_data(self, step_data):
        try:
            step_name = step_data["step_name"]
            display_title = step_data["display_title"]
            description = step_data["description"]
            step_sub_categroy = step_data["step_sub_categroy"]
            validate_form = step_data["validate_form"]
            auto_save = step_data["auto_save"]
            sheet_name = step_data["sheet_name"]

            menu_placement = step_data["menu_placement"]
            menu_placement = MenuPlacementDropdown(menu_placement)

            step_category = step_data["step_category"]
            step_category = StepCategoryDropdown(step_category)

            step_meta_data = {
                'step_name': step_name,
                'display_title': display_title,
                'description': description,
                'step_category': step_category.name,
                'step_sub_category': step_sub_categroy if step_sub_categroy else None,
                'menu_placement': menu_placement.name,
                'validate_form': validate_form,
                'auto_save': auto_save,
                'sheet_name': sheet_name,
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
                metadata_label = arr[row][0]
                metadata_value = arr[row][1]
                if metadata_label in StepConstants.MetaData:
                    step_meta_data.update({metadata_label: metadata_value})
            return step_meta_data
        except Exception as e:
            logger.exception(f"Error while converting the Meta data to dict: {e}")

    def get_final_data(self, step_meta_data):
        try:
            menu_placement = step_meta_data["menu_placement"]
            step_category = step_meta_data["step_category"]
            step_meta_data["menu_placement"] = StepConstants.MenuPlacementDropdown[menu_placement]
            step_meta_data["step_category"] = StepConstants.StepCategoryDropdown[step_category]
            return step_meta_data
        except Exception as e:
            logger.exception(f"Error while creating the json {e}")

    def automate_step(self):
        try:
            df, _, _ = self.convert_sheet_to_df("MetaData")
            df = self.get_general_data(df=df)
            dict_data = self.convert_data_to_dict(df)
            step_data = self.get_final_data(dict_data)
            final_data = self.get_meta_data(step_data)
            return final_data
        except Exception as e:
            logger.exception(f"Error while getting meta data {e}")

    def get_general_data(self, df):
        try:
            df = df.copy()
            # Get the name of the first column
            first_column = df.columns[0]
            # Find the index where the value is 'Workflow' in the first column (case insensitive)
            index_to_extract = df[first_column].str.lower().eq('Step1').idxmax()
            # Find the next row with a non-None value in the specified column
            next_non_none_row = self.find_next_non_none_row(df, (index_to_extract, 0))
            # Extract all the workflow metadata rows
            df = df.iloc[index_to_extract + 1:next_non_none_row]
            # delete all empty rows & columns
            df.dropna(how='all', inplace=True)
            df.dropna(how='all', inplace=True, axis=1)
            return df
        except Exception as e:
            logger.exception(f"Error while getting general data {e}")

    def find_next_non_none_row(self, df, current_index):
        try:
            start_row, column = current_index
            mask = df.iloc[start_row + 1:, column].notna()
            next_non_none_row = mask.idxmax() if mask.any() else None
            return next_non_none_row
        except Exception as df_conversion_error:
            logger.error(df_conversion_error)

    def convert_sheet_to_df(self, sheet_name):
        try:
            sheet = self.workbook[sheet_name]
            data = []
            for row in sheet.iter_rows(values_only=True):
                data.append(list(row))
            df = pd.DataFrame(data)
            df.dropna(how='all', inplace=True)
            df.dropna(how='all', inplace=True, axis=1)
            merged_cells = sheet.merged_cells.ranges
            return df, sheet, merged_cells
        except Exception as df_conversion_error:
            logger.error(df_conversion_error)
