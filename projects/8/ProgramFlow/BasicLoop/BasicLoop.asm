@0
D=A
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@LCL
M=M+D
@SP
M=M-1
A=M
D=M
@LCL
A=M
M=D
@0
D=A
@LCL
M=M-D
(LOOP)
@0
D=A
@ARG
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@LCL
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M
D=M
@SP
M=M-1
@SP
A=M
M=M+D
@SP
M=M+1
@0
D=A
@LCL
M=M+D
@SP
M=M-1
A=M
D=M
@LCL
A=M
M=D
@0
D=A
@LCL
M=M-D
@0
D=A
@ARG
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M
D=M
@SP
M=M-1
@SP
A=M
M=M-D
@SP
M=M+1
@0
D=A
@ARG
M=M+D
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D
@0
D=A
@ARG
M=M-D
@0
D=A
@ARG
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@LOOP
D;JNE
@0
D=A
@LCL
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1