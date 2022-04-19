// SPDX-License-Identifier: MIT

pragma solidity ^0.8.6;

import "./IWrapperCollateral.sol";

interface IWrapperDistributor is  IWrapperCollateral {

    function WrapAndDistrib721WithMint(
        address _original721, 
        address[] memory _receivers,
        uint256[] memory _tokenIds, 
        ERC20Collateral[] memory _forDistrib,
        uint256 _unwrapAfter
    ) external payable;

    function WrapAndDistribEmpty(
        address[] memory _receivers,
        ERC20Collateral[] memory _forDistrib,
        uint256 _unwrapAfter
    ) external payable; 

    function setDistributorState(address _user, bool _state) external;

    function transferOwnership(address newOwner) external;

    function distributors(address _distributor) external view returns(bool);
    function lastWrappedNFTId() external view returns(uint256);
    
    
}