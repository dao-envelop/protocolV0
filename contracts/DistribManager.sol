// SPDX-License-Identifier: MIT
// ENVELOP (NIFTSY) protocol for NFT. Distributor Role Manager
pragma solidity 0.8.10;


import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "../interfaces/IWrapperDistributor.sol";

/**
 * @title Distributor Manager contract 
 * @dev For sell Distributore Role membership
 */
contract DistribManager is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;
    
    struct ticketParams {
        address paymentToken;
        uint256 paymentAmount;
        uint256 timelockPeriod;    // in seconds e.g. 3600*24*30*12 = 31104000 = 1 year
        uint256 ticketValidPeriod; // in seconds e.g. 3600*24*30    =  2592000 = 1 month
    }

    ticketParams[] public ticketsOnSale;

    // mapping from address to block timestamp. After this date 
    // anybody can remove address from distributors Role
    mapping(address => uint256) public validDistributors;
    IWrapperDistributor public wrapper;

    event NewTicketSold(
        address indexed buyer, 
        uint256 indexed tarif, 
        address indexed distribContract, 
        uint256 tokenId
    );

    constructor (address distribContract) 
    {
        wrapper = IWrapperDistributor(distribContract);
        validDistributors[address(this)] = type(uint256).max;
    }

    function buyTicket(uint256 _tarifIndex) public nonReentrant {
        require(ticketsOnSale[_tarifIndex].paymentToken != address(0), 'Ticket not exist');
        
        // Lets receive payment tokens FROM sender
        IERC20(ticketsOnSale[_tarifIndex].paymentToken).safeTransferFrom(
            msg.sender, 
            address(this), 
            ticketsOnSale[_tarifIndex].paymentAmount
        );

        // Give Approve to Distributor
        IERC20(ticketsOnSale[_tarifIndex].paymentToken).safeApprove(
            address(wrapper), 
            ticketsOnSale[_tarifIndex].paymentAmount
        );

        // wrap for msg.sender
        address[] memory receiverArray = new address[](1);
        receiverArray[0] = msg.sender;

        IWrapperCollateral.ERC20Collateral[] memory collateralArray = new IWrapperCollateral.ERC20Collateral[](1);
        collateralArray[0] =  IWrapperCollateral.ERC20Collateral(
            ticketsOnSale[_tarifIndex].paymentToken, 
            ticketsOnSale[_tarifIndex].paymentAmount
        );
        wrapper.WrapAndDistribEmpty(
            receiverArray,
            collateralArray,
            ticketsOnSale[_tarifIndex].timelockPeriod + block.timestamp
        );

        // Save/update ticket record
        validDistributors[msg.sender] += ticketsOnSale[_tarifIndex].ticketValidPeriod;

        // Add to distributor role
        wrapper.setDistributorState(msg.sender, true);
        

        emit NewTicketSold(msg.sender, _tarifIndex, address(wrapper), wrapper.lastWrappedNFTId());

    }

    function removeFromDistributors(address _distributor) public {
        require(validDistributors[_distributor] < block.timestamp, 'Ticket is still valid');
        wrapper.setDistributorState(_distributor, false);

    }
   


    ////////////////////////////////////////////////////////////////
    //////////     Admins                                     //////
    ////////////////////////////////////////////////////////////////

    function addTarif(ticketParams calldata _newTarif) external onlyOwner {
        require (_newTarif.paymentToken != address(0), 'No zero token');
        ticketsOnSale.push(_newTarif);
    }

    function editTarif(
        uint256 _index, 
        address _paymentToken, 
        uint256 _paymentAmount,
        uint256 _timelockPeriod,
        uint256 _ticketValidPeriod
    ) external onlyOwner {
        ticketsOnSale[_index].paymentToken      = _paymentToken;
        ticketsOnSale[_index].paymentAmount     = _paymentAmount;
        ticketsOnSale[_index].timelockPeriod    = _timelockPeriod;
        ticketsOnSale[_index].ticketValidPeriod = _ticketValidPeriod;
    }

    function revokeOwnership(address _contract) external onlyOwner {
        wrapper.transferOwnership(owner());
    }

    ////////////////////////////////////////////////////////////////

   
}

