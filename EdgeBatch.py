import hashlib
import time
from Config import * 
from Tools import read_data_from_server

class EdgeServer:
    def __init__(self, server_id):
        self.server_id = server_id
        self.data_cache = read_data_from_server(server_id)
        # Initialize Reputation with 1.0 (Neutral)
        self.data_reputation = {filename: 1.0 for filename in self.data_cache}
        self.last_verified_time = 0 

    def get_timeliness_score(self, current_time):
        T_i = current_time - self.last_verified_time
        return 1.0 / (1.0 + T_i)

    def generate_proof(self, assigned_items, rho):
        proof_sum = 0
        print(f"    [S{self.server_id}] Hashing {len(assigned_items)} items...")
        for item_name in assigned_items:
            if item_name in self.data_cache:
                content = self.data_cache[item_name]
                h_int = int(hashlib.sha256(content).hexdigest(), 16)
                proof_sum = (proof_sum + h_int) % rho
            else:
                print(f"    [ERROR] Server {self.server_id} MISSING {item_name}!")
        return proof_sum

    def respond_to_invitation(self, target_files):
        available = [f for f in target_files if f in self.data_cache]
        return self.server_id, set(available)

class SmartContract:
    def __init__(self, edge_servers):
        self.edge_servers = edge_servers 
        self.current_time = time.time()
        self.consensus_latency = 0.5 # Simulate Blocktime

    def csa_main(self, responses, target_files, k_limit):
        print(f"\n[CSA] Phase 1: Generating Combinations (Targeting k={k_limit})")
        top_combinations = []
        
        candidate_pool = []
        for sid, covered_set in responses:
            if covered_set:
                candidate_pool.append({
                    'id': sid, 'coverage': covered_set, 'obj': self.edge_servers[sid]
                })

        for i in range(k_limit):
            print(f"  [CSA] Iteration {i+1}: Searching pool of {len(candidate_pool)} candidates...")
            raw_combo = self.find_single_combination(candidate_pool, target_files)
            if not raw_combo: break 

            optimized_combo = self.optimize_combination(raw_combo, target_files)
            top_combinations.append(optimized_combo)
            
            used_ids = {s['id'] for s in optimized_combo}
            candidate_pool = [c for c in candidate_pool if c['id'] not in used_ids]
            if not candidate_pool: break

        top_combinations.sort(key=lambda c: self.calculate_objective_score(c, target_files), reverse=True)
        return top_combinations

    def find_single_combination(self, pool, target_files):
        current_combo = []
        remaining_items = set(target_files)
        working_pool = [p for p in pool]
        
        while remaining_items and working_pool:
            best_candidate = None
            best_score = -1
            
            for candidate in working_pool:
                delta = candidate['coverage'].intersection(remaining_items)
                if not delta: continue
                rep_sum = sum(candidate['obj'].data_reputation.get(d, 1.0) for d in delta)
                score = beta * len(delta) + (1 - beta) * rep_sum
                
                if score > best_score:
                    best_score = score
                    best_candidate = candidate
            
            if best_candidate:
                current_combo.append(best_candidate)
                remaining_items -= best_candidate['coverage']
                working_pool.remove(best_candidate)
            else:
                break
        
        return current_combo if not remaining_items else None

    def optimize_combination(self, combination, target_files):
        optimized = combination[:]
        target_set = set(target_files)
        changed = True
        while changed:
            changed = False
            for server in optimized:
                temp_combo = [s for s in optimized if s['id'] != server['id']]
                covered_union = set()
                for s in temp_combo: covered_union.update(s['coverage'])
                
                if target_set.issubset(covered_union):
                    curr_score = self.calculate_objective_score(optimized, target_files)
                    new_score = self.calculate_objective_score(temp_combo, target_files)
                    if new_score > curr_score:
                        optimized = temp_combo
                        changed = True
                        break 
        return optimized

    def calculate_objective_score(self, combination, target_files):
        if not combination: return 0
        n_size = len(combination)
        h_score = 1.0 - (n_size - 1) / max(1, (len(self.edge_servers) - 1))
        avg_timeliness = sum(s['obj'].get_timeliness_score(self.current_time) for s in combination) / n_size
        
        data_rep_sum = 0
        for item in target_files:
            candidates = [s['obj'] for s in combination if item in s['coverage']]
            if candidates:
                best_rep = max(s.data_reputation.get(item, 1.0) for s in candidates)
                data_rep_sum += best_rep
        
        r_score = (avg_timeliness + (data_rep_sum / len(target_files))) / 2.0
        return beta * h_score + (1 - beta) * r_score

    def assign_data_items(self, combination, target_files):
        assignments = {s['id']: [] for s in combination}
        for item in target_files:
            candidates = [s for s in combination if item in s['coverage']]
            best_s = max(candidates, key=lambda s: s['obj'].data_reputation.get(item, 0))
            assignments[best_s['id']].append(item)
        return assignments


    def execute_verification(self, initiator_id, target_files, initiator_proof):
        print(f"\n[VerSC] --- Starting Verification for Initiator {initiator_id} ---")
        time.sleep(self.consensus_latency) # Simulate Chain Latency

        responses = []
        for sid, srv in self.edge_servers.items():
            if sid == initiator_id: continue
            _, covered = srv.respond_to_invitation(target_files)
            if covered: responses.append((sid, covered))
        
        top_k_combos = self.csa_main(responses, target_files, k)
        if not top_k_combos:
            print("[Error] No valid combinations found.")
            return False

        match_found = False
        matching_index = -1
        
        print("\n[VerSC] Entering Iterative Verification Loop...")
        for idx, combo in enumerate(top_k_combos):
            server_ids = [s['id'] for s in combo]
            print(f"  >>> Attempt #{idx+1}: Combination {server_ids}")
            
            assignments = self.assign_data_items(combo, target_files)
            verifier_proofs_sum = 0
            
            for s_dict in combo:
                sid = s_dict['id']
                items = assignments[sid]
                if items:
                    p = s_dict['obj'].generate_proof(items, PRIME_MODULUS)
                    verifier_proofs_sum = (verifier_proofs_sum + p) % PRIME_MODULUS
            
            if verifier_proofs_sum == initiator_proof:
                print(f"    [RESULT] MATCH FOUND! Integrity Confirmed.")
                match_found = True
                matching_index = idx
                break
            else:
                print(f"    [RESULT] MISMATCH. Trying next combination...")

        self.apply_settlement(initiator_id, target_files, top_k_combos, match_found, matching_index)
        return match_found

    def apply_settlement(self, initiator_id, target_files, all_combos, success, match_idx):
        print(f"\n[VerSC] Phase 3: Settlement & Reputation Updates")
        initiator = self.edge_servers[initiator_id]

        if success:
            # --- SUCCESS CASE ---
            print(f"  [Settlement] Outcome: SUCCESS (Match at index {match_idx})")
            
            # 1. Update Initiator (+ g_succ)
            print(f"  [Update] Initiator {initiator_id} Rep INCREASED (+{REP_INC_SUCCESS})")
            for d in target_files:
                initiator.data_reputation[d] = min(initiator.data_reputation.get(d, 1) + REP_INC_SUCCESS, 10)

            # 2. Reward Matching Combo (+ g_succ)
            combo_match = all_combos[match_idx]
            assignments = self.assign_data_items(combo_match, target_files)
            
            print(f"  [Reward] Winner Combo: {[s['id'] for s in combo_match]}")
            for s_dict in combo_match:
                srv = s_dict['obj']
                srv.last_verified_time = self.current_time
                
                # Correct Update Loop using Config
                for d in assignments[s_dict['id']]:
                    old_val = srv.data_reputation.get(d, 1)
                    new_val = min(old_val + REP_INC_SUCCESS, 10)
                    srv.data_reputation[d] = new_val
                    print(f"    -> Server {srv.server_id} Rep [{d}]: {old_val:.1f} -> {new_val:.1f}")

            # 3. Penalize Previous Failed Combos (- p_mis)
            if match_idx > 0:
                print(f"  [Penalty] Penalizing {match_idx} failed combinations...")
                for i in range(match_idx):
                    failed_combo = all_combos[i]
                    assignments_f = self.assign_data_items(failed_combo, target_files)
                    
                    for s_dict in failed_combo:
                        srv = s_dict['obj']
                        for d in assignments_f[s_dict['id']]:
                            old_val = srv.data_reputation.get(d, 1)
                            # Apply p_mis
                            new_val = max(old_val - REP_DEC_MISMATCH, 0)
                            srv.data_reputation[d] = new_val
                            print(f"    -> Server {srv.server_id} Rep [{d}]: {old_val:.1f} -> {new_val:.1f} (-{REP_DEC_MISMATCH})")

        else:
            # --- FAILURE CASE (All k failed) ---
            print(f"  [Settlement] Outcome: TOTAL FAILURE")
            print(f"  [CONCLUSION] INITIATOR {initiator_id} IS CORRUPT.")
            
            # Penalize Initiator (- p_init)
            print(f"  [Penalty] Initiator {initiator_id} Rep decreased (-{REP_DEC_INITIATOR})")
            for d in target_files:
                old_val = initiator.data_reputation.get(d, 1)
                new_val = max(old_val - REP_DEC_INITIATOR, 0)
                initiator.data_reputation[d] = new_val
            
            print("  [Comp] Verifiers compensated (No Rep Penalty).")

class Initiator:
    def __init__(self, server_id, smart_contract):
        self.id = server_id
        self.sc = smart_contract
        
    def trigger_verification(self):
        my_server = self.sc.edge_servers[self.id]
        target_files = list(my_server.data_cache.keys())
        if not target_files: return
        my_proof = my_server.generate_proof(target_files, PRIME_MODULUS)
        self.sc.execute_verification(self.id, target_files, my_proof)

if __name__ == "__main__":
    servers = {i: EdgeServer(i) for i in range(1, es_scale + 1)}
    sc = SmartContract(servers)
    initiator_node = Initiator(1, sc)
    initiator_node.trigger_verification()