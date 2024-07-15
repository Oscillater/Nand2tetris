import os
import glob
import re
from enum import Enum
class JackAnalyzer:
    def __init__(self):
        self.jacktokenizer=JackTokenizer()
    def complie(self,filename):
        self.filename=filename
        print(f"Compiling the dir {filename}...")
        self.files_array=self.get_files_in_path(filename)
        for file in self.files_array:
            self.processFileName(file)
            self.input_file=file
            self.read_and_write()
        print(f"Complete compiling {filename}.")
    def isfile(self):
        if os.path.isfile(self.filename):
            return True
        elif os.path.isdir(self.filename):
            return False
        else:
            print(f"Invalid input. Please provide a valid file or directory path.")
    def processFileName(self,filename):
        path,name=os.path.split(filename)
        base_name,ext=os.path.splitext(name)
        self.input_file=filename
        self.output_file= os.path.join(path,base_name+".vm")
    def get_files_in_path(self,path):
        files_array = glob.glob(os.path.join(path, '*.jack'))
        return files_array
    def readProcessFile(self):
        with open(self.input_file,'r') as input_file:
            input_file.seek(0)
            self.content=input_file.read()
            self.content=removeComment(self.content).replace('\n',' ')
            self.jacktokenizer.content=self.content
    def read_and_write(self):
        with open(self.input_file,'r') as input_file:
            self.compilationEngine=CompilationEngine(self.output_file)
            self.readProcessFile()
            while self.jacktokenizer.hasMoreContents():
                token,tokentype=self.jacktokenizer.tokenType()
                self.compilationEngine.tokens=self.compilationEngine.tokens+[token]
                self.compilationEngine.tokentypes=self.compilationEngine.tokentypes+[tokentype]
        self.compilationEngine.CompileClass()

class JackTokenizer:
    def __init__(self):
        self.content=""
    def hasMoreContents(self):
        if not self.content:
            return False
        else:
            return True

    def tokenType(self):
        self.content=self.content.lstrip(' ')
        self.content=self.content.lstrip('\t')
        self.content=self.content.lstrip(' ')
        self.content=self.content.lstrip('\t')
        if self.startWithKeyword():
            return self.keyword,TokenType.KEYWORD
        elif self.startWithSymbol():
            return self.symbol,TokenType.SYMBOL
        elif self.startWithNumber():
            return self.number,TokenType.INT_CONST
        elif self.startWithString():
            return self.string,TokenType.STRING_CONST
        else:
            self.content=self.content.lstrip(' ')
            self.giveMeIdentifier()
            return self.identifier,TokenType.IDENTIFIER
       
    def startWithKeyword(self):
        self.content=self.content.lstrip(' ')
        for keyword in keywords:
            if self.content.startswith(keyword):
                self.keyword=keyword
                self.content=self.content[len(keyword):]
                return True
        return False
    def startWithSymbol(self):
        self.content=self.content.lstrip(' ')
        for symbol in symbols:
            if self.content.startswith(symbol):
                self.symbol=symbol
                self.content=self.content[1:]
                return True
        return False
    def startWithNumber(self):
        self.content=self.content.lstrip(' ')
        match = re.match(r'^(3276[0-7]|327[0-6][0-9]|32[0-7][0-9]{0,2}|3[0-1][0-9]{0,3}|[1-3][0-9]{0,4}|[1-9][0-9]{0,3}|[0-9])', self.content)
        if match:
            self.number=int(match.group(0))
            self.content=self.content[len(match.group(0)):]
            return True
        else:
            return False
    def startWithString(self):
        self.content=self.content.lstrip(' ')
        pattern = r'^"([^"]*)"'  
        match = re.search(pattern, self.content)
        if match:
            self.string=match.group(1)
            self.content=self.content[len(self.string)+2:]
            return True
        return False
    def giveMeIdentifier(self):
        self.content=self.content.lstrip(' ')
        parts=self.content.split(' ',1)
        self.identifier=parts[0]
        length=len(parts[0])
        if len(parts)==1:
            self.last=""
        else:
            self.last=parts[1]
        for symbol in symbols:
            parts=self.content.split(symbol,1)
            if length>len(parts[0]):
                self.identifier=parts[0]
                length=len(parts[0])
                if len(parts)==1:
                    self.last=""
                else:
                    self.last=symbol+parts[1]
        self.content=self.last
                
class CompilationEngine:
    def __init__(self,outputfile):
        self.output_file=outputfile
        self.tokens=[]
        self.tokentypes=[]
        self.symbolTable=SymbolTable()
        self.VMwriter=VMwriter()
        self.classname=""
        self.ifIndex=0
        self.whileIndex=0
        self.isMethod=False
        self.isConstructor=False
        self.isVoid=False
        self.isArray=False
        self.expressionnumber=1
    def CompileClass(self):
        with open(self.output_file,'a') as outputfile:
            line='<class>\n'
            #outputfile.write(line)
        i=0
        while i<3:
            if self.tokentypes[0]==TokenType.IDENTIFIER:
                self.classname=self.tokens[0]
            self.writeLine()
            i=i+1
        while self.tokens[0]!='constructor' and self.tokens[0]!='method' and self.tokens[0]!='function' and self.tokens[3]!='(' and self.tokens[2]!='(':
            self.CompileClassVarDec()
        while self.tokens[0]!='}':
            self.CompileSubroutine()
        with open(self.output_file,'a') as outputfile:
            self.writeLine()
            line='</class>\n'
            #outputfile.write(line)
    def CompileClassVarDec(self):
        with open(self.output_file,'a') as outputfile:
            line='<classVarDec>\n'
            #outputfile.write(line)
        isField=False
        isStatic=False
        if self.tokens[0]=='field':
            isField=True
            self.writeLine()
        elif self.tokens[0]=='static':
            isStatic=True
            self.writeLine()
        varType=self.tokens[0]
        self.writeLine()
        while self.tokens[0]!=';':
            if self.tokentypes[0]==TokenType.IDENTIFIER and not self.symbolTable.isDefine(self.tokens[0]):
                if isField:
                    self.symbolTable.Define(self.tokens[0],varType,kind.FIELD) 
                elif isStatic:
                    self.symbolTable.Define(self.tokens[0],varType,kind.STATIC)
                else:
                    self.symbolTable.Define(self.tokens[0],varType,kind.VAR)
            self.writeLine()
        self.writeLine()
        with open(self.output_file,'a') as outputfile:
            line='</classVarDec>\n'
            #outputfile.write(line)
    def CompileSubroutine(self):
        with open(self.output_file,'a') as outputfile:
            line='<subroutineDec>\n'
            #outputfile.write(line)
        if self.tokens[0]=='method':
            self.symbolTable.Define("this",self.classname,kind.ARG)
            self.isMethod=True
        elif self.tokens[0]=='constructor':
            self.isConstructor=True
        self.writeLine()
        if self.tokens[0]=='void':
            self.isVoid=True
        self.writeLine()
        name=self.tokens[0]
        self.writeLine()
        self.writeLine()
        self.CompileParameterList()
        self.writeLine()
        self.VMwriter.writeFunction(name,self.symbolTable.VarCount(kind.ARG))
        if self.isConstructor:
            parameterNumber=self.symbolTable.VarCount(kind.ARG)
            self.VMwriter.writePush(PushPullSegment.CONST,parameterNumber)
            self.VMwriter.writeCall("Memory.alloc",1)
            self.VMwriter.writePop(PushPullSegment.POINTER,0)
            self.isConstructor=False
        elif self.isMethod:
            self.VMwriter.writePush(PushPullSegment.ARG,0)
            self.VMwriter.writePop(PushPullSegment.POINTER,0)
        with open(self.output_file,'a') as outputfile:
            line='<subroutineBody>\n'
            #outputfile.write(line)
        self.writeLine()
        while self.tokens[0]=='var':
            self.CompileVarDec()
        self.CompileStatements()
        if self.isVoid:
            self.VMwriter.writePush(PushPullSegment.CONST,0)
            self.VMwriter.writeReturn()
            self.isVoid=False
        self.writeLine()
        with open(self.output_file,'a') as outputfile:
            line='</subroutineBody>\n'
            #outputfile.write(line)
        with open(self.output_file,'a') as outputfile:
            line='</subroutineDec>\n'
            #outputfile.write(line)
    def CompileParameterList(self):
        with open(self.output_file,'a') as outputfile:
            line='<parameterList>\n'
            outputfile.write(line)
        while self.tokens[0]!=')':
            if self.tokentypes[1]==TokenType.IDENTIFIER and not self.symbolTable.isDefine(self.tokens[1]):
                self.symbolTable.Define(self.tokens[1],self.tokens[0],kind.ARG)
            self.writeLine()
        with open(self.output_file,'a') as outputfile:
            line='</parameterList>\n'
            outputfile.write(line)
    def CompileVarDec(self):
        with open(self.output_file,'a') as outputfile:
            line='<varDec>\n'
            outputfile.write(line)
        while self.tokens[0]!=';':
            if self.tokentypes[1]==TokenType.IDENTIFIER and not self.symbolTable.isDefine(self.tokens[1]) and str(self.tokens[0])!='var':
                self.symbolTable.Define(self.tokens[1],self.tokens[0],kind.VAR)           
            self.writeLine()
        self.writeLine()
        with open(self.output_file,'a') as outputfile:
            line='</varDec>\n'
            outputfile.write(line)
    def CompileStatements(self):
        with open(self.output_file,'a') as outputfile:
            line='<statements>\n'
            outputfile.write(line)
        while self.tokens[0]!='}':
            if self.tokens[0]=='let':
                self.CompileLet()
            elif self.tokens[0]=='if':
                self.CompileIf()
            elif self.tokens[0]=='while':
                self.CompileWhile()
            elif self.tokens[0]=='do':
                self.CompileDo()
            elif self.tokens[0]=='return':
                self.CompileReturn()
        with open(self.output_file,'a') as outputfile:
            line='</statements>\n'
            outputfile.write(line)
    def CompileDo(self):
        with open(self.output_file,'a') as outputfile:
            line='<doStatement>\n'
            #outputfile.write(line)
        self.writeLine()
        self.CompileSubroutineCall()
        self.VMwriter.writePop(PushPullSegment.TEMP,0)
        with open(self.output_file,'a') as outputfile:
            line='</doStatement>\n'
            #outputfile.write(line)
    def CompileLet(self):
        with open(self.output_file,'a') as outputfile:
            line='<letStatement>\n'
            #outputfile.write(line)
        self.writeLine()
        varName=self.tokens[0]
        self.writeLine()
        if self.tokens[0]=='[':     
            self.writeLine()
            self.VMwriter.writePush(processIdentifier(self.symbolTable.Kindof(varName)),self.symbolTable.Indexof(varName))
            self.CompileExpression()
            self.VMwriter.writeArithmetic(ArithmeticCommand.ADD)
            self.writeLine()
            self.writeLine()
            self.CompileExpression()
            self.VMwriter.writePop(PushPullSegment.TEMP,0)         
            self.VMwriter.writePop(PushPullSegment.POINTER,1)
            self.VMwriter.writePush(PushPullSegment.TEMP,0)
            self.VMwriter.writePop(PushPullSegment.THAT,0)
        else:
            self.writeLine()
            self.CompileExpression()
            self.VMwriter.writePop(processIdentifier(self.symbolTable.Kindof(varName)),self.symbolTable.Indexof(varName))
        self.writeLine()
        self.writeLine()
        with open(self.output_file,'a') as outputfile:
            line='</letStatement>\n'
            #outputfile.write(line)
    def CompileWhile(self):
        with open(self.output_file,'a') as outputfile:
            line='<whileStatement>\n'
            #outputfile.write(line)
        L1=self.classname+str(self.whileIndex)+'WHILEL1'
        L2=self.classname+str(self.whileIndex)+'WHILEL2'
        self.writeLine()
        self.VMwriter.writeLabel(L1)
        self.writeLine()
        self.CompileExpression()
        self.writeLine()
        self.VMwriter.writeArithmetic(ArithmeticCommand.NOT)
        self.VMwriter.writeIf(L2)
        self.writeLine()
        self.CompileStatements()
        self.writeLine()
        self.VMwriter.writeGoto(L1)
        self.VMwriter.writeLabel(L2)
        with open(self.output_file,'a') as outputfile:
            line='</whileStatement>\n'
            #outputfile.write(line)
    def CompileReturn(self):
        with open(self.output_file,'a') as outputfile:
            line='<returnStatement>\n'
            #outputfile.write(line)
        self.writeLine()
        if self.tokens[0]!=';' and self.tokens[0]!='this':
            self.CompileExpression()
        elif self.tokens[0]=='this':
            self.VMwriter.writePush(PushPullSegment.POINTER,0)
            self.writeLine()
        self.writeLine()
        self.VMwriter.writeReturn()
        with open(self.output_file,'a') as outputfile:
            line='</returnStatement>\n'
            #outputfile.write(line)
    def CompileIf(self):
        with open(self.output_file,'a') as outputfile:
            line='<ifStatement>\n'
            #outputfile.write(line)
        L1=self.classname+str(self.ifIndex)+'IFL1'
        L2=self.classname+str(self.ifIndex)+'IFL2'
        self.writeLine()
        self.writeLine()
        self.CompileExpression()
        self.writeLine()
        self.VMwriter.writeArithmetic(ArithmeticCommand.NOT)
        self.VMwriter.writeIf(L1)
        self.writeLine()
        self.CompileStatements()
        self.VMwriter.writeGoto(L2)
        self.VMwriter.writeLabel(L1)
        self.writeLine()
        if self.tokens[0]=='else':
            self.writeLine()
            self.writeLine()
            self.CompileStatements()
            self.writeLine()
        self.VMwriter.writeLabel(L2)
        with open(self.output_file,'a') as outputfile:
            line='</ifStatement>\n'
            #outputfile.write(line)
    def CompileExpression(self):
        with open(self.output_file,'a') as outputfile:
            line='<expression>\n'
            #outputfile.write(line)
        self.CompileTerm()
        while self.tokens[0]!=')' and self.tokens[0]!=']' and self.tokens[0]!=';' and self.tokens[0]!=',':
            op=self.tokens[0]
            self.writeLine()
            self.CompileTerm()
            self.VMwriter.writeArithmetic(processMathOp(op))
        with open(self.output_file,'a') as outputfile:
            line='</expression>\n'
            #outputfile.write(line)
    def CompileTerm(self):
        with open(self.output_file,'a') as outputfile:
            line='<term>\n'
            #outputfile.write(line)
        if self.tokentypes[0]==TokenType.INT_CONST or self.tokentypes[0]==TokenType.STRING_CONST or self.tokentypes[0]==TokenType.KEYWORD:
            if(self.tokentypes[0]==TokenType.INT_CONST):
                self.VMwriter.writePush(PushPullSegment.CONST,self.tokens[0])
            elif self.tokens[0]=='null':
                self.VMwriter.writePush(PushPullSegment.CONST,0)
            elif self.tokens[0]=='false':
                self.VMwriter.writePush(PushPullSegment.CONST,0)
            elif self.tokens[0]=='true':
                self.VMwriter.writePush(PushPullSegment.CONST,1)
                self.VMwriter.writeArithmetic(ArithmeticCommand.NEG)
            self.writeLine() #constant
        elif self.tokentypes[0]==TokenType.IDENTIFIER:
            if self.tokens[1]=='[':#varName[expression]
                self.writeLine()
                self.writeLine()
                self.CompileExpression()
                self.writeLine()
            elif self.tokens[1]=='(' or self.tokens[1]=='.':#subroutineCall
                self.CompileSubroutineCall()
            else:#varName
                if self.symbolTable.isDefine(self.tokens[0]):
                    self.VMwriter.writePush(processIdentifier(self.symbolTable.Kindof(self.tokens[0])),self.symbolTable.Indexof(self.tokens[0]))
                self.writeLine()
        elif self.tokens[0]=='(':#expression
            self.writeLine()
            self.CompileExpression()
            self.writeLine()
        elif self.tokens[0]=='-' or self.tokens[0]=='~':#unaryOp term
            unOp=self.tokens[0]
            self.writeLine()
            self.CompileTerm()
            self.VMwriter.writeArithmetic(processMathUnaryOp(unOp))
        with open(self.output_file,'a') as outputfile:
            line='</term>\n'
            #outputfile.write(line)
    def CompileSubroutineCall(self):
        if self.tokens[1]=='.':
            name=self.tokens[0]
            subroutine=self.tokens[2]
            self.writeLine()
            self.writeLine()
            self.writeLine()
            if name!=self.classname:
                nameType=self.symbolTable.Typeof(name)
                self.VMwriter.writePush(processIdentifier(self.symbolTable.Kindof(name)),self.symbolTable.Indexof(name))
                subroutine=nameType+'.'+subroutine
            else:
                subroutine=name+'.'+subroutine
        else:
            subroutine=self.classname+'.'+self.tokens[0]
            self.writeLine()
        self.writeLine()
        self.CompileExpressionList()
        self.writeLine()
        self.VMwriter.writeCall(subroutine,self.expressionnumber)
        self.expressionnumber=1
    def CompileExpressionList(self):
        with open(self.output_file,'a') as outputfile:
            line='<expressionList>\n'
            #outputfile.write(line)
        if self.tokens[0]!=')':
            self.CompileExpression()
            while self.tokens[0]==',':
                self.writeLine()
                self.CompileExpression()
                self.expressionnumber=self.expressionnumber+1
        with open(self.output_file,'a') as outputfile:
            line='</expressionList>\n'
            #outputfile.write(line)
    def writeLine(self):
        with open(self.output_file,'a') as outputfile:
            token=self.tokens[0]
            tokentype=self.tokentypes[0]
            if tokentype==TokenType.KEYWORD:
                line="<keyword> "+str(token)+" </keyword>\n"
            elif tokentype==TokenType.SYMBOL:
                line="<symbol> "
                if token=='<':
                    line=line+'&lt;'
                elif token=='>':
                    line=line+'&gt;'
                elif token=='&':
                    line=line+'&amp;'
                else:
                    line=line+str(token)
                line=line+'</symbol>\n'
            elif tokentype==TokenType.INT_CONST:
                line="<integerConstant> "+str(token)+" </integerConstant>\n"
            elif tokentype==TokenType.STRING_CONST:
                line="<stringConstant> "+str(token)+" </stringConstant>\n"
            elif tokentype==TokenType.IDENTIFIER:
                line=self.writeIdentifier(str(token))                 
            #outputfile.write(line)
        self.tokens=self.tokens[1:]
        self.tokentypes=self.tokentypes[1:]
    def writeIdentifier(self,token):
        line="<identifier>"
        if self.symbolTable.isDefine(token):
            line=line+str(self.symbolTable.Kindof(token))+" "+str(self.symbolTable.Typeof(token))+" "+str(self.symbolTable.Indexof(token))+" "+str(token)
        else:
            line=line+"class/subroutine "+str(token)
        line=line+"</identifier>\n"
        return line
class TokenType(Enum):
    KEYWORD=1
    SYMBOL=2
    IDENTIFIER=3
    INT_CONST=4
    STRING_CONST=5
class Keyword(Enum):
    CLASS=1
    METHOD=2
    INT=3
    FUNCTION=4
    BOOLEAN=5
    CONSTRUCTOR=6
    CHAR=7
    VOID=8
    VAR=9
    STATIC=10
    FIEID=11
    LET=12
    DO=13
    IF=14
    ELSE=15
    WHILE=16
    RETURN=17
    TRUE=18
    FALSE=19
    NULL=20
    THIS=21

class kind(Enum):
    STATIC=1
    FIELD=2
    ARG=3
    VAR=4
    CLASS=5
    SUBROUTINE=6
 

class SymbolTable:
    index=0
    indexsub=0
    def __init__(self):
        self.symbolTable={}
        self.subroutine={}
        SymbolTable.indexStatic=0
        SymbolTable.indexField=0
        SymbolTable.indexsubArg=0
        SymbolTable.indexsubVar=0
    def startSubroutine(self):
        self.subroutine={}
        SymbolTable.indexsub=0
    def Define(self,name,typename,kind):
        if kind==kind.STATIC or kind==kind.FIELD:
            if kind==kind.STATIC:
                self.symbolTable[str(name)]=[SymbolTable.indexStatic,typename,kind]
                SymbolTable.indexStatic=SymbolTable.indexStatic+1
            else:
                self.symbolTable[str(name)]=[SymbolTable.indexField,typename,kind]
                SymbolTable.indexField=SymbolTable.indexField+1
        else:
            if kind==kind.ARG:
                self.subroutine[str(name)]=[SymbolTable.indexsubArg,typename,kind]
                SymbolTable.indexsubArg=SymbolTable.indexsubArg+1
            else:
                self.subroutine[str(name)]=[SymbolTable.indexsubVar,typename,kind]
                SymbolTable.indexsubVar=SymbolTable.indexsubVar+1
    def VarCount(self,kind):
        if kind==kind.STATIC:
            return self.indexStatic+1
        elif kind==kind.FIELD:
            return self.indexField+1
        elif kind==kind.ARG:
            return self.indexsubArg+1
        elif kind==kind.VAR:
            return self.indexsubVar+1
    def isDefine(self,name):
        if (self.symbolTable.get(str(name),None) or self.subroutine.get(str(name),None)) == None:
            return False
        else:
            return True
    def Kindof(self,name):
        value=self.symbolTable.get(str(name),None)
        if value != None:
            return value[2]
        else:
            value=self.subroutine.get(str(name),None)
            if value==None:
                return None
            else:
                return value[2]
    def Typeof(self,name):
        value=self.symbolTable.get(str(name),None)
        if value != None:
            return value[1]
        else:
            value=self.subroutine.get(str(name),None)
            if value==None:
                return None
            else:
                return value[1]
    def Indexof(self,name):
        value=self.symbolTable.get(str(name),None)
        if value != None:
            return value[0]
        else:
            value=self.subroutine.get(str(name),None)
            if value==None:
                return None
            else:
                return value[0]        
class PushPullSegment(Enum):
    CONST="constant"
    ARG="argument"
    LOCAL="local"
    STATIC="static"
    THIS="this"
    THAT="that"
    POINTER="pointer"
    TEMP="temp"
    def get_value(self):
        return self.value
class ArithmeticCommand(Enum):
    ADD="add"
    SUB="sub"
    NEG="neg"
    MUL="Math.multiply()"
    DIV="Math.divide()"
    EQ="eq"
    GT="gt"
    LT="lt"
    AND="and"
    OR="or"
    NOT="not"
    def get_value(self):
        return self.value
class VMwriter:
    def __init__(self,outputfile):
        self.outputfile=outputfile
        self.line=""
    def writePush(self,segment,index):
        if isinstance(segment,PushPullSegment):
            self.line="push "+PushPullSegment.get_value(segment)+" "+str(index)+"\n"
            self.writeline()
    def writePop(self,segment,index):
        if isinstance(segment,PushPullSegment):
            self.line="pop "+PushPullSegment.get_value(segment)+" "+str(index)+"\n"
            self.writeline()
    def writeArithmetic(self,command):
        if isinstance(command,ArithmeticCommand):
            self.line=PushPullSegment.get_value(command)+"\n"
            self.writeline()
    def writeLabel(self,symbol):
        self.line="label "+symbol+"\n"
        self.writeline()
    def writeGoto(self,symbol):
        self.line="goto "+symbol+"\n"
        self.writeline()
    def writeIf(self,symbol):
        self.line="if-goto "+symbol+"\n"
        self.writeline()
    def writeCall(self,name,nArgs):
        self.line="call "+name+" "+nArgs+"\n"
        self.writeline()
    def writeFunction(self,name,nLocals):
        self.line="function "+name+" "+nLocals+"\n"
        self.writeline()
    def writeReturn(self):
        self.line="return"+"\n"
        self.writeline()
    def writeline(self):
        with open(self.output_file,'a') as outputfile:
            outputfile.write(self.line)


def removeComment(sentence):
    sentence=sentence.lstrip(' ')
    sentence = re.sub(r'//.*|\/\*.*?\*\/', '', sentence)
    processedSentence = re.sub(r'/\*\*.*?\*/', '', sentence, flags=re.DOTALL)
    return processedSentence
keywords=['class','constructor','function','method','field','static','var','int','char','boolean','void','true','false','null','this','let','do','if','else','while','return']
symbols=['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~']
def processIdentifier(segment):
    if segment==kind.FIELD:
        return PushPullSegment.THIS
    elif segment==kind.STATIC:
        return  PushPullSegment.STATIC
    elif segment==kind.VAR:
        return PushPullSegment.LOCAL
    elif segment==kind.ARG:
        return PushPullSegment.ARG
    
def processMathOp(op):
    if op=='+':
        return ArithmeticCommand.ADD
    elif op=='-':
        return ArithmeticCommand.SUB
    elif op=='*':
        return ArithmeticCommand.MUL
    elif op=='/':
        return ArithmeticCommand.DIV
    elif op=='&':
        return ArithmeticCommand.AND
    elif op=='|':
        return ArithmeticCommand.OR
    elif op=='<':
        return ArithmeticCommand.LT
    elif op=='>':
        return ArithmeticCommand.GT
    elif op=='=':
        return ArithmeticCommand.EQ
def processMathUnaryOp(op):
    if op=='-':
        return ArithmeticCommand.NEG
    elif op=='~':
        return ArithmeticCommand.NOT
def main():
    while True:
        jackAnzlyzer = JackAnalyzer()
        user_input = input("> ")
        if user_input.startswith("JackAnalyzer"):
            filename = user_input.split()[1]
            jackAnzlyzer.complie(filename)
        elif user_input == "exit":
            print("Exiting program...")
            break
        else:
            print("Invalid command. Please enter 'Vmtranslator filename' or 'exit'.")

if __name__ == "__main__":
    main()