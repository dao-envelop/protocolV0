from brownie import *
import json

accounts.clear()
#1 - 0xa11103Da33d2865C3B70947811b1436ea6Bb32eF
private_key='???'
accounts.add(private_key)

print('Deployer:{}'.format(accounts[0]))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))

def main():
    print('Deployer account= {}'.format(accounts[0]))
    erc20mock = TokenMock.deploy("ERC20 mock tokens", "ETM", {"from": accounts[0]})


    
    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("erc20mock = TokenMock.at('{}')".format(erc20mock.address))
    
 #okx-main  erc20mock = TokenMock.at('0xB7Ca883C29045D435d01de25b9522b937964f583')
