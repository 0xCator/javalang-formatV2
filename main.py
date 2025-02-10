from antlr4 import *
from JavaLexer import JavaLexer
from JavaParser import JavaParser 
from JavaParserVisitor import JavaParserVisitor
import json

class JavaFormatter(JavaParserVisitor):
    def __init__(self, config):
        self.config = config
        self.indent_level = 0
        self.formatted_code = ""

    def get_indent(self):
        return " " * (self.indent_level * self.config.get("indent_size", 4))

    def visitCompilationUnit(self, ctx):
        return self.visitChildren(ctx)

    def visitClassDeclaration(self, ctx):
        class_name = ctx.identifier().getText()
        modifiers = []
        parent = ctx.parentCtx  
        
        if isinstance(parent, JavaParser.TypeDeclarationContext):  
            if parent.classOrInterfaceModifier():
                modifiers = [mod.getText() for mod in parent.classOrInterfaceModifier()]
                modifiers = self.sort_modifiers(modifiers, self.config.get("class_modifier_order", []))

        class_signature = f"{' '.join(modifiers)} class {class_name}".strip()
        self.formatted_code += self.get_indent() + class_signature 
        
        # Brace placement based on config
        if self.config.get("brace_style", "attach") == "attach":
            self.formatted_code += " {\n"
        else:
            self.formatted_code += "\n" + self.get_indent() + "{\n"
        
        self.indent_level += 1
        self.visitChildren(ctx)
        self.indent_level -= 1
        self.formatted_code += self.get_indent() + "}\n"

    def visitMethodDeclaration(self, ctx):
        return_type = ctx.typeTypeOrVoid().getText()
        method_name = ctx.identifier().getText()
        modifiers = []
        parent = ctx.parentCtx  
        if isinstance(parent, JavaParser.MemberDeclarationContext):  
            grandparent = parent.parentCtx  
            if isinstance(grandparent, JavaParser.ClassBodyDeclarationContext):
                if grandparent.modifier():
                    modifiers = [mod.getText() for mod in grandparent.modifier()]
                    modifiers = self.sort_modifiers(modifiers, self.config.get("method_modifier_order", []))

        param_list = ctx.formalParameters().getText()
        method_signature = f"{' '.join(modifiers)} {return_type} {method_name}{param_list}".strip()
        self.formatted_code += self.get_indent() + method_signature
        if self.config.get("brace_style", "attach") == "attach":
            self.formatted_code += " {\n"
        else:
            self.formatted_code += "\n" + self.get_indent() + "{\n"
        
        self.indent_level += 1
        self.visitChildren(ctx)
        self.indent_level -= 1
        self.formatted_code += self.get_indent() + "}\n"

    def sort_modifiers(self, modifiers, order):
        if not order:
            return modifiers
        return sorted(modifiers, key=lambda x: order.index(x) if x in order else len(order))

    def getFormattedCode(self):
        return self.formatted_code.strip()


    def visitBlock(self, ctx):
        if len(ctx.blockStatement()) > 1:
            self.formatted_code += self.get_indent() + "{\n"
            self.indent_level += 1
        
        self.visitChildren(ctx)
        
        if len(ctx.blockStatement()) > 1:
            self.indent_level -= 1
            self.formatted_code += self.get_indent() + "}\n"

    def visitStatement(self, ctx):
        statement = ctx.getText()
        if not statement.endswith(";"):
            statement += ";"
        self.formatted_code += self.get_indent() + statement + "\n"


def load_config(config_path):
    try:
        f = open(config_path, "r")
        return json.load(f)
    except Exception:
        return {}  # Default empty config

def format_java_code(java_code, config):
    lexer = JavaLexer(InputStream(java_code))
    tokens = CommonTokenStream(lexer)
    parser = JavaParser(tokens)
    tree = parser.compilationUnit()

    formatter = JavaFormatter(config)
    formatter.visit(tree)
    return formatter.getFormattedCode()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Java Code Formatter")
    parser.add_argument("input_file", type=str, help="Java file to format")
    parser.add_argument("--config", type=str, default="java-format.json", help="Config file path")
    
    args = parser.parse_args()

    config = load_config(args.config) 
    
    with open(args.input_file, "r") as f:
        java_code = f.read()

    formatted_code = format_java_code(java_code, config)
    print(formatted_code)

