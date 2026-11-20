# Simulation model and equations

Four 20 MHz subchannels share fixed frames of duration `T = 1 ms`, with primary subchannel `P` at index 0 and secondaries `S1..S3` at indices 1..3. In the main sweep, `K` interference-eligible secondary blocks evolve as independent stationary two-state Markov chains with busy duty cycle `d` and lag-one autocorrelation `rho`, giving stationary mean busy count `K * d`.

Transition probabilities are `P(1 | 0) = d(1 - rho)` and `P(0 | 1) = (1 - d)(1 - rho)`. All policies perform immediate primary CCA at the start of every frame and probe secondary subchannels every `L` frames (`a = t mod L`). Given most recent probe state `b` at age `a`, the conditional clear probability on eligible secondary subchannels is `q(a | b) = 1 - d + (d - b) * rho^a`, and `q = 1` on non-eligible subchannels and on primary `P` after passing CCA.

Candidate masks in bit order `[P, S1, S2, S3]` are `1111` (80 MHz), `1011`, `1101`, `1110` (60 MHz single-hole non-OFDMA puncturing [9,10]), and `1000` (20 MHz primary fallback). Contiguous 40 MHz dynamic channel bonding (`1100`) is excluded to isolate single-hole puncturing against `Wait80` and `Fixed20`.

- `Wait80` transmits `1111` only when all latest secondary probes are clear, deferring otherwise.
- `Fixed20` transmits `1000` whenever primary CCA passes.
- `Greedy` selects the widest observed-clear mask and falls back to `1000` when two or more secondaries are observed busy.
- `AgeAware` maximizes `U(m, a) = (sum_k m_k r_k) * (prod_{k: m_k=1} q_k(a)) * (D_score(m) / T)` over observed-clear masks, where:
  `D_score(m) = T - (h_CCA + I_probe * h_probe + h_signal + I_punct(m) * h_punct + h_switch + h_AgeAware)`
  and `I_punct(m) = I[sum_k m_k == 3]` deducts `h_punct` only for the 60 MHz punctured masks (`1011`, `1101`, `1110`).

Realised frame overhead is `h_t = h_CCA + I_probe * h_probe + I_tx * h_signal + I_punct * h_punct + I_switch * h_switch + I_AgeAware * h_AgeAware`, where `I_switch = 1` only when the transmitted mask changes from the previous active transmission. Realised payload duration is `D_t = I_tx * (T - h_t)`, attempted payload is `A_t = 1000 * D_t * sum_k m_tk r_k` bits, and delivered payload `Y_t = A_t * I[all active blocks clear]` yields run goodput `G = sum_t Y_t / (1000 * N * T)` Mbps.
