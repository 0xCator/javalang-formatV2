from JavaParser import JavaParser
from JavaParserVisitor import JavaParserVisitor
from antlr4.TokenStreamRewriter import TokenStreamRewriter
from NameConventionHandler import NameConventionHandler

class FormattingVisitor(JavaParserVisitor):
    def __init__(self, tokens, config):
        self.rewriter = TokenStreamRewriter(tokens)
        self.config = config
        self.indent_level = 0
        self.allNeeded = []
        self.parameter_replacements = {}
        self.local_variable_replacements = {}

    def visitClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
        if ctx.identifier() is None:
            return self.visitChildren(ctx)

        class_name = ctx.identifier().getText()
        pascal_case = NameConventionHandler.to_pascal_case(class_name)
        self.allNeeded.append(pascal_case)

        modifiers = []
        parent = ctx.parentCtx

        if isinstance(parent, JavaParser.TypeDeclarationContext) and parent.classOrInterfaceModifier():
            modifiers = [mod.getText() for mod in parent.classOrInterfaceModifier()]
            modifiers = self._sort_modifiers(modifiers, self.config.get("class_modifier_order", []))

        class_signature = f"{' '.join(modifiers)} class {pascal_case}".strip()
        self.rewriter.replaceRangeTokens(parent.start, ctx.identifier().stop, class_signature)

        class_body = ctx.classBody()
        if class_body:
            open_brace = class_body.LBRACE().symbol
            close_brace = class_body.RBRACE().symbol

            self._remove_whitespace(open_brace.tokenIndex + 1)
            self._remove_whitespace(close_brace.tokenIndex - 1)

            if self.config.get("brace_style", "attach") == "attach":
                self.rewriter.replaceSingleToken(open_brace, " {")
            else:
                self.rewriter.replaceSingleToken(open_brace, "\n" + self._get_indent() + "{")

            self.rewriter.replaceSingleToken(close_brace, "\n" + self._get_indent() + "}")

            self.indent_level += 1

        return self.visitChildren(ctx)

    def visitMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
        if ctx.identifier() is None or ctx.typeTypeOrVoid() is None:
            return self.visitChildren(ctx)

        return_type = ctx.typeTypeOrVoid().getText()
        method_name = ctx.identifier().getText()
        camel_case = NameConventionHandler.to_camel_case(method_name)
        self.allNeeded.append(camel_case)

        modifiers = []
        parent = ctx.parentCtx
        if isinstance(parent, JavaParser.MemberDeclarationContext):
            grandparent = parent.parentCtx
            if isinstance(grandparent, JavaParser.ClassBodyDeclarationContext) and grandparent.modifier():
                modifiers = [mod.getText() for mod in grandparent.modifier()]
                modifiers = self._sort_modifiers(modifiers, self.config.get("method_modifier_order", []))

        method_signature = f"{' '.join(modifiers)} {return_type} {camel_case}".strip()
        self.rewriter.replaceRangeTokens(grandparent.start, ctx.identifier().stop, "\n" + self._get_indent() + method_signature)

        method_body = ctx.methodBody()
        if (method_body and method_body.block()):
            block = method_body.block()
            open_brace = block.LBRACE().symbol
            close_brace = block.RBRACE().symbol

            self._remove_whitespace(open_brace.tokenIndex - 1)

            if self.config.get("brace_style", "attach") == "attach":
                self.rewriter.replaceSingleToken(open_brace, " {")
            else:
                self.rewriter.replaceSingleToken(open_brace, "\n" + self._get_indent() + "{")

            self.rewriter.replaceSingleToken(close_brace, "\n" + self._get_indent() + "}")

        return self.visitChildren(ctx)

    def visitConstantDeclaration(self, ctx: JavaParser.ConstantDeclaratorContext):
        if ctx.identifier() is None:
            return self.visitChildren(ctx)

        constant_name = ctx.identifier().getText()
        full_case = NameConventionHandler.to_full_case(constant_name)
        self.allNeeded.append(full_case)
        self.rewriter.replaceRangeTokens(ctx.identifier().start, ctx.identifier().stop, full_case)

        return self.visitChildren(ctx)

    def visitFieldDeclaration(self, ctx: JavaParser.FieldDeclarationContext):
        if ctx.variableDeclarators():
            for variable in ctx.variableDeclarators().variableDeclarator():
                if variable.variableDeclaratorId():
                    var_name = variable.variableDeclaratorId().getText()
                    camel_case = NameConventionHandler.to_camel_case(var_name)
                    self.local_variable_replacements[var_name] = camel_case
                    self.rewriter.replaceRangeTokens(variable.variableDeclaratorId().start, variable.variableDeclaratorId().stop, camel_case)

        return self.visitChildren(ctx)

    def visitFormalParameter(self, ctx: JavaParser.FormalParameterContext):
        if ctx.variableDeclaratorId():
            param_name = ctx.variableDeclaratorId().getText()
            camel_case = NameConventionHandler.to_camel_case(param_name)
            self.parameter_replacements[param_name] = camel_case
            self.rewriter.replaceRangeTokens(ctx.variableDeclaratorId().start, ctx.variableDeclaratorId().stop, camel_case)

        return self.visitChildren(ctx)

    def visitLocalVariableDeclaration(self, ctx: JavaParser.LocalVariableDeclarationContext):
        if ctx.variableDeclarators():
            for variable in ctx.variableDeclarators().variableDeclarator():
                if variable.variableDeclaratorId():
                    var_name = variable.variableDeclaratorId().getText()
                    camel_case = NameConventionHandler.to_camel_case(var_name)
                    self.local_variable_replacements[var_name] = camel_case
                    self.rewriter.replaceRangeTokens(variable.variableDeclaratorId().start, variable.variableDeclaratorId().stop, camel_case)

        return self.visitChildren(ctx)

    def visitIdentifier(self, ctx: JavaParser.IdentifierContext):
        identifier_name = ctx.getText()
        if identifier_name in self.parameter_replacements:
            new_name = self.parameter_replacements[identifier_name]
            self.rewriter.replaceSingleToken(ctx.start, new_name)
        elif identifier_name in self.local_variable_replacements:
            new_name = self.local_variable_replacements[identifier_name]
            self.rewriter.replaceSingleToken(ctx.start, new_name)
        return self.visitChildren(ctx)

    def visitBlock(self, ctx: JavaParser.BlockContext):
        self.indent_level += 1
        if ctx.blockStatement():
            for statement in ctx.blockStatement():
                if statement.start:
                    self.rewriter.insertBeforeToken(statement.start, "\n" + self._get_indent())

        self.indent_level -= 1
        return self.visitChildren(ctx)

    def _remove_whitespace(self, pos):
        tokens = self.rewriter.getTokenStream()
        if 0 <= pos < len(tokens.tokens):
            token = tokens.get(pos)
            if token.text.isspace():
                self.rewriter.deleteToken(token)

    def _sort_modifiers(self, modifiers, order):
        return sorted(modifiers, key=lambda x: order.index(x) if x in order else len(order))

    def _get_indent(self):
        return " " * (self.indent_level * self.config.get("indent_size", 4))

    def get_formatted_code(self, tree):
        self.visit(tree)
        return self.rewriter.getDefaultText()

    def get_all_needed(self):
        return self.allNeeded
