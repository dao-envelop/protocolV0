import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest, makeWrapNFT
from checkData import checkWrappedNFT

LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
START_NATIVE_COLLATERAL = '1 ether'
ADD_NATIVE_COLLATERAL = '2 ether'
ERC20_COLLATERAL_AMOUNT = 2e17;
TRANSFER_FEE = 2e18
ROAYLTY_PERCENT = 10
UNWRAP_FEE_THRESHOLD = 6e18
protokolFee = 10
chargeFeeAfter = 100
royaltyBeneficiary = '0xbd7e5fb7525ed8583893ce1b1f93e21cc0cf02f6'
zero_address = '0x0000000000000000000000000000000000000000'

#add collateral contract in blackList
def test_test_wrapper_addERC20Collateral_blackList(accounts, erc721mock, wrapper, niftsy20, trmodel, pft, dai):
	#make test data
	makeNFTForTest(accounts, erc721mock, ORIGINAL_NFT_IDs)
	wrapper.setFee(protokolFee, chargeFeeAfter, pft.address, {"from": accounts[0]})
	dai.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	#wrap difficult nft

	pft.transfer(accounts[1], protokolFee, {"from": accounts[0]})
	unwrapAfter = chain.time() + 10

	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
	pft.approve(wrapper, TRANSFER_FEE, {'from':accounts[1]})

	makeWrapNFT(wrapper, erc721mock, ['originalTokenId', 'transferFee', 'royaltyBeneficiary', 'royaltyPercent', 'unwraptFeeThreshold'], [ORIGINAL_NFT_IDs[0], 0, zero_address, 0, 0], accounts[1], niftsy20)
	
	assert pft.balanceOf(accounts[1]) == 0
	assert pft.balanceOf(wrapper.address) == protokolFee
	assert wrapper.lastWrappedNFTId() == 1
	tokenId = wrapper.lastWrappedNFTId()
	nft = wrapper.getWrappedToken(tokenId)

	#try to add erc20 collaterals which is in blockList

	#add collateral contract in blackList
	wrapper.editPartnersItem(dai.address, False, zero_address, False, {"from": accounts[0]})
	
	dai.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT + 100, {"from": accounts[1]})
	with reverts("This ERC20 is not enabled for collateral"):
		wrapper.addERC20Collateral(tokenId, dai.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})

	#move collateral contract from blackList
	wrapper.editPartnersItem(dai.address, True, zero_address, False, {"from": accounts[0]})
	wrapper.addERC20Collateral(tokenId, dai.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})

	assert dai.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai.balanceOf(accounts[1].address) == 0
	logging.info('coll = {}'.format(wrapper.getERC20Collateral(tokenId)))
	assert wrapper.getERC20Collateral(tokenId)[0][0] == dai.address
	assert wrapper.getERC20Collateral(tokenId)[0][1] == ERC20_COLLATERAL_AMOUNT

	#add collateral contract in blackList again
	wrapper.editPartnersItem(dai.address, False, zero_address, False, {"from": accounts[0]})

	#try to unwrap nft
	#move date 
	chain.sleep(100)
	chain.mine()
	wrapper.unWrap721(tokenId, {"from": accounts[1]})
	assert dai.balanceOf(wrapper.address) == 0
	assert dai.balanceOf(accounts[1].address) == ERC20_COLLATERAL_AMOUNT
	