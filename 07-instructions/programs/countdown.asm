; Count down from 3 to 1, printing each value with OUT.
; Shows a loop that emits output on every iteration.

        LOADI 3         ; A = 3
        STORE N         ; N = 3

loop:   LOAD N          ; A = N
        OUT             ; print A
        ADD NEG1        ; A = N - 1
        STORE N         ; N = A
        JZ done         ; when N hits 0, stop
        JMP loop        ; otherwise keep counting down

done:   HALT

NEG1:   DB 0xFF         ; constant -1
N:      DB 0            ; current value
