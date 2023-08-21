"""
a script to find shitcoins to buy:
-growing price,
-huge volume,
-not pumped yet
"""

import ccxt
import time
import pandas as pd
from datetime import datetime
import time
from multiprocessing import Pool

class DataReciever:
    def __init__(self, exchange):
        self.exchange = exchange
        if self.exchange == 'bittrex':
            self.api = ccxt.bittrex({
                'apiKey': '',
                'secret': '',
            })
        if self.exchange == 'kucoin':
            self.api = ccxt.kucoin({
                'apiKey': '',
                'secret': '',
            })
        if self.exchange == 'binance':
            self.api = ccxt.binance({
                'apiKey': '',
                'secret': '',
            })


    #choose all BTC markets
    def get_market_list(self):
        data = self.api.fetch_markets()
        counter = 0
        result = []
        for i in data:
            if i['active'] == True and i['symbol'].endswith('BTC'):
                result.append(i['symbol']) # or i['id']
                counter += 1
        print(self.exchange, 'total markets: ', counter)
        return result

    def calc_start_time(self):
        now = time.time() * 1000
        result = now - 15552000000 # 180 days
        return result

    def get_ohlcv(self, market):
        start_time = self.calc_start_time()
        time.sleep(3)
        try:
            if self.exchange in ['bittrex', 'kucoin']:
                ohlcv = self.api.fetch_ohlcv(market, timeframe='1d', since=start_time, limit = 180)
            if self.exchange == 'binance':
                ohlcv = self.api.fetch_ohlcv(market, timeframe='1d', limit = 180)
            return [market, ohlcv]
        except Exception as e:
            print(e)
            return None

    def create_df(self, ohlcv):
        df = pd.DataFrame(data = ohlcv[1], columns = ['timestamp',
                                                   'open',
                                                   'high',
                                                   'low',
                                                   'close',
                                                   'volume'])
        return [ohlcv[0], df]

    def convert_time(self, df):
        for index, row in df[1].iterrows():
            df[1].at[index,'timestamp'] = datetime.fromtimestamp(row['timestamp'] / 1000)
        return [df[0], df[1]]


    def run(self):
        markets = self.get_market_list()
        #markets = markets[:10]
        #print(markets)
        ohlcvs = list(map(self.get_ohlcv, markets))
        #filters None values from list
        ohlcvs = [x for x in ohlcvs if x is not None]
        #print(ohlcvs)
        #print(list(ohlcvs))
        dfs = list(map(self.create_df, ohlcvs))
        dfs_converted_time = list(map(self.convert_time, dfs))
        #print(dfs_converted_time)
        return dfs_converted_time

class DataAnalyzer:
    def __init__(self, exchange):
        self.exchange = exchange

    #find growing price
    #5 of 7 last days close price > open price
    def find_growing_prices(self, data):
        df = data[1][-7:]
        #print(df)
        price_growth = 0
        for index, row in df.iterrows():
            if df.at[index, 'close'] - df.at[index, 'open'] > 0:
                price_growth += 1

        if price_growth <= 5:
            return data[0]

    #find huge volume, based on average volume per last 180 days
    def find_huge_volume(self, data):
        average_volume = data[1]["volume"].mean()
        #print(average_volume)
        df = data[1][-7:]
        volume_total_last_7_days = 0
        for index, row in df.iterrows():
            volume_total_last_7_days += df.at[index, 'volume']
        volume_increased = volume_total_last_7_days / 7 / average_volume
        #print(volume_increased)
        if volume_increased > 3:
            return data[0]

    #find not pumped shitcoins, price < 200% of 180-days low
    def find_not_pumped_coins(self, data):
        low = 9999999999999999999
        df = data[1]
        for index, row in df.iterrows():
            if df.at[index, 'low'] < low:
                low = df.at[index, 'low']
        #print(low)
        #print(df['close'].iloc[-1])
        if df['close'].iloc[-1] < 3 * low:
            return data[0]



    def run(self, dfs):
        markets_list_filtered_price_growth = list(map(self.find_growing_prices, dfs))
        #print(markets_list_filtered_price_growth)
        markets_list_filtered_huge_volume = list(map(self.find_huge_volume, dfs))
        markets_list_filtered_pump = list(map(self.find_not_pumped_coins, dfs))

        #filter None
        markets_list_filtered_price_growth = [x for x in markets_list_filtered_price_growth if x is not None]
        markets_list_filtered_huge_volume = [x for x in markets_list_filtered_huge_volume if x is not None]
        markets_list_filtered_pump = [x for x in markets_list_filtered_pump if x is not None]

        #find equal tickers in list1 and list2
        common_elements = list(set(markets_list_filtered_price_growth).intersection(markets_list_filtered_huge_volume))
        #find equal tickers in new list and list3
        result = list(set(common_elements).intersection(markets_list_filtered_pump))
        print('\n\n\n')
        print(self.exchange)
        print('price is growing: ', markets_list_filtered_price_growth)
        print('huge volume: ', markets_list_filtered_huge_volume)
        print('price is not pumped yet: ', markets_list_filtered_pump)
        print(self.exchange, 'result: ', result)
        return result

def run_all(exchange):
    a = DataReciever(exchange)
    dfs = a.run()
    b = DataAnalyzer(exchange)
    results = b.run(dfs)
    return results

#exchanges = ['bittrex', 'kucoin']
exchanges = ['binance']

if __name__ == '__main__':
    with Pool(2) as p:
        answer = sum(p.map(run_all, exchanges))
        print('all markets together: ', answer)
