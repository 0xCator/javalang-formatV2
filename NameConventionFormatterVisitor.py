from antlr4.TokenStreamRewriter import TokenStreamRewriter
from JavaParserVisitor import JavaParserVisitor
from JavaParser import JavaParser
import re

class NameConventionFormatterVisitor(JavaParserVisitor):
    def __init__(self, rewriter, config):
        self.rewriter = rewriter
        self.config = config
        self.function_calls = []

    def visitClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
        class_name = ctx.identifier().getText()
        print(f"Class name before: {class_name}")
        if not re.match(self.config.naming_conventions['class'], class_name):
            new_class_name = self.convert_to_pascal_case(class_name)
            print(f"Class name after: {new_class_name}")
            self.rewriter.replaceSingleToken(ctx.identifier().start, new_class_name)
            self.replace_usage(class_name, new_class_name)
        return self.visitChildren(ctx)

    def visitMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
        method_name = ctx.identifier().getText()
        print(f"Method name before: {method_name}")
        self.function_calls.append(f"Declared: {method_name}") 
        if not re.match(self.config.naming_conventions['method'], method_name):
            new_method_name = self.convert_to_camel_case(method_name)
            self.function_calls.append(new_method_name)
            print(f"Method name after: {new_method_name}")
            self.rewriter.replaceSingleToken(ctx.identifier().start, new_method_name)
            self.replace_usage(method_name, new_method_name)
        return self.visitChildren(ctx)

    def visitVariableDeclarator(self, ctx: JavaParser.VariableDeclaratorContext):
        variable_name = ctx.variableDeclaratorId().getText()
        print(f"Variable name before: {variable_name}")
        # Convert regular variables to camelCase
        new_variable_name = self.convert_to_camel_case(variable_name)
        if variable_name != new_variable_name:
            print(f"Variable name after: {new_variable_name}")
            self.rewriter.replaceSingleToken(ctx.variableDeclaratorId().start, new_variable_name)
            self.replace_usage(variable_name, new_variable_name)

        return self.visitChildren(ctx)

    def visitFormalParameter(self, ctx: JavaParser.FormalParameterContext):
        parameter_name = ctx.variableDeclaratorId().getText()
        print(f"Parameter name before: {parameter_name}")
        if not re.match(self.config.naming_conventions['parameter'], parameter_name):
            new_parameter_name = self.convert_to_camel_case(parameter_name)
            print(f"Parameter name after: {new_parameter_name}")
            self.rewriter.replaceSingleToken(ctx.variableDeclaratorId().start, new_parameter_name)
            self.replace_parameter_in_method_body(ctx, parameter_name, new_parameter_name)
        return self.visitChildren(ctx)

    def visitMethodCall(self, ctx: JavaParser.MethodCallContext):
            method_name = ctx.identifier().getText()
            self.function_calls.append(method_name)
            return self.visitChildren(ctx)
    
    def replace_usage(self, old_name, new_name):
        for token in self.rewriter.getTokenStream().tokens:
            if token.text == old_name:
                self.rewriter.replaceSingleToken(token, new_name)

    def replace_parameter_in_method_body(self, ctx, old_name, new_name):
        method_body = self.get_method_body(ctx)
        if method_body:
            for token in self.rewriter.getTokenStream().tokens:
                if (token.text == old_name and
                        method_body.start.tokenIndex <= token.tokenIndex <= method_body.stop.tokenIndex):
                    self.rewriter.replaceSingleToken(token, new_name)

    def get_method_body(self, ctx):
        parent = ctx.parentCtx
        while parent:
            if isinstance(parent, JavaParser.MethodDeclarationContext):
                return parent.methodBody()
            parent = parent.parentCtx
        return None

    def convert_to_pascal_case(self, text):
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
        text = re.sub(r"[ _-]+", " ", text).strip()
        return "".join(word.capitalize() for word in text.split())

    def convert_to_camel_case(self, text):
        pascal_case = self.convert_to_pascal_case(text)
        return pascal_case[0].lower() + pascal_case[1:] if pascal_case else ""

    def convert_to_constant_case(self, name):
        return re.sub(r'([a-z])([A-Z])', r'\1_\2', name).upper()
# Example usage:
# config = ConfigClass(".java-format.json")
# visitor = NameConventionFormatterVisitor(tokens, config)
# visitor.visit(tree)
