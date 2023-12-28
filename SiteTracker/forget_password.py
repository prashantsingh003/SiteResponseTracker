#this file contains functionality related to forget password API
from SiteTracker.utility import mycursor,mydb,load_dotenv,os
from datetime import datetime
link_expire_hours=int(os.getenv('FORGOT_PASSWORD_LINK_EXPIRE_HOURS'))
'''This function is used to update the user's account with hashed password'''
def save_forget_password_details(emailid,forgetpassword_hash,forgetpassword_date):
    try:
        update_statement= (
            f"UPDATE user_table SET forget_password_hash ='{forgetpassword_hash}',forget_password_datetime='{forgetpassword_date}' WHERE email='{emailid}'"
        )
        mycursor.execute(update_statement)
        mydb.commit()
    except Exception as ex:
        raise Exception(str(ex))

'''function for checking/fetching the password hash'''
def get_forget_password_hash(email):
    email_address_param=email
    print('email address param under get_forget_password_hash------>',email_address_param)
    try:
        fetch_statement=(f"SELECT forget_password_hash from user_table where email='{email_address_param}'")
        mycursor.execute(fetch_statement)
        fetched_forget_password_hash=mycursor.fetchone()
        print(fetched_forget_password_hash[0])
        return fetched_forget_password_hash[0]
    except Exception as ex:
        raise Exception(str(ex))

#this function is used in reset password API, for updating the password field and removing the value of     
def update_password(email,password,salt1):
    try: 
        update_statement=(f"UPDATE user_table SET user_password='{password}',salt='{salt1}'where email='{email}'")
        mycursor.execute(update_statement)
        mydb.commit()
        return True
    except Exception as ex:
        raise Exception(str(ex))
        
# Function to get date time of the creation of forgot password hash
def link_datetime_validy(user_email):
    try:
        query=f"select forget_password_datetime from user_table where email='{user_email}'"
        mycursor.execute(query)
        create_hash_datetime=mycursor.fetchone()
        create_hash_datetime=create_hash_datetime[0]
        current_time=datetime.utcnow()
        enlapsed_time=round( (current_time- create_hash_datetime).total_seconds()/( 60*60 ), 2)
        if enlapsed_time>link_expire_hours:
            return False
        return True
    except Exception as ex:
        raise Exception(str(ex))
    