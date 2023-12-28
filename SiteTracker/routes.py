from datetime import timedelta,datetime
import os
import ipdb
import string
import random
import status
from threading import Timer
from flask import jsonify, make_response,render_template, url_for, redirect, request, make_response, flash
import bcrypt

import jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request

from SiteTracker.forms import RegistrationForm, LoginForm
from SiteTracker.utility import reactivate_user, save_data_register, load_dotenv, fetch_login_data, deactivate_user_function, fetchsalt, email_taken_check, encode_email, decode_email, hashpassword, send_mail
from SiteTracker.validations import validate_register
from SiteTracker.forget_password import link_datetime_validy,update_password,get_forget_password_hash,save_forget_password_details
from SiteTracker.forget_password import link_expire_hours
from SiteTracker import app

jwt_token_expire_hours=int(os.getenv('JWT_TOKEN_EXPIRE_HOURS'))
reactivate_account_after=int(os.getenv('REACTIVATE_ACCOUNT_AFTER')
)
@app.route('/home')
@app.route('/')
def home():
    res=make_response(render_template('home.html'))
    return res

'''
--> API to register user 
'''
@app.route('/sign-up',methods=['GET','POST'])
def sign_up():
    form=RegistrationForm()
    if(request.method=='POST'):
        try:
            username=request.form.get("username")
            username=" ".join([name.strip().capitalize() for name in username.split(' ')])
            email=request.form.get("email").lower()
            password=request.form.get("password")
            print(f'Username\t: {username}\nEmail\t: {email}\nPassword\t: {password}')
            salt=bcrypt.gensalt()
            # print(len(salt.decode()[:10]))
            salt=salt.decode()[:10]
            create_datetime_value=datetime.now()
            updated_datetime_value=datetime.now()
            isactive_value=True
            result=validate_register(username,email,password)
            if result==True:
                hashed_password=hashpassword(password.encode(),salt.encode())
                save_data_register(username,email,hashed_password,salt,create_datetime_value,updated_datetime_value,isactive_value)
                # return make_response({'message':'User Registeration successfull','data':request.form},status.HTTP_201_CREATED)
                return redirect(url_for('log_in'))
        except Exception as ex:
            flash(str(ex),'danger')
            return(redirect(url_for('sign_up')))
            # return make_response({'error':str(ex)},status.HTTP_400_BAD_REQUEST)
    else:
        return render_template('sign-up.html',form=form)

@app.route('/log-in',methods=['POST','GET'])
def log_in():
    form=LoginForm()
    try:
        verify_jwt_in_request()
        if get_jwt_identity():
            flash('User already logged in','warning')
            return redirect(url_for('home'))
    except Exception as ex:
        pass
    if(request.method=='POST'):
        try:
            email=request.form.get("email").lower()
            password=request.form.get("password")
            if(email_taken_check(email)):
                emailid=str(email)
                (user_id,isactive_status,password_fetched,salt_fetched)=fetch_login_data(emailid)
                
                password_user=hashpassword(password.encode(),salt_fetched.encode())
                if password_user==password_fetched:
                    #condition to check if the user is deactivated
                    if isactive_status==0:
                        th=Timer(reactivate_account_after*60*60, reactivate_user, [user_id])
                        th.start()
                        return make_response({'message':f'Your account is deactivated! We will be activating it within {reactivate_account_after} hours'},status.HTTP_404_NOT_FOUND)
                    
                    user_jwt_token=create_access_token(identity=user_id,expires_delta=timedelta(hours=jwt_token_expire_hours))
                    # res=make_response({'message':'Congratulations, login successfull!','access_token':user_jwt_token,'status':status.HTTP_200_OK})
                    res=redirect(url_for('home'))
                    res.set_cookie('access_token_cookie', user_jwt_token)
                    return res
                else:
                    raise Exception('Wrong Password!!!!')
                    # return make_response({'msg':'Wrong Password!!!!','status':status.HTTP_401_UNAUTHORIZED},status.HTTP_401_UNAUTHORIZED)
            else:
                raise Exception('No such account exists!!')
                # return make_response({'error':'No such account exists!!','status':status.HTTP_404_NOT_FOUND},status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            flash(str(ex),'danger')
            # return make_response({'error':str(ex),'status':status.HTTP_400_BAD_REQUEST},status.HTTP_400_BAD_REQUEST)
    return render_template('log-in.html',form=form)

'''
--> API to deactivate the user account
--> Sets is active status to 0
'''
@app.route('/deactivate-account',methods=['DELETE','GET'])
@jwt_required()
def deactivate_account():
    try:
        current_user_id=get_jwt_identity()
        result=deactivate_user_function(current_user_id)
        if result:
            res=make_response({'message':'Account Deactivation Successfull!'},status.HTTP_200_OK)
            res.set_cookie('access_token_cookie',"")
            return res
    except Exception as ex:
        return make_response({'error':str(ex)},status.HTTP_400_BAD_REQUEST)

'''
This API will be triggered when a user clicks the forget password button
Input Parameters:- email address(proper email fomat eg : rishibha.lakhanpal@drishinfo.com)
Output:- A mail will be sent to the user along with the link where he or she can reset the password
'''
@app.route('/forgot_password',methods=['POST',"GET"])
def forgot_password():
    if request.method=='POST':
        email=request.form.get("email")
        print(email)
        if(email_taken_check(email)):
            forgot_password_hash=''.join(random.choices(string.ascii_letters+string.digits,k=6))
            encoded_email=encode_email(email)
            decoded_email=decode_email(encoded_email)
            link=request.host_url+"/reset_password/"+str(encoded_email)+"/"+forgot_password_hash
            message=f'Hello sir,\n\nAs per your request, please click on the link below to reset your password \n{link}\n\nThe link is valid for {link_expire_hours} hours.\n\n\nRegards,\nDrish Ping Reporter,\nDrish Infotech ltd'
            forget_password_datetime=datetime.now()
            save_forget_password_details(decoded_email,forgot_password_hash,forget_password_datetime)
            x=1
            x=send_mail(email,message)
            if x:
                return make_response({'message':'The link for password reset has been sent to your email address!','link':link},status.HTTP_200_OK)
            else:
                return make_response({'error':'Wasnt able to send link'},status.HTTP_404_NOT_FOUND)
        else:
            return make_response({'error':'This mail is not registered with us!'})
    elif request.method=='GET':
        return render_template('forgot_password.html')
    else:
        return make_response({'error':'method not allowed'},status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route('/reset_password/<encoded_email>/<forgot_password_hash>',methods=['GET'])
def generate_email_forget_password(encoded_email,forgot_password_hash):
    if request.method=='GET':
        try:
            encoded_email_from_url=encoded_email
            forgot_password_hash_from_url=forgot_password_hash
            decoded_email=decode_email(encoded_email_from_url)
            if(link_datetime_validy(decoded_email) is False): # i.e the if the link is not valid according to time
                raise Exception('Then link has expired please generate another link to continue')
            if(email_taken_check(decoded_email)):
                forgot_password_hash_from_db=get_forget_password_hash(decoded_email)
                if(forgot_password_hash_from_db==forgot_password_hash_from_url):
                    return redirect(f'/reset_password/{encoded_email}')
                    # return make_response({'email':decoded_email,'encoded email':encoded_email,'Message':'success'},status.HTTP_202_ACCEPTED)
                else:
                    raise Exception('The link is not valid')
                    # return make_response({'error':'The link is not valid'})
            else:
                raise Exception('Invalid link. Please check again!')
                # return make_response({'error':'Invalid link. Please check again!'},status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            flash(str(ex),'danger')
            return redirect(url_for('log_in'))
            # return make_response({'error':str(ex)},status.HTTP_400_BAD_REQUEST)


@app.route('/reset_password/<encoded_email>',methods=['POST','GET'])
def reset_password(encoded_email):
    if request.method=='POST':
        try:
            update_password_val=request.form.get('password')
            decoded_email=decode_email(encoded_email)
            (_,_,previous_password,salt_fetched)=fetchsalt(decoded_email)
            #checking if the previous and new password matches by fetching the previous salt
            hashed_update_password=hashpassword(update_password_val.encode(),salt_fetched.encode())
            if( hashed_update_password==previous_password):
                return make_response({'error':'new password cannot be the same as previous one'},status.HTTP_401_UNAUTHORIZED)
            #need to remove 'result=1' statement on code completion
            result=1
            # result=validate_password(update_password_val)
            if result:
                salt=bcrypt.gensalt().decode()[:10]
                #new hashed update password with newly generated salt
                hashed_update_password=hashpassword(update_password_val.encode(),salt.encode())
                update_password_success_status=update_password(decoded_email,hashed_update_password,salt)
                if(update_password_success_status):
                    flash('Password reset successful!','success')
                    return redirect(url_for('log_in'))
                    # return make_response({'message':'Password reset successful!'},status.HTTP_200_OK)
                else:
                    raise Exception('error resetting password!')
                    # return make_response({'error':'error resetting password!'},status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            flash(str(ex),'danger')
            return redirect(f'/reset_password/{encoded_email}')
            # return make_response({"error":str(ex)})
    elif request.method=='GET':
        decoded_email=decode_email(encoded_email)
        print(encoded_email)
        return render_template('reset_password.html',encoded_email=encoded_email)

@app.route('/article-details')
def article_details():
    return render_template('article-details.html')

@app.route('/about',methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/policy')
def policy():
    return render_template('privacy-policy.html')

@app.route('/terms-and-conditions')
def terms_conditions():
    return render_template('terms-conditions.html')

@app.route('/pricing',methods=['GET','POST'])
def pricing():
    return render_template('pricing.html')

@app.route('/id',methods=['GET'])
@jwt_required()
def id():
    user=get_jwt_identity()
    return make_response({'id':user})