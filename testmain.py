from antlr4 import *
from JavaLexer import JavaLexer
from JavaParser import JavaParser
from FormattingVisitor import FormattingVisitor
from ErrorLogger import ErrorLogger
from ConfigClass import ConfigClass
import re

def load_config(config_path):
    config = ConfigClass(config_path)
    return config

def parse_java_code(file_path):
    with open(file_path, "r") as file:
        code = file.read()
    
    cleaned_code = re.sub(r'[\t\n]+', '', code)  # Remove tabs and newlines
    cleaned_code = re.sub(r' {2,}', ' ', cleaned_code)
    cleaned_code = re.sub(r'^ +', '', cleaned_code, flags=re.M)

    code = cleaned_code

    lexer = JavaLexer(InputStream(code))
    tokens = CommonTokenStream(lexer)
    parser = JavaParser(tokens)
    tree = parser.compilationUnit()

    #print(tree.toStringTree(recog=parser))

    return tree, tokens

tree, tokens = parse_java_code("test2.java")
configs = load_config(".java-format.json")

formatter = FormattingVisitor(tokens, configs)

errorvisitor = ErrorLogger(configs)
errors = errorvisitor.find_errors(tree)
if errors:
    for error in errors:
        print(error)

formatted_code = formatter.get_formatted_code(tree)
print(formatted_code)