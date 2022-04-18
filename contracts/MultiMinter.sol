// SPDX-License-Identifier: MIT
// ENVELOP (NIFTSY) protocol for NFT. MultiMinter
pragma solidity 0.8.10;

//import "./WrapperWithERC20Collateral.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IERC721Mintable.sol";

/**
 * @title ERC-721 Non-Fungible Token Wrapper 
 * @dev For multiMint erc721
 */
contract MultiMinter721 is Ownable {
    
    mapping(address => bool) public distributors;

    constructor () 
    {
        distributors[msg.sender] = true;

    }

    function multiMint(
        address _original721, 
        address[] memory _receivers,
        uint256[] memory _tokenIds 
    ) public  
    {
        require(distributors[msg.sender], "Only for distributors");
        //require(_receivers.length <= 256, "Not more 256");
        require(_receivers.length == _tokenIds.length, "Not equal arrays");

        for (uint8 i = 0; i < _receivers.length; i ++) {
            // 1. Lits mint 721, but for gas save we will not do it for receiver
            // but wrapper contract as part of wrapp process
            IERC721Mintable(_original721).mint(_receivers[i], _tokenIds[i]);
        }
    }


    ////////////////////////////////////////////////////////////////
    //////////     Admins                                     //////
    ////////////////////////////////////////////////////////////////

    function setDistributorState(address _user, bool _state) external onlyOwner {
        distributors[_user] = _state;
    }

    function revokeOwnership(address _contract) external onlyOwner {
        IERC721Mintable(_contract).transferOwnership(owner());
    }
    ////////////////////////////////////////////////////////////////

   
}

