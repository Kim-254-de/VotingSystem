import logging
from .web3_config import web3, contract, PRIVATE_KEY, PUBLIC_ADDRESS
from web3.exceptions import TransactionNotFound, ContractLogicError
from eth_account.messages import encode_defunct

logger = logging.getLogger(__name__)

def cast_vote(voter_address: str, candidate_id: int) -> str:
    try:
        # Validate candidate_id
        if not isinstance(candidate_id, int) or candidate_id < 0:
            raise ValueError("Invalid candidate ID")

        # Ensure connection is active
        if not web3.is_connected():
            raise ConnectionError("Web3 provider is not connected.")

        # Use current nonce to avoid tx collision
        nonce = web3.eth.get_transaction_count(PUBLIC_ADDRESS)

        # Check if voter has already voted via smart contract call
        has_voted = contract.functions.hasVoted(voter_address).call()
        if has_voted:
            raise Exception("This address has already voted.")

        # Build transaction
        txn = contract.functions.vote(candidate_id).build_transaction({
            'from': PUBLIC_ADDRESS,
            'nonce': nonce,
            'gas': 200000,  # Optional: call estimate_gas here
            'gasPrice': web3.to_wei('5', 'gwei'),
        })

        # Sign transaction securely
        signed_txn = web3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)

        # Send transaction
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Log the tx
        logger.info(f"Vote transaction sent: {web3.to_hex(tx_hash)}")

        return web3.to_hex(tx_hash)

    except ContractLogicError as e:
        logger.error(f"Smart contract rejected the vote: {str(e)}")
        raise

    except ValueError as e:
        logger.error(f"Invalid input or transaction data: {str(e)}")
        raise

    except Exception as e:
        logger.exception("Unhandled exception during vote casting")
        raise
