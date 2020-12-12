# -*- coding: utf-8 -*-
import datetime
from datetime import datetime as dt
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import glob
import requests
import yaml
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import os
import matplotlib as mpl
import matplotlib.pyplot as plt

# main
def main(args):

    with open(args[1], 'r', encoding="utf-8") as yml:
        config = yaml.load(yml)

    # set data dir
    data_dir = config['data_dir']
    f_out0 = os.path.join(data_dir, 'all.csv' )

    # set start and end date
    sdate = config['start_date']; edate = config['end_date']
    sdate = dt.strptime(sdate, '%Y-%m-%d')
    edate = dt.strptime(edate, '%Y-%m-%d')

    # set obs_list
    obs_list = config['obs_id']

    # set data frame
    data = pd.DataFrame()
    for item in obs_list:

        # set url0
        print('<--- ' , item[1], ' --->')
        url0 = config['url'] + item[0]

        # set series
        ss = pd.Series()

        # set date
        dd = sdate
        while dd < edate + datetime.timedelta(days=1):
            #set url
            dd1 = dd + relativedelta(months=1) - datetime.timedelta(days=1)
            url = url0 + '&BGNDATE=' + dd.strftime('%Y') + dd.strftime('%m') + dd.strftime('%d') \
                    + '&ENDDATE=' + dd1.strftime('%Y') + dd1.strftime('%m') + dd1.strftime('%d') \
                    + '&KAWABOU=NO'
            print(url)

            # set output file name
            f_out = os.path.join(data_dir, item[0] + '_' \
                                    + dd.strftime('%Y') \
                                    + dd.strftime('%m') \
                                    + '.csv' )

            # set data frame
            df = pd.DataFrame(index=[], columns=range(1, 25))

            # get html data
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "lxml")
            table = soup.findAll("table")[1]
            rows = table.findAll("tr")
            icount = 0
            for row in rows:
                if icount < 2:
                    icount = icount + 1
                    continue

                qq = []
                for cell in row.findAll(["font"]):
                    qq.append(cell.get_text())

                # add data into the dataframe
                df.loc[qq[0]] = qq[1:25]
                
            #  replace no data
            df = df.replace("欠測", "0")
            df = df.astype('float64')
            #print(df.dtypes)
            
            #output csv
            if config['csv_save'] == True:
                df.to_csv(f_out)

            # transform data from 2d to 1d and concat
            ss = pd.concat([ss, df.stack()])

            # update date
            dd = dd + relativedelta(months=1)

        # add series into dataframe
        data[item[1]] = ss
        #print(data)

    # output all data
    if config['all_csv_save'] == True:
        data.to_csv(f_out0)

    #draw
    #data = data.reset_index(drop=True)
    data = data.reset_index()
    plt.figure()
    data.plot()

    # save figure?
    if config['all_fig_save'] == True:
        plt.savefig( data_dir + '/all.png')

    # show
    #plt.show() 

    # close
    plt.close('all')
    

    return 0

#root
if __name__ == "__main__":
    import sys
    args = sys.argv
    main(args)
