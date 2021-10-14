import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

ERC20_COLLATERAL_AMOUNT = 100e18
UNWRAP_AFTER = 0
COUNT=4
zero_address = '0x0000000000000000000000000000000000000000'
def test_distr(accounts,  distributor, niftsy20, dai, launcpad):
    RECEIVERS = [launcpad.address for x in range(COUNT)]
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
    assert distributor.balanceOf(launcpad)==COUNT

def test_wrapped_props(accounts,  distributor, launcpad, dai, niftsy20):
    for i in  range(distributor.balanceOf(launcpad)):
        logging.info('tokenId={}, erc20Balance={}'.format(
            distributor.tokenOfOwnerByIndex(launcpad, i),
            Wei(distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpad, i), niftsy20)).to('ether')
        ))
        assert distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpad, i), niftsy20)==ERC20_COLLATERAL_AMOUNT        

def test_set_price(accounts,  launcpad, distributor, dai, niftsy20):
    launcpad.setPrice(dai, 3, 100)
    launcpad.setPrice(zero_address, 2, 1000)
    for i in  range(distributor.balanceOf(launcpad)):
        tid=distributor.tokenOfOwnerByIndex(launcpad, i)
        p1 = launcpad.getWNFTPrice(tid, dai)
        p2 = launcpad.getWNFTPrice(tid, zero_address) #?????????????
        logging.info('tokenId={},\n erc20Balance={},\n priceErc20={},\n priceETH={}'.format(
            distributor.tokenOfOwnerByIndex(launcpad, i),
            distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpad, i), niftsy20),
            Wei(p1).to('ether'), Wei(p2).to('ether')
        ))

def test_claim_ERC20(accounts,  launcpad, distributor, dai, niftsy20):
    dai.approve(launcpad, 1e30)
    tx = launcpad.claimNFT(1, dai)
    assert distributor.balanceOf(accounts[0]) == 1
    assert dai.balanceOf(launcpad)==launcpad.getWNFTPrice(1, dai)


