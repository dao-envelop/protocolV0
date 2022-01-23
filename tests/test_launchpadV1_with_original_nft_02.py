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
def test_distr(accounts,  distributor, niftsy20, dai, launcpadWL, ERC721Distr, weth):
    RECEIVERS = [launcpadWL.address for x in range(COUNT)]
    for z in range(COUNT):

        ORIGINAL_TOKEN_IDs.append(z)

    niftsy20.approve(distributor, ERC20_COLLATERAL_AMOUNT * len(RECEIVERS), {'from':accounts[0]})
    weth.approve(distributor, ERC20_COLLATERAL_AMOUNT_WETH * len(RECEIVERS), {'from':accounts[0]})
    tx = distributor.WrapAndDistrib721WithMint(
        ERC721Distr.address, 
        RECEIVERS,
        ORIGINAL_TOKEN_IDs,
        [(niftsy20.address,ERC20_COLLATERAL_AMOUNT), (weth.address,ERC20_COLLATERAL_AMOUNT_WETH)],
        UNWRAP_AFTER,
        {'from':accounts[0], 'value':ETH_AMOUNT}
    )
    #logging.info(tx.events)
    #ids=[distributor.tokenURI(x['wrappedTokenId']) for x in tx.events['Wrapped']]
    #logging.info(ids)
    assert len(tx.events['Wrapped']) == len(RECEIVERS)
    assert distributor.balanceOf(launcpadWL)==COUNT
    assert weth.balanceOf(distributor.address) == ERC20_COLLATERAL_AMOUNT_WETH * len(RECEIVERS)
    assert niftsy20.balanceOf(distributor.address) == ERC20_COLLATERAL_AMOUNT * len(RECEIVERS)
    assert distributor.balance() == '10 ether'
    assert ERC721Distr.balanceOf(distributor.address) == COUNT

    with reverts("Ownable: caller is not the owner"):
        launcpadWL.setEnableAfterDate(UNWRAP_AFTER, {"from": accounts[1]})
    launcpadWL.setEnableAfterDate(UNWRAP_AFTER, {"from": accounts[0]})
    with reverts("Please wait for start date"):
        launcpadWL.claimNFT(1, dai)

    with reverts("Ownable: caller is not the owner"):
        launcpadWL.setPrice(dai, 3, 100, {"from": accounts[1]})