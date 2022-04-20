import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

ERC20_COLLATERAL_AMOUNT = 2e16
TIMELOCK = 3600*24*30*12
TICKET_VALID = 3600*24*30

def test_init(accounts, distrManager, dai):
    distrManager.addTarif((dai, ERC20_COLLATERAL_AMOUNT, TIMELOCK, TICKET_VALID ) , {'from':accounts[0]})
    assert distrManager.ticketsOnSale(0)[0] == dai.address

def test_buy(accounts, distrManager, dai, distributor):
    dai.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT)
    dai.approve(distrManager, ERC20_COLLATERAL_AMOUNT, {'from':accounts[1]})
    with reverts("Only for distributors"):
        distrManager.buyTicket(0, {'from':accounts[1]})
    distributor.setDistributorState(distrManager, True, {'from':accounts[0]})        
    distributor.transferOwnership(distrManager, {'from':accounts[0]})
    distrManager.buyTicket(0, {'from':accounts[1]})
    assert distrManager.validDistributors(accounts[1]) > 0
    assert distributor.distributors(accounts[1]) == True       

