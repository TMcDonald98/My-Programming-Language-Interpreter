##!/usr/bin/python3
#
# Author: Thomas McDonald
# Course: CPSC 326, Spring 2019
# Assignment: 5
# Description:
#   Implementation of typechecker for mypl
#----------------------------------------------------------------------
import mypl_token as token
import mypl_ast as ast
import mypl_error as error
import mypl_symbol_table as symbol_table

class TypeChecker(ast.Visitor):
    """A MyPL type checker visitor implementation where struct types
    take the form: type_id -> {v1:t1, ..., vn:tn} and function types
    take the form: fun_id -> [[t1, t2, ..., tn,], return_type]
    """
    
    def __init__(self):# initialize the symbol table (for ids -> types)
        self.sym_table = symbol_table.SymbolTable()
        # current_type holds the type of the last expression type
        self.current_type = None
        # global env (for return)
        self.sym_table.push_environment()
        # set global return type to int
        self.sym_table.add_id('return')
        self.sym_table.set_info('return', token.INTTYPE)
        # load in built-in function types
        self.sym_table.add_id('print')
        self.sym_table.set_info('print', [[token.STRINGTYPE], token.NIL]) 
        self.sym_table.add_id('length')
        self.sym_table.set_info('length', [[token.STRINGTYPE], token.INTTYPE])
        self.sym_table.add_id('reads')
        self.sym_table.set_info('reads', [[], token.STRINGVAL])
        self.sym_table.add_id('readi')
        self.sym_table.set_info('readi', [[], token.INTVAL])
        self.sym_table.add_id('readf')
        self.sym_table.set_info('readf', [[], token.FLOATVAL])
        self.sym_table.add_id('get')
        self.sym_table.set_info('get', [[token.INTVAL, token.STRINGVAL], token.STRINGVAL])
        self.sym_table.add_id('itos')
        self.sym_table.set_info('itos', [[token.INTVAL], token.STRINGVAL])
        self.sym_table.add_id('itof')
        self.sym_table.set_info('itof', [[token.INTVAL], token.FLOATVAL])
        self.sym_table.add_id('ftos')
        self.sym_table.set_info('ftos', [[token.FLOATVAL], token.STRINGVAL])
        self.sym_table.add_id('stoi')
        self.sym_table.set_info('stoi', [[token.STRINGVAL], token.INTVAL])
        self.sym_table.add_id('stof')
        self.sym_table.set_info('stof', [[token.STRINGVAL], token.FLOATVAL])

    def __error(self, msg, the_token):
        raise error.MyPLError(msg, the_token.line, the_token.column)

    def doTypesMatch(self, a_token_type):
        """matches vals with stypes using current type"""
        curr = self.current_type
        if(curr == a_token_type):
            return True
        if(a_token_type == token.STRINGTYPE and curr == token.STRINGVAL):
            return True
        if(a_token_type == token.INTTYPE and curr == token.INTVAL):
            return True
        if(a_token_type == token.BOOLTYPE and curr == token.BOOLVAL):
            return True
        if(a_token_type == token.FLOATTYPE and curr == token.FLOATVAL):
            return True
        if(curr == token.NIL):
            return True
        return False

    def visit_stmt_list(self, stmt_list):
        # add new block (scope)
        self.sym_table.push_environment()
        for stmt in stmt_list.stmts:
            stmt.accept(self)
        # remove new block
        self.sym_table.pop_environment()

    def visit_expr_stmt(self, expr_stmt):
        expr_stmt.expr.accept(self)

    def visit_var_decl_stmt(self, var_decl):
        self.sym_table.add_id(var_decl.var_id.lexeme)
        var_decl.var_expr.accept(self)
        if(var_decl.var_type != None):
            if(not self.doTypesMatch(var_decl.var_type.tokentype)):
                if(var_decl.var_type.tokentype is token.ID):
                    if(self.sym_table.id_exists(var_decl.var_type.lexeme)):
                        if(var_decl.var_type.lexeme == self.current_type):
                            self.sym_table.set_info(var_decl.var_id.lexeme,var_decl.var_type.lexeme)
                            return
                        else:
                            msg = 'different struct types'
                            self.__error(msg, var_decl.var_id)
                    else:
                        msg = 'struct type not declared'
                        self.__error(msg, var_decl.var_id)
                else:
                    msg = 'mismatch type in assignment'
                    self.__error(msg, var_decl.var_id)
            if(var_decl.var_type.tokentype is token.ID):
                self.sym_table.set_info(var_decl.var_id.lexeme,var_decl.var_type.lexeme)
            else:
                self.sym_table.set_info(var_decl.var_id.lexeme, var_decl.var_type.tokentype)
        elif(self.current_type is token.NIL):
            msg = 'Nil and no type defined'
            self.__error(msg, var_decl.var_id)
        else:
            self.sym_table.set_info(var_decl.var_id.lexeme, self.current_type)

    def visit_assign_stmt(self, assign_stmt):
        assign_stmt.lhs.accept(self)
        lhs_type = self.current_type
        assign_stmt.rhs.accept(self)
        if (not self.doTypesMatch(lhs_type)):
            msg = 'mismatch type in assignment'
            self.__error(msg, assign_stmt.lhs.path[0])

    def visit_struct_decl_stmt(self, struct_decl):
        self.sym_table.add_id(struct_decl.struct_id.lexeme)
        params = {}
        for decl_stmt in struct_decl.var_decls:
            decl_stmt.accept(self)
            params[decl_stmt.var_id.lexeme] = self.current_type
        self.sym_table.set_info(struct_decl.struct_id.lexeme, params)
        
    def visit_fun_decl_stmt(self, fun_decl): 
        self.sym_table.add_id(fun_decl.fun_name.lexeme)
        params = []
        if(fun_decl.return_type is None):
            return_type = token.NIL
        else:
            return_type = fun_decl.return_type
            if(not return_type is str):
                return_type = return_type.tokentype
        self.sym_table.push_environment()
        self.sym_table.add_id('return')
        self.sym_table.set_info('return', return_type)
        for param in fun_decl.params:
            param.accept(self)
            params.append(self.current_type)
        fun_decl.stmt_list.accept(self)
        self.sym_table.set_info(fun_decl.fun_name.lexeme, [params, return_type])
        self.sym_table.pop_environment()

    def visit_return_stmt(self, return_stmt):
        return_stmt.return_expr.accept(self)
        rtype = self.current_type
        expected = self.sym_table.get_info('return')
        if(rtype != token.NIL and not self.doTypesMatch(expected)):
            msg = 'mismatch return type'
            self.__error(msg, return_stmt.return_token)

    def visit_while_stmt(self, while_stmt): 
        while_stmt.bool_expr.accept(self)
        while_stmt.stmt_list.accept(self)

    def visit_if_stmt(self, if_stmt): 
        if_stmt.if_part.bool_expr.accept(self)
        if_stmt.if_part.stmt_list.accept(self)
        for elif_stmt in if_stmt.elseifs:
            elif_stmt.bool_expr.accept(self)
            elif_stmt.stmt_list.accept(self)
        if(if_stmt.has_else):
            if_stmt.else_stmts.accept(self)

    def visit_simple_expr(self, simple_expr):
        simple_expr.term.accept(self)

    def visit_complex_expr(self, complex_expr):
        complex_expr.first_operand.accept(self)
        
        lhs = self.current_type
        complex_expr.rest.accept(self)
        rhs = self.current_type
        symbol = complex_expr.math_rel.tokentype
        if(symbol == token.PLUS):
            if(self.doTypesMatch(lhs) and rhs in [token.STRINGVAL, token.INTVAL, token.FLOATVAL,token.STRINGTYPE, token.INTTYPE, token.FLOATTYPE]):
                self.current_type == rhs
            else:
                msg = 'mismatch type in assignment: complex expr'
                self.__error(msg, complex_expr.math_rel)
        elif(symbol in [token.MULTIPLY, token.DIVIDE, token.MINUS]):
            if(self.doTypesMatch(lhs) and rhs in [token.INTVAL, token.FLOATVAL, token.INTTYPE, token.FLOATTYPE]):
                self.current_type == rhs
            else:
                msg = 'mismatch type in assignment: complex expr'
                self.__error(msg, complex_expr.math_rel)
        elif(symbol == token.MODULO):
            if(self.doTypesMatch(lhs) and (rhs == token.INTVAL or rhs == token.INTTYPE)):
                self.current_type == rhs
            else:
                msg = 'mismatch type in assignment: complex expr'
                self.__error(msg, complex_expr.math_rel) 
        else:
            msg = 'bad Math symbol'
            self.__error(msg, complex_expr.math_rel)    

    def visit_bool_expr(self, bool_expr):
        bool_expr.first_expr.accept(self)
        lhs = self.current_type
        if(bool_expr.bool_rel != None):
            bool_expr.second_expr.accept(self)
            rhs = self.current_type
            symbol = bool_expr.bool_rel.tokentype
            if(symbol in [token.EQUAL, token.NOT_EQUAL]):
                if(lhs == rhs):
                    self.current_type == token.BOOLVAL
                elif(token.NIL in [lhs,rhs]):
                    self.current_type == token.BOOLVAL
                else:
                    msg = 'mismatch type in: BOOL expr'
                    self.__error(msg, bool_expr.bool_rel)
            elif(symbol in [token.LESS_THAN, token.LESS_THAN_EQUAL, token.GREATER_THAN, token.GREATER_THAN_EQUAL]):
                if(lhs == rhs and lhs in [token.STRINGVAL, token.INTVAL, token.FLOATVAL, token.BOOLVAL]):
                    self.current_type == token.BOOLVAL
                else:
                    msg = 'mismatch type in: BOOL expr'
                    self.__error(msg, bool_expr.bool_rel)
        else:
            pass#lhs must be bool or int???
        if(bool_expr.bool_connector != None):
            bool_expr.rest.accept(self)
            rest = self.current_type
            if(rest != token.BOOLVAL):
                msg = 'mismatch type in: BOOL expr, rest'
                self.__error(msg, bool_expr.bool_connector)
        self.current_type = token.BOOLVAL
        
    def visit_lvalue(self, lval):
        for i in lval.path:
            if(not self.sym_table.id_exists(i.lexeme)):
                msg = 'ID not declared'
                self.__error(msg, i)
        self.current_type = self.sym_table.get_info(lval.path[-1].lexeme)

    def visit_fun_param(self, fun_param): 
        self.sym_table.add_id(fun_param.param_name.lexeme)
        if(fun_param.param_type.tokentype is token.ID):
            self.sym_table.set_info(fun_param.param_name.lexeme, fun_param.param_type.lexeme)
        else:
            self.sym_table.set_info(fun_param.param_name.lexeme, fun_param.param_type.tokentype)
        self.current_type = fun_param.param_type.tokentype

    def visit_simple_rvalue(self, simple_rvalue):
        self.current_type = simple_rvalue.val.tokentype

    def visit_new_rvalue(self, new_rvalue):
        if(not self.sym_table.id_exists(new_rvalue.struct_type.lexeme)):
                msg = 'Struct ID not declared'
                self.__error(msg, new_rvalue)
        self.current_type = new_rvalue.struct_type.lexeme
        
    def visit_call_rvalue(self, call_rvalue):
        if(not self.sym_table.id_exists(call_rvalue.fun.lexeme)):
                msg = 'ID not declared'
                self.__error(msg, call_rvalue.fun)
        for expr in call_rvalue.args:
            expr.accept(self)
        info = self.sym_table.get_info(call_rvalue.fun.lexeme)
        self.current_type = info[1]

    def visit_id_rvalue(self, id_rvalue):
        for i in id_rvalue.path:
            if(not self.sym_table.id_exists(i.lexeme)):
                msg = 'ID not declared in id_rval'
                self.__error(msg, i)
        self.current_type = self.sym_table.get_info(id_rvalue.path[-1].lexeme)