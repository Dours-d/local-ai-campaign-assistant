
from eth_account import Account
import base58
import hashlib

def eth_to_tron(eth_address):
    # Remove '0x' prefix
    address_bytes = bytes.fromhex(eth_address[2:])
    # Add 0x41 prefix (Tron mainnet)
    prefixed_address = b'\x41' + address_bytes
    
    # Base58Check encoding:
    # 1. Double SHA256 for checksum
    checksum = hashlib.sha256(hashlib.sha256(prefixed_address).digest()).digest()[:4]
    # 2. Append checksum and encode
    return base58.b58encode(prefixed_address + checksum).decode()

Account.enable_unaudited_hdwallet_features()
mnemonic = "test test test test test test test test test test test junk"
path = "m/44'/195'/0'/0/0" # Tron path
acct = Account.from_mnemonic(mnemonic, account_path=path)
print(f"Eth-style address: {acct.address}")
print(f"Tron-style address: {eth_to_tron(acct.address)}")
