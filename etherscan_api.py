from decimal import Decimal
import requests


class EtherscanAPI:
    def __init__(self, api_key: str) -> None:
        self.base_url = "https://api.etherscan.io/api"
        self.api_key = api_key

    def get_eth_balance(self, address: str) -> float:
        """
        Get Ether Balance for a Single Address
        https://docs.etherscan.io/api-endpoints/accounts#get-ether-balance-for-a-single-address
        response = {
            "status":"1",
            "message":"OK",
            "result":"40891626854930000000000" -> unit in Wei (10^-18)
        }
        """
        params = {
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest",
            "apikey": self.api_key,
        }

        r = requests.get(self.base_url, params=params)
        r.raise_for_status()

        data = r.json()
        if data["status"] == "1":
            balance_wei = int(data["result"])
            return balance_wei / 10**18  # Convert Wei to Ether
        #     7877603157626932
        # 0.007877603157626933

    def get_transactions(
        self,
        transaction_type: str,
        address: str,
        startblock: int = 0,
        endblock: int = 99999999,
        sort: str = "asc",
    ) -> list[dict]:
        """
        Get a list of 'Normal' Transactions By Address
        https://docs.etherscan.io/api-endpoints/accounts#get-a-list-of-normal-transactions-by-address
        Get a list of 'ERC20 - Token Transfer Events' by Address
        """
        allowed_transactions = {
            "normal": "txlist",
            "internal": "txlistinternal",
            "erc20": "tokentx",
            "erc721": "tokennfttx",
            "erc1155": "token1155tx",
        }
        if transaction_type not in allowed_transactions:
            raise KeyError("Check allowed transaction types.")
        params = {
            "module": "account",
            "action": allowed_transactions[transaction_type],
            "address": address,
            "startblock": startblock,
            "endblock": endblock,
            "sort": sort,
            "apikey": self.api_key,
        }

        all_results = []
        page = 1

        while True:
            params["page"] = page
            r = requests.get(self.base_url, params=params)
            r.raise_for_status()

            data = r.json()

            if data["status"] != "1":
                break

            results = data["result"]
            all_results.extend(results)

            # Check if we've reached the last page
            if len(results) < 10_000:  # Assuming 10000 is the max results per page
                break

            page += 1

        return all_results

    def calculate_merged(self, address: str, merged_data) -> float:
        """Calculate the accumulated balance change for an Ethereum address."""
        sum = Decimal("0")

        for transaction in merged_data:
            transaction_type = transaction.get("transaction_type")
            if transaction_type not in {"normal", "internal"}:
                raise KeyError(f"Unknown transaction type: {transaction_type}")

            # "from" this address -> subtract value
            if transaction.get("from", "").lower() == address.lower():
                if transaction.get("isError") == "0":
                    sum -= Decimal(transaction.get("value", "0"))
                if transaction_type == "normal":
                    sum -= Decimal(transaction.get("gasPrice", "0")) * Decimal(transaction.get("gasUsed", "0"))

            # "to" this address -> add value (only if transaction succeeded)
            if (
                transaction.get("to", "").lower() == address.lower()
                and transaction.get("isError") == "0"
            ):
                sum += Decimal(transaction.get("value", "0"))

        return float(sum) / 10**18  # Convert wei to Ether

    def calculate_accumulated(self, address: str, data, transaction_type: str) -> float:
        """Calculate the accumulated balance change for an Ethereum address."""
        if transaction_type not in {"normal", "internal"}:
            raise KeyError("Check allowed transaction types.")

        sum = Decimal("0")

        for d in data:
            # "from" this address -> subtract value
            if d.get("from", "").lower() == address.lower():
                if d.get("isError") == "0":
                    sum -= Decimal(d.get("value", "0"))
                if transaction_type == "normal":
                    sum -= Decimal(d.get("gasPrice", "0")) * Decimal(
                        d.get("gasUsed", "0")
                    )
            # "to" this address -> add value (only if transaction succeeded)
            if d.get("to", "").lower() == address.lower() and d.get("isError") == "0":
                sum += Decimal(d.get("value", "0"))

        return float(sum) / 10**18  # Convert wei to Ether

    def calculate_ether_used_for_token_transfer(self, address: str, data) -> float:
        sum = Decimal("0")
        for d in data:
            # "from" this address -> subtract
            if d.get("from").lower() == address.lower():
                sum -= Decimal(d.get("gasPrice", "0")) * Decimal(d.get("gasUsed", "0"))

        return float(sum) / 10**18
