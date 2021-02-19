from functools import wraps
from flask import g, request, redirect, url_for
from flask_login import current_user

# decorator to use to 'lock' a view to only be accessible to logged in users.
# if the current_user is authenticated (only logged in users are authenticated), then return the view, otherwise redirect to login.
# next is the url that the person was trying to access, which should be included in login so that the user can login and immediately be where they want.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            current_user.is_authenticated()
        except:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function