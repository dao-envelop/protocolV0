// SPDX-License-Identifier: MIT

pragma solidity 0.8.10;

import "@openzeppelin/contracts/token/ERC721/extensions/IERC721Enumerable.sol";
import "./IWrapperCollateral.sol";

interface IWrapperCollateralWrap is  IWrapperCollateral {

    function wrap721(
        address _underlineContract, 
        uint256 _tokenId, 
        uint256 _unwrapAfter,
        uint256 _transferFee,
        address _royaltyBeneficiary,
        uint256 _royaltyPercent,
        uint256 _unwraptFeeThreshold,
        address _transferFeeToken
    ) 
        external 
        payable
        returns (uint256);   
 
    function addERC20Collateral(
        uint256 _wrappedTokenId, 
        address _erc20, 
        uint256 _amount
    ) external;

    function addNativeCollateral(uint256 _wrappedTokenId) external payable;

    /**
     * @dev Function for unwrap protocol token. If wrapped  NFT
     * has many erc20 collateral tokens it possible call this method
     * more than once, until unwrapped
     *
     * @param _tokenId id of protocol token to unwrapp
     */
    function unWrap721(uint256 _tokenId) external;
}