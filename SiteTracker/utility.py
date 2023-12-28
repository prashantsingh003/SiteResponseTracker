#this file contains the code that is reuqired in almost all the files or more than an API
import mysql.connector 
import hashlib
import smtplib
import base64,os
from dotenv import load_dotenv
load_dotenv()
from SiteTracker.utility import load_dotenv
mydb=mysql.connector.connect(host=os.getenv("DATABASE_HOST"),port=os.getenv("DATABASE_PORT"),passwd=os.getenv("DATABASE_PASSWORD"),user=os.getenv("DATABASE_USER"),database=os.getenv("DATABASE_NAME"))
mycursor=mydb.cursor(buffered=True)

sender_email=os.getenv("SENDER_EMAIL")
sender_password=os.getenv("SENDER_PASSWORD")
send_email_server_domain=os.getenv("SEND_EMAIL_SERVER_DOMAIN")
send_email_server_port=os.getenv("SEND_EMAIL_SERVER_PORT")

'''function for saving information regarding a new user into the database'''
def save_data_register(fullname,email,password,salt,registerationdate,updatedate,isactive):
        try:
                insert_statement=(
                        "INSERT INTO user_table (full_name,email,user_password,salt,create_datetime,update_datetime,is_active)" 
                        "VALUES(%s,%s,%s,%s,%s,%s,%s)"
                        )
                input_data=(fullname,email,password,salt,registerationdate,updatedate,isactive)
                mycursor.execute(insert_statement,input_data)
                mydb.commit()
                print('data saved')                     
        except Exception as ex:
                raise Exception(str(ex))

def fetch_login_data(emailid):
        try:
                fetch_statement=(f"SELECT user_id,is_active,user_password,salt from user_table where email='{emailid}'" )
                mycursor.execute(fetch_statement)
                fetched_data=mycursor.fetchone()
                return fetched_data
        except Exception as ex:
                raise Exception(str(ex))

def deactivate_user_function(userid):
        try:
                isactive_value=0
                userid_value=userid
                update_statement=(
                        f"UPDATE  user_table SET is_active = '{isactive_value}' WHERE user_id = '{userid_value}';"
                )
                mycursor.execute(update_statement)
                mydb.commit()
                return True
        except Exception as ex:
                raise Exception(str(ex))

def reactivate_user(user_id):
        try:
                isactive_value=1
                userid_value=user_id
                update_statement=(
                        f"UPDATE  user_table SET is_active = '{isactive_value}' WHERE user_id = '{userid_value}';"
                )
                mycursor.execute(update_statement)
                mydb.commit()
                print('user reactivated')
                return True
        except Exception as ex:
                raise Exception(str(ex))

'''function for fetching the salt from the database'''
def fetchsalt(email):
        try:    
                emailid=str(email)
                fetch_statement=(f"SELECT user_id,is_active,user_password,salt from user_table where email='{emailid}'" )
                fetch_statement1=(fetch_statement)
                mycursor.execute(fetch_statement1)
                fetched_salt=mycursor.fetchone()
                # print('fetched salt',fetched_salt)
                if fetched_salt is None:
                        raise Exception('No such Account exists!!!')
                return fetched_salt
        except Exception as ex:
                raise Exception(str(ex))

'''This function checks if the email is already registered or exists in the database'''
def email_taken_check(email):
        try:
                select_statement=("SELECT DISTINCT email from user_table" )
                mycursor.execute(select_statement)
                fetched_data=mycursor.fetchall()
                #print('email fetched data--->',fetched_data)
                email_taken_list=[]
                for data in fetched_data:
                        email_taken_list.append(data[0])
                # print('email taken list-->',email_taken_list)
                if email in email_taken_list:
                        return True
                else:
                        return False
        except Exception as ex:
                raise Exception(str(ex))

'''This function is mainly associated with hashing the password with respective salt and returning the hashed password'''            
def hashpassword(password,salt):
    hashed_password=hashlib.md5(password+salt)
#     print(hashed_password.hexdigest())
    return hashed_password.hexdigest()

'''this function is used to encode email, mainly used in forgot password API'''
def encode_email(email):
    try:
        message = email
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes).strip()
        # print('base 64 bytes ',base64_bytes)
        base64_message = base64_bytes.decode('ascii')
        # print('base 64 message',base64_message)
        return base64_message
    except Exception as ex:
        print('exception here encode email function')
        raise Exception(str(ex))

'''This functiom is used to decode the email,mainly used in forget password API'''    
def decode_email(email_encoded):
    try:
        # print('decode email')
        email_decoded=base64.b64decode(email_encoded).decode()
        # print('decoded email',email_decoded)
        return email_decoded
    except Exception as ex:
        raise Exception(str(ex))
    
'''Function to fetch email from user id'''
def fetch_user_email(user_id):
        try:
                query=(f"SELECT email from user_table where user_id='{user_id}'")
                mycursor.execute(query)
                email=mycursor.fetchall()
                return email[0][0]
        except Exception as ex:
                raise Exception(str(ex))

# def get_email_name():
#     try :
#         query=("SELECT user_id,full_name,email from user_table")
#         mycursor.execute(query)
#         fetched_data=mycursor.fetchall()
#         userids=[]
#         usernames=[]
#         user_emails=[]
#         for data in fetched_data:
#             userids.append(data[0])
#             usernames.append(data[1])
#             user_emails.append(data[2])
#         return userids,usernames,user_emails        
#     except Exception as ex:
#         print(str(ex))

'''Functon to fetch all userid that are registered for a website'''
def get_email_from_websiteid(websiteid):
        try:
                query=(f"SELECT DISTINCT userid from website_user_map where websiteid='{websiteid}' and is_active=1")
                mycursor.execute(query)
                userids=mycursor.fetchall()
                return [x[0] for x in userids]
        except Exception as ex:
                raise Exception(str(ex))
'''This is used to send the email along with the link when user request for password resetting'''
def send_mail(email,message):
        try:
                with smtplib.SMTP(send_email_server_domain,send_email_server_port) as server:
                        server.ehlo()
                        server.starttls()
                        server.ehlo()
                        server.login(sender_email,sender_password)
                        server.sendmail(sender_email,email,message)
                        print('email sent')
                return True
        except Exception as ex:
                raise Exception(str(ex))