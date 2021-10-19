import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

ERC20_COLLATERAL_AMOUNT = 100e18
UNWRAP_AFTER = 0
COUNT=4
zero_address = '0x0000000000000000000000000000000000000000'
def test_settings(accounts,  farming, niftsy20, dai):
    setting = farming.getRewardSettings(niftsy20)
    assert len(setting) == 4
    assert setting[0][1]==1000
