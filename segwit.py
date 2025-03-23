import bitcoinrpc.authproxy as authproxy
import json

def print_separator():
    print("\n" + "-" * 60 + "\n")

def get_input_amount(max_amount, prompt_text="Enter amount: "):
    while True:
        try:
            amt = float(input(f"{prompt_text} (max {max_amount:.8f} BTC): "))
            if amt <= 0:
                print("Amount must be greater than 0.")
            elif amt > max_amount:
                print("Amount exceeds available funds. Please enter a smaller amount.")
            else:
                return amt
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

def calc_script_metrics(hex_script):
    script_bytes = bytes.fromhex(hex_script)
    size = len(script_bytes)
    weight = size * 4
    vsize = size
    return size, weight, vsize

rpc_user = "Team_btc"
rpc_password = "Team_btc"
base_url = f"http://{rpc_user}:{rpc_password}@127.0.0.1:18443"
wallet_name = "Team_btc"

print_separator()
print("Loading wallet...")

rpc = authproxy.AuthServiceProxy(base_url)
try:
    rpc.loadwallet(wallet_name)
    print(f"Wallet '{wallet_name}' loaded successfully.")
except authproxy.JSONRPCException as e:
    if e.error['code'] == -35:
        print(f"Wallet '{wallet_name}' is already loaded.")
    elif e.error['code'] == -18:
        print(f"Wallet '{wallet_name}' does not exist. Creating wallet.")
        rpc.createwallet(wallet_name)
        rpc = authproxy.AuthServiceProxy(f"{base_url}/wallet/{wallet_name}")
        mining_address = rpc.getnewaddress()
        rpc.generatetoaddress(101, mining_address)
    else:
        raise

rpc = authproxy.AuthServiceProxy(f"{base_url}/wallet/{wallet_name}")

print_separator()
print("Wallet loaded and configured using bitcoin.conf settings.")

print_separator()
print("Generating P2SH-SegWit addresses for A', B', and C'...")

addr_A_prime = rpc.getnewaddress("A'", "p2sh-segwit")
addr_B_prime = rpc.getnewaddress("B'", "p2sh-segwit")
addr_C_prime = rpc.getnewaddress("C'", "p2sh-segwit")

print(f"Address A': {addr_A_prime}")
print(f"Address B': {addr_B_prime}")
print(f"Address C': {addr_C_prime}")

addresses = {"A_prime": addr_A_prime, "B_prime": addr_B_prime, "C_prime": addr_C_prime}
with open("segwit_addresses.json", "w") as f:
    json.dump(addresses, f)

mining_addr = rpc.getnewaddress()
rpc.generatetoaddress(101, mining_addr)

print_separator()
print("Funding Address A' with 10 BTC...")
txid_fund_A_prime = rpc.sendtoaddress(addr_A_prime, 10)
print(f"Transaction ID (Funding A'): {txid_fund_A_prime}")
mining_addr = rpc.getnewaddress()
rpc.generatetoaddress(1, mining_addr)
print("10 BTC has been added to Address A'.")

print_separator()
print("Creating transaction from A' -> B'...")

utxos_A_prime = rpc.listunspent(1, 9999999, [addr_A_prime])
if not utxos_A_prime:
    raise Exception("No UTXO found for Address A'")
utxo_A_prime = utxos_A_prime[0]
available_amount_A = float(utxo_A_prime["amount"])
print(f"Available amount in Address A': {available_amount_A:.8f} BTC")

transfer_amount_AtoB = get_input_amount(available_amount_A, "Enter amount to transfer from A' to B'")
fee_estimate = 0.0001
if transfer_amount_AtoB + fee_estimate > available_amount_A:
    raise Exception("Transfer amount plus fee exceeds available amount in Address A'.")

raw_tx_A_prime_to_B_prime = rpc.createrawtransaction(
    [{"txid": utxo_A_prime["txid"], "vout": utxo_A_prime["vout"]}],
    {addr_B_prime: transfer_amount_AtoB, addr_A_prime: available_amount_A - transfer_amount_AtoB - fee_estimate}
)
decoded_tx_A_prime_to_B_prime = rpc.decoderawtransaction(raw_tx_A_prime_to_B_prime)
challenge_script = decoded_tx_A_prime_to_B_prime["vout"][0]["scriptPubKey"]["hex"]

signed_tx_A_prime_to_B_prime = rpc.signrawtransactionwithwallet(raw_tx_A_prime_to_B_prime)
txid_A_prime_to_B_prime = rpc.sendrawtransaction(signed_tx_A_prime_to_B_prime["hex"])
mining_addr = rpc.getnewaddress()
rpc.generatetoaddress(1, mining_addr)

print(f"\nTxID (A' -> B'): {txid_A_prime_to_B_prime}")
print(f"Challenge Script (scriptPubKey for B'): {challenge_script}")

decoded_challenge = rpc.decodescript(challenge_script)
print("Decoded Challenge Script:")
print(json.dumps(decoded_challenge, indent=4))
size_cs, weight_cs, vsize_cs = calc_script_metrics(challenge_script)
print(f"Challenge Script Size (bytes): {size_cs}")
print(f"Challenge Script Weight: {weight_cs}")
print(f"Challenge Script Virtual Size (vsize): {vsize_cs}")

with open("CS_segwit.txt", "w") as f:
    f.write(challenge_script)
print("Challenge script saved to 'CS_segwit.txt'.")

print_separator()
print("Unloading wallet...")
rpc_unload = authproxy.AuthServiceProxy(base_url)
rpc_unload.unloadwallet(wallet_name)
print(f"Wallet '{wallet_name}' unloaded successfully.")
print_separator()
