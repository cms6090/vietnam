# 라이브러리 불러오기
import requests
import yfinance as yf
import pandas as pd
from yahooquery import Ticker
import numpy as np
import cloudscraper


def convert(value):  # 끝이 M, K일때 숫자로 변환
    if isinstance(value, str):  # 입력값이 문자열인 경우만 처리
        if "K" in value:
            return float(value.replace("K", "")) * 1000
        if "M" in value:
            return float(value.replace("M", "")) * 1000000
    return value


def get_data(ticker_name):
    data = yf.download(ticker_name)
    data = data.sort_values(by="Date", ascending=True)
    data = data.drop(columns=["Adj Close"])
    data.to_csv(ticker_name + ".csv", encoding="utf-8-sig")
    data.index = data.index.astype(str)
    return data


def get_data_investing(url, ticker_name):
    scraper = cloudscraper.create_scraper()
    html = scraper.get(url).content
    dfs = pd.read_html(html)

    if len(dfs) > 0:
        df = dfs[0]
    else:
        print("데이터를 찾을 수 없습니다.")
        return None

    df = df.drop(columns=["Change %"])
    df = df.rename(columns={"Vol.": "Volume", "Price": "Close"})
    df["Volume"] = df["Volume"].apply(convert)
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
    df.set_index("Date", inplace=True)

    data = pd.read_csv(ticker_name + ".csv", index_col="Date")
    data.index = pd.to_datetime(data.index)

    merged_data = pd.concat([data, df])

    for col in ["Open", "High", "Close", "Low"]:
        merged_data[col] = pd.to_numeric(
            merged_data[col].astype(str).str.replace(",", ""), errors="coerce"
        )

    # Remove duplicates if any.
    merged_data = merged_data.loc[~merged_data.index.duplicated(keep="first")]

    # Sort the dataframe based on date.
    merged_data.sort_index(inplace=True)
    merged_data.index = data.index.astype(str)
    # Save to csv.
    merged_data.to_csv(ticker_name + ".csv", index=True)

    return merged_data


def country_output(ticker_name):
    data = pd.read_csv(ticker_name + ".csv").dropna()
    data.index = pd.to_datetime(data["Date"])

    output = {}

    output["previous_close"] = "{:,.2f}".format(data.iloc[-1]["Close"])
    output["today_open"] = "{:,.2f}".format(data.iloc[-1]["Open"])
    output["today_volume"] = "{:,.2f}".format(data.iloc[-1]["Volume"])
    output["avg_volume"] = "{:,.0f}".format(data["Volume"].mean())

    last_row = data.iloc[-1]
    today_range = (
        "{:,.2f}".format(last_row["Low"]) + " - " + "{:,.2f}".format(last_row["High"])
    )
    output["range_days"] = today_range

    last_year_data = data.last("52W")
    year_range = (
        "{:,.2f}".format(last_year_data["Low"].min())
        + " - "
        + "{:,.2f}".format(last_year_data["High"].max())
    )
    output["range_52"] = year_range

    output["MA_50"] = round(data["Close"].rolling(window=50).mean().iloc[-1], 1)
    output["MA_200"] = round(data["Close"].rolling(window=200).mean().iloc[-1], 1)

    return output


def group_output(ticker_name):
    data = pd.read_csv(ticker_name + ".csv").dropna()
    data.index = pd.to_datetime(data["Date"])

    output = {}

    output["previous_close"] = "{:,.2f}".format(data.iloc[-1]["Close"])
    output["today_open"] = "{:,.2f}".format(data.iloc[-1]["Open"])
    output["today_volume"] = "{:,.2f}".format(data.iloc[-1]["Volume"])
    output["avg_volume"] = "{:,.0f}".format(data["Volume"].mean())

    last_row = data.iloc[-1]
    today_range = (
        "{:,.2f}".format(last_row["Low"]) + " - " + "{:,.2f}".format(last_row["High"])
    )
    output["range_days"] = today_range

    last_year_data = data.last("52W")
    year_range = (
        "{:,.2f}".format(last_year_data["Low"].min())
        + " - "
        + "{:,.2f}".format(last_year_data["High"].max())
    )
    output["range_52"] = year_range

    output["MA_50"] = round(data["Close"].rolling(window=50).mean().iloc[-1], 1)
    output["MA_200"] = round(data["Close"].rolling(window=200).mean().iloc[-1], 1)

    tick = yf.Ticker(ticker_name)

    output["Beta"] = tick.info["beta"]

    num = tick.info["enterpriseValue"]
    if num >= 10**12:  # 천억 이상
        output["enterprise"] = str(round(num / 10**12, 2)) + "T"
    elif num >= 10**8:  # 백만 이상
        output["enterprise"] = str(round(num / 10**8, 2)) + "M"
    else:
        output["enterprise"] = str(num)

    output["Buy"] = tick.info["bid"]
    output["Sell"] = tick.info["ask"]

    return output
