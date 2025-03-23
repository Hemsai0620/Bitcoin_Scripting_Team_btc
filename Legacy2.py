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


# Load Addresses from File

try:
    with open("Legacy_addresses.json", "r") as f:
        addresses = json.load(f)
    addr_B = addresses["B"]
    addr_C = addresses["C"]
    print_separator()
    print("Loaded addresses from file:")
    print(f"Address B: {addr_B}")
    print(f"Address C: {addr_C}")
except FileNotFoundError:
    raise Exception("addresses.json not found. Please run Program 1 first to generate and save addresses.")


rpc_user = "Team_btc"  #username
rpc_password = "Team_btc" #password
wallet_name = "Team_btc" #wallet name

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
print(f"Retrieving UTXO for Address B ({addr_B})...")


utxos_B = rpc.listunspent(1, 9999999, [addr_B])
if not utxos_B:
    raise Exception("No UTXO found for Address B.")
utxo_B = utxos_B[0]
available_amount_B = float(utxo_B["amount"])
print(f"Available amount in Address B: {available_amount_B:.8f} BTC")


transfer_amount_BtoC = get_input_amount(available_amount_B, "Enter amount to transfer from B to C")
fee_estimate = 0.0001  
if transfer_amount_BtoC + fee_estimate > available_amount_B:
    raise Exception("Transfer amount plus fee exceeds available amount in Address B.")


raw_tx_B_to_C = rpc.createrawtransaction(
    [{"txid": utxo_B["txid"], "vout": utxo_B["vout"]}],
    {addr_C: transfer_amount_BtoC, addr_B: available_amount_B - transfer_amount_BtoC - fee_estimate}
)
signed_tx_B_to_C = rpc.signrawtransactionwithwallet(raw_tx_B_to_C)
txid_B_to_C = rpc.sendrawtransaction(signed_tx_B_to_C["hex"])
mining_address = rpc.getnewaddress()
rpc.generatetoaddress(1, mining_address)

print_separator()
print(f"TxID (B -> C): {txid_B_to_C}")


decoded_tx_B_to_C = rpc.decoderawtransaction(signed_tx_B_to_C["hex"])
script_sig_hex = decoded_tx_B_to_C["vin"][0]["scriptSig"]["hex"]

print("Response Script (ScriptSig) for B -> C:")
print(f"Hex: {script_sig_hex}")


decoded_response = rpc.decodescript(script_sig_hex)
print("Decoded Response Script:")
print(json.dumps(decoded_response, indent=4))


with open("Legacy_RS.txt", "w") as f:
    f.write("Response Script: " + script_sig_hex)
print("Challenge script saved to 'Legacy_RS.txt'.")

print_separator()
print("Unloading wallet...")
rpc_unload = authproxy.AuthServiceProxy(base_url)
rpc_unload.unloadwallet(wallet_name)
print(f"Wallet '{wallet_name}' unloaded successfully.")
print_separator()
