import copy
import json
import openpyxl
import pandas as pd
from scripts.config.constants import Logics
from scripts.logging.logger import logger
from scripts.utils.logbook_utils import LogbookUtils


class TableMergeHandler:
    @staticmethod
    def merge_table(file_path, sheet_name):
        try:
            with open("scripts/utils/component.json", 'r') as file:
                component_json = json.load(file)
            workbook = openpyxl.load_workbook(file_path, data_only=True)
            sheet = workbook[sheet_name]
            data = []
            for row in sheet.iter_rows(values_only=True):
                data.append(list(row))
            df = pd.DataFrame(data)
            merged_cells = sheet.merged_cells.ranges
            table_no_rows, table_num_cols = df.shape
            merge = LogbookUtils.find_merged_cells(merged_cells)
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
            table_structure = {
                "components": [
                    {
                        "label": "Table",
                        "cellAlignment": "left",
                        "key": "table",
                        "type": "table",
                        "input": False,
                        "hideLabel": True,
                        "bordered": True,
                        "tableView": False,
                        "rows": [],
                        "numRows": api_key_index,
                        "numCols": table_num_cols
                    }
                ]
            }
            # creating the table
            manual_entry = {"manual_entry": "true"}
            for i in range(0, table_no_rows - 2):
                table_rows = []
                for j in range(0, table_num_cols):
                    current_component = {"components": []}
                    api_key = formatted_keys[j]
                    unique_api_key = LogbookUtils.normal_key_unique(api_key, key_list)
                    if arr[i][j]:
                        multi_component = arr[i][j].split(',')
                    print()
                    if str(arr[i][j]) == "None":
                        current_component["components"].append(Logics.merge_compo)
                    else:
                        if "[text]" in arr[i][j]:
                            textfield_compo = copy.deepcopy(component_json.get("text_field"))
                            unique_api_key = LogbookUtils.normal_key_unique(api_key, key_list)
                            textfield_compo["key"] = unique_api_key
                            textfield_compo["customClass"] = "w-150px"
                            key_list.append(unique_api_key)
                            if formatted_property_keys[j]:
                                textfield_compo["properties"] = formatted_property_keys[j]
                            current_component["components"].insert(multi_component.index('[text]'), textfield_compo)

                        if "[number]" in arr[i][j]:
                            number_field = copy.deepcopy(component_json.get("number_field"))
                            unique_api_key = LogbookUtils.normal_key_unique(api_key, key_list)
                            number_field["key"] = unique_api_key
                            number_field["properties"] = manual_entry
                            number_field["customClass"] = "w-150px"
                            key_list.append(unique_api_key)
                            if formatted_property_keys[j]:
                                number_field["properties"] = formatted_property_keys[j]
                            current_component["components"].insert(multi_component.index("[number]"), number_field)
                        if "[date]" in arr[i][j]:
                            date_filed = copy.deepcopy(component_json.get("date_time_picker"))
                            unique_api_key = LogbookUtils.normal_key_unique(api_key, key_list)
                            date_filed["key"] = unique_api_key
                            key_list.append(unique_api_key)
                            if formatted_property_keys[j]:
                                date_filed["properties"] = formatted_property_keys[j]
                            current_component["components"].insert(multi_component.index("[date]" ), date_filed)
                        if "[text area]" in arr[i][j]:
                            text_area = copy.deepcopy(component_json.get("text area"))
                            unique_api_key = LogbookUtils.normal_key_unique(api_key, key_list)
                            text_area["key"] = unique_api_key
                            text_area["customClass"] = "w-150px"
                            key_list.append(unique_api_key)
                            if formatted_property_keys[j]:
                                text_area["properties"] = formatted_property_keys[j]
                            current_component["components"].insert(multi_component.index("[text area]"), text_area)
                        if "[check box]" in str(arr[i][j]):
                            check_box = copy.deepcopy(component_json.get("check_box"))
                            unique_api_key = LogbookUtils.normal_key_unique(api_key, key_list)
                            check_box["key"] = unique_api_key
                            data_value = arr[i][j].replace("[check box]", "").strip()
                            check_box["label"] = data_value
                            key_list.append(unique_api_key)
                            if formatted_property_keys[j]:
                                check_box["properties"] = formatted_property_keys[j]
                            current_component["components"].insert(multi_component.index("[check box]"), check_box)
                        if "[time]" in arr[i][j]:
                            time_filed = copy.deepcopy(component_json.get("time"))
                            unique_api_key = LogbookUtils.normal_key_unique(api_key, key_list)
                            time_filed["key"] = unique_api_key
                            time_filed["properties"] = manual_entry
                            key_list.append(unique_api_key)
                            if formatted_property_keys[j]:
                                time_filed["properties"] = formatted_property_keys[j]
                            current_component["components"].insert(multi_component.index("[time]"), time_filed)
                        if "[sign]" in arr[i][j]:
                            digital_sign = copy.deepcopy(component_json.get("sign"))
                            digital_sign["properties"] = manual_entry
                            unique_api_key = LogbookUtils.normal_key_unique(api_key, key_list)
                            digital_sign["key"] = unique_api_key
                            key_list.append(unique_api_key)
                            if formatted_property_keys[j]:
                                digital_sign["properties"] = formatted_property_keys[j]
                            current_component["components"].insert(multi_component.index("[sign]"), digital_sign)
                        if "[radio]" in str(arr[i][j]):
                            data = []
                            radio = copy.deepcopy(component_json.get("radio_button"))
                            data_list = [item.strip() for item in arr[i][j].replace("[radio]", "").split(",")]
                            unique_api_key = LogbookUtils.normal_key_unique(api_key, key_list)
                            radio["key"] = unique_api_key
                            radio["customClass"] = "w-200px"
                            key_list.append(unique_api_key)
                            if formatted_property_keys[j]:
                                radio["properties"] = formatted_property_keys[j]
                            for item in data_list:
                                data.append({
                                    "label": item,
                                    "value": item
                                })
                            radio['values'] = data
                            current_component["components"].insert(multi_component.index("[radio]"), radio)
                        if "[drop down]" in str(arr[i][j]):
                            data = []
                            dropdown_field = copy.deepcopy(component_json.get("drop_down_field"))
                            data_list = [item.strip() for item in arr[i][j].replace("[drop down]", "").split(",")]
                            unique_api_key = LogbookUtils.normal_key_unique(api_key, key_list)
                            dropdown_field["key"] = unique_api_key
                            dropdown_field["customClass"] = "w-150px"
                            key_list.append(unique_api_key)
                            if formatted_property_keys[j]:
                                dropdown_field["properties"] = formatted_property_keys[j]
                            for item in data_list:
                                data.append({
                                    "label": item,
                                    "value": item
                                })
                            dropdown_field.get('data')['values'] = data
                            current_component["components"].insert(multi_component.index("[drop down]"), dropdown_field)
                        if "[html]" in str(arr[i][j]):
                            html_components = copy.deepcopy(component_json.get("html_compo"))
                            content = arr[i][j].replace("[html]", "").strip()
                            html_components["customClass"] = "text-left"
                            key_list.append(unique_api_key)
                            html_components["content"] = f"<p style='word-break: break-word;'> {content} </p>"
                            current_component["components"].insert(multi_component.index("[html]"), html_components)
                        if arr[i][j] == "[null]":
                            current_component["components"].append()
                        if not current_component["components"] and arr[i][j] != "[null]":
                            html_components = copy.deepcopy(component_json.get("html_compo"))
                            html_components["content"] = "<h6>" + "<center>" + "<b>" + str(
                                arr[i][j]) + "</b>" + "</center>" + "</h6>"
                            current_component["components"].append(html_components)
                    table_rows.append(current_component)
                table_structure["components"][0]["rows"].append(table_rows)
            # mering the rows and columns
            for i in merge:
                logic_row = copy.deepcopy(Logics.logic_rows)
                logic_col = copy.deepcopy(Logics.logic_cols)
                logic_row_col = copy.deepcopy(Logics.logic_row_cols)
                if i["span"] == "rowSpan":
                    merge_row = i["Row Range start"] - 1
                    merge_col = i["Column Range start"] - 1
                    rowspan_value = i["Row Range end"] - i["Row Range start"] + 1
                    placeholder = "$$$rowSpan$$"
                    if placeholder in logic_row[0]["actions"][0]["customAction"]:
                        logic_rows_span = logic_row[0]["actions"][0]["customAction"].replace(placeholder,
                                                                                             str(rowspan_value))
                        logic_row[0]["actions"][0]["customAction"] = logic_rows_span
                        table_structure["components"][0]["rows"][merge_row][merge_col]["components"][0][
                            "customClass"] = "text-center"
                        if table_structure["components"][0]["rows"][merge_row][merge_col]["components"][0].get(
                                "content") != "Merge":
                            table_structure["components"][0]["rows"][merge_row][merge_col]["components"][0][
                                "logic"] = logic_row
                if i["span"] == "colSpan":
                    merge_row = i["Row Range start"] - 1
                    merge_col = i["Column Range start"] - 1
                    colspan_value = i["Column Range end"] - i["Column Range start"] + 1
                    placeholder = "$$$colSpan$$"
                    if placeholder in logic_col[0]["actions"][0]["customAction"]:
                        logic_cols_span = logic_col[0]["actions"][0]["customAction"].replace(placeholder,
                                                                                             str(colspan_value))
                        logic_col[0]["actions"][0]["customAction"] = logic_cols_span
                        table_structure["components"][0]["rows"][merge_row][merge_col]["components"][0][
                            "customClass"] = "text-center"
                        if table_structure["components"][0]["rows"][merge_row][merge_col]["components"][0].get(
                                "content") != "Merge":
                            table_structure["components"][0]["rows"][merge_row][merge_col]["components"][0][
                                "logic"] = logic_col
                if i["span"] == "rowCol":
                    merge_row = i["Row Range start"] - 1
                    merge_col = i["Column Range start"] - 1
                    colspan_value = i["Column Range end"] - i["Column Range start"] + 1
                    rowspan_value = i["Row Range end"] - i["Row Range start"] + 1
                    placeholder = "$$$colSpan$$"
                    placeholder_row = "$$$rowSpan$$"
                    if placeholder in logic_row_col[0]["actions"][0]["customAction"]:
                        logic_cols_span = logic_row_col[0]["actions"][0]["customAction"].replace(placeholder,
                                                                                                 str(colspan_value))
                        logic_row_col[0]["actions"][0]["customAction"] = logic_cols_span
                        if (table_structure["components"][0]["rows"][merge_row][merge_col]["components"]):
                            table_structure["components"][0]["rows"][merge_row][merge_col]["components"][0][
                                "customClass"] = "text-center"
                            if table_structure["components"][0]["rows"][merge_row][merge_col]["components"][0][
                                "content"] != "Merge":
                                table_structure["components"][0]["rows"][merge_row][merge_col]["components"][0][
                                    "logic"] = logic_row_col
                    if placeholder_row in logic_row_col[0]["actions"][0]["customAction"]:
                        logic_cols_span = logic_row_col[0]["actions"][0]["customAction"].replace(placeholder_row,
                                                                                                 str(rowspan_value))
                        logic_row_col[0]["actions"][0]["customAction"] = logic_cols_span
                        if (table_structure["components"][0]["rows"][merge_row][merge_col]["components"]):
                            table_structure["components"][0]["rows"][merge_row][merge_col]["components"][0][
                                "customClass"] = "text-center"
                            if table_structure["components"][0]["rows"][merge_row][merge_col]["components"][0][
                                "content"] != "Merge":
                                table_structure["components"][0]["rows"][merge_row][merge_col]["components"][0][
                                    "logic"] = logic_row_col
            with open(f'assets/{sheet_name}.json', 'w') as json_file:
                json.dump(table_structure, json_file, indent=4)
            print(f"JSON {sheet_name} created")
            logger.info(f"{sheet_name} -> JSON created successfully!!!!!!!!!!!!")
            return True
        except Exception as e:
            logger.exception(f"exception from the table json creator {e}")

