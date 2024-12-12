# xctrace

Tracking actual branch prediction rate
```
xctrace record \
  --template 'bp.tracetemplate' \
  --output tree-analysis.trace \
  --launch -- /usr/local/bin/tree /

open tree-analysis.trace
```

To analyze data:
```
xctrace export \
  --input tree-analysis.trace \
  --xpath '/trace-toc/run/data/table[@schema="counters-profile"]' \
  --output summary.xml

python pmc-parse.py
```

Note: can also use `--time-limit 5s` to kill the program faster since
it's a long running program and will take a while to finish
(and if I run too long, won't open in instruments).

Note: need to install XCode and run:
```
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
```

Setup tracetemplate:
```
BR_INST_RETIRED.COND # total conditional branches
BR_MISP_RETIRED.COND # total mispredicted conditional branches
```


# otool

How to get the full disassembly!
```
otool -tv /usr/local/bin/tree > tree.asm
```

```
cat tree.asm | ./parse_asm.py > parse_asm.txt
cat tree.asm | ./trace_branch.py
```

```
lldb -b -s commands.lldb > lldb.txt
```
# old notes
Notes:

Find the text section of a binary:
```
lldb -b -o "target create /usr/local/bin/tree" -o "image dump sections /usr/local/bin/tree" | grep TEXT
```

Find code range:
```
lldb -b -o "target create /usr/local/bin/tree" -o "image dump sections /usr/local/bin/tree" |
  grep __TEXT.__text |
  ./find_code.py
```

Disassemble a binary:
```
lldb -b -o "target create /usr/local/bin/tree" -o "disassemble --start-address 0x0000000100004688 --count 20"
```
Force:
```
lldb -b -o "target create /usr/local/bin/tree" -o "disassemble --start-address 0x100004688 --end-address 0x10000c93a --force"
```


Print out assembly and parse fo branch instructions:
```
lldb -b -o "target create /usr/local/bin/tree" -o "disassemble --start-address 0x0000000100004688 --end-address 0x000000010000c93a" |
  ./parse_asm.py > parse_asm.txt
```


Break at one branch:
```
lldb -b -o "target create /usr/local/bin/tree" -o "disassemble --start-address 0x0000000100004688 --end-address 0x000000010000c93a" |
  ./trace_branch.py
```

Disassemble tree main:
```
lldb -b -o "target create /usr/local/bin/tree" -o "disassemble --name main"
lldb -b -o "target create /usr/local/bin/tree" -o "disassemble --name emit_tree"
```
