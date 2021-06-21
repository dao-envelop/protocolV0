import pytest
import logging
from brownie import Wei, reverts
LOGGER = logging.getLogger(__name__)


def test_niftsy_transferFrom(accounts, niftsy20):
	niftsy20.transfer(accounts[1], 1, {"from": accounts[0]})
	with reverts("ERC20: transfer amount exceeds allowance"):
		niftsy20.transferFrom(accounts[1], accounts[2], 1, {"from": accounts[2]})
	niftsy20.transferFrom(accounts[1], accounts[2], 1, {"from": accounts[0]})
	assert niftsy20.balanceOf(accounts[1]) == 0
	assert niftsy20.balanceOf(accounts[2]) == 1

	#minter
	niftsy20.transfer(accounts[1], 1, {"from": accounts[0]})
	niftsy20.addMinter(accounts[2], {'from':accounts[0]})
	niftsy20.transferFrom(accounts[1], accounts[2], 1, {"from": accounts[2]})
	assert niftsy20.balanceOf(accounts[1]) == 0
	assert niftsy20.balanceOf(accounts[2]) == 2

	niftsy20.approve(accounts[3], 1, {"from": accounts[1]})
	with reverts("ERC20: transfer amount exceeds balance"):
		niftsy20.transferFrom(accounts[1], accounts[3], 1, {"from": accounts[3]})


