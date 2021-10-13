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
def test_distr(accounts,  distributor, niftsy20, dai, launcpad, ERC721Distr, weth):
    RECEIVERS = [launcpad.address for x in range(COUNT)]
    for z in range(COUNT):
        #logging.info('z = {}'.format(z))
        #erc721mock.mint(z + 1)
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
    assert distributor.balanceOf(launcpad)==COUNT
    assert weth.balanceOf(distributor.address) == ERC20_COLLATERAL_AMOUNT_WETH * len(RECEIVERS)
    assert niftsy20.balanceOf(distributor.address) == ERC20_COLLATERAL_AMOUNT * len(RECEIVERS)
    assert distributor.balance() == '10 ether'
    assert ERC721Distr.balanceOf(distributor.address) == COUNT

def test_wrapped_props(accounts,  distributor, launcpad, dai, niftsy20, weth):
    for i in  range(distributor.balanceOf(launcpad)):
        logging.info('tokenId={}, erc20Balance={}, {}, ETHBalance = {}'.format(
            distributor.tokenOfOwnerByIndex(launcpad, i),
            Wei(distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpad, i), niftsy20)).to('ether'),
            Wei(distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpad, i), weth)).to('ether'),
            distributor.getTokenValue(distributor.tokenOfOwnerByIndex(launcpad, i))[0]
        ))
        assert distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpad, i), niftsy20)==ERC20_COLLATERAL_AMOUNT        
        assert distributor.getERC20CollateralBalance(distributor.tokenOfOwnerByIndex(launcpad, i), weth)==ERC20_COLLATERAL_AMOUNT_WETH
        assert distributor.getTokenValue(distributor.tokenOfOwnerByIndex(launcpad, i))[0]== Wei(ETH_AMOUNT)/COUNT

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

# claim with ether
def test_claim_Ether(accounts,  launcpad, distributor, dai, niftsy20, weth, ERC721Distr):
    #not enough ether
    with reverts("Received amount less then price"):
        launcpad.claimNFT(1, zero_address, {"value": '0.01 ether'})

    #enough ether and there is the change - claim
    bbe1 = accounts[0].balance()
    payAmount = launcpad.getWNFTPrice(1, zero_address) + Wei(change_amount)
    launcpad.claimNFT(1, zero_address, {"value": payAmount})

    assert accounts[0].balance() == bbe1 - launcpad.getWNFTPrice(1, zero_address)
    assert launcpad.balance() == launcpad.getWNFTPrice(1, zero_address)
    assert distributor.balanceOf(launcpad) == COUNT - 1
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
    assert ERC721Distr.balanceOf(accounts[0]) == 1


# claim with token
def test_claim_token(accounts,  launcpad, distributor, dai, niftsy20, weth, ERC721Distr):
    
    #token is claimed. try to claim again
    with reverts("ERC721: operator query for nonexistent token"):
        launcpad.claimNFT(1, zero_address, {"value": '0.01 ether'})

    #not allowed token to pay
    with reverts("Cant pay with this ERC20"):
        launcpad.claimNFT(2, weth)

    #not enough tokens
    dai.transfer(accounts[1], dai.balanceOf(accounts[0]) - 1, {"from": accounts[0]})
    payAmount = launcpad.getWNFTPrice(2, dai)
    dai.approve(launcpad, payAmount, {"from": accounts[0]})
    with reverts("ERC20: transfer amount exceeds balance"):
        launcpad.claimNFT(2, dai)

    #enough tokens and send ether
    dai.transfer(accounts[0], payAmount, {"from": accounts[1]})
    bbDAI0 = dai.balanceOf(accounts[0])
    bbeL = launcpad.balance()
    launcpad.claimNFT(2, dai, {"value": '1 ether'})

    assert dai.balanceOf(accounts[0]) == bbDAI0 - launcpad.getWNFTPrice(2, dai)
    assert dai.balanceOf(launcpad) == launcpad.getWNFTPrice(2, dai)
    assert launcpad.balance() == bbeL + Wei('1 ether')
    assert distributor.balanceOf(launcpad) == COUNT - 2
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
    assert ERC721Distr.balanceOf(accounts[0]) == 2

def test_withdraw(accounts, launcpad, dai):
    with reverts("Ownable: caller is not the owner"):
        launcpad.withdrawEther({"from": accounts[1]})

    with reverts("Ownable: caller is not the owner"):
        launcpad.withdrawTokens(dai,{"from": accounts[1]})

    bbeL = launcpad.balance()  
    bbe0 = accounts[0].balance()

    bbDAI0 = dai.balanceOf(accounts[0])
    bbDAIL = dai.balanceOf(launcpad)
    
    launcpad.withdrawEther({"from": accounts[0]})
    launcpad.withdrawTokens(dai,{"from": accounts[0]})

    assert dai.balanceOf(launcpad) == 0
    assert launcpad.balance()  == 0
    assert dai.balanceOf(accounts[0]) == bbDAI0 + bbDAIL
    assert accounts[0].balance() == bbeL + bbe0




    #оплата эфиром
    #-  достаточно эфира/недостаточно
    #- образовалась сдача в эфире
    #оплата токенами:
    # - в которых установлена цена
    # - не установлена цена
    # - установлена цена, но недостаточно токенов
    # не наступило время разворачивания
    #все функции потестить - гетеры
    # развернуть токен после выкупа
    # проверить, как работает метод возвращения цены, когда у меня 2 токена в обеспечении


