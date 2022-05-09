from brownie import *
import json

#1 - 0xa11103Da33d2865C3B70947811b1436ea6Bb32eF
private_key='???'
accounts.add(private_key)

print('Deployer:{}'.format(accounts[0]))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))

ERC20_COLLATERAL_AMOUNT = 200000e18
TIMELOCK = 3600*24*30*12
TICKET_VALID = 3600*24*30

def main():
    print('Deployer account= {}'.format(accounts[0]))
    #distributor = WrapperDistributor721.at('0x166f56bD3fE11bc55A981a99dCC61Ab931585AbD')
    #distrManager = DistribManager.deploy(distributor.address,{'from':accounts[0], 'gas_price': '10 gwei'})
    #DistribManager.publish_source(distrManager);

    distrManager = DistribManager.at("0x0a1e65A78aAfA3c63642531aEcADC98945Ddb724")


    #distrManager.addTarif(("0x7728cd70b3dD86210e2bd321437F448231B81733", ERC20_COLLATERAL_AMOUNT, TIMELOCK, TICKET_VALID), {'from':accounts[0]})
    distrManager.editTarif(0,"0x7728cd70b3dD86210e2bd321437F448231B81733", ERC20_COLLATERAL_AMOUNT, TIMELOCK, TICKET_VALID, {'from':accounts[0]})
    
    
    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("distrManager = DistribManager.at('{}')".format(distrManager.address))
    
 
    #rinkeby 0x679fc9D68d1Ccf20771F32368A0F8bCC2ebe6248
    #bsc-main 0x0a1e65A78aAfA3c63642531aEcADC98945Ddb724
    #bsc-testnet 0x894d235264e9D01F4f8aAD4C3Bba0d06c43cb495