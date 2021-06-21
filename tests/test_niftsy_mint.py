import pytest
import logging
from brownie import Wei, reverts
LOGGER = logging.getLogger(__name__)


def test_niftsy_mint_fail(accounts, niftsy20):
	with reverts("MinterRole: caller does not have the Minter role"):
		niftsy20.mint(accounts[0], 1, {"from":accounts[1]})
	assert niftsy20.balanceOf(accounts[0]) == niftsy20.totalSupply()

def test_niftsy_mint_big_supply_failed(accounts, niftsy20):
	with reverts("MAX_SUPPLY amount exceed"):
		niftsy20.mint(accounts[0], 1, {"from":accounts[0]})
	assert niftsy20.balanceOf(accounts[0]) == niftsy20.totalSupply()

def test_niftsy_mint_fail_zero_address(accounts, niftsy20):
	niftsy20.burn(accounts[0], 1, {"from":accounts[0]})
	before_balance = niftsy20.balanceOf(accounts[0])
	with reverts("ERC20: mint to the zero address"):
		niftsy20.mint('0x0000000000000000000000000000000000000000', 1, {"from":accounts[0]})
	assert niftsy20.totalSupply() == before_balance

def test_niftsy_mint_success(accounts, niftsy20):
	before_balance = niftsy20.balanceOf(accounts[0])
	niftsy20.mint(accounts[0], 1, {"from":accounts[0]})
	assert niftsy20.balanceOf(accounts[0]) == before_balance + 1
	assert niftsy20.totalSupply() == before_balance + 1