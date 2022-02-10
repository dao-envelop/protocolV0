import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

ORIGINAL_NFT_IDs = [1,2,3]
UNWRAP_AFTER = chain.time() + 100
ERC20_COLLATERAL_AMOUNT = 20e18

def test_ERC721Distr(accounts, original721):
    [original721.mint(accounts[0], x, {'from':accounts[0]}) for x in ORIGINAL_NFT_IDs]
    logging.info(original721.tokenURI(1))
    assert original721.balanceOf(accounts[0]) == len(ORIGINAL_NFT_IDs)

def test_multiwrap(accounts, original721, multiwrapper, distributor, niftsy20, dai):
    
    #global RECEIVERS
    RECEIVERS = [accounts[1] for x in ORIGINAL_NFT_IDs]
    multiwrapper.setWrapper(distributor,{'from':accounts[0]}) 
    [original721.transferFrom(accounts[0], multiwrapper, x, {'from':accounts[0]}) for x in ORIGINAL_NFT_IDs]
    tx = multiwrapper.WrapAndDistrib721Batch(
            original721, 
            RECEIVERS, 
            ORIGINAL_NFT_IDs,
            [],
            UNWRAP_AFTER, 
            {'from':accounts[0]}
        )
    #assert len(tx.events['Transfer']) == len(ORIGINAL_NFT_IDs)
    assert distributor.balanceOf(RECEIVERS[1])==len(ORIGINAL_NFT_IDs)

    #add collateral through batch method
    niftsy20.approve(multiwrapper, niftsy20.balanceOf(accounts[0]), {'from':accounts[0]}) 
    distributor.setCollateralStatus(niftsy20,True,{'from':accounts[0]})
    
    ERC20_COLLATERAL = [(niftsy20.address, ERC20_COLLATERAL_AMOUNT), (dai.address,ERC20_COLLATERAL_AMOUNT), (niftsy20.address, 2*ERC20_COLLATERAL_AMOUNT)]

    with reverts("ERC20: transfer amount exceeds allowance"):
        multiwrapper.AddOneCollateralToBatch(ORIGINAL_NFT_IDs, ERC20_COLLATERAL, {"from": accounts[0]})

    dai.approve(multiwrapper, dai.balanceOf(accounts[0]), {'from':accounts[0]}) 

    with reverts("This ERC20 is not enabled for collateral"):
        multiwrapper.AddOneCollateralToBatch(ORIGINAL_NFT_IDs, ERC20_COLLATERAL, {"from": accounts[0]})

    distributor.setCollateralStatus(dai,True, {'from':accounts[0]})

    with reverts("Only for distributors"):
        multiwrapper.AddOneCollateralToBatch(ORIGINAL_NFT_IDs, ERC20_COLLATERAL, {"from": accounts[1]})

    multiwrapper.AddOneCollateralToBatch(ORIGINAL_NFT_IDs, ERC20_COLLATERAL, {"from": accounts[0]})

    assert distributor.getERC20CollateralBalance(ORIGINAL_NFT_IDs[0], niftsy20.address) == Wei(ERC20_COLLATERAL_AMOUNT)
    assert distributor.getERC20CollateralBalance(ORIGINAL_NFT_IDs[1], dai.address) == Wei(ERC20_COLLATERAL_AMOUNT)
    assert distributor.getERC20CollateralBalance(ORIGINAL_NFT_IDs[2], niftsy20.address) == 2*Wei(ERC20_COLLATERAL_AMOUNT)

    assert niftsy20.balanceOf(distributor.address) == 3*ERC20_COLLATERAL_AMOUNT
    assert dai.balanceOf(distributor.address) == ERC20_COLLATERAL_AMOUNT

    ERC20_COLLATERAL = [(niftsy20.address, ERC20_COLLATERAL_AMOUNT), (dai.address,ERC20_COLLATERAL_AMOUNT)]

    with reverts("Not equal arrays"):
        multiwrapper.AddOneCollateralToBatch(ORIGINAL_NFT_IDs, ERC20_COLLATERAL, {"from": accounts[0]})



 