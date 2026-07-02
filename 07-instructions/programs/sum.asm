; Sum the integers 1..5, leaving the total in SUM (memory address 15).
; Demonstrates labels (loop/done) and data directives (DB).

        LOADI 5         ; A = 5
        STORE I         ; I = 5   (loop counter)
        LOADI 0         ; A = 0
        STORE SUM       ; SUM = 0

loop:   LOAD SUM        ; A = SUM
        ADD I           ; A = SUM + I
        STORE SUM       ; SUM = A
        LOAD I          ; A = I
        ADD NEG1        ; A = I - 1   (adding 0xFF sets the zero flag at 0)
        STORE I         ; I = A
        JZ done         ; if I reached 0, stop looping
        JMP loop        ; otherwise go again

done:   HALT

NEG1:   DB 0xFF         ; the constant -1 in 8-bit two's complement
I:      DB 0            ; loop counter (initialized by the code above)
SUM:    DB 0            ; running total -> ends as 15
