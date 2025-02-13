from JavaParser import JavaParser
from JavaParserVisitor import JavaParserVisitor
from antlr4.TokenStreamRewriter import TokenStreamRewriter

class FormattingVisitor(JavaParserVisitor):
    def __init__(self, tokens, config):
        self.rewriter : TokenStreamRewriter = TokenStreamRewriter(tokens)
        self.config = config
        self.indent_level: int = 0
    
    def visitClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
        class_name = ctx.identifier().getText()
        modifiers = []
        parent = ctx.parentCtx

        if isinstance(parent, JavaParser.TypeDeclarationContext):
            if parent.classOrInterfaceModifier():
                modifiers = [mod.getText() for mod in parent.classOrInterfaceModifier()]
                modifiers = self._sort_modifiers(modifiers, self.config.get("class_modifier_order", []))
        
        class_signature = f"{' '.join(modifiers)} class {class_name}".strip()
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
        return_type = ctx.typeTypeOrVoid().getText()
        method_name = ctx.identifier().getText()
        modifiers = []
        parent = ctx.parentCtx  
        grandparent: JavaParser.StatementContext = None
        if isinstance(parent, JavaParser.MemberDeclarationContext):  
            grandparent = parent.parentCtx  
            if isinstance(grandparent, JavaParser.ClassBodyDeclarationContext):
                if grandparent.modifier():
                    modifiers = [mod.getText() for mod in grandparent.modifier()]
                    modifiers = self._sort_modifiers(modifiers, self.config.get("method_modifier_order", []))

        method_signature = f"{' '.join(modifiers)} {return_type} {method_name}".strip()

        self.rewriter.replaceRangeTokens(grandparent.start, ctx.identifier().stop, "\n" + self._get_indent() + method_signature)


        method_body = ctx.methodBody()
        if method_body and method_body.block():
            block = method_body.block()
            open_brace = block.LBRACE().getSymbol()
            close_brace = block.RBRACE().getSymbol()

            self._remove_whitespace(open_brace.tokenIndex - 1)

            if self.config.get("brace_style", "attach") == "attach":
                self.rewriter.replaceSingleToken(open_brace, " {")
            else:
                self.rewriter.replaceSingleToken(open_brace, "\n" + self._get_indent() + "{")

            self.rewriter.replaceSingleToken(close_brace, "\n" + self._get_indent() + "}")

        return self.visitChildren(ctx)
    
    def visitStatement(self, ctx: JavaParser.StatementContext):
        self.indent_level += 1
        open_brace = ctx.LBRACE().getSymbol() if ctx.LBRACE() else None
        close_brace = ctx.RBRACE().getSymbol() if ctx.RBRACE() else None
        if open_brace:
            if self.config.get("brace_style", "attach") == "attach":
                self.rewriter.replaceSingleToken(open_brace, " {")
            else:
                self.rewriter.replaceSingleToken(open_brace, "\n" + self._get_indent() + "{")
            self.indent_level += 1
            self.rewriter.replaceSingleToken(close_brace, "\n" + self._get_indent() + "}")
            self.indent_level -= 1


        if ctx.SWITCH():
            switch_expr = ctx.parExpression().getText()
            switch_block = ctx.switchBlockStatementGroup()
            self.rewriter.replaceRangeTokens(ctx.SWITCH().getSymbol(), ctx.parExpression().stop, f"switch {switch_expr}")
            self.visitSwitchBlockStatementGroup(switch_block)


        statements: list[JavaParser.StatementContext] = ctx.statement()
        for statement in statements:
            if statement.block():
                block = statement.block()
                self.visitBlock(block)

        self.indent_level -= 1


    def visitSwitchBlockStatementGroup(self, ctx: JavaParser.SwitchBlockStatementGroupContext):
        self.indent_level += 1
        for block in list(ctx):
            self.visitSwitchLabel(block.switchLabel())

            for s in block.blockStatement():
                self.visitBlockStatement(s)

        self.indent_level -= 1

    def visitSwitchLabel(self, ctx: JavaParser.SwitchLabelContext):
        for label in list(ctx):
            if label.CASE():
                self.rewriter.replaceSingleToken(label.CASE().getSymbol(), "\n" + self._get_indent() + f"case")
            elif label.DEFAULT():
                self.rewriter.replaceSingleToken(label.DEFAULT().getSymbol(), "\n" + self._get_indent() + "default")
            self.rewriter.insertAfterToken(label.COLON().getSymbol(), "\n")

    def visitBlockStatement(self, ctx: JavaParser.BlockStatementContext):
        return self.visitChildren(ctx)

    def visitBlock(self, ctx: JavaParser.BlockContext):
        self.indent_level += 1
        open_brace = ctx.LBRACE().getSymbol()
        close_brace = ctx.RBRACE().getSymbol()
        self._remove_whitespace(open_brace.tokenIndex -1)
        if self.config.get("brace_style", "attach") == "attach":
            self.rewriter.replaceSingleToken(open_brace, " {")
        else:
            self.rewriter.replaceSingleToken(open_brace, "\n" + self._get_indent() + "{")
        self.rewriter.replaceSingleToken(close_brace, "\n" + self._get_indent() + "}")
        
        for statement in ctx.blockStatement():
            statement_start = statement.start
            self.rewriter.insertBeforeToken(statement_start, "\n" + self._get_indent())

        self.indent_level -= 1
        return self.visitChildren(ctx)

    
    def _remove_whitespace(self, pos):
        token = self.rewriter.getTokenStream().get(pos)
        if token.text.isspace():
            self.rewriter.deleteToken(token)

    def _sort_modifiers(self, modifiers, order):
        return sorted(modifiers, key=lambda x: order.index(x) if x in order else len(order))
    
    def _get_indent(self):
        return " " * (self.indent_level * self.config.get("indent_size", 4))
    
    def get_formatted_code(self, tree):
        self.visit(tree)
        return self.rewriter.getDefaultText()
