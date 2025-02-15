class NameConventionHandler:
    @staticmethod
    def to_pascal_case(name):
        return ''.join(word.capitalize() for word in name.split('_'))

    @staticmethod
    def to_camel_case(name):
        words = name.split('_')
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])

    @staticmethod
    def to_full_case(name):
        return name.upper()
