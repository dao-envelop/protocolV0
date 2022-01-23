import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

ERC20_COLLATERAL_AMOUNT = 100e18
ERC20_COLLATERAL_AMOUNT_WETH = 1000e18
NATIVE_COLLATERAL_AMOUNT = 10
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

    tx = distributor.WrapAndDistrib721WithMint(
        ERC721Distr.address, 
        RECEIVERS,
        ORIGINAL_TOKEN_IDs,
        [],
        UNWRAP_AFTER,
        {'from':accounts[0], 'value': ETH_AMOUNT}
    )
    #logging.info(tx.events)
    #ids=[distributor.tokenURI(x['wrappedTokenId']) for x in tx.events['Wrapped']]
    #logging.info(ids)
    assert len(tx.events['Wrapped']) == len(RECEIVERS)
    assert distributor.balanceOf(launcpadWLNative)==COUNT
    assert distributor.balance() == ETH_AMOUNT
    assert ERC721Distr.balanceOf(distributor.address) == COUNT

def test_wrapped_props(accounts,  distributor, launcpadWLNative, dai, niftsy20, weth):
    for i in  range(distributor.balanceOf(launcpadWLNative)):
        logging.info('tokenId={}, ETHBalance = {}'.format(
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
        logging.info('tokenId={},\n erc20Balance={},\n priceErc20={},\n priceETH={}'.format(
            distributor.tokenOfOwnerByIndex(launcpadWLNative, i),
            distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpadWLNative, i), niftsy20),
            Wei(p1).to('ether'), Wei(p2).to('ether')
        ))
    assert launcpadWLNative.getWNFTPrice(1, dai) == distributor.getTokenValue(1)[0] * launcpadWLNative.priceForOneCollateralUnit(dai)[0]/launcpadWLNative.priceForOneCollateralUnit(dai)[1]

# claim with ether
def test_claim_Ether(accounts,  launcpadWLNative, distributor, dai, niftsy20, weth, ERC721Distr):
    #not enough ether
    with reverts("Received amount less then price"):
        launcpadWLNative.claimNFT(1, zero_address, {"value": '0.000001 ether'})

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
    bbw0 = weth.balanceOf(accounts[0])
    
    bbeD = distributor.balance()
    bbnD = niftsy20.balanceOf(distributor)
    bbwD = weth.balanceOf(distributor)

    distributor.unWrap721(1)

    assert bbe0 + Wei(ETH_AMOUNT)/COUNT == accounts[0].balance()

    assert bbeD - Wei(ETH_AMOUNT)/COUNT == distributor.balance()

    assert distributor.balanceOf(accounts[0]) == 0
    assert ERC721Distr.balanceOf(accounts[0]) == 1


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
    assert ERC721Distr.balanceOf(accounts[0]) == 2

def test_withdraw(accounts, launcpadWLNative, dai):
    with reverts("Ownable: caller is not the owner"):
        launcpadWLNative.withdrawEther({"from": accounts[1]})

    bbeL = launcpadWLNative.balance()  
    bbe0 = accounts[0].balance()
    
    launcpadWLNative.withdrawEther({"from": accounts[0]})

    assert launcpadWLNative.balance()  == 0
    assert accounts[0].balance() == bbeL + bbe0

def test_claim_WL(accounts,  launcpadWLNative, distributor, dai, niftsy20, whitelist, ERC721Distr):
    with reverts("White list is NOT active"):
        launcpadWLNative.claimNFT(3,{'from':accounts[0]})
    launcpadWLNative.setAllocationList(whitelist)
    with reverts("Too low allocation"):
        launcpadWLNative.claimNFT(3,{'from':accounts[0]})
    whitelist.increaseAllocation(accounts[0], zero_address, NATIVE_COLLATERAL_AMOUNT * 1e18)
    whitelist.setOperator(launcpadWLNative, True)
    assert launcpadWLNative.getAvailableAllocation(accounts[0]) == NATIVE_COLLATERAL_AMOUNT * 1e18
    tx  = launcpadWLNative.claimNFT(3,{'from':accounts[0]})
    assert launcpadWLNative.getAvailableAllocation(accounts[0]) == (NATIVE_COLLATERAL_AMOUNT -1) * 1e18

    before_balance = distributor.balance()
    before_balance_acc = accounts[0].balance()

    distributor.unWrap721(3, {"from" :accounts[0]})

    assert ERC721Distr.ownerOf(2) == accounts[0]
    assert before_balance_acc -  Wei(ETH_AMOUNT)/COUNT < accounts[0].balance()


