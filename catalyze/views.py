from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.shortcuts import render
from catalyze.models import CatalystPic, CatalystPicForm
from settings import APP_KEY, APP_SECRET
from twython import Twython
from twython.exceptions import TwythonAuthError


TWEET_STATEMENT = 'My change catalyst of choice is'
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
TWEET_TAGS = '#techinclusion16 @techinclusion'


"""
 Displays the form and handles posting tweets after the user makes a selection.
 Redirects to oauth if user hasn't authenticated app to post to Twitter.
 If user's token expires or is revoked, redirects once tweeting fails.

 Note, the session flag 'twitter_oauth_final', when present and set to True,
 indicates whether a user is successfully authenticated. This bit dictates 
 flow through the index and callback state machines. Also, We've followed 
 oauth naming and flow conventions from our use of Twython.
""" 
def index(request):
    # TODO: ALLOWED_HOSTS is currently failing on production, so DEBUG=True on prod....
    # Add 'or TRUE' to the following predicate to see the form page...but don't commit it
    if request.session.get('twitter_oauth_final', False) or True:# or settings.DEBUG: 
        ### User is authenticated, show/process form
        if request.method == 'POST':
            form = CatalystPicForm(request.POST, request.FILES)
            if form.is_valid():
                new_catalyst_pic = form.save()
                print
                print "FILENAME", new_catalyst_pic.pic.name
                print
                # from Pillow import Image
                # from Pillow import ImageFont
                # from Pillow import ImageDraw 
                #img_data = form.cleaned_data['uploaded_image']
                # img = Image.open(img_data)
                # draw = ImageDraw.Draw(img)
                # font = ImageFont.truetype("sans-serif.ttf", 16)
                # draw.text((x, y),"Sample Text",(r,g,b))
                # draw.text((0, 0), "Sample Text", (255,255,255), font=font)
                # img.save("FOO.JPG")
                # return render(request, 'catalyze/index.html', {'TWEET_STATEMENT': TWEET_STATEMENT,
                #                                                'CHANGE_CATALYSTS': CHANGE_CATALYSTS,
                #                                                'TWEET_TAGS': TWEET_TAGS}) 

                ### Tweet user's selection from submitted form
                try:
                    twitter = Twython(
                        APP_KEY, APP_SECRET,
                        '2500517942-bYnoax2BLBWaAbI8CPVGMVzkMtQsAkTAp6kYzop',
                        'is8oId1K5UO27u2bHXuMzEhSYpmXPvA5y4jQjVTqhfWLV')
                        #request.session['twitter_oauth_token'],
                        #request.session['twitter_oauth_token_secret'])

                    photo = open(new_catalyst_pic.pic.name, 'rb')
                    response = twitter.upload_media(media=photo)

                    catalyst = request.POST.get('catalyst', DEFAULT_CATALYST)
                    twitter.update_status(
                        status='%s %s %s' % (TWEET_STATEMENT, catalyst, TWEET_TAGS),
                        media_ids=[response['media_id']])
                    
                    return redirect('https://twitter.com/hashtag/techinclusion16')
                except (TwythonAuthError, KeyError) as e:
                    request.session['twitter_oauth_final'] = False
                    return redirect('catalyze.index')
            else:
                ### Show form with error message
                return render(request, 'catalyze/index.html', {'TWEET_STATEMENT': TWEET_STATEMENT,
                                                           'CHANGE_CATALYSTS': CHANGE_CATALYSTS,
                                                           'TWEET_TAGS': TWEET_TAGS,
                                                           'errors': form.errors})

        else:
            ### Show form
            return render(request, 'catalyze/index.html', {'TWEET_STATEMENT': TWEET_STATEMENT,
                                                           'CHANGE_CATALYSTS': CHANGE_CATALYSTS,
                                                           'TWEET_TAGS': TWEET_TAGS})

    else:
        ### User is not authenticated. No form for them. Initiate oauth process.
        # TODO: From a UI point of view, maybe we should show the form first, and ask to authenticate after user has invested in a selection?
        twitter = Twython(APP_KEY, APP_SECRET)
        auth = twitter.get_authentication_tokens(callback_url='http://%s%s/' % (request.get_host(), reverse('catalyze.callback')))
        request.session['twitter_oauth_final'] = False
        # these are intermediate values. after the user authenticates this app and returns to the callback we'll overwrite 
        # with the the final authenticated values and set 'twitter_oauth_final' to True
        request.session['twitter_oauth_token'] = auth['oauth_token']
        request.session['twitter_oauth_token_secret'] = auth['oauth_token_secret']
        return redirect(auth['auth_url'])

"""
 Handles callback from Twitter page where user authorizes app to post on their behalf. 
"""
def callback(request):
    oauth_verifier = request.GET.get('oauth_verifier')
    oauth_token = request.GET.get('oauth_token')

    twitter_oauth_token = request.session.get('twitter_oauth_token', None)
    twitter_oauth_token_secret = request.session.get('twitter_oauth_token_secret', None)
    twitter = Twython(APP_KEY, APP_SECRET, twitter_oauth_token, twitter_oauth_token_secret)

    try:
        final_step = twitter.get_authorized_tokens(oauth_verifier)
    except:
        # try again from the beginning
        request.session['twitter_oauth_final'] = False
        return redirect('catalyze.index')

    request.session['twitter_oauth_token'] = final_step['oauth_token']
    request.session['twitter_oauth_token_secret'] = final_step['oauth_token_secret']
    request.session['twitter_oauth_final'] = True
    return redirect('catalyze.index')
