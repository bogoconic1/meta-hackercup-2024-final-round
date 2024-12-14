def solve(input: str) -> str:
    import sys
    MOD = 10**9 +7

    def precompute_factorials(max_n, MOD):
        fact = [1]*(max_n +1)
        for i in range(1, max_n +1):
            fact[i] = fact[i-1] *i % MOD
        inv_fact = [1]*(max_n +1)
        inv_fact[max_n] = pow(fact[max_n], MOD -2, MOD)
        for i in range(max_n,0,-1):
            inv_fact[i-1] = inv_fact[i] *i % MOD
        return fact, inv_fact

    def comb_mod(n, k, fact, inv_fact):
        if k <0 or k >n:
            return 0
        return fact[n] * inv_fact[k] % MOD * inv_fact[n -k] % MOD

    data = input.strip().split()
    T = int(data[0])
    test_cases = []
    idx =1
    max_n =0
    for _ in range(T):
        N = int(data[idx])
        M1 = int(data[idx +1])
        M2 = int(data[idx +2])
        H = int(data[idx +3])
        Sigma = int(data[idx +4])
        test_cases.append( (N, M1, M2, H, Sigma) )
        max_n = max(max_n, N)
        idx +=5
    # Precompute factorials up to 2*max_n
    max_fact = max_n *2
    fact, inv_fact = precompute_factorials(max_fact, MOD)

    results = []
    for t in range(1, T+1):
        N, M1, M2, H, Sigma = test_cases[t-1]
        if H > N:
            sum_pairs =0
            results.append(f"Case #{t}: {sum_pairs}")
            continue
        C_N_H = comb_mod(N, H, fact, inv_fact)
        pow_Sigm1_H = pow(Sigma -1, H, MOD)
        pow_Sigma_N = pow(Sigma, N, MOD)
        sum_pairs = C_N_H * pow_Sigm1_H % MOD
        sum_pairs = sum_pairs * pow_Sigma_N % MOD

        # Compute F correctly
        F =0
        w_max = min(M1, M2, N - H)
        for w in range(0, w_max +1):
            C_NH_w = comb_mod(N - H, w, fact, inv_fact)
            # Calculate t bounds
            t_low = max(H - M1 + w, 0)
            t_high = min(M2 - w, H)
            if t_low > t_high:
                continue
            # Compute sum_t = sum_{t=t_low}^{t_high} C(H,t) * (Sigma -1)^{H -t}
            sum_t =0
            for t_val in range(t_low, t_high +1):
                C_H_t = comb_mod(H, t_val, fact, inv_fact)
                term = C_H_t * pow(Sigma -1, H - t_val, MOD) % MOD
                sum_t = (sum_t + term) % MOD
            F = (F + C_NH_w * sum_t) % MOD
        total_sum = sum_pairs * F % MOD
        results.append(f"Case #{t}: {total_sum}")
    return '\n'.join(results)