# 將前面作業統合，用class呈現。
# 1.台灣50成分股。
# 2.台灣50外資買賣超前100排名者。
# 3.美元匯率是否為近5日最低價。
# 4.圖呈現:收盤價、短線、長線、買、賣點。
# 5.投資建議
# 本程式檔目標:就是練習class指令跟作業複習統整
# 本程式檔執行方式:選擇想要執行的method，用class語法設定執行，已預設各method執行。
# 本程式檔驗證方式:1.各種股票list可將list設定print，另參閱原爬蟲網站，進行校對。2.圖可參閱yahoo股市特定股票之交易圖進行比對。3.外匯輸出可直接將list print，以校對程式執行結果。4.預測，可參考圖片輸出method 買賣點標籤 或直接把can_buy can_sell print 進行校對。

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup 

class conclusion:
    def __init__(self, name):
        self.short = 5
        self.long = 20

    def taiwan_50(self):
        url = "https://histock.tw/global/globalclass.aspx?mid=0&id=2"
        headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        html = requests.get(url, headers=headers)
        stock_data = BeautifulSoup(html.text, "html5lib")
        stock_list_raw = stock_data.find_all("span", {"class":{"w70 lft-p stockno"}})
        stock_list = []
        for stock in stock_list_raw:
            elem = stock.text
            stock_fin = elem+".TW"
            stock_list.append(stock_fin)

        return stock_list

    def foreign_captial(self):
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
    
        foreign_investor_buy = list(set(foreign_100_buy).intersection(set(taiwan_50)))
        foreign_investor_sell = list(set(foreign_100_sell).intersection(set(taiwan_50)))
 
        return {"foreign_investor_buy":foreign_investor_buy, "foreign_investor_sell":foreign_investor_sell}
        
    def coin_ratio(self,slot="5d"):
        coin = yf.Ticker("USDTWD=X")
        coin_result = list(coin.history(period=slot, interval="1d").Close)

        min_value = min(coin_result)

        if min_value == coin_result[-1]:
            print("本日是近5日匯率最低點")
        else:
            print("本日不是近5日匯率最低點")


    def picture(self, stock):
        stock_el = yf.Ticker(stock)
        name = stock_el.info
        stock_detail = stock_el.history(period="1y",interval="1d")
        stock_data = pd.DataFrame(stock_detail)

        sma = stock_data.Close.rolling(self.short).mean()
        lma = stock_data.Close.rolling(self.long).mean()
        slope = sma.diff()

        stock_data["SMA"] = sma
        stock_data["LMA"] = lma
        stock_data["Surplus"] = sma-lma

        stock_data["Buy_signal"] = np.where(stock_data["Surplus"]>0,1,0)
        stock_data["Buy_point"] = np.where((stock_data["Buy_signal"].diff())==1,1,0)

        stock_data["Sell_signal"] = np.where(stock_data["Surplus"]<0,1,0)
        stock_data["Sell_point"] = np.where((stock_data["Sell_signal"].diff())==1,1,0)

        for_buy = stock_data[stock_data["Buy_point"] == 1]
        for_sell = stock_data[stock_data["Sell_point"] ==1]

        plt.plot(stock_data.Close, color = "navy", label = "Close Price")
        plt.plot(stock_data.SMA, color = "red", label = "sma")
        plt.plot(stock_data.LMA, color = "orange", label = "lma")
        plt.scatter(for_buy.index, for_buy["Close"], color="red", marker="^", s=200, label="buy point")
        plt.scatter(for_sell.index, for_sell["Close"], color="green",marker="v", s=200, label="sell point")
        plt.title(name["shortName"]+" analysis")
        plt.legend(loc="best")
        plt.grid()
        plt.show()

    def predict(self,stock):
        stock_el = yf.Ticker(stock)
        name = stock_el.info
        stock_detail = stock_el.history(period="1y",interval="1d")
        stock_data = pd.DataFrame(stock_detail)

        sma = stock_data.Close.rolling(self.short).mean()
        lma = stock_data.Close.rolling(self.long).mean()

        stock_data["SMA"] = sma
        stock_data["LMA"] = lma
        stock_data["Surplus"] = sma-lma

        stock_data["Buy_signal"] = np.where(stock_data["Surplus"]>0,1,0)
        stock_data["Buy_point"] = np.where((stock_data["Buy_signal"].diff())==1,1,0)

        stock_data["Sell_signal"] = np.where(stock_data["Surplus"]<0,1,0)
        stock_data["Sell_point"] = np.where((stock_data["Sell_signal"].diff())==1,1,0)

        recent_day = stock_data.tail()
        can_buy = recent_day[recent_day["Buy_point"]==1]
        can_sell = recent_day[recent_day["Sell_point"]==1]

        print(name["shortName"]+" Recommendation")
        print("Whether the latest 5 days are suitable to buy:")
        if can_buy.empty == True:
            print("It's not time yet.")
        else:
            print("Recommend to buy:")
            for buy_index in can_buy.index:
                index_buy = "{}".format(np.array(str(buy_index).replace("00:00:00","")))
                for buy_value in can_buy["Close"]:
                    print(index_buy, buy_value)

        print("Whether the latest 5 days are suitable to sell:")
        if can_sell.empty == True:
            print("It's not time yet.")
        else:
            print("Recommend to sell:")
            for sell_index in can_sell.index:
                index_sell = "{}".format(np.array(str(sell_index).replace("00:00:00","")))
                for sell_value in can_sell["Close"]:
                    print(index_sell, sell_value) 

        print(" ")


if __name__ == "__main__":        
    test = conclusion("test")
    taiwan_50 = test.taiwan_50()
    test.coin_ratio()
    foreign_captial = test.foreign_captial()
    foreign_captial_picture =[test.picture(elem) for elem in (foreign_captial["foreign_investor_buy"])]
    predict_1 = [test.predict(dot) for dot in foreign_captial["foreign_investor_buy"]]
