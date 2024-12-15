# extract_branch_data

A set of tools to extract branch taken data from a binary.

The core utilites are `branch_data.py` and `predict.py`.

## `branch_data.py`:
* disassembles a binary
* parses the assembly for branch instructions (x86)
* configures and runs LLDB log all branch instructions and
  if they were taken


## `predict.py`:
* runs the two-level adaptive branch predictor with global history
  on the data, comparing gshare and concatenation

## `bp.tracetemplate`:

* Apple Instruments template that measures branch
  mispredictions
* can compare CPU's branch prediction algorithm to the
  one implemented in `predict.py`

Example:
```
# record
xctrace record \
  --template 'bp.tracetemplate' \
  --output tree-analysis.trace \
  --launch -- /usr/local/bin/tree /

python pmc-parse.py
```

### Configuration

Must install the XCode IDE: XCode command line tools are not enough.
May also have to switch the XCode developer tools:
```
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
```

The trace template tracks the following CPU counters:
```
BR_INST_RETIRED.COND # total conditional branches
BR_MISP_RETIRED.COND # total mispredicted conditional branches
```
