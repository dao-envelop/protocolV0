import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

ERC20_COLLATERAL_AMOUNT = 100e18
ERC20_COLLATERAL_AMOUNT_WETH = 1000e18
UNWRAP_AFTER = 10e10
COUNT=10
zero_address = '0x0000000000000000000000000000000000000000'
ORIGINAL_TOKEN_IDs=[]
ETH_AMOUNT = '10 ether'
change_amount = '1 ether'
def test_distr(accounts,  distributor, niftsy20, dai, launcpadWLNative, ERC721Distr, weth):
    RECEIVERS = [launcpadWLNative.address for x in range(COUNT)]
    for z in range(COUNT):

        ORIGINAL_TOKEN_IDs.append(z)

    tx = distributor.WrapAndDistrib721WithMint(
        ERC721Distr.address, 
        RECEIVERS,
        ORIGINAL_TOKEN_IDs,
        [],
        UNWRAP_AFTER,
        {'from':accounts[0], 'value':ETH_AMOUNT}
    )
    #logging.info(tx.events)
    #ids=[distributor.tokenURI(x['wrappedTokenId']) for x in tx.events['Wrapped']]
    #logging.info(ids)
    assert len(tx.events['Wrapped']) == len(RECEIVERS)
    assert distributor.balanceOf(launcpadWLNative)==COUNT
    assert distributor.balance() == ETH_AMOUNT
    assert ERC721Distr.balanceOf(distributor.address) == COUNT

    with reverts("Ownable: caller is not the owner"):
        launcpadWLNative.setEnableAfterDate(UNWRAP_AFTER, {"from": accounts[1]})
    launcpadWLNative.setEnableAfterDate(UNWRAP_AFTER, {"from": accounts[0]})
    with reverts("Please wait for start date"):
        launcpadWLNative.claimNFT(1, dai)

    with reverts("Ownable: caller is not the owner"):
        launcpadWLNative.setPrice(dai, 3, 100, {"from": accounts[1]})