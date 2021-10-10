import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

# 輸入股票名、短線天數、長線天數，預測股票適合買/賣點及現在是否適合買
name = str(input("Stock brief Name:"))
sma = int(input("Moving average short period:"))
lma = int(input("Moving average long period:"))

# 取得股票各種重要data
def stock_data(name, sma, lma):
    target = yf.download(name, period="1y", interval="1d")                     # 母體資料  
    target_df = pd.DataFrame(target)                        
    mvs = target_df["Close"].rolling(sma).mean()                               # 短線     df["X"] -->選取單一欄位，Series型態
    mvl = target_df["Close"].rolling(lma).mean()                               # 長線     Series
    mvs_slope = mvs.diff()                                                     # 短線斜率  Series
    mvl_slope = mvl.diff()                                                     # 長線斜率  Series

    # 新增短線、長線、短線斜率、(短線-長線)4欄
    #new_target_df = target_df.copy()
    #new_target_df["mvs"] = mvs.values
    #new_target_df["mvl"] = mvl.values
    #new_target_df["mvs_slope"] = mvs_slope.values
    #new_target_df["cm_p"] = new_target_df["mvs"] - new_target_df["mvl"]
    new_target_df = pd.DataFrame({"Open":target_df.Open, "High":target_df.High, "Low":target_df.Low, "Close":target_df.Close, "Adj Close":target_df["Adj Close"], "Volume":target_df.Volume, "mvs":mvs, "mvl":mvl, "mvs_slope":mvs_slope, "cm_p":mvs-mvl})

    # 以DataFrame為母體，依序設定各種條件縮小選取範圍，直至縮小至1筆row，即是買/賣點
    # 買點
    bas_1 = new_target_df[new_target_df["cm_p"]>=0]                           #選取(短線-長線)>=0的列         
    bas_2 = bas_1[bas_1["mvs_slope"]>0]                                       #選取短線斜率>0的列
    buy_5 = bas_2.cm_p.nsmallest(5)                                           #選取(短線-長線)排序最小的5個值，Series
    buy_5_p = new_target_df.loc[buy_5.index,"Close"]                          #資料整理: 以DataFrame為母體，依上Series索引，取出收盤價，製作新Series
    buy_index = buy_5_p.idxmin()                                              #選取最小值索引---> 最佳買點日期
    buy_value = buy_5_p.min()                                                 #選取最小值    ---> 最佳買點收盤價  
    
    #賣點
    sell_5 = bas_2.cm_p.nlargest(5)                                          #選取(短線-長線)排序最大的5個值。                                         
    sell_5_p = new_target_df.loc[sell_5.index,"Close"]                       #同上資料整理  
    sell_index = sell_5_p.idxmax()                                           #選取最大值索引 ---> 最佳賣點日期
    sell_value = sell_5_p.max()                                              #選取最大值     ---> 最佳賣點收盤價
    
    
    return(new_target_df,mvl_slope,buy_index,buy_value,sell_index,sell_value)              
 #               0            1          2        3           4        5        
# 買/賣點建議
def buy_sell_point(buy_index,buy_value,sell_index,sell_value):         
    print("The best buying point date:",buy_index)
    print("The best buying point price",buy_value)
    print("The best selling point date:",sell_index)
    print("The best selling point price:",sell_value)


# 繪製分析圖
def stock_picture(new_target_df, mvs, mvl, buy_index, buy_value, sell_index, sell_value):   
    k_p = new_target_df[["Volume","Open","High","Low","Close"]]                                                                      # K線圖Data
    mc = mpf.make_marketcolors(up ="r", down="g", edge="", volume="inherit", wick="inherit")                                             # K線圖各種標記顏色設定-->調整bar 上漲紅 下跌綠               
    s = mpf.make_mpf_style(base_mpf_style="yahoo", marketcolors=mc)                                                                   # K線圖style設定        
    mpf.plot(k_p, type="candlestick", style=s, mav=(5,40), title=name+" K curve", volume=True, ylabel_lower="Shares", ylabel="$")           # K線圖
    plt.plot(new_target_df["Close"], color="blue", label="close price")                                                                # 收盤價
    plt.plot(mvs, color="red", label="short term price")                                                                               # 畫圖，短線曲線
    plt.plot(mvl, color="orange", label="long term price")                                                                             # 畫圖，長線曲線
    plt.scatter(buy_index,buy_value, c = "green", s = 200, marker="^", label="best buying point")                                        # 畫圖，買點
    plt.scatter(sell_index,sell_value,c = "red",s = 200,marker="v",label="best selling point")                                       # 畫圖，賣點           
    plt.annotate(str(buy_index).replace("00:00:00",""), xy = (buy_index, buy_value), xytext = (buy_index,buy_value), color="black")   # 標註買點
    plt.text(sell_index, sell_value, str(sell_index).replace("00:00:00",""), color="black")                                             # 標註賣點
    plt.title(name+"2021 analysis curve")                                                                                            # 畫圖，分析圖名子
    plt.legend(loc="best")                                                                                                           # 畫圖，註解位置
    plt.grid()                                                                                                                       # 畫圖，網格(mpf)
    plt.grid()                                                                                                                       # 畫圖，網格(plt)
                                                                                                                            
    plt.show()                                                                                                                       # 畫圖，出來吧!! \^O^/

"""
現在買賣建議。(短線值vs長線值)->(短線斜率VS長線斜率):3x3=9種情況:
    短線>長線->短線斜率>長線斜率-> 1 -> up tendency,reccomends to buy!!
    短線>長線->短線斜率=長線斜率-> 2 -> up tendency becomes weak,needs enough time to recheck.
    短線>長線->短線斜率<長線斜率-> 3 -> up tendency becomes weak,needs enough time to recheck.
    短線=長線->短線斜率>長線斜率-> 4 -> golden point!! strongly recommend to buy
    短線=長線->短線斜率=長線斜率-> 5 -> steady flow, needs time to see whether up or down
    短線=長線->短線斜率<長線斜率-> 6 -> golden point of collapse!! needs some emotional preparation to lose money!
    短線<長線->短線斜率>長線斜率-> 7 -> maybe be going to climb
    短線<長線->短線斜率=長線斜率-> 8 -> in a steady low statious
    短線<長線->短線斜率<長線斜率-> 9 -> keep collapsing!
df.iat[] --> pandas 提取特定列/行、列與行交叉對應之值，本case 因 mvs、mvl、mvs_slop、mvl_slop 只有 1 column，測試iat[]內僅輸入列(1個值即可)。
"""
def stock_pridict(mvs, mvl, mvs_slope, mvl_slope):
    if mvs.iat[-1] > mvl.iat[-1] :
        if mvs_slope.iat[-1] > mvl_slope.iat[-1]:
            print("up tendency,reccomends to buy!!")
        elif mvs_slope.iat[-1] == mvl_slope.iat[-1]:
            print("up tendency becomes weak,needs enough time to recheck.")
        else: 
            print("up tendency becomes weak,needs enough time to recheck.")
    elif mvs.iat[-1] == mvl.iat[-1] :
        if mvs_slope.iat[-1] > mvl_slope.iat[-1]:
            print("golden point!! strongly recommend to buy") 
        elif mvs_slope.iat[-1] == mvl_slope.iat[-1]:
            print("steady flow, needs time to see whether up or down")
        else:
            print("golden point of collapse!! needs some emotional preparation to lose money!")
    else:
        if mvs_slope.iat[-1] > mvl_slope.iat[-1]:
            print("maybe be going to climb")
        elif mvs_slope.iat[-1] == mvl_slope.iat[-1]:
            print("in a steady low statious ")
        else:
            print("keep collapsing!")

a = stock_data(name,sma,lma)
buy_sell_point(a[2],a[3],a[4],a[5])
stock_picture(a[0], a[0]["mvs"], a[0]["mvl"], a[2], a[3], a[4], a[5])
stock_pridict(a[0]["mvs"], a[0]["mvl"], a[0]["mvs_slope"], a[1])



watch_lst = ['ARKK','CRWD','LPX','MU','NMM','PLTR','SQ','GOOGL', 'JPM', \
             'TER','TRTN','VT','VGT','WCLD','DDOG','STX','NARI', 'ICE', \
             'TDOC','BBL','GSK','MTLS','RIO','RDS.BA', 'RDSA.AS','SONY', \
                 'SFTBY','UL','VWDRY','ZIM','VTI','QQQ','UPST','MA','TSM']
