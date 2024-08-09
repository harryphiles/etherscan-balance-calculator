import json
from typing import Any
from etherscan_api import EtherscanAPI


def store_as_json(file_name: str, data: list[list[Any]]) -> None:
    with open(file_name, "w") as f:
        json.dump(data, f, indent=2)


def merge_transactions_chronologically(normal, internal):
    len_normal, len_internal = len(normal), len(internal)
    i = j = 0
    result = []

    while i < len_normal and j < len_internal:
        if int(normal[i]["timeStamp"]) <= int(internal[j]["timeStamp"]):
            result.append({**normal[i], "transaction_type": "normal"})
            i += 1
        else:
            result.append({**internal[j], "transaction_type": "internal"})
            j += 1

    # Add remaining transactions using list comprehensions
    result.extend([{**t, "transaction_type": "normal"} for t in normal[i:]])
    result.extend([{**t, "transaction_type": "internal"} for t in internal[j:]])

    return result


def test_tokens(etherscan: EtherscanAPI, address):
    tx_erc20 = etherscan.get_transactions("erc20", address)
    tx_erc721 = etherscan.get_transactions("erc721", address)
    tx_erc1155 = etherscan.get_transactions("erc1155", address)
    if tx_erc20:
        print(f"{len(tx_erc20) = }")
        store_as_json("tx_erc20.json", tx_erc20)
        ether_used_erc20 = etherscan.calculate_ether_used_for_token_transfer(
            address, tx_erc20
        )
        print(f"{ether_used_erc20 = }")
    if tx_erc721:
        print(f"{len(tx_erc721) = }")
        store_as_json("tx_erc20.json", tx_erc721)
        ether_used_erc721 = etherscan.calculate_ether_used_for_token_transfer(
            address, tx_erc721
        )
        print(f"{ether_used_erc721 = }")
    if tx_erc1155:
        print(f"{len(tx_erc1155) = }")
        store_as_json("tx_erc20.json", tx_erc1155)
        ether_used_erc1155 = etherscan.calculate_ether_used_for_token_transfer(
            address, tx_erc1155
        )
        print(f"{ether_used_erc1155 = }")


def etherscan_test(etherscan: EtherscanAPI, address):
    api_balance = etherscan.get_eth_balance(address)

    tx_normal = etherscan.get_transactions("normal", address)
    if tx_normal:
        print(f"{len(tx_normal)   = }")
        # store_as_json("tx_normal.json", tx_normal)
    tx_internal = etherscan.get_transactions("internal", address)
    if tx_internal:
        print(f"{len(tx_internal) = }")
        # store_as_json("tx_internal.json", tx_internal)

    merged = merge_transactions_chronologically(tx_normal, tx_internal)
    print(f"{len(merged)      = }")
    calculate_merged = etherscan.calculate_merged(address, merged)
    sum_normal = etherscan.calculate_accumulated(address, tx_normal, "normal")
    sum_internal = etherscan.calculate_accumulated(address, tx_internal, "internal")

    calculated_balance = sum_normal + sum_internal

    print(f"{api_balance        = }")
    print(f"{calculated_balance = }")
    print(f"{sum_normal         = }")
    print(f"{sum_internal       = }")
    print(f"{calculate_merged   = }")

    # assert api_balance == calculated_balance


# Example usage
if __name__ == "__main__":
    from config import ETHERSCAN_API_KEY

    etherscan = EtherscanAPI(ETHERSCAN_API_KEY)
    # works
    # address = "0x63be42b40816eB08F6Ea480e5875E6F4668da379"
    # address = "0x6B300C1Aa4a9a91758f20C57861Ed8AB2b2540F6"
    address = "0x9a77D0900323b5F2b6cfF6138569846406cf7456"

    # Functions
    # test_new_func(etherscan, address)
    etherscan_test(etherscan, address)

    # test_tokens(etherscan, address)
