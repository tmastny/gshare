CXX = g++
CXXFLAGS = -std=c++17
LLVM_PATH = /usr/local/opt/llvm
INCLUDES = -I$(LLVM_PATH)/include
LIBS = -L$(LLVM_PATH)/lib -llldb
RPATH = -Wl,-rpath,$(LLVM_PATH)/lib

TARGET = lib/commands.out
SRC = lib/commands.cpp

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(INCLUDES) $(LIBS) $(RPATH)

.PHONY: clean
clean:
	rm -f $(TARGET)
