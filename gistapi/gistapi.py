"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

Github provides the Gist service as a pastebin analog for sharing code and
other develpment artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given Github account.
"""

import requests
from flask import Flask, jsonify, request
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
PER_PAGE = 30

@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"
    
def gists_for_user(username: str, page:int):
    """Provides the list of gist metadata for a given user.

    This abstracts the /users/:username/gist endpoint from the Github API.
    See https://developer.github.com/v3/gists/#list-a-users-gists for
    more information.

    To add pagination-new variable added -page

    Args:
        username (string): the user to query gists for
        page : page number to call as one time by default gist show only 30 gists

    Returns:
        The dict parsed from the json response from the Github API.  See
        the above URL for details of the expected structure.
    """
    try:
        
        gists_url = f'https://api.github.com/users/{username}/gists?page={page}&per_page={PER_PAGE}'
        headers= {'Accept':'application/vnd.github+json'}
        response = requests.get(gists_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f'Error retrieving gists for user "{username}": {str(e)}')
    except Exception as e:
        raise Exception(f'Error retrieving gists for user "{username}": {str(e)}')
    


@app.route("/api/v1/search", methods=['POST'])
def search():
    """Provides matches for a single pattern across a single users gists.

    Pulls down a list of all gists for a given user and then searches
    each gist for a given regular expression.

    Returns:
        A Flask Response object of type application/json.  The result
        object contains the list of matches along with a 'status' key
        indicating any failure conditions.
    """
    try:
        post_data = request.get_json()
        username = post_data['username']
        pattern = post_data['pattern']
        if not (username and username.strip()) or not (pattern and pattern.strip()):
            raise ValueError("Both username and pattern are required")

        page=1
        matches=[]
        result={}
        while True:
            gists = gists_for_user(username,page)
            total_gists = len(gists)
            if total_gists == 0:
                break

            headers= {'Accept':'application/vnd.github+json'}

            for gist in gists:
                # TODO: Fetch each gist and check for the pattern
                gist_id=gist['id']
                #get all files for the particular gistid
                gist_files_url= 'https://api.github.com/gists/{gist_id}'.format(gist_id=gist_id)
                gist_response= requests.get(gist_files_url,headers=headers)
                if gist_response.status_code!=200:
                    return jsonify({'status':'error','message':f'Failed to retrieve gist {gist_id}:{gist_response.status_code} {gist_response.reason}'})
                
                gist_files=gist_response.json()['files']
                for filename,data in gist_files.items():
                    data_response= requests.get(data['raw_url'],headers=headers)
                    if data_response.status_code!=200:
                        return jsonify({'status':'error','message':f'Failed to retrieve data {filename}:{data_response.status_code} {data_response.reason}'})
                    
                    text_content=data_response.text
                    # for matching pattern with text content
                    if re.search(pattern,text_content):
                        matches.append({'gist_id':gist_id,
                                            'file_name':filename})
            # pagination logic : if gists<30 then come out of loop
            if total_gists < PER_PAGE:
                break

            page=page+1
            
        result['status'] = 'success'
        result['username'] = username
        result['pattern'] = pattern
        result['matches'] = matches

        return jsonify(result)
    except requests.exceptions.RequestException as e:
        # Catch any exceptions raised by the requests library
        response = {'status': 'error', 'message': str(e)}
        return jsonify(response)
    except Exception as e:
        # Catch any other exceptions and return an error response
        response = {'status': 'error', 'message': str(e)}
        return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9876)
