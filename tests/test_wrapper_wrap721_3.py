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

#transferFee Contract is in blackList, it is client-side
def test_wrap_with_transferFeeContract_in_blackList(accounts, erc721mock, wrapper,  trmodel, pft, dai):

	#protocol fee is being taken
	wrapper.setFee(protokolFee, chargeFeeAfter, pft.address, {"from": accounts[0]})

	#make test data
	makeNFTForTest(accounts, erc721mock, ORIGINAL_NFT_IDs)

	#wrap nft
	pft.transfer(accounts[1], protokolFee, {"from": accounts[0]})

	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
	pft.approve(wrapper, protokolFee, {'from':accounts[1]})

	#add transferFeeContract contract in blackList
	wrapper.editPartnersItem(dai.address, False, trmodel, False, {"from": accounts[0]})
	dai.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT + 100, {"from": accounts[1]})
	
	with reverts("This transferFee token is not enabled"):
		makeWrapNFT(wrapper, erc721mock, ['originalTokenId'], [ORIGINAL_NFT_IDs[0]], accounts[1], dai)
	
	#move transferFeeToken from blackList
	wrapper.editPartnersItem(dai.address, True, trmodel, False, {"from": accounts[0]})
	makeWrapNFT(wrapper, erc721mock, ['originalTokenId', 'unwrap_fee_threshold'], [ORIGINAL_NFT_IDs[0], 0], accounts[1], dai)
	assert pft.balanceOf(wrapper.address) == protokolFee
	tokenId = wrapper.lastWrappedNFTId()

	before_balance = dai.balanceOf(wrapper.address) 
	wrapper.approve(accounts[3].address, tokenId, {"from": accounts[1]})
	dai.approve(trmodel, TRANSFER_FEE, {'from':accounts[1]})
	nft = wrapper.getWrappedToken(tokenId)
	dai.transfer(accounts[1].address, TRANSFER_FEE, {"from": accounts[0]}) #add tokens to pay transfer fee
	wrapper.transferFrom(accounts[1].address, accounts[2].address, tokenId, {"from": accounts[3]})

	assert dai.balanceOf(accounts[1]) == 0
	assert dai.balanceOf(wrapper.address) == before_balance + TRANSFER_FEE - nft[5]*nft[7]/100
	assert dai.balanceOf(royaltyBeneficiary) == nft[5]*nft[7]/100


	#add transferFeeContract contract in blackList again
	wrapper.editPartnersItem(dai.address, False, trmodel, False, {"from": accounts[0]})

	before_balance = dai.balanceOf(wrapper.address) 
	before_balance_royaltyBeneficiary = dai.balanceOf(royaltyBeneficiary) 
	wrapper.approve(accounts[3].address, tokenId, {"from": accounts[2]})
	nft = wrapper.getWrappedToken(tokenId)
	dai.transfer(accounts[2].address, TRANSFER_FEE, {"from": accounts[0]}) #add tokens to pay transfer fee
	dai.approve(trmodel, TRANSFER_FEE, {'from':accounts[2]})
	wrapper.transferFrom(accounts[2].address, accounts[3].address, tokenId, {"from": accounts[3]})

	assert dai.balanceOf(accounts[2]) == 0
	assert dai.balanceOf(wrapper.address) == before_balance + TRANSFER_FEE - nft[5]*nft[7]/100
	assert dai.balanceOf(royaltyBeneficiary) == before_balance_royaltyBeneficiary + nft[5]*nft[7]/100


	#unwrap

	#move date 
	chain.sleep(100)
	chain.mine()
	logging.info('wrapper.totalSupply() = {}'.format(wrapper.totalSupply()))
	logging.info('wrapper.balanceOf(accounts[3]) = {}'.format(wrapper.balanceOf(accounts[3])))
	logging.info('dai.balanceOf(accounts[3]) = {}'.format(dai.balanceOf(accounts[3])))
	logging.info('dai.balanceOf(wrapper.address) = {}'.format(dai.balanceOf(wrapper.address)))
	logging.info('********************AFTER UNWRAP*************')
	#unwrap
	nft = wrapper.getWrappedToken(tokenId)
	wrapper.unWrap721(tokenId, {"from": accounts[3]})
	assert wrapper.totalSupply() == 0
	assert wrapper.balanceOf(accounts[3].address) == 0
	assert dai.balanceOf(accounts[3].address) == nft[3]
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[3].address
	assert dai.balanceOf(wrapper.address) == 0
	assert dai.balanceOf(royaltyBeneficiary) == before_balance_royaltyBeneficiary + nft[5]*nft[7]/100

	logging.info('wrapper.balanceOf(accounts[3]) = {}'.format(wrapper.balanceOf(accounts[3])))
	logging.info('dai.balanceOf(accounts[3]) = {}'.format(dai.balanceOf(accounts[3])))
	logging.info('dai.balanceOf(wrapper.address) = {}'.format(dai.balanceOf(wrapper.address)))
	logging.info('dai.balanceOfroyaltyBeneficiary) = {}'.format(dai.balanceOf(royaltyBeneficiary)))
	



	