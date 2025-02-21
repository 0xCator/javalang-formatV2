from antlr4.TokenStreamRewriter import TokenStreamRewriter
from JavaParserVisitor import JavaParserVisitor
from JavaParser import JavaParser
from PatternTransformer import RegexAnalyzer, RegexRewriter
import re
from ConfigClass import ConfigClass
from StandardNamingConventions import StandardNamingConventions

class NameConventionFormatterVisitor(JavaParserVisitor):
    def __init__(self, tokens, config : ConfigClass):
        self.rewriter = TokenStreamRewriter(tokens)
        self.config = config
        self.function_calls = []
        self.regex_analyzer = RegexAnalyzer()
        self.regex_rewriter = RegexRewriter()
        self.imports = {
            'items': [],
            'start_index': -1,
            'end_index': -1
        }
        self.token_stream = tokens

    def visitImportDeclaration(self, ctx: JavaParser.ImportDeclarationContext):
            # Skip processing import statements
            return None  
    def visitClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
        class_name = ctx.identifier().getText()
        class_config = self.config.naming_conventions['class']
        class_pattern = self.check_convention(class_config)
        parsed_components = self.regex_analyzer.analyze(class_pattern)

        if not self._matches(class_name, parsed_components):
            new_class_name = self.regex_rewriter.rewrite(class_name, class_pattern)
            self.rewriter.replaceSingleToken(ctx.identifier().start, new_class_name)
            self.replaceUsage(class_name, new_class_name)

        return self.visitChildren(ctx)

    def visitCreator(self, ctx: JavaParser.CreatorContext):
        class_name = ctx.createdName().getText()
        class_config = self.config.naming_conventions['class']
        class_pattern = self.check_convention(class_config)
        parsed_components = self.regex_analyzer.analyze(class_pattern)

        if not self._matches(class_name, parsed_components):
            new_class_name = self.regex_rewriter.rewrite(class_name, class_pattern)
            self.rewriter.replaceSingleToken(ctx.createdName().start, new_class_name)
            self.replaceUsage(class_name, new_class_name)

        return self.visitChildren(ctx)

    def visitQualifiedName(self, ctx: JavaParser.QualifiedNameContext):
        identifiers = ctx.identifier()
        class_config = self.config.naming_conventions['class']
        class_pattern = self.check_convention(class_config)
        parsed_components = self.regex_analyzer.analyze(class_pattern)

        for identifier in identifiers:
            name = identifier.getText()

            if not self._matches(name, parsed_components):
                new_name = self.regex_rewriter.rewrite(name, class_pattern)
                self.rewriter.replaceSingleToken(identifier.start, new_name)
                self.replaceUsage(name, new_name)

        return self.visitChildren(ctx)

    def visitTypeType(self, ctx: JavaParser.TypeTypeContext):
        if ctx.classOrInterfaceType():
            type_name = ctx.classOrInterfaceType().getText()
            class_config = self.config.naming_conventions['class']
            class_pattern = self.check_convention(class_config)
            parsed_components = self.regex_analyzer.analyze(class_pattern)

            if not self._matches(type_name, parsed_components):
                new_type_name = self.regex_rewriter.rewrite(type_name, class_pattern)
                self.rewriter.replaceSingleToken(ctx.classOrInterfaceType().start, new_type_name)
                self.replaceUsage(type_name, new_type_name)

        return self.visitChildren(ctx)

    def visitExpression(self, ctx: JavaParser.ExpressionContext):
        if ctx.primary() and ctx.primary().identifier():
            static_call = ctx.primary().identifier().getText()
            class_config = self.config.naming_conventions['class']
            class_pattern = self.check_convention(class_config)
            parsed_components = self.regex_analyzer.analyze(class_pattern)

            if not self._matches(static_call, parsed_components):
                new_static_call = self.regex_rewriter.rewrite(static_call, class_pattern)
                self.rewriter.replaceSingleToken(ctx.primary().identifier().start, new_static_call)
                self.replaceUsage(static_call, new_static_call)

        return self.visitChildren(ctx)

    def visitAnnotation(self, ctx: JavaParser.AnnotationContext):
        annotation_name = ctx.qualifiedName().getText()
        class_config = self.config.naming_conventions['class']
        class_pattern = self.check_convention(class_config)
        parsed_components = self.regex_analyzer.analyze(class_pattern)

        if not self._matches(annotation_name, parsed_components):
            new_annotation_name = self.regex_rewriter.rewrite(annotation_name, class_pattern)
            self.rewriter.replaceSingleToken(ctx.qualifiedName().start, new_annotation_name)
            self.replaceUsage(annotation_name, new_annotation_name)

        return self.visitChildren(ctx)

    def visitMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
        method_name = ctx.identifier().getText()
        method_config = self.config.naming_conventions['method']
        method_pattern = self.check_convention(method_config)
        parsed_components = self.regex_analyzer.analyze(method_pattern)
        self.function_calls.append(f"Declared: {method_name}")

        if not self._matches(method_name, parsed_components):
            new_method_name = self.regex_rewriter.rewrite(method_name, method_pattern)
            self.function_calls.append(new_method_name)
            self.rewriter.replaceSingleToken(ctx.identifier().start, new_method_name)
            self.replaceUsage(method_name, new_method_name)

        return self.visitChildren(ctx)

    def visitFieldDeclaration(self, ctx: JavaParser.FieldDeclarationContext):
        declarators = ctx.variableDeclarators()
        modifiers = [mod.getText() for mod in ctx.parentCtx.parentCtx.modifier()]
        is_static = "static" in modifiers
        is_final = "final" in modifiers


        variable_config = self.config.naming_conventions['variable']
        variable_pattern = self.check_convention(variable_config)
        constant_config = self.config.naming_conventions['constant']
        constant_pattern = self.check_convention(constant_config)
        variable_components = self.regex_analyzer.analyze(variable_pattern)
        constant_components = self.regex_analyzer.analyze(constant_pattern)

        for declarator in declarators.variableDeclarator():
            field_name = declarator.variableDeclaratorId().getText()

            if is_static and is_final:
                if not self._matches(field_name, constant_components):
                    new_field_name = self.regex_rewriter.rewrite(field_name, constant_pattern)
                    self.rewriter.replaceSingleToken(declarator.variableDeclaratorId().start, new_field_name)
                    self.replaceUsage(field_name, new_field_name)
            else:
                if not self._matches(field_name, variable_components):
                    new_field_name = self.regex_rewriter.rewrite(field_name, variable_pattern)
                    self.rewriter.replaceSingleToken(declarator.variableDeclaratorId().start, new_field_name)
                    self.replaceUsage(field_name, new_field_name)

        return self.visitChildren(ctx)

    def visitLocalVariableDeclaration(self, ctx: JavaParser.LocalVariableDeclarationContext):
        declarators = ctx.variableDeclarators()
        variable_config = self.config.naming_conventions['variable']
        variable_pattern = self.check_convention(variable_config)
        parsed_components = self.regex_analyzer.analyze(variable_pattern)

        for declarator in declarators.variableDeclarator():
            variable_name = declarator.variableDeclaratorId().getText()

            if not self._matches(variable_name, parsed_components):
                new_variable_name = self.regex_rewriter.rewrite(variable_name, variable_pattern)
                self.rewriter.replaceSingleToken(declarator.variableDeclaratorId().start, new_variable_name)
                self.replaceUsage(variable_name, new_variable_name)

        return self.visitChildren(ctx)

    def visitVariableDeclarator(self, ctx: JavaParser.VariableDeclaratorContext):
        variable_name = ctx.variableDeclaratorId().getText()
        variable_config = self.config.naming_conventions['variable']
        variable_pattern = self.check_convention(variable_config)
        parsed_components = self.regex_analyzer.analyze(variable_pattern)

        if not self._matches(variable_name, parsed_components):
            new_variable_name = self.regex_rewriter.rewrite(variable_name, variable_pattern)
            self.rewriter.replaceSingleToken(ctx.variableDeclaratorId().start, new_variable_name)
            self.replaceUsage(variable_name, new_variable_name)

        return self.visitChildren(ctx)

    def visitFormalParameter(self, ctx: JavaParser.FormalParameterContext):
        parameter_name = ctx.variableDeclaratorId().getText()
        parameter_config = self.config.naming_conventions['parameter']
        parameter_pattern = self.check_convention(parameter_config)
        parsed_components = self.regex_analyzer.analyze(parameter_pattern)

        if not self._matches(parameter_name, parsed_components):
            new_parameter_name = self.regex_rewriter.rewrite(parameter_name, parameter_pattern)
            self.rewriter.replaceSingleToken(ctx.variableDeclaratorId().start, new_parameter_name)
            self.replaceParameterInMethodBody(ctx, parameter_name, new_parameter_name)

        return self.visitChildren(ctx)

    def visitMethodCall(self, ctx: JavaParser.MethodCallContext):
        method_name = ctx.identifier().getText()
        method_config = self.config.naming_conventions['method']
        method_pattern = self.check_convention(method_config)
        parsed_components = self.regex_analyzer.analyze(method_pattern)

        if not self._matches(method_name, parsed_components):
            new_method_name = self.regex_rewriter.rewrite(method_name, method_pattern)
            self.rewriter.replaceSingleToken(ctx.identifier().start, new_method_name)
            self.replaceUsage(method_name, new_method_name)

        self.function_calls.append(method_name)
        return self.visitChildren(ctx)

    def _matches(self, input_string, components):
        try:
            transformed_string, _ = self.regex_rewriter._process_components(input_string, components, self.regex_rewriter.max_insertions)
            print(transformed_string, input_string)
            return transformed_string == input_string
        except Exception as e:
            print(f"Matching error: {e}")
            return False

    def replaceUsage(self, old_name, new_name):
        for token in self.token_stream.tokens:
            if token.text == old_name:
                self.rewriter.replaceSingleToken(token, new_name)
    
    def replaceParameterInMethodBody(self, ctx, old_name, new_name):
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
    @staticmethod
    def check_convention(convention) -> bool:
        patterns = {
            StandardNamingConventions.PASCAL_CASE.value: r"[A-Z][a-zA-Z0-9]*",
            StandardNamingConventions.CAMEL_CASE.value: r"[a-z][a-zA-Z0-9]*",
            StandardNamingConventions.UPPER_CASE.value: r"[A-Z][A-Z0-9_]*"
        }

        return patterns.get(convention, convention)
    def _order_imports(self):
        if self.imports['items']:
            self.rewriter.replaceRange(self.imports['start_index'], self.imports['end_index'], "\n".join(sorted(self.imports['items'])))
        
        # Used to help with the lack of a newline in the last import
        if self.config.imports['merge'] == True:
            self.rewriter.insertBeforeIndex(self.imports['end_index']+1, "\n")
    def get_formatted_code(self, tree):
        self.imports = {
            'items': [],
            'start_index': -1,
            'end_index': -1
        }

        self.visit(tree)

        if self.config.imports['order'] == "sort":
            self._order_imports()

        return self.rewriter.getDefaultText()