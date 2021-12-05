import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

ORIGINAL_NFT_IDs = [1,2,3,4,5,6,7,8,9]

def test_ERC721Distr(accounts, original721):
    original721.mint(accounts[0], 0, {'from':accounts[0]})
    logging.info(original721.tokenURI(0))
    assert original721.balanceOf(accounts[0]) == 1

def test_multimint(accounts, original721, multiminter):
    #global RECEIVERS
    RECEIVERS = [accounts.add() for x in ORIGINAL_NFT_IDs]
    with reverts("Trusted address only"):
         multiminter.multiMint(original721, RECEIVERS, ORIGINAL_NFT_IDs, {'from':accounts[0]})
    original721.setMinter(multiminter)
    tx = multiminter.multiMint(original721, RECEIVERS, ORIGINAL_NFT_IDs, {'from':accounts[0]})
    assert len(tx.events['Transfer']) == len(ORIGINAL_NFT_IDs)
    assert original721.balanceOf(RECEIVERS[0])==1
