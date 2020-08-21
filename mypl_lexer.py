import mypl_token as token
import mypl_error as error

class Lexer(object):
    def __init__(self, input_stream):
        """initializes line and column number and input stream"""
        self.line = 1
        self.column = 0
        self.input_stream = input_stream

    def __peek(self):
        """returns the next char in the file while keeping place in stream"""
        pos = self.input_stream.tell()
        symbol = self.input_stream.read(1)
        self.input_stream.seek(pos)
        return symbol

    def __read(self):
        """reads a single char from input file"""
        self.column += 1
        return self.input_stream.read(1)

    def __parse_space(self):
        """ Reads space whie counting newline char"""
        while self.__peek().isspace():
            if(self.__peek()  == '\n'):
                self.line += 1
                self.column = -1
            self.__read()

    def __parse_command(self):
        """Reads and returns a sequence of alpha characters"""
        command = ''
        while self.__peek().isalpha():
            command += self.__read()
        return command

    def __parse_num(self):
        """Reads and returns a sequence of digit characters"""
        number = ''
        while self.__peek().isdigit():
            number += self.__read()
        return number
        
    def next_token(self):
        """ Creates  and returns token while checking for formatting errors"""
        #tokenType = ''
        #lexeme = ''
        self.__parse_space()#ignore spaces
        currCol = self.column + 1
        currLine = self.line
        if(not self.__peek()):#handles eos
            return token.Token(token.EOS, "", self.line, self.column)
        elif(self.__peek() == '#'):#handles comments by reading entire line
            self.input_stream.readline()
            self.column = 0
            self.line += 1
            return self.next_token()
        elif(self.__peek().isalpha()):#handles all symbols with letters
            lexeme = self.__parse_command() 
            while(self.__peek() not in {'=',':',',','/','.','=','>','<','!','(',')','-','%','*','+',';'}):
                if(not self.__peek().isspace()):
                    lexeme += self.__read()
                else:
                    break
            if(lexeme == 'bool'):
                tokenType = token.BOOLTYPE
            elif(lexeme == 'int'):
                tokenType = token.INTTYPE
            elif(lexeme == 'float'):
                tokenType = token.FLOATTYPE
            elif(lexeme == 'string'):
                tokenType = token.STRINGTYPE
            elif(lexeme == 'struct'):
                tokenType = token.STRUCTTYPE
            elif(lexeme == 'and'):
                tokenType = token.AND
            elif(lexeme == 'or'):
                tokenType = token.OR
            elif(lexeme == 'not'):
                tokenType = token.NOT
            elif(lexeme == 'while'):
                tokenType = token.WHILE
            elif(lexeme == 'do'):
                tokenType = token.DO
            elif(lexeme == 'if'):
                tokenType = token.IF
            elif(lexeme == 'then'):
                tokenType = token.THEN
            elif(lexeme == 'else'):
                tokenType = token.ELSE
            elif(lexeme == 'elif'):
                tokenType = token.ELIF
            elif(lexeme == 'end'):
                tokenType = token.END
            elif(lexeme == 'fun'):
                tokenType = token.FUN
            elif(lexeme == 'var'):
                tokenType = token.VAR
            elif(lexeme == 'set'):
                tokenType = token.SET
            elif(lexeme == 'return'):
                tokenType = token.RETURN
            elif(lexeme == 'new'):
                tokenType = token.NEW
            elif(lexeme == 'nil'):
                tokenType = token.NIL
            elif(lexeme == 'true' or lexeme == 'false'):
                tokenType = token.BOOLVAL
            else:#check if variable ID has more non-alpha chars
                tokenType = token.ID
                while(self.__peek() not in {'=',':',',','/','.','=','>','<','!','(',')','-','%','*','+',';'}):
                    if(not self.__peek().isspace()):
                        lexeme += self.__read()
                    else:
                        break
        elif(self.__peek().isdigit()): #Handles int and float values
            lexeme = self.__parse_num()
            if(len(lexeme) > 1 and lexeme[0:1] == '0'):
                raise error.MyPLError("invalid number value", currLine, currCol)
            if(self.__peek() == '.'):#Indicating float value
                lexeme += self.__read()
                floatVal = self.__parse_num()
                if(floatVal == "" or (len(floatVal) > 1 and floatVal[len(floatVal) - 1] == '0')):#test this
                    raise error.MyPLError("invalid float value", currLine, currCol)
                else:
                    lexeme = lexeme + floatVal
                    tokenType = token.FLOATVAL
            else:#int val
                tokenType = token.INTVAL
            if(self.__peek() not in {'=',':',',','/','.','=','>','<','!','(',')','-','%','*','+',';',' ','\n'}):
                raise error.MyPLError("invalid number value", currLine, currCol)
        elif(self.__peek() == '"'):#handles strings with " only (not ')
            self.__read()#read symbol '"'
            lexeme = ''
            tokenType = token.STRINGVAL
            while(self.__peek() != '"'):
                if(self.__peek() == '\n'):
                    raise error.MyPLError("invalid string", currLine, currCol) 
                else:
                    lexeme += self.__read()   
            self.__read()#read end string symbol '"' 
        elif(self.__peek() in {'=',':',',','/','.','=','>','<','!','(',')','-','%','*','+',';'}):#hendles symbols
            lexeme = self.__read()
            if(lexeme == '='):
                if (self.__peek() == '='):
                    lexeme += self.__read()
                    tokenType = token.EQUAL
                else:
                    tokenType = token.ASSIGN
            elif(lexeme == '!'): #handles not equal
                if(self.__peek() != '='):
                    raise error.MyPLError("invalid symbol", currLine, currCol)
                else:
                    lexeme += self.__read()
                    tokenType = token.NOT_EQUAL
            elif(lexeme == '<' or lexeme == '>'):#Handles conditionals
                if(self.__peek() != '='):
                    if(lexeme == '<'):
                        tokenType = token.LESS_THAN
                    else:
                        tokenType = token.GREATER_THAN
                else:
                    lexeme += self.__read()
                    if(lexeme == '<='):
                        tokenType = token.LESS_THAN_EQUAL
                    else:
                        tokenType = token.GREATER_THAN_EQUAL
            elif(lexeme == ':'):
                tokenType = token.COLON
            elif(lexeme == ','):
                tokenType = token.COMMA
            elif(lexeme == '/'):
                tokenType = token.DIVIDE
            elif(lexeme == '.'):
                tokenType = token.DOT
            elif(lexeme == '('):
                tokenType = token.LPAREN
            elif(lexeme == ')'):
                tokenType = token.RPAREN
            elif(lexeme == '-'):
                tokenType = token.MINUS
            elif(lexeme == '%'):
                tokenType = token.MODULO
            elif(lexeme == '*'):
                tokenType = token.MULTIPLY
            elif(lexeme == '+'):
                tokenType = token.PLUS
            elif(lexeme == ';'):
                tokenType = token.SEMICOLON
        return token.Token(tokenType, lexeme, currLine, currCol)