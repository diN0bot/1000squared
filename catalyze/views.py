from catalyze.models import CatalystPic, CatalystPicForm
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.shortcuts import render
import os
from PIL import Image, ImageDraw, ImageFont
import settings
import textwrap
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

# Twitter media upload doesn't accept images larger than 3mb
TWITTER_IMAGE_SIZE_LIMIT = 3145728

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
    if request.session.get('twitter_oauth_final', False) or settings.DEV_DEBUG:
        ### User is authenticated, show/process form
        if settings.DEV_DEBUG:
            request.session['twitter_oauth_token'] = settings.DEV_OAUTH_TOKEN
            request.session['twitter_oauth_token_secret'] = settings.DEV_OAUTH_TOKEN_SECRET

        if request.method == 'POST':
            form = CatalystPicForm(request.POST, request.FILES)
            if form.is_valid():
                new_catalyst_pic = form.save()

                ### Tweet user's selection from submitted form
                try:
                    catalyst = request.POST.get('catalyst', DEFAULT_CATALYST)
                    status = '%s %s %s' % (TWEET_STATEMENT, catalyst, TWEET_TAGS)

                    _process_image(new_catalyst_pic.pic.name, status)

                    twitter = Twython(
                        settings.APP_KEY, settings.APP_SECRET,
                        request.session['twitter_oauth_token'],
                        request.session['twitter_oauth_token_secret'])
                    photo = open(new_catalyst_pic.pic.name, 'rb')
                    response = twitter.upload_media(media=photo)

                    twitter.update_status(status=status, media_ids=[response['media_id']])
                    
                    return redirect('https://twitter.com/hashtag/techinclusion16')
                except (TwythonAuthError, KeyError) as e:
                    request.session['twitter_oauth_final'] = False
                    print "TwythonAuthError", e
                    return redirect('catalyze.index')
            else:
                ### Show form with error message
                return render(request, 'catalyze/index.html', {'TWEET_STATEMENT': TWEET_STATEMENT,
                                                           'CHANGE_CATALYSTS': CHANGE_CATALYSTS,
                                                           'TWEET_TAGS': TWEET_TAGS,
                                                           'errors': form.errors})

        else:
            ### Show form
            template_data = {'TWEET_STATEMENT': TWEET_STATEMENT,
                             'CHANGE_CATALYSTS': CHANGE_CATALYSTS,
                             'TWEET_TAGS': TWEET_TAGS}
            if settings.DEV_DEBUG:
                template_data['DEV_DEBUG'] = True
                template_data['a'] = request.session['twitter_oauth_token']
                template_data['b'] = request.session['twitter_oauth_token_secret']
            return render(request, 'catalyze/index.html', template_data)

    else:
        ### User is not authenticated. No form for them. Initiate oauth process.
        # TODO: From a UI point of view, maybe we should show the form first, and ask to authenticate after user has invested in a selection?
        twitter = Twython(settings.APP_KEY, settings.APP_SECRET)
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
    twitter = Twython(settings.APP_KEY, settings.APP_SECRET, twitter_oauth_token, twitter_oauth_token_secret)

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

def _process_image(filename, text):
    img = Image.open(filename)

    # add text to image
    draw = ImageDraw.Draw(img)
    font_path = os.path.join(settings.BASE_DIR, 'elegantly_simple.ttf')
    #font_path = os.path.join(settings.BASE_DIR, 'inky.ttf')
    font = ImageFont.truetype(font_path, 60)
    color = (256, 256, 256) #White
    outline_color = '#000000' #Black
    x = 0
    y = 0
    d = 2
    for line in textwrap.wrap(text, width=40):
        # border around text
        draw.text((x-d, y-d), line, font=font, fill=outline_color)
        draw.text((x+d, y-d), line, font=font, fill=outline_color)
        draw.text((x-d, y+d), line, font=font, fill=outline_color)
        draw.text((x+d, y+d), line, font=font, fill=outline_color)
        # text
        draw.text((x, y), line, color, font=font)
        y = y + 60
    img.save(filename)

    # resize if necessary
    statinfo = os.stat(filename)
    if statinfo.st_size >= TWITTER_IMAGE_SIZE_LIMIT:
        (w, h) = img.size
        quality = 85
        while statinfo.st_size >= TWITTER_IMAGE_SIZE_LIMIT:
            img.save(filename, optimize=True, quality=quality)
            statinfo = os.stat(filename)
            quality = quality - 5
            if quality < 70:
                quality = 70
                w = int(w * .90)
                h = int(h * .90)
                img = img.resize((w, h), Image.ANTIALIAS)
