from brownie import *
import json

if  (web3.eth.chainId != 56 
    and web3.eth.chainId != 1 
    and web3.eth.chainId != 137
    and web3.eth.chainId != 43114):
    # Testnets
    private_key='2cdbeadae3122f6b30a67733fd4f0fb6c27ccd85c3c68de97c8ff534c87603c8'
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

BSC_TESTNET_ERC20_COLLATERAL_TOKENS = [
'0xCEFe82aDEd5e1f8c2610256629d651840601EAa8', #NIFTSI ERC20
]

BSC_MAIN_ERC20_COLLATERAL_TOKENS = [
'0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3',  #DAI
'0x55d398326f99059fF775485246999027B3197955',  #USDT
'0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',  #USDC
]

POLYGON_MAIN_ERC20_COLLATERAL_TOKENS = [
'0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',  #DAI
'0xc2132D05D31c914a87C6611C10748AEb04B58e8F',  #USDT
'0x2791bca1f2de4661ed88a30c99a7a9449aa84174',  #USDC
]

AVALANCHE_MAIN_ERC20_COLLATERAL_TOKENS = [
'0xba7deebbfc5fa1100fb055a87773e1e99cd3507a',  #DAI
'0xde3a24028580884448a5397872046a019649b084',  #USDT
]

TRON_MAIN_ERC20_COLLATERAL_TOKENS = [
'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',  #USDT
]



CHAIN = {   
    0:{'explorer_base':'io'},
    1:{'explorer_base':'etherscan.io', 'enabled_erc20': ETH_MAIN_ERC20_COLLATERAL_TOKENS},
    4:{'explorer_base':'rinkeby.etherscan.io','enabled_erc20': ETH_RINKEBY_ERC20_COLLATERAL_TOKENS},
    56:{'explorer_base':'bscscan.com', 'enabled_erc20': BSC_MAIN_ERC20_COLLATERAL_TOKENS},
    97:{'explorer_base':' testnet.bscscan.com', 'enabled_erc20': BSC_TESTNET_ERC20_COLLATERAL_TOKENS},
    137:{'explorer_base':'polygonscan.com', 'enabled_erc20': POLYGON_MAIN_ERC20_COLLATERAL_TOKENS},
    80001:{'explorer_base':'mumbai.polygonscan.com', },  
    43114:{'explorer_base':'cchain.explorer.avax.network', 'enabled_erc20': AVALANCHE_MAIN_ERC20_COLLATERAL_TOKENS},
    43113:{'explorer_base':'cchain.explorer.avax-test.network', },

}.get(web3.eth.chainId, {'explorer_base':'io'})
print(CHAIN)



def main():
    print('Deployer account= {}'.format(accounts[0]))
    #techERC20 = TechToken.deploy({'from':accounts[0]})
    techERC20 = TechToken.at('0x6426Bc3F86E554f44bE7798c8D1f3482Fb7BB68C')
    wrapper   = WrapperWithERC20Collateral.deploy(techERC20.address,{'from':accounts[0]}) 
    #wrapper = WrapperWithERC20Collateral.at('0xc2571eBbc8F2af4f832bB8a2D3A4b0932Ce24773')
    trmodel   = TransferRoyaltyModel01.deploy(wrapper.address,{'from':accounts[0]})
    #trmodel   = TransferRoyaltyModel01.at('0x6664c8118284b3F5ECB47c2105cAa544Ab0Cf75B') 
    #Init
    techERC20.addMinter(wrapper.address, {'from': accounts[0]})
    if len(CHAIN.get('enabled_erc20', [])) > 0:
        print('Enabling collateral...')
        for erc in CHAIN.get('enabled_erc20', []):
            wrapper.editPartnersItem(erc, True, trmodel.address, False,{'from': accounts[0] })
    
    



    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("techERC20 = TechToken.at('{}')".format(techERC20.address))
    print("wrapper = WrapperWithERC20Collateral.at('{}')".format(wrapper.address))
    print("trmodel = TransferRoyaltyModel01.at('{}')".format(trmodel.address))
    
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],techERC20))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],wrapper))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],trmodel))

    if  web3.eth.chainId in [1,4, 43114]:
        TechToken.publish_source(techERC20);
        TransferRoyaltyModel01.publish_source(trmodel);
        WrapperWithERC20Collateral.publish_source(wrapper);

