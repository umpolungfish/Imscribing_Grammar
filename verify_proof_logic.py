import math

def sigma(n):
    total = 0
    for d in range(1, int(math.isqrt(n)) + 1):
        if n % d == 0:
            total += d
            if d != n // d:
                total += n // d
    return total

def check_solitary_10():
    # Target abundancy index for 10 is 18/10 = 9/5
    print("Verifying m=10: sigma(10)/10 =", sigma(10), "/ 10 =", sigma(10)/10)
    
    # Verify the specific Diophantine resolution steps
    # a=1, b=1, r=1
    m = 2**1 * 5**1 * 1
    s = sigma(m)
    if 5*s == 9*m:
        print(f"Verified solution m={m}")
    
    # Case a=0, b=2: sigma(r)/r = 45/31
    # Check that 31 is prime and 19531 is prime as used in the proof
    def is_prime(n):
        if n < 2: return False
        for i in range(2, int(math.isqrt(n)) + 1):
            if n % i == 0: return False
        return True
    
    print("Is 31 prime?", is_prime(31))
    print("Is 19531 prime?", is_prime(19531))
    print("781 factors:", [i for i in range(2, 781) if 781 % i == 0])

check_solitary_10()
