#!/usr/bin/env python3
# Smarter verification: prime factorization + bounds for solitary check of 10
import math

def prime_factors(n):
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def sigma_from_factors(factors):
    result = 1
    for p, e in factors.items():
        result *= (p**(e+1) - 1) // (p - 1)
    return result

def sigma(n):
    return sigma_from_factors(prime_factors(n))

target = 9/5
sigma_10 = sigma(10)
print(f"sigma(10) = {sigma_10}, abundancy(10) = {sigma_10}/10 = {sigma_10/10}")

# Check m up to 10^5 using factorization (much faster)
found = []
limit = 100000
for m in range(1, limit + 1):
    s = sigma(m)
    # Check 5*sigma(m) == 9*m exactly
    if 5 * s == 9 * m:
        found.append((m, s))

print(f"\nNumbers m <= {limit} with sigma(m)/m = 9/5:")
for m, s in found:
    print(f"  m = {m}, sigma(m) = {s}, 5*sigma(m) = {5*s}, 9*m = {9*m}")
print(f"Total: {len(found)}")

# Also show the Diophantine structure proof sketch
print("\n=== PROOF SKETCH ===")
print("Suppose 5*sigma(m) = 9*m for some integer m > 0.")
print("Write m = 2^a * 5^b * r where gcd(r,10) = 1.")
print("Then sigma(m) = sigma(2^a) * sigma(5^b) * sigma(r) = (2^{a+1}-1) * (5^{b+1}-1)/4 * sigma(r)")
print("So 5 * (2^{a+1}-1) * (5^{b+1}-1)/4 * sigma(r) = 9 * 2^a * 5^b * r")
print("=> sigma(r)/r = 36 * 2^a * 5^{b-1} / [(2^{a+1}-1) * (5^{b+1}-1)] * 5")
print("This gives strong constraints on a, b, and the structure of r.")
print("\nSUCCESS")
