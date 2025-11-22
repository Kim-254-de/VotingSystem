import os
import json
from web3 import Web3
from dotenv import load_dotenv
from web3.middleware import geth_poa_middleware

# Load environment variables
load_dotenv()

# Securely access environment variables
WEB3_PROVIDER = os.getenv("WEB3_PROVIDER")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_ADDRESS = os.getenv("PUBLIC_ADDRESS")

# Setup Web3
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))

# If using a PoA network (e.g., Hardhat, Ganache), enable middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Load ABI
ABI_PATH = os.path.join(os.path.dirname(__file__), 'VotingABI.json')
with open(ABI_PATH) as abi_file:
    abi = json.load(abi_file)

# Contract instance
contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)

# -------------------------
# Read Functions (Safe)
# -------------------------

def get_total_candidates():
    try:
        return contract.functions.getCandidateCount().call()
    except Exception as e:
        print(f"[Error] get_total_candidates: {e}")
        return None

def get_candidate_details(index):
    try:
        return contract.functions.getCandidate(index).call()
    except Exception as e:
        print(f"[Error] get_candidate_details: {e}")
        return None

def has_voted(voter_address):
    try:
        return contract.functions.hasVoted(Web3.to_checksum_address(voter_address)).call()
    except Exception as e:
        print(f"[Error] has_voted: {e}")
        return None

# -------------------------
# Write Functions (Requires Signing)
# -------------------------

def vote(candidate_id):
    try:
        nonce = w3.eth.get_transaction_count(PUBLIC_ADDRESS)

        txn = contract.functions.vote(candidate_id).build_transaction({
            'chainId': w3.eth.chain_id,
            'gas': 300000,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
        })

        signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt
    except Exception as e:
        print(f"[Error] vote: {e}")
        return None

# -------------------------
# Utility: Contract Status
# -------------------------

def is_contract_alive():
    try:
        # Simple call to verify contract availability
        _ = contract.functions.getCandidateCount().call()
        return True
    except Exception:
        return False
