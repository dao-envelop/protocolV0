// SPDX-License-Identifier: MIT
// NIFTSY protocol for NFT. Wrapper - main protocol contract
pragma solidity ^0.8.6;

import "./WrapperBase.sol";
/**
 * @title ERC-721 Non-Fungible Token Wrapper 
 * @dev For wrpap existing ERC721 with ability add ERC20 collateral
 */
contract WrapperWithERC20Collateral is WrapperBase {
    using SafeERC20 for IERC20;

    struct ERC20Collateral {
        address erc20Token;
        uint256 amount;
    }

    uint8 constant public MAX_ERC20_COUNT = 25; //max coins type count in collateral  

    //Map from wrapped token id to array  with erc20 collateral balances
    mapping(uint256 => ERC20Collateral[]) public erc20Collateral;

    event PartialUnWrapp(uint256 wrappedId, address owner);

    constructor (address _erc20) WrapperBase(_erc20) {} 

    /**
     * @dev Function for add arbitrary ERC20 collaterals 
     *
     * @param _wrappedTokenId  NFT id from thgis contarct
     * @param _erc20 address of erc20 collateral for add
     * @param _amount amount erc20 collateral for add  
     */
    function addERC20Collateral(uint256 _wrappedTokenId, address _erc20, uint256 _amount) external {
        require(ownerOf(_wrappedTokenId) != address(0));
        require(
            IERC20(_erc20).balanceOf(msg.sender) >= _amount,
            "Low balance for add collateral"
        );
        require(
            IERC20(_erc20).allowance(msg.sender, address(this)) >= _amount,
            "Please approve first"
        );

        IERC20(_erc20).safeTransferFrom(msg.sender, address(this), _amount);

        ERC20Collateral[] storage e = erc20Collateral[_wrappedTokenId];
        //If collateral  with this _erc20 already exist just update
        for (uint256 i = 0; i < e.length; i ++) {
            if (e[i].erc20Token == _erc20) {
                e[i].amount += _amount;
                return;
            }
        }
        //We can add more tokens if limit not exccedd
        if (e.length < MAX_ERC20_COUNT){
            e.push(ERC20Collateral({
              erc20Token: _erc20, 
              amount: _amount
            }));
        }
        
    }


    function getERC20Collateral(uint256 _wrappedId) external view returns (ERC20Collateral[] memory) {
        return erc20Collateral[_wrappedId];
    } 


    /////////////////////////////////////////////////////////////////////
    /////////////   Internals     ///////////////////////////////////////
    /////////////////////////////////////////////////////////////////////
    

    function _beforeUnWrapHook(uint256 _tokenId) internal virtual override(WrapperBase) returns (bool){
        return _returnERC20Collateral(_tokenId);
    }

    function _returnERC20Collateral(uint256 _tokenId) internal returns (bool) {
        //First we need release erc20 collateral, because erc20 transfers are
        // can be expencive
        ERC20Collateral[] storage e = erc20Collateral[_tokenId];
        if (e.length > 0) { 
            uint256 n = _getTransferBatchCount();
            if (e.length <= n) {
                n = e.length;
            } 
            
            for (uint256 i = n; i > 0; i --){
                IERC20(e[i-1].erc20Token).safeTransfer(msg.sender,  e[i-1].amount);
                e.pop();
            }

            // If not all erc20 collateral were transfered
            // we just exit.  User can finish unwrap with next tx
            if  (e.length > 0 ) {
                emit PartialUnWrapp(_tokenId, msg.sender);
                return false;
            }
        }
        return true;

    }

    function _getTransferBatchCount() internal view returns (uint256){
        // It can be modified in future protocol version
        return block.gaslimit / 50000; //average erc20 transfer cost 
    }

}