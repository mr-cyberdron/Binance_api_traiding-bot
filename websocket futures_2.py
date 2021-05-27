from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
import json
import numpy as np
from collections import deque
import matplotlib.pyplot as plt  # $ pip install matplotlib
import matplotlib.animation as animation
import talib

def websocket_plot(binance_websocket_api_manager,npoints =30,curentpair = 'BTCUSD',highlimit = 65,lowlimit = 35):
    stream = binance_websocket_api_manager.create_stream(['marketprice', 'kline_1m'], [curentpair])

    zero_point = 0

    #find fist point
    i = True
    while i == True:
        stream = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
        if stream:
            jsonstream = json.loads(stream)
            data = jsonstream.get('data')
            if data:
                zero_point = (float(data['k']['c']))
                i = False

    x = deque([0], maxlen=npoints)
    y = deque([zero_point], maxlen=npoints)
    y2 = deque([50], maxlen=npoints)
    fig, (ax1, ax2) = plt.subplots(2, 1)

    line1, = ax1.plot([], [],lw=0.5)
    line2, = ax2.plot([], [], lw=0.5, color='royalblue')
    line3, = ax2.plot([], [], lw=1, color='lime')
    line4, = ax2.plot([], [], lw=1, color='r')
    line = [line1, line2,line3,line4]



    def update(dy):
        stream = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
        if stream:
            jsonstream = json.loads(stream)
            data = jsonstream.get('data')
            if data:
                y.append(float(data['k']['c']))
                #print(data['k']['c'])
            else:
                y.append(y[-1])
        else:
            y.append(y[-1])
        #-----------------------The place to insert indicator counter-----------------------#
        timeperiod = 3158
        calculated_indicator = talib.RSI(np.double(np.array(y)), timeperiod=timeperiod)
        print(calculated_indicator)
        if calculated_indicator[-1]!=calculated_indicator[-1]:
            y2.append(50)
            print(y2)
        else:
            y2.append(calculated_indicator[-1])

        #------------------------------------------------------------------------------------


        x.append(x[-1]+1)
        line[0].set_data(x, y)
        line[1].set_data(x, y2)
        line[2].set_data(x, highlimit)
        line[3].set_data(x, lowlimit)
        ax1.add_line(line1)
        ax1.relim()  # update axes limits
        ax1.autoscale_view(True, True, True)
        ax2.relim()  # update axes limits
        ax2.autoscale_view(True, True, True)
        return line

    ani = animation.FuncAnimation(fig, update)
    plt.show()


binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures")
binance_websocket_api_manager.create_stream(['marketprice','kline_1m'], ['BNBUSDT'])





websocket_plot(binance_websocket_api_manager,npoints =5000,curentpair ='BNBUSDT')