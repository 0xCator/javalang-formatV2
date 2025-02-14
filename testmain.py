from antlr4 import *
from JavaLexer import JavaLexer
from JavaParser import JavaParser
from FormattingVisitor import FormattingVisitor
from ErrorLogger import ErrorLogger
import json

def load_config(config_path):
    try:
        f = open(config_path, "r")
        return json.load(f)
    except Exception:
        return {}  # Default empty config

def parse_java_code(file_path):
    with open(file_path, "r") as file:
        code = file.read()

    lexer = JavaLexer(InputStream(code))
    tokens = CommonTokenStream(lexer)
    parser = JavaParser(tokens)
    tree = parser.compilationUnit()

    return tree, tokens

tree, tokens = parse_java_code("test.java")
config = load_config(".java-format.json")

formatter = FormattingVisitor(tokens, config)

naming_convention_configs = config.get("naming_conventions", {})

errorvisitor = ErrorLogger(naming_convention_configs)
errors = errorvisitor.find_errors(tree)
if errors:
    for error in errors:
        print(error)