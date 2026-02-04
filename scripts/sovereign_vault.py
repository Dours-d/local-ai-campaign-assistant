
import os
import json
from eth_account import Account
from dotenv import load_dotenv

# Allow HD Wallet features (required for derivation from mnemonic)
Account.enable_unaudited_hdwallet_features()

VAULT_MAPPING = "data/vault_mapping.json"
DOTENV_PATH = ".env"

class SovereignVault:
    def __init__(self):
        load_dotenv(DOTENV_PATH)
        self.mnemonic = os.getenv("VAULT_MNEMONIC")
        
        if not self.mnemonic:
            # Generate a new secure mnemonic if none exists
            print("!!! NO VAULT MNEMONIC FOUND !!!")
            print("Generating a new Sovereign Root. This is the master key for all beneficiary funds.")
            new_acct, mnemonic = Account.create_with_mnemonic()
            self.mnemonic = mnemonic
            
            # Save to .env
            with open(DOTENV_PATH, "a") as f:
                if os.path.getsize(DOTENV_PATH) > 0:
                    f.write("\n")
                f.write(f"VAULT_MNEMONIC=\"{self.mnemonic}\"")
            
            print("--- IMPORTANT: SAVE THIS MNEMONIC SECURELY ---")
            print(f"ROOT_SEED: {self.mnemonic}")
            print("---------------------------------------------")

        self.mapping = {}
        if os.path.exists(VAULT_MAPPING):
            try:
                with open(VAULT_MAPPING, 'r') as f:
                    self.mapping = json.load(f)
            except json.JSONDecodeError:
                self.mapping = {}

    def get_address(self, beneficiary_id):
        """
        Returns a unique, provisioned USDT address for a beneficiary.
        Enforces a 1-person-1-address policy.
        """
        if beneficiary_id in self.mapping:
            return self.mapping[beneficiary_id]["address"]
        return None

    def register_external_address(self, beneficiary_id, address):
        """
        Manually register an existing self-custody address for a beneficiary.
        """
        self.mapping[beneficiary_id] = {
            "address": address,
            "status": "Self-Custody",
            "network": "USDT-External"
        }
        self.save_mapping()

    def provision_new_address(self, beneficiary_id):
        """
        Derives a new HD wallet address at the next available index.
        """
        if beneficiary_id in self.mapping:
            return self.mapping[beneficiary_id]["address"]

        # Derive new address at the next available index
        index = len(self.mapping)
        path = f"m/44'/60'/0'/0/{index}"
        
        try:
            acct = Account.from_mnemonic(self.mnemonic, account_path=path)
            self.mapping[beneficiary_id] = {
                "address": acct.address,
                "index": index,
                "path": path,
                "status": "Provisional",
                "network": "USDT-ERC20/BEP20/Polygon"
            }
            self.save_mapping()
            return acct.address
        except Exception as e:
            print(f"Error deriving address: {e}")
            return None

    def save_mapping(self):
        os.makedirs(os.path.dirname(VAULT_MAPPING), exist_ok=True)
        with open(VAULT_MAPPING, 'w', encoding='utf-8') as f:
            json.dump(self.mapping, f, indent=2)

if __name__ == "__main__":
    vault = SovereignVault()
    print("Sovereign Vault Initialized.")
    # Example usage:
    # addr = vault.get_address("Test-User-001")
    # print(f"Provisioned Address: {addr}")
