import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest, makeWrapNFT
from checkData import checkWrappedNFT

LOGGER = logging.getLogger(__name__)

def test_mint(accounts, originalNFT721):
	originalNFT721.mint(accounts[0], {"from": accounts[0]})
	logging.info(originalNFT721.tokenURI(1))