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
def test_distr(accounts,  distributor, niftsy20, dai, launcpadWL, ERC721Distr, weth):
    RECEIVERS = [launcpadWL.address for x in range(COUNT)]
    for z in range(COUNT):
        #logging.info('z = {}'.format(z))
        #erc721mock.mint(z + 1)
        ORIGINAL_TOKEN_IDs.append(z)

    niftsy20.approve(distributor, ERC20_COLLATERAL_AMOUNT * len(RECEIVERS), {'from':accounts[0]})
    weth.approve(distributor, ERC20_COLLATERAL_AMOUNT_WETH * len(RECEIVERS), {'from':accounts[0]})

    with reverts("Only for distributors"):
        distributor.WrapAndDistribEmpty( 
        RECEIVERS,
        [(niftsy20.address,ERC20_COLLATERAL_AMOUNT), (weth.address,ERC20_COLLATERAL_AMOUNT_WETH)],
        UNWRAP_AFTER,
        {'from':accounts[1], 'value':ETH_AMOUNT})

    tx = distributor.WrapAndDistribEmpty( 
        RECEIVERS,
        [(niftsy20.address,ERC20_COLLATERAL_AMOUNT), (weth.address,ERC20_COLLATERAL_AMOUNT_WETH)],
        UNWRAP_AFTER,
        {'from':accounts[0], 'value':ETH_AMOUNT})

    #logging.info(tx.events)
    #ids=[distributor.tokenURI(x['wrappedTokenId']) for x in tx.events['Wrapped']]
    #logging.info(ids)
    assert len(tx.events['Wrapped']) == len(RECEIVERS)
    assert distributor.balanceOf(launcpadWL)==COUNT
    assert weth.balanceOf(distributor.address) == ERC20_COLLATERAL_AMOUNT_WETH * len(RECEIVERS)
    assert niftsy20.balanceOf(distributor.address) == ERC20_COLLATERAL_AMOUNT * len(RECEIVERS)
    assert distributor.balance() == '10 ether'
    assert distributor.getWrappedToken(1)[0] == zero_address
    assert distributor.getWrappedToken(1)[1] == 0

def test_wrapped_props(accounts,  distributor, launcpadWL, dai, niftsy20, weth):
    for i in  range(distributor.balanceOf(launcpadWL)):
        logging.info('tokenId={}, erc20Balance={}, {}, ETHBalance = {}'.format(
            distributor.tokenOfOwnerByIndex(launcpadWL, i),
            Wei(distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpadWL, i), niftsy20)).to('ether'),
            Wei(distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpadWL, i), weth)).to('ether'),
            distributor.getTokenValue(distributor.tokenOfOwnerByIndex(launcpadWL, i))[0]
        ))
        assert distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpadWL, i), niftsy20)==ERC20_COLLATERAL_AMOUNT        
        assert distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpadWL, i), weth)==ERC20_COLLATERAL_AMOUNT_WETH
        assert distributor.getTokenValue(distributor.tokenOfOwnerByIndex(launcpadWL, i))[0]== Wei(ETH_AMOUNT)/COUNT

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
    assert launcpadWL.getWNFTPrice(1, dai) == distributor.getERC20CollateralBalance(1, niftsy20) * launcpadWL.priceForOneCollateralUnit(dai)[0]/launcpadWL.priceForOneCollateralUnit(dai)[1]

# claim with ether
def test_claim_Ether(accounts,  launcpadWL, distributor, dai, niftsy20, weth, ERC721Distr):
    #not enough ether
    with reverts("Received amount less then price"):
        launcpadWL.claimNFT(1, zero_address, {"value": '0.01 ether'})

    #enough ether and there is the change - claim
    bbe1 = accounts[0].balance()
    payAmount = launcpadWL.getWNFTPrice(1, zero_address) + Wei(change_amount)
    launcpadWL.claimNFT(1, zero_address, {"value": payAmount})

    assert accounts[0].balance() == bbe1 - launcpadWL.getWNFTPrice(1, zero_address)
    assert launcpadWL.balance() == launcpadWL.getWNFTPrice(1, zero_address)
    assert distributor.balanceOf(launcpadWL) == COUNT - 1
    assert distributor.balanceOf(accounts[0]) == 1

    #unwrap claimed token
    bbe0 = accounts[0].balance()
    bbn0 = niftsy20.balanceOf(accounts[0])
    bbw0 = weth.balanceOf(accounts[0])
    
    bbeD = distributor.balance()
    bbnD = niftsy20.balanceOf(distributor)
    bbwD = weth.balanceOf(distributor)

    distributor.unWrap721(1)

    assert bbe0 + Wei(ETH_AMOUNT)/COUNT == accounts[0].balance()
    assert bbn0 + ERC20_COLLATERAL_AMOUNT == niftsy20.balanceOf(accounts[0])
    assert bbw0 + ERC20_COLLATERAL_AMOUNT_WETH == weth.balanceOf(accounts[0])

    assert bbeD - Wei(ETH_AMOUNT)/COUNT == distributor.balance()
    assert bbnD - ERC20_COLLATERAL_AMOUNT == niftsy20.balanceOf(distributor)
    assert bbwD - ERC20_COLLATERAL_AMOUNT_WETH == weth.balanceOf(distributor)

    assert distributor.balanceOf(accounts[0]) == 0


# claim with token
def test_claim_token(accounts,  launcpadWL, distributor, dai, niftsy20, weth, ERC721Distr):
    
    #token is claimed. try to claim again
    with reverts("ERC721: operator query for nonexistent token"):
        launcpadWL.claimNFT(1, zero_address, {"value": '0.01 ether'})

    #not allowed token to pay
    with reverts("Cant pay with this ERC20"):
        launcpadWL.claimNFT(2, weth)

    #not enough tokens
    dai.transfer(accounts[1], dai.balanceOf(accounts[0]) - 1, {"from": accounts[0]})
    payAmount = launcpadWL.getWNFTPrice(2, dai)
    dai.approve(launcpadWL, payAmount, {"from": accounts[0]})
    with reverts("ERC20: transfer amount exceeds balance"):
        launcpadWL.claimNFT(2, dai)

    #enough tokens and send ether
    dai.transfer(accounts[0], payAmount, {"from": accounts[1]})
    bbDAI0 = dai.balanceOf(accounts[0])
    bbeL = launcpadWL.balance()
    with reverts("No need ether"):
        launcpadWL.claimNFT(2, dai, {"value": '1 ether'})
    launcpadWL.claimNFT(2, dai, {"from": accounts[0]})
    assert dai.balanceOf(accounts[0]) == bbDAI0 - launcpadWL.getWNFTPrice(2, dai)
    assert dai.balanceOf(launcpadWL) == launcpadWL.getWNFTPrice(2, dai)
    #assert launcpadWL.balance() == bbeL + Wei('1 ether')
    assert launcpadWL.balance() == bbeL 
    assert distributor.balanceOf(launcpadWL) == COUNT - 2
    assert distributor.balanceOf(accounts[0]) == 1

    #unwrap claimed token
    bbe0 = accounts[0].balance()
    bbn0 = niftsy20.balanceOf(accounts[0])
    bbw0 = weth.balanceOf(accounts[0])
    
    bbeD = distributor.balance()
    bbnD = niftsy20.balanceOf(distributor)
    bbwD = weth.balanceOf(distributor)

    distributor.unWrap721(2)

    assert bbe0 + Wei(ETH_AMOUNT)/COUNT == accounts[0].balance()
    assert bbn0 + ERC20_COLLATERAL_AMOUNT == niftsy20.balanceOf(accounts[0])
    assert bbw0 + ERC20_COLLATERAL_AMOUNT_WETH == weth.balanceOf(accounts[0])

    assert bbeD - Wei(ETH_AMOUNT)/COUNT == distributor.balance()
    assert bbnD - ERC20_COLLATERAL_AMOUNT == niftsy20.balanceOf(distributor)
    assert bbwD - ERC20_COLLATERAL_AMOUNT_WETH == weth.balanceOf(distributor)

    assert distributor.balanceOf(accounts[0]) == 0


# claim with allocation
def test_claim_allocation(accounts,  launcpadWL, distributor, dai, niftsy20, weth, ERC721Distr, whitelist):
    with reverts("White list is NOT active"):
        launcpadWL.claimNFT(3, {"from": accounts[1]})

    with reverts("Ownable: caller is not the owner"):
        launcpadWL.setAllocationList(whitelist.address, {"from": accounts[1]})

    launcpadWL.setAllocationList(whitelist.address, {"from": accounts[0]})

    with reverts("Too low allocation"):
        launcpadWL.claimNFT(3, {"from": accounts[1]})

    with reverts("Trusted operators only"):
        whitelist.increaseAllocation(accounts[1], weth.address, ERC20_COLLATERAL_AMOUNT_WETH, {"from": accounts[1]})

    whitelist.increaseAllocation(accounts[1], weth.address, ERC20_COLLATERAL_AMOUNT_WETH, {"from": accounts[0]})

    #there is allocation, but not tradable token
    with reverts("Too low allocation"):
        launcpadWL.claimNFT(3, {"from": accounts[1]})

    #there is allocation in tradable token
    whitelist.increaseAllocation(accounts[1], niftsy20.address, 3*ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
    launcpadWL.claimNFT(3, {"from": accounts[1]})

    assert distributor.ownerOf(3) == accounts[1]
    assert whitelist.availableAllocation(accounts[1], niftsy20.address) == 2*ERC20_COLLATERAL_AMOUNT
    assert whitelist.availableAllocation(accounts[1], weth.address) == ERC20_COLLATERAL_AMOUNT_WETH

    with reverts("Trusted operators only"):
        whitelist.spendAllocation(accounts[1], niftsy20.address, 1, {"from": accounts[2]})

    with reverts("Trusted operators only"):
        whitelist.decreaseAllocation(accounts[1], niftsy20.address, 1, {"from": accounts[2]})

    whitelist.decreaseAllocation(accounts[1], niftsy20.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
    assert whitelist.availableAllocation(accounts[1], niftsy20.address) == ERC20_COLLATERAL_AMOUNT


