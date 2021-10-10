# 本程式檔目標為找出台灣50股票中，每日外資買/賣超前三名之股票，列入選股參考。
# 本程式檔使用方式 : 已預設跑出台灣50中外資買/賣超前3名的股票，可重新設定希望呈現之前幾名股票，如 foreign_investor_buy = foreign_investor_buy[:5]
# 本程式檔如何驗證 : 可對照輸出之台灣50與每日外資買超前100名股票代號取交集的list，是否與台灣50股票及每日外資買超排名前100名單交叉比對一致。
#                   以及最後輸出之折線圖，其公司是否包含於 交集list、網路台灣50名單、網路每日外資買/賣超排名名單內。(參考爬蟲網頁。)

# 先載入將使用之第三方套件包，requests、BeautifulSoup、pandas、yfinance、matplotlib，若無下載皆須先行下載(pip install (requests、BeautifulSoup、pandas、yfinance、matplotlib))

import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# matplotlib圖檔若有中文字串，顯示中文字串之設定

font = {'family' : 'DFKai-SB',
'weight' : 'bold',
'size' : '12' }
plt.rc('font', **font)
plt.rc('axes',unicode_minus=False)


# 網路爬蟲，取得台灣50成分股代號，做成list
def Taiwan_50():
    url_1 = "https://histock.tw/twclass/A901"
    html_1 = requests.get(url_1)
    html_1_text = BeautifulSoup(html_1.text, "html5lib")
    html_1_data = html_1_text.find_all("span",{"class":{"w60 lft-p stockno"}})
    taiwan_50 = []
    for elem in html_1_data:
        list_1 = elem.text
        list_2 = list_1+".TW"
        taiwan_50.append(list_2)
    del taiwan_50[0]

    return taiwan_50


# 網路爬蟲，取得外資買超排名前100股票代號，做成list
def foreign_captial_buy():    
    url_2 = "https://tw.stock.yahoo.com/rank/foreign-investor-buy/"
    html_2 = requests.get(url_2)
    html_2_text = BeautifulSoup(html_2.text, "html5lib")
    html_2_data = html_2_text.find_all("div",{"class":{"D(f) Ai(c)"}})
    foreign_100_buy = []
    for symble in html_2_data:
        stock = symble.text
        foreign_100_buy.append(stock)
    for not_stock in foreign_100_buy:
        if len(not_stock)!= 7:
            foreign_100_buy.remove(not_stock)
    
    return foreign_100_buy


# 網路爬蟲，取得外資賣超排名前100股票代號，做成list
def foreign_captial_sell():    
    url_3 = "https://tw.stock.yahoo.com/rank/foreign-investor-sell"
    html_3 = requests.get(url_3)
    html_3_text = BeautifulSoup(html_3.text, "html5lib")
    html_3_data = html_3_text.find_all("div",{"class":{"D(f) Ai(c)"}})
    foreign_100_sell = []
    for point in html_3_data:
        sell_dot = point.text
        foreign_100_sell.append(sell_dot)
    for not_sell_dot in foreign_100_sell:
        if len(not_sell_dot)!=7:
            foreign_100_sell.remove(not_sell_dot)
    
    return foreign_100_sell


# 將 台灣50代號list 與 外資100買/賣超代號list，取交集，做成供查詢 的 台灣50買/賣超排名list。
# list 取交集:intersection；取聯集:union；取差集:difference
def foreign_investor_list(foreign_100_buy, foreign_100_sell,taiwan_50):
    foreign_investor_buy = list(set(foreign_100_buy).intersection(set(taiwan_50)))
    foreign_investor_sell = list(set(foreign_100_sell).intersection(set(taiwan_50)))
    
    return {"foreign_investor_buy":foreign_investor_buy, "foreign_investor_sell":foreign_investor_sell}

# 將預備好的 foreign_investor list 整理出股票資料DataFrame 以及最後折線圖呈現。
# 買超股票價格圖輸出
def stock_info_buy(foreign_investor_buy):
    stock = yf.Ticker(foreign_investor_buy)
    stock_data = stock.history(period="1y", interval="1d")
    stock_buy_name = stock.info
    stock_buy_pd = pd.DataFrame(stock_data)
    
    sma = stock_buy_pd["Close"].rolling(5).mean()
    lma = stock_buy_pd["Close"].rolling(20).mean()

    stock_buy_pd["SMA"] = sma
    stock_buy_pd["LMA"] = lma

    plt.plot(stock_buy_pd.Close, color = "navy", label="Close Price")
    plt.plot(stock_buy_pd.SMA, color="red", label="SMA")
    plt.plot(stock_buy_pd.LMA, color ="orange", label="LMA")
    plt.title(stock_buy_name["shortName"]+"買超績優股")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend(loc="best")
    plt.grid()
    plt.show() 

# 賣超股票價格圖輸出
def stock_info_sell(foreign_investor_sell):
    stock = yf.Ticker(foreign_investor_sell)
    stock_data = stock.history(period="1y", interval="1d")
    stock_sell_name = stock.info
    stock_sell_pd = pd.DataFrame(stock_data)
    
    sma = stock_sell_pd["Close"].rolling(5).mean()
    lma = stock_sell_pd["Close"].rolling(20).mean()

    stock_sell_pd["SMA"] = sma
    stock_sell_pd["LMA"] = lma

    plt.plot(stock_sell_pd.Close, color = "navy", label="Close Price")
    plt.plot(stock_sell_pd.SMA, color="red", label="SMA")
    plt.plot(stock_sell_pd.LMA, color ="orange", label="LMA")
    plt.title(stock_sell_name["shortName"]+"賣超績優股")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend(loc="best")
    plt.grid()
    plt.show()

# 依本程式目標，呼叫台灣50股票中，外資買/賣超前3高者，股票折線圖呈現。

if __name__ == "__main__":
    taiwan_50 = Taiwan_50()
    foreign_100_buy = foreign_captial_buy()
    foreign_100_sell = foreign_captial_sell()
    final_list = foreign_investor_list(foreign_100_buy, foreign_100_sell, taiwan_50)
    foreign_investor_buy = final_list["foreign_investor_buy"]
    foreign_investor_buy=  foreign_investor_buy[:3]
    foreign_investor_sell = final_list["foreign_investor_sell"]
    foreign_investor_sell = foreign_investor_sell[:3]
    for buy_elem in foreign_investor_buy:
        stock_info_buy(buy_elem)
    for sell_elem in foreign_investor_sell:
        stock_info_sell(sell_elem)
      
