def create_test_file(filename, size_mb=100):
    pattern = b"Hello, this is a test pattern with some variation 12345!\n"
    repeats = (size_mb * 1024 * 1024) // len(pattern)

    with open(filename, "wb") as f:
        for _ in range(repeats):
            f.write(pattern)


create_test_file("bzip2_test.txt", 1)
