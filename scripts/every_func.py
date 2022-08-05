from brownie import Options, XToken, YToken, accounts
from scripts.helpful_scripts import get_account, approve_erc20
import time


def deploy(new=False):
    account = get_account()
    stranger = accounts[1]
    xtkn = XToken.deploy({"from": account}) if new else XToken[-1]
    ytkn = YToken.deploy({"from": account}) if new else YToken[-1]

    opt = Options.deploy(xtkn, {"from": account}) if new else Options[-1]

    ytkn.transfer(stranger, 10000000000, {"from": account})
    xtkn.transfer(stranger, 10000000000, {"from": account})

    return xtkn, ytkn, opt, account


def write(
    new=False, callPut=True, exp=int(time.time()) + 10, tknAmount=10, strikePrice=100
):
    xtkn, ytkn, opt, account = deploy(new)

    approve_erc20(
        amount=tknAmount if callPut else strikePrice * tknAmount,
        spender=opt,
        erc20_address=ytkn if callPut else xtkn,
        account=account,
    )

    tx = opt.writeOption(
        strikePrice,
        3,
        exp,
        tknAmount,
        callPut,
        ytkn,
        {"from": account},
    )
    tx.wait(1)

    option = opt.getOption(0)

    print(f"Newly written option {option}")
    return xtkn, ytkn, opt, account, option


def cancel(new=False, id=0):
    xtkn, ytkn, opt, account, option = write(new)

    tx = opt.cancelOption(id, {"from": account})
    tx.wait(1)

    option = opt.getOption(id)
    print(f"Cancelled option {option}")


def buyOption(new=False, id=0):
    xtkn, ytkn, opt, account, option = write(new)

    strike = option[0]
    premium = option[1]
    amount = option[3]
    callPut = option[5]
    writer = option[-2]
    print(f"Parameters of the option being bought:")
    print(
        f"strike {strike} , premium {premium}, amount {amount}, callPut {callPut}, writer {writer}"
    )

    approve_erc20(
        amount=strike * amount + premium if callPut else premium,
        spender=opt,
        erc20_address=xtkn,
        account=account,
    )

    if not callPut:
        approve_erc20(
            amount=amount,
            spender=opt,
            erc20_address=ytkn,
            account=account,
        )

    tx = opt.buyOption(id, {"from": account})
    tx.wait(1)

    sent = tx.events["BuyOption"]["_amount"]
    print(sent)

    return xtkn, ytkn, opt, account, option


def exercise(new=False, id=0):
    xtkn, ytkn, opt, account, option = buyOption(new)

    tx = opt.exerciseOption(id, {"from": account})
    tx.wait(1)

    option = opt.getOption(id)
    print(option)


def refund(new=False, id=0):
    xtkn, ytkn, opt, account = buyOption(new)
    time.sleep("""Determine the amount to wait so that the option is expired""")

    tx = opt.refundExpiredOption(id, {"from": account})
    tx.wait(1)

    option = opt.getOption(id)
    print(option)


def main():
    exercise(True)
