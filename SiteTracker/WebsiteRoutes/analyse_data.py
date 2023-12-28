import pandas as pd
from datetime import datetime,date,timedelta,time
from SiteTracker.utility import mydb,mycursor

def get_website_weekly_performance(websiteid):
    try:
        datetime_last_week=datetime.now()-timedelta(days=7)
        datetime_now=datetime.now()
        query=(f"SELECT date_time,status_code,response_time from tracking_table where websiteid='{websiteid}' and date_time between '{datetime_last_week}' and '{datetime_now}'")
        mycursor.execute(query)
        data_fetched=mycursor.fetchall()
        datetime_fetched,status_code_fetched,response_time_fetched=[],[],[]
        for data_groupby_date in data_fetched:
            datetime_fetched.append(data_groupby_date[0])
            status_code_fetched.append(data_groupby_date[1])
            response_time_fetched.append(data_groupby_date[2])
        data_in_tabularform=pd.DataFrame({'Datetime':datetime_fetched,'status_code':status_code_fetched,'response_time':response_time_fetched})
        data_in_tabularform['response_time']=data_in_tabularform['response_time'].apply(pd.to_numeric)
        # print(data_in_tabularform)
        
        datetime_value=data_in_tabularform['Datetime'].values #extracted values from datetime column 
        converted_values=[pd.to_datetime(y) for y in datetime_value]#got the values converted from numpy.datetime to datetime.datetime
        datelist,timelist=[],[] #two empty lists for saving the date and time
        for val in converted_values :
            datelist.append(val.date()) #appending the value of date in datelist
            timelist.append(val.time()) #appending the value of time in timelist
            # print('DATE :'+str(val.date())+'\nTIME :'+str(val.time()))
        data_in_tabularform['date']=datelist #adding column for date
        data_in_tabularform['time']=timelist #added column for time
        # data_in_tabularform.to_csv('website_data'+str(websiteid)+'.csv')
        data_groupby_date=data_in_tabularform.groupby('date')
        print('=='*120)
        df=data_groupby_date.agg({'response_time':['mean'],'status_code':['median']}) # ERROR PRONE IF DATA EMPTY
        
        df.columns=['avg_response_time','status']
        df.reset_index(inplace=True)
        today = date.today()
        x=1
        list_by_days=[]
        while x<8:
            week_ago = today - timedelta(days=x)
            filt=df['date'].astype(str)==str(week_ago)
            row_data=df.loc[filt,['date','avg_response_time','status']] if filt.any() else None
            if(row_data is None):
                x=x+1
                continue
            converted_row_data={
                "date": row_data['date'].astype(str).values[0], 
                "average_response_time": round(row_data['avg_response_time'].values[0],3), 
                "status":int(row_data['status'].values[0])
                }
            list_by_days.append(converted_row_data)
            x+=1
        return list_by_days      
    except Exception as ex:
        raise Exception(str(ex))