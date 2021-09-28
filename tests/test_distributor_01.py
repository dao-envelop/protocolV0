import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

ORIGINAL_NFT_IDs = [1,2,3,4,5,6,7,8,9]
ERC20_COLLATERAL_AMOUNT = 2e16
UNWRAP_AFTER = 0

def test_ERC721Distr(accounts, ERC721Distr):
    ERC721Distr.mint(accounts[0], 0, {'from':accounts[0]})
    logging.info(ERC721Distr.tokenURI(0))
    assert ERC721Distr.tokenURI(0) == ERC721Distr.baseURI() + '0'

def test_distr(accounts, ERC721Distr, distributor, weth, dai):
    RECEIVERS = [accounts[x] for x in ORIGINAL_NFT_IDs]
    weth.approve(distributor, ERC20_COLLATERAL_AMOUNT * len(ORIGINAL_NFT_IDs))
    dai.approve(distributor, ERC20_COLLATERAL_AMOUNT * len(ORIGINAL_NFT_IDs))
    ERC721Distr.setMinterStatus(distributor, True)
    tx = distributor.WrapAndDistrib721WithMint(
        ERC721Distr.address, 
        RECEIVERS,
        ORIGINAL_NFT_IDs, 
        [(weth.address,ERC20_COLLATERAL_AMOUNT), (dai.address,ERC20_COLLATERAL_AMOUNT)],
        UNWRAP_AFTER,
        {'from':accounts[0]}
    )

    assert len(tx.events['Wrapped']) == len(ORIGINAL_NFT_IDs)
    assert distributor.balanceOf(accounts[1])==1

def test_wrapped_props(accounts,  distributor, weth, dai):
    logging.info(distributor.getERC20Collateral(5))
    assert distributor.getERC20Collateral(5)[0][0] == weth.address
    assert distributor.getERC20Collateral(5)[1][0] == dai.address
    assert distributor.getERC20Collateral(5)[0][1] == ERC20_COLLATERAL_AMOUNT
    assert distributor.getERC20Collateral(5)[1][1] == ERC20_COLLATERAL_AMOUNT

def test_unwrap(accounts, ERC721Distr, distributor, weth, dai):
    tx = distributor.unWrap721(5, {'from':accounts[5]})
    assert ERC721Distr.balanceOf(accounts[5]) == 1
    assert weth.balanceOf(accounts[5]) == ERC20_COLLATERAL_AMOUNT
    assert dai.balanceOf(accounts[5]) == ERC20_COLLATERAL_AMOUNT

