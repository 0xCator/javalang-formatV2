from antlr4.TokenStreamRewriter import TokenStreamRewriter
from JavaParserVisitor import JavaParserVisitor
from JavaParser import JavaParser
import re

class NameConventionFormatterVisitor(JavaParserVisitor):
    def __init__(self, rewriter, config):
        self.rewriter = rewriter
        self.config = config

    def visitClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
        class_name = ctx.identifier().getText()
        print(f"Class name before: {class_name}")
        if not re.match(self.config.naming_conventions['class'], class_name):
            new_class_name = self.convert_to_pascal_case(class_name)
            print(f"Class name after: {new_class_name}")
            self.rewriter.replaceSingleToken(ctx.identifier().start, new_class_name)
            self.replace_class_usages(class_name, new_class_name)
        return self.visitChildren(ctx)

    def visitMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
        method_name = ctx.identifier().getText()
        print(f"Method name before: {method_name}")
        if not re.match(self.config.naming_conventions['method'], method_name):
            new_method_name = self.convert_to_camel_case(method_name)
            print(f"Method name after: {new_method_name}")
            self.rewriter.replaceSingleToken(ctx.identifier().start, new_method_name)
            self.replace_method_calls(method_name, new_method_name)
        return self.visitChildren(ctx)

    def visitVariableDeclarator(self, ctx: JavaParser.VariableDeclaratorContext):
        variable_name = ctx.variableDeclaratorId().getText()
        print(f"Variable name before: {variable_name}")

        is_const = self.is_constant(ctx) # Cache the result
        if is_const:
            print(f"Identified as constant: {variable_name}")
            if not re.match(self.config.naming_conventions['constant'], variable_name):
                new_variable_name = self.convert_to_upper_case(variable_name)
                print(f"Constant name after: {new_variable_name}")
                self.rewriter.replaceSingleToken(ctx.variableDeclaratorId().start, new_variable_name)
        else:
            print(f"Identified as regular variable: {variable_name}")
            if not re.match(self.config.naming_conventions['variable'], variable_name):
                new_variable_name = self.convert_to_camel_case(variable_name)
                print(f"Variable name after: {new_variable_name}")
                self.rewriter.replaceSingleToken(ctx.variableDeclaratorId().start, new_variable_name)
                self.replace_variable_usages(variable_name, new_variable_name)
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

    def replace_class_usages(self, old_name, new_name):
        for token in self.rewriter.getTokenStream().tokens:
            if token.text == old_name:
                self.rewriter.replaceSingleToken(token, new_name)

    def replace_method_calls(self, old_name, new_name):
        for token in self.rewriter.getTokenStream().tokens:
            if token.text == old_name:
                self.rewriter.replaceSingleToken(token, new_name)

    def is_method_call(self, token):
        # Check if the token is part of a method call
        index = token.tokenIndex
        tokens = self.rewriter.getTokenStream().tokens
        if index > 0 and tokens[index - 1].text == '.':
            return True
        if index < len(tokens) - 1 and tokens[index + 1].text == '(':
            return True
        return False

    def replace_variable_usages(self, old_name, new_name):
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

    def is_constant(self, ctx: JavaParser.VariableDeclaratorContext):
        parent = ctx.parentCtx
        while parent is not None and not isinstance(parent, JavaParser.FieldDeclarationContext):
            parent = parent.parentCtx
        if parent is not None:
            grandparent = parent.parentCtx
            if hasattr(grandparent, 'classOrInterfaceModifier'):
                modifiers = [mod.getText() for mod in grandparent.classOrInterfaceModifier()]
                print(f"Modifiers found: {modifiers}")
                return 'final' in modifiers and 'static' in modifiers
        return False

    def convert_to_pascal_case(self, name):
        return ''.join(word.capitalize() for word in re.split(r'_|-| ', name))

    def convert_to_camel_case(self, name):
        words = re.split(r'_|-| ', name)
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])

    def convert_to_upper_case(self, name):
        return name.upper()

# Example usage:
# config = ConfigClass(".java-format.json")
# visitor = NameConventionFormatterVisitor(tokens, config)
# visitor.visit(tree)

