import re
from scripts.logging.logger import logger


class LogbookUtils:
    def __init__(self, header):
        self.header = header

    def format_text(self):
        try:
            # Ensure self.header is a list
            if not isinstance(self.header, list):
                raise ValueError("header must be a list")
            formatted_list_ = [
                re.sub(r'\([^)]*\)|\[[^\]]*\]', '', item).replace(' ', '_').replace('-', '_').replace('/', '').replace(
                    '.', '').replace('&', '').replace('\n', '').strip('_').lower()  # remove unwanted characters
                for item in self.header
            ]
            formatted_list = [re.sub(r'\([^)]*\)', '', re.sub(r'_{2,}', '_', item)).replace('%', '') for item in
                              formatted_list_]
            return formatted_list
        except Exception as e:
            logger.exception(f"Exception from formatting header: {e}")

    @staticmethod
    def normal_key_unique(key, key_list):
        try:
            count = 1
            new_key = key
            while new_key in key_list:
                new_key = f"{key}_{count}"
                count += 1
            return new_key
        except Exception as e:
            logger.exception(f"exception from normal key unique {e}")

    @staticmethod
    def make_key_unique(key, data):
        try:
            keys_set = {item["key"] for item in data}
            original_key = key
            count = 1
            while key in keys_set:
                key = f"{original_key}_{count}"
                count += 1
            return key
        except Exception as e:
            logger.exception(f"exception from making unique key {e}")

    @staticmethod
    def find_merged_cells(merged_cells):
        try:
            merge = []
            for merged_range in merged_cells:
                start_row, start_col, end_row, end_col = (
                    merged_range.min_row,
                    merged_range.min_col,
                    merged_range.max_row,
                    merged_range.max_col,
                )
                span = ""
                if start_row == end_row:
                    span = "colSpan"
                elif start_col == end_col:
                    span = "rowSpan"
                else:
                    span = "rowCol"
                merge.append({"Row Range start": start_row, "Row Range end": end_row, "Column Range start": start_col,
                              "Column Range end": end_col, "span": span})
            return merge
        except Exception as e:
            logger.exception(f"exception from find the merge cell details {e}")

    @staticmethod
    def extract_dict_from_string(string):
        if string is None:
            return None
        pairs = string.split(',')
        result_dict = {}
        for pair in pairs:
            key_value_pair = pair.split(':', 1)  # Split only at the first colon
            key = key_value_pair[0].strip()  # Remove leading/trailing whitespace from key
            value = key_value_pair[1].strip() if len(key_value_pair) > 1 else ""  # Handle case where value is empty
            result_dict[key] = value
        return result_dict

