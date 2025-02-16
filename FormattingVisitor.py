from antlr4.TokenStreamRewriter import TokenStreamRewriter
from JavaParserVisitor import JavaParserVisitor
from JavaParser import JavaParser
from functools import wraps
from ConfigClass import ConfigClass

class FormattingVisitor(JavaParserVisitor):
    def __init__(self, rewriter, config: ConfigClass):
        self.rewriter = rewriter
        self.config = config
        self.indent_level = 0

    def visitClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
        class_name = ctx.identifier().getText()
        modifiers = []
        parent = ctx.parentCtx

        if isinstance(parent, JavaParser.TypeDeclarationContext):
            if parent.classOrInterfaceModifier():
                modifiers = [mod.getText() for mod in parent.classOrInterfaceModifier()]
                modifiers = self._sort_modifiers(modifiers, self.config.class_modifier_order)
        
        class_signature = f"{' '.join(modifiers)} class {class_name}".strip()
        self.rewriter.replaceRangeTokens(parent.start, ctx.identifier().stop, class_signature)

        class_body = ctx.classBody()

        if class_body:
            open_brace = class_body.LBRACE().symbol
            close_brace = class_body.RBRACE().symbol

            self._remove_whitespace(open_brace.tokenIndex + 1)
            
            self._remove_whitespace(close_brace.tokenIndex - 1)

            if self.config.brace_style == "attach":
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
                    modifiers = self._sort_modifiers(modifiers, self.config.method_modifier_order)

        method_signature = f"{' '.join(modifiers)} {return_type} {method_name}".strip()

        self.rewriter.replaceRangeTokens(grandparent.start, ctx.identifier().stop, "\n" + self._get_indent() + method_signature)

        return self.visitChildren(ctx)
    
    def visitStatement(self, ctx: JavaParser.StatementContext):
        if ctx.SWITCH():
            close_paren = ctx.RBRACE().getSymbol()
            open_brace = ctx.LBRACE().getSymbol()
            if self.config.brace_style == "attach":
                self.rewriter.replaceSingleToken(open_brace, " {")
            else:
                self.rewriter.replaceSingleToken(open_brace, "\n" + self._get_indent() + "{")
            self.rewriter.insertBeforeToken(close_paren, "\n" + self._get_indent())
        return self.visitChildren(ctx)


    def handle_indentation(method):
        """Decorator to automatically increase and decrease indentation."""
        @wraps(method)
        def wrapper(self, ctx):
            self.indent_level += 1
            try:
                return method(self, ctx)
            finally:
                self.indent_level -= 1 
        return wrapper


    @handle_indentation
    def visitBlockStatement(self, ctx: JavaParser.BlockStatementContext):
        statement_start = ctx.start
        self.rewriter.insertBeforeToken(statement_start, "\n" + self._get_indent())
        return self.visitChildren(ctx)

    def visitSwitchLabel(self, ctx: JavaParser.SwitchLabelContext):
        lable_start = ctx.start
        self.rewriter.insertBeforeToken(lable_start, "\n" + self._get_indent())
        return super().visitSwitchLabel(ctx)

    @handle_indentation
    def visitSwitchBlockStatementGroup(self, ctx: JavaParser.SwitchBlockStatementGroupContext):
        return self.visitChildren(ctx)

    def visitBlock(self, ctx: JavaParser.BlockContext):
        open_brace = ctx.LBRACE().getSymbol()
        close_brace = ctx.RBRACE().getSymbol()
        parent = ctx.parentCtx 
        in_switch = False
        while parent:
            if isinstance(parent, JavaParser.SwitchBlockStatementGroupContext):
                in_switch = True
                break
            parent = parent.parentCtx  # Move up the tree


        if self.config.brace_style == "attach":
            self._remove_whitespace(open_brace.tokenIndex - 1) 
            if in_switch:
                self.rewriter.replaceSingleToken(open_brace, "{")
            else:
                self.rewriter.replaceSingleToken(open_brace, " {")
        else:
            self._remove_whitespace(open_brace.tokenIndex - 1) 
            if in_switch:
                self.rewriter.replaceSingleToken(open_brace, "{")
            self.rewriter.replaceSingleToken(open_brace, "\n" + self._get_indent() + "{")
        
        self.rewriter.replaceSingleToken(close_brace, "\n" + self._get_indent() + "}")
        return self.visitChildren(ctx)

    
    def _remove_whitespace(self, pos):
        while self.rewriter.getTokenStream().get(pos).type in [JavaParser.WS] or self.rewriter.getTokenStream().get(pos).text == "\n":
            self.rewriter.deleteToken(pos)
            pos -=1

    def _sort_modifiers(self, modifiers, order):
        return sorted(modifiers, key=lambda x: order.index(x) if x in order else len(order))
    
    def _get_indent(self):
        return " " * (self.indent_level * self.config.indent_size)
    
    def _debug_rewriter_operations(self):
        for program_name, rewrites in self.rewriter.programs.items():
            print(f"Program: {program_name}")
            for op in rewrites:
                try:
                    op_str = str(op)
                except TypeError:
                    op_str = repr(op)
                print(f"Operation: {op_str}")

    def get_formatted_code(self, tree):
        self.visit(tree)
        self._debug_rewriter_operations()  # Add this line to debug rewriter operations
        return self.rewriter.getDefaultText()
