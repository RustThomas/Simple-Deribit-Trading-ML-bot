# Simple-Deribit-Trading-ML-bot
Simple implementation of an automated cryptocurrency derivatives machine learning trading bot on Deribit that uses a Darts' model to predict price direction at next time resolution then open and closes orders.

This bot was profitable during a testing period of a few days in october 2025. The current parameters achieved a mean directional accuracy of 70% on the testing data with the default xgboost ```reg:squarederror``` objective function.  However, manual trading proved to generate larger profits. 

Significant tuning and changes are likely needed, including model, data and covariates. Consider user defined metrics, especially related to supports, resistances, maybe RSI and be aware of Regime Shifts.  
You may try to use [Polars](https://pola.rs/) instead of [Pandas](https://pandas.pydata.org/) as well as other ML libraries. 

The code of this project is absolutely not guaranteed to be without risks nor profitable. Time allowing, I will expand on the documentation and provide other examples. 

If you'd wish to thank me for these measly lines of code, you may do so by using my [referal link for metamask](https://link.metamask.io/rewards?referral=CMBA5F) or at ```0x15156ba57acce78843367f0a5816b52e06870ef5```.

# How to use

- Clone this repository with the command ```gh repo clone RustThomas/Simple-Deribit-Trading-ML-bot```.

- This project requires [Darts](https://unit8co.github.io/darts/), Pandas. To install dependencies, you may use ```pip install -r requirements.txt```. Feel free to try with other libraries and to add hyperoptimization. DLinear is a good candidate, and even simple linear regression had decent results. 

- You will need to [generate an API key](https://support.deribit.com/hc/en-us/articles/26268257333661-Creating-new-API-key-on-Deribit) on Deribit and then replace ```client_id``` and ```client_secret``` with yours. You can also change the instrument by using a different ```instrument_name``` string, such as the various Futures like ```BTC-26DEC25``` that have high maker rebates or other currencies such as ```ETH_PERPETUAL```.  
**Do not share them.**

You may optionally switch to [Deribit testing environment](https://test.deribit.com/) to experiment before going live. To do so, generate an API key on the test Network (make sure to use a different password than on the live network). 

- Then, simply run ```main.py```. 


