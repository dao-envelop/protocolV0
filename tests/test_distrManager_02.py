import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

ERC20_COLLATERAL_AMOUNT = 2e16
TIMELOCK = 3600*24*30*12
TICKET_VALID = 3600*24*30
zero_address = '0x0000000000000000000000000000000000000000'

def test_init(accounts, distrManager, dai, distributor):
    with reverts("Ownable: caller is not the owner"):
        distrManager.addTarif((dai, ERC20_COLLATERAL_AMOUNT, TIMELOCK, TICKET_VALID), {'from':accounts[1]})
    distrManager.addTarif((dai, ERC20_COLLATERAL_AMOUNT, TIMELOCK, TICKET_VALID), {'from':accounts[0]})
    assert distrManager.ticketsOnSale(0)[0] == dai.address

def test_distr(accounts, ERC721Distr, distributor, weth, dai, distrManager):
    dai.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT/2)
    dai.approve(distrManager, ERC20_COLLATERAL_AMOUNT/2, {'from':accounts[1]})
    distributor.setDistributorState(distrManager, True, {'from':accounts[0]})   
    distributor.transferOwnership(distrManager, {'from':accounts[0]})     
    distributor.owner() == distrManager.address
    with reverts("ERC20: transfer amount exceeds balance"):
        distrManager.buyTicket(0, {'from':accounts[1]})
    dai.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT/2)
    with reverts("ERC20: transfer amount exceeds allowance"):
        distrManager.buyTicket(0, {'from':accounts[1]})
    dai.approve(distrManager, ERC20_COLLATERAL_AMOUNT, {'from':accounts[1]})
    block_time = chain.time()
    distrManager.buyTicket(0, {'from':accounts[1]})
    assert distrManager.validDistributors(accounts[1]) > 0
    assert distributor.distributors(accounts[1]) == True 
    assert distributor.balanceOf(accounts[1]) == 1
    assert distributor.ownerOf(1) == accounts[1]
    assert dai.balanceOf(accounts[1]) == 0
    assert dai.balanceOf(distributor.address) == ERC20_COLLATERAL_AMOUNT

    wnft = distributor.getWrappedToken(1)
    assert wnft[0] == zero_address
    assert wnft[1] == 0
    assert wnft[2] == 0
    assert wnft[3] == 0
    assert wnft[4] == block_time + TIMELOCK
    assert wnft[5] == 0
    assert wnft[6] == zero_address
    assert wnft[7] == 0
    assert wnft[8] == 0
    assert wnft[9] == zero_address
    assert wnft[10] == 0
    assert wnft[11] == 0
    assert distributor.getERC20Collateral(1)[0][0] == dai.address
    assert distributor.getERC20Collateral(1)[0][1] == ERC20_COLLATERAL_AMOUNT
    assert distrManager.validDistributors(accounts[1]) == block_time+TICKET_VALID


    #нескольких дистрибьюторов так добавить, поменяв цену

    #change price
    with reverts("Ownable: caller is not the owner"):
        distrManager.editTarif(0, dai.address, ERC20_COLLATERAL_AMOUNT*2, TIMELOCK, TICKET_VALID, {"from": accounts[1]})
    distrManager.editTarif(0, dai.address, ERC20_COLLATERAL_AMOUNT*2, TIMELOCK, TICKET_VALID, {"from": accounts[0]})

    #add second distributor
    dai.transfer(accounts[2], ERC20_COLLATERAL_AMOUNT*2)
    dai.approve(distrManager, ERC20_COLLATERAL_AMOUNT*2, {'from':accounts[2]})
    block_time = chain.time()
    distrManager.buyTicket(0, {'from':accounts[2]})

    wnft = distributor.getWrappedToken(2)
    assert wnft[0] == zero_address
    assert wnft[1] == 0
    assert wnft[2] == 0
    assert wnft[3] == 0
    assert wnft[4] == block_time + TIMELOCK
    assert wnft[5] == 0
    assert wnft[6] == zero_address
    assert wnft[7] == 0
    assert wnft[8] == 0
    assert wnft[9] == zero_address
    assert wnft[10] == 0
    assert wnft[11] == 0
    assert distributor.getERC20Collateral(2)[0][0] == dai.address
    assert distributor.getERC20Collateral(2)[0][1] == 2*ERC20_COLLATERAL_AMOUNT
    assert distrManager.validDistributors(accounts[2]) == block_time+TICKET_VALID

    #try to remove distributor when ticket is valid
    with reverts("Ticket is still valid"):
        distrManager.removeFromDistributors(accounts[1], {"from": accounts[2]})

    #wrap by distributor
    weth.approve(distributor, ERC20_COLLATERAL_AMOUNT * 2, {'from':accounts[1]})
    dai.approve(distributor, ERC20_COLLATERAL_AMOUNT * 2, {'from':accounts[1]})
    weth.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT * 2, {'from':accounts[0]})
    dai.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT * 2, {'from':accounts[0]})
    tx = distributor.WrapAndDistribEmpty(
        [accounts[1], accounts[2]],
        [(weth.address,ERC20_COLLATERAL_AMOUNT), (dai.address,ERC20_COLLATERAL_AMOUNT)],
        0,
        {'from':accounts[1]}
    )

    assert distributor.balanceOf(accounts[1]) == 2
    assert distributor.balanceOf(accounts[2]) == 2

    #move time
    chain.sleep(1000)
    chain.mine()

    #buy new ticket - previous ticket is valid
    old_ticket_time = distrManager.validDistributors(accounts[1])
    dai.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT*2)
    dai.approve(distrManager, ERC20_COLLATERAL_AMOUNT*2, {'from':accounts[1]})
    block_time = chain.time()
    distrManager.buyTicket(0, {'from':accounts[1]})

    assert distrManager.validDistributors(accounts[1]) == old_ticket_time+TICKET_VALID

    #move time
    chain.sleep(TICKET_VALID+1000)
    chain.mine()

    #buy ticket again - previous ticket is invalid
    dai.transfer(accounts[2], ERC20_COLLATERAL_AMOUNT*2)
    dai.approve(distrManager, ERC20_COLLATERAL_AMOUNT*2, {'from':accounts[2]})
    block_time = chain.time()
    distrManager.buyTicket(0, {'from':accounts[2]})

    assert distrManager.validDistributors(accounts[2]) == block_time+TICKET_VALID
    assert distributor.balanceOf(accounts[2]) == 3

    #move time
    chain.sleep(TICKET_VALID+1000)
    chain.mine()
    #delete from distributor list
    distrManager.removeFromDistributors(accounts[1], {"from": accounts[2]})
    assert distributor.distributors(accounts[1]) == False

    #try to wrap - ticket is invalid
    weth.approve(distributor, ERC20_COLLATERAL_AMOUNT * 2, {'from':accounts[1]})
    dai.approve(distributor, ERC20_COLLATERAL_AMOUNT * 2, {'from':accounts[1]})
    weth.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT * 2, {'from':accounts[0]})
    dai.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT * 2, {'from':accounts[0]})
    with reverts("Only for distributors"):
        distributor.WrapAndDistribEmpty(
            [accounts[1], accounts[2]],
            [(weth.address,ERC20_COLLATERAL_AMOUNT), (dai.address,ERC20_COLLATERAL_AMOUNT)],
            0,
            {'from':accounts[1]}
        )

    #
    with reverts("Ownable: caller is not the owner"):
        distrManager.revokeOwnership({"from": accounts[1]})

    distrManager.revokeOwnership({"from": accounts[0]})
    distributor.owner() == accounts[0]





