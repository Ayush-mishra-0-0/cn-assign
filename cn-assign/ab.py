import sys
MOD=998244353

def mult(a, b, K):
    res = [0] * K
    for i in range(K):
        ai = a[i]
        if ai:
            for j in range(K):
                res[(i + j) % K] = (res[(i + j) % K] + ai * b[j]) % MOD
    return res

def power(a, e, K):
    res = [0] * K
    res[0] = 1
    while e:
        if e & 1:
            res = mult(res, a, K)
        a = mult(a, a, K)
        e >>= 1
    return res

def main():
    input = sys.stdin.read
    data = list(map(int, input().split()))
    
    ptr = 0
    N = data[ptr]
    P = data[ptr + 1]
    K = data[ptr + 2]
    ptr += 3
    
    M = data[ptr]
    ptr += 1
    
    L = data[ptr:ptr + M]
    ptr += M
    
    C = [P // K + (1 if j > 0 and j <= P % K else 0) for j in range(K)]
    LC = [0] * K
    
    for x in L:
        LC[x % K] += 1
    
    Cn = [(C[j] - LC[j]) % MOD for j in range(K)]
    
    T = power(C, N, K)[0]
    B = power(Cn, N, K)[0]
    
    print((T - B) % MOD)

main()