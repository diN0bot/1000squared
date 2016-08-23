from django.shortcuts import redirect
from django.shortcuts import render
import settings
from twython import Twython
from twython.exceptions import TwythonAuthError


APP_KEY = 'zOQLj02rTAYJRLz46a8IAcq5z'
APP_SECRET = '0EfAMPv6cbKBHo07oYek12FNXjPSAlUGKU63h5pGoCRWO058ZQ'


CHANGE_CATALYSTS = ['inclusion',
                    'creating solutions',
                    'being transparent',
                    'having a growth mindset',
                    'collaborating',
                    'creating safe spaces',
                    'my empathy',
                    'acceptance',
                    'hope',
                    'inspiring others',
                    'celebrating',
                    'telling stories',
                    'convening everyone together',
                    'empowering people around me',
                    'egalitarianism',
                    'changing myself',
                    'the truth',
                    'trust',
                    'being authentic',
                    'valuing diversity with money and action']

DEFAULT_CATALYST = CHANGE_CATALYSTS[0]


def index(request):
    if request.session.get('twitter_oauth_final', False) or settings.DEBUG:
        if request.POST.get('catalyst', None):
            try:
                twitter = Twython(APP_KEY, APP_SECRET,
                    request.session['twitter_oauth_token'],
                    request.session['twitter_oauth_token_secret'])

                catalyst = request.POST.get('catalyst', DEFAULT_CATALYST)
                twitter.update_status(status='My change catalyst of choice is %s #techinclusion16 @techinclusion' % catalyst)
                return redirect('https://twitter.com/hashtag/techinclusion16')
            except (TwythonAuthError, KeyError) as e:
                request.session['twitter_oauth_final'] = False
                return redirect('catalyze.index')

        else:
            return render(request, 'catalyze/index.html', {'CHANGE_CATALYSTS': CHANGE_CATALYSTS})

    else:
        twitter = Twython(APP_KEY, APP_SECRET)
        auth = twitter.get_authentication_tokens(callback_url='http://lusrc.com/callback/')
        request.session['twitter_oauth_final'] = False
        request.session['twitter_oauth_token'] = auth['oauth_token']
        request.session['twitter_oauth_token_secret'] = auth['oauth_token_secret']
        return redirect(auth['auth_url'])

def callback(request):
    oauth_verifier = request.GET.get('oauth_verifier')
    oauth_token = request.GET.get('oauth_token')

    twitter_oauth_token = request.session.get('twitter_oauth_token', None)
    twitter_oauth_token_secret = request.session.get('twitter_oauth_token_secret', None)
    twitter = Twython(APP_KEY, APP_SECRET, twitter_oauth_token, twitter_oauth_token_secret)

    try:
        final_step = twitter.get_authorized_tokens(oauth_verifier)
    except:
        request.session['twitter_oauth_final'] = False
        return redirect('catalyze.index')

    request.session['twitter_oauth_token'] = final_step['oauth_token']
    request.session['twitter_oauth_token_secret'] = final_step['oauth_token_secret']
    request.session['twitter_oauth_final'] = True

    return redirect('catalyze.index')
