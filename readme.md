# Bitcoin Scripting Assignment

This repository contains the implementation and analysis of Bitcoin transaction scripting using both Legacy (P2PKH) and SegWit (P2SH-P2WPKH) address formats.
## Team Name
**Team_btc**
## Team Members

| Name | Roll No. |
|------|----------|
| Ayush Kumar | 230001012 |
| Hemsai | 230001079 |
| Shubham Prajapati | 230005047 |

## Overview

This project demonstrates the process of creating and validating Bitcoin transactions using different address formats. The implementation includes:

1. Creating and funding addresses
2. Creating transactions between addresses
3. Analyzing transaction scripts
4. Comparing Legacy and SegWit transactions

## Prerequisites

- Bitcoin Core (bitcoind)
- Python 3.x
- Bitcoin CLI (bitcoin-cli)
- Bitcoin Debugger (btcdeb)

## Setup Instructions

### 1. Install Bitcoin Core

Download and install Bitcoin Core from the [official website](https://bitcoin.org/en/download).

### 2. Configure Bitcoin Core

Create or update your `bitcoin.conf` file in the following location:
- Windows: `C:\Users\<username>\AppData\Roaming\Bitcoin\bitcoin.conf`
- Linux: `~/.bitcoin/bitcoin.conf`
- macOS: `~/Library/Application Support/Bitcoin/bitcoin.conf`

Add the following configuration settings:

```
regtest=1
rpcuser=username
rpcpassword=password
paytxfee=0.0001
fallbackfee=0.0002
mintxfee=0.00001
txconfirmtarget=1
```

### 3. Start Bitcoin Daemon

Start the Bitcoin daemon in regtest mode:

```bash
bitcoind -regtest
```

### 4. Install Python Dependencies

Install the required Python libraries:

```bash
pip install python-bitcoinrpc
```

## Project Structure

```
└── bitcoin-scripting/
    ├── Legacy1.py       # Generate Legacy addresses and transaction from A to B
    ├── Legacy2.py       # Create transaction from B to C with Legacy addresses
    ├── Segwit1.py       # Generate SegWit addresses and transaction from A to B
    ├── Segwit2.py       # Create transaction from B to C with SegWit addresses
    ├── bitcoin.conf     # Bitcoin Core configuration
    └── readme.md        # This file
```

## Running the Project

The scripts must be run in a specific order to ensure proper transaction flow:

### Part 1: Legacy Address Transactions

#### Step 1: Generate addresses and create A → B transaction

```bash
python Legacy1.py
```

This script will:
- Connect to bitcoind using RPC
- Create a wallet (if it doesn't exist)
- Generate three Legacy addresses (A, B, C)
- Fund address A with 10 BTC
- Create and broadcast a transaction from A to B
- Extract and save the challenge script for B

The script will create these files:
- `Legacy_addresses.json`: Contains all generated addresses
- `Legacy_CS.txt`: Contains the challenge script for address B

#### Step 2: Create B → C transaction

```bash
python Legacy2.py
```

This script will:
- Load the previously generated addresses
- Retrieve UTXO for address B
- Create and broadcast a transaction from B to C
- Extract and save the response script
- Save the transaction details for analysis

The script will create this file:
- `RS_legacy.txt`: Contains the response script from B to C transaction

### Part 2: SegWit Address Transactions

#### Step 1: Generate addresses and create A' → B' transaction

```bash
python Segwit1.py
```

This script will:
- Connect to bitcoind using RPC
- Generate three P2SH-SegWit addresses (A', B', C')
- Fund address A' with 10 BTC
- Create and broadcast a transaction from A' to B'
- Extract and save the challenge script for B'

The script will create these files:
- `segwit_addresses.json`: Contains all generated SegWit addresses
- `CS_segwit.txt`: Contains the challenge script for address B'

#### Step 2: Create B' → C' transaction

```bash
python Segwit2.py
```

This script will:
- Load the previously generated SegWit addresses
- Retrieve UTXO for address B'
- Create and broadcast a transaction from B' to C'
- Extract and save the response script and witness data
- Save the transaction details for analysis

The script will create this file:
- `RS_segwit.txt`: Contains the response script from B' to C' transaction

## Interactive Features

When running the scripts, you will be prompted to:
1. Enter the amount to transfer between addresses
2. Confirm transactions

## Transaction Analysis

### Legacy P2PKH Transactions

Transaction IDs (sample from provided code):
- A -> B: Generated during execution of Legacy1.py
- B -> C: Generated during execution of Legacy2.py

### SegWit P2SH-P2WPKH Transactions

Transaction IDs (sample from provided code):
- A' -> B': Generated during execution of Segwit1.py
- B' -> C': Generated during execution of Segwit2.py

## Bitcoin Script Debugging


For debugging scripts on the remote server:

```bash
# SSH login
ssh guest@10.206.4.201
# Password: root1234

# Debugging a script
btcdeb -v '{ResponseScript}{ChallengeScript}'
# for Steps
step
# One step operation gives one step
```

## Troubleshooting

1. **RPC Connection Error**:
   - Ensure bitcoind is running
   - Verify rpcuser and rpcpassword in bitcoin.conf
   - Check port (18443 for regtest)

2. **Wallet Already Loaded Error**:
   - The scripts handle this error automatically

3. **No UTXO Found Error**:
   - Ensure previous transaction was confirmed (generated at least one block)
   - Check that the correct address is being used

4. **Insufficient Funds Error**:
   - Check address balance using `bitcoin-cli -regtest getbalance`
   - Generate more blocks for coinbase maturity

## Transaction Size Comparison

From our analysis:

| Type | Transaction Size (Vbyte) | Transaction Size (Weight) |
|------|--------------------------|--------------------------|
| Legacy (P2PKH) | 225 | 900 |
| SegWit (P2SH-P2WPKH) | 166 | 661 |

SegWit transactions are smaller due to the segregation of witness data, leading to lower fees and improved scalability.

## Further Information

For more detailed analysis and explanation, please refer to the full report included in the repository.
