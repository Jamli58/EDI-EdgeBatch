# EdgeBatch Implementation
This repository contains the source code for the paper "EdgeBatch: Efficient Decentralized Batch Verification for Edge Data Integrity via Reputation-Aware Combination Selection".

## Note on Implementation:
The experimental results in the paper regarding network latency and throughput were derived from a deployment on Hyperledger Fabric v3.0.0.

However, to facilitate easy reproducibility of the core contributions (the CSA Algorithm, Reputation Logic, and Batch Verification flow) without requiring the installation of a complex enterprise blockchain environment (Docker, Kubernetes, Fabric SDKs), this repository provides a Python-native implementation.

This version accurately simulates the protocol logic and mathematical proofs found in the manuscript. The blockchain network delays observed in our physical testbed are modeled here as processing overheads to replicate the timing results.

## Project Structure

*   `EdgeBatch.py`: The core protocol implementation (Initiator, Smart Contract, Verifiers).
*   `GenRanData.py`: A simulation script that generates synthetic data, distributes it with "partial coverage," and introduces random corruption based on faulty node ratios.
*   `Config.py`: System parameters (data_scale, egde_scale, block_size, etc.).
*   `Tools.py`: I/O utilities.


## Prerequisites
Python 3.8+
## How to Run
Generate Data: Run the data generator to create the ground truth and corrupted edge servers.
```
python GenRanData.py
```
Run Protocol: Execute the main protocol simulation.
```
python3 EdgeBatch.py
```
## Parameters
You can modify data_scale, edge_scale, etc. in `Config.py`.


