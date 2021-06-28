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
chargeFeeAfter = 10
royaltyBeneficiary = '0xbd7e5fb7525ed8583893ce1b1f93e21cc0cf02f6'
zero_address = '0x0000000000000000000000000000000000000000'

def test_wrapper_addERC20Collateral(accounts, erc721mock, wrapper, niftsy20, dai, weth):
	#make test data
	makeNFTForTest(accounts, erc721mock, ORIGINAL_NFT_IDs)
	wrapper.setFee(protokolFee, chargeFeeAfter, {"from": accounts[0]})
	dai.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	#wrap difficult nft

	niftsy20.transfer(accounts[1], protokolFee, {"from": accounts[0]})
	unwrapAfter = chain.time() + 10

	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
	
	makeWrapNFT(wrapper, erc721mock, ['originalTokenId'], [ORIGINAL_NFT_IDs[0]], accounts[1])
	assert niftsy20.balanceOf(accounts[1]) == 0
	assert niftsy20.balanceOf(wrapper.address) == protokolFee
	assert wrapper.lastWrappedNFTId() == 1
	checkWrappedNFT(wrapper, 
		wrapper.lastWrappedNFTId(), 
		erc721mock.address, 
		ORIGINAL_NFT_IDs[0], 
		START_NATIVE_COLLATERAL, 
		0,  
		unwrapAfter, 
		TRANSFER_FEE, 
		royaltyBeneficiary, 
		ROAYLTY_PERCENT, 
		UNWRAP_FEE_THRESHOLD)

	tokenId = wrapper.lastWrappedNFTId()
	nft = wrapper.getWrappedToken(tokenId)
	#there is not allowance
	with reverts("Please approve first"):
		wrapper.addERC20Collateral(tokenId, dai.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT + 100, {"from": accounts[1]})
	with reverts("Low balance for add collateral"):
		wrapper.addERC20Collateral(tokenId, dai.address, ERC20_COLLATERAL_AMOUNT + ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	assert dai.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai.balanceOf(accounts[1].address) == 0
	logging.info('coll = {}'.format(wrapper.getERC20Collateral(tokenId)))
	assert wrapper.getERC20Collateral(tokenId)[0][0] == dai.address
	assert wrapper.getERC20Collateral(tokenId)[0][1] == ERC20_COLLATERAL_AMOUNT

	#second call
	dai.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT + 100, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	assert wrapper.getERC20Collateral(tokenId)[0][1] == 2 * ERC20_COLLATERAL_AMOUNT
	assert len(wrapper.getERC20Collateral(tokenId)) == 1
	logging.info('coll = {}'.format(wrapper.getERC20Collateral(tokenId)))


	#nonexist tokenId
	dai.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT + 100, {"from": accounts[1]})
	with reverts("ERC721: owner query for nonexistent token"):
		wrapper.addERC20Collateral(100, dai.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})

	#not owner calls addNativeCollateral
	dai.transfer(accounts[2], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT + 100, {"from": accounts[2]})
	wrapper.addERC20Collateral(tokenId, dai.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[2]})
	assert wrapper.getERC20Collateral(tokenId)[0][1] == 3 * ERC20_COLLATERAL_AMOUNT
	assert len(wrapper.getERC20Collateral(tokenId)) == 1

	#add second token
	weth.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	weth.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT + 100, {"from": accounts[1]})
	wrapper.addERC20Collateral(wrapper.lastWrappedNFTId(), weth.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	assert len(wrapper.getERC20Collateral(tokenId)) == 2
	assert wrapper.getERC20Collateral(tokenId)[1][0] == weth.address
	assert wrapper.getERC20Collateral(tokenId)[1][1] == ERC20_COLLATERAL_AMOUNT

	#add third token
	niftsy20.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	niftsy20.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT + 100, {"from": accounts[1]})
	logging.info('before niftsy20.balanceOf(accounts[1]) = {}'.format(niftsy20.balanceOf(accounts[1])))
	logging.info('before niftsy20.balanceOf(wrapper.address) = {}'.format(niftsy20.balanceOf(wrapper.address)))
	wrapper.addERC20Collateral(tokenId, niftsy20.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	assert len(wrapper.getERC20Collateral(tokenId)) == 2
	assert niftsy20.balanceOf(accounts[1]) == ERC20_COLLATERAL_AMOUNT
	logging.info('after niftsy20.balanceOf(accounts[1]) = {}'.format(niftsy20.balanceOf(accounts[1])))
	logging.info('after niftsy20.balanceOf(wrapper.address) = {}'.format(niftsy20.balanceOf(wrapper.address)))

