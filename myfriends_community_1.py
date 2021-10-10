import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

font = {'family' : 'DFKai-SB',
'weight' : 'bold',
'size' : '12' }
plt.rc('font', **font)
plt.rc('axes',unicode_minus=False)


stock_2880 = yf.Ticker("2880.TW")
stock_2880_2021_7 = stock_2880.history(period="6mo",interval="1d")
stock_2880_2021_7_pd = pd.DataFrame(stock_2880_2021_7)


stock_2880_moving_average_5 = stock_2880_2021_7_pd.Close.rolling(5).mean()

stock_2880_moving_average_20 = stock_2880_2021_7_pd.Close.rolling(20).mean()


plt.plot(stock_2880_2021_7_pd.Close,color="blue",marker="o",label="收盤價")
plt.plot(stock_2880_moving_average_5,color="red",marker=".",label="短線")
plt.plot(stock_2880_moving_average_20,color="yellow",marker="o",markersize=2,label="月線")
plt.title("華南金2021年可以買時機點")
plt.xlabel("日期")
#plt.xticks(range(0,130,14),rotation=30)
plt.ylabel("股價")
plt.legend(loc = "upper left")
plt.grid()
plt.show()


def f(x):
    a1 = stock_2880_2021_7_pd.Close[x]
    a2 = stock_2880_moving_average_5[x]
    a3 = stock_2880_moving_average_20[x]
    print("華南金買賣時機點判斷")
    print("日期:",x)
    print("收盤價:",a1)
    print("短線價格:",a2)
    print("月線價格:",a3)
    if a2-a3>0.1:
        print("上漲趨勢")
    elif -0.1<=a2-a3<=0.1:
        print("黃金交叉點!!再行觀察前幾日短線與季線斜率")
    else:
        print("下跌趨勢")   

f('2021-08-16')

#草稿
#if 收盤價>五日均價 --->極短線看漲
#if 收盤價>十日均價 --->短線看漲
#if 五日均價>十日均價  ---> 上漲趨勢
   #五日均價<十日均價  ---> 下跌趨勢
   #五日均價 = 十日均價  ---> 黃金交叉點!! 不要買!!!
