// SPDX-License-Identifier: MIT
// NIFTSY protocol for NFT
pragma solidity ^0.8.6;
import "../MinterRole.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MaliciousTokenMock is ERC20 {

    address public failSender;
    constructor(string memory name_,
        string memory symbol_) ERC20(name_, symbol_)  {
        _mint(msg.sender, 1000000000000000000000000000);

    }

    function setFailSender(address _failSender) external {
        failSender = _failSender;
    }

    function _beforeTokenTransfer(address from, address to, uint256 amount) internal override {
        if (from != address(0)){
            require(from != failSender, "Hack your Wrapper");    
        } 
        
    }


}
