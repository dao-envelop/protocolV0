import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

ERC20_COLLATERAL_AMOUNT = 100e18
ERC20_COLLATERAL_AMOUNT_WETH = 1000e18
UNWRAP_AFTER = 0
COUNT=10
zero_address = '0x0000000000000000000000000000000000000000'
ORIGINAL_TOKEN_IDs=[]
def test_distr(accounts,  distributor, niftsy20, dai, launcpad, erc721mock2, weth):
    RECEIVERS = [launcpad.address for x in range(COUNT)]
    for z in range(COUNT):
        #logging.info('z = {}'.format(z))
        #erc721mock.mint(z + 1)
        ORIGINAL_TOKEN_IDs.append(z)

    niftsy20.approve(distributor, ERC20_COLLATERAL_AMOUNT * len(RECEIVERS), {'from':accounts[0]})
    weth.approve(distributor, ERC20_COLLATERAL_AMOUNT_WETH * len(RECEIVERS), {'from':accounts[0]})
    tx = distributor.WrapAndDistrib721WithMint(
        erc721mock2.address, 
        RECEIVERS,
        ORIGINAL_TOKEN_IDs,
        [(niftsy20.address,ERC20_COLLATERAL_AMOUNT), (weth.address,ERC20_COLLATERAL_AMOUNT_WETH)],
        UNWRAP_AFTER,
        {'from':accounts[0], 'value':'10 ether'}
    )
    #logging.info(tx.events)
    #ids=[distributor.tokenURI(x['wrappedTokenId']) for x in tx.events['Wrapped']]
    #logging.info(ids)
    assert len(tx.events['Wrapped']) == len(RECEIVERS)
    assert distributor.balanceOf(launcpad)==COUNT
    assert weth.balanceOf(distributor.address) == ERC20_COLLATERAL_AMOUNT_WETH * len(RECEIVERS)
    assert niftsy20.balanceOf(distributor.address) == ERC20_COLLATERAL_AMOUNT * len(RECEIVERS)
    assert distributor.balance() == '10 ether'

'''def test_wrapped_props(accounts,  distributor, launcpad, dai, niftsy20):
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
    assert dai.balanceOf(launcpad)==launcpad.getWNFTPrice(1, dai)'''


