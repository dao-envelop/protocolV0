import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

ERC20_COLLATERAL_AMOUNT = 2e16
UNWRAP_AFTER = 0
COUNT=40
zero_address = '0x0000000000000000000000000000000000000000'
def test_distr(accounts,  distributor, weth, dai):
    RECEIVERS = [accounts.add() for x in range(COUNT)]
    global R_LIST
    R_LIST = RECEIVERS
    weth.approve(distributor, ERC20_COLLATERAL_AMOUNT * len(RECEIVERS), {'from':accounts[0]})
    dai.approve(distributor, ERC20_COLLATERAL_AMOUNT * len(RECEIVERS), {'from':accounts[0]})
    tx = distributor.WrapAndDistribEmpty(
        RECEIVERS,
        [(weth.address,ERC20_COLLATERAL_AMOUNT), (dai.address,ERC20_COLLATERAL_AMOUNT)],
        UNWRAP_AFTER,
        {'from':accounts[0]}
    )
    logging.info(tx.events)
    #ids=[distributor.tokenURI(x['wrappedTokenId']) for x in tx.events['Wrapped']]
    #logging.info(ids)
    logging.info('RECEIVERS = {}'.format(len(RECEIVERS)))
    assert len(tx.events['Wrapped']) == len(RECEIVERS)
    assert distributor.balanceOf(RECEIVERS[0])==1

def test_wrapped_props(accounts,  distributor, weth, dai):
    logging.info(distributor.getERC20Collateral(5))
    assert distributor.getERC20Collateral(5)[0][0] == weth.address
    assert distributor.getERC20Collateral(5)[1][0] == dai.address
    assert distributor.getERC20Collateral(5)[0][1] == ERC20_COLLATERAL_AMOUNT
    assert distributor.getERC20Collateral(5)[1][1] == ERC20_COLLATERAL_AMOUNT


def test_unwrap(accounts,  distributor, weth, dai):
    # logging.info('{} {} {} {} {} {} {} {} {}'.format(
    #     accounts[10], accounts[11], accounts[12], accounts[13], accounts[14], accounts[15],
    #     accounts[16], accounts[17], accounts[18],
    # ))
    #logging.info(R_LIST)
    logging.info('Owner of wrapped {} is {}, index={}'.format(
        4, 
        distributor.ownerOf(4),
        R_LIST.index(distributor.ownerOf(4))
    ))

    distributor.transferFrom(
        R_LIST[R_LIST.index(distributor.ownerOf(4))], #from
        accounts[5], #to
        4, # tokenId
        {'from':R_LIST[R_LIST.index(distributor.ownerOf(4))]}
    )
    tx = distributor.unWrap721(4, {'from':accounts[5]})
    #assert ERC721Distr.balanceOf(accounts[5]) == 1
    assert weth.balanceOf(accounts[5]) == ERC20_COLLATERAL_AMOUNT
    assert dai.balanceOf(accounts[5]) == ERC20_COLLATERAL_AMOUNT
    logging.info(tx.events)

def test_distr_set(accounts,  distributor):
    with reverts("Ownable: caller is not the owner"):
        distributor.setDistributorState(accounts[1], True, {"from": accounts[1]})

