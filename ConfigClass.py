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

    def read_config(self):
        config_json = {}
        try:
            with open(self.config_path) as f:
                config_json = json.load(f)
        except Exception:
            print("Error reading config file. Using default config.")
            return
        
        self.indent_size = config_json.get('indent_size', self.indent_size)
        self.brace_style = config_json.get('brace_style', self.brace_style)
        self.space_around_operator = config_json.get('space_around_operator', self.space_around_operator)
        self.max_line_length = config_json.get('max_line_length', self.max_line_length)
        self.class_modifier_order = config_json.get('class_modifier_order', self.class_modifier_order)
        self.method_modifier_order = config_json.get('method_modifier_order', self.method_modifier_order)
        self.naming_conventions = config_json.get('naming_conventions', self.naming_conventions)

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