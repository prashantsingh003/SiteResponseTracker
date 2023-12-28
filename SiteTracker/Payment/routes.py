from flask import Blueprint
import stripe
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import redirect, render_template, request, make_response, flash, url_for

payment=Blueprint("payment",__name__,static_folder="static",template_folder="templates")

@payment.route('/<price_id>',methods=['GET','POST'])
@jwt_required()
def on_create_session(price_id):
    try:
        checkout_session=stripe.checkout.Session.create(
            line_items=[{
                'price':price_id,
                'quantity':1
            }],
            mode='subscription',
            success_url=url_for('home',_external=True)+'?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('about',_external=True)
        )
        print(dir(checkout_session))
    except Exception as ex:
        return {'error':str(ex)},400
    
    return redirect(checkout_session.url,code=303)