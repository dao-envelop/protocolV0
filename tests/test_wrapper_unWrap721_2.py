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
def test_wrapper_unWrap721_1(accounts, erc721mock, wrapper, niftsy20, dai, weth, TokenMock):
	#make test data
	makeNFTForTest(accounts, erc721mock, ORIGINAL_NFT_IDs)
	wrapper.setFee(protokolFee, chargeFeeAfter, {"from": accounts[0]})
	erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs[0], {'from':accounts[1]})
	logging.info('balanceOf(wrapper.address) = {}'.format(niftsy20.balanceOf(wrapper.address)))
	logging.info('balanceOf(royaltyBeneficiary) = {}'.format(niftsy20.balanceOf(royaltyBeneficiary)))
	#wrap difficult nft

	niftsy20.transfer(accounts[1], protokolFee, {"from": accounts[0]})
	unwrapAfter = chain.time() + 10
	
	before_balance = niftsy20.balanceOf(wrapper.address) 
	makeWrapNFT(wrapper, erc721mock, ['originalTokenId'], [ORIGINAL_NFT_IDs[0]], accounts[1])
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
	dai6 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI6")
	dai7 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI7")
	dai8 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI8")
	dai9 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI9")
	dai10 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI10")
	dai11 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI11")
	dai12 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI12")
	dai13 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI13")
	dai14 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI14")
	dai15 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI15")
	dai16 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI16")
	dai17 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI17")
	dai18 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI18")
	dai19 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI19")
	dai20 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI20")
	dai21 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI21")
	dai22 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI22")
	dai23 = accounts[0].deploy(TokenMock,"DAI MOCK Token1", "DAI23")
	
	dai1.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai2.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai3.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai4.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai5.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai6.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai7.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai8.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai9.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai10.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai11.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai12.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai13.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai14.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai15.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai16.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai17.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai18.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai19.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai20.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai21.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai22.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})
	dai23.transfer(accounts[1], ERC20_COLLATERAL_AMOUNT, {"from": accounts[0]})

	dai1.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai2.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai3.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai4.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai5.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai6.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai7.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai8.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai9.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai10.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai11.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai12.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai13.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai14.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai15.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai16.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai17.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai18.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai19.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai20.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai21.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai22.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	dai23.approve(wrapper.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})

	wrapper.addERC20Collateral(tokenId, dai1.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai2.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai3.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai4.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai5.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai6.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai7.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai8.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai9.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai10.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai11.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai12.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai13.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai14.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai15.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai16.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai17.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai18.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai19.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai20.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai21.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai22.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	wrapper.addERC20Collateral(tokenId, dai23.address, ERC20_COLLATERAL_AMOUNT, {"from": accounts[1]})
	
	assert dai1.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai2.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai3.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai4.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai5.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai6.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai7.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai8.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai9.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai10.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai11.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai12.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai13.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai14.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai15.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai16.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai17.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai18.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai19.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai20.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai21.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai22.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT
	assert dai23.balanceOf(wrapper.address) == ERC20_COLLATERAL_AMOUNT

	assert dai1.balanceOf(accounts[1].address) == 0
	assert dai2.balanceOf(accounts[1].address) == 0
	assert dai3.balanceOf(accounts[1].address) == 0
	assert dai4.balanceOf(accounts[1].address) == 0
	assert dai5.balanceOf(accounts[1].address) == 0
	assert dai6.balanceOf(accounts[1].address) == 0
	assert dai7.balanceOf(accounts[1].address) == 0
	assert dai8.balanceOf(accounts[1].address) == 0
	assert dai9.balanceOf(accounts[1].address) == 0
	assert dai10.balanceOf(accounts[1].address) == 0
	assert dai11.balanceOf(accounts[1].address) == 0
	assert dai12.balanceOf(accounts[1].address) == 0
	assert dai13.balanceOf(accounts[1].address) == 0
	assert dai14.balanceOf(accounts[1].address) == 0
	assert dai15.balanceOf(accounts[1].address) == 0
	assert dai16.balanceOf(accounts[1].address) == 0
	assert dai17.balanceOf(accounts[1].address) == 0
	assert dai18.balanceOf(accounts[1].address) == 0
	assert dai19.balanceOf(accounts[1].address) == 0
	assert dai20.balanceOf(accounts[1].address) == 0
	assert dai21.balanceOf(accounts[1].address) == 0
	assert dai22.balanceOf(accounts[1].address) == 0
	assert dai23.balanceOf(accounts[1].address) == 0
	assert len(wrapper.getERC20Collateral(tokenId)) == 23
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
	balance_eth = accounts[i+2].balance()
	balance_erc20 = niftsy20.balanceOf(wrapper.address)
	balance_erc20_owner = niftsy20.balanceOf(accounts[i+2].address)
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

	'''assert dai1.balanceOf(wrapper.address) == 0
	assert dai2.balanceOf(wrapper.address) == 0
	assert dai3.balanceOf(wrapper.address) == 0
	assert dai4.balanceOf(wrapper.address) == 0
	assert dai5.balanceOf(wrapper.address) == 0
	assert dai1.balanceOf(accounts[i+2].address) == ERC20_COLLATERAL_AMOUNT
	assert dai2.balanceOf(accounts[i+2].address) == ERC20_COLLATERAL_AMOUNT
	assert dai3.balanceOf(accounts[i+2].address) == ERC20_COLLATERAL_AMOUNT
	assert dai4.balanceOf(accounts[i+2].address) == ERC20_COLLATERAL_AMOUNT
	assert dai5.balanceOf(accounts[i+2].address) == ERC20_COLLATERAL_AMOUNT'''

	assert len(wrapper.getERC20Collateral(tokenId)) == 0
	logging.info('wrapper.getERC20Collateral(tokenId) = {}'.format(wrapper.getERC20Collateral(tokenId)))