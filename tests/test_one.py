import pytest
import logging
from brownie import Wei, reverts
LOGGER = logging.getLogger(__name__)

# def test_first(pool_repo):
# 	assert pool_repo.getPoolsCount() == '1'

def test_721mock(accounts, erc721mock):
    assert erc721mock.balanceOf(accounts[0]) == 1
    erc721mock.transferFrom(accounts[0], accounts[1], 0, {'from':accounts[0]})
    assert erc721mock.balanceOf(accounts[1]) == 1

def test_simple_wrap(accounts, erc721mock, wrapper):
    #Give approve
    erc721mock.approve(wrapper.address, 0, {'from':accounts[1]})
    wrapper.wrap721(erc721mock.address, 0, 0, 1e18, {'from':accounts[1]})
    assert erc721mock.balanceOf(accounts[1]) == 0
    assert erc721mock.ownerOf(0) == wrapper.address

def test_check_uri(accounts, erc721mock, wrapper, niftsy20):
    
    logging.info('wrapper.ownerOf(0) {}'.format(
        wrapper.ownerOf(wrapper.ourId())
    ))

    # logging.info('wrapper.ownerOf(1) {}'.format(
    #     wrapper.ownerOf(1)
    # ))

    logging.info('erc721mock.ownerOf(0) {}'.format(
        erc721mock.ownerOf(0)
    ))

    logging.info('URI from wrapped {}'.format(
        wrapper.tokenURI(wrapper.ourId())
    ))

    assert wrapper.tokenURI(wrapper.ourId()) ==  erc721mock.tokenURI(0) 
    #Aprrove for transfer
    #niftsy20.approve(wrapper.address, 1e25,  {'from':accounts[0]})
    #Aprrove for mint (Transfer from zero)
    #niftsy20.approve(wrapper.address, 1e25,  {'from':accounts[1]})
    #transfer wrapped "LP" to accounts[0] with erc20 fee
    wrapper.transferFrom(accounts[1], accounts[0], wrapper.ourId(), {'from':accounts[1]})
    assert wrapper.ownerOf(wrapper.ourId()) == accounts[0]

    assert wrapper.getTokenValue(wrapper.ourId()) == (0, wrapper.getWrappedToken(wrapper.ourId())[3])

def test_simple_unwrap(accounts, erc721mock, wrapper):
    #Give approve
    wrapper.unWrap721(wrapper.ourId(), {'from':accounts[0]})
    assert erc721mock.balanceOf(accounts[1]) == 0
    assert erc721mock.ownerOf(0) == accounts[0]  

def test_ether_wrap(accounts, erc721mock, wrapper):
    #Give approve
    erc721mock.approve(wrapper.address, 0, {'from':accounts[0]})
    logging.info('OurId before wrap {}'.format(wrapper.ourId()))
    wrapper.wrap721(erc721mock.address, 0, 0, 2e18, {'from':accounts[0], 'value':'1 ether'})
    assert erc721mock.balanceOf(accounts[0]) == 0
    assert erc721mock.ownerOf(0) == wrapper.address 
    assert wrapper.balance() == '1 ether' 
    assert wrapper.getTokenValue(wrapper.ourId()) == ('1 ether', 0)
    logging.info('URI from wrapped {}'.format(
        wrapper.tokenURI(wrapper.ourId())
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
    
    token_value = wrapper.getTokenValue(wrapper.ourId())
    logging.info('Token collateral before Unwrap (eth={}, token= {}'.format(
        Wei(token_value[0]).to('ether'),
        Wei(token_value[1]).to('ether')
    ))
    niftsy20_balance_Before_unwrap = niftsy20.balanceOf(accounts[0])
    wrapper.unWrap721(wrapper.ourId(), {'from':accounts[0]})
    logging.info('user Ether After unwrapp {}'.format(
        Wei((accounts[0].balance() - ethBefore)).to('ether')
    ))
    assert erc721mock.balanceOf(accounts[0]) == 1
    assert erc721mock.ownerOf(0) == accounts[0]
    assert wrapper.balance() == 0
    assert (accounts[0].balance() - ethBefore) == 1e18 
    assert  niftsy20.balanceOf(accounts[0]) - niftsy20_balance_Before_unwrap == 8e18  