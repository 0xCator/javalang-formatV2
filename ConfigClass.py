import json

class ConfigClass:
    def __init__(self, config_path):
        self.config_path = config_path

        self.default_config()

        self.read_config()

    def default_config(self):
        self.indent_size = 4
        self.brace_style = 'break'
        self.space_around_operator = True
        self.indentation_type = 'spaces'
        self.max_line_length = 100
        self.class_modifier_order = ['public', 'abstract', 'final']
        self.method_modifier_order = ['public', 'static', 'final']
        self.naming_conventions = {
            'class': 'pascalcase',
            'method': 'camelcase',
            'variable': 'camelcase',
            'parameter': 'camelcase',
            'constant': 'uppercase'
        }
        self.imports = {
            'order': 'preserve',
            'merge': False
        }

    def read_config(self):
        config_json = {}
        try:
            with open(self.config_path) as f:
                config_json = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in '{self.config_path}'.")
            exit(1)
        except Exception as e:
            print(f"Error reading config file: {e}.")
            exit(1)

        
        self.indent_size = config_json.get('indent_size', self.indent_size)
        self.brace_style = config_json.get('brace_style', self.brace_style)
        self.space_around_operator = config_json.get('space_around_operator', self.space_around_operator)
        self.indentation_type = config_json.get('indentation_type', self.indentation_type)
        self.max_line_length = config_json.get('max_line_length', self.max_line_length)
        self.class_modifier_order = config_json.get('class_modifier_order', self.class_modifier_order)
        self.method_modifier_order = config_json.get('method_modifier_order', self.method_modifier_order)
        self.naming_conventions = config_json.get('naming_conventions', self.naming_conventions)
        self.imports = config_json.get('imports', self.imports)

    # Kept for future use
    def save_config(self):
        config = {
            'indent_size': self.indent_size,
            'brace_style': self.brace_style,
            'space_around_operator': self.space_around_operator,
            'max_line_length': self.max_line_length,
            'class_modifier_order': self.class_modifier_order,
            'method_modifier_order': self.method_modifier_order,
            'naming_conventions': self.naming_conventions
        }

        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)
