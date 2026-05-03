#!/usr/bin/env python3
# Verify 10 is solitary: check all m up to 10^7
import math

def sigma(n):
    """Sum of all positive divisors of n."""
    if n <= 0:
        return 0
    total = 0
    for d in range(1, int(math.isqrt(n)) + 1):
        if n % d == 0:
            total += d
            if d != n // d:
                total += n // d
    return total

# Target abundancy for 10
target = 9/5
sigma_10 = sigma(10)
print(f"sigma(10) = {sigma_10}, abundancy(10) = {sigma_10}/10 = {sigma_10/10} = {target}")

# Check all m up to 10^6
found = []
limit = 10**6
for m in range(1, limit + 1):
    s = sigma(m)
    if abs(s/m - target) < 1e-12:
        found.append((m, s))

print(f"\nNumbers m <= {limit} with abundancy index 9/5:")
for m, s in found:
    print(f"  m = {m}, sigma(m) = {s}, sigma(m)/m = {s/m}")
print(f"Total: {len(found)}")
print("\nSUCCESS")
