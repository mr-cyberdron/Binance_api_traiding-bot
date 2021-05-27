import ccxt
import os
import re
import numpy as np
import time
import pandas as pd
#библиотека расчета индикаторов
import numpy
import financal_lib as fl
import copy
import sys
from datetime import datetime
import configparser  # импортируем библиотеку
import requests
import json
def send(text):
    b = a+str(text)
    requests.post(b)

def log (data_mas):
    f = open('log.txt', 'a')
    f.write(str(data_mas)+"\n")
    f.close()
def enough_volatility_flag(upperband,lowerband,scale_coef = 1,num_counts = 199):
    # определяем среднюю ширину скользящей средней
    # если ширина последнего отсчета выше средней на какой то коефициент
    #то тру
    a = upperband-lowerband
    mean_val = a.mean(axis=0)
    total_val = upperband[num_counts]-lowerband[num_counts]
    div = total_val/mean_val
    if div > scale_coef:
        return (True)
    else:
        return (False)



#----------------------Конфигурируем соединение--------------------------
# configure exchange
with open('config.ini') as f:
    config = json.load(f)
apiKey = config["apiKey"]
secret = config["secret"]
exchange = getattr(ccxt, 'binance')({
  'apiKey': apiKey,
  'secret': secret,
  'timeout': 10000,
  'enableRateLimit': True,
  'rateLimit':100 ,
  'options': {
        'defaultType': 'future',  # ←-------------- quotes and 'future'
    },
})

# load markets and all coin_pairs
exchange.load_markets()
# загружаем торговые пары
coin_pairs = exchange.symbols

#фильтруем по USDT
# list of coin pairs which are active and use BTC as base coin
valid_coin_pairs = []
# load only coin_pairs which match regex and are active
regex = '^.*/USDT'
#получаем валидные валютные пары
for coin_pair in coin_pairs:
  if re.match(regex, coin_pair) and exchange.markets[coin_pair]['active']:
    valid_coin_pairs.append(coin_pair)


print(valid_coin_pairs)
#-------------------------------------------------------------------------------------

starttt = 0
if __name__ == "__main__":
  ...
  while True:
    try:
      with open('config.ini') as f:
          config = json.load(f)
      timestep = config["timestep"]
      shortflag = config["shortflag"]
      longflag = config["longflag"]
      plotflag = config["plotflag"]
      trade_coef = config["trade_coef"]
      max_start_coef = config["max_start_coef"]
      scale_coef = config["scale_coef"]
      leverage = config["leverage"]
      change_aval = config["change_aval"]
      uperbend_boof_coef = config["uperbend_boof_coef"]
      Percent_stop_los_beg = config["Percent_stop_los_beg"]
      stoplos_after_coef =config["stoplos_after_coef"]
      start_high_pos_coef =config["start_high_pos_coef"]
      stop_bottom_coef = config["stop_bottom_coef"]
      new_middle_coef = config["new_middle_coef"]
      v1 = ["v1"]
      v2 = ["v2"]
      v3 = ["v3"]
      v4 = ["v4"]
      v5 = ["v5"]
      v6 = ["v6"]
      highgap = config["highgap"]
      lowgap = config["lowgap"]
      timeperiod = config["timeperiod"]
      third_num = config["third_num"]
      top_num = config["top_num"]
      banlist = config["banlist"]



      if starttt ==1:
          try:
              with open('temp_log.ini', ) as f:
                  config = json.load(f)
              order_ID = config["orderid"]
              symboll = config["symbol"]
              bs = config["deal"]
              buying_val_coin = config["buying_val"]
              if bs == 'buy':
                  exchange.create_order(symboll, 'market', 'sell', buying_val_coin, None)
              if bs == 'sell':
                  exchange.create_order(symboll, 'market', 'buy', buying_val_coin, None)
              data = {"none": 0}
              with open('temp_log.ini', 'w') as f:
                  json.dump(data, f)
          except:
              pass
      else:
          starttt = 1
      # исключаем бан лист
      valid_coin_pairs = list(set(valid_coin_pairs)-set(banlist))
      balance = exchange.fetchBalance()
      balance = float(balance['info']['availableBalance'])
      print('Total balance: ',str(balance))
      orders_closed = 0
      orders_opened = 0
      sucsess_orders = 0
      faild_orders = 0
      first_balance = exchange.fetchBalance()
      first_balance= float(first_balance['info']['availableBalance'])
      counter = 0

      if change_aval !=0:
          print('Changing leverages')
          for coin_pair in valid_coin_pairs:
              market = exchange.markets[coin_pair]
              exchange.fapiPrivate_post_leverage({
                  "symbol": market['id'],  # convert a unified CCXT symbol to an exchange-specific market id
                   "leverage": leverage,
              })
              counter = counter+1
              sys.stdout.write("\r{}".format([str(counter),'/',str(np.shape(valid_coin_pairs)[0])]))
              sys.stdout.flush()
      print('start')
      send('lets go')

      tmp_processed_coinlist = ""
      while True:

        for coin_pair in valid_coin_pairs: #

            #time.sleep(exchange.rateLimit / 1000)
            stock_data = fl.get_historical_data(exchange,coin_pair, timestep,limit=200)

            RSI = fl.RSI_index_counter(stock_data,plotflag=0,timeperiod = timeperiod,title = coin_pair,highgap = highgap,lowgap = lowgap)
            upperband, middleband, lowerband = fl.BBANDS_index_counter(stock_data)
            volatilty_enough = enough_volatility_flag(upperband,lowerband,scale_coef = scale_coef)
            print('Balance: ' , str(round(balance,2)), 'Orders opened: ',str(orders_opened),'Orders closed: ',str(orders_closed),
                  'Sucsess: ', str(sucsess_orders),'Fail: ',str(faild_orders)
                  ,'total profit:',str(round((balance-first_balance),2)),coin_pair,[RSI[197],RSI[198],RSI[199]],end='\r\n')
            
                print('\a')
                print('opa long')
                send(['Positition started!',coin_pair,'Long'])
                if plotflag!= 0:
                    fl.RSI_index_counter(stock_data, plotflag=1, timeperiod=timeperiod, title=coin_pair, highgap=highgap,
                                           lowgap=lowgap)
                buying_val = ((balance*trade_coef*leverage)/((stock_data['close'])[199]))
                #покупка
                startong_curent = ((stock_data['close'])[199])
                deall = 'buy'
                try:
                    order = exchange.create_order(coin_pair, 'market', deall,buying_val,
                                          None)
                    order_ID = order['info']['orderId']
                    data = {"symbol": coin_pair, "orderid": order_ID, "deal": deall, "buying_val": buying_val}
                    with open('temp_log.ini', 'w') as f:
                        json.dump(data, f)
                    tmp_processed_coinlist = coin_pair
                except:
                    print('filed buying')
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    logg = [current_time, 'failed buying','short',coin_pair,((sys.exc_info()[0]))]
                    log(logg)
                    send(logg)
                    tmp_processed_coinlist = coin_pair
                    break
                order_ID = order['info']['orderId']
                #проверка
                time.sleep(0.05)
                order_data = exchange.fetchOrder(order_ID, coin_pair)
                #если ордер на покупку выполнен
                if (order_data['info']['status']) == 'FILLED':
                    print('processing')
                    #начинаем следить
                    #пресваиваем первоначальный стоп лосс
                    total_stop_loss = copy.deepcopy(Percent_stop_los_beg)
                    #флаг обнаружения скользящей средней
                    middleband_detection_flag = 0
                    #флаг обнаружения второго стоп лоса
                    second_stop_loss_coef = 0
                    #флаг обнаружения безубытка
                    first_stop_loss_coef = 0
                    middle_stop_loss_coef = 0
                    zeroseven_stoploss = 0
                    zeroseven_stoploss_two = 0
                    prel_position_coef = 0
                    while True:
                        stock_data = fl.get_historical_data(exchange, coin_pair, timestep, limit=200)
                        total_cur = (stock_data['close'])[199]
                        pnl = round((total_cur-startong_curent)*buying_val,3)
                        roe = round(((((total_cur-startong_curent)/startong_curent)*100)*leverage),3)
                        sys.stdout.write("\r{}".format(['PNL:',pnl,'ROE%',roe,'stop ROE:',total_stop_loss]))
                        sys.stdout.flush()
                        RSI = fl.RSI_index_counter(stock_data, highgap=highgap,lowgap=lowgap)
                        upperband, middleband, lowerband = fl.BBANDS_index_counter(stock_data)
                        # Если pnl больше стоп лоса
                        if roe > Percent_stop_los_beg:
                            # если пересекло первую зону формируем безубыток
                            if total_cur > (startong_curent+((middleband[199]-startong_curent)*start_high_pos_coef)) \
                                    and first_stop_loss_coef == 0 and v1:
                                out_cur = startong_curent + ((middleband[199]-startong_curent)*stop_bottom_coef)
                                total_stop_loss = round(
                                    ((((out_cur - startong_curent) / startong_curent) * 100) * leverage), 3)
                                first_stop_loss_coef = 1
                                print('fitst Stop_loss changed:', str(total_stop_loss))
                            #вторая зона
                            if total_cur> (startong_curent+(middleband[199]-startong_curent)*new_middle_coef) \
                                    and middle_stop_loss_coef == 0 and v2:
                                out_cur = startong_curent + ((middleband[199] - startong_curent) * start_high_pos_coef)
                                total_stop_loss = round(
                                    ((((out_cur - startong_curent) / startong_curent) * 100) * leverage), 3)
                                middle_stop_loss_coef = 1
                                print('middle Stop_loss changed:', str(total_stop_loss))
                            #третяя
                            if total_cur> (startong_curent+(middleband[199]-startong_curent)*stoplos_after_coef) \
                                    and zeroseven_stoploss == 0 and v3:
                                out_cur = startong_curent + ((middleband[199] - startong_curent) * new_middle_coef)
                                total_stop_loss = round(
                                    ((((out_cur - startong_curent) / startong_curent) * 100) * leverage), 3)
                                zeroseven_stoploss = 1
                                print('Stop_loss changed:', str(total_stop_loss))
                            #если пересекло скользящую среднюю изменяем стоп лос
                            if total_cur > middleband[199] and middleband_detection_flag == 0:
                                #пересчитаем цену выхода при стоп лосе
                                out_cur = startong_curent+((middleband[199]-startong_curent)*stoplos_after_coef)
                                #пересчитаем в roe
                                total_stop_loss = round(((((out_cur-startong_curent)/startong_curent)*100)*leverage),3)
                                middleband_detection_flag = 1
                                print('roe Stop_loss changed:',str(total_stop_loss))

                            #если еще ниже устанавливаем новій стоп лосс
                            if total_cur > (((upperband[199]-middleband[199])*start_high_pos_coef)+middleband[199]) \
                                    and second_stop_loss_coef == 0 and v4:
                                out_cur = middleband[199]
                                total_stop_loss = round(
                                    ((((out_cur - startong_curent) / startong_curent) * 100) * leverage), 3)
                                second_stop_loss_coef = 1
                                print('Second stoploss changed', str(total_stop_loss))

                            # если еще ниже устанавливаем новій стоп лосс
                            if total_cur > (((upperband[199] - middleband[199]) * new_middle_coef) + middleband[
                                199]) and zeroseven_stoploss_two == 0 and v5:
                                out_cur = (((upperband[199] - middleband[199]) * start_high_pos_coef) + middleband[
                                199])
                                total_stop_loss = round(
                                    ((((out_cur - startong_curent) / startong_curent) * 100) * leverage), 3)
                                zeroseven_stoploss_two = 1
                                print('stoploss changed', str(total_stop_loss))

                            # если еще ниже устанавливаем новій стоп лосс
                            if total_cur > (((upperband[199] - middleband[199]) *stoplos_after_coef ) + middleband[
                                199]) and prel_position_coef == 0 and v6:
                                out_cur = (((upperband[199] - middleband[199]) * new_middle_coef) + middleband[
                                    199])
                                total_stop_loss = round(
                                    ((((out_cur - startong_curent) / startong_curent) * 100) * leverage), 3)
                                prel_position_coef= 1
                                print('stoploss changed', str(total_stop_loss))

                            #если выше верхнего предела закрываем сделку
                            if total_cur > (upperband[199]-(upperband[199] - middleband[199])*uperbend_boof_coef):
                                exchange.create_order(coin_pair, 'market', 'sell', buying_val,None)
                                print('Order closed: PNL(',pnl,' roe(',roe,')')
                                balance_dat = exchange.fetchBalance()
                                balance = float(balance_dat['info']['availableBalance'])
                                sucsess_orders = sucsess_orders+1
                                now = datetime.now()
                                current_time = now.strftime("%H:%M:%S")
                                logg = [current_time,'SUCSESS','Balance: ', round(balance,3), 'PNL:', pnl, 'roe%', roe,
                                        'sumary profit:',round((balance-first_balance),3),'failed_orsers:', faild_orders,
                                        'sucsess_orders:', sucsess_orders,'LONG ',coin_pair]
                                log(logg)
                                send(logg)
                                break
                            #если пересекло новый стоп лос, продаем

                            if roe < total_stop_loss and (middleband_detection_flag == 1 or first_stop_loss_coef ==1):
                                exchange.create_order(coin_pair, 'market', 'sell', buying_val, None)
                                print('Order closed: PNL(', pnl, ' roe(', roe, ')')
                                balance_dat = exchange.fetchBalance()
                                balance = float(balance_dat['info']['availableBalance'])
                                sucsess_orders = sucsess_orders + 1
                                now = datetime.now()
                                current_time = now.strftime("%H:%M:%S")
                                logg = [current_time, 'SUCSESS', 'Balance: ', round(balance,3), 'PNL:', pnl, 'roe%', roe,
                                        'sumary profit:', round((balance - first_balance), 3), 'failed_orsers:',
                                        faild_orders,
                                        'sucsess_orders:', sucsess_orders, 'LONG ', coin_pair]
                                log(logg)
                                send(logg)
                                break
                        #если меньше чем стоп лос то продаем
                        elif roe < Percent_stop_los_beg:
                            exchange.create_order(coin_pair, 'market', 'sell', buying_val, None)
                            print('Order closed: PNL(', pnl, ' roe(', roe, ')')
                            balance_dat = exchange.fetchBalance()
                            balance = float(balance_dat['info']['availableBalance'])
                            faild_orders = faild_orders + 1
                            now = datetime.now()
                            current_time = now.strftime("%H:%M:%S")
                            logg = [current_time, 'FAILED', 'Balance: ', round(balance,3), 'PNL:', pnl, 'roe%', roe,
                                    'sumary profit:', round((balance - first_balance), 3), 'failed_orsers:', faild_orders,
                                    'sucsess_orders:', sucsess_orders, 'LONG ', coin_pair]
                            log(logg)
                            send(logg)
                            break

                # если ордер на покупку еще не выполнен
                elif (order_data['info']['status']) == 'NEW':
                    print('order don`t filled')
                    exchange.cancel_order (str(order_ID),coin_pair)
                #в другом случае
                else:
                    print('Undefignet call: ',order_data['info']['status'])
                    exchange.cancel_order(str(order_ID), coin_pair)
                    exit(0)


            elif shortflag and RSI[third_num]> highgap and RSI[top_num]>highgap \
                    
                print('\a')
                print('opa short')
                send(['Positition started!', coin_pair,'Short'])

                if plotflag != 0:
                    fl.RSI_index_counter(stock_data, plotflag=1, timeperiod=timeperiod, title=coin_pair, highgap=highgap,
                                           lowgap=lowgap)

                buying_val = ((balance * trade_coef * leverage) / ((stock_data['close'])[199]))
                # продажа
                startong_curent = ((stock_data['close'])[199])
                deall = 'sell'
                try:
                    order = exchange.create_order(coin_pair, 'market', deall, buying_val,
                                                  None)
                    order_ID = order['info']['orderId']
                    data = {"symbol": coin_pair, "orderid": order_ID, "deal": deall, "buying_val": buying_val}
                    with open('temp_log.ini', 'w') as f:
                        json.dump(data, f)
                    tmp_processed_coinlist = coin_pair
                except:
                    print('filed buying')
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    logg = [current_time, 'failed buying','short',coin_pair,((sys.exc_info()[0]))]
                    log(logg)
                    send(logg)
                    tmp_processed_coinlist = coin_pair
                    break

                order_ID = order['info']['orderId']
                # проверка
                time.sleep(0.05)
                order_data = exchange.fetchOrder(order_ID, coin_pair)
                # если ордер на продажу выполнен
                if (order_data['info']['status']) == 'FILLED':
                    print('processing')
                    # начинаем следить
                    # пресваиваем первоначальный стоп лосс
                    total_stop_loss = copy.deepcopy(Percent_stop_los_beg)
                    # флаг обнаружения скользящей средней
                    middleband_detection_flag = 0
                    # флаг обнаружения второго стоп лоса
                    second_stop_loss_coef = 0
                    # флаг обнаружения безубытка
                    first_stop_loss_coef = 0
                    middle_stop_loss_coef = 0
                    zeroseven_stoploss = 0
                    zeroseven_stoploss_two = 0
                    prel_position_coef = 0
                    while True:
                        stock_data = fl.get_historical_data(exchange, coin_pair, timestep, limit=200)
                        total_cur = (stock_data['close'])[199]
                        pnl = -(round((total_cur - startong_curent) * buying_val, 3))
                        roe = -(round(((((total_cur - startong_curent) / startong_curent) * 100) * leverage), 3))
                        sys.stdout.write("\r{}".format(['PNL:', pnl, 'ROE%', roe, 'stop ROE%', total_stop_loss]))
                        sys.stdout.flush()
                        RSI = fl.RSI_index_counter(stock_data, highgap=highgap, lowgap=lowgap)
                        upperband, middleband, lowerband = fl.BBANDS_index_counter(stock_data)
                        # Если pnl больше стоп лоса
                        if roe > Percent_stop_los_beg:
                            # если пересекло первую зону формируем безубыток
                            if total_cur <(startong_curent - ((startong_curent-middleband[199])*start_high_pos_coef)) \
                                    and first_stop_loss_coef == 0 and v1:
                                out_cur = startong_curent - ((startong_curent-middleband[199])*stop_bottom_coef)
                                total_stop_loss = round(
                                    ((((startong_curent - out_cur) / startong_curent) * 100) * leverage), 3)
                                first_stop_loss_coef = 1
                                print('fitst Stop_loss changed:', str(total_stop_loss))
                            # вторая зона
                            if total_cur <(startong_curent - ((startong_curent-middleband[199])*new_middle_coef)) \
                                    and middle_stop_loss_coef == 0 and v2:
                                out_cur = startong_curent - ((startong_curent-middleband[199])*start_high_pos_coef)
                                total_stop_loss = round(
                                    ((((startong_curent - out_cur) / startong_curent) * 100) * leverage), 3)
                                middle_stop_loss_coef = 1
                                print('Stop_loss changed:', str(total_stop_loss))
                           

                            # если еще ниже устанавливаем новій стоп лосс
                            if total_cur < (middleband[199]-((middleband[199]-lowerband[199])*start_high_pos_coef)) \
                                    and second_stop_loss_coef == 0 and v4:
                                out_cur = (middleband[199])
                                total_stop_loss = round(
                                    ((((startong_curent - out_cur) / startong_curent) * 100) * leverage), 3)
                                print('Second stoploss changed',str(total_stop_loss))
                                second_stop_loss_coef = 1
                            # если еще ниже устанавливаем новій стоп лосс
                            if total_cur < (middleband[199] - ((middleband[199] - lowerband[
                                199]) * new_middle_coef)) and zeroseven_stoploss_two == 0 and v5:
                                out_cur = (middleband[199] - ((middleband[199] - lowerband[
                                199]) * start_high_pos_coef))
                                total_stop_loss = round(
                                    ((((startong_curent - out_cur) / startong_curent) * 100) * leverage), 3)
                                print(' stoploss changed', str(total_stop_loss))
                                zeroseven_stoploss_two = 1
                                # если еще ниже устанавливаем новій стоп лосс
                            if total_cur < (middleband[199] - ((middleband[199] - lowerband[
                                199]) * stoplos_after_coef)) and prel_position_coef == 0 and v6:
                                out_cur = (middleband[199] - ((middleband[199] - lowerband[
                                    199]) * new_middle_coef))
                                total_stop_loss = round(
                                    ((((startong_curent - out_cur) / startong_curent) * 100) * leverage), 3)
                                print(' stoploss changed', str(total_stop_loss))
                                prel_position_coef = 1

                            # если ниже нижнего предела закрываем сделку
                            if total_cur < (lowerband[199]+(middleband[199] - lowerband[199])*uperbend_boof_coef):
                                exchange.create_order(coin_pair, 'market', 'buy', buying_val, None)
                                print('Order closed: PNL(', pnl, ' roe(', roe, ')')
                                balance_dat = exchange.fetchBalance()
                                balance = float(balance_dat['info']['availableBalance'])
                                sucsess_orders = sucsess_orders + 1
                                now = datetime.now()
                                current_time = now.strftime("%H:%M:%S")
                                logg = [current_time, 'SUCSESS', 'Balance: ', round(balance,3), 'PNL:', pnl, 'roe%', roe,
                                        'sumary profit:', round((balance - first_balance), 3), 'failed_orsers:',
                                        faild_orders,
                                        'sucsess_orders:', sucsess_orders, 'LONG ', coin_pair]
                                log(logg)
                                send(logg)
                                break
                            # если пересекло новый стоп лос, покупаем
                            if roe < total_stop_loss and (middleband_detection_flag == 1 or first_stop_loss_coef ==1):
                                exchange.create_order(coin_pair, 'market', 'buy', buying_val, None)
                                print('Order closed: PNL(', pnl, ' roe(', roe, ')')
                                balance_dat = exchange.fetchBalance()
                                balance = float(balance_dat['info']['availableBalance'])
                                sucsess_orders = sucsess_orders + 1
                                now = datetime.now()
                                current_time = now.strftime("%H:%M:%S")
                                logg = [current_time, 'SUCSESS', 'Balance: ', round(balance,3), 'PNL:', pnl, 'roe%', roe,
                                        'sumary profit:', round((balance - first_balance), 3), 'failed_orsers:',
                                        faild_orders,
                                        'sucsess_orders:', sucsess_orders, 'LONG ', coin_pair]
                                log(logg)
                                send(logg)
                                break

                        # если меньше чем стоп лос то покупаем
                        elif roe < Percent_stop_los_beg:
                            exchange.create_order(coin_pair, 'market', 'buy', buying_val, None)
                            print('Order closed: PNL(', pnl, ' roe(', roe, ')')
                            balance_dat = exchange.fetchBalance()
                            balance = float(balance_dat['info']['availableBalance'])
                            faild_orders = faild_orders + 1
                            now = datetime.now()
                            current_time = now.strftime("%H:%M:%S")
                            logg = [current_time, 'FAILED', 'Balance: ', round(balance,3), 'PNL:', pnl, 'roe%', roe,
                                    'sumary profit:', round((balance - first_balance), 3), 'failed_orsers:', faild_orders,
                                    'sucsess_orders:', sucsess_orders, 'LONG ', coin_pair]
                            log(logg)
                            send(logg)
                            break


               
                else:
                    print('Undefignet call: ', order_data['info']['status'])
                    exchange.cancel_order(str(order_ID), coin_pair)
                    exit(0)
    except:
        send('Something gose wrong')
        send((sys.exc_info()[0]))
        print(sys.exc_info())
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print('retrying afrer 5 minutes ',current_time)
        t = 60*5
        time.sleep(t)


