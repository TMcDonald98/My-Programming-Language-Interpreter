import mypl_error as error
import mypl_lexer as lexer
import mypl_token as token
import mypl_ast as ast

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None

    def parse(self):
        """succeeds if program is syntactically well-formed"""
        stmt_list_node = ast.StmtList()
        self.__advance()
        self.__stmts(stmt_list_node)
        self.__eat(token.EOS, 'expecting end of file')
        return stmt_list_node

    def __advance(self):
        self.current_token = self.lexer.next_token()
        #print(self.current_token)

    def __eat(self, tokentype, error_msg):
        if self.current_token.tokentype == tokentype:
            self.__advance()
        else:
            self.__error(error_msg)

    def __error(self, error_msg):
        s = error_msg + ', found "' + self.current_token.lexeme + '" in parser'
        l = self.current_token.line
        c = self.current_token.column
        raise error.MyPLError(error_msg, l, c)

    # Beginning of recursive descent functions
    def __stmts(self, stmt_list_node):
        """<stmts> ::= <stmt> <stmts>  or  e"""
        if self.current_token.tokentype != token.EOS:      
            self.__stmt(stmt_list_node)
            self.__stmts(stmt_list_node)
        
    def __bstmts(self):
        """returns a list of bstmts"""
        bstmts_node = ast.StmtList()
        while self.current_token.tokentype == token.VAR or \
        self.current_token.tokentype == token.SET or \
        self.current_token.tokentype == token.IF or \
        self.current_token.tokentype == token.WHILE or \
        self.current_token.tokentype == token.RETURN or \
        self.current_token.tokentype == token.INTVAL or \
        self.current_token.tokentype == token.BOOLVAL or \
        self.current_token.tokentype == token.FLOATVAL or \
        self.current_token.tokentype == token.NIL or \
        self.current_token.tokentype == token.NEW or \
        self.current_token.tokentype == token.LPAREN or \
        self.current_token.tokentype == token.ID:
            bstmts_node.stmts.append(self.__bstmt())
        return bstmts_node

    def __stmt(self, stmt_list_node):
        """<stmt> ::= <sdecl>  or  <fdecl>  or <bstmt>"""
        if self.current_token.tokentype == token.STRUCTTYPE:
            self.__sdecl(stmt_list_node)
        elif self.current_token.tokentype == token.FUN:
            self.__fdecl(stmt_list_node)
        elif self.current_token.tokentype == token.VAR or \
        self.current_token.tokentype == token.SET or \
        self.current_token.tokentype == token.IF or \
        self.current_token.tokentype == token.WHILE or \
        self.current_token.tokentype == token.RETURN or \
        self.current_token.tokentype == token.STRINGVAL or \
        self.current_token.tokentype == token.INTVAL or \
        self.current_token.tokentype == token.BOOLVAL or \
        self.current_token.tokentype == token.FLOATVAL or \
        self.current_token.tokentype == token.NIL or \
        self.current_token.tokentype == token.NEW or \
        self.current_token.tokentype == token.LPAREN or \
        self.current_token.tokentype == token.ID:
            stmt_list_node.stmts.append(self.__bstmt())

    def __bstmt(self):
        """return a statement"""
        if self.current_token.tokentype == token.VAR:
            return self.__vdecl()
        elif self.current_token.tokentype == token.SET:
            return self.__assign()
        elif self.current_token.tokentype == token.IF:
            return self.__cond()
        elif self.current_token.tokentype == token.WHILE:
            return self.__while()
        elif self.current_token.tokentype == token.RETURN:
            return self.__exit()
        elif self.current_token.tokentype == token.STRINGVAL or \
        self.current_token.tokentype == token.INTVAL or \
        self.current_token.tokentype == token.BOOLVAL or \
        self.current_token.tokentype == token.FLOATVAL or \
        self.current_token.tokentype == token.NIL or \
        self.current_token.tokentype == token.NEW or \
        self.current_token.tokentype == token.LPAREN or \
        self.current_token.tokentype == token.ID:
            expr_node = ast.ExprStmt()
            expr_node.expr = self.__expr()
            self.__eat(token.SEMICOLON, "Invalid Syntax: expected SEMICOLON")
            return expr_node
        else:
            self.__error("Invalid Syntax: <bstmt>")

    def __sdecl(self, stmt_list_node):
        sdecl_node = ast.StructDeclStmt()
        self.__eat(token.STRUCTTYPE, "Invalid Syntax: expected STRUCT")
        sdecl_node.struct_id = self.current_token
        self.__eat(token.ID, "Invalid Syntax: expected ID")
        self.__vdecls(sdecl_node)
        self.__eat(token.END, "Invalid Syntax: expected END")
        stmt_list_node.stmts.append(sdecl_node)
   
    def __vdecls(self, sdecl_node):
        if self.current_token.tokentype == token.VAR:
            sdecl_node.var_decls.append(self.__vdecl())
            self.__vdecls(sdecl_node)

    def __fdecl(self, stmt_list_node):
        fdecl_node = ast.FunDeclStmt() 
        self.__eat(token.FUN, "Invalid Syntax: expected FUN")
        if self.current_token.tokentype == token.NIL:
            fdecl_node.return_type = self.current_token
            self.__advance()
        else:
            fdecl_node.return_type = self.__type()
        fdecl_node.fun_name = self.current_token
        self.__eat(token.ID, "Invalid Syntax: expected ID")
        self.__eat(token.LPAREN, "Invalid Syntax: expected LPAREN")
        fdecl_node.params = self.__params()
        self.__eat(token.RPAREN, "Invalid Syntax: expected RPAREN")
        fdecl_node.stmt_list = self.__bstmts()
        self.__eat(token.END, "Invalid Syntax: expected END")
        stmt_list_node.stmts.append(fdecl_node)
        
    def __params(self):
        params_list = []
        if self.current_token.tokentype == token.ID:
            curr = ast.FunParam()
            curr.param_name = self.current_token
            self.__advance()
            self.__eat(token.COLON, "Invalid Syntax: expected COLON")
            curr.param_type = self.__type()
            params_list.append(curr)
            while(self.current_token.tokentype == token.COMMA):
                curr = ast.FunParam()
                self.__advance()
                curr.param_name = self.current_token
                self.__eat(token.ID, "Invalid Syntax: expected ID")
                self.__eat(token.COLON, "Invalid Syntax: expected COLON")
                curr.param_type = self.__type()
                params_list.append(curr)
        return params_list
            
    def __type(self):
        theType = self.current_token
        if self.current_token.tokentype == token.ID or \
        self.current_token.tokentype == token.STRINGVAL or \
        self.current_token.tokentype == token.INTTYPE or \
        self.current_token.tokentype == token.FLOATTYPE or \
        self.current_token.tokentype == token.BOOLTYPE or \
        self.current_token.tokentype == token.STRINGTYPE:
            self.__advance()
        else:
            self.__error("Invalid Syntax: <type>")
        return theType

    def __exit(self):
        exit_node = ast.ReturnStmt()
        exit_node.return_token = self.current_token
        self.__eat(token.RETURN, "Invalid Syntax: expected RETURN")
        if self.current_token.tokentype == token.STRINGVAL or \
        self.current_token.tokentype == token.INTVAL or \
        self.current_token.tokentype == token.BOOLVAL or \
        self.current_token.tokentype == token.FLOATVAL or \
        self.current_token.tokentype == token.NIL or \
        self.current_token.tokentype == token.NEW or \
        self.current_token.tokentype == token.LPAREN or \
        self.current_token.tokentype == token.ID:
            exit_node.return_expr = self.__expr()
        self.__eat(token.SEMICOLON, "Invalid Syntax: expected SEMICOLON")
        return exit_node

    def __vdecl(self):
        vdecl_node = ast.VarDeclStmt()
        self.__eat(token.VAR, "Invalid Syntax: expected VAR")
        vdecl_node.var_id = self.current_token
        self.__eat(token.ID, "Invalid Syntax: expected ID")
        self.__tdecl(vdecl_node)
        self.__eat(token.ASSIGN, "Invalid Syntax: expected ASSIGN")
        vdecl_node.var_expr = self.__expr()
        self.__eat(token.SEMICOLON, "Invalid Syntax: expected SEMICOLON")
        return vdecl_node

    def __tdecl(self, vdecl_node):
        if self.current_token.tokentype == token.COLON:
            self.__advance()
            vdecl_node.var_type = self.__type()

    def __assign(self):
        assign_node = ast.AssignStmt()
        self.__eat(token.SET, "Invalid Syntax: expected SET")
        assign_node.lhs = self.__lvalue()
        self.__eat(token.ASSIGN, "Invalid Syntax: expected ASSIGN")
        assign_node.rhs = self.__expr()
        self.__eat(token.SEMICOLON, "Invalid Syntax: expected SEMICOLON")
        return assign_node

    def __lvalue(self):
        val = ast.LValue()
        val.path.append(self.current_token)
        self.__eat(token.ID, "Invalid Syntax: expected ID")
        while(self.current_token.tokentype == token.DOT):
            self.__advance()
            val.path.append(self.current_token)
            self.__eat(token.ID, "Invalid Syntax: expected ID")
        return val

    def __cond(self):
        cond_node = ast.BasicIf()
        if_state_node = ast.IfStmt()
        self.__eat(token.IF, "Invalid Syntax: expected IF")
        cond_node.bool_expr = self.__bexpr()
        self.__eat(token.THEN, "Invalid Syntax: expected THEN")
        cond_node.stmt_list = self.__bstmts()
        if_state_node.if_part = cond_node
        if self.current_token.tokentype == token.ELIF or \
        self.current_token.tokentype == token.ELSE:          
            self.__condt(if_state_node)
        self.__eat(token.END, "Invalid Syntax: expected END")
        return if_state_node

    def __condt(self, if_state_node):
        if self.current_token.tokentype == token.ELIF:
            self.__advance()
            new_elif = ast.BasicIf()
            new_elif.bool_expr = self.__bexpr()
            self.__eat(token.THEN, "Invalid Syntax: expected THEN")
            new_elif.stmt_list = self.__bstmts()
            if_state_node.elseifs.append(new_elif)
            self.__condt(if_state_node)
        elif self.current_token.tokentype == token.ELSE:
            if_state_node.has_else = True
            self.__advance()
            if_state_node.else_stmts = self.__bstmts()
        
    def __while(self):
        while_node = ast.WhileStmt()
        self.__eat(token.WHILE, "Invalid Syntax: expected WHILE")
        while_node.bool_expr = self.__bexpr()
        self.__eat(token.DO, "Invalid Syntax: expected DO")
        while_node.stmt_list = self.__bstmts()
        self.__eat(token.END, "Invalid Syntax: expected END")
        return while_node

    def __expr(self):
        expr_node = ast.SimpleExpr()
        complx_expr_node = ast.ComplexExpr()
        if self.current_token.tokentype == token.LPAREN:
            self.__advance()#what to do with (expr) "(" ")"
            expr_node = self.__expr()
            self.__eat(token.RPAREN, "Invalid Syntax: expected RPAREN")
        elif self.current_token.tokentype == token.STRINGVAL or \
        self.current_token.tokentype == token.INTVAL or \
        self.current_token.tokentype == token.BOOLVAL or \
        self.current_token.tokentype == token.FLOATVAL or \
        self.current_token.tokentype == token.NIL or \
        self.current_token.tokentype == token.NEW or \
        self.current_token.tokentype == token.ID:
            expr_node = self.__rvalue()
        else:
            self.__error("Invalid Syntax: <expr>")
        if self.current_token.tokentype == token.PLUS or \
        self.current_token.tokentype == token.MINUS or \
        self.current_token.tokentype == token.DIVIDE or \
        self.current_token.tokentype == token.MULTIPLY or \
        self.current_token.tokentype == token.MODULO:
            complx_expr_node.first_operand = expr_node
            complx_expr_node.math_rel = self.current_token
            self.__mathrel()
            complx_expr_node.rest = self.__expr()
            return complx_expr_node
        return expr_node

    def __mathrel(self):
        if self.current_token.tokentype == token.PLUS or \
        self.current_token.tokentype == token.MINUS or \
        self.current_token.tokentype == token.DIVIDE or \
        self.current_token.tokentype == token.MULTIPLY or \
        self.current_token.tokentype == token.MODULO:
            self.__advance()

    def __rvalue(self):
        """Returns a simple EXPR statement"""
        simple_expr_node = ast.SimpleExpr()
        if self.current_token.tokentype == token.STRINGVAL or \
        self.current_token.tokentype == token.INTVAL or \
        self.current_token.tokentype == token.BOOLVAL or \
        self.current_token.tokentype == token.FLOATVAL or \
        self.current_token.tokentype == token.NIL:
            a = ast.SimpleRValue()
            a.val = self.current_token
            self.__advance()
            simple_expr_node.term = a
            return simple_expr_node
        elif self.current_token.tokentype == token.NEW:
            self.__advance()
            a = ast.NewRValue()
            a.struct_type = self.current_token
            simple_expr_node.term = a
            self.__eat(token.ID, "Invalid Syntax: expected ID")
            return simple_expr_node
        elif self.current_token.tokentype == token.ID:
            return self.__idrval()
        else:
            self.__error("Invalid Syntax: <rvalue>")
        
    def __idrval(self):
        """returns a rvalue of relevant type"""
        initial_id = self.current_token
        self.__eat(token.ID, "Invalid Syntax: expected ID")
        if self.current_token.tokentype == token.DOT:
            a = ast.IDRvalue()
            a.path.append(initial_id)
            while(self.current_token.tokentype == token.DOT):
                self.__advance()
                a.path.append(self.current_token)
                self.__eat(token.ID, "Invalid Syntax: expected ID")
            return a
        elif self.current_token.tokentype == token.LPAREN:
            self.__advance()
            a = self.__exprlist()
            a.fun = initial_id
            self.__eat(token.RPAREN, "Invalid Syntax: expected RPAREN")
            return a
        else:
            a = ast.IDRvalue()
            a.path.append(initial_id)
            return a
        #return None

    def __exprlist(self):
        """returns CALLRValue for function call"""
        a = ast.CallRValue()
        if self.current_token.tokentype == token.STRINGVAL or \
        self.current_token.tokentype == token.INTVAL or \
        self.current_token.tokentype == token.BOOLVAL or \
        self.current_token.tokentype == token.FLOATVAL or \
        self.current_token.tokentype == token.NIL or \
        self.current_token.tokentype == token.NEW or \
        self.current_token.tokentype == token.LPAREN or \
        self.current_token.tokentype == token.ID:
            a.args.append(self.__expr())
            while(self.current_token.tokentype == token.COMMA):
                self.__advance()
                a.args.append(self.__expr())
        return a

    def __bexpr(self):
        bexpr_node = ast.BoolExpr()
        if self.current_token.tokentype == token.LPAREN:
            self.__advance()
            bexpr_node = self.__bexpr()#look at this and expr similar
            self.__eat(token.RPAREN, "Invalid Syntax: expected RPAREN")
            self.__bconnct(bexpr_node)
            return bexpr_node
        elif self.current_token.tokentype == token.STRINGVAL or \
        self.current_token.tokentype == token.INTVAL or \
        self.current_token.tokentype == token.BOOLVAL or \
        self.current_token.tokentype == token.FLOATVAL or \
        self.current_token.tokentype == token.NIL or \
        self.current_token.tokentype == token.NEW or \
        self.current_token.tokentype == token.ID:
            bexpr_node.first_expr = self.__expr()
            self.__bexprt(bexpr_node)
            return bexpr_node
        elif self.current_token.tokentype == token.NOT:
            self.__advance()
            bexpr_node = self.__bexpr()
            bexpr_node.negated = True #look at this
            self.__bexprt(bexpr_node)
            return bexpr_node
        else:
            self.__error("Invalid Syntax: <bexpr>")

    def __bexprt(self, bexpr_node):
        if self.current_token.tokentype == token.EQUAL or \
        self.current_token.tokentype == token.LESS_THAN or \
        self.current_token.tokentype == token.GREATER_THAN or \
        self.current_token.tokentype == token.LESS_THAN_EQUAL or \
        self.current_token.tokentype == token.GREATER_THAN_EQUAL or \
        self.current_token.tokentype == token.NOT_EQUAL:
            bexpr_node.bool_rel = self.__boolrel()
            bexpr_node.second_expr = self.__expr()
            self.__bconnct(bexpr_node)
        elif self.current_token.tokentype == token.AND or \
        self.current_token.tokentype == token.OR:
            self.__bconnct(bexpr_node)

    def __bconnct(self, bexpr_node):
        if self.current_token.tokentype == token.AND or \
        self.current_token.tokentype == token.OR:
            bexpr_node.bool_connector = self.current_token
            self.__advance()
            bexpr_node.rest = self.__bexpr()

    def __boolrel(self):
        if self.current_token.tokentype == token.EQUAL or \
        self.current_token.tokentype == token.LESS_THAN or \
        self.current_token.tokentype == token.GREATER_THAN or \
        self.current_token.tokentype == token.LESS_THAN_EQUAL or \
        self.current_token.tokentype == token.GREATER_THAN_EQUAL or \
        self.current_token.tokentype == token.NOT_EQUAL:
            curr = self.current_token
            self.__advance()
            return curr
        else: 
            self.__error("Invalid Syntax: <boolrel>")
