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

def test_wrap_with_protokolFee(accounts, erc721mock, wrapper, niftsy20, trmodel, pft):

	#protocol fee is being taken
	wrapper.setFee(protokolFee, chargeFeeAfter, pft.address, {"from": accounts[0]})

	#make test data
	makeNFTForTest(accounts, erc721mock, ORIGINAL_NFT_IDs)

	#wrap nft
	pft.transfer(accounts[1], protokolFee, {"from": accounts[0]})

	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
	pft.approve(wrapper, protokolFee, {'from':accounts[1]})
	
	makeWrapNFT(wrapper, erc721mock, ['originalTokenId'], [ORIGINAL_NFT_IDs[0]], accounts[1], niftsy20)
	assert pft.balanceOf(wrapper.address) == protokolFee

	#protocol fee is not being taken

	wrapper.setFee(protokolFee, 1e10, pft.address, {"from": accounts[0]})

	#wrap nft
	pft.transfer(accounts[1], protokolFee, {"from": accounts[0]})

	erc721mock.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[1], {'from':accounts[0]})
	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[1], {'from':accounts[1]})
	pft.approve(wrapper, protokolFee, {'from':accounts[1]})
	
	makeWrapNFT(wrapper, erc721mock, ['originalTokenId'], [ORIGINAL_NFT_IDs[1]], accounts[1], niftsy20)
	assert pft.balanceOf(wrapper.address) == protokolFee




	