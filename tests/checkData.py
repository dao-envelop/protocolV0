import pytest
import logging

def checkWrappedNFT(wrapper, tokenId, tokenContract, originalTokenId, backedValue, backedTokens, unwrapAfter, transferFee, royaltyBeneficiary, royaltyPercent, unwraptFeeThreshold):
	nft = wrapper.getWrappedToken(tokenId)
	#logging.info('nft = {}'.format(nft))
	assert nft[0] == tokenContract # tokenContract
	assert nft[1] == originalTokenId # tokenId
	assert nft[2] == backedValue # backedValue
	assert nft[3] == backedTokens # backedTokens
	assert abs(nft[4] - unwrapAfter) < 3 # unwrapAfter
	#logging.info('nft= {}'.format(nft[5]))
	#logging.info('transferFee= {}'.format(transferFee))
	assert nft[5] == transferFee # transferFee
	assert nft[6] == royaltyBeneficiary #royaltyBeneficiary
	assert nft[7] == royaltyPercent # royaltyPercent
	assert nft[8] == unwraptFeeThreshold #unwraptFeeThreshold
