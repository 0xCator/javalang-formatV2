from antlr4 import *
from antlr4.TokenStreamRewriter import TokenStreamRewriter
from JavaLexer import JavaLexer
from JavaParser import JavaParser
from FormattingVisitor import FormattingVisitor
from ErrorLogger import ErrorLogger
from ConfigClass import ConfigClass
from NameConventionFormatterVisitor import NameConventionFormatterVisitor

# ... (load_config and parse_java_code functions remain the same)
def load_config():
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
configs = load_config()

formatter_rewriter = TokenStreamRewriter(tokens)

# Apply code formatting
formatter = FormattingVisitor(formatter_rewriter, configs)
formatter.visit(tree)

formatted_code = formatter_rewriter.getDefaultText()
print("Formatted Code:\n", formatted_code)

formatted_lexer = JavaLexer(InputStream(formatted_code))
formatted_tokens = CommonTokenStream(formatted_lexer)
formatted_parser = JavaParser(formatted_tokens)
formatted_tree = formatted_parser.compilationUnit()


name_rewriter = TokenStreamRewriter(formatted_tokens) 

# Apply naming convention formatting
name_formatter = NameConventionFormatterVisitor(name_rewriter, configs)
name_formatter.visit(formatted_tree) 


name_formatted_code = name_rewriter.getDefaultText()
print("\nName Formatted Code:\n", name_formatted_code)  

error_logger = ErrorLogger(configs)
errors = error_logger.find_errors(formatted_tree)  # Check errors on the formatted tree

if errors:
    print("Naming Convention Errors:")
    for error in errors:
        print(error)
else:
    print("No naming convention errors found.")