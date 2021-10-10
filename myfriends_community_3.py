# 本程式檔目標:針對股市台灣50，分析其當下是否適合投資，於使用者視窗，將呈現台灣50成分股，1年來股價分析趨勢圖(一支股票1張，總計50張)，及最近5日是否適合投資建議(每支股票皆有建議，總計50個字串模組輸出)。
# 本程式檔使用方式:不用另外於使用者視窗輸入任何資料，只要直接執行本程式檔即可。
# 程式結果如何驗證? 就自己買股票試試看有沒有賺就知道了

# 使用之函式庫: requests、bs4、pandas、yfinance、matplotlib
# 若無下載， 皆須先行下載， pip install (requests、BeautifulSoup、pandas、yfinance、matplotlib)

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# 網路爬蟲，藉網路自行更新，取得台灣50股票代號
def webcraw():
    url = "https://histock.tw/global/globalclass.aspx?mid=0&id=2"
    headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
    html = requests.get(url, headers=headers)
    stock_data = BeautifulSoup(html.text, "html5lib")
    stock_ids = stock_data.find_all("span", {"class":{"w70 lft-p stockno"}})

    return stock_ids


# 股票代號轉成 list
def stock(stock_ids):
    list =[]
    for element in stock_ids:
        symble = element.text
        stock_id = symble+".TW"
        list.append(stock_id)

    return list


# 取得每支股票的細部data，以備後面畫圖及判斷買賣時機點使用:
# 取得母體資料、周線、月線、周線斜率、 整體平均股價、整體股價標準差，平均股價+-標準差=賣/買參考指標
def stock_detail(list):
    stock = yf.Ticker(list)                               
    data = stock.history(period="1y", interval="1d")         
    name = stock.info    
    data_pd = pd.DataFrame(data)

    sma = data_pd["Close"].rolling(5).mean()
    lma = data_pd["Close"].rolling(20).mean()
    slope = sma.diff()
    p_mean = data_pd["Close"].mean()
    p_std = data_pd["Close"].std()
    index_list = data_pd.index

    # 將預備用折線圖呈現的資料，修正成 Series 型態，以便與母體資料合併、及後續繪圖使用。
    #  average_line = 股價平均數曲線(因平均數為一特定數值，x軸設定為交易日期，y軸為平均股價，為一水平線。
    #  sell_line = (股價平均價格+標準差)曲線，x軸同上設定，y軸為(平均價格+標準差)也是特定數值，同樣為一水平線。
    #  buy_line = (平均價格-標準差)曲線，同上也是一水平線。
    #  因每日價格漲跌無法判定，故以股價過去一整年度資料當參考指標，假定價格會循環、漲跌皆有範圍，如果股價落在(平均數+標準差)以上，則很有可能處在本支股票價格高點，
    #  後續儘管有可能續漲，但賣出也會賣在相對高點價格，故價格只要高於此數值，皆適合賣出。
    #  同上假定，若股價價格低於(平均數-標準差)，則應該處於本支股票低點，需避免資金投入，徒增資金停滯及等待時間的焦慮心情，故若配合其他指標，
    #  判斷趨勢會上漲時，以:(平均數-標準差)<=股價<=平均價，為判斷基準，若價格落於此範圍，表示價格已上漲一陣子脫離谷底，且仍處於股票相對低點價格，皆適合買進。

    average_line = pd.Series([p_mean]*len(index_list), index=index_list)                                                    
    sell_p = p_mean + p_std
    sell_line = pd.Series([sell_p]*len(index_list), index=index_list)                                                        
    buy_p = p_mean - p_std
    buy_line = pd.Series([buy_p]*len(index_list), index=index_list)                                                          
    
    new_data_pd =  data_pd.copy()
    new_data_pd["SMA"] = sma
    new_data_pd["LMA"] = lma
    new_data_pd["Slope"] = slope
    new_data_pd["Average"] = average_line
    new_data_pd["Sell Line"] = sell_line
    new_data_pd["Buy_line"] = buy_line
    new_data_pd["Surplus"] = sma-lma
    for sellpoint in new_data_pd["Close"]:
        new_data_pd["Sell Signal"] = np.where(sellpoint > sell_p, 1, 0)
    for buypoint in new_data_pd["Close"]:
        new_data_pd["Buy Signal"] = np.where(buy_p < buypoint <= p_mean, 1, 0)

    return(new_data_pd, name)


# 繪圖，先將基本判斷資料呈現 : 股價、股名、周線、月線、股價平均線、股價賣出參考線、股價買進參考線
def picture(new_data_pd, name):    
    plt.plot(new_data_pd.Close, color="navy", label="Close price")
    plt.plot(new_data_pd.SMA, color="red", label="SMA")
    plt.plot(new_data_pd.LMA, color="orange", label="LMA")
    #plt.plot(new_data_pd.Average, color="yellow", label="mean")
    #plt.plot(new_data_pd["Sell Line"], color="green", linestyle="--", label="Sell Line")
    #plt.plot(new_data_pd["Buy_line"], color="magenta", linestyle="--", label="Buy line")
    plt.grid()
    plt.title(name["shortName"]+" Curve")

#  買賣點繪圖 : 
    # 買點繪圖: 
    # 取股票原母體資料(new_data_pd)最後五筆紀錄，理論上即為最近五天內的資料，    
    buyinfo = new_data_pd.tail(5)
    buyinfo_pd = buyinfo.copy()

    # 篩選 [周線-月線]>0 、[周線斜率]>0 及 [股價介於 buy_line 與平均股價之間] 的列
    buyinfo_pd = buyinfo_pd[buyinfo_pd["Surplus"]>0]
    buyinfo_pd = buyinfo_pd[buyinfo_pd["Slope"]>0]
    buyinfo_pd = buyinfo_pd[buyinfo_pd["Buy Signal"]==1]

    # 若經篩選仍有資料，繪圖出買點。
    plt.scatter(buyinfo_pd.index, buyinfo_pd.Close, marker="^", s=100, c="red", label="recommend to buy")
    #for buy_index, buy_value in zip(buyinfo_pd.index, buyinfo_pd.Close):
        #plt.text(buy_index, buy_value, str(buy_index).replace(' 00:00:00',''))
    
    # 賣點繪圖:
    # 篩選方法同買點，不同處於"Signal"欄位，設定為[股價大等於 sell_p]，若大等於則值返回1，否則為0]
    sellinfo_pd = buyinfo.copy()
    sellinfo_pd = sellinfo_pd[sellinfo_pd["Surplus"]>0]
    sellinfo_pd = sellinfo_pd[sellinfo_pd["Slope"]>0]
    sellinfo_pd = sellinfo_pd[sellinfo_pd["Sell Signal"]==1]

    plt.scatter(sellinfo_pd.index, sellinfo_pd.Close, marker="v", s=100, c="green", label="recommend to sell")
    #for sell_index, sell_value in zip(sellinfo_pd.index, sellinfo_pd.Close):
        #plt.text(sell_index, sell_value, str(sell_index).replace(' 00:00:00',''))
    
    plt.legend()
    plt.show()


# 近日買賣建議
def recommend_signal(new_data_pd, name):

    # 先呈現公司名稱，以分辨個別股票，
    print(name["shortName"])

    # 以原母體資料，取最後5筆 row，並分別製作買點、賣點DataFrame
    buy_signal = new_data_pd.tail(5)
    buy_signal_pd = buy_signal.copy()
    buy_signal_pd = buy_signal_pd[buy_signal_pd["Surplus"]>0]
    buy_signal_pd = buy_signal_pd[buy_signal_pd["Slope"]>0]
    buy_signal_pd = buy_signal_pd[buy_signal_pd["Buy Signal"]==1]

    sell_signal_pd = buy_signal.copy()
    sell_signal_pd = sell_signal_pd[sell_signal_pd["Surplus"]>0]
    sell_signal_pd = sell_signal_pd[sell_signal_pd["Slope"]>0]
    sell_signal_pd = sell_signal_pd[sell_signal_pd["Sell Signal"]==1]

    # 預備 numpy matrix，供後續分析判斷輸出內容使用。
    # 針對買點DataFrame，取出買點index、value，分別製作成list_1、list_2
    list_1=[]
    list_2=[]
    for buy_ind_elem in buy_signal_pd.index:
        buy_ind = "{}".format(np.array(str(buy_ind_elem).replace("00:00:00","")))
        list_1.append(buy_ind) 
    for buy_val_elem in buy_signal_pd["Close"]:
        buy_val = "{}".format(np.array(buy_val_elem))
        list_2.append(buy_val)

    # 針對賣點DataFrame，取出賣點index、value，分別製作成list_3、list_4
    list_3=[]
    list_4=[]
    for sell_ind_elem in sell_signal_pd.index:
        sell_index = "{}".format(np.array(str(sell_ind_elem).replace("00:00:00","")))
        list_3.append(sell_index)
    for sell_val_elem in sell_signal_pd["Close"]:
        sell_val = "{}".format(np.array(sell_val_elem))
        list_4.append(sell_val)
    
    # 取買點index、value 做成的list，合成一個買點 numpy matrix，再將此 matrix 行列轉置，使得日期與價格可兩兩成同一列。
    # 最後轉置之 matrix 即為預備輸出之分析結果
    buy_np = np.array([list_1,
                       list_2])
    buy_np_cq = buy_np.T

    # 賣點輸出資料製作同買點
    sell_np = np.array([list_3,
                        list_4])
    sell_np_cq = sell_np.T

    # 投資建議: 如果買點DataFrame 等於空集合，表示沒有買點，反之，則是有買點，再把買點日期、價格印出來
    print("Whether the latest 5 days are suitable to buy:")
    if buy_signal_pd.empty == True:
        print("It's not time yet.")
    else:
        print("Recommend to buy:")
        print(buy_np_cq)        
    
    # 投資建議，如果賣點DataFrame 等於空集合，表示沒有賣點，反之，則是有賣點，再把賣點日期、價格印出來
    print("Whether the latest 5 days are suitable to sell:")
    if sell_signal_pd.empty == True:
        print("It's not time yet.")
    else:
        print("Recommend to sell:")
        print(sell_np_cq)        

    print("   ")
    
rawdata = webcraw()
stock(rawdata)

qq = [stock_detail(list) for list in stock(rawdata)]

[picture(fu[0], fu[1]) for fu in qq] 

[recommend_signal(yu[0], yu[1]) for yu in qq]
