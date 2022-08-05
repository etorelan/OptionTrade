from brownie import Options, XToken, YToken
from scripts.helpful_scripts import get_account, approve_erc20
import time


def test_integration_call():
    account = get_account()
    xtkn = XToken.deploy({"from": account})
    ytkn = YToken.deploy({"from": account})
    opt = Options.deploy(xtkn, {"from": account})

    approve_erc20(
        amount=10,
        spender=opt,
        erc20_address=ytkn,
        account=account,
    )

    tx = opt.writeOption(
        100,
        3,
        int(time.time()) + 10,
        10,
        True,
        ytkn,
        {"from": account},
    )
    tx.wait(1)

    option = opt.getOption(0)
    strike = option[0]
    premium = option[1]
    amount = option[3]
    callPut = option[5]
    writer = option[-2]
    assert (
        strike == 100
        and premium == 3
        and amount == 10
        and callPut == True
        and writer == account
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

    tx = opt.buyOption(0, {"from": account})
    tx.wait(1)

    tx = opt.exerciseOption(0, {"from": account})
    tx.wait(1)

    option = opt.getOption(0)

    assert option[4] == False


def test_integration_put():
    account = get_account()
    xtkn = XToken.deploy({"from": account})
    ytkn = YToken.deploy({"from": account})
    opt = Options.deploy(xtkn, {"from": account})

    approve_erc20(
        amount=100 * 10,
        spender=opt,
        erc20_address=xtkn,
        account=account,
    )

    tx = opt.writeOption(
        100,
        3,
        int(time.time()) + 10,
        10,
        False,
        ytkn,
        {"from": account},
    )
    tx.wait(1)

    option = opt.getOption(0)
    strike = option[0]
    premium = option[1]
    amount = option[3]
    callPut = option[5]
    writer = option[-2]
    assert (
        strike == 100
        and premium == 3
        and amount == 10
        and callPut == False
        and writer == account
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

    tx = opt.buyOption(0, {"from": account})
    tx.wait(1)

    tx = opt.exerciseOption(0, {"from": account})
    tx.wait(1)

    option = opt.getOption(0)

    assert option[4] == False
