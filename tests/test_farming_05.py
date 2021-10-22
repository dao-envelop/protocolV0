import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

STAKED_AMOUNT = 1e18
UNWRAP_AFTER = 0
zero_address = '0x0000000000000000000000000000000000000000'

#two accounts farm
def test_settings(accounts,  farming, niftsy20, dai):
    setting = farming.getRewardSettings(niftsy20)
    logging.info('Settings={}'.format(setting))
    assert len(setting) == 4
    assert setting[0][1]==1000

def test_stake(accounts,  farming, niftsy20, dai):
    niftsy20.approve(farming, STAKED_AMOUNT,{'from':accounts[0]})
      

    farming.WrapForFarming(
        accounts[0],
        (niftsy20.address, STAKED_AMOUNT),
         chain.time() + 1000,
        {'from':accounts[0]}
    )
    
    assert farming.getAvailableRewardAmount(1, niftsy20) == 0
    assert farming.balanceOf(accounts[0]) == 1
    assert farming.getWrappedToken(1)[0] == zero_address
    assert farming.getWrappedToken(1)[1] == 0
    assert farming.ownerOf(1) == accounts[0]
    assert farming.getWrappedToken(1)[4] <= chain.time() + 1000
    assert niftsy20.balanceOf(farming) == STAKED_AMOUNT
    assert farming.getERC20CollateralBalance(1, niftsy20) == STAKED_AMOUNT
    assert farming.rewards(1)[0] <= chain.time() + 1000
    assert farming.rewards(1)[0] > 0
    assert farming.totalSupply() == 1



def test_check_uri(accounts,  farming, niftsy20, dai):
    logging.info(farming.tokenURI(farming.lastWrappedNFTId()))
    assert str(farming.tokenURI(farming.lastWrappedNFTId())).lower() == 'https://envelop.is/distribmetadata/'+str(farming.address).lower()+'/'+str(farming.lastWrappedNFTId())    


def test_check_reward(accounts,  farming, niftsy20):
    
    chain.sleep(200)
    chain.mine(10)
    assert farming.getCurrenntAPYByTokenId(1, niftsy20) < farming.getPlanAPYByTokenId(1, niftsy20)
    logging.info('getCurrenntAPYByTokenId = {}'.format(farming.getCurrenntAPYByTokenId(1, niftsy20)))
    logging.info('getPlanAPYByTokenId = {}'.format(farming.getPlanAPYByTokenId(1, niftsy20)))



    chain.sleep(800)
    chain.mine(10)


    #logging.info('getCurrenntAPYByTokenId_1 = {}'.format(farming.getCurrenntAPYByTokenId(1, niftsy20)))
    #logging.info('getPlanAPYByTokenId1 = {}'.format(farming.getPlanAPYByTokenId(1, niftsy20)))
    #logging.info('getCurrenntAPYByTokenId_2 = {}'.format(farming.getCurrenntAPYByTokenId(2, niftsy20)))
    #logging.info('timeInStake()={}'.format(
    #    chain.time() - farming.rewards(farming.lastWrappedNFTId())[0]
    #))

    #logging.info('getERC20CollateralBalance({},{})={}'.format(
    #    2,
    #    niftsy20,
    #    farming.getERC20CollateralBalance(2, niftsy20)
    #))

    #logging.info('farming.getAvailableRewardAmount(1, niftsy20)={}'.format(
    #    Wei(farming.getAvailableRewardAmount(1, niftsy20)).to('ether')
    #))

    #logging.info('farming.getAvailableRewardAmount(2, niftsy20)={}'.format(
    #    Wei(farming.getAvailableRewardAmount(2, niftsy20)).to('ether')

    #))

    assert farming.getAvailableRewardAmount(1, niftsy20) ==  farming.getRewardSettings(niftsy20)[3][1]*farming.getERC20CollateralBalance(1, niftsy20)/10000


def test_harvest(accounts,  farming, niftsy20):
    collateral = farming.getERC20CollateralBalance(1, niftsy20)
    logging.info('col = {}'.format(collateral))
    logging.info('avail = {}'.format(farming.getAvailableRewardAmount(1, niftsy20)))
    logging.info('rasch = {}'.format(farming.getRewardSettings(niftsy20)[3][1]*farming.getERC20CollateralBalance(1, niftsy20)/10000))
    rewards = farming.rewards(1)
    farming.harvest(1, niftsy20.address, {'from':accounts[1]})
    logging.info('getERC20CollateralBalance({},{})={}'.format(
        1,
        niftsy20,
        Wei(farming.getERC20CollateralBalance(1, niftsy20)).to('ether')
    ))

    assert collateral + farming.getRewardSettings(niftsy20)[3][1]*collateral/10000 == farming.getERC20CollateralBalance(1, niftsy20)
    assert rewards[0] < farming.rewards(1)[0]
    logging.info('rewwww = {}'.format(farming.rewards(1)[1]))
    assert farming.rewards(1)[1] == 0

def test_new_farming(accounts,  farming, niftsy20):
    chain.sleep(110)
    chain.mine(10)

    assert farming.getAvailableRewardAmount(1, niftsy20) ==  farming.getRewardSettings(niftsy20)[0][1]*farming.getERC20CollateralBalance(1, niftsy20)/10000

    collateral = farming.getERC20CollateralBalance(1, niftsy20)
    logging.info('col = {}'.format(collateral))
    logging.info('avail = {}'.format(farming.getAvailableRewardAmount(1, niftsy20)))
    logging.info('rasch = {}'.format(farming.getRewardSettings(niftsy20)[0][1]*farming.getERC20CollateralBalance(1, niftsy20)/10000))
    rewards = farming.rewards(1)
    farming.harvest(1, niftsy20.address, {'from':accounts[1]})
    logging.info('getERC20CollateralBalance({},{})={}'.format(
        1,
        niftsy20,
        Wei(farming.getERC20CollateralBalance(2, niftsy20)).to('ether')
    ))

    assert collateral + farming.getRewardSettings(niftsy20)[0][1]*collateral/10000 == farming.getERC20CollateralBalance(1, niftsy20)
    assert rewards[0] < farming.rewards(1)[0]
    assert farming.rewards(1)[1] == 0



def test_withdraw(accounts,  farming, niftsy20):
    # Send token for rewards
    collateral = farming.getERC20CollateralBalance(1, niftsy20)

    niftsy20.transfer(farming, 100e18, {'from':accounts[0]})
    bba0 = niftsy20.balanceOf(accounts[0])
    logging.info('col = {}'.format(collateral))
    logging.info('bba0 = {}'.format(bba0))
    

    bbc = niftsy20.balanceOf(farming)
    tx = farming.unWrap721(1, {'from':accounts[0]})
    logging.info(tx.events)
    assert niftsy20.balanceOf(accounts[0]) == collateral + bba0

    chain.sleep(110)
    chain.mine(10)

    assert farming.getAvailableRewardAmount(1, niftsy20) == 0

    assert farming.balanceOf(accounts[1]) == 0
    assert niftsy20.balanceOf(farming) == bbc - collateral
