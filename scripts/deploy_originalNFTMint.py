from brownie import *
import json

#private_key='???'
#0-0xE71978b1696a972b1a8f724A4eBDB906d9dA0885
private_key='???'
accounts.add(private_key)

def main():
    print('Deployer account= {}'.format(accounts[0]))
    originalNFT = OrigNFT.deploy("Envelop simple NFT", "ENVELOP", 'https://envelop.is/metadata/', {'from':accounts[0], 'gas_price': '60 gwei'})
    #originalNFT = EnvelopERC721.deploy("Envelop simple NFT", "Envelop", 'https://envelop.is/metadata/', {'from':accounts[0], 'gas_price': '40 gwei'})
    
    # Print addresses for quick access from console
    #originalNFT = OrigNFT.at('0xfE8e7F2aF5C9b2d131513E3ec99Aed78BAE5c8B9')
    #originalNFT = EnvelopERC721.at('0x32A7A8574b415F50C5A4e6802fF1ccB40DE93420')
    #distributor = WrapperDistributor721.at('0xfD137b2dC3578e0D9bB450C39D9EB647e12dE30C') - bsc testnet
    print("----------Deployment artifacts-------------------")
    print("originalNFT = OrigNFT.at('{}')".format(originalNFT.address))

    #originalNFT.setMinter(distributor.address, {"from": accounts[0], 'gas_price': '60 gwei'})

    #originalNFT = OrigNFT.at('0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578')
    #niftsy20 = Niftsy.at('0x1E991eA872061103560700683991A6cF88BA0028')


    #if  web3.eth.chainId in [1,4]:
    #    OrigNFT.publish_source(originalNFT);
    #print("originalNFT = EnvelopERC721.at('{}')".format(originalNFT.address))

    OrigNFT.publish_source(originalNFT)
    #EnvelopERC721.publish_source(originalNFT)
    #Niftsy.publish_source(niftsy20)

    

    #originalNFT.mint(accounts[0], {"from": accounts[0]})

    #0x1d612Ea6D87f045a8ef521AB1263A6B9bF2c0284 - bsc-test
    #0xfE8e7F2aF5C9b2d131513E3ec99Aed78BAE5c8B9 - bsc-test
    #0xcfbE64f70fC990a87384C073a486a231BED11D3c - bsc-test

    
    #0xe1383d47550b7b3b2ea6c4d327627a0a167f7b4b - rinkeby
    #0x11d30360d423DC2ACf8705007F87957739438aB6 - rinkeby

    #last deploy - OrigNFT
    #0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578 - bsc-test
    #0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578 - rinkeby
    #0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578 - bsc-main
    #0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578 - polygon - mainnet
    #0x03D6f1a04ab5Ca96180a44F3bd562132bCB8b578 - polygon - testnet

    #last deploy - EnvelopERC721
    #0x32A7A8574b415F50C5A4e6802fF1ccB40DE93420 - bsc-test
    #0x32A7A8574b415F50C5A4e6802fF1ccB40DE93420 - bsc-main
    #0x32A7A8574b415F50C5A4e6802fF1ccB40DE93420 - rinkeby
    #0xDb9C821142F19Ae0172E4E631a3Bd185430b7f0d - polygon - mainnet
    #0x48C78C0ae35F683210FbBB2D2D64e3F1c477De6B - polygon - testnet

    #print(originalNFT.tokenURI(2))

    #originalNFT.approve('0xfD137b2dC3578e0D9bB450C39D9EB647e12dE30C', 1, {"from": accounts[0]})
    #originalNFT.approve('0xfD137b2dC3578e0D9bB450C39D9EB647e12dE30C', 4, {"from": accounts[0]})
    '''print(originalNFT.ownerOf(1))
    print(originalNFT.ownerOf(4))

    RECEIVERS = ['0x989FA3062bc4329B2E3c5907c48Ea48a38437fB7', '0x989FA3062bc4329B2E3c5907c48Ea48a38437fB7']
    ORIGINAL_NFT_IDs = [1, 4]
    tx = distributor.WrapAndDistrib721WithMint(
        originalNFT.address, 
        RECEIVERS,
        ORIGINAL_NFT_IDs, 
        [],
        0,
        {'from':accounts[0], "value": "0.0001 ether", 'gas': 30_000_000, "allow_revert": True}
    )'''

