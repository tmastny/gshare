CC=gcc
CFLAGS=-O0 -march=native
WARNINGS=-Wall -Wextra
TARGET=spectre

.PHONY: all clean run

all: $(TARGET)

$(TARGET): spectrev1.c
	$(CC) $(CFLAGS) $(WARNINGS) -o $(TARGET) spectrev1.c

debug: CFLAGS += -g
debug: $(TARGET)

clean:
	rm -f $(TARGET)

run: $(TARGET)
	./$(TARGET)
