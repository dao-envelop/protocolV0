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

#revert cases
def test_wrapper_unWrap721_1(accounts, erc721mock, wrapper, niftsy20, dai, weth):
	#make test data
	makeNFTForTest(accounts, erc721mock, ORIGINAL_NFT_IDs)
	wrapper.setFee(protokolFee, chargeFeeAfter, {"from": accounts[0]})
	#wrap difficult nft

	niftsy20.transfer(accounts[1], protokolFee, {"from": accounts[0]})
	unwrapAfter = chain.time() + 10

	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
	
	makeWrapNFT(wrapper, erc721mock, ['originalTokenId', 'transferFee', 'royaltyBeneficiary', 'royaltyPercent'], [ORIGINAL_NFT_IDs[0], 0, zero_address, 0], accounts[1])
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
		0, 
		zero_address, 
		0, 
		UNWRAP_FEE_THRESHOLD)

	#unwrap

	#non exists token
	with reverts("ERC721: owner query for nonexistent token"):
		wrapper.unWrap721(100, {"from": accounts[1]})

	#not owner tries to unwrap token
	with reverts("Only owner can unwrap it!"):
		wrapper.unWrap721(tokenId, {"from": accounts[3]})

	#date of unwrap has not happened
	with reverts("Cant unwrap before day X"):
		wrapper.unWrap721(tokenId, {"from": accounts[1]})

	#move date 
	chain.sleep(100)
	chain.mine()

	#unwraptFeeThreshold is not collected
	with reverts("Cant unwrap due Fee Threshold"):
		wrapper.unWrap721(tokenId, {"from": accounts[1]})







	'''wrapper.approve(accounts[3].address, tokenId, {"from": accounts[1]})
	wrapper.transferFrom(accounts[1].address, accounts[2].address, tokenId, {"from": accounts[3]})
	assert wrapper.ownerOf(tokenId) == accounts[2].address
	#return tokenId - owner transfer
	wrapper.transferFrom(accounts[2].address, accounts[1].address, tokenId, {"from": accounts[2]})
	assert wrapper.ownerOf(tokenId) == accounts[1].address

	nft = wrapper.getWrappedToken(tokenId)
	assert nft[3] == 0 #check backedTokens'''

#transferFee > 0
'''def test_wrapper_transfer_transferFee_2(accounts, erc721mock, wrapper, niftsy20, dai, weth):
	#make test data
	erc721mock.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], {'from':accounts[0]})
	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[1], {'from':accounts[1]})
	#wrap difficult nft

	niftsy20.transfer(accounts[1], protokolFee, {"from": accounts[0]})
	unwrapAfter = chain.time() + 10
	
	makeWrapNFT(wrapper, erc721mock, ['originalTokenId', 'royaltyBeneficiary', 'royaltyPercent'], [ORIGINAL_NFT_IDs[1], zero_address, 0], accounts[1])
	assert niftsy20.balanceOf(accounts[1]) == 0
	assert niftsy20.balanceOf(wrapper.address) == 2 * protokolFee
	assert wrapper.lastWrappedNFTId() == 2

	tokenId = wrapper.lastWrappedNFTId()
	nft = wrapper.getWrappedToken(tokenId)
	logging.info('nft1 = {}'.format(nft))

	checkWrappedNFT(wrapper, 
		tokenId, 
		erc721mock.address, 
		ORIGINAL_NFT_IDs[1], 
		START_NATIVE_COLLATERAL, 
		0,  
		unwrapAfter, 
		TRANSFER_FEE, 
		zero_address, 
		0, 
		UNWRAP_FEE_THRESHOLD)

	#not enough niftsy20 tokens for paying of transferFee
	wrapper.approve(accounts[3].address, tokenId, {"from": accounts[1]})
	with reverts("insufficient NIFTSY balance for fee"):
		wrapper.transferFrom(accounts[1].address, accounts[2].address, tokenId, {"from": accounts[3]})
	#add niftsy tokens to acc1
	before_balance = niftsy20.balanceOf(wrapper.address) 
	niftsy20.transfer(accounts[1].address, TRANSFER_FEE, {"from": accounts[0]}) #add niftsy tokens to pay transfer fee
	wrapper.transferFrom(accounts[1].address, accounts[2].address, tokenId, {"from": accounts[3]})

	nft = wrapper.getWrappedToken(tokenId)
	logging.info('nft1 = {}'.format(nft))
	assert niftsy20.balanceOf(accounts[1]) == 0
	assert niftsy20.balanceOf(wrapper.address) == before_balance + TRANSFER_FEE
	checkWrappedNFT(wrapper, 
		tokenId, 
		erc721mock.address, 
		ORIGINAL_NFT_IDs[1], 
		START_NATIVE_COLLATERAL, 
		TRANSFER_FEE,  
		unwrapAfter, 
		TRANSFER_FEE, 
		zero_address, 
		0, 
		UNWRAP_FEE_THRESHOLD)

#transferFee > 0, royalty_percent > 0
#there are transferFee, royalty_percent
def test_wrapper_transfer_transferFee_3(accounts, erc721mock, wrapper, niftsy20, dai, weth):
	#make test data
	erc721mock.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[2], {'from':accounts[0]})
	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[2], {'from':accounts[1]})
	logging.info('balanceOf(wrapper.address) = {}'.format(niftsy20.balanceOf(wrapper.address)))
	logging.info('balanceOf(royaltyBeneficiary) = {}'.format(niftsy20.balanceOf(royaltyBeneficiary)))
	#wrap difficult nft

	niftsy20.transfer(accounts[1], protokolFee, {"from": accounts[0]})
	unwrapAfter = chain.time() + 10
	
	before_balance = niftsy20.balanceOf(wrapper.address) 
	makeWrapNFT(wrapper, erc721mock, ['originalTokenId'], [ORIGINAL_NFT_IDs[2]], accounts[1])
	assert niftsy20.balanceOf(accounts[1]) == 0
	assert niftsy20.balanceOf(wrapper.address) == before_balance + protokolFee
	assert wrapper.lastWrappedNFTId() == 3

	tokenId = wrapper.lastWrappedNFTId()
	nft = wrapper.getWrappedToken(tokenId)
	logging.info('nft2 = {}'.format(nft))

	checkWrappedNFT(wrapper, 
		tokenId, 
		erc721mock.address, 
		ORIGINAL_NFT_IDs[2], 
		START_NATIVE_COLLATERAL, 
		0,  
		unwrapAfter, 
		TRANSFER_FEE, 
		royaltyBeneficiary, 
		ROAYLTY_PERCENT, 
		UNWRAP_FEE_THRESHOLD)

	wrapper.approve(accounts[3].address, tokenId, {"from": accounts[1]})
	before_balance = niftsy20.balanceOf(wrapper.address) 
	niftsy20.transfer(accounts[1].address, TRANSFER_FEE, {"from": accounts[0]}) #add niftsy tokens to pay transfer fee
	wrapper.transferFrom(accounts[1].address, accounts[2].address, tokenId, {"from": accounts[3]})
	logging.info('balanceOf(wrapper.address) = {}'.format(niftsy20.balanceOf(wrapper.address)))
	logging.info('balanceOf(royaltyBeneficiary) = {}'.format(niftsy20.balanceOf(royaltyBeneficiary)))

	nft = wrapper.getWrappedToken(tokenId)
	logging.info('nft2 = {}'.format(nft))
	assert niftsy20.balanceOf(accounts[1]) == 0
	assert niftsy20.balanceOf(wrapper.address) == before_balance + TRANSFER_FEE - nft[5]*nft[7]/100
	assert niftsy20.balanceOf(royaltyBeneficiary) == nft[5]*nft[7]/100
	checkWrappedNFT(wrapper, 
		tokenId, 
		erc721mock.address, 
		ORIGINAL_NFT_IDs[2], 
		START_NATIVE_COLLATERAL, 
		TRANSFER_FEE - nft[5]*nft[7]/100,  
		unwrapAfter, 
		TRANSFER_FEE, 
		royaltyBeneficiary, 
		ROAYLTY_PERCENT, 
		UNWRAP_FEE_THRESHOLD)

	#transfer token again
	before_nft = wrapper.getWrappedToken(tokenId)
	wrapper.approve(accounts[3].address, tokenId, {"from": accounts[2]})
	before_balance = niftsy20.balanceOf(wrapper.address) 
	before_balance_royalty = niftsy20.balanceOf(royaltyBeneficiary) 
	niftsy20.transfer(accounts[2].address, TRANSFER_FEE, {"from": accounts[0]}) #add niftsy tokens to pay transfer fee
	wrapper.transferFrom(accounts[2].address, accounts[3].address, tokenId, {"from": accounts[3]})

	nft = wrapper.getWrappedToken(tokenId)
	logging.info('nft2 = {}'.format(nft))
	assert niftsy20.balanceOf(accounts[1]) == 0
	assert niftsy20.balanceOf(wrapper.address) == before_balance + TRANSFER_FEE - nft[5]*nft[7]/100
	assert niftsy20.balanceOf(royaltyBeneficiary) == before_balance_royalty + nft[5]*nft[7]/100
	logging.info('balanceOf(wrapper.address) = {}'.format(niftsy20.balanceOf(wrapper.address)))
	logging.info('balanceOf(royaltyBeneficiary) = {}'.format(niftsy20.balanceOf(royaltyBeneficiary)))
	checkWrappedNFT(wrapper, 
		tokenId, 
		erc721mock.address, 
		ORIGINAL_NFT_IDs[2], 
		START_NATIVE_COLLATERAL, 
		before_nft[3] + TRANSFER_FEE - nft[5]*nft[7]/100,  
		unwrapAfter, 
		TRANSFER_FEE, 
		royaltyBeneficiary, 
		ROAYLTY_PERCENT, 
		UNWRAP_FEE_THRESHOLD)

#transferFee = 1, royalty_percent = 1 - very small
#there are transferFee, royalty_percent
def test_wrapper_transfer_transferFee_4(accounts, erc721mock, wrapper, niftsy20, dai, weth):
	#make test data
	erc721mock.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[3], {'from':accounts[0]})
	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[3], {'from':accounts[1]})
	logging.info('balanceOf(wrapper.address) = {}'.format(niftsy20.balanceOf(wrapper.address)))
	logging.info('balanceOf(royaltyBeneficiary) = {}'.format(niftsy20.balanceOf(royaltyBeneficiary)))
	#wrap difficult nft

	niftsy20.transfer(accounts[1], protokolFee, {"from": accounts[0]})
	unwrapAfter = chain.time() + 10
	
	before_balance = niftsy20.balanceOf(wrapper.address) 
	makeWrapNFT(wrapper, erc721mock, ['originalTokenId', 'transferFee', 'royaltyPercent' ], [ORIGINAL_NFT_IDs[3], 1, 1], accounts[1])
	assert niftsy20.balanceOf(accounts[1]) == 0
	assert niftsy20.balanceOf(wrapper.address) == before_balance + protokolFee
	assert wrapper.lastWrappedNFTId() == 4

	tokenId = wrapper.lastWrappedNFTId()
	nft = wrapper.getWrappedToken(tokenId)
	logging.info('nft3 = {}'.format(nft))

	checkWrappedNFT(wrapper, 
		tokenId, 
		erc721mock.address, 
		ORIGINAL_NFT_IDs[3], 
		START_NATIVE_COLLATERAL, 
		0,  
		unwrapAfter, 
		1, 
		royaltyBeneficiary, 
		1, 
		UNWRAP_FEE_THRESHOLD)

	wrapper.approve(accounts[3].address, tokenId, {"from": accounts[1]})
	before_balance = niftsy20.balanceOf(wrapper.address) 
	before_balance_royalty = niftsy20.balanceOf(royaltyBeneficiary) 
	niftsy20.transfer(accounts[1].address, 1, {"from": accounts[0]}) #add niftsy tokens to pay transfer fee
	wrapper.transferFrom(accounts[1].address, accounts[2].address, tokenId, {"from": accounts[3]})
	logging.info('balanceOf(wrapper.address) = {}'.format(niftsy20.balanceOf(wrapper.address)))
	logging.info('balanceOf(royaltyBeneficiary) = {}'.format(niftsy20.balanceOf(royaltyBeneficiary)))

	nft = wrapper.getWrappedToken(tokenId)
	logging.info('nft3 = {}'.format(nft))
	assert niftsy20.balanceOf(accounts[1]) == 0
	assert niftsy20.balanceOf(wrapper.address) == before_balance + 1 - round(nft[5]*nft[7]/100)
	assert niftsy20.balanceOf(royaltyBeneficiary) == before_balance_royalty + round(nft[5]*nft[7]/100)
	checkWrappedNFT(wrapper, 
		tokenId, 
		erc721mock.address, 
		ORIGINAL_NFT_IDs[3], 
		START_NATIVE_COLLATERAL, 
		1 - round(nft[5]*nft[7]/100), 
		unwrapAfter, 
		1, 
		royaltyBeneficiary, 
		1, 
		UNWRAP_FEE_THRESHOLD)'''