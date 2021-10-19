// SPDX-License-Identifier: MIT
// ENVELOP (NIFTSY) protocol for NFT. Wrapper & Farming contract
pragma solidity ^0.8.6;

import "./WrapperWithERC20Collateral.sol";
import "../interfaces/IERC721Mintable.sol";

/**
 * @title ERC-721 Non-Fungible Token Wrapper 
 * @dev For wrpap and Rewarf farming. ERC20 reward must be on this contract balance
 * !!!!!!!!! Important  !!!!!!!!!!!!!!!!!!!!!!!!!!!
 * Please Don't add farming token in erc20 collateral whitelist
 */
contract WrapperFarming is WrapperWithERC20Collateral {
    using SafeERC20 for IERC20;
    using ERC165Checker for address;
    
    struct RewardSettings {
        uint256 period;
        uint256 rewardPercent; // multiplyed by 100, 1%-100, 12$-1200,99%-
    }

    struct NFTReward {
        uint256 stakedDate;
        uint256 harvestedAmount;
    }

    uint8 public MAX_SETTINGS_SLOTS = 10;
    
    // from farming token address  to settings(reward points) 
    mapping(address => RewardSettings[]) public rewardSettings;
    mapping(uint256 => NFTReward) public rewards;

    constructor (address _erc20, address _defaultRewardToken, RewardSettings[] memory _settings ) 
        WrapperWithERC20Collateral(_erc20) 
    {
        require (_settings.length <= MAX_SETTINGS_SLOTS, "Too many seeting items");
        RewardSettings[] storage set = rewardSettings[_defaultRewardToken];
        for (uint8 i = 0; i < _settings.length; i ++) {
            set.push(RewardSettings({
                period: _settings[i].period,
                rewardPercent: _settings[i].rewardPercent
            }));
        }

    }
    


    /// !!!!For gas safe this low levelfunction has NO any check before wrap
    /// So you have NO warranty to do Unwrap well
    function WrapForFarming(
        address  _receiver,
        ERC20Collateral memory _erc20Collateral,
        uint256 _unwrapAfter
    ) public payable 
    {
        require(_receiver != address(0), "No zero address");
        // 1.topup wrapper contract with erc20 that would be added in collateral
        IERC20(_erc20Collateral.erc20Token).safeTransferFrom(
            msg.sender, 
            address(this), 
            _erc20Collateral.amount
        );


        // 2.Mint wrapped NFT for receiver and populate storage
        lastWrappedNFTId += 1;
        _mint(_receiver, lastWrappedNFTId);
        wrappedTokens[lastWrappedNFTId] = NFT(
            address(0), // _original721, 
            0, // _tokenIds[i], 
            msg.value,        // native blockchain asset
            0,                // accumalated fee token
            _unwrapAfter,     // timelock
            0,                //_transferFee,
            address(0),       // _royaltyBeneficiary,
            0,                //_royaltyPercent,
            0,                //_unwraptFeeThreshold,
            address(0),       //_transferFeeToken,
            AssetType.UNDEFINED,
            0
        );

        // 3.Add erc20 collateral
        ERC20Collateral[] storage coll = erc20Collateral[lastWrappedNFTId];
        coll.push(ERC20Collateral({
            erc20Token: _erc20Collateral.erc20Token, 
            amount: _erc20Collateral.amount
        }));
        emit Wrapped(address(0), 0, lastWrappedNFTId);

        // 4. Register farming
        NFTReward storage r = rewards[lastWrappedNFTId];
        r.stakedDate = block.timestamp;
    }

    function harvest(uint256 _wrappedTokenId, address _erc20) public {
        // We dont need chec ownership because reward will  be added to wNFT
        // And unWrap this nft can only owner
        uint256 rewardAmount = getAvailableRewardAmount(_wrappedTokenId, _erc20);
        if (rewardAmount > 0) {
            NFTReward storage thisNFTReward = rewards[_wrappedTokenId]; 
            ERC20Collateral[] storage e = erc20Collateral[_wrappedTokenId];
            for (uint256 i = 0; i < e.length; i ++) {
                if (e[i].erc20Token == _erc20) {
                    e[i].amount += rewardAmount;
                    thisNFTReward.harvestedAmount += rewardAmount;  
                    break;
                }
            }

        }
    }

    function getAvailableRewardAmount(uint256 _tokenId, address _erc20) public view returns (uint256 rewardAccrued) {
        uint256 timeInStake = block.timestamp - rewards[_tokenId].stakedDate;
        if (rewardSettings[_erc20][0].period > timeInStake) {
            //case when time too short
            rewardAccrued = 0;
            return rewardAccrued;
        } 
        for (uint8 i = 0; i < rewardSettings[_erc20].length; i ++) {
            if (rewardSettings[_erc20][i].period <= timeInStake 
                &&  rewardSettings[_erc20][i + 1].period < timeInStake) {
                // Case when  user have reward apprpriate current stake time
                rewardAccrued = rewardSettings[_erc20][i].rewardPercent
                * getERC20CollateralBalance(_tokenId, _erc20) 
                / 10000;
                break;
            } else {
                if (
                    //Case when next slot is last
                    (i + 2 == rewardSettings[_erc20].length) 
                    //Case when nex slot is last
                    || (rewardSettings[_erc20][i + 2].period == 0)
                    ) {
                    // Case when user have MAX  percent (last possible setting slot)
                    rewardAccrued = rewardSettings[_erc20][i + 1].rewardPercent
                    * getERC20CollateralBalance(_tokenId, _erc20) 
                    / 10000;
                }
            }
        }
        rewardAccrued -= rewards[_tokenId].harvestedAmount;

        return rewardAccrued; 
    }

    ////////////////////////////////////////////////////////////////
    //////////     Admins                                     //////
    ////////////////////////////////////////////////////////////////

    function setRewardSettings(
        address _erc20, 
        uint256 _settingsSlotId, 
        uint256 _period, 
        uint256 _percent
    ) external onlyOwner {
        require(rewardSettings[_erc20].length > 0, "There is no settings for this token");
        RewardSettings[] storage set = rewardSettings[_erc20];
        set[_settingsSlotId].period = _period;
    }

    function addRewardSettingsSlot(
        address _erc20, 
        uint256 _settingsSlotId, 
        uint256 _period, 
        uint256 _percent
    ) external onlyOwner {
        require(rewardSettings[_erc20].length < MAX_SETTINGS_SLOTS - 1, "Too much settings slot");
        RewardSettings[] storage set = rewardSettings[_erc20];
        set.push(RewardSettings({
            period: _period,
            rewardPercent: _percent
        }));
    }
    ////////////////////////////////////////////////////////////////

    function _baseURI() internal view  override(ERC721) returns (string memory) {
        return 'https://envelop.is/distribmetadata/';
    }


    /**
     * @dev Function returns tokenURI of **underline original token** 
     *
     * @param _tokenId id of protocol token (new wrapped token)
     */
    function tokenURI(uint256 _tokenId) public view override returns (string memory) {
        NFT storage nft = wrappedTokens[_tokenId];
        if (nft.tokenContract != address(0)) {
            return IERC721Metadata(nft.tokenContract).tokenURI(nft.tokenId);
        } else {
            return ERC721.tokenURI(_tokenId);
        }    
    }
}

