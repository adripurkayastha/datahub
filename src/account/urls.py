from django.conf.urls import patterns, url
from account import forms as account_forms


urlpatterns = patterns(
    '',
    url(r'^login/?$', 'account.views.login', name='login'),
    url(r'^register/?$', 'account.views.register', name='register'),
    url(r'^logout/?$', 'account.views.logout', name='logout'),
    url(r'^choose_username/?$', 'account.views.get_user_details'),
    url(r'^settings/?$', 'account.views.settings', name='settings'),
    url(r'^add_login/?$', 'account.views.add_extra_login', name='add_extra_login'),
    url(r'^delete/?$', 'account.views.delete', name='delete'),
    # Use Django's built-in password reset tools.
    url(r'^forgot/?$', 'django.contrib.auth.views.password_reset',
        {
            'template_name': 'password_reset.html',
            'email_template_name': 'password_reset_email.html',
            'subject_template_name': 'password_reset_subject.txt',
            'password_reset_form': account_forms.ForgotPasswordForm,
            'from_email': 'noreply@datahub.csail.mit.edu',
        },
        name='password_reset'),
    url(r'^forgot/done/?$',
        'django.contrib.auth.views.password_reset_done',
        {
            'template_name': 'password_reset_done.html',
        },
        name='password_reset_done'),
    url((r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
         r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/?$'),
        'django.contrib.auth.views.password_reset_confirm',
        {
            'template_name': 'password_reset_confirm.html',
        },
        name='password_reset_confirm'),
    url(r'^reset/done/?$',
        'django.contrib.auth.views.password_reset_complete',
        {
            'template_name': 'password_reset_complete.html',
        },
        name='password_reset_complete'),
    # url(r'^verify/$', 'account.views.verify_email'),
)
