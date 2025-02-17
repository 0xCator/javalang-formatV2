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
        if not re.match(self.config.naming_conventions['class'], class_name):
            new_class_name = self.convertToPascalCase(class_name)
            self.rewriter.replaceSingleToken(ctx.identifier().start, new_class_name)
            self.replaceUsage(class_name, new_class_name)
        return self.visitChildren(ctx)

    def visitCreator(self, ctx: JavaParser.CreatorContext):
        class_name = ctx.createdName().getText()

        if not re.match(self.config.naming_conventions['class'], class_name):
            new_class_name = self.convertToPascalCase(class_name)
            self.rewriter.replaceSingleToken(ctx.createdName().start, new_class_name)
            self.replaceUsage(class_name, new_class_name)

        return self.visitChildren(ctx)

    def visitQualifiedName(self, ctx: JavaParser.QualifiedNameContext):
        identifiers = ctx.identifier()
        for identifier in identifiers:
            name = identifier.getText()

            if not re.match(self.config.naming_conventions['class'], name):
                new_name = self.convert_to_pascal_case(name)
                self.rewriter.replaceSingleToken(identifier.start, new_name)
                self.replace_usage(name, new_name)

        return self.visitChildren(ctx)

    def visitTypeType(self, ctx: JavaParser.TypeTypeContext):
        if ctx.classOrInterfaceType():
            type_name = ctx.classOrInterfaceType().getText()

            if not re.match(self.config.naming_conventions['class'], type_name):
                new_type_name = self.convertToPascalCase(type_name)
                self.rewriter.replaceSingleToken(ctx.classOrInterfaceType().start, new_type_name)
                self.replaceUsage(type_name, new_type_name)

        return self.visitChildren(ctx)

    def visitExpression(self, ctx: JavaParser.ExpressionContext):
        if ctx.primary() and ctx.primary().identifier():
            static_call = ctx.primary().identifier().getText()

            if not re.match(self.config.naming_conventions['class'], static_call):
                new_static_call = self.convert_to_pascal_case(static_call)
                self.rewriter.replaceSingleToken(ctx.primary().identifier().start, new_static_call)
                self.replace_usage(static_call, new_static_call)

        return self.visitChildren(ctx)

    def visitAnnotation(self, ctx: JavaParser.AnnotationContext):
        annotation_name = ctx.qualifiedName().getText()

        if not re.match(self.config.naming_conventions['class'], annotation_name):
            new_annotation_name = self.convert_to_pascal_case(annotation_name)
            self.rewriter.replaceSingleToken(ctx.qualifiedName().start, new_annotation_name)
            self.replace_usage(annotation_name, new_annotation_name)

        return self.visitChildren(ctx)

    def visitMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
        method_name = ctx.identifier().getText()
        self.function_calls.append(f"Declared: {method_name}") 
        if not re.match(self.config.naming_conventions['method'], method_name):
            new_method_name = self.convertToCamelCase(method_name)
            self.function_calls.append(new_method_name)
            self.rewriter.replaceSingleToken(ctx.identifier().start, new_method_name)
            self.replaceUsage(method_name, new_method_name)
        return self.visitChildren(ctx)

    def visitFieldDeclaration(self, ctx: JavaParser.FieldDeclarationContext):
        declarators = ctx.variableDeclarators()
        modifiers = [mod.getText() for mod in ctx.parentCtx.parentCtx.modifier()]
        is_static = "static" in modifiers
        is_final = "final" in modifiers

        variable_config = self.config.naming_conventions["variable"]
        constant_config = self.config.naming_conventions["constant"]

        for declarator in declarators.variableDeclarator():
            field_name = declarator.variableDeclaratorId().getText()

            if is_static and is_final:
                if not re.match(constant_config, field_name):
                    new_field_name = self.convertToConstantCase(field_name)  # Convert to constant case
                    self.rewriter.replaceSingleToken(declarator.variableDeclaratorId().start, new_field_name)
                    self.replaceUsage(field_name, new_field_name)
            else:
                if not re.match(variable_config, field_name):
                    new_field_name = self.convertToCamelCase(field_name)
                    self.rewriter.replaceSingleToken(declarator.variableDeclaratorId().start, new_field_name)
                    self.replaceUsage(field_name, new_field_name)


        return self.visitChildren(ctx)
    
    def visitLocalVariableDeclaration(self, ctx: JavaParser.LocalVariableDeclarationContext):
        declarators = ctx.variableDeclarators()
        variable_config = self.config.naming_conventions["variable"]

        for declarator in declarators.variableDeclarator():
            variable_name = declarator.variableDeclaratorId().getText()

            if not re.match(variable_config, variable_name):
                new_variable_name = self.convertToCamelCase(variable_name)
                self.rewriter.replaceSingleToken(declarator.variableDeclaratorId().start, new_variable_name)
                self.replaceUsage(variable_name, new_variable_name)

        return self.visitChildren(ctx)

    def visitVariableDeclarator(self, ctx: JavaParser.VariableDeclaratorContext):
        variable_name = ctx.variableDeclaratorId().getText()
        # Convert regular variables to camelCase
        new_variable_name = self.convertToCamelCase(variable_name)
        if variable_name != new_variable_name:
            self.rewriter.replaceSingleToken(ctx.variableDeclaratorId().start, new_variable_name)
            self.replaceUsage(variable_name, new_variable_name)

        return self.visitChildren(ctx)

    def visitFormalParameter(self, ctx: JavaParser.FormalParameterContext):
        parameter_name = ctx.variableDeclaratorId().getText()
        if not re.match(self.config.naming_conventions['parameter'], parameter_name):
            new_parameter_name = self.convertToCamelCase(parameter_name)
            self.rewriter.replaceSingleToken(ctx.variableDeclaratorId().start, new_parameter_name)
            self.replace_parameter_in_method_body(ctx, parameter_name, new_parameter_name)
        return self.visitChildren(ctx)

    def visitMethodCall(self, ctx: JavaParser.MethodCallContext):
            method_name = ctx.identifier().getText()
            self.function_calls.append(method_name)
            return self.visitChildren(ctx)
    
    def replaceUsage(self, old_name, new_name):
        for token in self.rewriter.getTokenStream().tokens:
            if token.text == old_name:
                self.rewriter.replaceSingleToken(token, new_name)

    def replace_parameter_in_method_body(self, ctx, old_name, new_name):
        method_body = self.getMethodBody(ctx)
        if method_body:
            for token in self.rewriter.getTokenStream().tokens:
                if (token.text == old_name and
                        method_body.start.tokenIndex <= token.tokenIndex <= method_body.stop.tokenIndex):
                    self.rewriter.replaceSingleToken(token, new_name)

    def getMethodBody(self, ctx):
        parent = ctx.parentCtx
        while parent:
            if isinstance(parent, JavaParser.MethodDeclarationContext):
                return parent.methodBody()
            parent = parent.parentCtx
        return None

    def convertToPascalCase(self, text):
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
        text = re.sub(r"[ _-]+", " ", text).strip()
        return "".join(word.capitalize() for word in text.split())

    def convertToCamelCase(self, text):
        pascal_case = self.convertToPascalCase(text)
        return pascal_case[0].lower() + pascal_case[1:] if pascal_case else ""

    def convertToConstantCase(self, name):
        return re.sub(r'([a-z])([A-Z])', r'\1_\2', name).upper()
# Example usage:
# config = ConfigClass(".java-format.json")
# visitor = NameConventionFormatterVisitor(tokens, config)
# visitor.visit(tree)
