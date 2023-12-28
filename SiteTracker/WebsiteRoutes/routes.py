from flask import redirect, render_template, request, make_response, flash, url_for
from datetime import datetime, timedelta
import status
from flask_jwt_extended import jwt_required, get_jwt_identity
from SiteTracker.WebsiteRoutes.websites_util import fetch_website_id, get_notify_status, get_user_urls, toggle_notify_status, update_website_user_map, save_website, savedata_website_user_map, check_userid_websiteid_relation, get_user_website_relation_status, set_user_website_relation_status
from SiteTracker.WebsiteRoutes.analyse_data import get_website_weekly_performance
from SiteTracker.forms import AddWebsiteForm
from flask import Blueprint
website=Blueprint("website",__name__,static_folder="static",template_folder="templates")
'''
--> Needs jwt token
--> Checks if the website already exists in the website table
--> Adds the site if exists if not returns error 409
--> Adds data to the user_map_id table 
'''
@website.route('/add',methods=['POST','GET'])
def add_website():
    form=AddWebsiteForm()
    if request.method=='POST':
        try:
            url_value=request.form.get('url')
            create_datetime_value=datetime.now()
            update_datetime_value=datetime.now()
            role_value=request.form.get('role') if request.form.get('role') else 1
            isactive_value=True
            do_notify_value=request.form.get('role') if (request.form.get('role') and request.form.get('role')=='YES') else 1
            @jwt_required()
            def function_test():
                current_user_id=get_jwt_identity()
                website_id=fetch_website_id(url_value)
                if website_id is None:
                    response=save_website(url_value,create_datetime_value,update_datetime_value,isactive_value)
                    if response:
                        fetched_website_id=fetch_website_id(url_value)
                        another_response=savedata_website_user_map(fetched_website_id,current_user_id,role_value,create_datetime_value,update_datetime_value,isactive_value,do_notify_value)
                        if another_response:
                            msg='website added'
                            return True,msg
                else:
                    relation_exist=check_userid_websiteid_relation(current_user_id,website_id)
                    is_active=get_user_website_relation_status(current_user_id,website_id)
                    if(relation_exist and is_active):
                        msg='Website already in to monitor list'
                        return False,msg
                    elif(relation_exist and not is_active):
                        res=set_user_website_relation_status(current_user_id,website_id,True)
                        if res:
                            msg='The relation found in database, changed to active from unactive'
                            return True,msg
                    else:
                        response1=savedata_website_user_map(website_id,current_user_id,role_value,create_datetime_value,update_datetime_value,isactive_value,do_notify_value)
                        if response1:
                            msg='website added to map table'
                            return True,msg
            #calling the function
            response,msg=function_test()
            if response:
                flash(msg,'success')
                return redirect(url_for('website.fetch_websites'))
                # return make_response({'msg':msg},status.HTTP_201_CREATED)
            else:
                raise Exception(msg)
                # return make_response({'error':msg},status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            flash(str(ex),'danger')
            return redirect(url_for('website.add_website'))
            # return make_response({'error':str(ex)},status.HTTP_400_BAD_REQUEST)
    elif request.method=='GET':
        return render_template('add-website.html',form=form)

'''
--> API to update/change the website registered to the user to monitor
--> If the new website doesn't exists in the database, it add it in website_table and updates the user_map_table
--> if the website exists in database , it simly updates the user_map_table 
'''
@website.route('/update/<int:website_id>',methods=['POST','PUT','GET'])
def update_website(website_id):
    if request.method in['PUT','POST']:
        update_url=request.form['url']
        @jwt_required()
        def jwtfunction():
            try:
                current_user_id=get_jwt_identity()
                update_url_id=fetch_website_id(update_url)

                #condition to add url to database if it doesn't exists already
                if update_url_id is None:
                    save_website(update_url,datetime.utcnow(),datetime.utcnow(),True)
                    update_url_id=fetch_website_id(update_url)
                    print(f'--> Added "{update_url}" to database with id: {update_url_id}')
                else:
                    relation_exist=check_userid_websiteid_relation(current_user_id,update_url_id)
                    is_active=get_user_website_relation_status(current_user_id,update_url_id)
                    # print(relation_exist,is_active)
                    if(relation_exist and is_active):
                        msg='Website already in monitor list'
                        return False,msg
                    elif(relation_exist and not is_active):
                        res=set_user_website_relation_status(current_user_id,update_url_id,True)
                        if res:
                            msg='The relation found in database, changed to active from unactive'
                            return True,msg
                
                # update_res=update_website_user_map(update_url_id,current_user_id,website_id)
                update_res=1
                if update_res:
                    return True,'Website changed/updated'
            except Exception as ex:
                return False,str(ex)
        resp,msg=jwtfunction()
        if resp:
            flash(msg,'success')
            return redirect(url_for('website.fetch_websites'))
            # return make_response({'message':msg},status.HTTP_200_OK)
        else:
            flash(msg,'warning')
            return redirect(url_for('website.fetch_websites'))
            # return make_response({'error':msg},status.HTTP_400_BAD_REQUEST)
    if request.method in['GET']:
        form=AddWebsiteForm()
        return render_template('add-website.html',page_name='Update Site',form=form,website_id=website_id)

'''
--> Api to remove the website from the users monitoring list(set relation to inactive)
'''
@website.route('/remove/<int:website_id>',methods=['DELETE','GET'])
@jwt_required()
def remove_website(website_id):
    if request.method=='GET' or request.method=='DELETE':
        try:
            current_user_id=get_jwt_identity()
            relation_exist=check_userid_websiteid_relation(current_user_id,website_id)
            is_active=get_user_website_relation_status(current_user_id,website_id)
            if not relation_exist:
                return make_response({'error':'No such entry exists'},status.HTTP_404_NOT_FOUND)
            if set_user_website_relation_status(current_user_id,website_id,status=False):
                flash('Site successfuly removed','success')
                return redirect(url_for('website.fetch_websites'))
                # return make_response({'Message':'Website removed successfully from your list'})
        except Exception as ex:
            flash(ex,'danger')
            return redirect(url_for('website.fetch_websites'))
            # return make_response({'error':str(ex)},status.HTTP_400_BAD_REQUEST)

@website.route('/all',methods=['GET'])
@jwt_required() #check pending :isactive functionality
def fetch_websites():
    if request.method=='GET':
        try:
            current_user_id=get_jwt_identity()
            datafetched=get_user_urls(current_user_id)
            # print(datafetched)
            res=make_response(render_template('dashboard.html',url_data_list=datafetched))
            return res
            # return make_response({'msg':'data fetched successfully','url_list':datafetched},status.HTTP_200_OK)
        except Exception as ex:
            flash(ex,'danger')
            res= redirect(url_for('website.fetch_websites'))
            return res
            # return make_response({'error':str(ex)},status.HTTP_400_BAD_REQUEST)
    else:
        return make_response({'error':'This method is not supported'},status.HTTP_405_METHOD_NOT_ALLOWED)

@website.route('/<int:website_id>',methods=['GET'])
@jwt_required()
def get_site_report(website_id):
    if request.method=='GET':
        try:
            current_user_id=get_jwt_identity()
            rel=check_userid_websiteid_relation(current_user_id,website_id)
            if rel:
                weekly_report_data=get_website_weekly_performance(website_id)
                if(len(weekly_report_data)==0):
                    flash('No data available for the site yet','warning')
                    return redirect(url_for('website.fetch_websites'))
                return render_template('website-data.html',data_list=weekly_report_data,website_id=website_id)
                # return make_response(weekly_report_data,status.HTTP_200_OK)
            else:
                raise Exception("subscription to the website doesn't exist")
                # return make_response({'error':"subscription to the website doesn't exist"},status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            flash(ex,'danger')
            return redirect(url_for('website.get_site_report',website_id=website_id))
            # return make_response({'error':str(ex)},status.HTTP_400_BAD_REQUEST)


@website.route('/data/<int:website_id>',methods=['GET'])
@jwt_required()
def site_data(website_id):
    if request.method=='GET':
        try:
            current_user_id=get_jwt_identity()
            rel=check_userid_websiteid_relation(current_user_id,website_id)
            if rel:
                weekly_report_data=get_website_weekly_performance(website_id)
                if(len(weekly_report_data)==0):
                    # flash('No data available for the site yet','warning')
                    # return redirect(url_for('website.fetch_websites'))
                    raise Exception('No data available for the site yet')
                # return{'data':weekly_report_data}
                return make_response({'weekly_data':weekly_report_data},status.HTTP_200_OK)
            else:
                raise Exception("subscription to the website doesn't exist")
        except Exception as ex:
            return make_response({'error':str(ex)},status.HTTP_400_BAD_REQUEST)

@website.route('/notification/<int:website_id>',methods=['GET','POST'])
@jwt_required()
def change_notification(website_id):
    if request.method=='GET':
        try:
            current_user_id=get_jwt_identity()
            rel=check_userid_websiteid_relation(current_user_id,website_id)
            if rel:
                return {'notify_status':get_notify_status(current_user_id,website_id)}
            else:
                raise Exception("subscription to the website doesn't exist")
        except Exception as ex:
            return make_response({'error':str(ex)},status.HTTP_400_BAD_REQUEST)
    if request.method=='POST':
        print(request.headers)
        try:
            current_user_id=get_jwt_identity()
            rel=check_userid_websiteid_relation(current_user_id,website_id)
            if rel:
                toggle_notify_status(current_user_id,website_id)
                return {'notify_status':get_notify_status(current_user_id,website_id)}
            else:
                raise Exception("subscription to the website doesn't exist")
        except Exception as ex:
            return make_response({'error':str(ex)},status.HTTP_400_BAD_REQUEST)