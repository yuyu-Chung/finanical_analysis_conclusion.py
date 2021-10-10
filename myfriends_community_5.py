#  本程式檔目標:查詢本日美金匯率是否為近5日最低點。
#  本程式檔使用方式:已先行設定查詢天數為5日，直接執行程式檔即可，或另外修改查詢天數、最小匯率索引值，再行執行本程式檔。
#  本程是檔驗證方式: 因預設查詢僅5日，data不多，可將本程式檔變數"coin_result"再行設定"print"直接核對原程式執行結果是否正確。
#  本程式檔使用之第三方套件:yfinance，若無下載須先行下載(pip install yfinance)

import yfinance as yf


def coin_ratio(slot="5d"):
    coin = yf.Ticker("USDTWD=X")
    coin_result = list(coin.history(period=slot, interval="1d").Close)

    min_value = min(coin_result)
    #min_idx = coin_result.index(min_value)


    if min_value == coin_result[-1]:
        print("本日是近5日匯率最低點")
    else:
        print("本日不是近5日匯率最低點")

coin_ratio()
