# OptionTrade
An options exchange template built on the Ethereum blockchain with a deployer-defined common medium of exchange `XToken.sol` and a user defined erc20 token used for trade. The functionality is quickly understood refering to the `Call` and `Put` diagrams. 


## Features

- Users can use and/or customize `XToken.sol`, `YToken.sol` to change and extend the base token functionality
- Writing, cancelling, buying, exercising and refunding options built-in

## Technologies Used

- Brownie: Python backend blockchain framework
- Ganache: Providing local development blockchains

## Installation

1. Clone the repository:

```
git clone https://github.com/etorelan/OptionTrade.git
```

2. Install dependencies:

```
cd OptionTrade/
pip install -r requirements.txt
```

3. Set up environment variables:

   - Create a `.env` file in the root directory and set the `PRIVATE_KEY` variable to your wallet's private key:


## License

This project is licensed under the MIT License

## Acknowledgments

- Special thanks to the developers of Solidity, Brownie, and Ganache for their tools and documentation.
- Thanks to the open-source community for providing helpful resources and tutorials.