import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

NATIVE_COLLATERAL_AMOUNT = 10
ERC20_COLLATERAL_AMOUNT = 100e18
UNWRAP_AFTER = 0
COUNT=4
zero_address = '0x0000000000000000000000000000000000000000'
def test_distr(accounts,  distributor, niftsy20, dai, launcpadWLNative):
    RECEIVERS = [launcpadWLNative.address for x in range(COUNT)]
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
        {'from':accounts[0], 'value': str(NATIVE_COLLATERAL_AMOUNT * len(RECEIVERS))+' ether'}
    )
    #logging.info(tx.events)
    #ids=[distributor.tokenURI(x['wrappedTokenId']) for x in tx.events['Wrapped']]
    #logging.info(ids)
    assert len(tx.events['Wrapped']) == len(RECEIVERS)
    assert distributor.balanceOf(launcpadWLNative)==COUNT

def test_wrapped_props(accounts,  distributor, launcpadWLNative, dai, niftsy20):
    for i in  range(distributor.balanceOf(launcpadWLNative)):
        logging.info('tokenId={}, erc20Balance={}, nativeBalance={}'.format(
            distributor.tokenOfOwnerByIndex(launcpadWLNative, i),
            Wei(distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpadWLNative, i), niftsy20)).to('ether'),
            Wei(distributor.getTokenValue(distributor.tokenOfOwnerByIndex(launcpadWLNative, i))[0]).to('ether')
        ))
        assert distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpadWLNative, i), niftsy20)==ERC20_COLLATERAL_AMOUNT        

def test_set_price(accounts,  launcpadWLNative, distributor, dai, niftsy20):
    launcpadWLNative.setPrice(dai, 3, 100)
    launcpadWLNative.setPrice(zero_address, 2, 1000)
    for i in  range(distributor.balanceOf(launcpadWLNative)):
        tid=distributor.tokenOfOwnerByIndex(launcpadWLNative, i)
        p1 = launcpadWLNative.getWNFTPrice(tid, dai)
        p2 = launcpadWLNative.getWNFTPrice(tid, zero_address) #?????????????
        logging.info('tokenId={},\n erc20Balance={},\n priceErc20={},\n priceETH={}'.format(
            distributor.tokenOfOwnerByIndex(launcpadWLNative, i),
            distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpadWLNative, i), niftsy20),
            Wei(p1).to('ether'), Wei(p2).to('ether')
        ))

def test_claim_WL(accounts,  launcpadWLNative, distributor, dai, niftsy20, whitelist):
    with reverts("White list is NOT active"):
        launcpadWLNative.claimNFT(1,{'from':accounts[0]})
    launcpadWLNative.setAllocationList(whitelist)
    with reverts("Too low allocation"):
        launcpadWLNative.claimNFT(1,{'from':accounts[0]})
    whitelist.increaseAllocation(accounts[0], zero_address, NATIVE_COLLATERAL_AMOUNT * 10e18)
    whitelist.setOperator(launcpadWLNative, True)
    assert launcpadWLNative.getAvailableAllocation(accounts[0]) == NATIVE_COLLATERAL_AMOUNT * 10e18
    tx  = launcpadWLNative.claimNFT(1,{'from':accounts[0]})
    assert launcpadWLNative.getAvailableAllocation(accounts[0]) == 0

    # tx = launcpadWLNative.claimNFT(1, dai)
    # assert distributor.balanceOf(accounts[0]) == 1
    # assert dai.balanceOf(launcpadWLNative)==launcpadWLNative.getWNFTPrice(1, dai)


