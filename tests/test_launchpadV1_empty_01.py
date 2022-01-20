import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

ERC20_COLLATERAL_AMOUNT = 100e18
UNWRAP_AFTER = 0
COUNT=4
zero_address = '0x0000000000000000000000000000000000000000'
def test_distr(accounts,  distributor, niftsy20, dai, launcpadWL):
    RECEIVERS = [launcpadWL.address for x in range(COUNT)]
    niftsy20.approve(distributor, ERC20_COLLATERAL_AMOUNT * len(RECEIVERS), {'from':accounts[0]})
    with reverts("Only for distributors"):
        distributor.WrapAndDistribEmpty(
        RECEIVERS,
        [(niftsy20.address,ERC20_COLLATERAL_AMOUNT)],
        UNWRAP_AFTER,
        {'from':accounts[1]}
        )
    tx = distributor.WrapAndDistribEmpty(
        RECEIVERS,
        [(niftsy20.address,ERC20_COLLATERAL_AMOUNT)],
        UNWRAP_AFTER,
        {'from':accounts[0]}
    )
    #logging.info(tx.events)
    #ids=[distributor.tokenURI(x['wrappedTokenId']) for x in tx.events['Wrapped']]
    #logging.info(ids)
    assert len(tx.events['Wrapped']) == len(RECEIVERS)
    assert distributor.balanceOf(launcpadWL)==COUNT

def test_wrapped_props(accounts,  distributor, launcpadWL, dai, niftsy20):
    for i in  range(distributor.balanceOf(launcpadWL)):
        logging.info('tokenId={}, erc20Balance={}'.format(
            distributor.tokenOfOwnerByIndex(launcpadWL, i),
            Wei(distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpadWL, i), niftsy20)).to('ether')
        ))
        assert distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpadWL, i), niftsy20)==ERC20_COLLATERAL_AMOUNT        

def test_set_price(accounts,  launcpadWL, distributor, dai, niftsy20):
    launcpadWL.setPrice(dai, 3, 100)
    launcpadWL.setPrice(zero_address, 2, 1000)
    for i in  range(distributor.balanceOf(launcpadWL)):
        tid=distributor.tokenOfOwnerByIndex(launcpadWL, i)
        p1 = launcpadWL.getWNFTPrice(tid, dai)
        p2 = launcpadWL.getWNFTPrice(tid, zero_address) #?????????????
        logging.info('tokenId={},\n erc20Balance={},\n priceErc20={},\n priceETH={}'.format(
            distributor.tokenOfOwnerByIndex(launcpadWL, i),
            distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpadWL, i), niftsy20),
            Wei(p1).to('ether'), Wei(p2).to('ether')
        ))

def test_claim_WL(accounts,  launcpadWL, distributor, dai, niftsy20, whitelist):
    with reverts("White list is NOT active"):
        launcpadWL.claimNFT(1,{'from':accounts[0]})
    launcpadWL.setAllocationList(whitelist)
    with reverts("Too low allocation"):
        launcpadWL.claimNFT(1,{'from':accounts[0]})
    whitelist.increaseAllocation(accounts[0], niftsy20, ERC20_COLLATERAL_AMOUNT)
    whitelist.setOperator(launcpadWL, True)
    assert launcpadWL.getAvailableAllocation(accounts[0]) == ERC20_COLLATERAL_AMOUNT
    tx  = launcpadWL.claimNFT(1,{'from':accounts[0]})
    assert launcpadWL.getAvailableAllocation(accounts[0]) == 0

    # tx = launcpadWL.claimNFT(1, dai)
    # assert distributor.balanceOf(accounts[0]) == 1
    # assert dai.balanceOf(launcpadWL)==launcpadWL.getWNFTPrice(1, dai)


