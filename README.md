Notes:

Find the text section of a binary:
```
lldb -b -o "target create /bin/ls" -o "image dump sections /bin/ls" | grep TEXT
```

Find code range:
```
lldb -b -o "target create /bin/ls" -o "image dump sections /bin/ls" | 
  grep __TEXT.__text |
  ./find_code.py
```

Disassemble a binary:
```
lldb -b -o "target create /bin/ls" -o "disassemble --start-address 0x0000000100003940 --count 20"
```


Print out assembly and parse fo branch instructions:
```
lldb -b -o "target create /bin/ls" -o "disassemble --start-address 0x0000000100003940 --end-address 0x00000001000073df" |
  ./parse_asm.py > parse_asm.txt
```



