import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

STAKED_AMOUNT = 1e18
UNWRAP_AFTER = 0
zero_address = '0x0000000000000000000000000000000000000000'

#two accounts farm
def test_mint(accounts,  originalNFT721):
    originalNFT721.mint(accounts[1], {"from": accounts[1]})
    assert originalNFT721.ownerOf(originalNFT721.lastNFTId()) == accounts[1]
    logging.info(originalNFT721.tokenURI(originalNFT721.lastNFTId()))

