import copy
import json
import re

import numpy as np
import openpyxl
import pandas as pd
from scripts.logging.logger import logger
from scripts.utils.logbook_utils import LogbookUtils


class FormHandler:
    def __init__(self, file_path, sheet_name):
        self.file_path = file_path
        self.sheet_name = sheet_name
        with open("scripts/utils/component.json", 'r') as file:
            self.component_json = json.load(file)
        self.workbook = openpyxl.load_workbook(self.file_path, data_only=True)
        self.unique_key_counter = {}

    def generate_form_json(self):
        try:

            df, _, _ = self.convert_sheet_to_df(self.sheet_name)
            table_no_rows, table_num_cols = df.shape
            arr = df.to_numpy()
            components_list = []
            index_list = []
            for row in range(0, table_no_rows):
                if row in {tup[0] for tup in index_list}:
                    continue
                for col in range(0, table_num_cols):
                    if (row, col) in index_list:
                        continue

                    cell_value = arr[row][col]
                    if cell_value is not None and (re.search(r"<table.*>", cell_value) or re.search(r"<customTable.*>", cell_value)):
                        table_json = copy.deepcopy(self.component_json.get('table'))
                        table_json, index_list = self.process_table_json(df, row, col, table_json, child="rows")
                        components_list.append(table_json)

                    elif cell_value is not None and re.search(r"<html.*>", cell_value):
                        html_components = copy.deepcopy(self.component_json.get("html_compo"))
                        content = str(cell_value).replace("<html>", "").replace('{', '').replace('}', '').strip()
                        html_components["customClass"] = "text-left"
                        html_components["content"] = f"<p style='word-break: break-word;'> {content} </p>"
                        if html_components:
                            components_list.append(html_components)

                    elif cell_value is not None and not re.search(r"<.*>", cell_value):
                        html_components = copy.deepcopy(self.component_json.get("html_compo"))
                        html_components["customClass"] = "text-left"
                        html_components["content"] = "<h6>" + "<center>" + "<b>" + str(cell_value) + "</b>" + "</center>" + "</h6>"
                        if html_components:
                            components_list.append(html_components)

            with open(f'assets/{self.sheet_name}.json', 'w') as json_file:
                json.dump({"components": components_list}, json_file, indent=4)
            print(f"JSON {self.sheet_name} created")
            logger.info(f"{self.sheet_name} -> JSON created successfully!!!!!!!!!!!!")
            return True
            # for i in range(0, table_no_rows):
            #     for j in range(0, table_num_cols):
            #         cell_value = arr[i][j]
            #         if re.search(r"<table.*>", cell_value):
            #             table_json = component_json.get('table')
            #             section_exists = re.search(r"<table:.*>", cell_value)
            #             if section_exists:
            #                 _pattern = r"<table:(.*?)>"
            #                 match = re.search(_pattern, cell_value)
            #                 _sheet = workbook[match.group(1)]
            #                 _data = []
            #                 for row in _sheet.iter_rows(values_only=True):
            #                     _data.append(list(row))
            #                 _df = pd.DataFrame(_sheet)
            #                 _df.dropna(how='all', inplace=True)
            #                 _df.dropna(how='all', inplace=True, axis=1)
            #                 a = ''
            #             else:
            #                 pass
            #             parent_component_details.update({'name': 'table', 'row': 0, 'col': 0, 'index': len(components_list)})
            #             components_list.append(table_json)
            #         elif '<html>' in cell_value:
            #             if parent_component_details.get('name', '') in ['table', 'custom_table']:
            #                 index = parent_component_details['index']
            #                 _row = parent_component_details['row']
            #                 _cols = parent_component_details['col']
            #                 html_json = component_json.get('html_element')
            #                 components_list[index]['rows'][_row].append(html_json)
            #                 _row += 1

        except Exception as e:
            logger.exception(f"exception from the generate form json creator {e}")

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

    @staticmethod
    def process_components():
        try:
            pass
        except Exception as component_error:
            logger.error(component_error)

    @staticmethod
    def process_rows():
        try:
            pass
        except Exception as row_error:
            logger.error(row_error)

    @staticmethod
    def process_column_json():
        try:
            pass
        except Exception as column_error:
            logger.error(column_error)

    def process_table_json(self, df, row, col, table_json, child='rows', from_parent_section=False):
        try:
            index_list = []
            _df = df.copy()
            if from_parent_section:
                row, col = 0, 0

            def find_next_non_none_row(df, current_index):
                start_row, column = current_index
                # Create a boolean mask for non-None values in the specified column after the start_row
                mask = df.iloc[start_row + 1:, column].notna()
                # Find the index of the first True value in the mask
                next_non_none_row = mask.idxmax() if mask.any() else None
                return next_non_none_row

            # Find the next row with a non-None value in the specified column
            next_non_none_row = find_next_non_none_row(_df, (row, col))

            _df = _df.iloc[row:]
            if next_non_none_row and not from_parent_section:
                # Keep only rows up to the specific row index (exclusive)
                _df = _df.iloc[:next_non_none_row]

            if not from_parent_section:
                _df.drop(index=row, inplace=True)
                _df.drop(columns=_df.columns[col], inplace=True)
            _df.dropna(how='all', inplace=True)
            _df.dropna(how='all', inplace=True, axis=1)
            arr = _df.to_numpy()
            table_no_rows, table_num_cols = _df.shape
            if child == 'rows':
                unique_key = 'table'
                if unique_key in self.unique_key_counter:
                    unique_key_count = self.unique_key_counter[unique_key]
                    self.unique_key_counter[unique_key] += unique_key_count
                else:
                    self.unique_key_counter[unique_key] = 1

                table_json.update({
                    "numRows": table_no_rows,
                    "numCols": table_num_cols,
                    'key': f'{unique_key}_{self.unique_key_counter[unique_key]}'
                })
            row_list = []
            _index_list = []
            for new_row in range(0, table_no_rows):
                col_list = []
                if new_row in {tup[0] for tup in _index_list}:
                    continue
                for new_col in range(0, table_num_cols):
                    if (new_row, new_col) in _index_list:
                        continue
                    cell_value = arr[new_row][new_col]
                    # Use numpy.where to find indices where the condition matches
                    row_index, col_index = np.where(df == cell_value)
                    # Since np.where returns arrays of indices, we take the first occurrence
                    try:
                        if row_index and col_index:
                            index_list.append((row_index[0], col_index[0]))
                    except Exception:
                        pass

                    current_component = {"components": []}
                    if cell_value is not None and re.search(r"<html.*>", cell_value):
                        html_components = copy.deepcopy(self.component_json.get("html_compo"))
                        content = str(cell_value).replace("<html>", "").replace('{', '').replace('}', '').strip()
                        html_components["customClass"] = "text-left"
                        html_components["content"] = f"<p style='word-break: break-word;'> {content} </p>"
                        if child == 'rows':
                            current_component["components"].append(html_components)
                            if current_component:
                                col_list.append(current_component)
                        else:
                            row_list.append(html_components)
                    elif cell_value is not None and not re.search(r"<.*>", cell_value):
                        html_components = copy.deepcopy(self.component_json.get("html_compo"))
                        html_components["customClass"] = "text-left"
                        html_components["content"] = "<h6>" + "<center>" + "<b>" + str(cell_value) + "</b>" + "</center>" + "</h6>"
                        if child == 'rows':
                            current_component["components"].append(html_components)
                            if current_component:
                                col_list.append(current_component)
                        else:
                            row_list.append(html_components)
                    elif cell_value is not None and re.search(r"<panel.*>", cell_value):
                        section_exists = re.search(r"<panel:.*>", cell_value)
                        if section_exists:
                            _pattern = r"<panel:(.*?)>"
                            match = re.search(_pattern, cell_value)
                            _sheet = match.group(1)
                            __df, _, _ = self.convert_sheet_to_df(_sheet)
                            _panel_json = copy.deepcopy(self.component_json.get('panel'))
                            _panel_json, _index_list = self.process_table_json(__df, new_row, new_col, _panel_json, child='components', from_parent_section=True)
                            if child == 'rows':
                                current_component["components"].append(_panel_json)
                                if current_component:
                                    col_list.append(current_component)
                            else:
                                row_list.append(_panel_json)

                    elif cell_value is not None and re.search(r"<date.*>", cell_value):
                        date_filed = copy.deepcopy(self.component_json.get("date_time_picker"))
                        unique_key = 'date'
                        if unique_key in self.unique_key_counter:
                            unique_key_count = self.unique_key_counter[unique_key]
                            self.unique_key_counter[unique_key] += unique_key_count
                        else:
                            self.unique_key_counter[unique_key] = 1
                        _match = re.search(r'\{(.*?)\}', cell_value)
                        label = _match.group(1) if _match else ''
                        date_filed['label'] = label
                        if label:
                            date_filed['hideLabel'] = False
                        date_filed["key"] = f'{unique_key}_{self.unique_key_counter[unique_key]}'
                        if child == 'rows':
                            current_component["components"].append(date_filed)
                            if current_component:
                                col_list.append(current_component)
                        else:
                            row_list.append(date_filed)
                    elif cell_value is not None and re.search(r"<time.*>", cell_value):
                        time_filed = copy.deepcopy(self.component_json.get("time"))
                        unique_key = 'time'
                        if unique_key in self.unique_key_counter:
                            unique_key_count = self.unique_key_counter[unique_key]
                            self.unique_key_counter[unique_key] += unique_key_count
                        else:
                            self.unique_key_counter[unique_key] = 1
                        time_filed["key"] = f'{unique_key}_{self.unique_key_counter[unique_key]}'
                        _match = re.search(r'\{(.*?)\}', cell_value)
                        label = _match.group(1) if _match else ''
                        time_filed['label'] = label
                        if label:
                            time_filed['hideLabel'] = False
                        time_filed["properties"] = {"manual_entry": "true"}
                        if child == 'rows':
                            current_component["components"].append(time_filed)
                            if current_component:
                                col_list.append(current_component)
                        else:
                            row_list.append(time_filed)
                    elif cell_value is not None and re.search(r"<text_area.*>", cell_value):
                        text_area = copy.deepcopy(self.component_json.get("text area"))
                        unique_key = 'textarea'
                        if unique_key in self.unique_key_counter:
                            unique_key_count = self.unique_key_counter[unique_key]
                            self.unique_key_counter[unique_key] += unique_key_count
                        else:
                            self.unique_key_counter[unique_key] = 1
                        text_area["key"] = f'{unique_key}_{self.unique_key_counter[unique_key]}'
                        text_area["customClass"] = "w-150px"
                        _match = re.search(r'\{(.*?)\}', cell_value)
                        label = _match.group(1) if _match else ''
                        text_area['label'] = label
                        if label:
                            text_area['hideLabel'] = False
                        if child == 'rows':
                            current_component["components"].append(text_area)
                            if current_component:
                                col_list.append(current_component)
                        else:
                            row_list.append(text_area)
                    elif cell_value is not None and re.search(r"<select.*>", cell_value):
                        data = []
                        dropdown_field = copy.deepcopy(self.component_json.get("drop_down_field"))
                        data_list = [item.strip() for item in str(cell_value).replace("[drop down]", "").split(",")]
                        unique_key = 'select'
                        if unique_key in self.unique_key_counter:
                            unique_key_count = self.unique_key_counter[unique_key]
                            self.unique_key_counter[unique_key] += unique_key_count
                        else:
                            self.unique_key_counter[unique_key] = 1
                        dropdown_field["key"] = f'{unique_key}_{self.unique_key_counter[unique_key]}'
                        dropdown_field["customClass"] = "w-150px"
                        _match = re.search(r'\{(.*?)\}', cell_value)
                        label = _match.group(1) if _match else ''
                        dropdown_field['label'] = label
                        if label:
                            dropdown_field['hideLabel'] = False
                        for item in data_list:
                            data.append({
                                "label": item,
                                "value": item
                            })
                        dropdown_field.get('data')['values'] = data
                        if child == 'rows':
                            current_component["components"].append(dropdown_field)
                            if current_component:
                                col_list.append(current_component)
                        else:
                            row_list.append(dropdown_field)
                    elif cell_value is not None and re.search(r"<number.*>", cell_value):
                        number_field = copy.deepcopy(self.component_json.get("number_field"))
                        unique_key = 'number'
                        if unique_key in self.unique_key_counter:
                            unique_key_count = self.unique_key_counter[unique_key]
                            self.unique_key_counter[unique_key] += unique_key_count
                        else:
                            self.unique_key_counter[unique_key] = 1
                        number_field["key"] = f'{unique_key}_{self.unique_key_counter[unique_key]}'
                        number_field["properties"] = {"manual_entry": "true"}
                        number_field["customClass"] = "w-150px"
                        _match = re.search(r'\{(.*?)\}', cell_value)
                        label = _match.group(1) if _match else ''
                        number_field['label'] = label
                        if label:
                            number_field['hideLabel'] = False
                        if child == 'rows':
                            current_component["components"].append(number_field)
                            if current_component:
                                col_list.append(current_component)
                        else:
                            row_list.append(number_field)
                    elif cell_value is not None and re.search(r"<divider.*>", cell_value):
                        html_components = copy.deepcopy(self.component_json.get("html_compo"))
                        html_components["content"] = f"<p style='word-break: break-word;'> </p>"
                        if child == 'rows':
                            current_component["components"].append(html_components)
                            if current_component:
                                col_list.append(current_component)
                        else:
                            row_list.append(html_components)
                    elif cell_value is not None and re.search(r"<sign.*>", cell_value):
                        digital_sign = copy.deepcopy(self.component_json.get("sign"))
                        unique_key = 'sign'
                        if unique_key in self.unique_key_counter:
                            unique_key_count = self.unique_key_counter[unique_key]
                            self.unique_key_counter[unique_key] += unique_key_count
                        else:
                            self.unique_key_counter[unique_key] = 1
                        digital_sign["key"] = f'{unique_key}_{self.unique_key_counter[unique_key]}'
                        _match = re.search(r'\{(.*?)\}', cell_value)
                        label = _match.group(1) if _match else 'sign'
                        digital_sign['label'] = label
                        if label:
                            digital_sign['hideLabel'] = True
                        if child == 'rows':
                            current_component["components"].append(digital_sign)
                            if current_component:
                                col_list.append(current_component)
                        else:
                            row_list.append(digital_sign)

                    elif cell_value is not None and (re.search(r"<table.*>", cell_value) or re.search(r"<customTable.*>", cell_value)):
                        _table_json = copy.deepcopy(self.component_json.get('table'))
                        _table_json, _index_list = self.process_table_json(_df, new_row, new_col, _table_json, child="rows")
                        if child == 'rows':
                            current_component["components"].append(_table_json)
                            if current_component:
                                col_list.append(current_component)
                        else:
                            row_list.append(_table_json)
                if child == 'rows':
                    if col_list:
                        row_list.append(col_list)
            table_json[child] = row_list
            return table_json, index_list
        except Exception as table_error:
            logger.error(table_error)



    @staticmethod
    def process_component_json(df, row, col, parent_json):
        try:
            pass
        except Exception as column_error:
            logger.error(column_error)