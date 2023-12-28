from datetime import datetime,timedelta
from turtle import pensize
from flask import make_response
from SiteTracker.utility import mycursor,mydb  
import pandas as pd

'''Function used to register a new website to the website table'''      
def save_website(url,create_datetime,update_datetime,is_active):
   try:
      insert_statement=(
                        "INSERT INTO website_table(website_url,create_datetime, update_datetime,is_active)"
                                "VALUES(%s,%s,%s,%s)"
                                )
      input_data=(url,create_datetime,update_datetime,is_active)
      mycursor.execute(insert_statement,input_data)
      mydb.commit()
      return True
   except Exception as ex:
      raise Exception(str(ex))
            
'''This function is used to fetch website if from website table'''
def fetch_website_id(url_value_parameter):
   try:
      url_value=url_value_parameter
      #needs to be verified
      fetch_statement=(f"SELECT website_id from website_table where website_url='{url_value}'")
      mycursor.execute(fetch_statement)
      website_id_fetched=mycursor.fetchone()
      if website_id_fetched is None:
         return None
      else:
            # print('fetched user id')
            # print(website_id_fetched[0])
            return website_id_fetched[0]
   except Exception as ex:
      raise Exception("Problem in fetching data!!Try again later!")

'''
Function to check if the relation pre-exists in a table or not
'''
def user_website_relation_status(user_id,website_id):
    try:
        get_statement=(f"SELECT is_active from website_user_map WHERE websiteid={website_id} and userid= {user_id}")
        mycursor.execute(get_statement)
        active_status=mycursor.fetchone()
        if(active_status):
            print(active_status[0])
            return True,True if active_status[0]==1 else False
        return False,False
    except Exception as ex:
        raise Exception(str(ex))

'''
Function to get status of the user website relation
'''
def get_user_website_relation_status(user_id,website_id):
    try:
        set_statement=(f"Select is_active from website_user_map WHERE websiteid={website_id} and userid= {user_id}")
        mycursor.execute(set_statement)
        status=mycursor.fetchone()
        return True if status[0]==1 else False
    except Exception as ex:
        raise Exception(str(ex))

def check_userid_websiteid_relation(userid,websiteid):
    try:
        query=(f"SELECT websiteid from website_user_map where userid={userid}")
        mycursor.execute(query)
        fetched_id=mycursor.fetchall()
        for d in fetched_id:
            # print(d[0])
            if d[0]==websiteid:
                return True
        return False
    except Exception as ex:
        return make_response({'error':str(ex)})

'''
Function to change status of the user website relation
'''
def set_user_website_relation_status(user_id,website_id,status):
    try:
        set_statement=(f"Update website_user_map SET is_active={status} WHERE websiteid={website_id} and userid= {user_id}")
        mycursor.execute(set_statement)
        mydb.commit()
        return True
    except Exception as ex:
        raise Exception(str(ex))

'''This function is used to add a relationship between the user and the website in the website user map table'''
def savedata_website_user_map(websiteid,userid,role,createdatetime,updatedatetime,isactive,donotify):
    try:
        insert_statement=("INSERT INTO website_user_map(websiteid,userid,user_role,update_datetime,create_datetime,is_active,do_notify) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s)"
                )
        input_data=(websiteid,userid,role,createdatetime,updatedatetime,isactive,donotify)
        mycursor.execute(insert_statement,input_data)
        mydb.commit()
        return True
    except Exception as ex:
        raise Exception(str(ex))

'''Function used to get website id and website url from user id'''        
def get_websites_linked_with_user(userid):
        sql_statement=(f"SELECT website_user_map.websiteid, website_table.website_url FROM website_table INNER JOIN website_user_map ON website_table.website_id=website_user_map.websiteid WHERE website_user_map.userid='{userid}' and website_user_map.is_active='{True}'")
        mycursor.execute(sql_statement)
        fetched_data=mycursor.fetchall()
        print(fetched_data)
        websiteids=[]
        website_urls=[]
        for data in fetched_data:
            websiteids.append(data[0])
            website_urls.append(data[1])
        return websiteids,website_urls
            
'''checks if url that is to be updated'''               
def check_url_exists_db(website_url):
    try:
        fetch_statement=("SELECT website_id,website_url from website_table")
        mycursor.execute(fetch_statement)
        fetched_website_info=mycursor.fetchall()
        for data in fetched_website_info:
            website_id,url=(data[0],data[1])
            if url==website_url:
                return website_id
        return False
    except Exception  as ex:
                raise Exception(str(ex))

'''This function is used to update the website id inside the website user map table'''        
def update_website_user_map(websiteid_param,userid_param,websiteid_previous_param):
    try:
        update_statement=(f"UPDATE website_user_map SET websiteid='{websiteid_param}' WHERE userid='{userid_param}' AND websiteid='{websiteid_previous_param}'")
        mycursor.execute(update_statement)
        mydb.commit()
        return True
    except Exception as ex:
        raise Exception(str(ex))
        
'''This function is for updating the url in the website_table'''
def update_website_url(websiteid,url):
    try:
        updatetime=datetime.now()
        update_statement=(f"UPDATE website_table SET website_url='{url}'and update_datetime='{updatetime}' where website_id='{websiteid}'")
        mycursor.execute(update_statement)
        return True
    except Exception as ex:
       raise Exception('Unable to update data')

# '''This function is used to mark website inactive in the user map table'''        
# def remove_website_user_map(userid,websiteid):
#     try:
#         isactive_state=False
#         update_statement=(f"UPDATE website_user_map SET is_active='{isactive_state}' where websiteid='{websiteid}' and userid='{userid}'")
#         mycursor.execute(update_statement)
#         print('updated website url in website table')
#     except Exception as ex:
#         raise Exception('Unable to remove website')
   

'''
--> Function to get the list of website data related to a user
'''
def get_user_urls(user_id):
    try:
        fetch_statement=f'''
        select websiteid,user_role, wt.is_active, wum.do_notify, wt.website_url
        from website_user_map as wum 
        inner join website_table as wt on wt.website_id=wum.websiteid
        where userid='{user_id}' and wum.is_active=1
        '''
        mycursor.execute(fetch_statement)
        fetched_data=mycursor.fetchall()
        res=[]
        for data in fetched_data:
            res.append({'id':data[0],'url':data[4],'role':data[1],'active':True if data[2]==1 else False,'notify':True if data[3]==1 else False})
        return res
    except Exception as ex:
        raise Exception(str(ex))


def get_website_details(userid):
    try:
        isactive=1
        fetch_statement=(f"SELECT DISTINCT tracking_table.date_time, tracking_table.response_time,tracking_table.status_code FROM tracking_table INNER JOIN website_user_map ON tracking_table.websiteid=website_user_map.websiteid WHERE website_user_map.userid='{userid}' and website_user_map.is_active='{isactive}'")
        mycursor.execute(fetch_statement)
        data_fetched=mycursor.fetchall()
        print('websit details dashboard')
        # print(data_fetched)
                # print(data_fetched[0])
        listofdata_fetched=[]
        for data in data_fetched:
            # print('------------')
            # print(data)
            listofdata_fetched.append(data)
        # print(listofdata_fetched)
        return listofdata_fetched
    except Exception as ex:
        raise Exception(str(ex))
# get_website_details(2)


'''This function is used to get the list of URLs of all the websites marked with isactive status'''        
def get_url_list():
    try:
        isactive_status=1
        query=(f"SELECT website_url from website_table where is_active='{isactive_status}'")
        mycursor.execute(query)
        data_fetched=mycursor.fetchall()
        if data_fetched is None:
            return False
        listofurls=[]
        for data in data_fetched:
            listofurls.append(data[0])
        return listofurls
    except Exception as ex:
        raise Exception(str(ex))

'''This function is used to get the detailed daily performance of the website based on the data that was fetched in the report API'''
def get_website_performance_daily(data_fetched):
    try:
        datetime_fetched,status_code_fetched,response_time_fetched=[],[],[]
        print(data_fetched)
        for data in data_fetched:
            print(data[0])
            datetime_fetched.append(data[0])
            response_time_fetched.append(data[1])
            status_code_fetched.append(data[2])
        print(response_time_fetched)
        data_in_tabularform=pd.DataFrame({'Datetime':datetime_fetched,'status_code':status_code_fetched,'response_time':response_time_fetched})
        print('groupby datetime')
        import datetime as dt
        data_in_tabularform['year']=data_in_tabularform['Datetime'].dt.year
        data_in_tabularform['month']=data_in_tabularform['Datetime'].dt.month
        data_in_tabularform['date']=data_in_tabularform['Datetime'].dt.day
        data_in_tabularform['hour']=data_in_tabularform['Datetime'].dt.hour
        data_in_tabularform['minute']=data_in_tabularform['Datetime'].dt.minute
        data_in_tabularform.drop(['Datetime'],inplace=True,axis=1)
        data_in_tabularform.to_csv('website_data'+str(121)+'.csv')
        average_reponse_time=data_in_tabularform.groupby(['date']).response_time.mean()
        print(average_reponse_time)
        
        
    except Exception as ex:
        raise Exception(str(ex))
        
'''Function for scheduler to save website response data to tracking_table'''
def save_website_tracking(statuscode,responsetimeparam,websiteid):
    current_datetime=datetime.now()
    insert_statement=("INSERT INTO tracking_table(date_time,websiteid,status_code,response_time)"
                      "VALUES(%s,%s,%s,%s)")
    input_val=(current_datetime,websiteid,str(statuscode),str(responsetimeparam))
    # print('input_val-->',input_val)
    mycursor.execute(insert_statement,input_val)
    # print('executed')
    mydb.commit()
    # print('saved')

def get_website_list(userid):
    try:
        isactive=1
        fetch_statement=(f"SELECT DISTINCT website_url,website_id from website_table  INNER JOIN website_user_map ON website_table.website_id=website_user_map.websiteid WHERE website_user_map.userid='{userid}' and website_user_map.is_active='{isactive}'")
        mycursor.execute(fetch_statement)
        data_fetched=mycursor.fetchall()
        print('websit details dashboard')
        print(data_fetched)
                # print(data_fetched[0])
        listofdata_fetched=[]
        for data in data_fetched:
            # print('------------')
            # print(data)
            listofdata_fetched.append(data[0])
        # print(listofdata_fetched)
        if len(listofdata_fetched):
            return listofdata_fetched
        else:
            return False
    
    except Exception as ex:
        raise Exception(str(ex))

def get_notify_status(user_id,website_id):
    try:
        fetch_statement=(f"Select do_notify from website_user_map where userid={user_id} and websiteid={website_id}")
        mycursor.execute(fetch_statement)
        notify_status=mycursor.fetchone()
        notify_status=int(notify_status[0])
        if notify_status != 0:
            return True
        else:
            return False
    except Exception as ex:
        raise Exception(str(ex))

def toggle_notify_status(user_id,website_id):
    try:
        notify_status=get_notify_status(user_id,website_id)
        update_statement=f'update website_user_map set do_notify={not notify_status} where userid={user_id} and websiteid={website_id}'
        mycursor.execute(update_statement)
        mydb.commit()
    except Exception as ex:
        raise Exception(str(ex))        