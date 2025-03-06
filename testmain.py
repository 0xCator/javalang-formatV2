from antlr4 import *
from JavaLexer import JavaLexer
from JavaParser import JavaParser
from FormattingVisitor import FormattingVisitor
from AlignmentVisitor import AlignmentVisitor
from ErrorLogger import ErrorLogger
from ConfigClass import ConfigClass
import re

from FileHandler import FileHandler 

def load_config(config_path):
    config = ConfigClass(config_path)
    return config

def parse_java_code(file_path):
    # Use FileHandler to safely read the Java file
    file_handler = FileHandler(file_path)
    code = file_handler.read()
    
    if code is None:
        raise FileNotFoundError(f"Could not read Java file: {file_path}")
    
    cleaned_code = re.sub(r'[\t\n]+', '', code)  # Remove tabs and newlines
    cleaned_code = re.sub(r' {2,}', ' ', cleaned_code)
    cleaned_code = re.sub(r'^ +', '', cleaned_code, flags=re.M)

    code = cleaned_code

    lexer = JavaLexer(InputStream(code))
    tokens = CommonTokenStream(lexer)
    parser = JavaParser(tokens)
    tree = parser.compilationUnit()

    return tree, tokens, code  # Return original code as well

def format_code(tree, tokens, configs):
    formatter = FormattingVisitor(tokens, configs)
    first_code_pass = formatter.get_formatted_code(tree)
    
    lexer = JavaLexer(InputStream(first_code_pass))
    tokens = CommonTokenStream(lexer)
    parser = JavaParser(tokens)
    tree = parser.compilationUnit()

    aligner = AlignmentVisitor(tokens, configs)
    second_code_pass = aligner.get_formatted_code(tree)

    return second_code_pass

def save_formatted_code(file_path, formatted_code):
    file_handler = FileHandler(file_path)
    
    
    if not file_handler.write(formatted_code):
        print(f"Error writing formatted code to {file_path}")
        print("Original file was preserved.")
        return False

    
    return True

def main(java_file_path, config_path=".java-format.json"):
    try:
        configs = load_config(config_path)
        if configs is None:
            return False
        
        tree, tokens, _ = parse_java_code(java_file_path)
        
        errorvisitor = ErrorLogger(configs)
        errors = errorvisitor.find_errors(tree)
        if errors:
            for error in errors:
                print(error)
        
        formatted_code = format_code(tree, tokens, configs)
        
        success = save_formatted_code(java_file_path, formatted_code)
        
        if success:
            print(f"Successfully formatted {java_file_path}")
            print(formatted_code)
        
        return success
    
    except Exception as e:
        print(f"An error occurred during formatting: {str(e)}")
        return False

if __name__ == "__main__":
    main("test2.java")
