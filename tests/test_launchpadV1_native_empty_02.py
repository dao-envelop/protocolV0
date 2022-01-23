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
ETH_AMOUNT = '10 ether'
change_amount = '1 ether'
def test_distr(accounts,  distributor, niftsy20, dai, launcpadWLNative, ERC721Distr, weth):
    RECEIVERS = [launcpadWLNative.address for x in range(COUNT)]
    for z in range(COUNT):
        #logging.info('z = {}'.format(z))
        #erc721mock.mint(z + 1)
        ORIGINAL_TOKEN_IDs.append(z)

    with reverts("Only for distributors"):
        distributor.WrapAndDistribEmpty( 
        RECEIVERS,
        [],
        UNWRAP_AFTER,
        {'from':accounts[1], 'value':ETH_AMOUNT})

    tx = distributor.WrapAndDistribEmpty( 
        RECEIVERS,
        [],
        UNWRAP_AFTER,
        {'from':accounts[0], 'value':ETH_AMOUNT})

    #logging.info(tx.events)
    #ids=[distributor.tokenURI(x['wrappedTokenId']) for x in tx.events['Wrapped']]
    #logging.info(ids)
    assert len(tx.events['Wrapped']) == len(RECEIVERS)
    assert distributor.balanceOf(launcpadWLNative)==COUNT
    assert distributor.balance() == '10 ether'
    assert distributor.getWrappedToken(1)[0] == zero_address

def test_wrapped_props(accounts,  distributor, launcpadWLNative, dai, niftsy20, weth):
    for i in  range(distributor.balanceOf(launcpadWLNative)):
        logging.info('tokenId={}, etherBalance={}'.format(
            distributor.tokenOfOwnerByIndex(launcpadWLNative, i),
            distributor.getTokenValue(distributor.tokenOfOwnerByIndex(launcpadWLNative, i))[0]
        ))
        assert distributor.getTokenValue(distributor.tokenOfOwnerByIndex(launcpadWLNative, i))[0]== Wei(ETH_AMOUNT)/COUNT

def test_set_price(accounts,  launcpadWLNative, distributor, dai, niftsy20):
    launcpadWLNative.setPrice(dai, 3, 100)
    launcpadWLNative.setPrice(zero_address, 2, 1000)
    for i in  range(distributor.balanceOf(launcpadWLNative)):
        tid=distributor.tokenOfOwnerByIndex(launcpadWLNative, i)
        p1 = launcpadWLNative.getWNFTPrice(tid, dai)
        p2 = launcpadWLNative.getWNFTPrice(tid, zero_address) #?????????????
        logging.info('tokenId={},\n etherBalance={},\n priceErc20={},\n priceETH={}'.format(
            distributor.tokenOfOwnerByIndex(launcpadWLNative, i),
            Wei(distributor.getTokenValue(distributor.tokenOfOwnerByIndex(launcpadWLNative, i))[0]).to('ether'),
            Wei(p1).to('ether'), Wei(p2).to('ether')
        ))
    assert launcpadWLNative.getWNFTPrice(1, dai) == distributor.getTokenValue(distributor.tokenOfOwnerByIndex(launcpadWLNative, i))[0]* launcpadWLNative.priceForOneCollateralUnit(dai)[0]/launcpadWLNative.priceForOneCollateralUnit(dai)[1]

# claim with ether
def test_claim_Ether(accounts,  launcpadWLNative, distributor, dai, niftsy20, weth, ERC721Distr):
    #not enough ether
    with reverts("Received amount less then price"):
        launcpadWLNative.claimNFT(1, zero_address, {"value": '0.00001 ether'})

    #enough ether and there is the change - claim
    bbe1 = accounts[0].balance()
    payAmount = launcpadWLNative.getWNFTPrice(1, zero_address) + Wei(change_amount)
    launcpadWLNative.claimNFT(1, zero_address, {"value": payAmount})

    assert accounts[0].balance() == bbe1 - launcpadWLNative.getWNFTPrice(1, zero_address)
    assert launcpadWLNative.balance() == launcpadWLNative.getWNFTPrice(1, zero_address)
    assert distributor.balanceOf(launcpadWLNative) == COUNT - 1
    assert distributor.balanceOf(accounts[0]) == 1

    #unwrap claimed token
    bbe0 = accounts[0].balance()
    
    bbeD = distributor.balance()

    distributor.unWrap721(1)

    assert bbe0 + Wei(ETH_AMOUNT)/COUNT == accounts[0].balance()

    assert bbeD - Wei(ETH_AMOUNT)/COUNT == distributor.balance()

    assert distributor.balanceOf(accounts[0]) == 0


# claim with token
def test_claim_token(accounts,  launcpadWLNative, distributor, dai, niftsy20, weth, ERC721Distr):
    
    
    #token is claimed. try to claim again
    with reverts("ERC721: operator query for nonexistent token"):
        launcpadWLNative.claimNFT(1, zero_address, {"value": '0.01 ether'})

    #not allowed token to pay
    with reverts("Cant pay with this ERC20"):
        launcpadWLNative.claimNFT(2, weth)

    #not enough tokens
    dai.transfer(accounts[1], dai.balanceOf(accounts[0]) - 1, {"from": accounts[0]})
    payAmount = launcpadWLNative.getWNFTPrice(2, dai)
    dai.approve(launcpadWLNative, payAmount, {"from": accounts[0]})
    with reverts("ERC20: transfer amount exceeds balance"):
        launcpadWLNative.claimNFT(2, dai)

    #enough tokens and send ether
    dai.transfer(accounts[0], payAmount, {"from": accounts[1]})
    bbDAI0 = dai.balanceOf(accounts[0])
    bbeL = launcpadWLNative.balance()
    with reverts("No need ether"):
        launcpadWLNative.claimNFT(2, dai, {"value": '1 ether'})
    launcpadWLNative.claimNFT(2, dai, {"from": accounts[0]})
    assert dai.balanceOf(accounts[0]) == bbDAI0 - launcpadWLNative.getWNFTPrice(2, dai)
    assert dai.balanceOf(launcpadWLNative) == launcpadWLNative.getWNFTPrice(2, dai)
    #assert launcpadWLNative.balance() == bbeL + Wei('1 ether')
    assert launcpadWLNative.balance() == bbeL 
    assert distributor.balanceOf(launcpadWLNative) == COUNT - 2
    assert distributor.balanceOf(accounts[0]) == 1

    #unwrap claimed token
    bbe0 = accounts[0].balance()
    
    bbeD = distributor.balance()

    distributor.unWrap721(2)

    assert bbe0 + Wei(ETH_AMOUNT)/COUNT == accounts[0].balance()

    assert bbeD - Wei(ETH_AMOUNT)/COUNT == distributor.balance()

    assert distributor.balanceOf(accounts[0]) == 0


# claim with allocation
def test_claim_allocation(accounts,  launcpadWLNative, distributor, dai, niftsy20, weth, ERC721Distr, whitelist):
    with reverts("White list is NOT active"):
        launcpadWLNative.claimNFT(3, {"from": accounts[1]})

    with reverts("Ownable: caller is not the owner"):
        launcpadWLNative.setAllocationList(whitelist.address, {"from": accounts[1]})

    launcpadWLNative.setAllocationList(whitelist.address, {"from": accounts[0]})

    with reverts("Too low allocation"):
        launcpadWLNative.claimNFT(3, {"from": accounts[1]})

    whitelist.increaseAllocation(accounts[1], zero_address, Wei(ETH_AMOUNT)/20, {"from": accounts[0]})
    logging.info(whitelist.availableAllocation(accounts[1], zero_address))
    #there is allocation, but not tradable token
    with reverts("Too low allocation"):
        launcpadWLNative.claimNFT(3, {"from": accounts[1]})

    #there is allocation in tradable token
    whitelist.increaseAllocation(accounts[1],zero_address, 3*Wei(ETH_AMOUNT)/10, {"from": accounts[0]})
    logging.info(whitelist.availableAllocation(accounts[1], zero_address))
    logging.info(whitelist.availableAllocation(accounts[1], zero_address))
    launcpadWLNative.claimNFT(3, {"from": accounts[1]})


    assert distributor.ownerOf(3) == accounts[1]
    assert whitelist.availableAllocation(accounts[1], zero_address) == 5*Wei(ETH_AMOUNT)/20

    whitelist.decreaseAllocation(accounts[1], zero_address, 2*Wei(ETH_AMOUNT)/10, {"from": accounts[0]})
    assert whitelist.availableAllocation(accounts[1], zero_address) == 0.5*Wei(ETH_AMOUNT)/10
    with reverts("Too low allocation"):
        launcpadWLNative.claimNFT(4, {"from": accounts[1]})

def test_claim_allocation_1(accounts,  launcpadWLNative, distributor, dai, niftsy20, weth, ERC721Distr, whitelist):

    whitelist.increaseAllocationBatch([accounts[2], accounts[3]], zero_address, [Wei(ETH_AMOUNT)/10, 2*Wei(ETH_AMOUNT)/10], {"from": accounts[0]})
    assert whitelist.availableAllocation(accounts[2], zero_address) == Wei(ETH_AMOUNT)/10
    assert whitelist.availableAllocation(accounts[3], zero_address) == 2*Wei(ETH_AMOUNT)/10

    whitelist.decreaseAllocationBatch([accounts[2], accounts[3]], zero_address, [0.4*Wei(ETH_AMOUNT)/10, Wei(ETH_AMOUNT)/10], {"from": accounts[0]})
    assert whitelist.availableAllocation(accounts[2], zero_address) == 0.6*Wei(ETH_AMOUNT)/10
    assert whitelist.availableAllocation(accounts[3], zero_address) == Wei(ETH_AMOUNT)/10


