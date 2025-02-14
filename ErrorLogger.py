from JavaParser import JavaParser
from JavaParserVisitor import JavaParserVisitor
from StandardNamingConventions import StandardNamingConventions
import re

class ErrorLogger(JavaParserVisitor):
    def __init__(self, naming_convention_configs):
        self.naming_convention_configs = naming_convention_configs
        self.error_log = []

    def visitClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
        class_name = ctx.identifier().getText()
        
        if "class" in self.naming_convention_configs:
            class_config = self.naming_convention_configs["class"]

            if StandardNamingConventions.PASCAL_CASE.value in class_config and not self._is_pascal_case(class_name):
                self.error_log.append(f"Class name {class_name} should be in PascalCase")
        
        return self.visitChildren(ctx)
    
    def visitMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
        method_name = ctx.identifier().getText()
        
        if "method" in self.naming_convention_configs:
            method_config = self.naming_convention_configs["method"]

            if StandardNamingConventions.CAMEL_CASE.value in method_config and not self._is_camel_case(method_name):
                self.error_log.append(f"Method name {method_name} should be in camelCase")

        return self.visitChildren(ctx)
    
    def visitFieldDeclaration(self, ctx: JavaParser.FieldDeclarationContext):
        declarators = ctx.variableDeclarators()
        modifiers = [mod.getText() for mod in ctx.parentCtx.parentCtx.modifier()]
        is_final = "final" in modifiers
        is_static = "static" in modifiers

        if "variable" in self.naming_convention_configs:
            variable_config = self.naming_convention_configs["variable"]
        
        if "constant" in self.naming_convention_configs:
            constant_config = self.naming_convention_configs["constant"]

        for declarator in declarators.variableDeclarator():
            variable_name = declarator.variableDeclaratorId().getText()
            if is_final and is_static:
                if StandardNamingConventions.UPPER_CASE.value in constant_config and not self._is_upper_case(variable_name):
                    self.error_log.append(f"Static final variable name {variable_name} should be in UPPER_CASE")
            else:
                if StandardNamingConventions.CAMEL_CASE.value in variable_config and not self._is_camel_case(variable_name):
                    self.error_log.append(f"Variable name {variable_name} should be in camelCase")
    
        return self.visitChildren(ctx)
    
    def visitLocalVariableDeclaration(self, ctx: JavaParser.LocalVariableDeclarationContext):
        declarators = ctx.variableDeclarators()

        for declarator in declarators.variableDeclarator():
            variable_name = declarator.variableDeclaratorId().getText()
            if "variable" in self.naming_convention_configs:
                variable_config = self.naming_convention_configs["variable"]
                if StandardNamingConventions.CAMEL_CASE.value in variable_config and not self._is_camel_case(variable_name):
                    self.error_log.append(f"Variable name {variable_name} should be in camelCase")
                    
        return self.visitChildren(ctx)
        

    def _is_pascal_case(self, name):
        return bool(re.fullmatch(r"[A-Z][a-zA-Z0-9]*", name))

    def _is_camel_case(self, name):
        return bool(re.fullmatch(r"[a-z][a-zA-Z0-9]*", name))
    
    def _is_upper_case(self, name):
        return bool(re.fullmatch(r"[A-Z][A-Z0-9_]*", name))

    def find_errors(self, tree):
        self.error_log = []
        self.visit(tree)
        return self.error_log