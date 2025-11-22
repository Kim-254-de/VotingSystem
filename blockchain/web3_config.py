from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to local Ganache or remote node
WEB3_PROVIDER = os.getenv("WEB3_PROVIDER")  # e.g. http://127.0.0.1:7545
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # admin's key
PUBLIC_ADDRESS = os.getenv("PUBLIC_ADDRESS")

web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))

# Load compiled contract ABI
import json
with open("blockchain/contracts/VotingABI.json") as f:
    abi = json.load(f)

contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
