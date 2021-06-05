// SPDX-License-Identifier: MIT
// NIFTSY protocol ERC20
pragma solidity ^0.8.2;

import "OpenZeppelin/openzeppelin-contracts@4.1.0/contracts/token/ERC20/ERC20.sol";
import "./MinterRole.sol";

contract Niftsy is ERC20, MinterRole {
	//using SafeMath for uint256;

    uint256 constant MAX_SUPPLY = 500000000e18;

    constructor(address protocol)
    ERC20("NIFTSY protocol token", "NIFTSY")
    MinterRole(protocol)
    { 
        //Initial supply mint  - review before PROD
        _mint(msg.sender, MAX_SUPPLY);
    }

    function mint(address to, uint256 amount ) external onlyMinter {
        require(totalSupply() <= MAX_SUPPLY - amount, "MAX_SUPPLY amount exceed");
        _mint(to, amount);
    }

    //REmove if note used
    function burn(address to, uint256 amount ) external onlyMinter {
        _burn(to, amount);
    }

    /**
     * @dev Overriding standart function for gas transfer from protocol contract
     * Requirements:
     *
     * - `sender` and `recipient` cannot be the zero address.
     * - `sender` must have a balance of at least `amount`.
     * - the caller must have allowance for ``sender``'s tokens of at least (exclude trustedSpender)
     * `amount`.
     */
    function transferFrom(address sender, address recipient, uint256 amount) public override returns (bool) {

        if  (isMinter(msg.sender)==false) {
            return super.transferFrom(sender, recipient, amount);
        } else {
           _transfer(sender, recipient, amount);
           return true;
        }

    }

}
