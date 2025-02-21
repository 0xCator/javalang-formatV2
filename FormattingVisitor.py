from typing import Optional
from JavaParser import JavaParser
from JavaParserVisitor import JavaParserVisitor
from antlr4.TokenStreamRewriter import TokenStreamRewriter
from functools import wraps
from ConfigClass import ConfigClass

class FormattingVisitor(JavaParserVisitor):
    def __init__(self, tokens, config: ConfigClass):
        self.rewriter : TokenStreamRewriter = TokenStreamRewriter(tokens)
        self.config = config
        self.indent_level: int = 0
        self.imports = {
            'items': [],
            'start_index': -1,
            'end_index': -1
        }
    
    def visitImportDeclaration(self, ctx: JavaParser.ImportDeclarationContext):
        if self.config.imports["merge"] == True:
            if self.rewriter.getTokenStream().get(ctx.stop.tokenIndex+1).type in [JavaParser.WS]:
                self.rewriter.replaceIndex(ctx.stop.tokenIndex+1, "\n")
            else:
                self.rewriter.insertBeforeIndex(ctx.stop.tokenIndex+1, "\n")

        if self.config.imports['order'] == "sort":
            if self.imports['start_index'] == -1:
                self.imports['start_index'] = ctx.start.tokenIndex
            self.imports['end_index'] = ctx.stop.tokenIndex
            self.imports['items'].append(self._get_import_text(ctx.start.tokenIndex, ctx.stop.tokenIndex))

        return self.visitChildren(ctx)
    
    def _get_import_text(self, start, stop):
        text = []
        for i in range(start, stop+1):
            text.append(self.rewriter.getTokenStream().get(i).text)
        return text[0] + " " + "".join(text[1:]).strip()
    
    def _order_imports(self):
        if self.imports['items']:
            self.rewriter.replaceRange(self.imports['start_index'], self.imports['end_index'], "\n".join(sorted(self.imports['items'])))
        
        # Used to help with the lack of a newline in the last import
        if self.config.imports['merge'] == True:
            self.rewriter.insertBeforeIndex(self.imports['end_index']+1, "\n")

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
                self.rewriter.replaceSingleToken(open_brace, f"\n{self._get_indent()}"+"{")

            self.rewriter.replaceSingleToken(close_brace, f"\n{self._get_indent()}" + "}")

            self.indent_level += 1

        
        return self.visitChildren(ctx)
    
    def visitMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
        return_type = ctx.typeTypeOrVoid().getText()
        method_name = ctx.identifier().getText()
        modifiers = []
        parent = ctx.parentCtx  
        grandparent: Optional[JavaParser.StatementContext] = None
        if isinstance(parent, JavaParser.MemberDeclarationContext):  
            grandparent = parent.parentCtx  
            if isinstance(grandparent, JavaParser.ClassBodyDeclarationContext):
                if grandparent.modifier():
                    modifiers = [mod.getText() for mod in grandparent.modifier()]
                    modifiers = self._sort_modifiers(modifiers, self.config.method_modifier_order)

        method_signature = f"{' '.join(modifiers)} {return_type} {method_name}".strip()

        if grandparent: 
            self.rewriter.replaceRangeTokens(grandparent.start, ctx.identifier().stop, f"\n{self._get_indent()}{method_signature}")
        return self.visitChildren(ctx)
    
    def visitStatement(self, ctx: JavaParser.StatementContext):
        if ctx.SWITCH():
            close_paren = ctx.RBRACE().getSymbol()
            open_brace = ctx.LBRACE().getSymbol()
            if self.config.brace_style == "attach":
                self.rewriter.replaceSingleToken(open_brace, " {")
            else:
                self.rewriter.replaceSingleToken(open_brace, f"\n{self._get_indent()}" + "{")
            self.rewriter.insertBeforeToken(close_paren, f"\n{self._get_indent()}")
        return self.visitChildren(ctx)


    @staticmethod
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
        self.rewriter.insertBeforeToken(statement_start, f"\n{self._get_indent()}")
        return self.visitChildren(ctx)

    def visitSwitchLabel(self, ctx: JavaParser.SwitchLabelContext):
        lable_start = ctx.start
        self.rewriter.insertBeforeToken(lable_start, f"\n{self._get_indent()}")
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
            self.rewriter.replaceSingleToken(open_brace, f"\n{self._get_indent()}" + "{")
        
        self.rewriter.replaceSingleToken(close_brace, f"\n{self._get_indent()}" + "}")
        return self.visitChildren(ctx)

    
    def _remove_whitespace(self, pos):
        while self.rewriter.getTokenStream().get(pos).type in [JavaParser.WS] or self.rewriter.getTokenStream().get(pos).text == "\n":
            self.rewriter.deleteToken(pos)
            pos -=1

    def _sort_modifiers(self, modifiers, order):
        return sorted(modifiers, key=lambda x: order.index(x) if x in order else len(order))
    
    def _get_indent(self):
        match self.config.indentation_type:
            case "spaces":
                return " " * (self.indent_level * self.config.indent_size)
            case "tabs":
                return "\t" * self.indent_level
    
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
