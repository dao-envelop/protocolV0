import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

ETH_AMOUNT = '4 ether'
UNWRAP_AFTER = 0
COUNT=4
zero_address = '0x0000000000000000000000000000000000000000'
def test_distr(accounts,  distributor, niftsy20, dai, launcpadWLNative):
    RECEIVERS = [launcpadWLNative.address for x in range(COUNT)]
    with reverts("Only for distributors"):
        distributor.WrapAndDistribEmpty(
        RECEIVERS,
        [],
        UNWRAP_AFTER,
        {'from':accounts[1], 'value':ETH_AMOUNT}
        )
    tx = distributor.WrapAndDistribEmpty(
        RECEIVERS,
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

def test_wrapped_props(accounts,  distributor, launcpadWLNative, dai, niftsy20):
    for i in  range(distributor.balanceOf(launcpadWLNative)):
        logging.info('tokenId={}, etherBalance={}'.format(
            distributor.tokenOfOwnerByIndex(launcpadWLNative, i),
            Wei(distributor.getTokenValue(distributor.tokenOfOwnerByIndex(launcpadWLNative, i))[0]).to('ether')
        ))
        assert distributor.getTokenValue(distributor.tokenOfOwnerByIndex(launcpadWLNative, i))[0]==Wei(ETH_AMOUNT)/  COUNT      

def test_set_price(accounts,  launcpadWLNative, distributor, dai, niftsy20):
    launcpadWLNative.setPrice(dai, 3, 100)
    launcpadWLNative.setPrice(zero_address, 2, 1000)
    for i in  range(distributor.balanceOf(launcpadWLNative)):
        tid=distributor.tokenOfOwnerByIndex(launcpadWLNative, i)
        p1 = launcpadWLNative.getWNFTPrice(tid, dai)
        p2 = launcpadWLNative.getWNFTPrice(tid, zero_address) 
        logging.info('tokenId={},\n etherBalance={},\n priceErc20={},\n priceETH={}'.format(
            distributor.tokenOfOwnerByIndex(launcpadWLNative, i),
            distributor.getTokenValue(distributor.tokenOfOwnerByIndex(launcpadWLNative, i))[0],
            Wei(p1).to('ether'), Wei(p2).to('ether')
        ))

def test_claim_WL(accounts,  launcpadWLNative, distributor, dai, niftsy20, whitelist):
    with reverts("White list is NOT active"):
        launcpadWLNative.claimNFT(1,{'from':accounts[0]})
    launcpadWLNative.setAllocationList(whitelist)
    with reverts("Too low allocation"):
        launcpadWLNative.claimNFT(1,{'from':accounts[0]})
    whitelist.increaseAllocation(accounts[0], zero_address, "2 ether")
    whitelist.setOperator(launcpadWLNative, True)
    assert launcpadWLNative.getAvailableAllocation(accounts[0]) == "2 ether"
    tx  = launcpadWLNative.claimNFT(1,{'from':accounts[0]})
    assert launcpadWLNative.getAvailableAllocation(accounts[0]) == "1 ether"

    # tx = launcpadWLNative.claimNFT(1, dai)
    # assert distributor.balanceOf(accounts[0]) == 1
    # assert dai.balanceOf(launcpadWLNative)==launcpadWLNative.getWNFTPrice(1, dai)


