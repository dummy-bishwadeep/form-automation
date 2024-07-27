import copy
import json

import openpyxl
import pandas as pd

from scripts.utils.logbook_utils import LogbookUtils


class CreateJson:
    @staticmethod
    def get_datagrid(excel_file_path, sheet_name, output_filename):
        try:
            with open("scripts/utils/component.json", 'r') as file:
                component_json = json.load(file)
            workbook = openpyxl.load_workbook(excel_file_path, data_only=True)
            sheet = workbook[sheet_name]
            data = []
            for row in sheet.iter_rows(values_only=True):
                data.append(list(row))
            df = pd.DataFrame(data)
            table_no_rows, table_num_cols = df.shape
            api_key_index = 0
            api_properties_index = 0
            formatted_property_keys = []
            api_keys = None
            for index, row in df.iterrows():
                if "[api keys]" in row.values:
                    api_key_index = index
                if "[properties]" in row.values:
                    api_properties_index = index
            if api_key_index != 0:
                if api_properties_index != 0:
                    api_keys = df.iloc[api_key_index + 1:api_properties_index].values
                else:
                    api_keys = df.iloc[api_key_index + 1:].values

            keys = [item for sublist in api_keys for item in sublist if item is not None]
            formatter = LogbookUtils(keys)
            if api_properties_index != 0:
                api_properties = df.iloc[api_properties_index + 1].values
                formatted_property_keys = [formatter.extract_dict_from_string(item) if isinstance(item, str) else item
                                           for
                                           item in api_properties]
            formatted_keys = formatter.format_text()
            arr = df.to_numpy()
            key_list = []
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
            response_data_grid = data_grid_structure
            component_value = []
            for j in range(0, table_num_cols):
                api_key = formatted_keys[j]
                unique_api_key = LogbookUtils.normal_key_unique(api_key, key_list)
                if arr[1][j] == "[text]":
                    textfield_compo = copy.deepcopy(component_json.get("text_field"))
                    textfield_compo["key"] = unique_api_key
                    textfield_compo["customClass"] = "w-150px"
                    key_list.append(unique_api_key)
                    if formatted_property_keys[j]:
                        textfield_compo["properties"] = formatted_property_keys[j]
                    textfield_compo["hideLabel"] = False
                    textfield_compo[
                        "label"] = "<h6>" + "<center>" + "<b>" + arr[0][j] + "</b>" + "</center>" + "</h6>"
                    component_value.append(textfield_compo)
                elif arr[1][j] == "[number]":
                    number_field = copy.deepcopy(component_json.get("number_field"))
                    number_field["key"] = unique_api_key
                    number_field["customClass"] = "w-150px"
                    key_list.append(unique_api_key)
                    if formatted_property_keys[j]:
                        number_field["properties"] = formatted_property_keys[j]
                    number_field["hideLabel"] = False
                    number_field[
                        "label"] = "<h6>" + "<center>" + "<b>" + arr[0][j] + "</b>" + "</center>" + "</h6>"
                    component_value.append(number_field)
                elif arr[1][j] == "[date]":
                    date_filed = copy.deepcopy(component_json.get("date_time_picker"))
                    date_filed["key"] = unique_api_key
                    key_list.append(unique_api_key)
                    if formatted_property_keys[j]:
                        date_filed["properties"] = formatted_property_keys[j]
                    date_filed["hideLabel"] = False
                    date_filed[
                        "label"] = "<h6>" + "<center>" + "<b>" + arr[0][j] + "</b>" + "</center>" + "</h6>"
                    component_value.append(date_filed)
                elif arr[1][j] == "[text area]":
                    text_area = copy.deepcopy(component_json.get("text area"))
                    text_area["key"] = unique_api_key
                    text_area["customClass"] = "w-150px"
                    key_list.append(unique_api_key)
                    if formatted_property_keys[j]:
                        text_area["properties"] = formatted_property_keys[j]
                    text_area["hideLabel"] = False
                    text_area[
                        "label"] = "<h6>" + "<center>" + "<b>" + arr[0][j] + "</b>" + "</center>" + "</h6>"
                    component_value.append(text_area)
                elif "[check box]" in str(arr[1][j]):
                    check_box = copy.deepcopy(component_json.get("check_box"))
                    check_box["key"] = unique_api_key
                    key_list.append(unique_api_key)
                    if formatted_property_keys[j]:
                        check_box["properties"] = formatted_property_keys[j]
                    check_box["hideLabel"] = False
                    check_box[
                        "label"] = "<h6>" + "<center>" + "<b>" + arr[0][j] + "</b>" + "</center>" + "</h6>"
                    component_value.append(check_box)
                elif arr[1][j] == "[time]":
                    time_filed = copy.deepcopy(component_json.get("time"))
                    time_filed["key"] = unique_api_key
                    key_list.append(unique_api_key)
                    if formatted_property_keys[j]:
                        time_filed["properties"] = formatted_property_keys[j]
                    time_filed["hideLabel"] = False
                    time_filed[
                        "label"] = "<h6>" + "<center>" + "<b>" + arr[0][j] + "</b>" + "</center>" + "</h6>"
                    component_value.append(time_filed)
                elif arr[0][j] == "[sign]":
                    digital_sign = copy.deepcopy(component_json.get("sign"))
                    digital_sign["key"] = unique_api_key
                    key_list.append(unique_api_key)
                    if formatted_property_keys[j]:
                        digital_sign["properties"] = formatted_property_keys[j]
                    digital_sign["hideLabel"] = False
                    digital_sign[
                        "label"] = "<h6>" + "<center>" + "<b>" + arr[0][j] + "</b>" + "</center>" + "</h6>"
                    component_value.append(digital_sign)
                elif "[radio]" in str(arr[1][j]):
                    data = []
                    radio = copy.deepcopy(component_json.get("radio_button"))
                    data_list = [item.strip() for item in arr[1][j].replace("[radio]", "").split(",")]
                    radio["key"] = unique_api_key
                    key_list.append(unique_api_key)
                    if formatted_property_keys[j]:
                        radio["properties"] = formatted_property_keys[j]
                    for item in data_list:
                        data.append({
                            "label": item,
                            "value": item
                        })
                    radio['values'] = data
                    radio["hideLabel"] = False
                    radio[
                        "label"] = "<h6>" + "<center>" + "<b>" + arr[0][j] + "</b>" + "</center>" + "</h6>"
                    component_value.append(radio)
                elif "[drop down]" in str(arr[1][j]):
                    data = []
                    dropdown_field = copy.deepcopy(component_json.get("drop_down_field"))
                    data_list = [item.strip() for item in arr[1][j].replace("[drop down]", "").split(",")]
                    dropdown_field["key"] = unique_api_key
                    key_list.append(unique_api_key)
                    if formatted_property_keys[j]:
                        dropdown_field["properties"] = formatted_property_keys[j]
                    for item in data_list:
                        data.append({
                            "label": item,
                            "value": item
                        })
                    dropdown_field.get('data')['values'] = data
                    dropdown_field["hideLabel"] = False
                    dropdown_field[
                        "label"] = "<h6>" + "<center>" + "<b>" + arr[0][j] + "</b>" + "</center>" + "</h6>"
                    component_value.append(dropdown_field)
                else:
                    html_components = copy.deepcopy(component_json.get("html_compo"))
                    content = arr[0][j].replace("[html]", "").strip()
                    html_components["customClass"] = "text-left"
                    key_list.append(unique_api_key)
                    html_components["content"] = f"<p style='word-break: break-word;'> {content} </p>"
                    html_components["hideLabel"] = False
                    html_components[
                        "label"] = "<h6>" + "<center>" + "<b>" + arr[0][j] + "</b>" + "</center>" + "</h6>"
                    component_value.append(html_components)
            response_data_grid["components"][0]['components'] = component_value
            with open(f'assets/{output_filename}.json', 'w') as json_file:
                json.dump(response_data_grid, json_file, indent=4)
            return True
        except Exception as e:
            print(f"An error occurred: {e}")


