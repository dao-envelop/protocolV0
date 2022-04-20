from brownie import *
import json

private_key='7a1851357aebcd2b94291fa3a321901430ed7715fa48906ec1b6d7dd28b1b723'
accounts.add(private_key)

print('Deployer:{}'.format(accounts[0]))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))

def main():
    print('Deployer account= {}'.format(accounts[0]))
    #distributor   = WrapperDistributor721.deploy(techERC20.address,{'from':accounts[0], 'gas_price': '30 gwei'}) 
    distributor = WrapperDistributor721.at('0xe96cd0542297e08972a14131be7e999b86591142')
    trmodel   = TransferRoyaltyModel01.deploy(distributor.address,{'from':accounts[0], 'gas_price': '30 gwei'})
    #trmodel   = TransferRoyaltyModel01.at('0xdC5A1cF2D671bbC15851727577Ce6f4AACEd9142')

    #niftsy20 = Niftsy.deploy(accounts[0],{'from':accounts[0], 'gas_price': '10 gwei'})
   
    #Init
    #techERC20.addMinter(distributor.address, {'from': accounts[0], 'gas_price': '10 gwei'})
    '''if len(CHAIN.get('enabled_erc20', [])) > 0:
        print('Enabling collateral...')
        for erc in CHAIN.get('enabled_erc20', []):
            distributor.editPartnersItem(erc, True, trmodel.address, False,{'from': accounts[0], 'gas_price': '10 gwei'})'''
    
    
    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("distributor = WrapperDistributor721.at('{}')".format(distributor.address))
    print("trmodel = TransferRoyaltyModel01.at('{}')".format(trmodel.address))
    #print("niftsy20 = Niftsy.at('{}')".format(niftsy20.address))
    
    
    
    TransferRoyaltyModel01.publish_source(trmodel);


#result

#trmodel = TransferRoyaltyModel01.at('0xdC5A1cF2D671bbC15851727577Ce6f4AACEd9142') - bsc-testnet
#trmodel = TransferRoyaltyModel01.at('0xFC733E3538EAB2DFb2f35040bb5491c909B65d71') - bsc-mainnet
#trmodel = TransferRoyaltyModel01.at('0x0384Dac880447E1d23749B3e987b1A2C5376DBF2') - polygon-main
#trmodel = TransferRoyaltyModel01.at('0x058B7b0fE9D1204E462EDbB01A85f2E57E8A5b7E') - polygon-test


