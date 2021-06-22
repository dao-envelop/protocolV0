import pytest
import logging

def checkWrapedNFT(wrapper, tokenId, tokenContract, originalTokenId, backedValue, backedTokens, unwrapAfter, transferFee, royaltyBeneficiary, royaltyPercent, unwraptFeeThreshold):
	nft = wrapper.getWrappedToken(tokenId)
	
	assert nft[0] == tokenContract # tokenContract
	assert nft[1] == originalTokenId # tokenId
	assert nft[2] == backedValue # backedValue
	assert nft[3] == backedTokens # backedTokens
	logging.info('check nft4 = {}'.format(nft[4]))
	logging.info('check unwrapAfter = {}'.format(unwrapAfter))
	assert abs(nft[4] - unwrapAfter) < 3 # unwrapAfter
	assert nft[5] == transferFee # transferFee
	assert nft[6] == royaltyBeneficiary #royaltyBeneficiary
	assert nft[7] == royaltyPercent # royaltyPercent
	assert nft[8] == unwraptFeeThreshold #unwraptFeeThreshold