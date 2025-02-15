from antlr4 import *
from JavaLexer import JavaLexer
from JavaParser import JavaParser
from FormattingVisitor import FormattingVisitor
from ErrorLogger import ErrorLogger
from ConfigClass import ConfigClass

def load_config(config_path):
    config = ConfigClass(config_path)
    return config

def parse_java_code(file_path):
    with open(file_path, "r") as file:
        code = file.read()

    lexer = JavaLexer(InputStream(code))
    tokens = CommonTokenStream(lexer)
    parser = JavaParser(tokens)
    tree = parser.compilationUnit()

    return tree, tokens

tree, tokens = parse_java_code("test.java")
configs = load_config(".java-format.json")

formatter = FormattingVisitor(tokens, configs)

errorvisitor = ErrorLogger(configs)
errors = errorvisitor.find_errors(tree)
if errors:
    for error in errors:
        print(error)
print(formatter.get_formatted_code(tree))
