# Bug CSCwr82677 - Complete Report

Generated on: Fri, 23 Jan 2026 13:05:38 GMT

---

## Bug Summary

- **Component**: ewlc-docs
- **Description**: When generating a CSR from the WLC GUI, the process hangs indefinitely and never returns the CSR contents. The browser shows the page loading animation but will never complete the process.

The same CSR generation process on the CLI works as expected without any notable issues.
- **Headline**: CSR generation from the GUI hangs indefinitely and does not complete
- **Product**: ewlc
- **Severity**: 3
- **Status**: A
- **Version**: 17.12
- **Version**: 17.12.5
- **Version**: 17.9
- **Version**: 17.9.5
- **Status**: Y
- **Status**: Y

---

## Attached Files

### 1. 172.18.122.131_Archive-25-10-23 16-48-23.har

- **Type**: ascii text
- **Size**: 196564 bytes
- **Created**: 10/27/2025 10:00:40 by jorelder
- **URL**: https://cdetsng.cisco.com/wsapi/latest/api/bug/CSCwr82677/file/172.18.122.131_Archive-25-10-23 16-48-23.har

**Content:**

```
{
  "log": {
    "version": "1.2",
    "creator": {
      "name": "Firefox",
      "version": "144.0"
    },
    "browser": {
      "name": "Firefox",
      "version": "144.0"
    },
    "pages": [
      {
        "id": "page_1",
        "pageTimings": {
          "onContentLoad": -506475,
          "onLoad": -500875
        },
        "startedDateTime": "2025-10-23T16:47:00.095-05:00",
        "title": "https://172.18.122.131:2274/webui/#/certificate"
      }
    ],
    "entries": [
      {
        "startedDateTime": "2025-10-23T16:47:00.095-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/lscCertificate?parameters=trustpoint",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            },
            {
              "name": "Priority",
              "value": "u=0"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [
            {
              "name": "parameters",
              "value": "trustpoint"
            }
          ],
          "headersSize": 881
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:46:59 GMT"
            },
            {
              "name": "Content-Type",
              "value": "application/json; charset=UTF-8"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Vary",
              "value": "Accept-Encoding"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            },
            {
              "name": "Content-Encoding",
              "value": "gzip"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "application/json; charset=UTF-8",
            "size": 1182,
            "text": "{\"trustpointLabels\":\"[{\\\"Certificaterequests\\\":\\\"Yes\\\",\\\"TrustPoint\\\":\\\"TP-self-signed-915488100\\\",\\\"Keysgenerated\\\":\\\"Yes\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"None\\\",\\\"TrustPoint\\\":\\\"SLA-TrustPoint\\\",\\\"Keysgenerated\\\":\\\"No\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"None\\\",\\\"TrustPoint\\\":\\\"WLC_CA\\\",\\\"Keysgenerated\\\":\\\"Yes\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"Yes\\\",\\\"TrustPoint\\\":\\\"TimWLC3_WLC_TP\\\",\\\"Keysgenerated\\\":\\\"Yes\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"Yes\\\",\\\"TrustPoint\\\":\\\"mauriciowlc1_WLC_TP\\\",\\\"Keysgenerated\\\":\\\"Yes\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"None\\\",\\\"TrustPoint\\\":\\\"DNAC-CA\\\",\\\"Keysgenerated\\\":\\\"No\\\",\\\"IssuingCAauthenticated\\\":\\\"No\\\"},{\\\"Certificaterequests\\\":\\\"Yes\\\",\\\"TrustPoint\\\":\\\"dnaspaces1425\\\",\\\"Keysgenerated\\\":\\\"Yes\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"None\\\",\\\"TrustPoint\\\":\\\"dnaspaces1425-rrr1\\\",\\\"Keysgenerated\\\":\\\"No\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"None\\\",\\\"TrustPoint\\\":\\\"LWAVideo\\\",\\\"Keysgenerated\\\":\\\"No\\\",\\\"IssuingCAauthenticated\\\":\\\"No\\\"}]\"}\n"
          },
          "redirectURL": "",
          "headersSize": 781,
          "bodySize": 1059
        },
        "cache": {},
        "timings": {
          "blocked": -1,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 189,
          "receive": 0
        },
        "time": 189,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:00.110-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:46:59 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 84,
          "receive": 0
        },
        "time": 84,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:00.214-05:00",
        "request": {
          "bodySize": 1742,
          "method": "POST",
          "url": "https://ec.walkme.com/event/tell",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "Host",
              "value": "ec.walkme.com"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "text/html, */*; q=0.01"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "Content-Type",
              "value": "text/plain"
            },
            {
              "name": "Content-Length",
              "value": "1742"
            },
            {
              "name": "Origin",
              "value": "https://172.18.122.131:2274"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "cross-site"
            },
            {
              "name": "TE",
              "value": "trailers"
            }
          ],
          "cookies": [],
          "queryString": [],
          "headersSize": 472,
          "postData": {
            "mimeType": "text/plain",
            "params": [],
            "text": "{\"_static\":true,\"Wm-Client-Timestamp\":1761256020194}\n{\"_enc\":\"bbd%=rk|=3b//,%=zqpezrvk=3zls~y%=zsv}pr=3b/-&.%=wk{vh=3/'/.%=kwxvzw=d%=qzzm|l=3b=/.=%=qpvlmzi=3=lhp{qvH=%=zr~q=d%=lp=3b=/1++.=%=qpvlmzi=3=gpyzmvY=%=zr~q=d%=mzlhpm}=d%=iqz=3bB=/....).=3=&,-*&*.=D%=l{VkqrxL~=3=(,z}{}.-y)&,~.y'-)}+y,,}+}~'/yz*=%={V~lr=3='({'(}'.,(~,2-+*&2}||+2||z'2*+-),{)z=%={Vjzl|=3b=.=%=pyqv=3=*1-.1(.=%=ljk~kl=3=WV*RT,,^QM&=%=zofk=3=/=%=zspm=3=rmpyk~sO?s~jkmvI?zm~hRI?2?S\\\\2//'&\\\\=%=zr~q=d%=lm~Imzlj=3.%=rmpyk~so=3/%=iqz=3.2%={Vrmzo=3={.'-.,/(~//.}}/}-~++(-z|,+y*}+*&=%={Vj=3=mzvyvkqz{V=%=z|mjpL{Vjz=3=?WV*RT,,^QM&2kppm=%={Vjz=d%=rh=3=+|~,,},/y--{2-z(}2(-.+2/,,z2&){y)+~(=%={Vl=3b=-1/1*=%=zo=3=,-}(/yy-2+.|&,..'2*.+/.-2*-&/*-/-=%=}vs=3=((1/1*=%=~m}~=d%=qpvlmzi=3b=0vj}zh0+(--%.,.1--.1'.1-(.00%lokkw=%=mzmmzyzm=3=kqzrzx~q~R?VTO?2?qpvk~mjxvyqp\\\\?2?S\\\\2//'&\\\\?p|lv\\\\?%%^W\\\\SH=%=zskvk=3=y-,+}~~}.}--z.(}.,.+~*{}~.-/(y.(=%={Vkvlvi=3zls~y%=zr~myVlv=3b=zk~|vyvkmz|0<=%=wl~w=3=0vj}zh0=%=zr~qwk~o=3=+(--=%=kmpo=3=.,.1--.1'.1-(.=%=zr~qklpw=3=%lokkw=%=sp|pkpmo=d%=qpvk~|ps=3=).''yy'&~.(}*,.'y|)++'&/(}&,z+y/=%={Vqvh=3b.-,&%=zrvK{~ps=3./&&/***-.)(.%=km~kLi~q=d%=xqvrvk=d%=gk|=3.,&&./)*-.)(.%=zrvk=3b.%=}rvs|=3=mzkqvpo=%=zofk=d%=|lvr=3b=zk~|vyvkmz\\\\?{{^=%=kgzk=3=VS?SJ?B=Coo~2xq=C\\\"{vDF[P]=%=fmzjNpkj~=3=tqvs2t1B-Dq~ol0}~k\\\"zspm967}~Kqpvk~mzqzXzk~|vyvkmz\\\\z|viz[zlvs~vkvqv\\\"t|vs|2xq9xqv{qv}2xq1opk2qp2}~k2t1ksj~yz{2zk~kl2t1zivk|~2zk~kl2t1rzkv2t1B+Dvs0lrzkv2ovmkl}~k2t1kzlzm2t1B.Dsj0klvs}~k\\\"zspm9kzx{vh2t1opk2ovmkl}~k2t1ovmkl}~k2t1mz{~zw2t1o~mhk~psy2t1B.Div{0mzoo~mh2ovmkl}~k2t1B.Div{0B-Div{0zop|l2xq1B.Div{0zop|l2xq1B-Div{0mzqv~kqp|2vj}zh1B-Div{0qv~r1B-Div{0hpm1zop|l2xq1B.Div{0mzqv~kqp|2qv~r1mzqv~kqp|1B-Div{0oo~2xq<B.Df{p}0B.Dsrkw=%=wk~og=d%=kqzrzsz=3=qhp{zljpr=%=zofk=d\"}"
          }
        },
        "response": {
          "status": 200,
          "statusText": "",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "strict-transport-security",
              "value": "max-age=31536000; includeSubDomains; preload"
            },
            {
              "name": "x-frame-options",
              "value": "DENY"
            },
            {
              "name": "x-xss-protection",
              "value": "1; mode=block"
            },
            {
              "name": "x-content-type-options",
              "value": "nosniff"
            },
            {
              "name": "referrer-policy",
              "value": "strict-origin"
            },
            {
              "name": "cache-control",
              "value": "private, max-age=600"
            },
            {
              "name": "cross-origin-resource-policy",
              "value": "cross-origin"
            },
            {
              "name": "content-security-policy",
              "value": "upgrade-insecure-requests; block-all-mixed-content; default-src 'none'; frame-ancestors: 'none'"
            },
            {
              "name": "access-control-allow-origin",
              "value": "*"
            },
            {
              "name": "content-type",
              "value": "text/html; charset=utf-8"
            },
            {
              "name": "content-length",
              "value": "2"
            },
            {
              "name": "date",
              "value": "Thu, 23 Oct 2025 21:47:00 GMT"
            },
            {
              "name": "via",
              "value": "1.1 google"
            },
            {
              "name": "alt-svc",
              "value": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000"
            },
            {
              "name": "X-Firefox-Spdy",
              "value": "h2"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/html; charset=utf-8",
            "size": 2,
            "text": "ok"
          },
          "redirectURL": "",
          "headersSize": 634,
          "bodySize": 636
        },
        "cache": {},
        "timings": {
          "blocked": -1,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 130,
          "receive": 0
        },
        "time": 130,
        "_securityState": "secure",
        "serverIPAddress": "35.201.109.167",
        "connection": "443",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:03.986-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/lscCertificate?parameters=trustpointPKI",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            },
            {
              "name": "Priority",
              "value": "u=0"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [
            {
              "name": "parameters",
              "value": "trustpointPKI"
            }
          ],
          "headersSize": 884
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:47:04 GMT"
            },
            {
              "name": "Content-Type",
              "value": "application/json; charset=UTF-8"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Vary",
              "value": "Accept-Encoding"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            },
            {
              "name": "Content-Encoding",
              "value": "gzip"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "application/json; charset=UTF-8",
            "size": 15599,
            "text": "{\"rsaECKey\":\"% Key pair was generated at: 23:47:16 UTC Jul 25 2023\\r\\nKey name: ssh-key\\r\\nKey type: RSA KEYS      2048 bits\\r\\n Storage Device: private-config\\r\\n Usage: General Purpose Key\\r\\n Key is not exportable. Redundancy enabled.\\r\\n Key Data:\\r\\n  30820122 300D0609 2A864886 F70D0101 01050003 82010F00 3082010A 02820101 \\r\\n  00B27DC7 860C4E81 15862F33 51F7EEAA 4C69AA0C AABDC656 88DD396D 9AA37787 \\r\\n  C1F251E7 5A8F3BAE 16A5B0CB 8245C227 CCBA84E6 748C8850 396BFF1F 79CB3FE6 \\r\\n  1ADD4184 7418B98A C0E78359 191852ED 086A2C13 FE81DA47 DD9B708E 20B89DBF \\r\\n  9EF7926F 789F35CF 07FA0DEA 4498DDDF EED21311 DB80DE13 61B9DA3C 210B3E5C \\r\\n  50539403 E2133ABA A22FE3DC B98B01FC 3B873D7F C42DAAE0 6FC861C3 76DD88EF \\r\\n  302CF9AD D7DD24B2 4E4A9494 5DBE7B52 450DCC90 A24C75F4 8B88163A 4730BBDE \\r\\n  5F2703CE 0C7C633F 20515086 5748CB56 6AF22332 4E64541C 402C2000 AED4E42B \\r\\n  D117DE88 A1427144 2505BF93 EB9B907E E69D5D2B D910FD6B 526BE2A3 9ECB887C \\r\\n  1F020301 0001\\r\\n% Key pair was generated at: 23:47:26 UTC Jul 25 2023\\r\\nKey name: TP-self-signed-915488100\\r\\nKey type: RSA KEYS      2048 bits\\r\\n Storage Device: private-config\\r\\n Usage: General Purpose Key\\r\\n Key is not exportable. Redundancy enabled.\\r\\n Key Data:\\r\\n  30820122 300D0609 2A864886 F70D0101 01050003 82010F00 3082010A 02820101 \\r\\n  00B03D20 BFBC54B4 8AD3B81E 58D3BEAF 7290A89E 5083F616 C92E9370 173A70F8 \\r\\n  B8FA2B64 37917EB7 962E0421 93FC8B31 A14F4C30 1F1F7A01 91FFFE63 49AE6578 \\r\\n  74B2C9F3 58B22BEE 7D022E70 3D9051B8 14AF7BB8 D904A6C8 CA6B6E2F 18B67738 \\r\\n  6B91547B B4208AB4 3DCE8CE3 3AB538F2 F8977432 99F255CD 52B5550A 809C2B5F \\r\\n  2C2BBA08 6226C383 CA8F5130 3B15C53C AF74040D 6A72EEF9 3653D9B0 9B372612 \\r\\n  65D5FE07 A001DA2C 3CB36820 AA882990 E7A87FB5 BF655EFA 148370E3 964F1439 \\r\\n  01DD4A1B DE0045D9 7315E2F0 13FD6792 88DD04E0 B6D374F6 D59F816F ACB2728A \\r\\n  D15AE519 C2744856 3BBB51AE 40F87031 C57A1162 9355DAF0 461364C7 84901CFE \\r\\n  83020301 0001\\r\\n% Key pair was generated at: 00:02:33 UTC Jul 26 2023\\r\\nKey name: WLC_CA\\r\\nKey type: RSA KEYS      2048 bits\\r\\n Storage Device: private-config\\r\\n Usage: General Purpose Key\\r\\n Key is not exportable. Redundancy enabled.\\r\\n Key Data:\\r\\n  30820122 300D0609 2A864886 F70D0101 01050003 82010F00 3082010A 02820101 \\r\\n  00BA32FD 528D50DE 3C4C0718 275E0D70 D7D9D872 5B0A65ED BC920F92 621B38E1 \\r\\n  9D7F3F52 A21749C9 BAF8D7D9 BDD90076 79C288D0 F63A8E0A AD5AFCD8 C010C86A \\r\\n  F4074829 A060BE87 E7AB3E0E 55A118C0 DC3A2087 6EE6AAF3 498DCEBB 46AC822E \\r\\n  4959F6A0 EBB911A4 B043382A B08DD5A7 593ACD21 F3CA6766 44E6D1E0 F5BF5602 \\r\\n  62346D62 48BCB273 74535952 0D7383E4 F3B30F66 BD15BFCA 0AB12D8E 3A53F4F5 \\r\\n  FE576450 4EDDD5A8 E6259156 0F5D3224 56F51941 170A174C F3EC15EC D2DAC31D \\r\\n  80045EB3 3713A1A1 C5490F66 DFACC28C CC25AEF3 6C1B3DC8 A78286B0 8C00F6A3 \\r\\n  85D30386 F6A6841F 6249DA52 60C45B90 53C46CB6 194AD60F C9C1FBEA 20B220A1 \\r\\n  5D020301 0001\\r\\n% Key pair was generated at: 00:02:37 UTC Jul 26 2023\\r\\nKey name: TimWLC3_WLC_TP\\r\\nKey type: RSA KEYS      2048 bits\\r\\n Storage Device: private-config\\r\\n Usage: General Purpose Key\\r\\n Key is exportable. Redundancy enabled.\\r\\n Key Data:\\r\\n  30820122 300D0609 2A864886 F70D0101 01050003 82010F00 3082010A 02820101 \\r\\n  00D39869 5AA6EACE 0EF202CE E8A23F91 67989DD9 D2926CBB 0E236384 F21ECB85 \\r\\n  CE2ADBD2 217C1763 CE8A628C 1D5238F3 B22F0C72 3223DDCF C75F612F F7B89170 \\r\\n  292E7570 A9F5046E EC92DE76 BECCDECC 13E2F3F5 64637938 CC0BA936 181869BA \\r\\n  D75FB258 F51A96A2 BD62EFBC 73064DFA 1BA78A82 658488BC 63C0CCAA 9EEC5B2A \\r\\n  B9BC815B CA6543B1 4BB94FCF 503FB713 E11680B8 13AB2F2B 49FC454D C5FC0D2B \\r\\n  C40583D8 4995214B F9173AFF 15EF580F 2E55050B 5AA92BE5 5F55C9F8 4E7F65A9 \\r\\n  3DC0408D 71C0B499 8C9BDC22 04727CE2 01BA263B D9E31AD6 CB4E89A1 84BCFBDF \\r\\n  7386C141 B7ECEF6F 3D2C7454 373B966D 3B180341 8476FC2A 5D9F30E7 00929E34 \\r\\n  EB020301 0001\\r\\n% Key pair was generated at: 16:46:45 UTC Aug 14 2023\\r\\nKey name: CLOUDM_PKEY\\r\\nKey type: RSA KEYS      2048 bits\\r\\n Storage Device: private-config\\r\\n Usage: General Purpose Key\\r\\n Key is not exportable. Redundancy enabled.\\r\\n Key Data:\\r\\n  30820122 300D0609 2A864886 F70D0101 01050003 82010F00 3082010A 02820101 \\r\\n  00A61763 E5A27EE9 7D663B5D 8EE79033 4C03DB9A AD35363C F203E1A8 6ACF7B19 \\r\\n  F47F98B6 BB0F9AB4 72F788F3 8AA634FA 8BEB3FC9 407C08EC 14040AED C1F49B89 \\r\\n  45A2734B 9B8DAADF AAD92BC0 7B6C4C25 F387F65E 7E902E45 3C91E4A4 B51D0E1F \\r\\n  2E7188DF FB61CEAB E5B2BD1F 14105CFD 39DD516C 69FF69F2 4454F61A F98D14E1 \\r\\n  5EAAFCA8 6F95E309 C701113B 36D84FA0 6AFA9F30 986E0B0B BA6B429A 8D799761 \\r\\n  C1A4E0C9 3A4717AA 5F360FF1 BE326F95 0F4FCDFF BB1A2860 6CB41F05 6CB9EBC5 \\r\\n  4C649240 B7DE5B67 769B27C5 8CB4FC62 DC61A732 C0FEBD5A 20F466F8 DA626970 \\r\\n  95091584 20A56D72 60C46C36 A240EB69 A8A6CDA7 913CD394 657C306D 79BF7569 \\r\\n  8F020301 0001\\r\\n% Key pair was generated at: 02:33:51 UTC Mar 11 2024\\r\\nKey name: mauriciowlc1_WLC_TP\\r\\nKey type: RSA KEYS      2048 bits\\r\\n Storage Device: private-config\\r\\n Usage: General Purpose Key\\r\\n Key is exportable. Redundancy enabled.\\r\\n Key Data:\\r\\n  30820122 300D0609 2A864886 F70D0101 01050003 82010F00 3082010A 02820101 \\r\\n  009A9432 8A4B9D0B C28D6FB2 B6C55612 135F529F F3E03B0B 54EB04A1 3D6B25FE \\r\\n  915766D4 E906ED66 9EE5844D 72074C7A A4C9A566 B80426D5 FBE28D9F 2E2B6B90 \\r\\n  18818F9A B398F4B5 1ED2628D 98FE4E94 3C44D3C0 8E997A16 3EE1CDFD DCF63B49 \\r\\n  B697C7F4 6DE23371 A96381E7 F2F9B3BB 08AE70D0 9CB6DA9B 355524DB 97D6D00F \\r\\n  32A971ED C0E6AED5 B809830C 86C407B6 D30B049F E291EF7E 14BD284F 06C22F56 \\r\\n  74FC7562 5EB9F2F5 BDC118BB 9F4AF9A6 0AA4764F 877C0BA3 67B5D39A 7FBFEE3F \\r\\n  5F5C6B7C C094848E 30010486 42DB25DC 9EC61071 BFAC4D9D 6EA43387 422818D4 \\r\\n  AD07728D C7D5934F DDB43749 D0E50A56 1263CFB7 446CC711 00CDD7E6 CD34A060 \\r\\n  2B020301 0001\\r\\n% Key pair was generated at: 19:41:15 UTC Jun 5 2025\\r\\nKey name: dnaspaces1425\\r\\nKey type: RSA KEYS      2048 bits\\r\\n Storage Device: private-config\\r\\n Usage: General Purpose Key\\r\\n Key is not exportable. Redundancy enabled.\\r\\n Key Data:\\r\\n  30820122 300D0609 2A864886 F70D0101 01050003 82010F00 3082010A 02820101 \\r\\n  00ADE9C8 809505DF A5CBDDC2 359BA372 B3F11629 4519721A 959FE3A6 BD4DD12F \\r\\n  F730BA13 D9C38906 12DE22D7 F5E2B7D5 37176E9D CFC80D89 D7B8C791 A58FCEB9 \\r\\n  6629813E D0115E79 A90FCA00 55516D4A C35B54EC 1B408D60 E95E4F69 1707D08E \\r\\n  69E0D7F9 820B3979 FFAC3C07 06885461 205A46C8 816BC8BB 34BF288B 7D691A01 \\r\\n  A8808AED 08EB9308 FF43AC3C E30E9A12 83065CC2 22583A04 0DB5C1F6 93669F31 \\r\\n  E5292A73 812DD520 E5205A3B D5BB009D 740BC870 531967B2 3FAEAE0B 45636B9A \\r\\n  7C8E4E50 797CB609 580AAD0D BAE5DCEB 3753D40A 35A8F818 41EFA408 FF7A2717 \\r\\n  E0EF7F2A 91F90E66 3AE3D982 F85F219D 222FBCC6 2123DDD5 7BDE265D A2987576 \\r\\n  87020301 0001\\r\\n% Key pair was generated at: 21:38:33 UTC Sep 20 2025\\r\\nKey name: ssh-key.server\\r\\nKey type: RSA KEYS      2176 bits\\r\\nTemporary key\\r\\n Usage: Encryption Key\\r\\n Key is not exportable.\\r\\n Key Data:\\r\\n  30820132 300D0609 2A864886 F70D0101 01050003 82011F00 3082011A 02820111 \\r\\n  00B7FB41 A82DD2EF 701D4438 EF056DB1 FCB71C59 5D4C65BA DEAFE903 2E1F441C \\r\\n  F669B4EA C0BD6815 B4F8DD17 05402A72 BF7B3A83 9DDBA489 E3DCDDC7 A9CCE16B \\r\\n  0C73FE9E 8013CB99 859F27F2 D2E2272A DF4B2612 9B489668 F5D50844 C0C5063A \\r\\n  CB8AB61D 9B258E4E 7B6BA0CB F9015AD9 7CB63C8B B98537B5 52C6F9E5 FAB3FC2A \\r\\n  4AEB7FF2 48752F7C 89DE107F D5E71174 9B2360CA 21AC4638 647B09B0 EA51F51F \\r\\n  7993E356 40026E32 6BF0A2C9 F1A5DAB6 46C65733 F0758327 6D2BFB3B 7C95CA22 \\r\\n  3549414E AFD828FF E21578A7 6F93F31C 0BC8EA60 3B4A9FCA 136F657B 7C94DC57 \\r\\n  FF2B8A91 1648F8BD 26D9E995 81C824F3 E35DB5C8 F0F827A5 A7F3EEF3 59B607E3 \\r\\n  CA342191 F5DB61C9 BDEC3EF9 1C07A8F8 6F020301 0001\\r\\n% Key pair was generated at: 21:30:25 UTC Oct 23 2025\\r\\nKey name: ShineyNewKey\\r\\nKey type: RSA KEYS      2048 bits\\r\\n Storage Device: not specified\\r\\n Usage: General Purpose Key\\r\\n Key is exportable. Redundancy enabled.\\r\\n Key Data:\\r\\n  30820122 300D0609 2A864886 F70D0101 01050003 82010F00 3082010A 02820101 \\r\\n  008C8B1C CA4E5F21 63B91638 E7F70C22 7D428420 D6511C5B 94DC7791 E6D69084 \\r\\n  296E3A3E D90F6C1D A4DAB738 251FB9BA 55EC3668 0B0E69B1 276601D1 19E0257D \\r\\n  D6DC31DC D5CF0A06 F3B999D9 BD21DB60 A8C063AA E28D78A4 55ECD45A FB1289CD \\r\\n  5F13DC56 BB7937EC 7A5861D7 BDFB76F1 DD427494 7D39EC7F 7F26C5C5 B0C9936A \\r\\n  7F00151B 3F67284A B84BF061 6A1ABFAF 25CB598C B9DAE905 064C3B9C 5F92006C \\r\\n  E4FB8A20 AA44A845 EAC2F26E 590A1DD1 9AC3E109 DBAC2B70 743E3985 159C55E6 \\r\\n  2B34B3E7 C56C39AC BE2C5C35 975C860F D1561439 CB874AAD 858661E1 AE26EDC1 \\r\\n  6ABE3570 FA1320BE 00CCE571 F6AF1238 3260D736 A2F40FE5 703143D1 8C26C17F \\r\\n  A9020301 0001\",\"caServerSupport\":true,\"trustpoint\":\"[{\\\"Certificaterequests\\\":\\\"Yes\\\",\\\"TrustPoint\\\":\\\"TP-self-signed-915488100\\\",\\\"Keysgenerated\\\":\\\"Yes\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"None\\\",\\\"TrustPoint\\\":\\\"SLA-TrustPoint\\\",\\\"Keysgenerated\\\":\\\"No\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"None\\\",\\\"TrustPoint\\\":\\\"WLC_CA\\\",\\\"Keysgenerated\\\":\\\"Yes\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"Yes\\\",\\\"TrustPoint\\\":\\\"TimWLC3_WLC_TP\\\",\\\"Keysgenerated\\\":\\\"Yes\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"Yes\\\",\\\"TrustPoint\\\":\\\"mauriciowlc1_WLC_TP\\\",\\\"Keysgenerated\\\":\\\"Yes\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"None\\\",\\\"TrustPoint\\\":\\\"DNAC-CA\\\",\\\"Keysgenerated\\\":\\\"No\\\",\\\"IssuingCAauthenticated\\\":\\\"No\\\"},{\\\"Certificaterequests\\\":\\\"Yes\\\",\\\"TrustPoint\\\":\\\"dnaspaces1425\\\",\\\"Keysgenerated\\\":\\\"Yes\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"None\\\",\\\"TrustPoint\\\":\\\"dnaspaces1425-rrr1\\\",\\\"Keysgenerated\\\":\\\"No\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"None\\\",\\\"TrustPoint\\\":\\\"LWAVideo\\\",\\\"Keysgenerated\\\":\\\"No\\\",\\\"IssuingCAauthenticated\\\":\\\"No\\\"}]\",\"webAdmin\":\" TimWLC3_WLC_TP\\r\",\"certificate\":{\"mauriciowlc1_WLC_TP\":\"Certificate\\r\\n  Status: Available\\r\\n  Certificate Serial Number (hex): 03\\r\\n  Certificate Usage: General Purpose\\r\\n  Issuer: \\r\\n    o=Cisco Virtual Wireless LAN Controller\\r\\n    cn=CA-vWLC_TimWLC3\\r\\n  Subject:\\r\\n    Name: mauriciowlc1\\r\\n    Serial Number: 9RNA33KM5IH\\r\\n    serialNumber=9RNA33KM5IH+hostname=mauriciowlc1\\r\\n    o=Cisco Virtual Wireless LAN Controller\\r\\n    cn=mauriciowlc1_WLC_TP\\r\\n  Validity Date: \\r\\n    start date: 02:33:54 UTC Mar 11 2024\\r\\n    end   date: 00:02:34 UTC Jul 25 2033\\r\\n  Associated Trustpoints: mauriciowlc1_WLC_TP \\r\\n  Storage: nvram:CiscoVirtual#4.cer\\r\\nCA Certificate\\r\\n  Status: Available\\r\\n  Certificate Serial Number (hex): 01\\r\\n  Certificate Usage: Signature\\r\\n  Issuer: \\r\\n    o=Cisco Virtual Wireless LAN Controller\\r\\n    cn=CA-vWLC_TimWLC3\\r\\n  Subject: \\r\\n    o=Cisco Virtual Wireless LAN Controller\\r\\n    cn=CA-vWLC_TimWLC3\\r\\n  Validity Date: \\r\\n    start date: 00:02:34 UTC Jul 26 2023\\r\\n    end   date: 00:02:34 UTC Jul 25 2033\\r\\n  Associated Trustpoints: mauriciowlc1_WLC_TP TimWLC3_WLC_TP WLC_CA \\r\\n  Storage: nvram:CiscoVirtual#3CA.cer\",\"WLC_CA\":\"CA Certificate\\r\\n  Status: Available\\r\\n  Certificate Serial Number (hex): 01\\r\\n  Certificate Usage: Signature\\r\\n  Issuer: \\r\\n    o=Cisco Virtual Wireless LAN Controller\\r\\n    cn=CA-vWLC_TimWLC3\\r\\n  Subject: \\r\\n    o=Cisco Virtual Wireless LAN Controller\\r\\n    cn=CA-vWLC_TimWLC3\\r\\n  Validity Date: \\r\\n    start date: 00:02:34 UTC Jul 26 2023\\r\\n    end   date: 00:02:34 UTC Jul 25 2033\\r\\n  Associated Trustpoints: mauriciowlc1_WLC_TP TimWLC3_WLC_TP WLC_CA \\r\\n  Storage: nvram:CiscoVirtual#3CA.cer\",\"dnaspaces1425-rrr1\":\"CA Certificate\\r\\n  Status: Available\\r\\n  Certificate Serial Number (hex): 0096C2BF446C2DEEBA\\r\\n  Certificate Usage: Signature\\r\\n  Issuer: \\r\\n    cn=DNASpacesRootCA\\r\\n    ou=DNA Spaces\\r\\n    o=Cisco System Inc\\r\\n    l=San Jose\\r\\n    st=California\\r\\n    c=US\\r\\n  Subject: \\r\\n    cn=DNASpacesRootCA\\r\\n    ou=DNA Spaces\\r\\n    o=Cisco System Inc\\r\\n    l=San Jose\\r\\n    st=California\\r\\n    c=US\\r\\n  Validity Date: \\r\\n    start date: 01:36:23 UTC Apr 4 2020\\r\\n    end   date: 01:36:23 UTC Mar 30 2040\\r\\n  Associated Trustpoints: dnaspaces1425-rrr1 \\r\\n  Storage: nvram:DNASpacesRoo#EEBACA.cer\",\"TimWLC3_WLC_TP\":\"Certificate\\r\\n  Status: Available\\r\\n  Certificate Serial Number (hex): 02\\r\\n  Certificate Usage: General Purpose\\r\\n  Issuer: \\r\\n    o=Cisco Virtual Wireless LAN Controller\\r\\n    cn=CA-vWLC_TimWLC3\\r\\n  Subject:\\r\\n    Name: TimWLC3\\r\\n    Serial Number: 9A5HRRVFBYZ\\r\\n    serialNumber=9A5HRRVFBYZ+hostname=TimWLC3\\r\\n    o=Cisco Virtual Wireless LAN Controller\\r\\n    cn=TimWLC3_WLC_TP\\r\\n  Validity Date: \\r\\n    start date: 00:02:39 UTC Jul 26 2023\\r\\n    end   date: 00:02:34 UTC Jul 25 2033\\r\\n  Associated Trustpoints: TimWLC3_WLC_TP \\r\\n  Storage: nvram:CiscoVirtual#3.cer\\r\\nCA Certificate\\r\\n  Status: Available\\r\\n  Certificate Serial Number (hex): 01\\r\\n  Certificate Usage: Signature\\r\\n  Issuer: \\r\\n    o=Cisco Virtual Wireless LAN Controller\\r\\n    cn=CA-vWLC_TimWLC3\\r\\n  Subject: \\r\\n    o=Cisco Virtual Wireless LAN Controller\\r\\n    cn=CA-vWLC_TimWLC3\\r\\n  Validity Date: \\r\\n    start date: 00:02:34 UTC Jul 26 2023\\r\\n    end   date: 00:02:34 UTC Jul 25 2033\\r\\n  Associated Trustpoints: mauriciowlc1_WLC_TP TimWLC3_WLC_TP WLC_CA \\r\\n  Storage: nvram:CiscoVirtual#3CA.cer\",\"dnaspaces1425\":\"Certificate\\r\\n  Status: Available\\r\\n  Certificate Serial Number (hex): 42525D32C08AAFE0\\r\\n  Certificate Usage: General Purpose\\r\\n  Issuer: \\r\\n    cn=DNASpacesIntermediateCA\\r\\n    ou=DNA Spaces\\r\\n    o=Cisco System Inc\\r\\n    st=California\\r\\n    c=US\\r\\n  Subject:\\r\\n    Name: 192.168.166.6\\r\\n    IP Address: 192.168.166.6\\r\\n    cn=192.168.166.6\\r\\n    o=Cisco\\r\\n    l=SanJose\\r\\n    st=California\\r\\n    c=US\\r\\n  Validity Date: \\r\\n    start date: 19:40:03 UTC Jun 5 2025\\r\\n    end   date: 19:40:03 UTC Jun 3 2035\\r\\n  Associated Trustpoints: dnaspaces1425 \\r\\n  Storage: nvram:DNASpacesInt#AFE0.cer\\r\\nCA Certificate\\r\\n  Status: Available\\r\\n  Certificate Serial Number (hex): 1000\\r\\n  Certificate Usage: Signature\\r\\n  Issuer: \\r\\n    cn=DNASpacesRootCA\\r\\n    ou=DNA Spaces\\r\\n    o=Cisco System Inc\\r\\n    l=San Jose\\r\\n    st=California\\r\\n    c=US\\r\\n  Subject: \\r\\n    cn=DNASpacesIntermediateCA\\r\\n    ou=DNA Spaces\\r\\n    o=Cisco System Inc\\r\\n    st=California\\r\\n    c=US\\r\\n  Validity Date: \\r\\n    start date: 01:43:32 UTC Apr 4 2020\\r\\n    end   date: 01:43:32 UTC Apr 2 2030\\r\\n  Associated Trustpoints: dnaspaces1425 \\r\\n  Storage: nvram:DNASpacesRoo#1000CA.cer\",\"SLA-TrustPoint\":\"CA Certificate\\r\\n  Status: Available\\r\\n  Certificate Serial Number (hex): 01\\r\\n  Certificate Usage: Signature\\r\\n  Issuer: \\r\\n    cn=Cisco Licensing Root CA\\r\\n    o=Cisco\\r\\n  Subject: \\r\\n    cn=Cisco Licensing Root CA\\r\\n    o=Cisco\\r\\n  Validity Date: \\r\\n    start date: 19:48:47 UTC May 30 2013\\r\\n    end   date: 19:48:47 UTC May 30 2038\\r\\n  Associated Trustpoints: Trustpool Trustpool SLA-TrustPoint \\r\\n  Storage: nvram:CiscoLicensi#1CA.cer\",\"TP-self-signed-915488100\":\"Router Self-Signed Certificate\\r\\n  Status: Available\\r\\n  Certificate Serial Number (hex): 01\\r\\n  Certificate Usage: General Purpose\\r\\n  Issuer: \\r\\n    cn=IOS-Self-Signed-Certificate-915488100\\r\\n  Subject:\\r\\n    Name: IOS-Self-Signed-Certificate-915488100\\r\\n    cn=IOS-Self-Signed-Certificate-915488100\\r\\n  Validity Date: \\r\\n    start date: 23:47:26 UTC Jul 25 2023\\r\\n    end   date: 23:47:26 UTC Jul 24 2033\\r\\n  Associated Trustpoints: TP-self-signed-915488100 \\r\\n  Storage: nvram:IOS-Self-Sig#3.cer\"}}\n"
          },
          "redirectURL": "",
          "headersSize": 781,
          "bodySize": 6018
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 1289,
          "receive": 0
        },
        "time": 1289,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:04.016-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:47:03 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 80,
          "receive": 0
        },
        "time": 80,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:04.311-05:00",
        "request": {
          "bodySize": 1563,
          "method": "POST",
          "url": "https://ec.walkme.com/event/tell",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "Host",
              "value": "ec.walkme.com"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "text/html, */*; q=0.01"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "Content-Type",
              "value": "text/plain"
            },
            {
              "name": "Content-Length",
              "value": "1563"
            },
            {
              "name": "Origin",
              "value": "https://172.18.122.131:2274"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "cross-site"
            },
            {
              "name": "TE",
              "value": "trailers"
            }
          ],
          "cookies": [],
          "queryString": [],
          "headersSize": 472,
          "postData": {
            "mimeType": "text/plain",
            "params": [],
            "text": "{\"_static\":true,\"Wm-Client-Timestamp\":1761256024307}\n{\"_enc\":\"bbd%=rk|=3b//,%=zqpezrvk=3zls~y%=zsv}pr=3b/-&.%=wk{vh=3/'/.%=kwxvzw=d%=qzzm|l=3b=/.=%=qpvlmzi=3=lhp{qvH=%=zr~q=d%=lp=3b=/1++.=%=qpvlmzi=3=gpyzmvY=%=zr~q=d%=mzlhpm}=d%=iqz=3bB=/....).=3=&,-*&*.=D%=l{VkqrxL~=3=(,z}{}.-y)&,~.y'-)}+y,,}+}~'/yz*=%={V~lr=3='({'(}'.,(~,2-+*&2}||+2||z'2*+-),{)z=%={Vjzl|=3b=.=%=pyqv=3=*1-.1(.=%=ljk~kl=3=WV*RT,,^QM&=%=zofk=3=/=%=zspm=3=rmpyk~sO?s~jkmvI?zm~hRI?2?S\\\\2//'&\\\\=%=zr~q=d%=lm~Imzlj=3.%=rmpyk~so=3/%=iqz=3.2%={Vrmzo=3={.'-.,/(~//.}}/}-~++(-z|,+y*}+*&=%={Vj=3=mzvyvkqz{V=%=z|mjpL{Vjz=3=?WV*RT,,^QM&2kppm=%={Vjz=d%=rh=3=+|~,,},/y--{2-z(}2(-.+2/,,z2&){y)+~(=%={Vl=3b=-1/1*=%=zo=3=,-}(/yy-2+.|&,..'2*.+/.-2*-&/*-/-=%=}vs=3=((1/1*=%=~m}~=d%=qpvlmzi=3b=0vj}zh0+(--%.,.1--.1'.1-(.00%lokkw=%=mzmmzyzm=3=kqzrzx~q~R?VTO?2?qpvk~mjxvyqp\\\\?2?S\\\\2//'&\\\\?p|lv\\\\?%%^W\\\\SH=%=zskvk=3=y-,+}~~}.}--z.(}.,.+~*{}~.-/(y.(=%={Vkvlvi=3zls~y%=zr~myVlv=3b=zk~|vyvkmz|0<=%=wl~w=3=0vj}zh0=%=zr~qwk~o=3=+(--=%=kmpo=3=.,.1--.1'.1-(.=%=zr~qklpw=3=%lokkw=%=sp|pkpmo=d%=qpvk~|ps=3=).''yy'&~.(}*,.'y|)++'&/(}&,z+y/=%={Vqvh=3b.-,&%=zrvK{~ps=3./&&/***-.)(.%=km~kLi~q=d%=xqvrvk=d%=gk|=3,'(,-/)*-.)(.%=zrvk=3b.%=}rvs|=3=mzkqvpo=%=zofk=d%=|lvr=3b=B=Cqp|VwlzmyzMzx~o=C\\\"{vD^=%=fmzjNpkj~=3=wlzmyzm2~y1~y1B.Dv068wlzmyzm87hp{qvHhpwl\\\"t|vs|2xq90CC0CC%kovm|l~i~u\\\"yzmw9qp|VwlzmyzMzx~o<B'D~0qpvk|zl2szq~o2opk1B-Div{0hzvIqp|Vszq~Oopk1lsppk2szq~o2opk1B-Div{0szq~o2opk1kqzv{~mx2szq~o1gvym~zs|1B.Div{0hpm1zop|l2xq1B.Div{0mzqv~kqp|2qv~r1mzqv~kqp|1B-Div{0oo~2xq<B.Df{p}0B.Dsrkw=%=wk~og=d%=kqzrzsz=3=qhp{zljpr=%=zofk=d\"}"
          }
        },
        "response": {
          "status": 200,
          "statusText": "",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "strict-transport-security",
              "value": "max-age=31536000; includeSubDomains; preload"
            },
            {
              "name": "x-frame-options",
              "value": "DENY"
            },
            {
              "name": "x-xss-protection",
              "value": "1; mode=block"
            },
            {
              "name": "x-content-type-options",
              "value": "nosniff"
            },
            {
              "name": "referrer-policy",
              "value": "strict-origin"
            },
            {
              "name": "cache-control",
              "value": "private, max-age=600"
            },
            {
              "name": "cross-origin-resource-policy",
              "value": "cross-origin"
            },
            {
              "name": "content-security-policy",
              "value": "upgrade-insecure-requests; block-all-mixed-content; default-src 'none'; frame-ancestors: 'none'"
            },
            {
              "name": "access-control-allow-origin",
              "value": "*"
            },
            {
              "name": "content-type",
              "value": "text/html; charset=utf-8"
            },
            {
              "name": "content-length",
              "value": "2"
            },
            {
              "name": "date",
              "value": "Thu, 23 Oct 2025 21:47:04 GMT"
            },
            {
              "name": "via",
              "value": "1.1 google"
            },
            {
              "name": "alt-svc",
              "value": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000"
            },
            {
              "name": "X-Firefox-Spdy",
              "value": "h2"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/html; charset=utf-8",
            "size": 2,
            "text": "ok"
          },
          "redirectURL": "",
          "headersSize": 634,
          "bodySize": 636
        },
        "cache": {},
        "timings": {
          "blocked": -1,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 129,
          "receive": 0
        },
        "time": 129,
        "_securityState": "secure",
        "serverIPAddress": "35.201.109.167",
        "connection": "443",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:05.282-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:47:04 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": -1,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 81,
          "receive": 0
        },
        "time": 81,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:05.283-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:47:04 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 103,
          "receive": 0
        },
        "time": 103,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:05.348-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/monitor/localEap",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 846
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:47:04 GMT"
            },
            {
              "name": "Content-Type",
              "value": "application/json; charset=UTF-8"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Vary",
              "value": "Accept-Encoding"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            },
            {
              "name": "Content-Encoding",
              "value": "gzip"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "application/json; charset=UTF-8",
            "size": 399,
            "text": "{\"localEAPProfiles\":\"eap profile OEAP2_localeap\\r\\n method fast\\r\\nend\",\"eapFastParameters\":{},\"eapTrustPoint\":[{\"TrustPoint\":\"TP-self-signed-915488100\"},{\"TrustPoint\":\"SLA-TrustPoint\"},{\"TrustPoint\":\"WLC_CA\"},{\"TrustPoint\":\"TimWLC3_WLC_TP\"},{\"TrustPoint\":\"mauriciowlc1_WLC_TP\"},{\"TrustPoint\":\"DNAC-CA\"},{\"TrustPoint\":\"dnaspaces1425\"},{\"TrustPoint\":\"dnaspaces1425-rrr1\"},{\"TrustPoint\":\"LWAVideo\"}]}\n"
          },
          "redirectURL": "",
          "headersSize": 781,
          "bodySize": 1002
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 1,
          "connect": 60,
          "ssl": 0,
          "send": 0,
          "wait": 339,
          "receive": 0
        },
        "time": 400,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:07.378-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/lscCertificate?parameters=trustpoint",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            },
            {
              "name": "Priority",
              "value": "u=0"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [
            {
              "name": "parameters",
              "value": "trustpoint"
            }
          ],
          "headersSize": 881
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:47:06 GMT"
            },
            {
              "name": "Content-Type",
              "value": "application/json; charset=UTF-8"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Vary",
              "value": "Accept-Encoding"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            },
            {
              "name": "Content-Encoding",
              "value": "gzip"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "application/json; charset=UTF-8",
            "size": 1182,
            "text": "{\"trustpointLabels\":\"[{\\\"Certificaterequests\\\":\\\"Yes\\\",\\\"TrustPoint\\\":\\\"TP-self-signed-915488100\\\",\\\"Keysgenerated\\\":\\\"Yes\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"None\\\",\\\"TrustPoint\\\":\\\"SLA-TrustPoint\\\",\\\"Keysgenerated\\\":\\\"No\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"None\\\",\\\"TrustPoint\\\":\\\"WLC_CA\\\",\\\"Keysgenerated\\\":\\\"Yes\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"Yes\\\",\\\"TrustPoint\\\":\\\"TimWLC3_WLC_TP\\\",\\\"Keysgenerated\\\":\\\"Yes\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"Yes\\\",\\\"TrustPoint\\\":\\\"mauriciowlc1_WLC_TP\\\",\\\"Keysgenerated\\\":\\\"Yes\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"None\\\",\\\"TrustPoint\\\":\\\"DNAC-CA\\\",\\\"Keysgenerated\\\":\\\"No\\\",\\\"IssuingCAauthenticated\\\":\\\"No\\\"},{\\\"Certificaterequests\\\":\\\"Yes\\\",\\\"TrustPoint\\\":\\\"dnaspaces1425\\\",\\\"Keysgenerated\\\":\\\"Yes\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"None\\\",\\\"TrustPoint\\\":\\\"dnaspaces1425-rrr1\\\",\\\"Keysgenerated\\\":\\\"No\\\",\\\"IssuingCAauthenticated\\\":\\\"Yes\\\"},{\\\"Certificaterequests\\\":\\\"None\\\",\\\"TrustPoint\\\":\\\"LWAVideo\\\",\\\"Keysgenerated\\\":\\\"No\\\",\\\"IssuingCAauthenticated\\\":\\\"No\\\"}]\"}\n"
          },
          "redirectURL": "",
          "headersSize": 781,
          "bodySize": 1059
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 175,
          "receive": 0
        },
        "time": 175,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:07.402-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:47:06 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 81,
          "receive": 0
        },
        "time": 81,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:07.560-05:00",
        "request": {
          "bodySize": 1728,
          "method": "POST",
          "url": "https://ec.walkme.com/event/tell",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "Host",
              "value": "ec.walkme.com"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "text/html, */*; q=0.01"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "Content-Type",
              "value": "text/plain"
            },
            {
              "name": "Content-Length",
              "value": "1728"
            },
            {
              "name": "Origin",
              "value": "https://172.18.122.131:2274"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "cross-site"
            }
          ],
          "cookies": [],
          "queryString": [],
          "headersSize": 472,
          "postData": {
            "mimeType": "text/plain",
            "params": [],
            "text": "{\"_static\":true,\"Wm-Client-Timestamp\":1761256027547}\n{\"_enc\":\"bbd%=rk|=3b//,%=zqpezrvk=3zls~y%=zsv}pr=3b/-&.%=wk{vh=3/'/.%=kwxvzw=d%=qzzm|l=3b=/.=%=qpvlmzi=3=lhp{qvH=%=zr~q=d%=lp=3b=/1++.=%=qpvlmzi=3=gpyzmvY=%=zr~q=d%=mzlhpm}=d%=iqz=3bB=/....).=3=&,-*&*.=D%=l{VkqrxL~=3=(,z}{}.-y)&,~.y'-)}+y,,}+}~'/yz*=%={V~lr=3='({'(}'.,(~,2-+*&2}||+2||z'2*+-),{)z=%={Vjzl|=3b=.=%=pyqv=3=*1-.1(.=%=ljk~kl=3=WV*RT,,^QM&=%=zofk=3=/=%=zspm=3=rmpyk~sO?s~jkmvI?zm~hRI?2?S\\\\2//'&\\\\=%=zr~q=d%=lm~Imzlj=3.%=rmpyk~so=3/%=iqz=3.2%={Vrmzo=3={.'-.,/(~//.}}/}-~++(-z|,+y*}+*&=%={Vj=3=mzvyvkqz{V=%=z|mjpL{Vjz=3=?WV*RT,,^QM&2kppm=%={Vjz=d%=rh=3=+|~,,},/y--{2-z(}2(-.+2/,,z2&){y)+~(=%={Vl=3b=-1/1*=%=zo=3=,-}(/yy-2+.|&,..'2*.+/.-2*-&/*-/-=%=}vs=3=((1/1*=%=~m}~=d%=qpvlmzi=3b=0vj}zh0+(--%.,.1--.1'.1-(.00%lokkw=%=mzmmzyzm=3=kqzrzx~q~R?VTO?2?qpvk~mjxvyqp\\\\?2?S\\\\2//'&\\\\?p|lv\\\\?%%^W\\\\SH=%=zskvk=3=y-,+}~~}.}--z.(}.,.+~*{}~.-/(y.(=%={Vkvlvi=3zls~y%=zr~myVlv=3b=zk~|vyvkmz|0<=%=wl~w=3=0vj}zh0=%=zr~qwk~o=3=+(--=%=kmpo=3=.,.1--.1'.1-(.=%=zr~qklpw=3=%lokkw=%=sp|pkpmo=d%=qpvk~|ps=3=).''yy'&~.(}*,.'y|)++'&/(}&,z+y/=%={Vqvh=3b.-,&%=zrvK{~ps=3./&&/***-.)(.%=km~kLi~q=d%=xqvrvk=d%=gk|=3((-(-/)*-.)(.%=zrvk=3b.%=}rvs|=3=mzkqvpo=%=zofk=d%=|lvr=3b=zk~|vyvkmz\\\\?{{^=%=kgzk=3=VS?SJ?B=Coo~2xq=C\\\"{vDF[P]=%=fmzjNpkj~=3=tqvs2t1B-Dq~ol0}~k\\\"zspm967}~Kqpvk~mzqzXzk~|vyvkmz\\\\z|viz[zlvs~vkvqv\\\"t|vs|2xq9xqv{qv}2xq1mzipw2zk~kl2t1ksj~yz{2zk~kl2t1rzkv2t1B+Dvs0lrzkv2ovmkl}~k2t1kzlzm2t1B.Dsj0klvs}~k\\\"zspm9kzx{vh2t1opk2ovmkl}~k2t1ovmkl}~k2t1mz{~zw2t1o~mhk~psy2t1B.Div{0mzoo~mh2ovmkl}~k2t1B.Div{0B-Div{0zop|l2xq1B.Div{0zop|l2xq1B-Div{0mzqv~kqp|2vj}zh1B-Div{0qv~r1B-Div{0hpm1zop|l2xq1B.Div{0mzqv~kqp|2qv~r1mzqv~kqp|1B-Div{0oo~2xq<B.Df{p}0B.Dsrkw=%=wk~og=d%=kqzrzsz=3=qhp{zljpr=%=zofk=d\"}"
          }
        },
        "response": {
          "status": 200,
          "statusText": "",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "strict-transport-security",
              "value": "max-age=31536000; includeSubDomains; preload"
            },
            {
              "name": "x-frame-options",
              "value": "DENY"
            },
            {
              "name": "x-xss-protection",
              "value": "1; mode=block"
            },
            {
              "name": "x-content-type-options",
              "value": "nosniff"
            },
            {
              "name": "referrer-policy",
              "value": "strict-origin"
            },
            {
              "name": "cache-control",
              "value": "private, max-age=600"
            },
            {
              "name": "cross-origin-resource-policy",
              "value": "cross-origin"
            },
            {
              "name": "content-security-policy",
              "value": "upgrade-insecure-requests; block-all-mixed-content; default-src 'none'; frame-ancestors: 'none'"
            },
            {
              "name": "access-control-allow-origin",
              "value": "*"
            },
            {
              "name": "content-type",
              "value": "text/html; charset=utf-8"
            },
            {
              "name": "content-length",
              "value": "2"
            },
            {
              "name": "date",
              "value": "Thu, 23 Oct 2025 21:47:07 GMT"
            },
            {
              "name": "via",
              "value": "1.1 google"
            },
            {
              "name": "alt-svc",
              "value": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000"
            },
            {
              "name": "X-Firefox-Spdy",
              "value": "h2"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/html; charset=utf-8",
            "size": 2,
            "text": "ok"
          },
          "redirectURL": "",
          "headersSize": 634,
          "bodySize": 636
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 129,
          "receive": 0
        },
        "time": 129,
        "_securityState": "secure",
        "serverIPAddress": "35.201.109.167",
        "connection": "443",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:10.720-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:47:09 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 78,
          "receive": 0
        },
        "time": 78,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:10.873-05:00",
        "request": {
          "bodySize": 2031,
          "method": "POST",
          "url": "https://ec.walkme.com/event/tell",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "Host",
              "value": "ec.walkme.com"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "text/html, */*; q=0.01"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "Content-Type",
              "value": "text/plain"
            },
            {
              "name": "Content-Length",
              "value": "2031"
            },
            {
              "name": "Origin",
              "value": "https://172.18.122.131:2274"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "cross-site"
            }
          ],
          "cookies": [],
          "queryString": [],
          "headersSize": 472,
          "postData": {
            "mimeType": "text/plain",
            "params": [],
            "text": "{\"_static\":true,\"Wm-Client-Timestamp\":1761256030870}\n{\"_enc\":\"bbd%=rk|=3b//,%=zqpezrvk=3zls~y%=zsv}pr=3b/-&.%=wk{vh=3/'/.%=kwxvzw=d%=qzzm|l=3b=/.=%=qpvlmzi=3=lhp{qvH=%=zr~q=d%=lp=3b=/1++.=%=qpvlmzi=3=gpyzmvY=%=zr~q=d%=mzlhpm}=d%=iqz=3bB=/....).=3=&,-*&*.=D%=l{VkqrxL~=3=(,z}{}.-y)&,~.y'-)}+y,,}+}~'/yz*=%={V~lr=3='({'(}'.,(~,2-+*&2}||+2||z'2*+-),{)z=%={Vjzl|=3b=.=%=pyqv=3=*1-.1(.=%=ljk~kl=3=WV*RT,,^QM&=%=zofk=3=/=%=zspm=3=rmpyk~sO?s~jkmvI?zm~hRI?2?S\\\\2//'&\\\\=%=zr~q=d%=lm~Imzlj=3.%=rmpyk~so=3/%=iqz=3.2%={Vrmzo=3={.'-.,/(~//.}}/}-~++(-z|,+y*}+*&=%={Vj=3=mzvyvkqz{V=%=z|mjpL{Vjz=3=?WV*RT,,^QM&2kppm=%={Vjz=d%=rh=3=+|~,,},/y--{2-z(}2(-.+2/,,z2&){y)+~(=%={Vl=3b=-1/1*=%=zo=3=,-}(/yy-2+.|&,..'2*.+/.-2*-&/*-/-=%=}vs=3=((1/1*=%=~m}~=d%=qpvlmzi=3b=0vj}zh0+(--%.,.1--.1'.1-(.00%lokkw=%=mzmmzyzm=3=kqzrzx~q~R?VTO?2?qpvk~mjxvyqp\\\\?2?S\\\\2//'&\\\\?p|lv\\\\?%%^W\\\\SH=%=zskvk=3=y-,+}~~}.}--z.(}.,.+~*{}~.-/(y.(=%={Vkvlvi=3zls~y%=zr~myVlv=3b=zk~|vyvkmz|0<=%=wl~w=3=0vj}zh0=%=zr~qwk~o=3=+(--=%=kmpo=3=.,.1--.1'.1-(.=%=zr~qklpw=3=%lokkw=%=sp|pkpmo=d%=qpvk~|ps=3=).''yy'&~.(}*,.'y|)++'&/(}&,z+y/=%={Vqvh=3b.-,&%=zrvK{~ps=3./&&/***-.)(.%=km~kLi~q=d%=xqvrvk=d%=gk|=3./)/,/)*-.)(.%=zrvk=3b-%=}rvs|=3=mzkqvpo=%=zofk=d%=|lvr=3b=klzjnzM?xqvqxvL?zk~|vyvkmz\\\\?zk~mzqzX=%=kgzk=3=Q^OL?VS?SJ?B=Coo~2xq=C\\\"{vDF[P]=%=fmzjNpkj~=3=zskvk@@m~}szq~o1xqv{qv}2xq1B-Div{0szq~OML\\\\\\\"zr~q9mz{~zw@@m~}szq~o1zjs}2kqzv{~mx2szq~o1gvym~zs|1B.Dq~ol0mzipw2zk~kl2t1tqvs2t1mz{~zw2t1B.Dq~ol0rzkvjqzr\\\"zspm9ksj~yz{2zk~kl2t1kl~s2t1rzkv2t1klmvy2t1B.Dvs0jqzr\\\"zspm9m~}szq~o1zop|l2xq1kzx{vh2t1kzlzm2t1m~}szq~o2t1mz{~zw2t1ojpmx2rmpy1B.Dsj08srkw1CChzvIml|0CClhzvi0CCzk~|vyvkmz|0CClzmjk~zy8\\\"|ml9zop|l2xq1B.Div{0szq~o}~k\\\"zspm9zivk|~2zk~kl2t1kqzkqp|2t1+2&||~||'{{)zz2&,}~2+z,+2*&),2&&&)z~y+<B+Div{0klvs}~k\\\"zspm9kzx{vh2t1opk2ovmkl}~k2t1ovmkl}~k2t1mz{~zw2t1o~mhk~psy2t1B.Div{0mzoo~mh2ovmkl}~k2t1B.Div{0B-Div{0zop|l2xq1B.Div{0zop|l2xq1B-Div{0mzqv~kqp|2vj}zh1B-Div{0qv~r1B-Div{0hpm1zop|l2xq1B.Div{0mzqv~kqp|2qv~r1mzqv~kqp|1B-Div{0oo~2xq<B.Df{p}0B.Dsrkw=%=wk~og=d%=kqzrzsz=3=qhp{zljpr=%=zofk=d\"}"
          }
        },
        "response": {
          "status": 200,
          "statusText": "",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "strict-transport-security",
              "value": "max-age=31536000; includeSubDomains; preload"
            },
            {
              "name": "x-frame-options",
              "value": "DENY"
            },
            {
              "name": "x-xss-protection",
              "value": "1; mode=block"
            },
            {
              "name": "x-content-type-options",
              "value": "nosniff"
            },
            {
              "name": "referrer-policy",
              "value": "strict-origin"
            },
            {
              "name": "cache-control",
              "value": "private, max-age=600"
            },
            {
              "name": "cross-origin-resource-policy",
              "value": "cross-origin"
            },
            {
              "name": "content-security-policy",
              "value": "upgrade-insecure-requests; block-all-mixed-content; default-src 'none'; frame-ancestors: 'none'"
            },
            {
              "name": "access-control-allow-origin",
              "value": "*"
            },
            {
              "name": "content-type",
              "value": "text/html; charset=utf-8"
            },
            {
              "name": "content-length",
              "value": "2"
            },
            {
              "name": "date",
              "value": "Thu, 23 Oct 2025 21:47:11 GMT"
            },
            {
              "name": "via",
              "value": "1.1 google"
            },
            {
              "name": "alt-svc",
              "value": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000"
            },
            {
              "name": "X-Firefox-Spdy",
              "value": "h2"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/html; charset=utf-8",
            "size": 2,
            "text": "ok"
          },
          "redirectURL": "",
          "headersSize": 634,
          "bodySize": 636
        },
        "cache": {},
        "timings": {
          "blocked": 1,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 130,
          "receive": 5
        },
        "time": 136,
        "_securityState": "secure",
        "serverIPAddress": "35.201.109.167",
        "connection": "443",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:24.139-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:47:23 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 81,
          "receive": 0
        },
        "time": 81,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:24.339-05:00",
        "request": {
          "bodySize": 2407,
          "method": "POST",
          "url": "https://ec.walkme.com/event/tell",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "Host",
              "value": "ec.walkme.com"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "text/html, */*; q=0.01"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "Content-Type",
              "value": "text/plain"
            },
            {
              "name": "Content-Length",
              "value": "2407"
            },
            {
              "name": "Origin",
              "value": "https://172.18.122.131:2274"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "cross-site"
            },
            {
              "name": "TE",
              "value": "trailers"
            }
          ],
          "cookies": [],
          "queryString": [],
          "headersSize": 472,
          "postData": {
            "mimeType": "text/plain",
            "params": [],
            "text": "{\"_static\":true,\"Wm-Client-Timestamp\":1761256044335}\n{\"_enc\":\"bbd%=rk|=3b//,%=zqpezrvk=3zls~y%=zsv}pr=3b/-&.%=wk{vh=3/'/.%=kwxvzw=d%=qzzm|l=3b=/.=%=qpvlmzi=3=lhp{qvH=%=zr~q=d%=lp=3b=/1++.=%=qpvlmzi=3=gpyzmvY=%=zr~q=d%=mzlhpm}=d%=iqz=3bB=/....).=3=&,-*&*.=D%=l{VkqrxL~=3=(,z}{}.-y)&,~.y'-)}+y,,}+}~'/yz*=%={V~lr=3='({'(}'.,(~,2-+*&2}||+2||z'2*+-),{)z=%={Vjzl|=3b=.=%=pyqv=3=*1-.1(.=%=ljk~kl=3=WV*RT,,^QM&=%=zofk=3=/=%=zspm=3=rmpyk~sO?s~jkmvI?zm~hRI?2?S\\\\2//'&\\\\=%=zr~q=d%=lm~Imzlj=3.%=rmpyk~so=3/%=iqz=3.2%={Vrmzo=3={.'-.,/(~//.}}/}-~++(-z|,+y*}+*&=%={Vj=3=mzvyvkqz{V=%=z|mjpL{Vjz=3=?WV*RT,,^QM&2kppm=%={Vjz=d%=rh=3=+|~,,},/y--{2-z(}2(-.+2/,,z2&){y)+~(=%={Vl=3b=-1/1*=%=zo=3=,-}(/yy-2+.|&,..'2*.+/.-2*-&/*-/-=%=}vs=3=((1/1*=%=~m}~=d%=qpvlmzi=3b=0vj}zh0+(--%.,.1--.1'.1-(.00%lokkw=%=mzmmzyzm=3=kqzrzx~q~R?VTO?2?qpvk~mjxvyqp\\\\?2?S\\\\2//'&\\\\?p|lv\\\\?%%^W\\\\SH=%=zskvk=3=y-,+}~~}.}--z.(}.,.+~*{}~.-/(y.(=%={Vkvlvi=3zls~y%=zr~myVlv=3b=zk~|vyvkmz|0<=%=wl~w=3=0vj}zh0=%=zr~qwk~o=3=+(--=%=kmpo=3=.,.1--.1'.1-(.=%=zr~qklpw=3=%lokkw=%=sp|pkpmo=d%=qpvk~|ps=3=).''yy'&~.(}*,.'y|)++'&/(}&,z+y/=%={Vqvh=3b.-,&%=zrvK{~ps=3./&&/***-.)(.%=km~kLi~q=d%=xqvrvk=d%=gk|=3)-/++/)*-.)(.%=zrvk=3b(%=}rvs|=3=zkj}vmkk~=%=zofk=d%=|lvr=3b=zk~mzqzXqCzr~Q?qv~rp[qCqpvk~evq~xmPqCkvqJ?s~qpvk~evq~xmPqCqpvk~|pSqCzk~kLqCz{p\\\\?fmkqjp\\\\qCzr~Q?fzTqCzr~Q?zk~|vyvkmz\\\\qCklzjnzM?xqvqxvL?zk~|vyvkmz\\\\?zk~mzqzX=%=kgzk=3=SJ?B=Coo~2xq=C\\\"{vDF[P]=%=fmzjNpkj~=3=kgzk\\\"zofk9zr~Qml|\\\"zr~q9{zw|jpkqj2xq1zqvklvmo2xq1{zmvjnzm2{vs~iqv2xq1{vs~iqv2xq1fkorz2xq1gp}kgzk2t1spmkqp|2rmpy1{Vzr~Qml|<B.Dkjoqv0kjoqv{szvy1,2rl2sp|1B-Div{0hpm1go/-2opk2qvxm~r1ojpmx2rmpy1B.Div{0'2rl2sp|1B.Div{0rmpYml|\\\"zr~q9zlm~o2{vs~i2xq1zqvklvmo2xq1{zmvjnzm2{vs~iqv2xq1{vs~iqv2xq1zsfkLqpvk~{vs~IrmpYhzq1{VrmpYml|<B.Drmpy0qpvxzm\\\"zspm9hpm1kqzkqp|2t1ojpmx2rmpy1B.Div{0rzkvjqzr\\\"zspm9kwxvswxvw2zk~kl2t1ksj~yz{2zk~kl2t1zivk|~2zk~kl2t1kl~s2t1rzkv2t1klmvy2t1B.Dvs0jqzr\\\"zspm9m~}szq~o1zop|l2xq1kzx{vh2t1kzlzm2t1m~}szq~o2t1mz{~zw2t1ojpmx2rmpy1B.Dsj08srkw1CChzvIml|0CClhzvi0CCzk~|vyvkmz|0CClzmjk~zy8\\\"|ml9zop|l2xq1B.Div{0szq~o}~k\\\"zspm9zivk|~2zk~kl2t1kqzkqp|2t1+2&||~||'{{)zz2&,}~2+z,+2*&),2&&&)z~y+<B+Div{0klvs}~k\\\"zspm9kzx{vh2t1opk2ovmkl}~k2t1ovmkl}~k2t1mz{~zw2t1o~mhk~psy2t1B.Div{0mzoo~mh2ovmkl}~k2t1B.Div{0B-Div{0zop|l2xq1B.Div{0zop|l2xq1B-Div{0mzqv~kqp|2vj}zh1B-Div{0qv~r1B-Div{0hpm1zop|l2xq1B.Div{0mzqv~kqp|2qv~r1mzqv~kqp|1B-Div{0oo~2xq<B.Df{p}0B.Dsrkw=%=wk~og=d%=kqzrzsz=3=qhp{zljpr=%=zofk=d\"}"
          }
        },
        "response": {
          "status": 200,
          "statusText": "",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "strict-transport-security",
              "value": "max-age=31536000; includeSubDomains; preload"
            },
            {
              "name": "x-frame-options",
              "value": "DENY"
            },
            {
              "name": "x-xss-protection",
              "value": "1; mode=block"
            },
            {
              "name": "x-content-type-options",
              "value": "nosniff"
            },
            {
              "name": "referrer-policy",
              "value": "strict-origin"
            },
            {
              "name": "cache-control",
              "value": "private, max-age=600"
            },
            {
              "name": "cross-origin-resource-policy",
              "value": "cross-origin"
            },
            {
              "name": "content-security-policy",
              "value": "upgrade-insecure-requests; block-all-mixed-content; default-src 'none'; frame-ancestors: 'none'"
            },
            {
              "name": "access-control-allow-origin",
              "value": "*"
            },
            {
              "name": "content-type",
              "value": "text/html; charset=utf-8"
            },
            {
              "name": "content-length",
              "value": "2"
            },
            {
              "name": "date",
              "value": "Thu, 23 Oct 2025 21:47:24 GMT"
            },
            {
              "name": "via",
              "value": "1.1 google"
            },
            {
              "name": "alt-svc",
              "value": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000"
            },
            {
              "name": "X-Firefox-Spdy",
              "value": "h2"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/html; charset=utf-8",
            "size": 2,
            "text": "ok"
          },
          "redirectURL": "",
          "headersSize": 634,
          "bodySize": 636
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 128,
          "receive": 0
        },
        "time": 128,
        "_securityState": "secure",
        "serverIPAddress": "35.201.109.167",
        "connection": "443",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:26.709-05:00",
        "request": {
          "bodySize": 2232,
          "method": "POST",
          "url": "https://ec.walkme.com/event/tell",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "Host",
              "value": "ec.walkme.com"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "text/html, */*; q=0.01"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "Content-Type",
              "value": "text/plain"
            },
            {
              "name": "Content-Length",
              "value": "2232"
            },
            {
              "name": "Origin",
              "value": "https://172.18.122.131:2274"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "cross-site"
            },
            {
              "name": "TE",
              "value": "trailers"
            }
          ],
          "cookies": [],
          "queryString": [],
          "headersSize": 472,
          "postData": {
            "mimeType": "text/plain",
            "params": [],
            "text": "{\"_static\":true,\"Wm-Client-Timestamp\":1761256046705}\n{\"_enc\":\"bbd%=rk|=3b//,%=zqpezrvk=3zls~y%=zsv}pr=3b/-&.%=wk{vh=3/'/.%=kwxvzw=d%=qzzm|l=3b=/.=%=qpvlmzi=3=lhp{qvH=%=zr~q=d%=lp=3b=/1++.=%=qpvlmzi=3=gpyzmvY=%=zr~q=d%=mzlhpm}=d%=iqz=3bB=/....).=3=&,-*&*.=D%=l{VkqrxL~=3=(,z}{}.-y)&,~.y'-)}+y,,}+}~'/yz*=%={V~lr=3='({'(}'.,(~,2-+*&2}||+2||z'2*+-),{)z=%={Vjzl|=3b=.=%=pyqv=3=*1-.1(.=%=ljk~kl=3=WV*RT,,^QM&=%=zofk=3=/=%=zspm=3=rmpyk~sO?s~jkmvI?zm~hRI?2?S\\\\2//'&\\\\=%=zr~q=d%=lm~Imzlj=3.%=rmpyk~so=3/%=iqz=3.2%={Vrmzo=3={.'-.,/(~//.}}/}-~++(-z|,+y*}+*&=%={Vj=3=mzvyvkqz{V=%=z|mjpL{Vjz=3=?WV*RT,,^QM&2kppm=%={Vjz=d%=rh=3=+|~,,},/y--{2-z(}2(-.+2/,,z2&){y)+~(=%={Vl=3b=-1/1*=%=zo=3=,-}(/yy-2+.|&,..'2*.+/.-2*-&/*-/-=%=}vs=3=((1/1*=%=~m}~=d%=qpvlmzi=3b=0vj}zh0+(--%.,.1--.1'.1-(.00%lokkw=%=mzmmzyzm=3=kqzrzx~q~R?VTO?2?qpvk~mjxvyqp\\\\?2?S\\\\2//'&\\\\?p|lv\\\\?%%^W\\\\SH=%=zskvk=3=y-,+}~~}.}--z.(}.,.+~*{}~.-/(y.(=%={Vkvlvi=3zls~y%=zr~myVlv=3b=zk~|vyvkmz|0<=%=wl~w=3=0vj}zh0=%=zr~qwk~o=3=+(--=%=kmpo=3=.,.1--.1'.1-(.=%=zr~qklpw=3=%lokkw=%=sp|pkpmo=d%=qpvk~|ps=3=).''yy'&~.(}*,.'y|)++'&/(}&,z+y/=%={Vqvh=3b.-,&%=zrvK{~ps=3./&&/***-.)(.%=km~kLi~q=d%=xqvrvk=d%=gk|=3),+)+/)*-.)(.%=zrvk=3b=klzkklzkklzk=%=zjs~i=3=B=C{Vzr~Qml|=C\\\"{vDKJOQV=%=fmzjNpkj~=3=kgzk\\\"zofk9zr~Qml|\\\"zr~q9{zmvjnzm2{vs~i2xq1zlm~o2{vs~i2xq1{vs~i2xq1{zw|jpkqj2xq1fkorz2kpq2xq1fkmv{2xq1gp}kgzk2t1spmkqp|2rmpy1{Vzr~Qml|<B.Dkjoqv0kjoqv{szvy1,2rl2sp|1B-Div{0hpm1go/-2opk2qvxm~r1ojpmx2rmpy1B.Div{0'2rl2sp|1B.Div{0rmpYml|\\\"zr~q9zlm~o2{vs~i2xq1{zmvjnzm2{vs~iqv2xq1{vs~iqv2xq1fkmv{2xq1zsfkLqpvk~{vs~IrmpYhzq1{VrmpYml|<B.Drmpy0qpvxzm\\\"zspm9hpm1kqzkqp|2t1ojpmx2rmpy1B.Div{0rzkvjqzr\\\"zspm9kwxvswxvw2zk~kl2t1ksj~yz{2zk~kl2t1zivk|~2zk~kl2t1kl~s2t1rzkv2t1klmvy2t1B.Dvs0jqzr\\\"zspm9m~}szq~o1zop|l2xq1kzx{vh2t1kzlzm2t1m~}szq~o2t1mz{~zw2t1ojpmx2rmpy1B.Dsj08srkw1CChzvIml|0CClhzvi0CCzk~|vyvkmz|0CClzmjk~zy8\\\"|ml9zop|l2xq1B.Div{0szq~o}~k\\\"zspm9zivk|~2zk~kl2t1kqzkqp|2t1+2&||~||'{{)zz2&,}~2+z,+2*&),2&&&)z~y+<B+Div{0klvs}~k\\\"zspm9kzx{vh2t1opk2ovmkl}~k2t1ovmkl}~k2t1mz{~zw2t1o~mhk~psy2t1B.Div{0mzoo~mh2ovmkl}~k2t1B.Div{0B-Div{0zop|l2xq1B.Div{0zop|l2xq1B-Div{0mzqv~kqp|2vj}zh1B-Div{0qv~r1B-Div{0hpm1zop|l2xq1B.Div{0mzqv~kqp|2qv~r1mzqv~kqp|1B-Div{0oo~2xq<B.Df{p}0B.Dsrkw=%=wk~og=d%=kqzrzsz=3=zxq~w|=%=zofk=d\"}"
          }
        },
        "response": {
          "status": 200,
          "statusText": "",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "strict-transport-security",
              "value": "max-age=31536000; includeSubDomains; preload"
            },
            {
              "name": "x-frame-options",
              "value": "DENY"
            },
            {
              "name": "x-xss-protection",
              "value": "1; mode=block"
            },
            {
              "name": "x-content-type-options",
              "value": "nosniff"
            },
            {
              "name": "referrer-policy",
              "value": "strict-origin"
            },
            {
              "name": "cache-control",
              "value": "private, max-age=600"
            },
            {
              "name": "cross-origin-resource-policy",
              "value": "cross-origin"
            },
            {
              "name": "content-security-policy",
              "value": "upgrade-insecure-requests; block-all-mixed-content; default-src 'none'; frame-ancestors: 'none'"
            },
            {
              "name": "access-control-allow-origin",
              "value": "*"
            },
            {
              "name": "content-type",
              "value": "text/html; charset=utf-8"
            },
            {
              "name": "content-length",
              "value": "2"
            },
            {
              "name": "date",
              "value": "Thu, 23 Oct 2025 21:47:26 GMT"
            },
            {
              "name": "via",
              "value": "1.1 google"
            },
            {
              "name": "alt-svc",
              "value": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000"
            },
            {
              "name": "X-Firefox-Spdy",
              "value": "h2"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/html; charset=utf-8",
            "size": 2,
            "text": "ok"
          },
          "redirectURL": "",
          "headersSize": 634,
          "bodySize": 636
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 130,
          "receive": 0
        },
        "time": 130,
        "_securityState": "secure",
        "serverIPAddress": "35.201.109.167",
        "connection": "443",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:28.866-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:47:27 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": -1,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 84,
          "receive": 0
        },
        "time": 84,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:28.996-05:00",
        "request": {
          "bodySize": 2395,
          "method": "POST",
          "url": "https://ec.walkme.com/event/tell",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "Host",
              "value": "ec.walkme.com"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "text/html, */*; q=0.01"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "Content-Type",
              "value": "text/plain"
            },
            {
              "name": "Content-Length",
              "value": "2395"
            },
            {
              "name": "Origin",
              "value": "https://172.18.122.131:2274"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "cross-site"
            },
            {
              "name": "TE",
              "value": "trailers"
            }
          ],
          "cookies": [],
          "queryString": [],
          "headersSize": 472,
          "postData": {
            "mimeType": "text/plain",
            "params": [],
            "text": "{\"_static\":true,\"Wm-Client-Timestamp\":1761256048993}\n{\"_enc\":\"bbd%=rk|=3b//,%=zqpezrvk=3zls~y%=zsv}pr=3b/-&.%=wk{vh=3/'/.%=kwxvzw=d%=qzzm|l=3b=/.=%=qpvlmzi=3=lhp{qvH=%=zr~q=d%=lp=3b=/1++.=%=qpvlmzi=3=gpyzmvY=%=zr~q=d%=mzlhpm}=d%=iqz=3bB=/....).=3=&,-*&*.=D%=l{VkqrxL~=3=(,z}{}.-y)&,~.y'-)}+y,,}+}~'/yz*=%={V~lr=3='({'(}'.,(~,2-+*&2}||+2||z'2*+-),{)z=%={Vjzl|=3b=.=%=pyqv=3=*1-.1(.=%=ljk~kl=3=WV*RT,,^QM&=%=zofk=3=/=%=zspm=3=rmpyk~sO?s~jkmvI?zm~hRI?2?S\\\\2//'&\\\\=%=zr~q=d%=lm~Imzlj=3.%=rmpyk~so=3/%=iqz=3.2%={Vrmzo=3={.'-.,/(~//.}}/}-~++(-z|,+y*}+*&=%={Vj=3=mzvyvkqz{V=%=z|mjpL{Vjz=3=?WV*RT,,^QM&2kppm=%={Vjz=d%=rh=3=+|~,,},/y--{2-z(}2(-.+2/,,z2&){y)+~(=%={Vl=3b=-1/1*=%=zo=3=,-}(/yy-2+.|&,..'2*.+/.-2*-&/*-/-=%=}vs=3=((1/1*=%=~m}~=d%=qpvlmzi=3b=0vj}zh0+(--%.,.1--.1'.1-(.00%lokkw=%=mzmmzyzm=3=kqzrzx~q~R?VTO?2?qpvk~mjxvyqp\\\\?2?S\\\\2//'&\\\\?p|lv\\\\?%%^W\\\\SH=%=zskvk=3=y-,+}~~}.}--z.(}.,.+~*{}~.-/(y.(=%={Vkvlvi=3zls~y%=zr~myVlv=3b=zk~|vyvkmz|0<=%=wl~w=3=0vj}zh0=%=zr~qwk~o=3=+(--=%=kmpo=3=.,.1--.1'.1-(.=%=zr~qklpw=3=%lokkw=%=sp|pkpmo=d%=qpvk~|ps=3=).''yy'&~.(}*,.'y|)++'&/(}&,z+y/=%={Vqvh=3b.-,&%=zrvK{~ps=3./&&/***-.)(.%=km~kLi~q=d%=xqvrvk=d%=gk|=3/,('+/)*-.)(.%=zrvk=3b.%=}rvs|=3=mzkqvpo=%=zofk=d%=|lvr=3b=Q^OL?B=C{VrmpYml|=C\\\"{vDRMPY=%=fmzjNpkj~=3=qp|v2t1qhp{2/)2hpmm~2v2t1B.Dq~ol0qpkkj}\\\"zspm9k|zszl2t1B-Dq~ol0mzipw2zk~kl2t1{zlj|py2zk~kl2t1ksj~yz{2zk~kl2t1o~mh2qhp{opm{2t1B.Dq~ol0zlm~o2{vs~i2xq1{zw|jpkqj2xq1zqvklvmo2xq1{zmvjnzm2{vs~iqv2xq1{vs~iqv2xq1fkorz2xq1kzx{vh2t1zs}~m~zs|2gp}p}rp|2t1gp}p}rp|2t1B.Dq~ol0{vmXzqvsqVf~solv{1B.Div{0kjoqv{szvy1,2rl2sp|1B+Div{0hpm1go/-2opk2qvxm~r1ojpmx2rmpy1B.Div{0'2rl2sp|1B.Div{0rmpYml|\\\"zr~q9zlm~o2{vs~i2xq1{zmvjnzm2{vs~iqv2xq1{vs~iqv2xq1fkmv{2xq1zsfkLqpvk~{vs~IrmpYhzq1{VrmpYml|<B.Drmpy0qpvxzm\\\"zspm9hpm1kqzkqp|2t1ojpmx2rmpy1B.Div{0rzkvjqzr\\\"zspm9kwxvswxvw2zk~kl2t1ksj~yz{2zk~kl2t1zivk|~2zk~kl2t1kl~s2t1rzkv2t1klmvy2t1B.Dvs0jqzr\\\"zspm9m~}szq~o1zop|l2xq1kzx{vh2t1kzlzm2t1m~}szq~o2t1mz{~zw2t1ojpmx2rmpy1B.Dsj08srkw1CChzvIml|0CClhzvi0CCzk~|vyvkmz|0CClzmjk~zy8\\\"|ml9zop|l2xq1B.Div{0szq~o}~k\\\"zspm9zivk|~2zk~kl2t1kqzkqp|2t1+2&||~||'{{)zz2&,}~2+z,+2*&),2&&&)z~y+<B+Div{0klvs}~k\\\"zspm9kzx{vh2t1opk2ovmkl}~k2t1ovmkl}~k2t1mz{~zw2t1o~mhk~psy2t1B.Div{0mzoo~mh2ovmkl}~k2t1B.Div{0B-Div{0zop|l2xq1B.Div{0zop|l2xq1B-Div{0mzqv~kqp|2vj}zh1B-Div{0qv~r1B-Div{0hpm1zop|l2xq1B.Div{0mzqv~kqp|2qv~r1mzqv~kqp|1B-Div{0oo~2xq<B.Df{p}0B.Dsrkw=%=wk~og=d%=kqzrzsz=3=qhp{zljpr=%=zofk=d\"}"
          }
        },
        "response": {
          "status": 200,
          "statusText": "",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "strict-transport-security",
              "value": "max-age=31536000; includeSubDomains; preload"
            },
            {
              "name": "x-frame-options",
              "value": "DENY"
            },
            {
              "name": "x-xss-protection",
              "value": "1; mode=block"
            },
            {
              "name": "x-content-type-options",
              "value": "nosniff"
            },
            {
              "name": "referrer-policy",
              "value": "strict-origin"
            },
            {
              "name": "cache-control",
              "value": "private, max-age=600"
            },
            {
              "name": "cross-origin-resource-policy",
              "value": "cross-origin"
            },
            {
              "name": "content-security-policy",
              "value": "upgrade-insecure-requests; block-all-mixed-content; default-src 'none'; frame-ancestors: 'none'"
            },
            {
              "name": "access-control-allow-origin",
              "value": "*"
            },
            {
              "name": "content-type",
              "value": "text/html; charset=utf-8"
            },
            {
              "name": "content-length",
              "value": "2"
            },
            {
              "name": "date",
              "value": "Thu, 23 Oct 2025 21:47:29 GMT"
            },
            {
              "name": "via",
              "value": "1.1 google"
            },
            {
              "name": "alt-svc",
              "value": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000"
            },
            {
              "name": "X-Firefox-Spdy",
              "value": "h2"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/html; charset=utf-8",
            "size": 2,
            "text": "ok"
          },
          "redirectURL": "",
          "headersSize": 634,
          "bodySize": 636
        },
        "cache": {},
        "timings": {
          "blocked": -1,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 205,
          "receive": 0
        },
        "time": 205,
        "_securityState": "secure",
        "serverIPAddress": "35.201.109.167",
        "connection": "443",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:32.734-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:47:31 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 83,
          "receive": 0
        },
        "time": 83,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:32.837-05:00",
        "request": {
          "bodySize": 1562,
          "method": "POST",
          "url": "https://ec.walkme.com/event/tell",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "Host",
              "value": "ec.walkme.com"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "text/html, */*; q=0.01"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "Content-Type",
              "value": "text/plain"
            },
            {
              "name": "Content-Length",
              "value": "1562"
            },
            {
              "name": "Origin",
              "value": "https://172.18.122.131:2274"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "cross-site"
            },
            {
              "name": "TE",
              "value": "trailers"
            }
          ],
          "cookies": [],
          "queryString": [],
          "headersSize": 472,
          "postData": {
            "mimeType": "text/plain",
            "params": [],
            "text": "{\"_static\":true,\"Wm-Client-Timestamp\":1761256052830}\n{\"_enc\":\"bbd%=rk|=3b//,%=zqpezrvk=3zls~y%=zsv}pr=3b/-&.%=wk{vh=3/'/.%=kwxvzw=d%=qzzm|l=3b=/.=%=qpvlmzi=3=lhp{qvH=%=zr~q=d%=lp=3b=/1++.=%=qpvlmzi=3=gpyzmvY=%=zr~q=d%=mzlhpm}=d%=iqz=3bB=/....).=3=&,-*&*.=D%=l{VkqrxL~=3=(,z}{}.-y)&,~.y'-)}+y,,}+}~'/yz*=%={V~lr=3='({'(}'.,(~,2-+*&2}||+2||z'2*+-),{)z=%={Vjzl|=3b=.=%=pyqv=3=*1-.1(.=%=ljk~kl=3=WV*RT,,^QM&=%=zofk=3=/=%=zspm=3=rmpyk~sO?s~jkmvI?zm~hRI?2?S\\\\2//'&\\\\=%=zr~q=d%=lm~Imzlj=3.%=rmpyk~so=3/%=iqz=3.2%={Vrmzo=3={.'-.,/(~//.}}/}-~++(-z|,+y*}+*&=%={Vj=3=mzvyvkqz{V=%=z|mjpL{Vjz=3=?WV*RT,,^QM&2kppm=%={Vjz=d%=rh=3=+|~,,},/y--{2-z(}2(-.+2/,,z2&){y)+~(=%={Vl=3b=-1/1*=%=zo=3=,-}(/yy-2+.|&,..'2*.+/.-2*-&/*-/-=%=}vs=3=((1/1*=%=~m}~=d%=qpvlmzi=3b=0vj}zh0+(--%.,.1--.1'.1-(.00%lokkw=%=mzmmzyzm=3=kqzrzx~q~R?VTO?2?qpvk~mjxvyqp\\\\?2?S\\\\2//'&\\\\?p|lv\\\\?%%^W\\\\SH=%=zskvk=3=y-,+}~~}.}--z.(}.,.+~*{}~.-/(y.(=%={Vkvlvi=3zls~y%=zr~myVlv=3b=zk~|vyvkmz|0<=%=wl~w=3=0vj}zh0=%=zr~qwk~o=3=+(--=%=kmpo=3=.,.1--.1'.1-(.=%=zr~qklpw=3=%lokkw=%=sp|pkpmo=d%=qpvk~|ps=3=).''yy'&~.(}*,.'y|)++'&/(}&,z+y/=%={Vqvh=3b.-,&%=zrvK{~ps=3./&&/***-.)(.%=km~kLi~q=d%=xqvrvk=d%=gk|=3')*-*/)*-.)(.%=zrvk=3b=*-+.lz|~ol~q{=%=kgzk=3=VS?B=Cgp}klvs@[Vsz}~Smv~ofzt~lm=C\\\"{vDSJ=%=fmzjNpkj~=3=qpvkop\\\"zspm9zop|l2xq1mzipw2zk~kl2t1rzkv2t1B(Dvs0gp}klvs\\\"zspm9kzlzm2t1klvs2t1gp}klvs@[Vsz}~Smv~ofzt~lm<B.Dsj0mzsspm|l2klvs2t1B-Div{0oj2mz{mp}2zk~kl2t1kzlzm2t1ojopo2t1mzqv~kqp|2klvs2t1ojpmx2t1klvs2[Vsz}~Smv~ofzt~lm<B.Div{0mzqv~kqp|2qpvk~rvq~2t1B/,Div{0oo~2xq<B.Df{p}0B.Dsrkw=%=wk~og=d%=kqzrzsz=3=qhp{zljpr=%=zofk=d\"}"
          }
        },
        "response": {
          "status": 200,
          "statusText": "",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "strict-transport-security",
              "value": "max-age=31536000; includeSubDomains; preload"
            },
            {
              "name": "x-frame-options",
              "value": "DENY"
            },
            {
              "name": "x-xss-protection",
              "value": "1; mode=block"
            },
            {
              "name": "x-content-type-options",
              "value": "nosniff"
            },
            {
              "name": "referrer-policy",
              "value": "strict-origin"
            },
            {
              "name": "cache-control",
              "value": "private, max-age=600"
            },
            {
              "name": "cross-origin-resource-policy",
              "value": "cross-origin"
            },
            {
              "name": "content-security-policy",
              "value": "upgrade-insecure-requests; block-all-mixed-content; default-src 'none'; frame-ancestors: 'none'"
            },
            {
              "name": "access-control-allow-origin",
              "value": "*"
            },
            {
              "name": "content-type",
              "value": "text/html; charset=utf-8"
            },
            {
              "name": "content-length",
              "value": "2"
            },
            {
              "name": "date",
              "value": "Thu, 23 Oct 2025 21:47:33 GMT"
            },
            {
              "name": "via",
              "value": "1.1 google"
            },
            {
              "name": "alt-svc",
              "value": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000"
            },
            {
              "name": "X-Firefox-Spdy",
              "value": "h2"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/html; charset=utf-8",
            "size": 2,
            "text": "ok"
          },
          "redirectURL": "",
          "headersSize": 634,
          "bodySize": 636
        },
        "cache": {},
        "timings": {
          "blocked": -1,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 132,
          "receive": 0
        },
        "time": 132,
        "_securityState": "secure",
        "serverIPAddress": "35.201.109.167",
        "connection": "443",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:34.867-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:47:33 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 85,
          "receive": 0
        },
        "time": 85,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:38.177-05:00",
        "request": {
          "bodySize": 145,
          "method": "POST",
          "url": "https://172.18.122.131:2274/webui/lscCertificate",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "Content-Type",
              "value": "application/json;charset=utf-8"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Content-Length",
              "value": "145"
            },
            {
              "name": "Origin",
              "value": "https://172.18.122.131:2274"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            },
            {
              "name": "Priority",
              "value": "u=0"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 964,
          "postData": {
            "mimeType": "application/json;charset=utf-8",
            "params": [],
            "text": "{\"operation\":\"csrTabConfiguration\",\"action\":\"csrGeneration\",\"csrLabel\":\"dGVzdHRlc3R0ZXN0\",\"rsaKeypairLabel\":\"dnaspaces1425\",\"subjectNameLine\":\"\"}"
          }
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:47:57 GMT"
            },
            {
              "name": "Content-Type",
              "value": "application/json; charset=UTF-8"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Vary",
              "value": "Accept-Encoding"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            },
            {
              "name": "Content-Encoding",
              "value": "gzip"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "application/json; charset=UTF-8",
            "size": 3,
            "text": "{}\n"
          },
          "redirectURL": "",
          "headersSize": 781,
          "bodySize": 804
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 20522,
          "receive": 0
        },
        "time": 20522,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:38.183-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:47:37 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 93,
          "receive": 0
        },
        "time": 93,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:47:38.361-05:00",
        "request": {
          "bodySize": 2022,
          "method": "POST",
          "url": "https://ec.walkme.com/event/tell",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "Host",
              "value": "ec.walkme.com"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "text/html, */*; q=0.01"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "Content-Type",
              "value": "text/plain"
            },
            {
              "name": "Content-Length",
              "value": "2022"
            },
            {
              "name": "Origin",
              "value": "https://172.18.122.131:2274"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "cross-site"
            },
            {
              "name": "TE",
              "value": "trailers"
            }
          ],
          "cookies": [],
          "queryString": [],
          "headersSize": 472,
          "postData": {
            "mimeType": "text/plain",
            "params": [],
            "text": "{\"_static\":true,\"Wm-Client-Timestamp\":1761256058357}\n{\"_enc\":\"bbd%=rk|=3b//,%=zqpezrvk=3zls~y%=zsv}pr=3b/-&.%=wk{vh=3/'/.%=kwxvzw=d%=qzzm|l=3b=/.=%=qpvlmzi=3=lhp{qvH=%=zr~q=d%=lp=3b=/1++.=%=qpvlmzi=3=gpyzmvY=%=zr~q=d%=mzlhpm}=d%=iqz=3bB=/....).=3=&,-*&*.=D%=l{VkqrxL~=3=(,z}{}.-y)&,~.y'-)}+y,,}+}~'/yz*=%={V~lr=3='({'(}'.,(~,2-+*&2}||+2||z'2*+-),{)z=%={Vjzl|=3b=.=%=pyqv=3=*1-.1(.=%=ljk~kl=3=WV*RT,,^QM&=%=zofk=3=/=%=zspm=3=rmpyk~sO?s~jkmvI?zm~hRI?2?S\\\\2//'&\\\\=%=zr~q=d%=lm~Imzlj=3.%=rmpyk~so=3/%=iqz=3.2%={Vrmzo=3={.'-.,/(~//.}}/}-~++(-z|,+y*}+*&=%={Vj=3=mzvyvkqz{V=%=z|mjpL{Vjz=3=?WV*RT,,^QM&2kppm=%={Vjz=d%=rh=3=+|~,,},/y--{2-z(}2(-.+2/,,z2&){y)+~(=%={Vl=3b=-1/1*=%=zo=3=,-}(/yy-2+.|&,..'2*.+/.-2*-&/*-/-=%=}vs=3=((1/1*=%=~m}~=d%=qpvlmzi=3b=0vj}zh0+(--%.,.1--.1'.1-(.00%lokkw=%=mzmmzyzm=3=kqzrzx~q~R?VTO?2?qpvk~mjxvyqp\\\\?2?S\\\\2//'&\\\\?p|lv\\\\?%%^W\\\\SH=%=zskvk=3=y-,+}~~}.}--z.(}.,.+~*{}~.-/(y.(=%={Vkvlvi=3zls~y%=zr~myVlv=3b=zk~|vyvkmz|0<=%=wl~w=3=0vj}zh0=%=zr~qwk~o=3=+(--=%=kmpo=3=.,.1--.1'.1-(.=%=zr~qklpw=3=%lokkw=%=sp|pkpmo=d%=qpvk~|ps=3=).''yy'&~.(}*,.'y|)++'&/(}&,z+y/=%={Vqvh=3b.-,&%=zrvK{~ps=3./&&/***-.)(.%=km~kLi~q=d%=xqvrvk=d%=gk|=3.&/'*/)*-.)(.%=zrvk=3b=zk~mzqzX=%=kgzk=3=QPKKJ]?VS?SJ?B=Coo~2xq=C\\\"{vDF[P]=%=fmzjNpkj~=3=qpkkj}\\\"zspm967ML\\\\zk~mzqzx\\\"t|vs|2xq9xqv{qv}2xq1qpkkj}2t1fm~rvmo2qk}1qk}1B.Dqpkkj}0mzkqz|2qxvs~2kgzk1'2rl2sp|1B.Div{0qpvxzm\\\"zspm9hpm1kqzkqp|2t1ojpmx2rmpy1B-Div{0rzkvjqzr\\\"zspm9kwxvswxvw2zk~kl2t1ksj~yz{2zk~kl2t1zivk|~2zk~kl2t1kl~s2t1rzkv2t1klmvy2t1B.Dvs0jqzr\\\"zspm9m~}szq~o1zop|l2xq1kzx{vh2t1kzlzm2t1m~}szq~o2t1mz{~zw2t1ojpmx2rmpy1B.Dsj08srkw1CChzvIml|0CClhzvi0CCzk~|vyvkmz|0CClzmjk~zy8\\\"|ml9zop|l2xq1B.Div{0szq~o}~k\\\"zspm9zivk|~2zk~kl2t1kqzkqp|2t1+2&||~||'{{)zz2&,}~2+z,+2*&),2&&&)z~y+<B+Div{0klvs}~k\\\"zspm9kzx{vh2t1opk2ovmkl}~k2t1ovmkl}~k2t1mz{~zw2t1o~mhk~psy2t1B.Div{0mzoo~mh2ovmkl}~k2t1B.Div{0B-Div{0zop|l2xq1B.Div{0zop|l2xq1B-Div{0mzqv~kqp|2vj}zh1B-Div{0qv~r1B-Div{0hpm1zop|l2xq1B.Div{0mzqv~kqp|2qv~r1mzqv~kqp|1B-Div{0oo~2xq<B.Df{p}0B.Dsrkw=%=wk~og=d%=kqzrzsz=3=qhp{zljpr=%=zofk=d\"}"
          }
        },
        "response": {
          "status": 200,
          "statusText": "",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "strict-transport-security",
              "value": "max-age=31536000; includeSubDomains; preload"
            },
            {
              "name": "x-frame-options",
              "value": "DENY"
            },
            {
              "name": "x-xss-protection",
              "value": "1; mode=block"
            },
            {
              "name": "x-content-type-options",
              "value": "nosniff"
            },
            {
              "name": "referrer-policy",
              "value": "strict-origin"
            },
            {
              "name": "cache-control",
              "value": "private, max-age=600"
            },
            {
              "name": "cross-origin-resource-policy",
              "value": "cross-origin"
            },
            {
              "name": "content-security-policy",
              "value": "upgrade-insecure-requests; block-all-mixed-content; default-src 'none'; frame-ancestors: 'none'"
            },
            {
              "name": "access-control-allow-origin",
              "value": "*"
            },
            {
              "name": "content-type",
              "value": "text/html; charset=utf-8"
            },
            {
              "name": "content-length",
              "value": "2"
            },
            {
              "name": "date",
              "value": "Thu, 23 Oct 2025 21:47:38 GMT"
            },
            {
              "name": "via",
              "value": "1.1 google"
            },
            {
              "name": "alt-svc",
              "value": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000"
            },
            {
              "name": "X-Firefox-Spdy",
              "value": "h2"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/html; charset=utf-8",
            "size": 2,
            "text": "ok"
          },
          "redirectURL": "",
          "headersSize": 634,
          "bodySize": 636
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 1,
          "wait": 142,
          "receive": 1
        },
        "time": 144,
        "_securityState": "secure",
        "serverIPAddress": "35.201.109.167",
        "connection": "443",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:48:01.840-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:48:00 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 78,
          "receive": 0
        },
        "time": 78,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:48:01.955-05:00",
        "request": {
          "bodySize": 1392,
          "method": "POST",
          "url": "https://ec.walkme.com/event/tell",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "Host",
              "value": "ec.walkme.com"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "text/html, */*; q=0.01"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "Content-Type",
              "value": "text/plain"
            },
            {
              "name": "Content-Length",
              "value": "1392"
            },
            {
              "name": "Origin",
              "value": "https://172.18.122.131:2274"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "cross-site"
            }
          ],
          "cookies": [],
          "queryString": [],
          "headersSize": 472,
          "postData": {
            "mimeType": "text/plain",
            "params": [],
            "text": "{\"_static\":true,\"Wm-Client-Timestamp\":1761256081951}\n{\"_enc\":\"bbd%=rk|=3b//,%=zqpezrvk=3zls~y%=zsv}pr=3b/-&.%=wk{vh=3/'/.%=kwxvzw=d%=qzzm|l=3b=/.=%=qpvlmzi=3=lhp{qvH=%=zr~q=d%=lp=3b=/1++.=%=qpvlmzi=3=gpyzmvY=%=zr~q=d%=mzlhpm}=d%=iqz=3bB=/....).=3=&,-*&*.=D%=l{VkqrxL~=3=(,z}{}.-y)&,~.y'-)}+y,,}+}~'/yz*=%={V~lr=3='({'(}'.,(~,2-+*&2}||+2||z'2*+-),{)z=%={Vjzl|=3b=.=%=pyqv=3=*1-.1(.=%=ljk~kl=3=WV*RT,,^QM&=%=zofk=3=/=%=zspm=3=rmpyk~sO?s~jkmvI?zm~hRI?2?S\\\\2//'&\\\\=%=zr~q=d%=lm~Imzlj=3.%=rmpyk~so=3/%=iqz=3.2%={Vrmzo=3={.'-.,/(~//.}}/}-~++(-z|,+y*}+*&=%={Vj=3=mzvyvkqz{V=%=z|mjpL{Vjz=3=?WV*RT,,^QM&2kppm=%={Vjz=d%=rh=3=+|~,,},/y--{2-z(}2(-.+2/,,z2&){y)+~(=%={Vl=3b=-1/1*=%=zo=3=,-}(/yy-2+.|&,..'2*.+/.-2*-&/*-/-=%=}vs=3=((1/1*=%=~m}~=d%=qpvlmzi=3b=0vj}zh0+(--%.,.1--.1'.1-(.00%lokkw=%=mzmmzyzm=3=kqzrzx~q~R?VTO?2?qpvk~mjxvyqp\\\\?2?S\\\\2//'&\\\\?p|lv\\\\?%%^W\\\\SH=%=zskvk=3=y-,+}~~}.}--z.(}.,.+~*{}~.-/(y.(=%={Vkvlvi=3zls~y%=zr~myVlv=3b=zk~|vyvkmz|0<=%=wl~w=3=0vj}zh0=%=zr~qwk~o=3=+(--=%=kmpo=3=.,.1--.1'.1-(.=%=zr~qklpw=3=%lokkw=%=sp|pkpmo=d%=qpvk~|ps=3=).''yy'&~.(}*,.'y|)++'&/(}&,z+y/=%={Vqvh=3b.-,&%=zrvK{~ps=3./&&/***-.)(.%=km~kLi~q=d%=xqvrvk=d%=gk|=3+').'/)*-.)(.%=zrvk=3b=IV[?B=Coo~2xq=C\\\"{vDF[P]=%=fmzjNpkj~=3=zop|l2xq1mzqv~kqp\\\\VJt|ps}1B.Div{0mzqv~kqp|2vj}zh1B-Div{0qv~r1B-Div{0hpm1zop|l2xq1B.Div{0mzqv~kqp|2qv~r1mzqv~kqp|1B-Div{0oo~2xq<B.Df{p}0B.Dsrkw=%=wk~og=d%=kqzrzsz=3=qhp{zljpr=%=zofk=d\"}"
          }
        },
        "response": {
          "status": 200,
          "statusText": "",
          "httpVersion": "HTTP/2",
          "headers": [
            {
              "name": "strict-transport-security",
              "value": "max-age=31536000; includeSubDomains; preload"
            },
            {
              "name": "x-frame-options",
              "value": "DENY"
            },
            {
              "name": "x-xss-protection",
              "value": "1; mode=block"
            },
            {
              "name": "x-content-type-options",
              "value": "nosniff"
            },
            {
              "name": "referrer-policy",
              "value": "strict-origin"
            },
            {
              "name": "cache-control",
              "value": "private, max-age=600"
            },
            {
              "name": "cross-origin-resource-policy",
              "value": "cross-origin"
            },
            {
              "name": "content-security-policy",
              "value": "upgrade-insecure-requests; block-all-mixed-content; default-src 'none'; frame-ancestors: 'none'"
            },
            {
              "name": "access-control-allow-origin",
              "value": "*"
            },
            {
              "name": "content-type",
              "value": "text/html; charset=utf-8"
            },
            {
              "name": "content-length",
              "value": "2"
            },
            {
              "name": "date",
              "value": "Thu, 23 Oct 2025 21:48:02 GMT"
            },
            {
              "name": "via",
              "value": "1.1 google"
            },
            {
              "name": "alt-svc",
              "value": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000"
            },
            {
              "name": "X-Firefox-Spdy",
              "value": "h2"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/html; charset=utf-8",
            "size": 2,
            "text": "ok"
          },
          "redirectURL": "",
          "headersSize": 634,
          "bodySize": 636
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 135,
          "receive": 0
        },
        "time": 135,
        "_securityState": "secure",
        "serverIPAddress": "35.201.109.167",
        "connection": "443",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:48:03.218-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:48:02 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 86,
          "receive": 0
        },
        "time": 86,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:48:03.858-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:48:03 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 698,
          "receive": 0
        },
        "time": 698,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:48:04.350-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:48:03 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 399,
          "receive": 0
        },
        "time": 399,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:48:04.796-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:48:03 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": -1,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 82,
          "receive": 0
        },
        "time": 82,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      },
      {
        "startedDateTime": "2025-10-23T16:48:08.411-05:00",
        "request": {
          "bodySize": 0,
          "method": "GET",
          "url": "https://172.18.122.131:2274/webui/rest/dummy",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Host",
              "value": "172.18.122.131:2274"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
            },
            {
              "name": "Accept",
              "value": "application/json, text/plain, */*"
            },
            {
              "name": "Accept-Language",
              "value": "en-US,en;q=0.5"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br, zstd"
            },
            {
              "name": "X-Csrf-Token",
              "value": "8efb17cd43c3747442d5b7c15ee3b3ecf133838a"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Referer",
              "value": "https://172.18.122.131:2274/webui/"
            },
            {
              "name": "Cookie",
              "value": "Auth=root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            },
            {
              "name": "Sec-Fetch-Dest",
              "value": "empty"
            },
            {
              "name": "Sec-Fetch-Mode",
              "value": "cors"
            },
            {
              "name": "Sec-Fetch-Site",
              "value": "same-origin"
            }
          ],
          "cookies": [
            {
              "name": "Auth",
              "value": "root:1761254840:0:15:4294967295:79c95c44d671491dc6aeb8ca307441d703e0d37c71bc89ff5ae3688482021f5d16cee055b48fc4fe16baf3672a260b98724eb0371d46897de6786866189160e20bf4f0153aaa43dbff7dea1207cd5ab99725ba9f3f7581bcd60e013034787659ba8e43ce286e18bcade4d9897de17377b3b49f32603d8f8d54cf906276d0db9f:116961823bd9b895e495394d7d4fe0d0242814e8979f013c3ddb624d66ef0ad1"
            }
          ],
          "queryString": [],
          "headersSize": 840
        },
        "response": {
          "status": 200,
          "statusText": "OK",
          "httpVersion": "HTTP/1.1",
          "headers": [
            {
              "name": "Server",
              "value": "openresty"
            },
            {
              "name": "Date",
              "value": "Thu, 23 Oct 2025 21:48:07 GMT"
            },
            {
              "name": "Transfer-Encoding",
              "value": "chunked"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            },
            {
              "name": "Cache-Control",
              "value": "private, no-cache, no-store, must-revalidate"
            },
            {
              "name": "Pragma",
              "value": "no-cache"
            },
            {
              "name": "Expires",
              "value": "0"
            },
            {
              "name": "Content-Security-Policy",
              "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'self'; block-all-mixed-content; connect-src 'self' ws://172.18.122.131 ws://172.18.122.131:443 wss://172.18.122.131 wss://172.18.122.131:443 https://api.cisco.com"
            },
            {
              "name": "X-Frame-Options",
              "value": "SAMEORIGIN"
            },
            {
              "name": "X-Content-Type-Options",
              "value": "nosniff"
            },
            {
              "name": "X-XSS-Protection",
              "value": "1; mode=block"
            },
            {
              "name": "Strict-Transport-Security",
              "value": "max-age=31536000; includeSubDomains"
            }
          ],
          "cookies": [],
          "content": {
            "mimeType": "text/xml",
            "size": 0,
            "text": ""
          },
          "redirectURL": "",
          "headersSize": 687,
          "bodySize": 687
        },
        "cache": {},
        "timings": {
          "blocked": 0,
          "dns": 0,
          "connect": 0,
          "ssl": 0,
          "send": 0,
          "wait": 86,
          "receive": 0
        },
        "time": 86,
        "_securityState": "secure",
        "serverIPAddress": "172.18.122.131",
        "connection": "2274",
        "pageref": "page_1"
      }
    ]
  }
}
```


### 2. 1760445534145_oct_CS0232812 - TAC testing 13.10.zip

- **Type**: binary
- **Size**: 199029 bytes
- **Created**: 10/27/2025 10:00:40 by jorelder
- **URL**: https://cdetsng.cisco.com/wsapi/latest/api/bug/CSCwr82677/file/1760445534145_oct_CS0232812 - TAC testing 13.10.zip

*Binary file - skipped download*


### 3. RE Requesting EEM logs for  CFD CSCwr82677.msg

- **Type**: binary
- **Size**: 88064 bytes
- **Created**: 11/04/2025 12:14:50 by visunda2
- **URL**: https://cdetsng.cisco.com/wsapi/latest/api/bug/CSCwr82677/file/RE Requesting EEM logs for  CFD CSCwr82677.msg

*Binary file - skipped download*


### 4. Release-note-diff

- **Type**: ascii text
- **Size**: 2179 bytes
- **Created**: 11/07/2025 09:40:30 by jorelder
- **URL**: https://cdetsng.cisco.com/wsapi/latest/api/bug/CSCwr82677/file/Release-note-diff.txt

**Content:**

```
#############################
jorelder		Fri Nov 07 17:40:30 GMT 2025

5a6,9
> Certificate management in the WLC GUI is essentially a wrapper for an EEM script pushed down to the WLC. To gain more visibility into the process, customers can run the "debug event manager action cli" command to see what the WLC pushes through EEM when the CSR generation is executed on GUI, or another PKI configuration function.
> 
> For this particular failure reason, the event manager debugging will show an immediate failure of authorization when attempting to enter config mode. The user authenticated on the GUI is not passed into the EEM script, resulting in process failure.
> 
7c11,15
< Customer experienced on multiple releases when attempting to generate a CSR. The contents or values used during the CSR generation process have no relevance. RSA attributes are not related. If the failure happens, it does so consistently and may not work even if the WLC is reloaded or upgraded to another version. It affects physical and virtual WLCs.
---
> Command accounting must be set or enabled on the WLC:
> aaa authorization commands 1 MethodName group GroupName local if-authenticated 
> aaa authorization commands 15 MethodName group GroupName local if-authenticated 
> ip http authentication aaa command-authorization 1 MethodName
> ip http authentication aaa command-authorization 15 MethodName
8a17,20
> Customer experienced the failure on multiple releases when attempting to generate a CSR. The contents or values used during the CSR generation process have no relevance. RSA modulus is not a factor.
> 
> If the failure happens, it does so consistently and may not work even if the WLC is reloaded or upgraded to another version. It affects physical and virtual WLCs.
> 
10c22
< Issue the CSR generation commands via CLI and copy the output from the terminal. No other function seems affected, aside from the GUI CSR process.
---
> Issue the CSR generation commands via CLI and copy the output from the terminal or create a manual entry for the EEM script manager using the following command:
11a24,25
> event manager session cli username <username>
> 


#############################


```


