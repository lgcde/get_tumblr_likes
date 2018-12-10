# -*- coding: utf-8 -*-

from requests_oauthlib import OAuth1Session
from requests_oauthlib import OAuth1
import requests
import yaml
import os
import json
import urllib.parse

# PROXIES = { "http": "http://127.0.0.1:1080", "https": "https://127.0.0.1:1080" } 
PROXIES = {}

# consumer_key = ''
# consumer_secret = ''

like_json = open("likes.json",'w',encoding='utf-8')

def new_oauth(yaml_path, consumer_key, consumer_secret):

	print('Retrieve consumer key and consumer secret from http://www.tumblr.com/oauth/apps')

	request_token_url = 'http://www.tumblr.com/oauth/request_token'
	authorize_url = 'http://www.tumblr.com/oauth/authorize'
	access_token_url = 'http://www.tumblr.com/oauth/access_token'

	# STEP 1: Obtain request token
	oauth_session = OAuth1Session(consumer_key, client_secret=consumer_secret)
	fetch_response = oauth_session.fetch_request_token(request_token_url, proxies=PROXIES)
	resource_owner_key = fetch_response.get('oauth_token')
	resource_owner_secret = fetch_response.get('oauth_token_secret')
	print("step 1 pass");

	# STEP 2: Authorize URL + Rresponse
	full_authorize_url = oauth_session.authorization_url(authorize_url)

	# Redirect to authentication page
	print('# 用你的浏览器打开这个网站 点击同意')
	print('\nPlease go here and authorize:\n{}'.format(full_authorize_url))
	print('# 等待网页自动跳转 复制新网址粘贴到这里')
	redirect_response = input('Allow then paste the full redirect URL here:')
	print(redirect_response)

	# Retrieve oauth verifier
	oauth_response = oauth_session.parse_authorization_response(redirect_response)
	print(oauth_response)

	verifier = oauth_response.get('oauth_verifier')
	print(verifier)

	# STEP 3: Request final access token
	oauth_session = OAuth1Session(
	    consumer_key,
	    client_secret=consumer_secret,
	    resource_owner_key=resource_owner_key,
	    resource_owner_secret=resource_owner_secret,
	    verifier=verifier
	)
	oauth_tokens = oauth_session.fetch_access_token(access_token_url, proxies=PROXIES)

	tokens = {
	    'consumer_key': consumer_key,
	    'consumer_secret': consumer_secret,
	    'oauth_token': oauth_tokens.get('oauth_token'),
	    'oauth_token_secret': oauth_tokens.get('oauth_token_secret')
	}

	yaml_file = open(yaml_path, 'w+')
	yaml.dump(tokens, yaml_file, indent=2)
	yaml_file.close()

	print("oauth succ!\n")
	return tokens

# if __name__ == '__main__':
def main():
	print('#1 get_json main()')
	# yaml_path = os.path.expanduser('~') + '/.tumblr'
	yaml_path = 'tumblr.cfg'  # 用于登陆的配置文件，首次登陆时验证并创建
	print(yaml_path)

	if not os.path.exists(yaml_path):
		print('This is the first authentication, so plese input info')
		# print("add a new oauth")
		consumer_key = input('plese input consumer_key :')
		consumer_secret = input('plese input consumer_secret :')
		tokens = new_oauth(yaml_path, consumer_key, consumer_secret)
	else:
	    yaml_file = open(yaml_path, "r")
	    tokens = yaml.safe_load(yaml_file)
	    yaml_file.close()

	oauth = OAuth1(
            tokens['consumer_key'],
        	tokens['consumer_secret'],
        	tokens['oauth_token'],
        	tokens['oauth_token_secret']
        )

	info_url = 'https://api.tumblr.com/v2/user/info'

	resp = requests.get(info_url, allow_redirects=False, auth=oauth, proxies=PROXIES)
	print(resp)

	try:
		data = resp.json()
	except ValueError:
		data = {'meta': { 'status': 500, 'msg': 'Server Error'}, 'response': {"error": "Malformed JSON or HTML was returned."}}

	if 200 <= data['meta']['status'] <= 399:
	    # print(data['response'])
	    like_item = data['response']['user']['likes']
	    print('like_item = ',like_item)
	    # json.dump(data,like_json)
	else:
	    print('error',data)

	raw_url = 'https://api.tumblr.com/v2/user/likes?limit=20&offset={0}'

	# loop_cnt = int(like_item/20) + 1
	# print('loop_cnt = ',loop_cnt)
	offset = 0
	# for i in range(0,loop_cnt):
	while offset<like_item:
		likes_url = raw_url.format(offset)

		resp = requests.get(likes_url, allow_redirects=False, auth=oauth, proxies=PROXIES)
		print(resp)

		try:
			data = resp.json()
		except ValueError:
			data = {'meta': { 'status': 500, 'msg': 'Server Error'}, 'response': {"error": "Malformed JSON or HTML was returned."}}

		if 200 <= data['meta']['status'] <= 399:
			# print(data['response'])
			# print(data['response']['user']['likes'])
			res_item_len = len(data['response']['liked_posts'])
			print("res_item_len = ",res_item_len)
			json.dump(data, like_json)
		else:
			print('error',data)

		# offset += 20 	
		offset += res_item_len
		like_json.write(u'\n'); # json 文件分割符

	like_json.close()	

if __name__ == '__main__':
	main()
