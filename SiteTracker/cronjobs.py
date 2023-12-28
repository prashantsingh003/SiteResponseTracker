import requests, os
import pandas as pd
from datetime import datetime,timedelta
from flask import request
import concurrent.futures
from SiteTracker.utility import get_email_from_websiteid,mycursor,mydb,fetch_user_email, send_mail
from SiteTracker.WebsiteRoutes.websites_util import fetch_website_id, get_url_list, save_website_tracking
from apscheduler.schedulers.background import BackgroundScheduler

max_threads=int(os.getenv('MAX_THREADS'))
scheduler_max_instances=int(os.getenv('APSCHEDULER_MAX_INSTANCES'))

scheduler=BackgroundScheduler({'apscheduler.job_defaults.max_instances': scheduler_max_instances,'timezone':'Asia/Kolkata'})

free_plan_interval=int(os.getenv('FREE_PLAN_INTERVAL_SECONDS'))
inactivity_check_interval_hours=int(os.getenv('INACTIVITY_CHECK_INTERVAL_HOURS'))
error_response_percentage_threshold=float(os.getenv('ERROR_RESPONSE_PERCENTAGE_THRESHOLD'))

'''function for getting the status of the respective url . This function takes as input a list of urls'''
def check_status(url):
    try:
        headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': '*/*',
        'Origin': '*',
        'Referer': '*'
        }
        response=requests.get(url,headers=headers,timeout=30)
        # print(response.status_code,'status code <---<')
        if response:
            response_time=response.elapsed.total_seconds()
            return response.status_code,response_time      
    except Exception as ex:
        print('*****************\nException\n***********************')
        raise Exception(str(ex))

def alert_users(website_id):
    user_id_list=get_email_from_websiteid(website_id)
    user_email_list=list(map(fetch_user_email,user_id_list))
    message=f'Hello sir,\n\n Your registered site is not functioning well for the last {inactivity_check_interval_hours} hours.\nIts error response percentage is above {error_response_percentage_threshold}%\n\nRegards,\nDrish Ping Reporter,\nDrish Infotech ltd'
    for email in user_email_list:
        # send_mail(email,message)
        print(f'sent email to {email}')

def record_website_status():
    try:
        site_list=get_url_list()
        if len(site_list)>0:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executer:
                sites_data=list(executer.map(check_status, site_list,timeout=15))
            for url,data in zip(site_list,sites_data):
                fetched_website_id=fetch_website_id(url)
                if data is None:
                    print(f'data for "{url}" not able to fetch')
                    continue
                save_website_tracking(data[0],data[1],fetched_website_id)
                # print(data[0],data[1],fetched_website_id)
        else:
            print('no data found in the lists')
    except Exception as ex:
        raise Exception(str(ex))

def check_website_inactivity():
    datetime_from=datetime.now()-timedelta(hours=inactivity_check_interval_hours)
    datetime_now=datetime.now()
    try:
        query=(f"SELECT websiteid,status_code from tracking_table where date_time between '{datetime_from}' and '{datetime_now}'")
        mycursor.execute(query)
        data_fetched=mycursor.fetchall()

        #FETCHED DATA from database to PYTHON PANDAS DATAFRAME
        df=pd.DataFrame(data_fetched,columns=['website_id','response_status'])
        grouped_website_df=df.groupby(['website_id'])

        #NEW VARIABLES TO STORE TOTAL RESPONSES AND NUMBER OF POSITIVE/GOOD RESPONSES
        total_responses=df['website_id'].value_counts()
        error_response=grouped_website_df['response_status'].apply(lambda x:x.str.startswith('2').sum()).astype(int)

        #CREATING NEW DATAFRAME CONSISTING TOTAL RESPONSES, ERROR RESPONSES
        evaluated_df=pd.concat([total_responses,error_response],axis='columns')

        #RENAMING COLUMNS AND REMOVING INDEX NAMING INDEX COLUMN AS WEBSITE ID
        evaluated_df.reset_index(inplace=True)
        evaluated_df.rename(columns={'website_id':'total_responses','response_status':'error_response','index':'website_id'},inplace=True)

        #CONVERTING GOOD RESPONSES VALUES TO ERROR RESPONSES VALUE
        evaluated_df['error_response']=abs(evaluated_df['total_responses']-evaluated_df['error_response'])

        #NEW COLUMN FOR ERROR RESPONSE PERCENTAGE
        evaluated_df['error_response_percentage']=(evaluated_df['error_response']/evaluated_df['total_responses'])*100

        #FILTER TO GET DATA THAT IS HAVING ERROR RESPONSE GREATER THAN DESIRED
        filt=evaluated_df['error_response_percentage']>error_response_percentage_threshold

        #SENDING WEBSITE ID TO THE send alert FUNCTION WHERE ERROR RESPONSE IS GREATER THAN DESIRED
        evaluated_df.loc[filt,['website_id']].apply(alert_users,axis='columns')
    except Exception as ex:
        print()
        print('**********EXCEPTION**********')
        print(ex)


def start():
    scheduler.add_job(func=record_website_status,id='site_status_recorder', trigger= 'interval',seconds=free_plan_interval)
    scheduler.add_job(func=check_website_inactivity,id='website_inactivity_check', trigger='cron', hour=inactivity_check_interval_hours )
    scheduler.start()