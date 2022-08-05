from scripts.every_func import buyOption, write
from scripts.helpful_scripts import get_account, approve_erc20
from brownie import Options, XToken, YToken
import time

account = get_account()


def deploy():
    xtkn = XToken.deploy({"from": account})
    ytkn = YToken.deploy({"from": account})

    opt = Options.deploy(xtkn, {"from": account})
    return xtkn, ytkn, opt


def test_cant_write_unless_approved(callPut=True):
    xtkn, ytkn, opt = deploy()

    try:
        tx = opt.writeOption(
            100,
            3,
            int(time.time()) + 10,
            10,
            callPut,
            ytkn,
            {"from": account},
        )
        tx.wait(1)
    except:
        approve_erc20(
            amount=10 if callPut else 100 * 10,
            spender=opt,
            erc20_address=ytkn if callPut else xtkn,
            account=account,
        )
        tx = opt.writeOption(
            100,
            3,
            int(time.time()) + 10,
            10,
            callPut,
            ytkn,
            {"from": account},
        )
        tx.wait(1)
    cur = opt.getOption(0)
    assert cur[-2] == account


def test_cancel_withdraws(callPut=True):
    xtkn, ytkn, opt, account, option = write(True, callPut)

    cur = opt.getOption(0)
    tkn = ytkn if callPut else xtkn
    before = tkn.balanceOf(account)

    amount = cur[3]
    strike = cur[0]

    checkDiff = amount if callPut == True else strike * amount

    tx = opt.cancelOption(0, {"from": account})
    tx.wait(1)

    after = tkn.balanceOf(account)

    print(f"CHeck {checkDiff}")
    assert after - before == checkDiff


def test_can_buy(callPut=True):
    xtkn, ytkn, opt, account, option = write(True, callPut)

    strike = option[0]
    premium = option[1]
    amount = option[3]
    writer = option[-2]

    tkn = xtkn if callPut else ytkn

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

    before = tkn.balanceOf(writer)
    optBefore = tkn.balanceOf(opt)

    tx = opt.buyOption(0, {"from": account})
    tx.wait(1)

    after = tkn.balanceOf(writer)
    optAfter = tkn.balanceOf(opt)

    sent = tx.events["BuyOption"]["_amount"]

    print(strike, amount)

    assert before - after == strike * amount if callPut else amount
    # ↑ because in this example writer == buyer
    # ↑ otherwise it would be after - before == -premium
    assert optAfter - optBefore == sent


def test_can_exercise():

    xtkn, ytkn, opt, account, option = buyOption(True)

    strike = option[0]
    amount = option[3]

    xBefore = xtkn.balanceOf(opt)
    yBefore = ytkn.balanceOf(opt)

    print(xBefore, yBefore)

    tx = opt.exerciseOption(0, {"from": account})
    tx.wait(1)

    xAfter = xtkn.balanceOf(opt)
    yAfter = ytkn.balanceOf(opt)

    assert xBefore - xAfter == strike * amount and yBefore - yAfter == amount


def test_can_refund(callPut=True):
    xtkn, ytkn, opt, account, option = write(new=True, callPut=callPut)

    time.sleep(12)

    strike = option[0]
    amount = option[3]
    writer = option[-2]
    buyer = option[-1]

    xBefore = xtkn.balanceOf(buyer) if callPut else xtkn.balanceOf(writer)
    yBefore = ytkn.balanceOf(writer) if callPut else ytkn.balanceOf(buyer)

    tx = opt.refundExpiredOption(0, {"from": account})
    tx.wait(1)

    xAfter = xtkn.balanceOf(buyer) if callPut else xtkn.balanceOf(writer)
    yAfter = ytkn.balanceOf(writer) if callPut else ytkn.balanceOf(buyer)
    print(yAfter, xBefore)

    assert yAfter - yBefore == amount
    assert (
        xAfter - xBefore == 0
        if buyer == "0x0000000000000000000000000000000000000000"
        else strike * amount
    )
