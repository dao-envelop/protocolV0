import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

STAKED_AMOUNT = 1e18
UNWRAP_AFTER = 0
zero_address = '0x0000000000000000000000000000000000000000'
def test_settings(accounts,  farming, niftsy20, dai):
    setting = farming.getRewardSettings(niftsy20)
    assert len(setting) == 4
    assert setting[0][1]==1000

def test_stake(accounts,  farming, niftsy20, dai):
    niftsy20.approve(farming, STAKED_AMOUNT)
    tx = farming.WrapForFarming(
        accounts[1],
        (niftsy20.address, STAKED_AMOUNT),
        chain.time() + 100,
        {'from':accounts[0]}
    )
    assert farming.getAvailableRewardAmount(farming.lastWrappedNFTId(), niftsy20) == 0

def test_check_reward(accounts,  farming, niftsy20):
    chain.sleep(100)
    assert farming.getAvailableRewardAmount(farming.lastWrappedNFTId(), niftsy20) > 0

def test_harves(accounts,  farming, niftsy20):
    farming.harvest(farming.lastWrappedNFTId(), niftsy20.address)
