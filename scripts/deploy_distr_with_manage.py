from brownie import *
import json

if  len(accounts) == 0:
    if  web3.eth.chainId in [1,56]:
        # Available Main nets
        accounts.load('envdeployer')
    else:
        accounts.load('tzero','')     

   

print('Deployer:{}, balance = {}'.format(
    accounts[0], 
    Wei(accounts[0].balance()).to('ether')
))
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

BSC_MAIN_ERC20_COLLATERAL_TOKENS = [
'0x7728cd70b3dD86210e2bd321437F448231B81733', #NIFTSI ERC20
'0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3',  #DAI
'0x55d398326f99059fF775485246999027B3197955',  #BUSD-T
'0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',  #USDC
'0xF81628EDeb110a73c016ab7aFA57d80afAe07f59'   #LOTT
]

BSC_TESTNET_ERC20_COLLATERAL_TOKENS = []
POLYGON_MAIN_ERC20_COLLATERAL_TOKENS = []
AVALANCHE_MAIN_ERC20_COLLATERAL_TOKENS = []



CHAIN = {   
    0:{'explorer_base':'io'},
    1:{'explorer_base':'etherscan.io', 'enabled_erc20': ETH_MAIN_ERC20_COLLATERAL_TOKENS},
    4:{'explorer_base':'rinkeby.etherscan.io','enabled_erc20': ETH_RINKEBY_ERC20_COLLATERAL_TOKENS},
    56:{'explorer_base':'bscscan.com', 'enabled_erc20': BSC_MAIN_ERC20_COLLATERAL_TOKENS},
    65:{'explorer_base': 'www.oklink.com/oec-test',},
    66:{'explorer_base': 'www.oklink.com/oec',},
    85:{'explorer_base': 'https://gatescan.org/testnet',},
    86:{'explorer_base': 'https://www.gatescan.org',},
    97:{'explorer_base':'testnet.bscscan.com', 'enabled_erc20': BSC_TESTNET_ERC20_COLLATERAL_TOKENS},
    137:{'explorer_base':'polygonscan.com', 'enabled_erc20': POLYGON_MAIN_ERC20_COLLATERAL_TOKENS},
    80001:{'explorer_base':'mumbai.polygonscan.com', },  
    43114:{'explorer_base':'cchain.explorer.avax.network', 'enabled_erc20': AVALANCHE_MAIN_ERC20_COLLATERAL_TOKENS},
    43113:{'explorer_base':'cchain.explorer.avax-test.network', },

}.get(web3.eth.chainId, {'explorer_base':'io'})

print(CHAIN)

tx_params = {'from':accounts[0]}

if web3.eth.chainId in  [1,4]:
    tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}
elif web3.eth.chainId in  [65, 66]:    
    tx_params={'from':accounts[0], 'allow_revert': True}    
elif web3.eth.chainId in  [85, 86]:
    tx_params={'from':accounts[0], 'allow_revert': True,'gas_price': '5 gwei', 'gas_limit': 1e8} 

def main():
    #techERC20 = TechToken.deploy(tx_params)
    techERC20 = TechToken.at('0x6426Bc3F86E554f44bE7798c8D1f3482Fb7BB68C')
    distributor   = WrapperDistributor721Saft.deploy(
        'https://api.envelop.is/metadata/',
        techERC20.address, 
        tx_params
    ) 
    #distributor = WrapperDistributor721Saft.at('')
    trmodel = TransferRoyaltyModel01.deploy(distributor.address,tx_params)
   
    manager = DistribManager.deploy(distributor, tx_params) 
    #Init
    techERC20.addMinter(distributor.address,tx_params)
    if len(CHAIN.get('enabled_erc20', [])) > 0:
        print('Enabling collateral...')
        for erc in CHAIN.get('enabled_erc20', []):
            distributor.editPartnersItem(erc, True, trmodel.address, False,tx_params)
    
    
    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("techERC20 = TechToken.at('{}')".format(techERC20.address))
    print("distributor = WrapperDistributor721Saft.at('{}')".format(distributor.address))
    print("trmodel = TransferRoyaltyModel01.at('{}')".format(trmodel.address))
    print("manager = DistribManager.at('{}')".format(manager.address))
    
    
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],distributor))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],trmodel))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],manager))

    if  web3.eth.chainId in [1,4,56]:
        TransferRoyaltyModel01.publish_source(trmodel);
        WrapperDistributor721Saft.publish_source(distributor);
        DistribManager.publish_source(manager)




