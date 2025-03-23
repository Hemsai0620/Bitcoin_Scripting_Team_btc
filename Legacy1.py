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


rpc_user = "Team_btc" # username
rpc_password = "Team_btc" #password
base_url = f"http://{rpc_user}:{rpc_password}@127.0.0.1:18443"
wallet_name = "Team_btc"  #wallet name

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
print("Wallet and fee configuration complete.")


print_separator()
print("Generating legacy addresses for A, B, and C...")

addr_A = rpc.getnewaddress("A", "legacy")
addr_B = rpc.getnewaddress("B", "legacy")
addr_C = rpc.getnewaddress("C", "legacy")

print(f"Address A: {addr_A}")
print(f"Address B: {addr_B}")
print(f"Address C: {addr_C}")

addresses = {"A": addr_A, "B": addr_B, "C": addr_C}
with open("Legacy_addresses.json", "w") as f:
    json.dump(addresses, f)


mining_address = rpc.getnewaddress()
rpc.generatetoaddress(101, mining_address)


print_separator()
print("Funding Address A with 10 BTC...")
txid_fund_A = rpc.sendtoaddress(addr_A, 10)
print(f"Transaction ID (Funding A): {txid_fund_A}")
mining_address = rpc.getnewaddress()
rpc.generatetoaddress(1, mining_address)
print("10 BTC has been added to address A.")


print_separator()
print("Creating transaction from A -> B...")


utxos_A = rpc.listunspent(1, 9999999, [addr_A])
if not utxos_A:
    raise Exception("No UTXO found for address A.")
utxo_A = utxos_A[0]
available_amount_A = float(utxo_A["amount"])
print(f"Available amount in Address A: {available_amount_A:.8f} BTC")


transfer_amount_AtoB = get_input_amount(available_amount_A, "Enter amount to transfer from A to B")
fee_estimate = 0.0001  
if transfer_amount_AtoB + fee_estimate > available_amount_A:
    raise Exception("Transfer amount plus fee exceeds available amount in Address A.")


raw_tx_A_to_B = rpc.createrawtransaction(
    [{"txid": utxo_A["txid"], "vout": utxo_A["vout"]}],
    {addr_B: transfer_amount_AtoB, addr_A: available_amount_A - transfer_amount_AtoB - fee_estimate}
)
decoded_tx_A_to_B = rpc.decoderawtransaction(raw_tx_A_to_B)
script_pubkey_B = decoded_tx_A_to_B["vout"][0]["scriptPubKey"]["hex"]


signed_tx_A_to_B = rpc.signrawtransactionwithwallet(raw_tx_A_to_B)
txid_A_to_B = rpc.sendrawtransaction(signed_tx_A_to_B["hex"])
mining_address = rpc.getnewaddress()
rpc.generatetoaddress(1, mining_address)

print(f"\nTxID (A -> B): {txid_A_to_B}")
print(f"Challenge Script (ScriptPubKey for B): {script_pubkey_B}")


decoded_challenge = rpc.decodescript(script_pubkey_B)
print("Decoded Challenge Script:")
print(json.dumps(decoded_challenge, indent=4))


with open("Legacy_CS.txt", "w") as f:
    f.write("Challenge Script: " + script_pubkey_B)
print("Challenge script saved to 'Legacy_CS.txt'.")

print_separator()
print("Unloading wallet...")
rpc_unload = authproxy.AuthServiceProxy(base_url)
rpc_unload.unloadwallet(wallet_name)
print(f"Wallet '{wallet_name}' unloaded successfully.")
print_separator()
