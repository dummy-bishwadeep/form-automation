import copy
import json
import re
import numpy as np
import openpyxl
import pandas as pd
from scripts.logging.logger import logger
from scripts.utils.logbook_utils import LogbookUtils


class FormHandler:
    def __init__(self, file_path, sheet_name, current_ts):
        self.file_path = file_path
        self.sheet_name = sheet_name
        with open("scripts/utils/component.json", 'r') as file:
            self.component_json = json.load(file)
        self.workbook = openpyxl.load_workbook(self.file_path, data_only=True)
        self.unique_key_counter = {}
        self.current_ts = current_ts

    def generate_form_json(self):
        try:
            # convert excel data into dataframe
            df, _, _ = self.convert_sheet_to_df(self.sheet_name)
            table_no_rows, table_num_cols = df.shape
            arr = df.to_numpy()
            components_list = []
            index_list = []

            # iterating through each rows and columns from the initial worksheet
            for row in range(0, table_no_rows):
                # skip rows when component section are already iterated
                if row in {tup[0] for tup in index_list}:
                    continue
                for col in range(0, table_num_cols):
                    # skip columns when component section are already iterated
                    if (row, col) in index_list:
                        continue

                    # fetch cell value
                    cell_value = arr[row][col]

                    # generate component data based on its types
                    if cell_value is not None and re.search(r"<html.*>", cell_value):
                        components_list, _, _ = self.process_html_component(
                            from_parent_itr=True,
                            cell_value=cell_value,
                            components_list=components_list)

                    elif cell_value is not None and not re.search(r"<.*>", cell_value):
                        components_list, _, _ = self.process_header_html_component(
                            from_parent_itr=True,
                            cell_value=cell_value,
                            components_list=components_list)

                    elif cell_value is not None and (re.search(r"<text_area.*>", cell_value) or re.search(r"<text_field.*>", cell_value)):
                        components_list, _, _ = self.process_text_area_component(
                            from_parent_itr=True,
                            cell_value=cell_value,
                            components_list=components_list)

                    elif cell_value is not None and re.search(r"<panel.*>", cell_value):
                        components_list, _, _, index_list = self.process_panel_component(
                            from_parent_itr=True,
                            cell_value=cell_value,
                            components_list=components_list,
                            row=row,
                            col=col,
                            df=df)

                    elif cell_value is not None and re.search(r"<date.*>", cell_value):
                        components_list, _, _ = self.process_date_component(
                            from_parent_itr=True,
                            cell_value=cell_value,
                            components_list=components_list)

                    elif cell_value is not None and re.search(r"<time.*>", cell_value):
                        components_list, _, _ = self.process_time_component(
                            from_parent_itr=True,
                            cell_value=cell_value,
                            components_list=components_list)

                    elif cell_value is not None and re.search(r"<select.*>", cell_value):
                        components_list, _, _ = self.process_dropdown_component(
                            from_parent_itr=True,
                            cell_value=cell_value,
                            components_list=components_list)

                    elif cell_value is not None and re.search(r"<radio.*>", cell_value):
                        components_list, _, _ = self.process_radio_component(
                            from_parent_itr=True,
                            cell_value=cell_value,
                            components_list=components_list)

                    elif cell_value is not None and re.search(r"<number.*>", cell_value):
                        components_list, _, _ = self.process_number_component(
                            from_parent_itr=True,
                            cell_value=cell_value,
                            components_list=components_list)

                    elif cell_value is not None and re.search(r"<divider.*>", cell_value):
                        components_list, _, _ = self.process_divider_component(
                            from_parent_itr=True,
                            components_list=components_list)

                    elif cell_value is not None and re.search(r"<sign.*>", cell_value):
                        components_list, _, _ = self.process_esign_component(
                            from_parent_itr=True,
                            cell_value=cell_value,
                            components_list=components_list)

                    elif cell_value is not None and (re.search(r"<table.*>", cell_value) or re.search(r"<customTable.*>", cell_value)):
                        components_list, _, _, index_list = self.process_table_component(
                            from_parent_itr=True,
                            cell_value=cell_value,
                            components_list=components_list,
                            row=row,
                            col=col,
                            df=df)

                    elif cell_value is not None and (re.search(r"<dataGrid.*>", cell_value)):
                        components_list, _, index_list = self.process_datagrid_component(
                            from_parent_itr=True,
                            components_list=components_list,
                            row=row,
                            col=col,
                            df=df)

                    elif cell_value is not None and re.search(r"<columns.*>", cell_value):
                        components_list, _, _, index_list = self.process_columns_component(
                            from_parent_itr=True,
                            cell_value=cell_value,
                            components_list=components_list,
                            row=row,
                            col=col,
                            df=df)

            #storing final form json to a file
            file_name = f'{self.sheet_name}_{self.current_ts}'
            with open(f'assets/{file_name}.json', 'w') as json_file:
                json.dump({"components": components_list}, json_file, indent=4)
            print(f"JSON {file_name} created")
            logger.info(f"{file_name} -> JSON created successfully!!!!!!!!!!!!")
            return True

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

    def process_table_json(self, df, row, col, table_json, child='rows', from_parent_section=False, child_sheet=None):
        try:
            index_list = []
            _df = df.copy()

            merge = []
            if from_parent_section:
                row, col = 0, 0
                merged_cells = child_sheet.merged_cells.ranges
                merge = LogbookUtils.find_merged_cells(merged_cells)
                merge = [] if merge is None else merge

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
                _df = _df.iloc[:next_non_none_row-row]

            if not from_parent_section:
                _df.drop(index=row, inplace=True)
                _df.drop(columns=_df.columns[col], inplace=True)
            _df.dropna(how='all', inplace=True)
            _df.dropna(how='all', inplace=True, axis=1)
            arr = _df.to_numpy()
            table_no_rows, table_num_cols = _df.shape
            if child in ['rows', "dataGrid"]:
                unique_key = 'table'
                if child == 'dataGrid':
                    unique_key = "dataGrid"
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

                    merge_properties = {}
                    for merge_index in merge:
                        row_range_start = merge_index["Row Range start"] - 1
                        col_range_start = merge_index["Column Range start"] - 1
                        span = merge_index['span']
                        if new_row == row_range_start and new_col == col_range_start:
                            if span == 'rowSpan':
                                rowspan_value = merge_index["Row Range end"] - merge_index["Row Range start"] + 1
                                merge_properties = {
                                    'rowSpan': rowspan_value
                                }
                            elif span == 'colSpan':
                                colspan_value = merge_index["Column Range end"] - merge_index["Column Range start"] + 1
                                merge_properties = {
                                    'colSpan': colspan_value
                                }
                            for merge_row_index in range(merge_index["Row Range start"], merge_index["Row Range end"]-1):
                                for merge_col_index in range(merge_index["Column Range start"], merge_index["Column Range end"]-1):
                                    _index_list.append((merge_row_index, merge_col_index))
                            break

                    current_component = {"components": []}
                    if cell_value is not None and re.search(r"<html.*>", cell_value):
                        _, row_list, col_list = self.process_html_component(
                            cell_value=cell_value,
                            merge_properties=merge_properties,
                            child=child,
                            current_component=current_component,
                            row_list=row_list,
                            col_list=col_list)

                    elif cell_value is not None and not re.search(r"<.*>", cell_value):
                        _, row_list, col_list = self.process_header_html_component(
                            cell_value=cell_value,
                            merge_properties=merge_properties,
                            child=child,
                            current_component=current_component,
                            row_list=row_list,
                            col_list=col_list)

                    elif cell_value is not None and re.search(r"<panel.*>", cell_value):
                        _, row_list, col_list, _index_list = self.process_panel_component(
                            cell_value=cell_value,
                            merge_properties=merge_properties,
                            child=child,
                            current_component=current_component,
                            row_list=row_list,
                            col_list=col_list,
                            row=new_row,
                            col=new_col,
                            df=_df)

                    elif cell_value is not None and re.search(r"<date.*>", cell_value):
                        _, row_list, col_list = self.process_date_component(
                            cell_value=cell_value,
                            merge_properties=merge_properties,
                            child=child,
                            current_component=current_component,
                            row_list=row_list,
                            col_list=col_list)

                    elif cell_value is not None and re.search(r"<time.*>", cell_value):
                        _, row_list, col_list = self.process_time_component(
                            cell_value=cell_value,
                            merge_properties=merge_properties,
                            child=child,
                            current_component=current_component,
                            row_list=row_list,
                            col_list=col_list
                        )

                    elif cell_value is not None and (
                            re.search(r"<text_area.*>", cell_value) or re.search(r"<text_field.*>", cell_value)):
                        _, row_list, col_list = self.process_text_area_component(
                            cell_value=cell_value,
                            merge_properties=merge_properties,
                            child=child,
                            current_component=current_component,
                            row_list=row_list,
                            col_list=col_list)

                    elif cell_value is not None and re.search(r"<select.*>", cell_value):
                        _, row_list, col_list = self.process_dropdown_component(
                            cell_value=cell_value,
                            merge_properties=merge_properties,
                            child=child,
                            current_component=current_component,
                            row_list=row_list,
                            col_list=col_list)

                    elif cell_value is not None and re.search(r"<radio.*>", cell_value):
                        _, row_list, col_list  =self.process_radio_component(
                            cell_value=cell_value,
                            merge_properties=merge_properties,
                            child=child,
                            current_component=current_component,
                            row_list=row_list,
                            col_list=col_list)

                    elif cell_value is not None and re.search(r"<number.*>", cell_value):
                        components_list, row_list, col_list = self.process_number_component(
                            cell_value=cell_value,
                            merge_properties=merge_properties,
                            child=child,
                            current_component=current_component,
                            row_list=row_list,
                            col_list=col_list)

                    elif cell_value is not None and re.search(r"<divider.*>", cell_value):
                        components_list, row_list, col_list = self.process_divider_component(
                            merge_properties=merge_properties,
                            child=child,
                            current_component=current_component,
                            row_list=row_list,
                            col_list=col_list)

                    elif cell_value is not None and re.search(r"<sign.*>", cell_value):
                        components_list, row_list, col_list = self.process_esign_component(
                            cell_value=cell_value,
                            merge_properties=merge_properties,
                            child=child,
                            current_component=current_component,
                            row_list=row_list,
                            col_list=col_list)

                    elif cell_value is not None and (re.search(r"<table.*>", cell_value) or re.search(r"<customTable.*>", cell_value)):
                        components_list, row_list, col_list, _index_list = self.process_table_component(
                            cell_value=cell_value,
                            merge_properties=merge_properties,
                            child=child,
                            current_component=current_component,
                            row_list=row_list,
                            col_list=col_list,
                            row=new_row,
                            col=new_col,
                            df=_df)

                    elif cell_value is not None and (re.search(r"<dataGrid.*>", cell_value)):
                        components_list, row_list, _index_list = self.process_datagrid_component(
                            merge_properties=merge_properties,
                            row_list=row_list,
                            row=new_row,
                            col=new_col,
                            df=_df)

                    elif cell_value is not None and re.search(r"<columns.*>", cell_value):
                        components_list, row_list, col_list, _index_list = self.process_columns_component(
                            cell_value=cell_value,
                            merge_properties=merge_properties,
                            child=child,
                            current_component=current_component,
                            row_list=row_list,
                            col_list=col_list,
                            row=new_row,
                            col=new_col,
                            df=_df)

                if child == 'rows' and col_list:
                    row_list.append(col_list)
            if child == 'dataGrid':
                table_json["components"] = row_list
            elif child == "columns":
                if row_list:
                    first_col = row_list[0]
                    second_col = {}
                    if len(row_list) > 1:
                        second_col = row_list[1]
                    if first_col:
                        table_json[child][0]["components"].insert(0, first_col)
                    if second_col:
                        table_json[child][1]["components"].insert(0, second_col)
            else:
                table_json[child] = row_list
            return table_json, index_list
        except Exception as table_error:
            logger.error(table_error)


    def extract_dropdown_values(self, cell_value):
        try:
            match = re.search(r'\[(.*?)\]', cell_value)
            if match:
                extracted_string = match.group(1)
                extracted_list = eval(extracted_string)
                return extracted_list
            return []
        except Exception as dropdown_error:
            logger.error(dropdown_error)

    def process_html_component(self, from_parent_itr=False, cell_value=None, components_list=None,
                               merge_properties=None, child=None, current_component=None, row_list=None,
                               col_list=None):
        try:
            # fetch static html component json
            html_components = copy.deepcopy(self.component_json.get("html_compo"))
            content = str(cell_value).replace("<html>", "").replace('{', '').replace('}', '').strip()
            html_components["customClass"] = "text-left"
            html_components["content"] = f"<p style='word-break: break-word;'> {content} </p>"

            unique_key_id = self.generate_unique_id(comp_type='html')
            html_components['key'] = unique_key_id

            if from_parent_itr:
                if html_components:
                    components_list.append(html_components)
            else:
                # if any rows/columns are merged
                if merge_properties:
                    html_components['properties'] = merge_properties

                if child == 'rows':
                    current_component["components"].append(html_components)
                    if current_component:
                        col_list.append(current_component)
                else:
                    row_list.append(html_components)

            return components_list, row_list, col_list
        except Exception as row_error:
            logger.error(row_error)

    def process_header_html_component(self, from_parent_itr=False, cell_value=None, components_list=None,
                                      merge_properties=None, child=None, current_component=None,
                                      row_list=None, col_list=None):
        try:
            html_components = copy.deepcopy(self.component_json.get("html_compo"))
            html_components["customClass"] = "text-left"
            html_components["content"] = "<h6>" + "<center>" + "<b>" + str(
                cell_value) + "</b>" + "</center>" + "</h6>"

            unique_key_id = self.generate_unique_id(comp_type='html')
            html_components['key'] = unique_key_id

            if from_parent_itr:
                if html_components:
                    components_list.append(html_components)
            else:
                if merge_properties:
                    html_components['properties'] = merge_properties
                if child == 'rows':
                    current_component["components"].append(html_components)
                    if current_component:
                        col_list.append(current_component)
                else:
                    row_list.append(html_components)

            return components_list, row_list, col_list
        except Exception as row_error:
            logger.error(row_error)

    def process_text_area_component(self, from_parent_itr=False, cell_value=None, components_list=None,
                                    merge_properties=None, child=None, current_component=None,
                                    row_list=None, col_list=None):
        try:
            text_area = copy.deepcopy(self.component_json.get("text area"))
            unique_key = 'textarea'
            if re.search(r"<text_field.*>", cell_value):
                text_area = copy.deepcopy(self.component_json.get('text_field'))
                unique_key = 'textfield'

            unique_key_id = self.generate_unique_id(comp_type=unique_key)
            text_area["key"] = unique_key_id

            _match = re.search(r'\{(.*?)\}', cell_value)
            label = _match.group(1) if _match else ''
            text_area['label'] = f"<h6> <b>{label}</b> </h6>"
            if merge_properties:
                text_area['properties'] = merge_properties
            if label:
                text_area['hideLabel'] = False

            if from_parent_itr:
                if text_area:
                    components_list.append(text_area)
            else:
                if child == 'rows':
                    current_component["components"].append(text_area)
                    if current_component:
                        col_list.append(current_component)
                else:
                    row_list.append(text_area)

            return components_list, row_list, col_list
        except Exception as row_error:
            logger.error(row_error)

    def process_panel_component(self, from_parent_itr=False, cell_value=None, components_list=None,
                                merge_properties=None, child=None, current_component=None,
                                row_list=None, col_list=None, row=None, col=None, df=None):
        try:
            _panel_json = copy.deepcopy(self.component_json.get('panel'))

            unique_key_id = self.generate_unique_id(comp_type='panel')
            _panel_json['key'] = unique_key_id

            if from_parent_itr:
                _panel_json, index_list = self.process_table_json(df, row, col, _panel_json,
                                                                  child='components')
                if _panel_json:
                    components_list.append(_panel_json)
            else:
                section_exists = re.search(r"<panel:.*>", cell_value)
                if section_exists:
                    _pattern = r"<panel:(.*?)>"
                    match = re.search(_pattern, cell_value)
                    _sheet = match.group(1)
                    __df, _wb_sheet, _ = self.convert_sheet_to_df(_sheet)
                    _panel_json, index_list = self.process_table_json(__df, row, col, _panel_json,
                                                                       child='components', from_parent_section=True,
                                                                       child_sheet=_wb_sheet)
                else:
                    _panel_json, index_list = self.process_table_json(df, row, col, _panel_json,
                                                                       child='components')
                if merge_properties:
                    _panel_json['properties'] = merge_properties
                if child == 'rows':
                    current_component["components"].append(_panel_json)
                    if current_component:
                        col_list.append(current_component)
                else:
                    row_list.append(_panel_json)

            return components_list, row_list, col_list, index_list
        except Exception as row_error:
            logger.error(row_error)

    def process_date_component(self, from_parent_itr=False, cell_value=None, components_list=None,
                               merge_properties=None, child=None, current_component=None, row_list=None,
                               col_list=None):
        try:
            date_filed = copy.deepcopy(self.component_json.get("date_time_picker"))

            unique_key_id = self.generate_unique_id(comp_type='date')
            date_filed["key"] = unique_key_id

            _match = re.search(r'\{(.*?)\}', cell_value)
            label = _match.group(1) if _match else ''
            date_filed['label'] = f"<h6> <b>{label}</b> </h6>"
            if label:
                date_filed['hideLabel'] = False
            # date_filed["key"] = f'{unique_key}_{self.unique_key_counter[unique_key]}'

            if from_parent_itr:
                if date_filed:
                    components_list.append(date_filed)
            else:
                if merge_properties:
                    date_filed['properties'] = merge_properties
                if child == 'rows':
                    current_component["components"].append(date_filed)
                    if current_component:
                        col_list.append(current_component)
                else:
                    row_list.append(date_filed)

            return components_list, row_list, col_list
        except Exception as row_error:
            logger.error(row_error)

    def process_time_component(self, from_parent_itr=False, cell_value=None, components_list=None,
                               merge_properties=None, child=None, current_component=None, row_list=None,
                               col_list=None):
        try:
            time_filed = copy.deepcopy(self.component_json.get("time"))

            unique_key_id = self.generate_unique_id(comp_type='time')
            time_filed["key"] = unique_key_id

            # time_filed["key"] = f'{unique_key}_{self.unique_key_counter[unique_key]}'
            _match = re.search(r'\{(.*?)\}', cell_value)
            label = _match.group(1) if _match else ''
            time_filed['label'] = f"<h6> <b>{label}</b> </h6>"
            if merge_properties:
                time_filed['properties'] = merge_properties
            if label:
                time_filed['hideLabel'] = False
            time_filed["properties"] = {"manual_entry": "true"}

            if from_parent_itr:
                if time_filed:
                    components_list.append(time_filed)
            else:
                if child == 'rows':
                    current_component["components"].append(time_filed)
                    if current_component:
                        col_list.append(current_component)
                else:
                    row_list.append(time_filed)

            return components_list, row_list, col_list
        except Exception as row_error:
            logger.error(row_error)

    def process_dropdown_component(self, from_parent_itr=False, cell_value=None, components_list=None,
                                   merge_properties=None, child=None, current_component=None,
                                   row_list=None, col_list=None):
        try:
            data = []
            dropdown_field = copy.deepcopy(self.component_json.get("drop_down_field"))
            data_list = self.extract_dropdown_values(cell_value)

            unique_key_id = self.generate_unique_id(comp_type='time')
            dropdown_field['key'] = unique_key_id

            _match = re.search(r'\{(.*?)\}', cell_value)
            label = _match.group(1) if _match else ''
            dropdown_field['label'] = f"<h6> <b>{label}</b> </h6>"
            if merge_properties:
                dropdown_field['properties'] = merge_properties
            if label:
                dropdown_field['hideLabel'] = False
            for item in data_list:
                data.append({
                    "label": item,
                    "value": item
                })
            dropdown_field.get('data')['values'] = data

            if from_parent_itr:
                if dropdown_field:
                    components_list.append(dropdown_field)
            else:
                if child == 'rows':
                    current_component["components"].append(dropdown_field)
                    if current_component:
                        col_list.append(current_component)
                else:
                    row_list.append(dropdown_field)

            return components_list, row_list, col_list
        except Exception as row_error:
            logger.error(row_error)

    def process_radio_component(self, from_parent_itr=False, cell_value=None, components_list=None,
                                merge_properties=None, child=None, current_component=None, row_list=None,
                                col_list=None):
        try:
            data = []
            dropdown_field = copy.deepcopy(self.component_json.get("radio_button"))
            data_list = self.extract_dropdown_values(cell_value)

            unique_key_id = self.generate_unique_id(comp_type='radio')
            dropdown_field['key'] = unique_key_id

            _match = re.search(r'\{(.*?)\}', cell_value)
            label = _match.group(1) if _match else ''
            dropdown_field['label'] = f"<h6> <b>{label}</b> </h6>"
            if merge_properties:
                dropdown_field['properties'] = merge_properties
            if label:
                dropdown_field['hideLabel'] = False
            for item in data_list:
                data.append({
                    "label": item,
                    "value": item
                })
            dropdown_field['values'] = data

            if from_parent_itr:
                if dropdown_field:
                    components_list.append(dropdown_field)
            else:
                if child == 'rows':
                    current_component["components"].append(dropdown_field)
                    if current_component:
                        col_list.append(current_component)
                else:
                    row_list.append(dropdown_field)

            return components_list, row_list, col_list
        except Exception as row_error:
            logger.error(row_error)

    def process_number_component(self, from_parent_itr=False, cell_value=None, components_list=None,
                                 merge_properties=None, child=None, current_component=None, row_list=None,
                                 col_list=None):
        try:
            number_field = copy.deepcopy(self.component_json.get("number_field"))

            unique_key_id = self.generate_unique_id(comp_type='number')
            number_field['key'] = unique_key_id

            number_field["properties"] = {"manual_entry": "true"}
            if merge_properties:
                number_field['properties'].update(merge_properties)
            _match = re.search(r'\{(.*?)\}', cell_value)
            label = _match.group(1) if _match else ''
            number_field['label'] = f"<h6> <b>{label}</b> </h6>"
            if label:
                number_field['hideLabel'] = False

            if from_parent_itr:
                if number_field:
                    components_list.append(number_field)
            else:
                if child == 'rows':
                    current_component["components"].append(number_field)
                    if current_component:
                        col_list.append(current_component)
                else:
                    row_list.append(number_field)

            return components_list, row_list, col_list
        except Exception as row_error:
            logger.error(row_error)

    def process_divider_component(self, from_parent_itr=False, components_list=None,
                                  merge_properties=None, child=None, current_component=None,
                                  row_list=None, col_list=None):
        try:
            html_components = copy.deepcopy(self.component_json.get("html_compo"))
            html_components["content"] = f"<p style='word-break: break-word;'> </p>"

            unique_key_id = self.generate_unique_id(comp_type='html')
            html_components['key'] = unique_key_id

            if from_parent_itr:
                if html_components:
                    components_list.append(html_components)
            else:
                if merge_properties:
                    html_components['properties'] = merge_properties
                if child == 'rows':
                    current_component["components"].append(html_components)
                    if current_component:
                        col_list.append(current_component)
                else:
                    row_list.append(html_components)

            return components_list, row_list, col_list
        except Exception as row_error:
            logger.error(row_error)

    def process_esign_component(self, from_parent_itr=False, cell_value=None, components_list=None,
                                merge_properties=None, child=None, current_component=None, row_list=None,
                                col_list=None):
        try:
            digital_sign = copy.deepcopy(self.component_json.get("sign"))

            unique_key_id = self.generate_unique_id(comp_type='sign')
            digital_sign["key"] = unique_key_id

            _match = re.search(r'\{(.*?)\}', cell_value)
            label = _match.group(1) if _match else 'sign'
            digital_sign['label'] = f"<h6> <b>{label}</b> </h6>"
            signature_properties = {
                "signature_keys": unique_key_id
            }
            digital_sign['properties'] = signature_properties
            if merge_properties:
                digital_sign['properties'].update(merge_properties)
            if label:
                digital_sign['hideLabel'] = True
                if label == 'sign':
                    digital_sign['label'] = unique_key_id

            if from_parent_itr:
                if digital_sign:
                    components_list.append(digital_sign)
            else:
                if child == 'rows':
                    current_component["components"].append(digital_sign)
                    if current_component:
                        col_list.append(current_component)
                else:
                    row_list.append(digital_sign)

            return components_list, row_list, col_list
        except Exception as row_error:
            logger.error(row_error)

    def process_table_component(self, from_parent_itr=False, cell_value=None, components_list=None,
                                merge_properties=None, child=None, current_component=None, row_list=None,
                                col_list=None, row=None, col=None, df=None):
        try:
            _pattern = r"<table:(.*?)>"
            _table_json = copy.deepcopy(self.component_json.get('table'))
            section_exists = re.search(r"<table:.*>", cell_value)
            unique_key = 'table'
            if re.search(r"<customTable.*>", cell_value):
                _table_json = copy.deepcopy(self.component_json.get('customTable'))
                section_exists = re.search(r"<customTable:.*>", cell_value)
                _pattern = r"<customTable:(.*?)>"
                unique_key = 'customTable'

            unique_key_id = self.generate_unique_id(comp_type=unique_key)
            _table_json['key'] = unique_key_id

            if from_parent_itr:
                _table_json, _index_list = self.process_table_json(df, row, col, _table_json,
                                                                 child="rows")
                if _table_json:
                    components_list.append(_table_json)
            else:
                if section_exists:
                    match = re.search(_pattern, cell_value)
                    _sheet = match.group(1)
                    __df, _wb_sheet, _ = self.convert_sheet_to_df(_sheet)
                    _table_json, _index_list = self.process_table_json(__df, row, col, _table_json,
                                                                       child="rows", from_parent_section=True,
                                                                       child_sheet=_wb_sheet)
                else:
                    _table_json, _index_list = self.process_table_json(df, row, col, _table_json, child="rows")
                if merge_properties:
                    _table_json['properties'] = merge_properties
                if child == 'rows':
                    current_component["components"].append(_table_json)
                    if current_component:
                        col_list.append(current_component)
                else:
                    row_list.append(_table_json)

            return components_list, row_list, col_list, _index_list
        except Exception as row_error:
            logger.error(row_error)

    def process_datagrid_component(self, from_parent_itr=False, components_list=None,
                                   merge_properties=None, row_list=None, row=None, col=None, df=None):
        try:
            datagrid_json = copy.deepcopy(self.component_json.get('dataGrid'))

            unique_key_id = self.generate_unique_id(comp_type='dateGrid')
            datagrid_json['key'] = unique_key_id

            datagrid_json, index_list = self.process_table_json(df, row, col, datagrid_json, child="dataGrid")

            if from_parent_itr:
                if datagrid_json:
                    components_list.append(datagrid_json)
            else:
                if merge_properties:
                    datagrid_json['properties'] = merge_properties
                row_list.append(datagrid_json)

            return components_list, row_list, index_list
        except Exception as row_error:
            logger.error(row_error)

    def process_columns_component(self, from_parent_itr=False, cell_value=None, components_list=None,
                                  merge_properties=None, child=None, current_component=None,
                                  row_list=None, col_list=None, row=None, col=None, df=None):
        try:
            _pattern = r"<columns:(.*?)>"
            _table_json = copy.deepcopy(self.component_json.get('columns'))
            section_exists = re.search(r"<columns:.*>", cell_value)

            unique_key_id = self.generate_unique_id(comp_type='columns')
            _table_json['key'] = unique_key_id

            if from_parent_itr:
                _table_json, _index_list = self.process_table_json(df, row, col, _table_json, child="columns")
                if _table_json:
                    components_list.append(_table_json)
            else:
                if section_exists:
                    match = re.search(_pattern, cell_value)
                    _sheet = match.group(1)
                    __df, _wb_sheet, _ = self.convert_sheet_to_df(_sheet)
                    _table_json, _index_list = self.process_table_json(__df, row, col, _table_json,
                                                                       child="columns", from_parent_section=True,
                                                                       child_sheet=_wb_sheet)
                else:
                    _table_json, _index_list = self.process_table_json(df, row, col, _table_json,
                                                                       child="columns")
                if merge_properties:
                    _table_json['properties'] = merge_properties
                if child == 'rows':
                    current_component["components"].append(_table_json)
                    if current_component:
                        col_list.append(current_component)
                else:
                    row_list.append(_table_json)

            return components_list, row_list, col_list, _index_list
        except Exception as row_error:
            logger.error(row_error)

    def generate_unique_id(self, comp_type):
        try:
            unique_key = copy.deepcopy(comp_type)
            if unique_key in self.unique_key_counter:
                unique_key_count = self.unique_key_counter[unique_key]
                self.unique_key_counter[unique_key] += unique_key_count
            else:
                self.unique_key_counter[unique_key] = 1
            unique_key_id = f'{unique_key}_{self.unique_key_counter[unique_key]}'
            return unique_key_id
        except Exception as id_error:
            logger.error(id_error)
