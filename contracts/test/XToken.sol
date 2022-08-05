// SPDX-License-Identifier: MIT
pragma solidity 0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract XToken is ERC20 {
    constructor() ERC20("XToken", "XTKN") {
        _mint(msg.sender, 1000000000000000000000000000000000);
    }
}
