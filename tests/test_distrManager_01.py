import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

ERC20_COLLATERAL_AMOUNT = 2e16
TIMELOCK = 3600*24*30
TICKET_VALID =  3600*24*30*12

def test_init(accounts, distrManager, dai):
    distrManager.addTarif((dai, ERC20_COLLATERAL_AMOUNT, TIMELOCK, TICKET_VALID ) , {'from':accounts[0]})
    assert distrManager.ticketsOnSale(0)[0] == dai.address

def test_buy(accounts, distrManager, dai, distributor):
    dai.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT)
    dai.approve(distrManager, ERC20_COLLATERAL_AMOUNT, {'from':accounts[1]})
    with reverts("Only for distributors"):
        distrManager.buyTicket(0, {'from':accounts[1]})
    distributor.setDistributorState(distrManager, True, {'from':accounts[0]})        
    distributor.transferOwnership(distrManager, {'from':accounts[0]})
    distrManager.buyTicket(0, {'from':accounts[1]})
    assert distrManager.validDistributors(accounts[1]) > 0
    assert distributor.distributors(accounts[1]) == True       

# def test_distr(accounts, ERC721Distr, distributor, weth, dai):
#     global RECEIVERS
#     RECEIVERS = [accounts.add() for x in ORIGINAL_NFT_IDs]
#     weth.approve(distributor, ERC20_COLLATERAL_AMOUNT * len(ORIGINAL_NFT_IDs), {'from':accounts[0]})
#     dai.approve(distributor, ERC20_COLLATERAL_AMOUNT * len(ORIGINAL_NFT_IDs), {'from':accounts[0]})
#     ERC721Distr.setMinter(distributor.address, {"from": accounts[0]})
#     tx = distributor.WrapAndDistrib721WithMint(
#         ERC721Distr.address, 
#         RECEIVERS,
#         ORIGINAL_NFT_IDs, 
#         [(weth.address,ERC20_COLLATERAL_AMOUNT), (dai.address,ERC20_COLLATERAL_AMOUNT)],
#         UNWRAP_AFTER,
#         {'from':accounts[0]}
#     )

#     assert len(tx.events['Wrapped']) == len(ORIGINAL_NFT_IDs)
#     assert distributor.balanceOf(RECEIVERS[0])==1

# def test_wrapped_props(accounts,  distributor, weth, dai):
#     logging.info(distributor.getERC20Collateral(5))
#     assert distributor.getERC20Collateral(5)[0][0] == weth.address
#     assert distributor.getERC20Collateral(5)[1][0] == dai.address
#     assert distributor.getERC20Collateral(5)[0][1] == ERC20_COLLATERAL_AMOUNT
#     assert distributor.getERC20Collateral(5)[1][1] == ERC20_COLLATERAL_AMOUNT

# def test_unwrap(accounts, ERC721Distr, distributor, weth, dai):
#     # logging.info('{} {} {} {} {} {} {} {} {}'.format(
#     #     accounts[10], accounts[11], accounts[12], accounts[13], accounts[14], accounts[15],
#     #     accounts[16], accounts[17], accounts[18],
#     # ))
#     logging.info('Owner of wrapped {} is {}'.format(4, distributor.ownerOf(4)))
#     distributor.transferFrom(
#         RECEIVERS[RECEIVERS.index(distributor.ownerOf(4))], 
#         accounts[5], 
#         4, 
#        {'from':RECEIVERS[RECEIVERS.index(distributor.ownerOf(4))]}
#     )
#     tx = distributor.unWrap721(4, {'from':accounts[5]})
#     assert ERC721Distr.balanceOf(accounts[5]) == 1
#     assert weth.balanceOf(accounts[5]) == ERC20_COLLATERAL_AMOUNT
#     assert dai.balanceOf(accounts[5]) == ERC20_COLLATERAL_AMOUNT
#     logging.info(tx.events)

