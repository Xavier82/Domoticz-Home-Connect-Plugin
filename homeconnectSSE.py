#!/usr/bin/env python3.6

import sys
import requests
from sseclient import SSEClient
from requests.exceptions import HTTPError
from requests.exceptions import ConnectionError
import traceback
import logging
from logging.handlers import TimedRotatingFileHandler
import time

logHandler = TimedRotatingFileHandler("/var/log/homeconnectSSE.log",when="midnight")
logFormatter = logging.Formatter('%(asctime)s %(message)s')
logHandler.setFormatter( logFormatter )
logger = logging.getLogger( 'MyLogger' )
logger.addHandler( logHandler )
logger.setLevel( logging.INFO )

if len (sys.argv) == 4:
    count = 0
    while(True):
        logger.info("Start...")
        try:
            HEADER_JSON = {"content-type": "application/vnd.bsh.sdk.v1+json"}
            response = requests.post("http://"+sys.argv[2]+":"+sys.argv[3],"haId:"+sys.argv[1],HEADER_JSON)
            haId = response.text
            response.close()
            logger.info(haId)
            response = requests.post("http://"+sys.argv[2]+":"+sys.argv[3],"access_token",HEADER_JSON)
            access_token = response.text
            response.close()
            logger.info(access_token)
            BASEURL = "https://api.home-connect.com"
            if haId != "" and access_token != "":
                url_SSEConnection = BASEURL + "/api/homeappliances/" + haId + "/events"
                header = {"Accept": "application/vnd.bsh.sdk.v1+json", "Authorization": "Bearer " + access_token}
                messages = SSEClient(url_SSEConnection, headers=header)
                for msg in messages:
                    logger.info("message: [["+str(msg)+"]]")
                    HEADER_JSON = {"content-type": "application/vnd.bsh.sdk.v1+json"}
                    response = requests.post("http://"+sys.argv[2]+":"+sys.argv[3],str(msg),HEADER_JSON)
                    response.close()
                    count = 0
        except HTTPError as httperror:
            logger.error(httperror.response.text)
        except Exception as e:
            logger.error(traceback.format_exc())
        except ConnectionError as e:
            logger.error(e.response.text)
        if count < 60: 
            count = count + 1
        logger.info("Restarting after "+str(count*60)+" minutes...")
        time.sleep(count * 60)
