import ccxt
import os
import re
import numpy as np
import time
import pandas as pd
#библиотека расчета индикаторов
from stockstats import StockDataFrame as Sdf
import plotly.graph_objects as go
from datetime import datetime
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly
import talib
import numpy

def candle_plot2(df,indicator_name,highgap,lowgap,title):

  fig = make_subplots(rows=2, cols=1)
  upperband, middleband, lowerband = BBANDS_index_counter(df)
  df['middleband'] = middleband
  df['upperband'] = upperband
  df['lowerband'] = lowerband
  fig.add_trace((go.Candlestick(x=df['timestamp'],
                                       open=df['open'], high=df['high'],
                                       low=df['low'], close=df['close'],)
                                       ),row = 1, col = 1)

  fig.add_trace(((go.Scatter(          x=df['timestamp'],
                                       y=df['middleband']))
                                       ), row=1, col=1)
  fig.add_trace(go.Scatter(            x=df['timestamp'],
                                       y=df['upperband'],
                                       mode='lines',
                                       name='lines'), row=1, col=1)
  fig.add_trace(go.Scatter(            x=df['timestamp'],
                                       y=df['lowerband'],
                                       mode='lines',
                                       name='lines'), row=1, col=1)

  fig.add_trace(((go.Scatter(          x=df['timestamp'],
                                       y=df[indicator_name]))
                                       ), row=2, col=1)
  fig.add_trace(go.Scatter(            x=df['timestamp'],
                                       y=df[highgap],
                                       mode='lines',
                                       name='lines'),row=2, col=1)
  fig.add_trace(go.Scatter(            x=df['timestamp'],
                                       y=df[lowgap],
                                       mode='lines',
                                       name='lines'), row=2, col=1)
  fig.update_layout(title=title,xaxis_rangeslider_visible=False)
  plotly.offline.plot(fig)


def candle_plot(df):
    fig = make_subplots(rows=1, cols=1)

    fig.add_trace((go.Candlestick(x=df['timestamp'],
                                  open=df['open'], high=df['high'],
                                  low=df['low'], close=df['close'])
                   ), row=1, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.show()

def RSI_index_counter(data,timeperiod = 10,plotflag = 0,highgap = 85,lowgap = 15,delay =0,title = ''):
  # Calculate RSI

  prep_data = data['close']
  prep_data = talib.RSI(prep_data,timeperiod=timeperiod)

  if delay !=0:
      for i in range(timeperiod+ delay):
          prep_data[i] = 50
  if plotflag !=0:
      data['RSI'] = prep_data
      data['highgap'] = highgap
      data['lowgap'] = lowgap

      candle_plot2(data, 'RSI', 'highgap', 'lowgap',title)


  return (prep_data)

def BBANDS_index_counter(data, timeperiod=20,nbdevup=2, nbdevdn=2, matype=0, plotflag=0, highgap=70, lowgap=30, title=''):
  # Calculate RSI
  prep_data = data['close']
  upperband, middleband, lowerband = talib.BBANDS(prep_data, timeperiod=timeperiod,nbdevup=nbdevup, nbdevdn=nbdevdn, matype=matype)

  if plotflag != 0:
      RSI_index_counter(data, timeperiod=10, plotflag=1, highgap=highgap, lowgap=lowgap)
  return (upperband, middleband, lowerband)

  # получаем данные о ценах

def get_historical_data(exchange,coin_pair, timeframe, limit=200):
  # данные о свечах
  data = exchange.fetch_ohlcv(coin_pair, timeframe, limit=limit)
  # Делаем нормальный датафрейм
  data = [[exchange.iso8601(candle[0])] + candle[1:] for candle in data]
  header = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
  df = pd.DataFrame(data, columns=header)
  return df

