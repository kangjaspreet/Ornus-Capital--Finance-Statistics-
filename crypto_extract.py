from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf

    
### Testing function: function for one coin that returns just pct change
def test_coin(beg_date, end_date, coin_name):
    url = "https://coinmarketcap.com/currencies/" + str(coin_name) + "/historical-data/?start=" + str(beg_date) + "&end=" + str(end_date)
    content = requests.get(url).content
    soup = BeautifulSoup(content,'html.parser')
    table = soup.find('table', {'class': 'table'})
    
    data = [[td.text.strip() for td in tr.findChildren('td')] 
            for tr in table.findChildren('tr')]
    df = pd.DataFrame(data)
    df.drop(df.index[0], inplace=True) # first row is empty
    df[0] =  pd.to_datetime(df[0]) # date
    for i in range(1,7):
        df[i] = pd.to_numeric(df[i].str.replace(",","").str.replace("-","")) # some vol is missing and has -
    df.columns = ['Date','Open','High','Low','Close','Volume','Market Cap']
    df.set_index('Date',inplace=True)
    df.sort_index(inplace=True)
    df['Price'] = (df['Open'] + df['Close']) / 2
    df[str(coin_name) + '%'] = df['Price'].pct_change()
    df_pct = pd.DataFrame(df[str(coin_name) + '%'])
    return df_pct

#### everything function: function that inputs beginning date, end date, and x number of
    #### coins you'd like to inspect. Calling function will spit out graphs and important 
    #### information
def everything1(date1, date2, arg, *args):
    d = test_coin(date1, date2, arg)
    for coin in args:
        df = test_coin(date1, date2, coin)
        d = pd.concat([d, df], axis=1, join='inner')
    if (len(d.columns) == 2):
        corr = d.corr()
        print(corr); print(corr**2)
        model = smf.ols('d[d.columns[1]] ~ d[d.columns[0]]', data=d, missing='drop').fit()
        print(model.summary())
        #d_norm = d.divide(d.ix[1])# a lot of coins have different starting dates. thats why we index 2 row instead of 1st
        plt.ion(); plt.figure()
        #d_norm.plot(figsize = (15,10))
        d.plot(figsize = (15,10))
        plt.pause(1); plt.figure(figsize = (10, 10))
        sns.regplot(x=d[d.columns[0]], y=d[d.columns[1]], data=d)
        plt.ioff(); plt.show()
    else:
        corr = d.corr()
        print(corr); print(corr**2)
        d_norm = d.divide(d.ix[1])
        plt.ion(); plt.figure()
        d_norm.plot(figsize = (15, 10))
        plt.pause(1)
        plt.figure(figsize=(10,10))
        sns.heatmap(corr, xticklabels=corr.columns.values, yticklabels=corr.columns.values)
        plt.ioff(); plt.show()