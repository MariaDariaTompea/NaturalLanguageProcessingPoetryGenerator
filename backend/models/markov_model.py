import numpy as np
from collections import defaultdict

class CMPPoet:
    def __init__(self, corpus_lines):
        """Initializes the Markov Process M"""
        self.vocab = sorted(list(set(" ".join(corpus_lines).split())))
        self.w2i = {w: i for i, w in enumerate(self.vocab)}
        self.i2w = {i: w for w, i in self.w2i.items()}
        self.n = len(self.vocab)
        
        self.M = np.zeros((self.n, self.n))
        self.prior = np.zeros(self.n)
        self._build_model(corpus_lines)

    def _build_model(self, lines):
        """Maximum-likelihood estimation for style capturing"""
        for line in lines:
            tokens = line.split()
            if not tokens: continue
            self.prior[self.w2i[tokens[0]]] += 1
            for i in range(len(tokens)-1):
                self.M[self.w2i[tokens[i]], self.w2i[tokens[i+1]]] += 1
        
        self.prior /= (self.prior.sum() + 1e-9)
        sums = self.M.sum(axis=1)
        self.M = np.divide(self.M, sums[:, None], where=sums[:, None]!=0)

    def generate_line(self, L, constraints):
        """CMP Algorithm: Filtering -> Back-prop -> Renormalization"""
        Z = [self.M.copy() for _ in range(L - 1)]
        Z_prior = self.prior.copy()

        # Step 1: Filtering
        for pos, allowed in constraints.items():
            allowed_idx = [self.w2i[w] for w in allowed if w in self.w2i]
            mask = np.ones(self.n, dtype=bool)
            mask[allowed_idx] = False
            if pos == 0: Z_prior[mask] = 0
            else: Z[pos-1][:, mask] = 0

        # Step 2: Back-propagation of Alphas
        alphas = [np.zeros(self.n) for _ in range(L)]
        alphas[L-1] = np.ones(self.n)
        for i in range(L-2, -1, -1):
            alphas[i] = Z[i] @ alphas[i+1]

        # Step 3: Generation
        line = []
        p0 = Z_prior * (Z[0] @ alphas[1] if L > 1 else 1)
        if p0.sum() == 0: return "Constraint Satisfaction Failed."
        
        curr_idx = np.random.choice(self.n, p=p0/p0.sum())
        line.append(self.i2w[curr_idx])
        for i in range(L-1):
            prob_row = Z[i][curr_idx] * alphas[i+1]
            curr_idx = np.random.choice(self.n, p=prob_row/prob_row.sum())
            line.append(self.i2w[curr_idx])
        return " ".join(line)