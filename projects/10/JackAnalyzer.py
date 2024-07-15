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
        self.output_file= os.path.join(path,base_name+".xml")
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
    def CompileClass(self):
        with open(self.output_file,'a') as outputfile:
            line='<class>\n'
            outputfile.write(line)
            i=0
        while i<3:
                self.writeLine()
                i=i+1
        while self.tokens[0]!='constructor' and self.tokens[0]!='method' and self.tokens[0]!='function' and self.tokens[3]!='(' and self.tokens[2]!='(':
            self.CompileClassVarDec()
        while self.tokens[0]!='}':
            self.CompileSubroutine()
        with open(self.output_file,'a') as outputfile:
            self.writeLine()
            line='</class>\n'
            outputfile.write(line)
    def CompileClassVarDec(self):
        with open(self.output_file,'a') as outputfile:
            line='<classVarDec>\n'
            outputfile.write(line)
        while self.tokens[0]!=';':
            self.writeLine()
        self.writeLine()
        with open(self.output_file,'a') as outputfile:
            line='</classVarDec>\n'
            outputfile.write(line)
    def CompileSubroutine(self):
        with open(self.output_file,'a') as outputfile:
            line='<subroutineDec>\n'
            outputfile.write(line)
        i=0
        while i<4:
            self.writeLine()
            i=i+1
        self.CompileParameterList()
        self.writeLine()
        with open(self.output_file,'a') as outputfile:
            line='<subroutineBody>\n'
            outputfile.write(line)
        self.writeLine()
        while self.tokens[0]=='var':
            self.CompileVarDec()
        self.CompileStatements()
        self.writeLine()
        with open(self.output_file,'a') as outputfile:
            line='</subroutineBody>\n'
            outputfile.write(line)
        with open(self.output_file,'a') as outputfile:
            line='</subroutineDec>\n'
            outputfile.write(line)

    def CompileParameterList(self):
        with open(self.output_file,'a') as outputfile:
            line='<parameterList>\n'
            outputfile.write(line)
        while self.tokens[0]!=')':
            self.writeLine()
        with open(self.output_file,'a') as outputfile:
            line='</parameterList>\n'
            outputfile.write(line)
    def CompileVarDec(self):
        with open(self.output_file,'a') as outputfile:
            line='<varDec>\n'
            outputfile.write(line)
        while self.tokens[0]!=';':
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
            outputfile.write(line)
        self.writeLine()
        while self.tokens[0]!='(':
            self.writeLine()
        self.writeLine()
        self.CompileExpressionList()
        self.writeLine()
        self.writeLine()
        with open(self.output_file,'a') as outputfile:
            line='</doStatement>\n'
            outputfile.write(line)
    def CompileLet(self):
        with open(self.output_file,'a') as outputfile:
            line='<letStatement>\n'
            outputfile.write(line)
        self.writeLine()
        self.writeLine()
        if self.tokens[0]=='[':
            self.writeLine()
            self.CompileExpression()
            self.writeLine()
        self.writeLine()
        self.CompileExpression()
        self.writeLine()
        with open(self.output_file,'a') as outputfile:
            line='</letStatement>\n'
            outputfile.write(line)
    def CompileWhile(self):
        with open(self.output_file,'a') as outputfile:
            line='<whileStatement>\n'
            outputfile.write(line)
        self.writeLine()
        self.writeLine()
        self.CompileExpression()
        self.writeLine()
        self.writeLine()
        self.CompileStatements()
        self.writeLine()
        with open(self.output_file,'a') as outputfile:
            line='</whileStatement>\n'
            outputfile.write(line)
    def CompileReturn(self):
        with open(self.output_file,'a') as outputfile:
            line='<returnStatement>\n'
            outputfile.write(line)
        self.writeLine()
        if self.tokens[0]!=';':
            self.CompileExpression()
        self.writeLine()
        with open(self.output_file,'a') as outputfile:
            line='</returnStatement>\n'
            outputfile.write(line)
    def CompileIf(self):
        with open(self.output_file,'a') as outputfile:
            line='<ifStatement>\n'
            outputfile.write(line)
        self.writeLine()
        self.writeLine()
        self.CompileExpression()
        self.writeLine()
        self.writeLine()
        self.CompileStatements()
        self.writeLine()
        if self.tokens[0]=='else':
            self.writeLine()
            self.writeLine()
            self.CompileStatements()
            self.writeLine()
        with open(self.output_file,'a') as outputfile:
            line='</ifStatement>\n'
            outputfile.write(line)
    def CompileExpression(self):
        with open(self.output_file,'a') as outputfile:
            line='<expression>\n'
            outputfile.write(line)
        self.CompileTerm()
        while self.tokens[0]!=')' and self.tokens[0]!=']' and self.tokens[0]!=';' and self.tokens[0]!=',':
            self.writeLine()
            self.CompileTerm()
        with open(self.output_file,'a') as outputfile:
            line='</expression>\n'
            outputfile.write(line)
    def CompileTerm(self):
        with open(self.output_file,'a') as outputfile:
            line='<term>\n'
            outputfile.write(line)
        if self.tokentypes[0]==TokenType.INT_CONST or self.tokentypes[0]==TokenType.STRING_CONST or self.tokentypes[0]==TokenType.KEYWORD:
            self.writeLine()
        elif self.tokentypes[0]==TokenType.IDENTIFIER:
            if self.tokens[1]=='[':
                self.writeLine()
                self.writeLine()
                self.CompileExpression()
                self.writeLine()
            elif self.tokens[1]=='(' or self.tokens[1]=='.':
                while self.tokens[0]!='(':
                    self.writeLine()
                self.writeLine()
                self.CompileExpressionList()
                self.writeLine()
            else:
                self.writeLine()
        elif self.tokens[0]=='(':
            self.writeLine()
            self.CompileExpression()
            self.writeLine()
        elif self.tokens[0]=='-' or self.tokens[0]=='~':
            self.writeLine()
            self.CompileTerm()
        with open(self.output_file,'a') as outputfile:
            line='</term>\n'
            outputfile.write(line)
    def CompileExpressionList(self):
        with open(self.output_file,'a') as outputfile:
            line='<expressionList>\n'
            outputfile.write(line)
        if self.tokens[0]!=')':
            self.CompileExpression()
            while self.tokens[0]==',':
                self.writeLine()
                self.CompileExpression()
        with open(self.output_file,'a') as outputfile:
            line='</expressionList>\n'
            outputfile.write(line)
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
                line="<identifier> "+str(token)+" </identifier>\n"                 
            outputfile.write(line)
        self.tokens=self.tokens[1:]
        self.tokentypes=self.tokentypes[1:]
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

def removeComment(sentence):
    sentence=sentence.lstrip(' ')
    sentence = re.sub(r'//.*|\/\*.*?\*\/', '', sentence)
    processedSentence = re.sub(r'/\*\*.*?\*/', '', sentence, flags=re.DOTALL)
    return processedSentence
keywords=['class','constructor','function','method','field','static','var','int','char','boolean','void','true','false','null','this','let','do','if','else','while','return']
symbols=['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~']
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