from brownie import *
import json

if web3.eth.chainId != 56 and web3.eth.chainId != 1 :
    # Rinkeby
    private_key='???'
else:
    # Mainnet
    private_key=input('PLease input private key for deployer address..:')
accounts.add(private_key)

print('Deployer:{}'.format(accounts[0]))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))

ETH_MAIN_ERC20_COLLATERAL_TOKENS = [
'0x7728cd70b3dD86210e2bd321437F448231B81733', #NIFTSI ERC20
'0x6b175474e89094c44da98b954eedeac495271d0f',  #DAI
'0xdAC17F958D2ee523a2206206994597C13D831ec7',  #USDT
'0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',  #USDC
]

ETH_RINKEBY_ERC20_COLLATERAL_TOKENS = [
'0x1E991eA872061103560700683991A6cF88BA0028', #NIFTSI ERC20
'0xc7ad46e0b8a400bb3c915120d284aafba8fc4735',  #DAI
'0xc778417e063141139fce010982780140aa0cd5ab',  #WETH
]

CHAIN = {   
    0:{'explorer_base':'io'},
    1:{'explorer_base':'etherscan.io', 'enabled_erc20': ETH_MAIN_ERC20_COLLATERAL_TOKENS},
    4:{'explorer_base':'rinkeby.etherscan.io','enabled_erc20': ETH_RINKEBY_ERC20_COLLATERAL_TOKENS},
    56:{'explorer_base':'bscscan.com'},
    97:{'explorer_base':' testnet.bscscan.com'},

}.get(web3.eth.chainId, {'explorer_base':'io'})
print(CHAIN)



def main():
    print('Deployer account= {}'.format(accounts[0]))
    techERC20 = TechToken.at('0xbbe47167666100eC33de9079c1EE7B150cCbD874')
    #distributor   = WrapperDistributor721.deploy(techERC20.address,{'from':accounts[0], 'gas_price': '30 gwei'}) 
    distributor = WrapperDistributor721.at('0xfCA81c8F236263c4CE94BF2205c60D9df06E6b63')
    trmodel   = TransferRoyaltyModel01.deploy(distributor.address,{'from':accounts[0], 'gas_price': '10 gwei'})
    niftsy20 = Niftsy.deploy(accounts[0],{'from':accounts[0], 'gas_price': '10 gwei'})
   
    #Init
    techERC20.addMinter(distributor.address, {'from': accounts[0], 'gas_price': '10 gwei'})
    if len(CHAIN.get('enabled_erc20', [])) > 0:
        print('Enabling collateral...')
        for erc in CHAIN.get('enabled_erc20', []):
            distributor.editPartnersItem(erc, True, trmodel.address, False,{'from': accounts[0], 'gas_price': '10 gwei'})
    
    distributor.editPartnersItem(niftsy20.address, True, trmodel.address, False,{'from': accounts[0], 'gas_price': '10 gwei'})
    
    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("techERC20 = TechToken.at('{}')".format(techERC20.address))
    print("distributor = WrapperDistributor721.at('{}')".format(distributor.address))
    print("trmodel = TransferRoyaltyModel01.at('{}')".format(trmodel.address))
    print("niftsy20 = Niftsy.at('{}')".format(niftsy20.address))
    
    
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],distributor))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],trmodel))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],niftsy20))

    if  web3.eth.chainId in [1,4]:
        TransferRoyaltyModel01.publish_source(trmodel);
        WrapperDistributor721.publish_source(distributor);
        Niftsy.publish_source(niftsy20);


#result
#techERC20 = TechToken.at('0xbbe47167666100eC33de9079c1EE7B150cCbD874')
#distributor = WrapperDistributor721.at('0xfCA81c8F236263c4CE94BF2205c60D9df06E6b63')
#trmodel = TransferRoyaltyModel01.at('0x4560C4278F38517a3a83e6ED9BBeB04aB8545008')
#niftsy20 = Niftsy.at('0x3125B3b583D576d86dBD38431C937F957B94B47d')

