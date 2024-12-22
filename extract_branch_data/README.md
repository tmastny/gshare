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
  --launch -- /usr/local/bin/tree .

# create output
xctrace export \
  --input tree-analysis_pwd.trace \
  --xpath '/trace-toc/run/data/table[@schema="counters-profile"]' \
  --output summary.xml

python pmc-parse.py
```

## benchmark.py

```
Starting benchmark...


Benchmarking ./branch_data_cpp.py:
./branch_data_cpp.py run 1: 82.561 seconds
./branch_data_cpp.py run 2: 82.877 seconds
./branch_data_cpp.py run 3: 82.979 seconds
./branch_data_cpp.py run 4: 83.747 seconds
./branch_data_cpp.py run 5: 83.311 seconds
Average: 83.095 seconds
Std Dev: 0.452 seconds

Benchmarking ./branch_data_py.py:
./branch_data_py.py run 1: 95.494 seconds
./branch_data_py.py run 2: 94.985 seconds
./branch_data_py.py run 3: 94.480 seconds
./branch_data_py.py run 4: 94.650 seconds
./branch_data_py.py run 5: 95.459 seconds
Average: 95.014 seconds
Std Dev: 0.460 seconds

Benchmarking ./branch_data_lldb.py:
./branch_data_lldb.py run 1: 98.673 seconds
./branch_data_lldb.py run 2: 98.939 seconds
./branch_data_lldb.py run 3: 98.967 seconds
./branch_data_lldb.py run 4: 99.316 seconds
./branch_data_lldb.py run 5: 98.648 seconds
Average: 98.909 seconds
Std Dev: 0.271 seconds

Summary:
--------------------------------------------------
./branch_data_cpp.py 83.095 ± 0.452 seconds
./branch_data_py.py  95.014 ± 0.460 seconds
./branch_data_lldb.py 98.909 ± 0.271 seconds


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
