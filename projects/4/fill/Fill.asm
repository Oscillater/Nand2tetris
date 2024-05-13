// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

//// Replace this comment with your code.
(LOOP)
@SCREEN
D=A
@i
M=D
(LOOP1)
@24576
D=M
@BLACK
D;JNE
@i
A=M
M=0
(BLACK)
@i
A=M
M=-1
@i
M=M+1
D=M
@24575
D=D-A
@LOOP1
D;JLT
@LOOP
0;JMP