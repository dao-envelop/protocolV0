def makeNFTForTest(accounts, erc721mock, ORIGINAL_NFT_IDs):
    [erc721mock.mint(x, {'from':accounts[0]})  for x in ORIGINAL_NFT_IDs]
    erc721mock.transferFrom(accounts[0], accounts[1], ORIGINAL_NFT_IDs[0], {'from':accounts[0]})