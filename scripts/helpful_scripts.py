from brownie import (
    network,
    accounts,
    config,
    interface,
)
import json, requests, os
from web3 import Web3

INITIAL_PRICE_FEED_VALUE = 2 * (10**21)
DECIMALS = 18

WEB3_PROVIDER = "YOUR WEB3 PROVIDER LINK"
PRICING_API = "YOUR json PRICING API LINK"
NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["from_key"])


def get_verify_status():
    verify = (
        config["networks"][network.show_active()]["verify"]
        if config["networks"][network.show_active()].get("verify")
        else False
    )
    return verify


def get_price():
    req = requests.get(PRICING_API)
    d = json.loads(req.content)
    print("safelow: ", d["safeLow"])
    print("average: ", d["average"])
    print("fast: ", d["fast"])
    print("fastest: ", d["fastest"])

    web3 = Web3(
        Web3.HTTPProvider(
            WEB3_PROVIDER
        )
    )
    gas_price1 = web3.eth.gas_price
    print("gas: ", gas_price1 / 10 ** 8)


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx


def increaseAllowance(amount, spender, erc20_address, account):
    print("Increasing allowance of ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.increaseAllowance(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx
