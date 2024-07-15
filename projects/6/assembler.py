from enum import Enum
import os
class CommandType(Enum):
    A_COMMAND=1
    C_COMMAND=2
    L_COMMAND=3
class Translate:
    def __init__(self):
        pass
    def dest(self,deststring):
        if deststring=='null':
            return '000'
        result=''
        if 'A' in deststring:
            result=result+'1'
        else:
            result=result+'0'
        if 'D' in deststring:
            result=result+'1'
        else:
            result=result+'0'
        if 'M' in deststring:
            result=result+'1'
        else:
            result=result+'0'
        return result
    def jump(self,jumpstring):
        if jumpstring=='null':
            return '000'
        elif jumpstring=='JGT':
            return '001'
        elif jumpstring=='JEQ':
            return '010'
        elif jumpstring=='JGE':
            return '011'
        elif jumpstring=='JLT':
            return '100'
        elif jumpstring=='JNE':
            return '101'
        elif jumpstring=='JLE':
            return '110'
        elif jumpstring=='JMP':
            return '111'
    def comp(self,compstring):
        result=''
        if 'M' in compstring:
            result=result+'1'
        else:
            result=result+'0'
        if compstring=='0':
            add='101010'
        elif compstring=='1':
            add='111111'
        elif compstring=='-1':
            add='111010'
        elif compstring=='D':
            add='001100'
        elif compstring=='A' or compstring=='M':
            add='110000'
        elif compstring=='!D':
            add='001101'
        elif compstring=='!A' or compstring=='!M':
            add='110001'
        elif compstring=='-D':
            add='001111'
        elif compstring=='-A' or compstring=='-M':
            add='110011'
        elif compstring=='D+1':
            add='011111'
        elif compstring=='A+1' or compstring=='M+1':
            add='110111'
        elif compstring=='D-1':
            add='001110'
        elif compstring=='A-1' or compstring=='M-1':
            add='110010'
        elif compstring=='D+A' or compstring=='D+M':
            add='000010'
        elif compstring=='D-A' or compstring=='D-M':
            add='010011'
        elif compstring=='A-D' or compstring=='M-D':
            add='000111'
        elif compstring=='D&A' or compstring=='D&M':
            add='000000'
        elif compstring=='D|A' or compstring=='D|M':
            add='010101'
        return result+add
    def deci2Bin(self,symbolstring):
        decimalNum=int(symbolstring)
        padding=16
        binNum=bin(decimalNum)[2:]
        binNum = binNum.zfill(padding)
        return str(binNum)
class SymbolTable:
    def __init__(self):
        self.hash_table={}
        self.hash_table['SP']='0'
        self.hash_table['LCL']='1'
        self.hash_table['ARG']='2'
        self.hash_table['THIS']='3'
        self.hash_table['THAT']='4'
        self.hash_table['R0']='0'
        self.hash_table['R1']='1'
        self.hash_table['R2']='2'
        self.hash_table['R3']='3'
        self.hash_table['R4']='4'
        self.hash_table['R5']='5'
        self.hash_table['R6']='6'
        self.hash_table['R7']='7'
        self.hash_table['R8']='8'
        self.hash_table['R9']='9'
        self.hash_table['R10']='10'
        self.hash_table['R11']='11'
        self.hash_table['R12']='12'
        self.hash_table['R13']='13'
        self.hash_table['R14']='14'
        self.hash_table['R15']='15'
        self.hash_table['SCREEN']='16384'
        self.hash_table['KBD']='24576'
    def addEntry(self,symbol,address):
        self.hash_table[symbol]=address
    def contains(self,symbol):
        if symbol in self.hash_table:
            return True
        else:
            return False
    def getAddress(self,symbol):
        return self.hash_table[symbol]
class Parser:
    def __init__(self,input_file,output_file,symbolTable):
        self.file=input_file
        self.result=output_file
        self.line="//First line"
        self.command=""
        self.symbolTable=symbolTable

     
    def hasMoreCommands(self):
        if not self.line:
            return False
        else:
            return True
    def first_read(self):
        with open(self.input_file,'r') as input_file:
            romNumber=0
            while self.hasMoreCommands():
                self.line=input_file.readline()
                self.command=removeSpaceComment(self.line)
                if self.command !="":
                    self.lineCommandType=self.commandType()
                    if self.lineCommandType==CommandType.L_COMMAND:
                        symbolofL=self.symbol()
                        self.symbolTable.hash_table[symbolofL]=str(romNumber)
                    elif self.lineCommandType==CommandType.A_COMMAND or self.lineCommandType==CommandType.C_COMMAND:
                        romNumber=romNumber+1
                

    def second_read(self):
        self.line="//first line"
        with open(self.input_file,'r') as input_file,open(self.result,'a') as outputfile:
            input_file.seek(0)
            outputfile.truncate(0)
            ramNumber=16
            while self.hasMoreCommands():
                self.line=input_file.readline()
                self.command=removeSpaceComment(self.line)
                if self.command != "":
                    self.lineCommandType=self.commandType()
                    if self.lineCommandType==CommandType.A_COMMAND:
                        commandSymbol=self.symbol()
                        if commandSymbol.isdigit():
                           translateSymbol=commandSymbol
                        else:
                            if self.symbolTable.contains(commandSymbol):
                                translateSymbol=self.symbolTable.getAddress(commandSymbol)
                            else:
                                self.symbolTable.hash_table[commandSymbol]=str(ramNumber)
                                translateSymbol=ramNumber
                                ramNumber=ramNumber+1        
                        translate=Translate()
                        line=translate.deci2Bin(translateSymbol)
                        outputfile.write(line+'\n')
                    elif self.lineCommandType==CommandType.C_COMMAND:
                        commandDest=self.dest()
                        commandJump=self.jump()
                        commandComp=self.comp()
                        translate=Translate()
                        resultDest=translate.dest(commandDest)
                        resultJump=translate.jump(commandJump)
                        resultComp=translate.comp(commandComp)
                        line='111'+resultComp+resultDest+resultJump
                        outputfile.write(line+'\n')

    def symbol(self):
        if self.lineCommandType==CommandType.A_COMMAND:
            return self.command[1:]
        elif self.lineCommandType==CommandType.L_COMMAND:
            return self.command[1:-1]
    def dest(self):
        if '=' in self.command:
            return self.command.split('=')[0]
        else:
            return 'null'
    def jump(self):
        if ';' in self.command:
            return self.command.split(';')[1]
        else:
            return 'null'
    def comp(self):
        result=self.command
        if '=' in result:
            result=result.split('=')[1]
        if ';' in result:
            result=result.split(';')[0]
        return result

    def commandType(self):
        if self.command.startswith('@'):
            return CommandType.A_COMMAND
        elif '=' in self.command or ';' in self.command:
            return CommandType.C_COMMAND
        elif self.command.startswith('(') and self.command.endswith(')'):
            return CommandType.L_COMMAND
        else:
            raise SyntaxError
def removeSpaceComment(sentence):
    words = sentence.split()
    result = []
    for word in words:
        if '//' in word:
            word = word.split('//')[0]
            result.append(word)
            break
        result.append(word)
        if word.endswith('//'):
            break
    processed_sentence = ''.join(result)
    return processed_sentence

class AssemblerCompiler:
    def __init__(self,parser):
        self.parser = parser

    def compile(self, filename):
        print(f"Compiling {filename}...")
        path,name=os.path.split(filename)
        base_name,ext=os.path.splitext(name)
        output_filename = os.path.join(path,base_name+".hack")
        self.parser.input_file=filename
        self.parser.result=output_filename
        self.parser.first_read()
        self.parser.second_read()
        print(f"Complete compiling {filename}.")
        
def main():
    while True:
        symbolTable=SymbolTable()
        parser=Parser("","",symbolTable)
        assembler_compiler = AssemblerCompiler(parser)
        user_input = input("> ")
        if user_input.startswith("Assembler"):
            filename = user_input.split()[1]
            assembler_compiler.compile(filename)
        elif user_input == "exit":
            print("Exiting program...")
            break
        else:
            print("Invalid command. Please enter 'Assembler filename' or 'exit'.")

if __name__ == "__main__":
    main()
