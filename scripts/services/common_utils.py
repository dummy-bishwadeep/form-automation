import pandas as pd
from scripts.logging.logger import logger

class CommonUtils:
    def __init__(self, workbook=None):
        self.workbook = workbook

    def convert_sheet_to_df(self, sheet_name):
        try:
            sheet = self.workbook[sheet_name]
            data = []
            for row in sheet.iter_rows(values_only=True):
                data.append(list(row))
            df = pd.DataFrame(data)
            df = df.copy()
            df.dropna(how='all', inplace=True)
            df.dropna(how='all', inplace=True, axis=1)
            merged_cells = sheet.merged_cells.ranges
            return df, sheet, merged_cells
        except Exception as df_conversion_error:
            logger.error(df_conversion_error)

    def find_next_non_none_row(self, df, current_index):
        start_row, column = current_index
        # Create a boolean mask for non-None values in the specified column after the start_row
        mask = df.iloc[start_row + 1:, column].notna()
        # Find the index of the first True value in the mask
        next_non_none_row = mask.idxmax() if mask.any() else None
        return next_non_none_row
