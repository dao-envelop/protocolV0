import pytest
import logging
from brownie import Wei, reverts
LOGGER = logging.getLogger(__name__)


def test_niftsy_burn_minter_fail(accounts, niftsy20):
    with reverts("MinterRole: caller does not have the Minter role"):
        niftsy20.burn(accounts[0], 1, {"from":accounts[1]})
    assert niftsy20.balanceOf(accounts[0]) == niftsy20.totalSupply()

def test_niftsy_burn_amount_failed(accounts, niftsy20):
    with reverts("ERC20: burn amount exceeds balance"):
        niftsy20.burn(accounts[0], niftsy20.totalSupply() + 1 , {"from":accounts[0]})
    assert niftsy20.balanceOf(accounts[0]) == niftsy20.totalSupply()

def test_niftsy_burn_success(accounts, niftsy20):
    before_balance = niftsy20.balanceOf(accounts[0])
    logging.info('acc = {}'.format(niftsy20.balanceOf(accounts[0])))
    niftsy20.burn(accounts[0], 1, {"from":accounts[0]})
    assert niftsy20.balanceOf(accounts[0]) == before_balance - 1
    assert niftsy20.totalSupply() == before_balance - 1

def test_niftsy_burn_fail_zero_address(accounts, niftsy20):
    before_balance = niftsy20.balanceOf(accounts[0])
    with reverts("ERC20: burn from the zero address"):
        niftsy20.burn('0x0000000000000000000000000000000000000000', 1, {"from":accounts[0]})
    assert niftsy20.totalSupply() == before_balance
    assert niftsy20.balanceOf(accounts[0]) == before_balance