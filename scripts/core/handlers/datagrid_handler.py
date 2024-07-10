import copy
import json
import logging
import math
import re
import string

import openpyxl
import pandas as pd
from scripts.config import Services
from scripts.utils.fix_error import FormatError
from scripts.utils.logbook_utils import LogbookUtils

logger = logging.getLogger(Services.PROJECT_NAME)


class CreateJson:

    @staticmethod
    def get_datagrid(excel_file_path, sheet_name, length_header, output_file_name, type_row, logic_row, logic_columns):
        with open("scripts/utils/component.json", 'r') as file:
            component_json = json.load(file)
        sheet_name_formatted = re.sub(r'_+', '_', re.sub(r'\([^)]*\)', '',
                                                         sheet_name.lower().replace(' ', '_').strip('_').replace('-',
                                                                                                                 '_'))).rstrip(
            '_')
        data_grid_structure = {
            'components': [{
                'label': 'Data Grid',
                'reorder': False,
                'addAnotherPosition': 'bottom',
                'layoutFixed': False,
                'enableRowGroups': False,
                'initEmpty': False,
                'tableView': False,
                'defaultValue': [{}],
                'key': 'dataGrid',
                'type': 'datagrid',
                'input': True,
                'components': []
            }
            ]
        }
        try:
            workbook = openpyxl.load_workbook(excel_file_path, data_only=False)
            logic_columns = [int(item) for item in logic_columns[0].split(',')]
            sheet = workbook[sheet_name]
            data = []
            for row in sheet.iter_rows(values_only=True):
                data.append(list(row))
            df = pd.DataFrame(data)
            combined_header = df.iloc[:length_header].fillna('').astype(str).agg('<br>'.join, axis=0)
            header_list = pd.DataFrame(combined_header)
            header_dict = header_list[0].to_list()
            header_items_stripped = [item.strip() for item in header_dict]
            formatter = LogbookUtils(header_dict)
            formatted_list = formatter.format_text()
            data_list = df.to_dict(orient='records')
            type_list = [item.strip().replace(' ', '').lower() if isinstance(item, str) else item for item in
                         data_list[type_row].values()]
            logic_row = logic_row - 1
            logic = [item for item in df.iloc[logic_row].values if item is not None]
            logic_list = []
            for cell in logic:
                if isinstance(cell, str) and cell.startswith('='):
                    value = cell.lstrip('=')
                    logic_list.append(value)
            final_response = []
            response_data_grid = data_grid_structure
            component_value = response_data_grid["components"][0]['components']
            index = 0
            uppercase_alphabets = string.ascii_uppercase
            uppercase_alphabet_list = list(uppercase_alphabets)
            api_key_list = []
            manual_entry = {"manual_entry": "true"}
            for type_item, formatted_item, header_item in zip(type_list, formatted_list, header_items_stripped):
                api_key = formatted_item
                unique_api_key = LogbookUtils.make_key_unique(api_key, component_value)
                if type_item in ("Manual", "manual"):
                    response_data_text = copy.deepcopy(component_json.get("text_field"))
                    response_data_text["key"] = unique_api_key
                    if index < 26:
                        api_key_data = {f'{uppercase_alphabet_list[index]}': unique_api_key}
                    else:
                        api_key_data = {
                            f'{uppercase_alphabet_list[(index // 26) - 1]}{uppercase_alphabet_list[index % 26]}': unique_api_key}
                    api_key_list.append(api_key_data)
                    response_data_text["properties"] = manual_entry
                    response_data_text["hideLabel"] = False
                    response_data_text[
                        "label"] = "<h6>" + "<center>" + "<b>" + header_item + "</b>" + "</center>" + "</h6>"
                    component_value.append(response_data_text)
                elif type_item in ("Dropdown", "Drop Down", "Drop down", " Drop down", "dropdown"):
                    data = []
                    response_data_drop_down = copy.deepcopy(component_json.get("drop_down_field"))
                    response_data_drop_down["key"] = unique_api_key
                    if index < 26:
                        api_key_data = {f'{uppercase_alphabet_list[index]}': unique_api_key}
                    else:
                        api_key_data = {
                            f'{uppercase_alphabet_list[(index // 26) - 1]}{uppercase_alphabet_list[index % 26]}': unique_api_key}
                    api_key_list.append(api_key_data)
                    response_data_drop_down["properties"] = manual_entry
                    response_data_drop_down["hideLabel"] = False

                    desired_column_index = index
                    desired_column = [value for value in df[desired_column_index].tolist() if value is not None]
                    data_list = desired_column[length_header + 1:]
                    cleaned_list = [x for x in data_list if not isinstance(x, float) or not math.isnan(x)]

                    response_data_drop_down[
                        "label"] = "<h6>" + "<center>" + "<b>" + header_item + "</b>" + "</center>" + "</h6>"
                    for item in cleaned_list:
                        data.append({
                            "label": item,
                            "value": item
                        })
                    response_data_drop_down.get('data')['values'] = data
                    component_value.append(response_data_drop_down)
                elif type_item in ('"0.0000"', '"0.00"', "number", "Number"):
                    response_data_number = copy.deepcopy(component_json.get("number_field"))
                    response_data_number["key"] = unique_api_key
                    if index < 26:
                        api_key_data = {f'{uppercase_alphabet_list[index]}': unique_api_key}
                    else:
                        api_key_data = {
                            f'{uppercase_alphabet_list[(index // 26) - 1]}{uppercase_alphabet_list[index % 26]}': unique_api_key}
                    api_key_list.append(api_key_data)
                    response_data_number["properties"] = manual_entry
                    response_data_number["hideLabel"] = False
                    response_data_number[
                        "label"] = "<h6>" + "<center>" + "<b>" + header_item + "</b>" + "</center>" + "</h6>"
                    component_value.append(response_data_number)
                elif type_item in ('Auto Fetching', 'Auto ( Fetching )', 'Auto' "fetched", "Fetched", "auto"):
                    response_data_auto_fetch = copy.deepcopy(component_json.get("auto_fetch_field"))
                    response_data_auto_fetch["key"] = unique_api_key
                    if index < 26:
                        api_key_data = {f'{uppercase_alphabet_list[index]}': unique_api_key}
                    else:
                        api_key_data = {
                            f'{uppercase_alphabet_list[(index // 26) - 1]}{uppercase_alphabet_list[index % 26]}': unique_api_key}
                    api_key_list.append(api_key_data)
                    response_data_auto_fetch["properties"] = manual_entry
                    response_data_auto_fetch["hideLabel"] = False
                    response_data_auto_fetch[
                        "label"] = "<h6>" + "<center>" + "<b>" + header_item + "</b>" + "</center>" + "</h6>"
                    component_value.append(response_data_auto_fetch)
                elif type_item in ("radio", "radio button"):
                    data = []
                    response_data_drop_down = copy.deepcopy(component_json.get("radio_button"))
                    response_data_drop_down["key"] = unique_api_key
                    if index < 26:
                        api_key_data = {f'{uppercase_alphabet_list[index]}': unique_api_key}
                    else:
                        api_key_data = {
                            f'{uppercase_alphabet_list[(index // 26) - 1]}{uppercase_alphabet_list[index % 26]}': unique_api_key}
                    api_key_list.append(api_key_data)
                    response_data_drop_down["properties"] = manual_entry
                    response_data_drop_down["hideLabel"] = False
                    desired_column_index = index
                    desired_column = df[desired_column_index].tolist()
                    data_list = desired_column[length_header + 1:]
                    response_data_drop_down[
                        "label"] = "<h6>" + "<center>" + "<b>" + header_item + "</b>" + "</center>" + "</h6>"
                    for item in data_list:
                        data.append({
                            "label": item,
                            "value": item
                        })
                    response_data_drop_down['values'] = data
                    component_value.append(response_data_drop_down)
                elif type_item in ("date", "Date"):
                    date_field = copy.deepcopy(component_json.get('date_time_picker'))
                    date_field['key'] = unique_api_key
                    if index < 26:
                        api_key_data = {f'{uppercase_alphabet_list[index]}': unique_api_key}
                    else:
                        api_key_data = {
                            f'{uppercase_alphabet_list[(index // 26) - 1]}{uppercase_alphabet_list[index % 26]}': unique_api_key}
                    api_key_list.append(api_key_data)
                    date_field[
                        "label"] = "<h6>" + "<center>" + "<b>" + header_item + "</b>" + "</center>" + "</h6>"
                    date_field["hideLabel"] = False
                    component_value.append(date_field)
                elif type_item in ("time", "Time"):
                    time_field = copy.deepcopy(component_json.get('time'))
                    time_field['key'] = unique_api_key
                    if index < 26:
                        api_key_data = {f'{uppercase_alphabet_list[index]}': unique_api_key}
                    else:
                        api_key_data = {
                            f'{uppercase_alphabet_list[(index // 26) - 1]}{uppercase_alphabet_list[index % 26]}': unique_api_key}
                    api_key_list.append(api_key_data)
                    time_field[
                        "label"] = "<h6>" + "<center>" + "<b>" + header_item + "</b>" + "</center>" + "</h6>"
                    time_field["hideLabel"] = False
                    component_value.append(time_field)
                else:
                    response_data_texts = copy.deepcopy(component_json.get("text_field"))
                    response_data_texts["key"] = unique_api_key
                    if index < 26:
                        api_key_data = {f'{uppercase_alphabet_list[index]}': unique_api_key}
                    else:
                        api_key_data = {
                            f'{uppercase_alphabet_list[(index // 26) - 1]}{uppercase_alphabet_list[index % 26]}': unique_api_key}
                    api_key_list.append(api_key_data)
                    response_data_texts["properties"] = manual_entry
                    response_data_texts["hideLabel"] = False
                    response_data_texts[
                        "label"] = "<h6>" + "<center>" + "<b>" + header_item + "</b>" + "</center>" + "</h6>"
                    component_value.append(response_data_texts)
                index += 1
            table_row = component_value
            desired_value = None
            final_logic = ""
            for logic_column, logic_pattern in zip(logic_columns, logic_list):
                unit_row = 0
                js_logic = "var calcValue="
                desired_column = table_row[logic_column - 1]
                dynamic_logic_pattern = logic_pattern
                pattern = r'([A-Z]{1,2}\d+|[+\-*/])'
                tokens = re.findall(pattern, logic_pattern)
                keys = [token for token in tokens if not re.match(r'[+\-*/]', token)]
                for key in keys:
                    key_without_number = re.sub(r'\d+', '', key)
                    desired_key = key_without_number
                    for item in api_key_list:
                        if desired_key in item:
                            desired_value = item[desired_key]
                            dynamic_logic_pattern = dynamic_logic_pattern.replace(key,
                                                                                  f"parseFloat(row['{desired_value}'])")
                            break
                js_logic += dynamic_logic_pattern
                update_value = "\n value = calcValue ? calcValue.toFixed(2) : 0;\n instance.updateValue();"
                js_logic = FormatError.balance_brackets(js_logic)
                lines = js_logic.split('\n')
                value_line = None
                for i, line in enumerate(lines):
                    if "(value=" in line:
                        value_line = line
                        lines[i] = lines[i].replace("(value=", "value=(")
                        break
                formatted_js_logic = "\n".join(lines)
                desired_column['calculateValue'] = formatted_js_logic + update_value
            final_response.append(response_data_grid)
            final_data = final_response[0]
            with open(f'assets/{output_file_name}.json', 'w') as json_file:
                json.dump(final_data, json_file, indent=4)
            logger.info(f"JSON create successfully in file name as {output_file_name}")
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
