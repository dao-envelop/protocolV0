from brownie import *
import json

private_key='721fd469cc7604dcc6ab618e4055822216d977cd14deeae23e6e452c82da9ae9'
accounts.add(private_key)

def main():
    print('Deployer account= {}'.format(accounts[0]))
    #originalNFT = OrigNFT.deploy("Simple NFT with default uri", "XXX", 'https://envelop.is/metadata/', {'from':accounts[0], 'gas_price': '60 gwei'})
    
    # Print addresses for quick access from console
    #originalNFT = OrigNFT.at('0x43fac3a97A78F6F2F6116e05BEcdF8C13c90ee03')
    #print("----------Deployment artifacts-------------------")
    #print("originalNFT = OrigNFT.at('{}')".format(originalNFT.address))

    originalNFT = OrigNFT.at('0xb6CB784a59439515DFEc0D18170C06c085135113')

    #if  web3.eth.chainId in [1,4]:
    #    OrigNFT.publish_source(originalNFT);

    

    #originalNFT.mint(accounts[0], {"from": accounts[0]})

    #0x1d612Ea6D87f045a8ef521AB1263A6B9bF2c0284 - bsc testnet
    #0xe1383d47550b7b3b2ea6c4d327627a0a167f7b4b - rinkeby
    print(originalNFT.tokenURI(1))