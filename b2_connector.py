'''
Backblaze wants developers and organization to copy and re-use our
code examples, so we make the samples available by several different
licenses.  One option is the MIT license (below).  Other options are
available here:

    https://www.backblaze.com/using_b2_code.html


The MIT License (MIT)

Copyright (c) 2020 Backblaze

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from __future__ import print_function

# Python Imports

import base64
import sys
import requests
import json
import hashlib
import datetime

# Tools Imports

import yaml

# Project Imports

class B2Connector:

    def __init__(self):
        '''
        Initiliaze & load configuration from settings file. Also -
        calls authentication method during initialization so object is ready
        to make requests to B2.
        :return: None
        '''

        settings_file = 'config.yaml'
        with open(settings_file, 'r') as stream:
            settings = yaml.safe_load(stream)

        self.key_id = settings['keyid']
        self.app_key = settings['appkey']
        self.bucket_name = settings['bucketName']
        self.api_version = settings['apiVersion']

        self.apiUrl = ''
        self.authToken = ''
        self.downloadUrl = ''
        self.accountId = ''

        self.authB2()

    def authB2(self):
        '''
        Authentication against B2 using the credentials stored in the
        configuration file. If successful, the return token will be stored in
        the instance of the class for future references.
        :return: None
        '''

        # TODO: Instead of fetching a new auth token each time this class is
        # instantiated, persist the token somewhere (on disk?) and try using
        # it. If it fails, fetch another one.

        auth_string = self.key_id + ':' + self.app_key
        basic_auth_string = 'Basic ' + base64.b64encode(auth_string.encode(
            'ascii')).decode('ascii')

        baseUrl = "https://api.backblaze.com" + self.api_version
        authCmd = "b2_authorize_account"

        url = baseUrl + authCmd

        headers = {}
        headers['Authorization'] = basic_auth_string

        result, status_code = self.fetchUrl(url, 'GET', False, headers=headers)
        result = json.loads(result)
        self.apiUrl = result['apiUrl']
        self.authToken = result['authorizationToken']
        self.downloadUrl = result['downloadUrl']
        self.accountId = result['accountId']

        # if the application key is bound to only one bucket, the bucketId
        # is actually in the result. In this case, just use the bucketId if
        # it matches the name in config.yaml. If not, error out.

        if result['allowed']['bucketId']:
            if result['allowed']['bucketName'] == self.bucket_name:
                self.bucket_id = result['allowed']['bucketId']
            else:
                print('Bucket authorized in key does not match config.yaml. '
                      'Exiting.')
                sys.exit()
        else:
            self.bucket_id = self.getBucketIdFromName(self.bucket_name)

    def getBucketIdFromName(self, bucket_name):
        '''
        Returns a bucket ID from a bucket_name.
        :param bucket_name: bucket_name
        :return: bucketId
        '''

        cmd = "b2_list_buckets"
        url = self.apiUrl + self.api_version + cmd

        headers = {}
        headers['Authorization'] = self.authToken

        params = {}
        params['accountId'] = self.accountId

        result, status_code = self.fetchUrl(url, 'GET', False,
                                            headers=headers, params=params)
        result = json.loads(result)
        for r in result['buckets']:
            if r['bucketName'] == bucket_name:
                return r['bucketId']

    def download_file_by_name(self, filename, expected_sha1, attempt_num):
        '''
        Download a file using b2_download_file_by_name API
        :param filename: filename
        :return: request, response
        '''

        url = self.downloadUrl + '/file/' + self.bucket_name + '/' + filename

        headers = {}
        headers['Authorization'] = self.authToken

        # Adding a Range header for the first 10MB of a file, just in case
        # this could be related.

        if int(attempt_num) % 2 == 0:
            headers['Range'] = 'bytes=0-9999999'

        session, req, res, timestamp = self.fetchUrl(url, 'GET', True,
                                                     headers=headers)

        print('[Attempt: %s]: Request made at %s' % (attempt_num, timestamp))

        if res.status_code != 200:

            # If the status code isn't 200, just report it and continue. A
            # 900 error indicates a RequestExeception.

            print ('[Attempt: %s]: Returned status code %s. Continuing.'
                   % attempt_num, str(res.status_code))
        else:
            # If 200, let's check the contents of the response SHA1 with the
            # SHA1 returned by B2 with the expected SHA1.

            res_content_sha1 = hashlib.sha1(res.content).hexdigest()
            b2_content_sha1  = res.headers['X-Bz-Content-Sha1']
            if (res_content_sha1 == expected_sha1 == b2_content_sha1):
                print('[Attempt: %s]: All SHA1 match.' % attempt_num)
            else:
                print('[Attempt: %s]: SHA1 do not match.' % attempt_num)
                print('[Attempt: %s]: expected_content_sha1: %s' %
                      (attempt_num, expected_sha1))
                print('[Attempt: %s]: b2_content_sha1: %s' %
                      (attempt_num, b2_content_sha1))
                print('[Attempt: %s]: res_content_sha1: %s' %
                      (attempt_num, res_content_sha1))
                self.print_request(req, session, attempt_num)
                self.print_response(res, attempt_num)

    def fetchUrl(self, url, method, doExamine, headers={}, params={}):
        '''
        Fetch URL. If the connection fails, it return a status 900.
        :param url: url to fetch.
        :param method: The http verb. Supports only GET.
        :param doExamine: Calling method needs to examine the session,
        request and response. Return them all.
        :param headers: dictionary of headers to pass with the request (
        optional)
        :param params: dictionary of parameters to pass with the request (
        optional)
        :return: If doExamine, return the request, session and response.
        Otherwise, just return the response content and status_code. A 900 error
        indicates an HTTP RequestExeception to the caller.
        '''

        try:
            req = requests.Request(
                method,
                url=url,
                params=params,
                headers=headers,
            )

            now = datetime.datetime.utcnow().strftime(
                '%a, %d %b %Y %H:%M:%S GMT')
            prepared = req.prepare()
            session = requests.Session()
            res = session.send(prepared)

            if doExamine:
                return session, req, res, now

            return res.content, res.status_code

        except requests.exceptions.RequestException as e:
            print('HTTP GET Request failed', file=sys.stderr)
            print(url, file=sys.stderr)
            print(e, file=sys.stderr)

            result = json.loads('[]')
            return result, 0, 900

    def print_request(self, req, session, attempt_num):
        """
        At this point it is completely built and ready
        to be fired; it is "prepared".

        However pay attention at the formatting used in
        this function because it is programmed to be pretty
        printed and may differ from the actual request.
        """

        headers = {**req.headers, **session.headers}

        # Omit authorization header itself
        headers['Authorization'] = '[omitted]'

        print('[Attempt: %s] REQUEST  **********' % attempt_num)
        print('{request_method_and_url}\n{headers}\n'.format(
            request_method_and_url=req.method + ' ' + req.url,
            headers='\n'.join(
                '{}: {}'.format(k, v) for k, v in headers.items())
        ))

    def print_response(self, res, attempt_num):
        print('[Attempt: %s] RESPONSE  **********' % attempt_num)
        print('HTTP/{version} {status_code}\n{headers}\n'.format(
            version=res.raw.version,
            status_code=res.status_code,
            headers='\n'.join(
                '{}: {}'.format(k, v) for k, v in res.headers.items())
        ))
