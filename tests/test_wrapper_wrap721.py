import pytest
import logging
from brownie import Wei, reverts, chain
from makeTestData import makeNFTForTest
from checkData import checkWrapedNFT

LOGGER = logging.getLogger(__name__)
ORIGINAL_NFT_IDs = [10000,11111,22222]
START_NATIVE_COLLATERAL = '1 ether'
ADD_NATIVE_COLLATERAL = '2 ether'
ERC20_COLLATERAL_AMOUNT = 2e17;
TRANSFER_FEE = '2 ether'
ROAYLTY_PERCENT = 10
UNWRAP_FEE_THRESHOLD = 6e18
protokolFee = 10
chargeFeeAfter = 10
royaltyBeneficiary = '0xbd7e5fb7525ed8583893ce1b1f93e21cc0cf02f6'
zero_address = '0x0000000000000000000000000000000000000000'

def test_simple_wrap(accounts, erc721mock, wrapper, niftsy20):
	#make test data
	makeNFTForTest(accounts, erc721mock, ORIGINAL_NFT_IDs)
    #Give approve

    #bad _underlineContract
	with reverts(""):
		wrapper.wrap721(
			zero_address, 
			ORIGINAL_NFT_IDs[0], 
			0, 
			1e18,
			zero_address,
			0,
			0, 
			{'from':accounts[1]})
	#nonexist nft
	with reverts("ERC721: approved query for nonexistent token"):
		wrapper.wrap721(
			erc721mock.address, 
			1, 
			0, 
			1e18,
			zero_address,
			0,
			0, 
			{'from':accounts[1]})
	#there is not allowance for wrapper.address
	with reverts("Please call approve in your NFT contract"):
		wrapper.wrap721(
			erc721mock.address, 
			ORIGINAL_NFT_IDs[0], 
			0, 
			1e18,
			zero_address,
			0,
			0, 
			{'from':accounts[1]})
	#check ROYALTY_PERCENT
	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
	with reverts("Royalty percent too big"):
		wrapper.wrap721(
			erc721mock.address, 
			ORIGINAL_NFT_IDs[0], 
			0, 
			1e18,
			zero_address,
			wrapper.MAX_ROYALTY_PERCENT() + 1,
			0, 
			{'from':accounts[1]})

	#check ROYALTY_PERCENT again
	with reverts("Royalty source is transferFee"):
		wrapper.wrap721(
			erc721mock.address, 
			ORIGINAL_NFT_IDs[0], 
			0, 
			0,
			zero_address,
			wrapper.MAX_ROYALTY_PERCENT(),
			0, 
			{'from':accounts[1]})

	#check ROYALTY_address 
	with reverts("No Royalty without transferFee"):
		wrapper.wrap721(
			erc721mock.address, 
			ORIGINAL_NFT_IDs[0], 
			0, 
			0,
			royaltyBeneficiary,
			0,
			0, 
			{'from':accounts[1]})

	#check _unwrapAfter
	with reverts("Too long Wrap"):
		wrapper.wrap721(
			erc721mock.address, 
			ORIGINAL_NFT_IDs[0], 
			chain.time() + wrapper.MAX_TIME_TO_UNWRAP() + 10,
			0,
			zero_address,
			0,
			0, 
			{'from':accounts[1]})

	#check _unwraptFeeThreshold
	with reverts("Too much threshold"):
		wrapper.wrap721(
			erc721mock.address, 
			ORIGINAL_NFT_IDs[0], 
			0,
			0,
			zero_address,
			0,
			niftsy20.totalSupply() * wrapper.MAX_FEE_THRESHOLD_PERCENT() / 100 + 1, 
			{'from':accounts[1]})

	wrapper.setFee(protokolFee, chargeFeeAfter, {"from": accounts[0]})
	#does not have niftsi token for protokol fee
	with reverts("insufficient NIFTSY balance for fee"):
		wrapper.wrap721(
			erc721mock.address, 
			ORIGINAL_NFT_IDs[0], 
			0,
			0,
			zero_address,
			0,
			0, 
			{'from':accounts[1]})

	niftsy20.transfer(accounts[1], protokolFee, {"from": accounts[0]})
	wrapper.wrap721(
		erc721mock.address, 
		ORIGINAL_NFT_IDs[0], 
		0,
		0,
		zero_address,
		0,
		0, 
		{'from':accounts[1]})

	assert wrapper.lastWrappedNFTId() == 1
	checkWrapedNFT(wrapper, wrapper.lastWrappedNFTId(), erc721mock.address, ORIGINAL_NFT_IDs[0], 0, 0, 0, 0, zero_address, 0, 0)



