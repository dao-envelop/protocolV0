// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Wrapper - main protocol contract
pragma solidity 0.8.11;
import "@openzeppelin/contracts/access/Ownable.sol";

contract WLAllocation is Ownable {
    struct ERC20Allocation {
        uint256 allocation;  // user's reserved allocation
        uint256 used;        // 
    }

    
    mapping(address => bool) public trustedOperators;
    
    // mpp from user to tokenaddress to allocation
    mapping(address => mapping(address => ERC20Allocation)) public userAllocation;

    constructor () {
        trustedOperators[msg.sender] = true;
    }

    function increaseAllocation(address _user, address _erc20, uint256 _increment) public {
        require(trustedOperators[msg.sender], "Trusted operators only");
        userAllocation[_user][_erc20].allocation += _increment;
    }

    function decreaseAllocation(address _user, address _erc20, uint256 _decrement) public {
        require(trustedOperators[msg.sender], "Trusted operators only");
        require(
            userAllocation[_user][_erc20].allocation - _decrement >= userAllocation[_user][_erc20].used,
            "Cant set less then used"
        );
        userAllocation[_user][_erc20].allocation -= _decrement;
    }

    function increaseAllocationBatch(
        address[] calldata _users, 
        address _erc20, 
        uint256[] calldata _increments
    ) external 
    {
        require(trustedOperators[msg.sender], "Trusted operators only");
        require(_users.length == _increments.length, "Non equal arrays");
        for (uint256 i = 0; i < _users.length; i ++){
            userAllocation[_users[i]][_erc20].allocation += _increments[i];
        }

    }

    function decreaseAllocationBatch(
        address[] calldata _users, 
        address _erc20, 
        uint256[] calldata _decrements
    ) external 
    {
        require(trustedOperators[msg.sender], "Trusted operators only");
        require(_users.length == _decrements.length, "Non equal arrays");
        for (uint256 i = 0; i < _users.length; i ++){
            require(
                userAllocation[_users[i]][_erc20].allocation - _decrements[i] >= userAllocation[_users[i]][_erc20].used,
                "Cant set less then used"
            );
            userAllocation[_users[i]][_erc20].allocation -= _decrements[i];
        }
    }

    function spendAllocation(address _user, address _erc20, uint256 _amount) public returns (bool){
        require(trustedOperators[msg.sender], "Trusted operators only");
        require(
            userAllocation[_user][_erc20].used + _amount <= userAllocation[_user][_erc20].allocation,
            "Cant spend more then allocated"
        );
        userAllocation[_user][_erc20].used += _amount;
    }

    function availableAllocation(address _user, address _erc20) public view returns (uint256 allocation) {
        allocation = userAllocation[_user][_erc20].allocation - userAllocation[_user][_erc20].used;
    } 
    ////////////////////////////////////////////////
    //   Admin functions                         ///
    ////////////////////////////////////////////////
    function setOperator(address _operator, bool _isValid) external {
        trustedOperators[_operator] = _isValid;
    }

}