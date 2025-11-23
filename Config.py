

data_scale = 10           # Total number of unique data items
data_size = 1024          # Size of data file in Bytes
es_scale = 10             # Number of edge servers

corrupted_edge_ratio = 0.2  # Ratio of servers with corruption
corrupted_data_ratio = 0.3  # Ratio of corrupted files on bad servers


k = 5                     # Max combinations to try
beta = 0.5                # Selection Weight (0.5 = Balanced Coverage/Rep)
PRIME_MODULUS = 99999989  # rho


REP_INC_SUCCESS   = 1.0   # g_succ (Increase for verified data)
REP_DEC_MISMATCH  = 0.5   # p_mis  (Decrease for ambiguous mismatch)
REP_DEC_INITIATOR = 1.0   # p_init (Decrease for Initiator after k failures)


GAMMA = 0.8               # Reward share: 80% to Success Combo, 20% to Failed