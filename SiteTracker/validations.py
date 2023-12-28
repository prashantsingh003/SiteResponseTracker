import re
from SiteTracker.utility import email_taken_check

'''This function is used to validate password'''        
def validate_password(password):
        if not len(password.strip()):
            raise Exception('Password is required')
        if re.match('^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$',password):
                print('valid password') 
                return True
        else:
                raise Exception('Invalid Password!!your password must contain at least one charachter each:- a)uppercase b)lowercase c)Special charachter d)digit')


def validate_email(email):
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if not len(email.strip()):
                raise Exception('Email is required!')
        if not re.fullmatch(regex,email):
                raise Exception('Please enter a valid email')

'''This function is used to validate full name'''
def validate_name(fullname):
    try:
        if not len(fullname.strip()):
            raise Exception('Full name is required!')
        if not re.match("^[a-zA-Z]{3,}(?: [a-zA-Z]+){0,2}$",fullname):
               raise Exception('Fullname not valid') 
    except Exception as ex:
        raise Exception(str(ex))

'''This function is used to validate fullname, emailaddress, password and then this function calls validation function for all the individual paramaters'''
def validate_register(fullname,emailaddress,password):
        try:
                validate_name(fullname)                  
                validate_email(emailaddress)
                result=email_taken_check(emailaddress)
                if result:
                        raise Exception('Email Already Registered')
                result=validate_password(password)
                if result:
                        print('password valid')
                        return True
              
        except Exception as ex:
                raise Exception(str(ex))