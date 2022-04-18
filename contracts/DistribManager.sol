// SPDX-License-Identifier: MIT
// ENVELOP (NIFTSY) protocol for NFT. Distributor Role Manager
pragma solidity 0.8.10;


import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../interfaces/IWrapperDistributor.sol";

/**
 * @title ERC-721 Non-Fungible Token Wrapper 
 * @dev For multiMint erc721
 */
contract DistribManager is Ownable {
    using SafeERC20 for IERC20;
    
    // mapping from address to block timestamp
    mapping(address => uint256) public validDistributors;
    IWrapperDistributor public wrapper;

    constructor (address distribContracr) 
    {
        wrapper = IWrapperDistributor(distribContracr);
    }


   


    ////////////////////////////////////////////////////////////////
    //////////     Admins                                     //////
    ////////////////////////////////////////////////////////////////

    function revokeOwnership(address _contract) external onlyOwner {
        wrapper.transferOwnership(owner());
    }

    ////////////////////////////////////////////////////////////////

   
}

