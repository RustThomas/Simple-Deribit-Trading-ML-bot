# Simple-Deribit-Trading-ML-bot
Simple implementation of an automated trading bot on Deribit that uses a Darts model to predict price direction at next time resolution then open and closes orders.

This bot was profitable during a testing period of a few days in october 2025. The current parameters achieved a mean directional accuracy of 70% on the testing data with the default reg:squarederror objective function.  However, manual trading proved to generate larger profits. 
Significant tuning and changes are likely needed, including model, data and covariates. 

The code of this project is absolutely not guaranteed to be without risks nor profitable. 

If you'd wish to tip me for these measly lines of code, you may do so at 0x15156ba57acce78843367f0a5816b52e06870ef5.

# Using

This project requires Darts, Pandas. 

To use, you need to generate an API key on Deribit and then replace client_id and client_secret with yours. You can also change the instrument by using a different instrument_name.  

**Do not share them.**

You may switch to Deribit testing environment to experiment before going live.

Them, simply run main. 


