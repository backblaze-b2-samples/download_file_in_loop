# Download file in a loop (using the Backblaze B2 API)

This script takes three inputs on the command line:
1. A B2 filepath
2. The expected SHA1 hash for this file.
3. The number of times the file should be downloaded.

For any download attempt where the SHA1 from the input does not match the 
SHA1 from the B2 response AND the SHA1 of the downloaded file contents, request 
response information will be output to help troubleshoot why the hash does 
not match.

## Pre-requisites
This scripts requires: 

yaml
```
pip install pyyaml
```

requests
```
pip install requests
```

## Config
Configuration is stored in config.yaml.

```yaml
bucketName : '[bucket name here]'
keyid      : '[add keyId here]'
appkey     : '[add appkey here]'
apiVersion : '/b2api/v2/'
```

## Running the script
```bash
$ python start.py [filepath] [Sha1] [num of requests] 
```

## Sample successful output
```
[Sun, 14 Feb 2021 20:34:19 GMT]: Starting downloads, 2 times
[Attempt: 0]: Request made at Sun, 14 Feb 2021 20:34:19 GMT
[Attempt: 0]: All SHA1 match.
[Attempt: 1]: Request made at Sun, 14 Feb 2021 20:34:19 GMT
[Attempt: 1]: All SHA1 match.
[Sun, 14 Feb 2021 20:34:20 GMT]: End
```

## Sample failed output
```
[Sun, 14 Feb 2021 20:33:44 GMT]: Starting downloads, 2 times
[Attempt: 0]: Request made at Sun, 14 Feb 2021 20:33:44 GMT
[Attempt: 0]: SHA1 do not match.
[Attempt: 0]: expected_content_sha1: 2e95d7582c53583fa8afb54e0fe7a2597c92cbbb
[Attempt: 0]: b2_content_sha1: 2e95d7582c53583fa8afb54e0fe7a2597c92cbba
[Attempt: 0]: res_content_sha1: 2e95d7582c53583fa8afb54e0fe7a2597c92cbba
[Attempt: 0] REQUEST  **********
GET https://f000.backblazeb2.com/file/nilayptmp/5mb.bin
Authorization: [omitted]
User-Agent: python-requests/2.25.1
Accept-Encoding: gzip, deflate
Accept: */*
Connection: keep-alive

[Attempt: 0] RESPONSE  **********
HTTP/11 200
Cache-Control: max-age=0, no-cache, no-store
x-bz-file-name: 5mb.bin
x-bz-file-id: 4_ze80632700cadcd4875410b15_f1095ab792eace83f_d20210214_m184505_c000_v0001073_t0009
x-bz-content-sha1: 2e95d7582c53583fa8afb54e0fe7a2597c92cbba
X-Bz-Upload-Timestamp: 1613328305000
Accept-Ranges: bytes
x-bz-info-src_last_modified_millis: 1613328240000
Content-Type: application/macbinary
Content-Length: 5242880
Date: Sun, 14 Feb 2021 20:33:43 GMT

[Attempt: 1]: Request made at Sun, 14 Feb 2021 20:33:45 GMT
[Attempt: 1]: SHA1 do not match.
[Attempt: 1]: expected_content_sha1: 2e95d7582c53583fa8afb54e0fe7a2597c92cbbb
[Attempt: 1]: b2_content_sha1: 2e95d7582c53583fa8afb54e0fe7a2597c92cbba
[Attempt: 1]: res_content_sha1: 2e95d7582c53583fa8afb54e0fe7a2597c92cbba
[Attempt: 1] REQUEST  **********
GET https://f000.backblazeb2.com/file/nilayptmp/5mb.bin
Authorization: [omitted]
User-Agent: python-requests/2.25.1
Accept-Encoding: gzip, deflate
Accept: */*
Connection: keep-alive

[Attempt: 1] RESPONSE  **********
HTTP/11 200
Cache-Control: max-age=0, no-cache, no-store
x-bz-file-name: 5mb.bin
x-bz-file-id: 4_ze80632700cadcd4875410b15_f1095ab792eace83f_d20210214_m184505_c000_v0001073_t0009
x-bz-content-sha1: 2e95d7582c53583fa8afb54e0fe7a2597c92cbba
X-Bz-Upload-Timestamp: 1613328305000
Accept-Ranges: bytes
x-bz-info-src_last_modified_millis: 1613328240000
Content-Type: application/macbinary
Content-Length: 5242880
Date: Sun, 14 Feb 2021 20:33:44 GMT

[Sun, 14 Feb 2021 20:33:45 GMT]: End
```
