#! /usr/bin/env python

from dca import get_trade_history
from settings import BITFLYER_API_KEY, BITFLYER_API_SECRET
import pandas as pd
from pathlib import Path


def main():
    res = get_trade_history(BITFLYER_API_KEY, BITFLYER_API_SECRET).json()
    df = pd.DataFrame(res)
    #path = Path.home()
    path = Path.home() / 'project' / 'bitFlyer-dca/data' / '2020_trade_history.csv'
    df.to_csv(path, index=False) 

if __name__ == '__main__':
    main()