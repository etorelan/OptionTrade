//SPDX-License-Identifier: MIT

/// @title OptionTrade
/// @author etorelan
/// @notice An options exchange with a deployer-defined common medium of exchange (XTKN) and option writer set ERC20 token
/// @dev To easily understand what the contract is all about, please refer to the "Call" and "Put" diagrams

pragma solidity 0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract Options {
    ERC20 internal XTKN;

    string private constant ERROR_TOKEN_TRANSFER_FAILED =
        "Token transfer failed";

    struct option {
        uint256 strike; //Price per token to buy/sell
        uint256 premium; //Paid to the writer
        uint256 expiration;
        uint256 amount; // Amount of ERC20 tokens to buy/sell
        bool available; // False when exercised, refunded or cancelled
        bool callPut; //if true -> call, if false -> put
        address tokenAddr; // adress of ERC20 token
        address writer;
        address buyer;
    }

    option[] public options;

    event WriteOption(
        uint256 _strike,
        uint256 _premium,
        uint256 _expiration,
        uint256 _tokenAmount,
        address _tokenAddr,
        uint256 _id
    );

    event CancelOption(address _tokenAddr, uint256 _id);
    event BuyOption(address _tokenAddr, uint256 _id, uint256 _amount);
    event ExerciseOption(address _tokenAddr, uint256 _id);
    event RefundExpiredOption(address _tokenAddr, uint256 _id);
    event UpdateExerciseCost(address _tokenAddr, uint256 _id);

    constructor(address _XTKNAddress) {
        XTKN = ERC20(_XTKNAddress);
    }

    function writeOption(
        uint256 _strike,
        uint256 _premium,
        uint256 _expiration,
        uint256 _tokenAmount,
        bool _callPut,
        address _tokenAddr // Address of the ERC20 token to be used
    ) external {
        require(
            _expiration > block.timestamp,
            "Expiration time cannot be lower than now"
        );

        if (_callPut) {
            require(
                ERC20(_tokenAddr).transferFrom(
                    msg.sender,
                    address(this),
                    _tokenAmount
                ),
                "Incorrect amount of token provided"
            );
        } else {
            require(
                XTKN.transferFrom(
                    msg.sender,
                    address(this),
                    _strike * _tokenAmount
                ),
                "Incorrect amount of token provided"
            );
        }
        options.push(
            option({
                strike: _strike,
                premium: _premium,
                expiration: _expiration,
                amount: _tokenAmount,
                available: true,
                callPut: _callPut,
                tokenAddr: _tokenAddr,
                writer: msg.sender,
                buyer: address(0)
            })
        );
        emit WriteOption(
            _strike,
            _premium,
            _expiration,
            _tokenAmount,
            _tokenAddr,
            options.length - 1 //option id
        );
    }

    /// @notice Transfers writer's deposited tokens back if the option has not been bought
    ///@notice and deletes the option afterwards
    function cancelOption(uint256 _id) external {
        option memory curOption = options[_id];

        require(
            msg.sender == curOption.writer,
            "Option writer is not the msg.sender"
        );
        require(
            curOption.available && curOption.buyer == address(0),
            "Option cannot be cancelled"
        );

        if (curOption.callPut) {
            require(
                ERC20(curOption.tokenAddr).transfer(
                    msg.sender,
                    curOption.amount
                ),
                ERROR_TOKEN_TRANSFER_FAILED
            );
        } else {
            require(
                XTKN.transfer(msg.sender, curOption.strike * curOption.amount),
                ERROR_TOKEN_TRANSFER_FAILED
            );
        }

        emit CancelOption(curOption.tokenAddr, _id);
        delete options[_id];
    }

    ///@notice Depending on the callPut parameter the buyer is
    ///@notice required to either send XTKN or the option specific
    ///@notice ERC20 token, for further explanation refer to the
    ///@notice "Call" and "Put" diagrams
    function buyOption(uint256 _id) external {
        option memory curOption = options[_id];
        require(
            curOption.available && curOption.expiration > block.timestamp,
            "Option cannot be bought"
        );
        require(curOption.buyer == address(0), "Option already bought");

        require(
            XTKN.transferFrom(msg.sender, curOption.writer, curOption.premium),
            "Not enough XTKN for the premium"
        );

        uint256 sent;
        if (curOption.callPut) {
            require(
                XTKN.transferFrom(
                    msg.sender,
                    address(this),
                    curOption.strike * curOption.amount
                ),
                ERROR_TOKEN_TRANSFER_FAILED
            );
            sent = curOption.strike * curOption.amount;
        } else {
            require(
                ERC20(curOption.tokenAddr).transferFrom(
                    msg.sender,
                    address(this),
                    curOption.amount
                ),
                ERROR_TOKEN_TRANSFER_FAILED
            );
            sent = curOption.amount;
        }

        options[_id].buyer = msg.sender;
        emit BuyOption(curOption.tokenAddr, _id, sent);
    }

    ///@notice Transfering tokens deposited to proper addresses
    function exerciseOption(uint256 _id) external {
        option memory curOption = options[_id];

        require(curOption.buyer == msg.sender, "msg.sender != option.buyer ");
        require(
            curOption.available && curOption.expiration > block.timestamp,
            "Option must be available"
        );

        if (curOption.callPut) {
            require(
                XTKN.transfer(
                    curOption.writer,
                    curOption.amount * curOption.strike
                ),
                ERROR_TOKEN_TRANSFER_FAILED
            );
            require(
                ERC20(curOption.tokenAddr).transfer(
                    msg.sender,
                    curOption.amount
                ),
                ERROR_TOKEN_TRANSFER_FAILED
            );
        } else {
            require(
                XTKN.transfer(msg.sender, curOption.amount * curOption.strike),
                ERROR_TOKEN_TRANSFER_FAILED
            );
            require(
                ERC20(curOption.tokenAddr).transfer(
                    curOption.writer,
                    curOption.amount
                ),
                ERROR_TOKEN_TRANSFER_FAILED
            );
        }

        emit ExerciseOption(curOption.tokenAddr, _id);
        delete options[_id];
    }

    ///@notice Transfering deposited tokens to proper addresses
    ///@notice if option has not been exercised
    function refundExpiredOption(uint256 _id) external {
        option memory curOption = options[_id];

        require(
            curOption.available && curOption.expiration <= block.timestamp,
            "Refund not possible"
        );
        require(
            msg.sender == curOption.writer || msg.sender == curOption.buyer,
            "msg.sender != option writer or buyer"
        );

        if (curOption.callPut) {
            require(
                ERC20(curOption.tokenAddr).transfer(
                    curOption.writer,
                    curOption.amount
                ),
                ERROR_TOKEN_TRANSFER_FAILED
            );
            if (curOption.buyer != address(0)) {
                require(
                    XTKN.transfer(
                        curOption.buyer,
                        curOption.amount * curOption.strike
                    ),
                    ERROR_TOKEN_TRANSFER_FAILED
                );
            }
        } else {
            require(
                XTKN.transfer(
                    curOption.writer,
                    curOption.amount * curOption.strike
                ),
                ERROR_TOKEN_TRANSFER_FAILED
            );
            if (curOption.buyer != address(0)) {
                require(
                    ERC20(curOption.tokenAddr).transfer(
                        curOption.buyer,
                        curOption.amount
                    ),
                    ERROR_TOKEN_TRANSFER_FAILED
                );
            }
        }

        emit RefundExpiredOption(curOption.tokenAddr, _id);
        delete options[_id];
    }

    function getOption(uint256 _id) external view returns (option memory) {
        return options[_id];
    }
}
