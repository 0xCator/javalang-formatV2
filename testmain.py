from antlr4 import *
from antlr4.TokenStreamRewriter import TokenStreamRewriter
from JavaLexer import JavaLexer
from JavaParser import JavaParser
from FormattingVisitor import FormattingVisitor
from ErrorLogger import ErrorLogger
from ConfigClass import ConfigClass
from NameConventionFormatterVisitor import NameConventionFormatterVisitor

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

# Create a single TokenStreamRewriter instance
rewriter = TokenStreamRewriter(tokens)

# Apply naming convention formatting
name_formatter = NameConventionFormatterVisitor(rewriter, configs)
name_formatter.visit(tree)
# Print the final formatted output
# print(rewriter.getDefaultText())
# Apply code formatting
formatter = FormattingVisitor(rewriter, configs)
formatter.visit(tree)

# Print the final formatted output
print(rewriter.getDefaultText())