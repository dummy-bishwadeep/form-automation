import subprocess


class FormatError:
    @staticmethod
    def balance_brackets(js_logic):
        opening_brackets = js_logic.count('(')
        closing_brackets = js_logic.count(')')
        if opening_brackets > closing_brackets:
            js_logic += ')' * (opening_brackets - closing_brackets)
        if closing_brackets > opening_brackets:
            js_logic = '(' * (closing_brackets - opening_brackets) + js_logic
        return js_logic

    @staticmethod
    def format_javascript_code(js_code):
        try:
            prettier_path = r"C:\Users\arjun.b\AppData\Roaming\npm\prettier"
            formatted_code = subprocess.check_output([prettier_path, "--parser", "babel", "--stdin"],
                                                     input=js_code.encode("utf-8"), text=True)
        except subprocess.CalledProcessError as e:
            # Handle errors, e.g., Prettier not found, or code formatting fails
            print(f"Error formatting JavaScript code: {e}")
