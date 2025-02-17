from antlr4 import *
from antlr4.TokenStreamRewriter import TokenStreamRewriter
from JavaLexer import JavaLexer
from JavaParser import JavaParser
from FormattingVisitor import FormattingVisitor
from ErrorLogger import ErrorLogger
from ConfigClass import ConfigClass
from NameConventionFormatterVisitor import NameConventionFormatterVisitor

def load_config():
    # Create an instance of ConfigClass with the default settings
    config = ConfigClass()
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
configs = load_config()  # Use the default configuration

# Create a single TokenStreamRewriter instance
rewriter = TokenStreamRewriter(tokens)

# Apply naming convention formatting
name_formatter = NameConventionFormatterVisitor(rewriter, configs)
name_formatter.visit(tree)

# Print the final formatted output
print(rewriter.getDefaultText())

# Apply code formatting
formatter = FormattingVisitor(rewriter, configs)
formatter.visit(tree)

# Print the final formatted output (optional)
# print(rewriter.getDefaultText())


error_logger = ErrorLogger(configs)
errors = error_logger.find_errors(tree)

if errors:
    print("Naming Convention Errors:")
    for error in errors:
        print(error)
else:
  print("No naming convention errors found.")
