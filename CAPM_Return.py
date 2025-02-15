# importing Libraries

import streamlit as st
import pandas as pd
import yfinance as yf
import datetime 
import pandas_datareader as web
import capm_functions


st.set_page_config(page_title = "CAPM",
                   page_icon = "chart_with_upwards_trend",
                   layout = 'wide'
                   )

st.title("Capital Asset Pricing Model")


# getting input from user


col1, col2 = st.columns([1, 1])
with col1:
    stocks_list = st.multiselect("choose 4 stocks",('TSLA','AAPL','NFLX','MSFT','MGM','AMZN','NVDA','GOOGL'),['TSLA','AAPL','AMZN','GOOGL'])
with col2:
    year = st.number_input("Number of years",1,10)


# downloading data for SP500
try: 
    end = datetime.date.today()
    start = datetime.date(datetime.date.today().year-year,datetime.date.today().month, datetime.date.today().day)
    SP500 = web.DataReader(['sp500'],'fred',start,end)
    #print(SP500.head())


    stocks_df = pd.DataFrame()

    for stock in stocks_list:
        data = yf.download(stock, period= f'{year}y')
        #print(data.head())
        stocks_df[f'{stock}'] = data['Close']

    #print(stocks_df.head())


    stocks_df.reset_index(inplace=True)
    SP500.reset_index(inplace = True)
    SP500.columns = ['Date','sp500']
    print(stocks_df.dtypes)
    print(SP500.dtypes)


    # merging both 

    stocks_df = pd.merge(stocks_df, SP500, on='Date', how='inner')
    print(stocks_df)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Dataframe head")
        st.dataframe(stocks_df.head(), use_container_width= True)
    with col2:
        st.markdown("### Dataframe tail")
        st.dataframe(stocks_df.tail(), use_container_width= True)


    # call capm_functions
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Price of all the stocks")
        st.plotly_chart(capm_functions.interactive_plot(stocks_df))
    with col2:
        st.markdown("### Price of all the Stocks (After Normalizing)")
        st.plotly_chart(capm_functions.interactive_plot(capm_functions.normalize(stocks_df)))

    # stocks daily return
    stocks_daily_return = capm_functions.daily_return(stocks_df)
    print(stocks_daily_return.head())

    # storing alpha and beta values for every stocks
    beta = {}
    alpha = {}

    for i in stocks_daily_return.columns:
        if i != 'Date' and i != 'sp500':
            b, a = capm_functions.calculate_beta(stocks_daily_return, i)

            beta[i] = b
            alpha[i] = a 
    print(alpha, beta)

    beta_df = pd.DataFrame(columns = ['Stock','Beta Value'])
    beta_df['Stock'] = beta.keys()
    beta_df['Beta Value'] = [str(round(i,2)) for i in beta.values()]

    with col1:
        st.markdown("### Calculated Beta Value")
        st.dataframe(beta_df, use_container_width=True)

    rf = 0
    rm = stocks_daily_return['sp500'].mean()*252


    return_df = pd.DataFrame()
    return_value = []
    for stock, value in beta.items():
        return_value.append(str(round(rf+(value*(rm-rf)))))
    return_df['Stock'] = stocks_list


    return_df['Return Value'] = return_value

    with col2:
        st.markdown("### Calculated Returns using CAPM")
        st.dataframe(return_df, use_container_width=True)
except:
    st.write("Data Loading Please Wait!!!")
