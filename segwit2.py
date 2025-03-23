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


try:
    with open("segwit_addresses.json", "r") as f:
        addresses = json.load(f)
    addr_B_prime = addresses["B_prime"]
    addr_C_prime = addresses["C_prime"]
    print_separator()
    print("Loaded segwit addresses from file:")
    print(f"Address B': {addr_B_prime}")
    print(f"Address C': {addr_C_prime}")
except FileNotFoundError:
    raise Exception("segwit_addresses.json not found. Please run Program 1 first to generate and save addresses.")


rpc_user = "Team_btc"
rpc_password = "Team_btc"
wallet_name = "Team_btc"
base_url = f"http://{rpc_user}:{rpc_password}@127.0.0.1:18443"

print_separator()
print("Loading wallet...")

rpc = authproxy.AuthServiceProxy(base_url)
try:
    rpc.loadwallet(wallet_name)
    print(f"Wallet '{wallet_name}' loaded successfully.")
except authproxy.JSONRPCException as e:
    if e.error['code'] == -35:
        print(f"Wallet '{wallet_name}' is already loaded.")
    else:
        raise

rpc = authproxy.AuthServiceProxy(f"{base_url}/wallet/{wallet_name}")


print_separator()
print(f"Retrieving UTXO for Address B' ({addr_B_prime})...")

utxos_B_prime = rpc.listunspent(1, 9999999, [addr_B_prime])
if not utxos_B_prime:
    raise Exception("No UTXO found for Address B'.")
utxo_B_prime = utxos_B_prime[0]
available_amount_B = float(utxo_B_prime["amount"])
print(f"Available amount in Address B': {available_amount_B:.8f} BTC")

transfer_amount_BtoC = get_input_amount(available_amount_B, "Enter amount to transfer from B' to C'")
fee_estimate = 0.0001  
if transfer_amount_BtoC + fee_estimate > available_amount_B:
    raise Exception("Transfer amount plus fee exceeds available amount in Address B'.")

raw_tx_B_prime_to_C_prime = rpc.createrawtransaction(
    [{"txid": utxo_B_prime["txid"], "vout": utxo_B_prime["vout"]}],
    {addr_C_prime: transfer_amount_BtoC, addr_B_prime: available_amount_B - transfer_amount_BtoC - fee_estimate}
)
signed_tx_B_prime_to_C_prime = rpc.signrawtransactionwithwallet(raw_tx_B_prime_to_C_prime)
txid_B_prime_to_C_prime = rpc.sendrawtransaction(signed_tx_B_prime_to_C_prime["hex"])
mining_addr = rpc.getnewaddress()
rpc.generatetoaddress(1, mining_addr)

print_separator()
print(f"TxID (B' -> C'): {txid_B_prime_to_C_prime}")

decoded_tx_B_prime_to_C_prime = rpc.decoderawtransaction(signed_tx_B_prime_to_C_prime["hex"])
response_script_sig = decoded_tx_B_prime_to_C_prime["vin"][0]["scriptSig"]["hex"]
response_witness = decoded_tx_B_prime_to_C_prime["vin"][0].get("txinwitness", [])

print("\n--- Response Script (Unlocking Data) ---")
print(f"ScriptSig (redeemScript): {response_script_sig}")
print(f"Witness: {response_witness}")

decoded_response = rpc.decodescript(response_script_sig)
print("Decoded Response Script:")
print(json.dumps(decoded_response, indent=4))

with open("RS_segwit.txt", "w") as f:
    f.write(response_script_sig)
print("Response script saved to 'RS_segwit.txt'.")


print_separator()
print("Unloading wallet...")
rpc_unload = authproxy.AuthServiceProxy(base_url)
rpc_unload.unloadwallet(wallet_name)
print(f"Wallet '{wallet_name}' unloaded successfully.")
print_separator()
