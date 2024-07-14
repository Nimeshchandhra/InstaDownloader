from flask import Flask, render_template, request, redirect, url_for, session
import instaloader
import time
import random
import requests
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a random secret key for session management

SAVE_DIR = "./static/instagram_downloads"
os.makedirs(SAVE_DIR, exist_ok=True)

L = instaloader.Instaloader()

def handle_rate_limit():
    delay = random.randint(300, 600)
    print(f"Rate limit hit. Sleeping for {delay // 60} minutes.")
    time.sleep(delay)

def login_to_instagram(username, password):
    try:
        L.login(username, password)
        print("Login successful!")
        return True
    except instaloader.exceptions.InvalidCredentialsException:
        print("Invalid username or password.")
        return False
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        print("Two-factor authentication is required.")
        return False
    except instaloader.exceptions.BadRequestException as e:
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def download_all_posts(profile_name):
    try:
        profile = instaloader.Profile.from_username(L.context, profile_name)
        if profile.is_private and not profile.followed_by_viewer:
            return f"Profile {profile_name} is private. You need to follow it to access posts."
        
        for post in profile.get_posts():
            L.download_post(post, target=SAVE_DIR)
            time.sleep(random.randint(1, 5))
        return f"All posts from {profile_name} downloaded successfully."
    except instaloader.exceptions.ProfileNotExistsException:
        return f"Profile {profile_name} does not exist."
    except instaloader.exceptions.TooManyRequestsException:
        handle_rate_limit()
        return download_all_posts(profile_name)

def download_all_stories(profile_name):
    try:
        profile = instaloader.Profile.from_username(L.context, profile_name)
        if profile.is_private and not profile.followed_by_viewer:
            return f"Profile {profile_name} is private. You need to follow it to access stories."
        
        for story in L.get_stories(userids=[profile.userid]):
            for item in story.get_items():
                L.download_storyitem(item, target=SAVE_DIR)
                time.sleep(random.randint(1, 5))
        return f"All stories from {profile_name} downloaded successfully."
    except instaloader.exceptions.ProfileNotExistsException:
        return f"Profile {profile_name} does not exist."
    except instaloader.exceptions.TooManyRequestsException:
        handle_rate_limit()
        return download_all_stories(profile_name)

def download_profile_picture(profile_name):
    try:
        profile = instaloader.Profile.from_username(L.context, profile_name)
        pic_url = profile.profile_pic_url
        if pic_url:
            pic_filename = os.path.join(SAVE_DIR, f"{profile.username}_profile_pic.jpg")
            with open(pic_filename, 'wb') as f:
                response = requests.get(pic_url)
                f.write(response.content)
            return f"Profile picture saved: {pic_filename}"
        else:
            return f"No profile picture found for {profile_name}"
    except instaloader.exceptions.ProfileNotExistsException:
        return f"Profile {profile_name} does not exist."
    except instaloader.exceptions.TooManyRequestsException:
        handle_rate_limit()
        return download_profile_picture(profile_name)

def download_followers_followees(profile_name):
    try:
        profile = instaloader.Profile.from_username(L.context, profile_name)
        followers = [follower.username for follower in profile.get_followers()]
        followees = [followee.username for followee in profile.get_followees()]
        return followers, followees
    except instaloader.exceptions.ProfileNotExistsException:
        return f"Profile {profile_name} does not exist."
    except instaloader.exceptions.TooManyRequestsException:
        handle_rate_limit()
        return download_followers_followees(profile_name)

def download_follow_back(profile_name):
    followers, followees = download_followers_followees(profile_name)
    if isinstance(followers, str):
        return followers

    follow_back = set(followees).intersection(set(followers))
    return list(follow_back)

def download_not_follow_back(profile_name):
    followers, followees = download_followers_followees(profile_name)
    if isinstance(followers, str):
        return followers

    not_follow_back = set(followees).difference(set(followers))
    return list(not_follow_back)

def download_followees_stories():
    try:
        for story in L.get_stories():
            for item in story.get_items():
                L.download_storyitem(item, target=SAVE_DIR)
                time.sleep(random.randint(1, 5))
        return f"All followees' stories downloaded successfully."
    except instaloader.exceptions.TooManyRequestsException:
        handle_rate_limit()
        return download_followees_stories()

def download_tagged_posts(profile_name):
    try:
        profile = instaloader.Profile.from_username(L.context, profile_name)
        if profile.is_private and not profile.followed_by_viewer:
            return f"Profile {profile_name} is private. You need to follow it to access tagged posts."
        
        for post in profile.get_tagged_posts():
            L.download_post(post, target=SAVE_DIR)
            time.sleep(random.randint(1, 5))
        return f"All tagged posts from {profile_name} downloaded successfully."
    except instaloader.exceptions.ProfileNotExistsException:
        return f"Profile {profile_name} does not exist."
    except instaloader.exceptions.TooManyRequestsException:
        handle_rate_limit()
        return download_tagged_posts(profile_name)

def download_saved_posts():
    try:
        saved_posts = L.get_saved_posts()
        for post in saved_posts:
            L.download_post(post, target=SAVE_DIR)
            time.sleep(random.randint(1, 5))
        return "All saved posts downloaded successfully."
    except Exception as e:
        print(f"Error: {e}")
        handle_rate_limit()
        return download_saved_posts()

def download_igtv_videos(profile_name):
    try:
        profile = instaloader.Profile.from_username(L.context, profile_name)
        if profile.is_private and not profile.followed_by_viewer:
            return f"Profile {profile_name} is private. You need to follow it to access IGTV videos."
        
        for igtv in profile.get_igtv_posts():
            L.download_igtv(igtv, target=SAVE_DIR)
            time.sleep(random.randint(1, 5))
        return f"All IGTV videos from {profile_name} downloaded successfully."
    except instaloader.exceptions.ProfileNotExistsException:
        return f"Profile {profile_name} does not exist."
    except instaloader.exceptions.TooManyRequestsException:
        handle_rate_limit()
        return download_igtv_videos(profile_name)

def download_highlights(profile_name):
    try:
        profile = instaloader.Profile.from_username(L.context, profile_name)
        if profile.is_private and not profile.followed_by_viewer:
            return f"Profile {profile_name} is private. You need to follow it to access highlights."
        
        for highlight in profile.get_highlights():
            for item in highlight.get_items():
                L.download_storyitem(item, target=SAVE_DIR)
                time.sleep(random.randint(1, 5))
        return f"All highlights from {profile_name} downloaded successfully."
    except instaloader.exceptions.ProfileNotExistsException:
        return f"Profile {profile_name} does not exist."
    except instaloader.exceptions.TooManyRequestsException:
        handle_rate_limit()
        return download_highlights(profile_name)

def download_public_post_from_link(post_url):
    try:
        post = instaloader.Post.from_shortcode(L.context, post_url)
        L.download_post(post, target=SAVE_DIR)
        return f"Public post downloaded successfully."
    except instaloader.exceptions.TooManyRequestsException:
        handle_rate_limit()
        return download_public_post_from_link(post_url)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if login_to_instagram(username, password):
        session['username'] = username
        session['password'] = password
        return redirect(url_for('dashboard'))
    else:
        return "Login failed. Please try again."

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('index'))

@app.route('/download', methods=['POST'])
def download():
    action = request.form['action']
    profile_name = request.form.get('profile_name', None)
    post_url = request.form.get('post_url', None)

    if action == 'all_posts':
                 message = download_all_posts(profile_name)
       elif action == 'all_stories':
           message = download_all_stories(profile_name)
       elif action == 'profile_picture':
           message = download_profile_picture(profile_name)
       elif action == 'followers_followees':
           followers, followees = download_followers_followees(profile_name)
           if isinstance(followers, str):
               message = followers
           else:
               message = f"Followers of {profile_name}: {followers}<br>Followees of {profile_name}: {followees}"
       elif action == 'follow_back':
           follow_back = download_follow_back(profile_name)
           message = f"Follow back from {profile_name}: {follow_back}"
       elif action == 'not_follow_back':
           not_follow_back = download_not_follow_back(profile_name)
           message = f"Not following back from {profile_name}: {not_follow_back}"
       elif action == 'followees_stories':
           message = download_followees_stories()
       elif action == 'tagged_posts':
           message = download_tagged_posts(profile_name)
       elif action == 'saved_posts':
           message = download_saved_posts()
       elif action == 'igtv_videos':
           message = download_igtv_videos(profile_name)
       elif action == 'highlights':
           message = download_highlights(profile_name)
       elif action == 'public_post':
           message = download_public_post_from_link(post_url)
       else:
           message = "Invalid action."

       return render_template('result.html', message=message)

   if __name__ == "__main__":
       app.run(debug=True)

       
