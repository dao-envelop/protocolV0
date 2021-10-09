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

#unwrap 
def test_wrapper_unWrap721_1(accounts, erc721mock, wrapper, niftsy20, dai, weth, TokenMock,trmodel):
	#make test data
	niftsy20.approve(wrapper, TRANSFER_FEE, {'from':accounts[0]})
	makeNFTForTest(accounts, erc721mock, ORIGINAL_NFT_IDs)
	wrapper.setFee(protokolFee, chargeFeeAfter, niftsy20, {"from": accounts[0]})
	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
	logging.info('balanceOf(wrapper.address) = {}'.format(niftsy20.balanceOf(wrapper.address)))
	logging.info('balanceOf(royaltyBeneficiary) = {}'.format(niftsy20.balanceOf(royaltyBeneficiary)))
	#wrap difficult nft

	niftsy20.transfer(accounts[1], protokolFee, {"from": accounts[0]})
	unwrapAfter = chain.time() + 10
	
	before_balance = niftsy20.balanceOf(wrapper.address) 
	niftsy20.approve(wrapper, TRANSFER_FEE, {'from':accounts[1]})
	makeWrapNFT(wrapper, erc721mock, ['originalTokenId'], [ORIGINAL_NFT_IDs[0]], accounts[1], niftsy20)
	assert niftsy20.balanceOf(accounts[1]) == 0
	assert niftsy20.balanceOf(wrapper.address) == before_balance + protokolFee
	assert wrapper.lastWrappedNFTId() == 1

	tokenId = wrapper.lastWrappedNFTId()
	nft = wrapper.getWrappedToken(tokenId)

	c = round(UNWRAP_FEE_THRESHOLD/TRANSFER_FEE) + 1
	backedTokens = 0
	royalty_tokens = 0
	i = 0
	for i in range(c):
		wrapper.approve(accounts[i+2].address, tokenId, {"from": accounts[i+1]})
		niftsy20.transfer(accounts[i + 1].address, TRANSFER_FEE, {"from": accounts[0]}) #add niftsy tokens to pay transfer fee
		niftsy20.approve(trmodel, TRANSFER_FEE, {'from':accounts[i+1]})
		wrapper.transferFrom(accounts[i+1].address, accounts[i+2].address, tokenId, {"from": accounts[i+2]}) #make transfers
		royalty_tokens += TRANSFER_FEE*nft[7]/100
		backedTokens += TRANSFER_FEE - TRANSFER_FEE*nft[7]/100

	#check backedTokens after transfers
	nft = wrapper.getWrappedToken(tokenId)
	logging.info('nft2 = {}'.format(nft))
	assert nft[3] == backedTokens

	#add ERC20Collateral
	dai1 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI1")
	dai2 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI2")
	dai3 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI3")
	dai4 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI4")
	dai5 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI5")

	wrapper.setCollateralStatus(dai1.address, True, {"from": accounts[0]})
	wrapper.setCollateralStatus(dai2.address, True, {"from": accounts[0]})
	wrapper.setCollateralStatus(dai3.address, True, {"from": accounts[0]})
	wrapper.setCollateralStatus(dai4.address, True, {"from": accounts[0]})
	wrapper.setCollateralStatus(dai5.address, True, {"from": accounts[0]})

	dai1.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai2.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai3.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai4.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai5.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})

	dai1.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai2.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai3.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai4.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai5.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})

	wrapper.addERC20Collateral(tokenId, dai1.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai2.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai3.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai4.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai5.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	assert dai1.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai2.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai3.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai4.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai5.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai1.balanceOf(accounts[1].address) == 0
	assert dai2.balanceOf(accounts[1].address) == 0
	assert dai3.balanceOf(accounts[1].address) == 0
	assert dai4.balanceOf(accounts[1].address) == 0
	assert dai5.balanceOf(accounts[1].address) == 0
	assert len(wrapper.getERC20Collateral(tokenId)) == 5
	logging.info('wrapper.getERC20Collateral(tokenId) = {}'.format(wrapper.getERC20Collateral(tokenId)))
	
	#move date 
	chain.sleep(100)
	chain.mine()
	logging.info('wrapper.totalSupply() = {}'.format(wrapper.totalSupply()))
	logging.info('accounts[i+2].balance() = {}'.format(accounts[i+2].balance()))
	logging.info('wrapper.balanceOf(accounts[i+2]) = {}'.format(wrapper.balanceOf(accounts[i+2])))
	logging.info('niftsy20.balanceOf(accounts[i+2]) = {}'.format(niftsy20.balanceOf(accounts[i+2])))
	logging.info('wrapper.balance() = {}'.format(wrapper.balance()))
	logging.info('niftsy20.balanceOf(wrapper.address) = {}'.format(niftsy20.balanceOf(wrapper.address)))
	logging.info('niftsy20.balanceOf(wrapper.address) = {}'.format(niftsy20.balanceOf(wrapper.address)))
	balance_eth = accounts[i+2].balance()
	balance_erc20 = niftsy20.balanceOf(wrapper.address)
	balance_erc20_owner = niftsy20.balanceOf(accounts[i+2].address)
	logging.info('wrapper.getWrappedToken(tokenId) = {}'.format(wrapper.getWrappedToken(tokenId)))

	logging.info('********************AFTER UNWRAP*************')
	#unwrap
	wrapper.unWrap721(tokenId, {"from": accounts[i+2]})
	assert wrapper.totalSupply() == 0
	assert wrapper.balanceOf(accounts[i+2].address) == 0
	assert niftsy20.balanceOf(accounts[i+2].address) == balance_erc20_owner + backedTokens
	assert erc721mock.ownerOf(ORIGINAL_NFT_IDs[0]) == accounts[i+2].address
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

	assert dai1.balanceOf(wrapper.address) == 0
	assert dai2.balanceOf(wrapper.address) == 0
	assert dai3.balanceOf(wrapper.address) == 0
	assert dai4.balanceOf(wrapper.address) == 0
	assert dai5.balanceOf(wrapper.address) == 0
	assert dai1.balanceOf(accounts[i+2].address) == ERC20_COLLATERAL_AMOUNT
	assert dai2.balanceOf(accounts[i+2].address) == ERC20_COLLATERAL_AMOUNT
	assert dai3.balanceOf(accounts[i+2].address) == ERC20_COLLATERAL_AMOUNT
	assert dai4.balanceOf(accounts[i+2].address) == ERC20_COLLATERAL_AMOUNT
	assert dai5.balanceOf(accounts[i+2].address) == ERC20_COLLATERAL_AMOUNT
    # commented due new approach 20211009
	#assert len(wrapper.getERC20Collateral(tokenId)) == 0
	logging.info('wrapper.getERC20Collateral(tokenId) = {}'.format(wrapper.getERC20Collateral(tokenId)))