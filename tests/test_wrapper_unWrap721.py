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

#unwrap simple wrapped nft
def test_wrapper_unWrap721(accounts, erc721mock, wrapper, niftsy20, dai, weth):
	#make test data
	makeNFTForTest(accounts, erc721mock, ORIGINAL_NFT_IDs)
	wrapper.setFee(protokolFee, chargeFeeAfter, {"from": accounts[0]})
	#wrap difficult nft

	niftsy20.transfer(accounts[1], protokolFee, {"from": accounts[0]})
	unwrapAfter = chain.time() + 10

	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
	
	makeWrapNFT(wrapper, erc721mock, ['originalTokenId', 'transferFee', 'royaltyBeneficiary', 'royaltyPercent', 'unwraptFeeThreshold'], [ORIGINAL_NFT_IDs[0], 0, zero_address, 0, 0], accounts[1])
	tokenId = wrapper.lastWrappedNFTId()

	assert niftsy20.balanceOf(accounts[1]) == 0
	assert niftsy20.balanceOf(wrapper.address) == protokolFee

	#unwrap

	#move date 
	chain.sleep(100)
	chain.mine()
	logging.info('wrapper.totalSupply() = {}'.format(wrapper.totalSupply()))
	logging.info('balance acc1 = {}'.format(wrapper.balanceOf(accounts[1])))
	logging.info('accounts[1].balance() = {}'.format(accounts[1].balance()))
	balance_eth = accounts[1].balance()
	nft = wrapper.getWrappedToken(tokenId)
	wrapper.unWrap721(tokenId, {"from": accounts[1]})
	logging.info('********************AFTER UNWRAP*************')
	assert wrapper.totalSupply() == 0
	assert wrapper.balanceOf(accounts[1].address) == 0
	assert niftsy20.balanceOf(accounts[1].address) == 0
	assert niftsy20.balanceOf(wrapper.address) == protokolFee
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[1].address
	assert accounts[1].balance() == balance_eth + nft[2]
	logging.info('accounts[1].balance() = {}'.format(accounts[1].balance()))
	with reverts("ERC721: owner query for nonexistent token"):
		wrapper.ownerOf(tokenId)


#revert cases
def test_wrapper_unWrap721_1(accounts, erc721mock, wrapper, niftsy20, dai, weth):
	#prepare test data
	erc721mock.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], {'from':accounts[0]})
	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[1], {'from':accounts[1]})
	
	#wrap nft
	niftsy20.transfer(accounts[1], protokolFee, {"from": accounts[0]})
	unwrapAfter = chain.time() + 10

	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[1], {'from':accounts[1]})
	
	before_balance = niftsy20.balanceOf(wrapper.address)
	makeWrapNFT(wrapper, erc721mock, ['originalTokenId', 'royaltyBeneficiary', 'royaltyPercent'], [ORIGINAL_NFT_IDs[1], zero_address, 0], accounts[1])
	tokenId = wrapper.lastWrappedNFTId()

	assert niftsy20.balanceOf(accounts[1]) == 0
	assert niftsy20.balanceOf(wrapper.address) == before_balance + protokolFee
	assert wrapper.lastWrappedNFTId() == 2

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

#transferFee > 0, royalty_percent = 0 
def test_wrapper_transfer_transferFee_2(accounts, erc721mock, wrapper, niftsy20, dai, weth):
	tokenId = wrapper.lastWrappedNFTId()
	#transfer several time
	c = round(UNWRAP_FEE_THRESHOLD/TRANSFER_FEE) + 1
	transfer_amount = 0
	i = 0
	for i in range(c):
		wrapper.approve(accounts[i+2].address, tokenId, {"from": accounts[i+1]})
		niftsy20.transfer(accounts[i + 1].address, TRANSFER_FEE, {"from": accounts[0]}) #add niftsy tokens to pay transfer fee
		wrapper.transferFrom(accounts[i+1].address, accounts[i+2].address, tokenId, {"from": accounts[i+2]}) #make transfers
		transfer_amount += TRANSFER_FEE

	#check backedTokens after transfers
	nft = wrapper.getWrappedToken(tokenId)
	assert nft[3] == transfer_amount
	
	#move date 
	chain.sleep(100)
	chain.mine()
	logging.info('wrapper.totalSupply() = {}'.format(wrapper.totalSupply()))
	logging.info('balance accI+2 = {}'.format(wrapper.balanceOf(accounts[i+2])))
	logging.info('accounts[i+2].balance() = {}'.format(accounts[i+2].balance()))
	balance_eth = accounts[i+2].balance()
	balance_erc20 = niftsy20.balanceOf(wrapper.address)
	logging.info('********************AFTER UNWRAP*************')
	#unwrap
	wrapper.unWrap721(tokenId, {"from": accounts[i+2]})
	assert wrapper.totalSupply() == 0
	assert wrapper.balanceOf(accounts[i+2].address) == 0
	assert niftsy20.balanceOf(accounts[i+2].address) == transfer_amount
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[1]) == accounts[i+2].address
	assert accounts[i+2].balance() == balance_eth + nft[2]
	assert niftsy20.balanceOf(wrapper.address) == balance_erc20 - transfer_amount

	logging.info('accounts[i+2].balance() = {}'.format(accounts[i+2].balance()))
	logging.info('wrapper.balanceOf(accounts[i+2]) = {}'.format(wrapper.balanceOf(accounts[i+2])))
	logging.info('niftsy20.balanceOf(accounts[i+2]) = {}'.format(niftsy20.balanceOf(accounts[i+2])))
	logging.info('wrapper.balance() = {}'.format(wrapper.balance()))
	logging.info('niftsy20.balanceOf(wrapper.address) = {}'.format(niftsy20.balanceOf(wrapper.address)))
	with reverts("ERC721: owner query for nonexistent token"):
		wrapper.ownerOf(tokenId)

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

	c = round(UNWRAP_FEE_THRESHOLD/TRANSFER_FEE) + 1
	backedTokens = 0
	royalty_tokens = 0
	i = 0
	for i in range(c):
		wrapper.approve(accounts[i+2].address, tokenId, {"from": accounts[i+1]})
		niftsy20.transfer(accounts[i + 1].address, TRANSFER_FEE, {"from": accounts[0]}) #add niftsy tokens to pay transfer fee
		wrapper.transferFrom(accounts[i+1].address, accounts[i+2].address, tokenId, {"from": accounts[i+2]}) #make transfers
		royalty_tokens += TRANSFER_FEE*nft[7]/100
		backedTokens += TRANSFER_FEE - TRANSFER_FEE*nft[7]/100

	#check backedTokens after transfers
	nft = wrapper.getWrappedToken(tokenId)
	logging.info('nft2 = {}'.format(nft))
	assert nft[3] == backedTokens

	#move date 
	chain.sleep(100)
	chain.mine()
	logging.info('wrapper.totalSupply() = {}'.format(wrapper.totalSupply()))
	logging.info('accounts[i+2].balance() = {}'.format(accounts[i+2].balance()))
	logging.info('wrapper.balanceOf(accounts[i+2]) = {}'.format(wrapper.balanceOf(accounts[i+2])))
	logging.info('niftsy20.balanceOf(accounts[i+2]) = {}'.format(niftsy20.balanceOf(accounts[i+2])))
	logging.info('wrapper.balance() = {}'.format(wrapper.balance()))
	logging.info('niftsy20.balanceOf(wrapper.address) = {}'.format(niftsy20.balanceOf(wrapper.address)))
	balance_eth = accounts[i+2].balance()
	balance_erc20 = niftsy20.balanceOf(wrapper.address)
	balance_erc20_owner = niftsy20.balanceOf(accounts[i+2].address)
	logging.info('********************AFTER UNWRAP*************')
	#unwrap
	wrapper.unWrap721(tokenId, {"from": accounts[i+2]})
	assert wrapper.totalSupply() == 0
	assert wrapper.balanceOf(accounts[i+2].address) == 0
	assert niftsy20.balanceOf(accounts[i+2].address) == balance_erc20_owner + backedTokens
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[2]) == accounts[i+2].address
	assert accounts[i+2].balance() == balance_eth + nft[2]
	assert niftsy20.balanceOf(wrapper.address) == balance_erc20 - backedTokens
	assert niftsy20.balanceOf(royaltyBeneficiary) == royalty_tokens

	logging.info('accounts[i+2].balance() = {}'.format(accounts[i+2].balance()))
	logging.info('wrapper.balanceOf(accounts[i+2]) = {}'.format(wrapper.balanceOf(accounts[i+2])))
	logging.info('niftsy20.balanceOf(accounts[i+2]) = {}'.format(niftsy20.balanceOf(accounts[i+2])))
	logging.info('wrapper.balance() = {}'.format(wrapper.balance()))
	logging.info('niftsy20.balanceOf(wrapper.address) = {}'.format(niftsy20.balanceOf(wrapper.address)))
	with reverts("ERC721: owner query for nonexistent token"):
		wrapper.ownerOf(tokenId)

	#wrap this nft again by first nft owner  - after unwrap
	#prepare test data
	niftsy20.transfer(accounts[1], protokolFee, {"from": accounts[0]})
	unwrapAfter = chain.time() + 10
	erc721mock.transferFrom(accounts[i+2], accounts[1], ORIGINAL_NFT_IDs[2], {"from": accounts[i+2]} )
	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[2], {'from':accounts[1]})
	
	#wrap
	before_balance = niftsy20.balanceOf(wrapper.address) 
	makeWrapNFT(wrapper, erc721mock, ['originalTokenId'], [ORIGINAL_NFT_IDs[2]], accounts[1])
	assert niftsy20.balanceOf(accounts[1]) == 0
	assert wrapper.balanceOf(accounts[1]) == 1
	assert niftsy20.balanceOf(wrapper.address) == before_balance + protokolFee
	assert wrapper.lastWrappedNFTId() == 4

	tokenId = wrapper.lastWrappedNFTId()

	#check new wrappedNFT
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
	nft = wrapper.getWrappedToken(tokenId)
	logging.info('new nft = {}'.format(nft))