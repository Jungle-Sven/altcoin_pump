# altcoin_pump
A script to monitor price pumps of altcoins @Binance

Gets data from Binance exchange and then filters tokens that:
- are not yet pumped (the price is < 200% of 180-day low)
- price went up at least 5 of 7 last days
- trading volume for the last 7 days was at least x3 higher than average

# run

python bot.py 

and wait 2-3 minutes

# exchanges

- Binance
- Kucoin
- Bittrex
# altcoin_pump
