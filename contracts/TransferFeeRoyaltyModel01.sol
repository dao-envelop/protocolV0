// SPDX-License-Identifier: MIT
// NIFTSY protocol ERC20
pragma solidity ^0.8.6;

import "../interfaces/IFeeRoyaltyCharger.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";



contract TransferRoyaltyModel01 is IFeeRoyaltyCharger {
    using SafeERC20 for IERC20;
    
    address public wrapperContract;
    constructor(address _wrapper)
    { 
        wrapperContract = _wrapper;
    }

   
    /**
     * @dev Function is part of transferFeeModel interface
     * for charge fee in tech protokol Token 
     *
     */
    function chargeTransferFeeAndRoyalty(
        address from, 
        address to, 
        uint256 transferFee, 
        uint256 royaltyPercent, 
        address royaltyBeneficiary,
        address _transferFeeToken
    ) external
      override 
      returns (uint256 feeIncrement)
    {
        require(msg.sender == wrapperContract, "Wrapper only");
        uint256 rAmount = royaltyPercent * transferFee / 100;
        require(
            IERC20(_transferFeeToken).allowance(from, address(this)) >= transferFee,
            "insufficient NIFTSY balance for fee"
        );
        
        IERC20(_transferFeeToken).safeTransferFrom(from, wrapperContract, transferFee - rAmount);
        if (royaltyBeneficiary != address(0) && rAmount > 0) {
            IERC20(_transferFeeToken).safeTransferFrom(from, royaltyBeneficiary, rAmount);
        }    
        return transferFee - rAmount;
    }

}
