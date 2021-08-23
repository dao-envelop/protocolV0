import pytest
import logging
from brownie import chain
LOGGER = logging.getLogger(__name__)

ORIGINAL_NFT_IDs_ = []


#logging.info('make UNWRAPAFTER_ = {}'.format(UNWRAPAFTER_))

def makeNFTForTest(accounts, erc721mock, original_nft_ids):
    [erc721mock.mint(x, {'from':accounts[0]})  for x in original_nft_ids]
    erc721mock.transferFrom(accounts[0], accounts[1], original_nft_ids[0], {'from':accounts[0]})

def makeWrapNFT(wrapper, erc721mock, fields, values, account, niftsy20):
    START_NATIVE_COLLATERAL_ = '1 ether'
    ADD_NATIVE_COLLATERAL_ = '2 ether'
    ERC20_COLLATERAL_AMOUNT_ = 2e17;
    TRANSFER_FEE_ = 2e18
    ROAYLTY_PERCENT_ = 10
    UNWRAP_FEE_THRESHOLD_ = 6e18
    protokolFee_ = 10
    chargeFeeAfter_ = 10
    ROYALTYBENEFICIARY_= '0xbd7e5fb7525ed8583893ce1b1f93e21cc0cf02f6'
    zero_address_ = '0x0000000000000000000000000000000000000000'
    UNWRAPAFTER_ = chain.time() + 10

    #logging.info('TRANSFER_FEE_ from make 1= {}'.format(TRANSFER_FEE_))

    #logging.info('make UNWRAPAFTER_ = {}'.format(UNWRAPAFTER_))
    
    UNDERLINECONTRACT_ = erc721mock.address
    UNWRAPAFTER_ = chain.time() + 10
    for i in range(len(fields)):
        if fields[i] ==  'originalTokenId':
            ORIGINAL_NFT_IDs_ = []
            ORIGINAL_NFT_IDs_.append(values[i])
        elif fields[i] ==  'unwrapAfter':
            UNWRAPAFTER_ = values[i]
        elif fields[i] ==  'transferFee':
            TRANSFER_FEE_ = values[i]
        elif fields[i] ==  'royaltyBeneficiary':
            ROYALTYBENEFICIARY_ = values[i]
        elif fields[i] ==  'royaltyPercent':
            ROAYLTY_PERCENT_ = values[i]
        elif fields[i] ==  'start_native_collateral':
            START_NATIVE_COLLATERAL_ = values[i]
        else: #result
            UNWRAP_FEE_THRESHOLD_ = values[i]
    #logging.info('TRANSFER_FEE_ from make 2= {}'.format(TRANSFER_FEE_))

    erc721mock.approve(wrapper.address, ORIGINAL_NFT_IDs_[0], {'from':account})
    
    wrapper.wrap721(
        UNDERLINECONTRACT_, 
        ORIGINAL_NFT_IDs_[0], 
        UNWRAPAFTER_,
        TRANSFER_FEE_,
        ROYALTYBENEFICIARY_,
        ROAYLTY_PERCENT_,
        UNWRAP_FEE_THRESHOLD_, 
        niftsy20.address,
        {'from':account, 'value':START_NATIVE_COLLATERAL_})
    assert erc721mock.ownerOf(ORIGINAL_NFT_IDs_[0]) == wrapper.address
    assert wrapper.ownerOf(wrapper.lastWrappedNFTId()) == account

def _addErc20Collateral(account0, account1, wrapper, amount, tokenId , TokenMock):
    dai = account0.deploy(TokenMock,"DAI MOCK Token", "DAI")
    wrapper.setCollateralStatus(dai.address, True, {"from": account0})
    dai.approve(wrapper.address, amount, {"from": account1})
    dai.transfer(account1, amount, {"from": account0})
    wrapper.addERC20Collateral(tokenId, dai.address, amount, {"from": account1})
    assert dai.balanceOf(wrapper.address) == amount
    #logging.info('dai.balanceOf(account.address) = {}'.format(dai.balanceOf(account1.address)))
    assert dai.balanceOf(account1.address) == 0
    return dai

    
    