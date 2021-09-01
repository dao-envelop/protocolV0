import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest, makeWrapNFT
from checkData import checkWrappedNFT

LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222, 33333]
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


def test_wrapper_transfer_1(accounts, erc721mock, wrapper, niftsy20, dai, weth, trmodel):
	#make test data for case
	wrapper.editPartnersItem(niftsy20.address, True, zero_address, False,{'from': accounts[0]})

	#make test data
	makeNFTForTest(accounts, erc721mock, ORIGINAL_NFT_IDs)
	wrapper.setFee(protokolFee, chargeFeeAfter, niftsy20, {"from": accounts[0]})
	#wrap difficult nft

	niftsy20.transfer(accounts[1], protokolFee, {"from": accounts[0]})
	unwrapAfter = chain.time() + 10

	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
	niftsy20.approve(wrapper, TRANSFER_FEE, {'from':accounts[1]})
	makeWrapNFT(wrapper, erc721mock, ['originalTokenId', 'royaltyBeneficiary', 'royaltyPercent', 'unwraptFeeThreshold'], [ORIGINAL_NFT_IDs[0], zero_address, 0, 0], accounts[1], niftsy20)
	tokenId = wrapper.lastWrappedNFTId()

	assert niftsy20.balanceOf(accounts[1]) == 0
	assert niftsy20.balanceOf(wrapper.address) == protokolFee
	assert wrapper.lastWrappedNFTId() == 1
	checkWrappedNFT(wrapper, 
		tokenId, 
		erc721mock.address, 
		ORIGINAL_NFT_IDs[0], 
		START_NATIVE_COLLATERAL, 
		0,  
		unwrapAfter, 
		TRANSFER_FEE, 
		zero_address, 
		0, 
		0)

	wrapper.approve(accounts[3].address, tokenId, {"from": accounts[1]})
	niftsy20.approve(wrapper, TRANSFER_FEE, {'from':accounts[1]})
	niftsy20.transfer(accounts[1], TRANSFER_FEE, {'from':accounts[0]})
	wrapper.transferFrom(accounts[1].address, accounts[2].address, tokenId, {"from": accounts[3]})
	assert wrapper.ownerOf(tokenId) == accounts[2].address
	
	nft = wrapper.getWrappedToken(tokenId)
	assert nft[3] == TRANSFER_FEE #check backedTokens