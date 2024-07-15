from enum import Enum
import os
import re
import glob
class VMTranslator:
    def __init__(self):
        self.parser=Parser()
        self.codewriter=CodeWriter("")

    def complie(self,filename):
        self.filename=filename
        if self.isfile():
            print(f"Compiling {filename}...")
            self.processFileName(filename)
            self.read_and_write()
        else:
            print(f"Compiling the dir {filename}...")
            self.files_array=self.get_files_in_path(filename)
            self.processDirName(filename)
            for file in self.files_array:
                self.codewriter=CodeWriter("")
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
        self.output_file= os.path.join(path,base_name+".asm")
    def processDirName(self,filename):
        self.files_array=self.get_files_in_path(filename)
        dir_name=os.path.basename(filename)
        output_filename=os.path.join(filename,dir_name+".asm")
        self.output_file=output_filename
    def get_files_in_path(self,path):
        files_array = glob.glob(os.path.join(path, '*.vm'))
        return files_array
    def read_and_write(self):
        self.codewriter.output_file=self.output_file
        self.codewriter.input_file=os.path.splitext(os.path.split(self.input_file)[1])[0]
        print(self.codewriter.input_file)
        with open(self.input_file,'r') as input_file:
            input_file.seek(0)
            while self.parser.hasMoreCommands():
                self.parser.line=input_file.readline()
                commandtype=self.parser.getCommandType()
                self.codewriter.commandType=commandtype
                if commandtype==CommandType.C_PUSH or commandtype==CommandType.C_POP:
                    self.codewriter.segment=self.parser.segment
                    self.codewriter.number=self.parser.arg
                    self.codewriter.input_file=self.input_file
                    self.codewriter.writePushPop()
                elif commandtype==CommandType.C_ARITHMETIC:
                    self.codewriter.math=self.parser.arg
                    self.codewriter.writeArithmetic()
                elif commandtype==CommandType.C_LABEL:
                    self.codewriter.label=self.parser.arg
                    self.codewriter.writeLabel()
                elif commandtype==CommandType.C_GOTO:
                    self.codewriter.label=self.parser.arg
                    self.codewriter.writeGoto()
                elif commandtype==CommandType.C_IF:
                    self.codewriter.label=self.parser.arg
                    self.codewriter.writeIf()
                elif commandtype==CommandType.C_FUNCTION:
                    function=self.parser.arg1()
                    localnumber=int(self.parser.arg2())
                    self.codewriter.label=function
                    self.codewriter.writeLabel()
                    self.codewriter.number=localnumber
                    self.codewriter.writeFunction()
                elif commandtype==CommandType.C_RETURN:
                    self.codewriter.writeReturn()

class CommandType(Enum):
    C_ARITHMETIC=1
    C_PUSH=2
    C_POP=3
    C_LABEL=4
    C_GOTO=5
    C_IF=6
    C_FUNCTION=7
    C_RETURN=8
    C_CALL=9
    C_NONE=10
class Parser:
    def __init__(self):
        self.line="//First line"
    def getCommandType(self):
        self.command=removeSpaceComment(self.line)
        if self.command != "":
            self.lineCommandType=self.commandType()
            if self.lineCommandType==CommandType.C_ARITHMETIC:
                self.arg=self.arg1()
            elif self.lineCommandType==CommandType.C_PUSH or self.lineCommandType==CommandType.C_POP:
                fullarg2=self.arg2()
                self.testFullArg2(fullarg2)
            elif self.lineCommandType==CommandType.C_LABEL:
                self.arg=self.arg2()
            elif self.lineCommandType==CommandType.C_GOTO:
                self.arg=self.arg2()
            elif self.lineCommandType==CommandType.C_IF:
                self.arg=self.arg2()
            return self.lineCommandType
        else:
            return CommandType.C_NONE
    def testFullArg2(self,fullarg2):
        num=3
        if self.lineCommandType==CommandType.C_PUSH:
            num=4
        if fullarg2.startswith("constant"):
            self.segment="constant"
            self.arg=self.command[num+8:]
        elif fullarg2.startswith("local"):
            self.segment="local"
            self.arg=self.command[num+5:]
        elif fullarg2.startswith("argument"):
            self.segment="argument"
            self.arg=self.command[num+8:]
        elif fullarg2.startswith("this"):
            self.segment="this"
            self.arg=self.command[num+4:]
        elif fullarg2.startswith("that"):
            self.segment="that"
            self.arg=self.command[num+4:]
        elif fullarg2.startswith("pointer"):
            self.segment="pointer"
            self.arg=self.command[num+7:]
        elif fullarg2.startswith("temp"):
            self.segment="temp"
            self.arg=self.command[num+4:]
        elif fullarg2.startswith("static"):
            self.segment="static"
            self.arg=self.command[num+6:]
        else:
            print(f"Error, put in wrong push/pop command.")

    def hasMoreCommands(self):
        if not self.line:
            return False
        else:
            return True
    def commandType(self):
        if self.command.startswith("add") or self.command.startswith("sub") or self.command.startswith("neg") or self.command.startswith("eq") or self.command.startswith("gt") or self.command.startswith("lt") or self.command.startswith("and") or self.command.startswith("or") or self.command.startswith("not"):
            return CommandType.C_ARITHMETIC
        elif self.command.startswith("push"):
            return CommandType.C_PUSH
        elif self.command.startswith("pop"):
            return CommandType.C_POP
        elif self.command.startswith("label"):
            if isNumberStart(self.command[5:]):
                print("Error, label name shouldn't start with number.")
            else:
                return CommandType.C_LABEL
        elif self.command.startswith("goto"):
            return CommandType.C_GOTO
        elif self.command.startswith("if-goto"):
            return CommandType.C_IF
        elif self.command.startswith("call"):
            return CommandType.C_CALL
        elif self.command.startswith("function"):
            if isNumberStart(self.command[8:]):
                print("Error, function name shouldn't start with number.")
            else:
                return CommandType.C_FUNCTION
        elif self.command.startswith("return"):
            return CommandType.C_RETURN

    def arg1(self):
        if self.lineCommandType==CommandType.C_ARITHMETIC:
            return self.command
        elif self.lineCommandType==CommandType.C_PUSH:
            return "push"
        elif self.lineCommandType==CommandType.C_POP:
            return "pop"
        elif self.lineCommandType==CommandType.C_FUNCTION or self.lineCommandType==CommandType.C_CALL:
            return self.command.split()[1] 
        elif self.lineCommandType==CommandType.C_RETURN:
            print(f"Error, C_RETURN can't call this function.")
    def arg2(self):
        if self.lineCommandType==CommandType.C_PUSH or self.lineCommandType==CommandType.C_GOTO:
            return self.command[4:]
        elif self.lineCommandType==CommandType.C_POP:
            return self.command[3:]
        elif self.lineCommandType==CommandType.C_LABEL:
            return self.command[5:]
        elif self.lineCommandType==CommandType.C_IF:
            return self.command[7:]
        elif self.lineCommandType==CommandType.C_FUNCTION or self.lineCommandType==CommandType.C_CALL:
            return self.command.split()[2] 
        

class CodeWriter():
    time=0
    def __init__(self,output_file):
        self.output_file=output_file
        self.segment=""
        self.segmentType=""
    def writePushPop(self):
        with open(self.output_file,'a') as outputfile:
            self.segmentType=''
            self.processSegmentType()
            if self.commandType==CommandType.C_PUSH:
                if self.segment=="constant" or self.segment=="local" or self.segment=="argument" or self.segment=="this" or self.segment=="that":
                    line='@'+str(self.number)+'\nD=A\n'
                    if self.segment!="constant":
                        line=line+'@'+self.segmentType+'\nA=M+D\nD=M\n'
                    line=line+'@SP\nA=M\nM=D\n@SP\nM=M+1\n'
                elif self.segment=="temp" or self.segment=="pointer":
                    line='@'+str(self.number)+'\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
                elif self.segment=="static":
                    line='@'+str(self.input_file)+'.'+str(self.number)+'\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
            elif self.commandType==CommandType.C_POP:
                if self.segment=="local" or self.segment=="argument" or self.segment=="this" or self.segment=="that":  
                    line='@'+str(self.number)+'\nD=A\n@'+self.segmentType+'\nM=M+D\n@SP\nM=M-1\nA=M\nD=M\n@'+self.segmentType+'\nA=M\nM=D\n@'+self.number+'\nD=A\n@'+self.segmentType+'\nM=M-D\n'
                elif self.segment=="temp" or self.segment=="pointer":   
                    line='@SP\nM=M-1\nA=M\nD=M\n@'+str(self.number)+'\nM=D\n'
                elif self.segment=="static":
                    line='@SP\nM=M-1\nA=M\nD=M\n@'+str(self.input_file)+'.'+str(self.number)+'\nM=D\n'
            outputfile.write(line)
    def processSegmentType(self):
        if self.segment=="local":
            self.segmentType='LCL'
        elif self.segment=="argument":
            self.segmentType='ARG'
        elif self.segment=="this":
            self.segmentType='THIS'
        elif self.segment=="that":
            self.segmentType='THAT'
        elif self.segment=="temp":
            self.number=str(int(self.number)+5)
        elif self.segment=="pointer":
            self.number=str(int(self.number)+3)
    def writeArithmetic(self):
        with open(self.output_file,'a') as outputfile:
            if self.math=='neg' or self.math=='not':
                line1='@SP\nM=M-1\nA=M\n'
                if self.math=='neg':
                    line2='M=-M\n'
                elif self.math=='not':
                    line2='M=!M\n'
            else:
                line1='@SP\nM=M-1\n@SP\nA=M\nD=M\n@SP\nM=M-1\n@SP\nA=M\n'
                if self.math=='add':
                    line2='M=M+D\n'
                elif self.math=='sub':
                    line2='M=M-D\n'
                elif self.math=='and':
                    line2='M=M&D\n'
                elif self.math=='or':
                    line2='M=M|D\n'
                elif self.math=='eq' or self.math=='gt' or self.math=='lt':
                    line2='D=M-D\nM=-1\n@IF'+str(self.time)+'\nD;'
                    if self.math=='eq':
                        line2=line2+'JEQ\n'
                    elif self.math=='gt':
                        line2=line2+'JGT\n'
                    elif self.math=='lt':
                        line2=line2+'JLT\n'
                    line2=line2+'@SP\nA=M\nM=0\n(IF'+str(self.time)+')\n'
                    CodeWriter.time=CodeWriter.time+1
            line3='@SP\nM=M+1\n'
            outputfile.write(line1+line2+line3)
    def writeLabel(self):
        with open(self.output_file,'a') as outputfile:
            line='('+self.label+')\n'
            outputfile.write(line)
    def writeGoto(self):
        with open(self.output_file,'a') as outputfile:
            line='@'+self.label+'\n0;JMP\n'
            outputfile.write(line)
    def writeIf(self):
        with open(self.output_file,'a') as outputfile:
            line='@SP\nM=M-1\nA=M\nD=M\n@'+self.label+'\nD;JNE\n'
            outputfile.write(line)
    def writeFunction(self):
        with open(self.output_file,'a') as outputfile:
            i=0
            while i<self.number:
                line='@'+str(i)+'\nD=A\n@LCL\nM=M+D\n@LCL\nA=M\nM=0\n@'+str(i)+'\nD=A\n@LCL\nM=M-D\n'
                i=i+1
                outputfile.write(line)
    def writeReturn(self):
        with open(self.output_file,'a') as outputfile:
            line='@LCL\nD=M\n@frame\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@ARG\nA=M\nM=D\n@ARG\nD=M\n@SP\nM=D+1\n@frame\nMD=M-1\nA=D\nD=M\n@THAT\nM=D\n@frame\nMD=M-1\nA=D\nD=M\n@THIS\nM=D\n@frame\nMD=M-1\nA=D\nD=M\n@ARG\nM=D\n@frame\nMD=M-1\nA=D\nD=M\n@LCL\nM=D\n@frame\nMD=M-1\nA=M\n0;JMP\n'
            outputfile.write(line)
def isNumberStart(string):
    pattern=r'^[0-9].*$'
    return re.match(pattern,string) is not None
def removeSpaceComment(sentence):
    if sentence.startswith("function") or sentence.startswith("call"):
        words=sentence.split('//')[0]
        return words
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

def main():
    while True:
        vmTranslator = VMTranslator()
        user_input = input("> ")
        if user_input.startswith("Vmtranslator"):
            filename = user_input.split()[1]
            vmTranslator.complie(filename)
        elif user_input == "exit":
            print("Exiting program...")
            break
        else:
            print("Invalid command. Please enter 'Vmtranslator filename' or 'exit'.")

if __name__ == "__main__":
    main()
