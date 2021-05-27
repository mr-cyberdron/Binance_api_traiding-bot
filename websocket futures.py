from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
import json
import numpy as np
from collections import deque
import matplotlib.pyplot as plt  # $ pip install matplotlib
import matplotlib.animation as animation

def websocket_plot(binance_websocket_api_manager,npoints =30,curentpair = 'BTCUSD'):
    binance_websocket_api_manager.create_stream(['marketprice', 'kline_1m'], [curentpair])
    x = deque([0], maxlen=npoints)
    y = deque([0], maxlen=npoints)

    fig, (ax) = plt.subplots()

    [line] = ax.plot(x, y)


    def update(dy):
        stream = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
        if stream:
            jsonstream = json.loads(stream)
            data = jsonstream.get('data')
            if data:
                y.append(float(data['k']['c']))
                print(data['k']['c'])
            else:
                y.append(y[-1])
        else:
            y.append(y[-1])

        x.append(x[-1] + 1)  # update data

        line.set_xdata(x)  # update plot data
        line.set_ydata(y)

        ax.relim()  # update axes limits
        ax.autoscale_view(True, True, True)
        return line

    ani = animation.FuncAnimation(fig, update)
    plt.show()


binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures")
binance_websocket_api_manager.create_stream(['marketprice','kline_1m'], ['BNBUSDT'])





websocket_plot(binance_websocket_api_manager,npoints =30,curentpair ='BNBUSDT')