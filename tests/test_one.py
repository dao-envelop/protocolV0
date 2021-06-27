import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

# def test_first(pool_repo):
# 	assert pool_repo.getPoolsCount() == '1'
ORIGINAL_NFT_IDs = [10000,11111,22222]
START_NATIVE_COLLATERAL = '1 ether'
ADD_NATIVE_COLLATERAL = '2 ether'
ERC20_COLLATERAL_AMOUNT = 2e17;
TRANSFER_FEE = '2 ether'
ROAYLTY_PERCENT = 10
UNWRAP_FEE_THRESHOLD = 6e18

def test_721mock(accounts, erc721mock):
    assert erc721mock.balanceOf(accounts[0]) == 1
    erc721mock.transferFrom(accounts[0], accounts[1], 0, {'from':accounts[0]})
    assert erc721mock.balanceOf(accounts[1]) == 1
    [erc721mock.mint(x, {'from':accounts[0]})  for x in ORIGINAL_NFT_IDs]
    erc721mock.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[0], {'from':accounts[0]})
    erc721mock.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[2], {'from':accounts[0]})

def test_simple_wrap(accounts, erc721mock, wrapper):
    #Give approve
    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
    wrapper.wrap721(
        erc721mock.address, 
        ORIGINAL_NFT_IDs[0], 
        0, 
        1e18,
        '0x0000000000000000000000000000000000000000',
        0,
        0, 
        {'from':accounts[1]})
    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == wrapper.address

def test_check_uri(accounts, erc721mock, wrapper, niftsy20):
    
    logging.info('wrapper.ownerOf(0) {}'.format(
        wrapper.ownerOf(wrapper.lastWrappedNFTId())
    ))

    logging.info('erc721mock.ownerOf(0) {}'.format(
        erc721mock.ownerOf(0)
    ))

    logging.info('URI from wrapped {}'.format(
        wrapper.tokenURI(wrapper.lastWrappedNFTId())
    ))

    assert wrapper.tokenURI(wrapper.lastWrappedNFTId()) ==  erc721mock.tokenURI(ORIGINAL_NFT_IDs[0]) 
    #Aprrove for transfer
    #niftsy20.approve(wrapper.address, 1e25,  {'from':accounts[0]})
    #Aprrove for mint (Transfer from zero)
    #niftsy20.approve(wrapper.address, 1e25,  {'from':accounts[1]})
    #transfer wrapped "LP" to accounts[0] with erc20 fee
    with reverts('insufficient NIFTSY balance for fee'):
        wrapper.transferFrom(accounts[1], accounts[0], wrapper.lastWrappedNFTId(), {'from':accounts[1]})
    

    niftsy20.transfer(accounts[1], 10e18,  {'from':accounts[0]})
    wrapper.transferFrom(accounts[1], accounts[0], wrapper.lastWrappedNFTId(), {'from':accounts[1]})    
    assert wrapper.ownerOf(wrapper.lastWrappedNFTId()) == accounts[0]

    assert wrapper.getTokenValue(wrapper.lastWrappedNFTId()) == (0, wrapper.getWrappedToken(wrapper.lastWrappedNFTId())[3])

def test_simple_unwrap(accounts, erc721mock, wrapper):
    #Give approve
    wrapper.unWrap721(wrapper.lastWrappedNFTId(), {'from':accounts[0]})
    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[0]  

def test_ether_wrap(accounts, erc721mock, wrapper):
    #Give approve
    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[1], {'from':accounts[0]})
    logging.info('lastWrappedNFTId before wrap {}'.format(wrapper.lastWrappedNFTId()))
    wrapper.wrap721(
        erc721mock.address, 
        ORIGINAL_NFT_IDs[1], 
        0, 
        2e18,
        '0x0000000000000000000000000000000000000000',
        0,
        0, 
        {'from':accounts[0], 'value':'1 ether'})
    #assert erc721mock.balanceOf(accounts[0]) == 0
    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[1]) == wrapper.address 
    assert wrapper.balance() == '1 ether' 
    assert wrapper.getTokenValue(wrapper.lastWrappedNFTId()) == ('1 ether', 0)
    logging.info('URI from wrapped {}'.format(
        wrapper.tokenURI(wrapper.lastWrappedNFTId())
    ))
    logging.info('getWrappedToken {}'.format(
        wrapper.getWrappedToken(wrapper.lastWrappedNFTId())
    ))

def test_add_collateral(accounts, wrapper):
    native_collateral_before = wrapper.getWrappedToken(wrapper.lastWrappedNFTId())[2]
    tx = wrapper.addNativeCollateral(wrapper.lastWrappedNFTId(), {'from':accounts[0], 'value': ADD_NATIVE_COLLATERAL})
    logging.info('getWrappedToken {}'.format(
        wrapper.getWrappedToken(wrapper.lastWrappedNFTId())
    ))
    assert Wei(wrapper.getWrappedToken(wrapper.lastWrappedNFTId())[2] - native_collateral_before) == Wei(ADD_NATIVE_COLLATERAL)
        
def test_enumerable_features(accounts, wrapper):
    logging.info('tokenByIndex {}'.format(
      wrapper.tokenByIndex(0)
    ))
    logging.info('tokenOfOwnerByIndex {}'.format(
      wrapper.tokenOfOwnerByIndex(accounts[0], 0)
    ))
    


def test_ether_unwrap(accounts, erc721mock, wrapper, niftsy20):
    niftsy20.transfer(accounts[1], 1e21,  {'from':accounts[0]})
    wrapper.transferFrom(accounts[0], accounts[1], 2, {'from':accounts[0]})
    wrapper.transferFrom(accounts[1], accounts[0], 2, {'from':accounts[1]})
    wrapper.transferFrom(accounts[0], accounts[1], 2, {'from':accounts[0]})
    wrapper.transferFrom(accounts[1], accounts[0], 2, {'from':accounts[1]})

    ethBefore = accounts[0].balance()
    logging.info('user Ether before unwrapp {}'.format(
        Wei(ethBefore).to('ether')
    ))
    
    token_value = wrapper.getTokenValue(wrapper.lastWrappedNFTId())
    logging.info('Token collateral before Unwrap (eth={}, NIFTSY= {}'.format(
        Wei(token_value[0]).to('ether'),
        Wei(token_value[1]).to('ether')
    ))
    niftsy20_balance_Before_unwrap = niftsy20.balanceOf(accounts[0])
    collateral = wrapper.getWrappedToken(wrapper.lastWrappedNFTId())[2]
    wrapper.unWrap721(wrapper.lastWrappedNFTId(), {'from':accounts[0]})
    logging.info('user Ether After unwrapp {}'.format(
        Wei((accounts[0].balance() - ethBefore)).to('ether')
    ))
    #assert erc721mock.balanceOf(accounts[0]) == 1
    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[1]) == accounts[0]
    assert wrapper.balance() == 0
    assert (accounts[0].balance() - ethBefore) == collateral 
    assert  niftsy20.balanceOf(accounts[0]) - niftsy20_balance_Before_unwrap == 8e18


def test_advanced_wrap(accounts, erc721mock, wrapper, niftsy20, dai):
    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[2], {'from':accounts[1]})
    tx = wrapper.wrap721(
        erc721mock.address, 
        ORIGINAL_NFT_IDs[2], 
        chain.time() + 100, #unwrapAfter
        TRANSFER_FEE, 
        accounts[2], #_royaltyBeneficiary
        ROAYLTY_PERCENT, #_royaltyPercent
        UNWRAP_FEE_THRESHOLD, 
        {'from':accounts[1], 'value':START_NATIVE_COLLATERAL}
    )
    logging.info('getWrappedToken {}'.format(
        wrapper.getWrappedToken(wrapper.lastWrappedNFTId())
    ))
    wrapper.transferFrom(accounts[1], accounts[0], wrapper.lastWrappedNFTId(), {'from':accounts[1]})
    with reverts("Cant unwrap before day X"):
        wrapper.unWrap721(wrapper.lastWrappedNFTId(), {'from':accounts[0]})
    
    logging.info('Time machine running.....+100 sec...............')
    chain.sleep(100)
    chain.mine()
    logging.info('Chain time {}'.format( chain.time()))
    with reverts("Cant unwrap due Fee Threshold"):
        wrapper.unWrap721(wrapper.lastWrappedNFTId(), {'from':accounts[0]})    
    wrapper.addNativeCollateral(wrapper.lastWrappedNFTId(), {'from':accounts[0], 'value': ADD_NATIVE_COLLATERAL})
    dai.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {'from':accounts[0]})
    niftsy20.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {'from':accounts[0]})
    wrapper.addERC20Collateral(wrapper.lastWrappedNFTId(),niftsy20.address, ERC20_COLLATERAL_AMOUNT ,{'from':accounts[0]})
    wrapper.addERC20Collateral(wrapper.lastWrappedNFTId(),dai.address, ERC20_COLLATERAL_AMOUNT ,{'from':accounts[0]})
    logging.info(wrapper.getERC20Collateral(wrapper.lastWrappedNFTId())) 
    wrapper.transferFrom(accounts[0], accounts[1], wrapper.lastWrappedNFTId(), {'from':accounts[0]})
    wrapper.transferFrom(accounts[1], accounts[0], wrapper.lastWrappedNFTId(), {'from':accounts[1]})
    tx = wrapper.transferFrom(accounts[0], accounts[3], wrapper.lastWrappedNFTId(), {'from':accounts[0]})
    logging.info('NiftsyProtocolTransfer={}'.format(tx.events['NiftsyProtocolTransfer']))
    token_before_unwrap = wrapper.getWrappedToken(wrapper.lastWrappedNFTId())
    logging.info('getWrappedToken {}'.format(token_before_unwrap))
    ethBefore = accounts[3].balance()
    tx = wrapper.unWrap721(wrapper.lastWrappedNFTId(), {'from':accounts[3]})
    logging.info('wrapper.unWrap721 Transfer events={}'.format(tx.events))
    logging.info('Niftsy20 balance of Wrapper={}'.format(niftsy20.balanceOf(wrapper)))
    assert niftsy20.balanceOf(accounts[3]) == token_before_unwrap[3] + ERC20_COLLATERAL_AMOUNT
    assert accounts[3].balance() == Wei(ethBefore) + Wei(START_NATIVE_COLLATERAL) + Wei(ADD_NATIVE_COLLATERAL)
    assert niftsy20.balanceOf(wrapper) == 0
    assert dai.balanceOf(wrapper) == 0
    assert dai.balanceOf(accounts[3]) == ERC20_COLLATERAL_AMOUNT


def test_ERC165_helper(accounts, erc721mock, wrapper):
    assert wrapper.isERC721(wrapper.address, 0x80ac58cd)
    assert wrapper.isERC721(wrapper.address, 0x5b5e139f)
    assert wrapper.isERC721(erc721mock.address, 0x80ac58cd)


def test_hacker_ok(accounts, mockHacker):
    mockHacker.setFailSender(accounts[0], {'from':accounts[0]})
    with reverts('Hack your Wrapper'):
        mockHacker.transfer(accounts[1], 1)    

def test_add_hacker_collateral(accounts, mockHacker, erc721mock, wrapper, niftsy20, dai):
    mockHacker.setFailSender(wrapper.address, {'from':accounts[0]})
    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[2], {'from':accounts[3]})
    tx = wrapper.wrap721(
        erc721mock.address, 
        ORIGINAL_NFT_IDs[2], 
        0, #unwrapAfter
        TRANSFER_FEE, 
        accounts[2], #_royaltyBeneficiary
        ROAYLTY_PERCENT, #_royaltyPercent
        0,#UNWRAP_FEE_THRESHOLD, 
        {'from':accounts[3], 'value':START_NATIVE_COLLATERAL}
    )
    wrapper.transferFrom(accounts[3], accounts[0], wrapper.lastWrappedNFTId(), {'from':accounts[3]})
    wrapper.addNativeCollateral(wrapper.lastWrappedNFTId(), {'from':accounts[0], 'value': ADD_NATIVE_COLLATERAL})
    dai.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {'from':accounts[0]})
    mockHacker.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {'from':accounts[0]})
    wrapper.addERC20Collateral(wrapper.lastWrappedNFTId(),mockHacker.address, ERC20_COLLATERAL_AMOUNT ,{'from':accounts[0]})
    wrapper.addERC20Collateral(wrapper.lastWrappedNFTId(),dai.address, ERC20_COLLATERAL_AMOUNT ,{'from':accounts[0]})
    logging.info(wrapper.getERC20Collateral(wrapper.lastWrappedNFTId())) 
    wrapper.transferFrom(accounts[0], accounts[1], wrapper.lastWrappedNFTId(), {'from':accounts[0]})
    wrapper.transferFrom(accounts[1], accounts[0], wrapper.lastWrappedNFTId(), {'from':accounts[1]})
    tx = wrapper.transferFrom(accounts[0], accounts[3], wrapper.lastWrappedNFTId(), {'from':accounts[0]})
    logging.info('NiftsyProtocolTransfer={}'.format(tx.events['NiftsyProtocolTransfer']))
    token_before_unwrap = wrapper.getWrappedToken(wrapper.lastWrappedNFTId())
    logging.info('getWrappedToken {}'.format(token_before_unwrap))
    ethBefore = accounts[3].balance()
    tx = wrapper.unWrap721(wrapper.lastWrappedNFTId(), {'from':accounts[3]})
    logging.info('wrapper.unWrap721 Transfer events={}'.format(tx.events))
    assert dai.balanceOf(wrapper) == 0
    assert mockHacker.balanceOf(wrapper) == ERC20_COLLATERAL_AMOUNT
