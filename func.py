# OCI Email Event Notifications (Python example)
# (in the style of Dyn Email postbacks)
# 
# Bounce postback URL:
# https://ascentwebs.com/dyn-http-handler.php?type=b&e=@email&br=@bouncerule&bt=@bouncetype&bc=@bouncecode&dc=@diagnostic&s=@status&c=@X-CampaignID&sub=@X-SubscriberID&q=@X-UserData3&z=@X-Multiple-Dashes&LIVE=1
# Complaint postback URL:
# https://ascentwebs.com/dyn-http-handler.php?type=c&e=@email&c=@X-CampaignID&sub=@X-SubscriberID&q=@X-UserData3&z=@X-Multiple-Dashes&LIVE=1
# Unsubscribe postback URL:
# https://ascentwebs.com/dyn-http-handler.php?type=u&e=@email&c=@X-CampaignID&sub=@X-SubscriberID&q=@X-UserData3&z=@X-Multiple-Dashes&LIVE=1
# Postback handler log:
# https://ascentwebs.com/dyn-postbacks.log

import io
import json
import logging
import requests

from fdk import response


postback_url_with_fields = "https://ascentwebs.com/dyn-http-handler.php?type={notifytype}&e={email}&message={message}" 
postback_url_no_fields = "https://ascentwebs.com/dyn-http-handler.php"
bounce_postback_querystring = "&bt={bouncetype}&bc={bouncecode}&br={bouncerule}&dc={diagnostic}&s={status}"


def handler(ctx, data: io.BytesIO=None):

    # Input is one or more Log events; parse into JSON and loop through them
    try:
        logs = json.loads(data.getvalue())

        for item in logs: 

            # Pull postback field values from log event
            log_data = item['data']
            querystring_values = {
                "notifytype": log_data['action'],  # bounce, complaint, open, click
                "email": log_data['recipient'],
                "message": log_data['message']  # high-level, human-readable summary of event
            }

            if log_data['action'] == 'bounce':
                querystring_values.update({
                    "bouncetype": log_data['errorType'],
                    "bouncecode": log_data['bounceCode'],
                    "bouncerule": log_data['bounceCategory'],
                    "diagnostic": log_data['smtpStatus'],
                    "status": log_data['bounceCode']
                })

            # For custom headers, gather them (if present) then can loop through
            #headers = log_data['headers']  # gives a dictionary of (header_name -> value) pairs

            # Other possibly helpful fields to include, which were not available in Dyn:
            # (see for list of all available fields)
            #message_id = log_data['messageId']  # original SMTP message ID
            #action = log_data['action']  # type of log event (accept, relay, bounce, open, click, etc.)
            #sender = log_data['sender']  # sender of the message
            #recip_domain = log_data['receivingDomain']  # Recipient domain (gmail.com, comcast.net, hotmail.com, etc.)

            # GET method
            response = requests.get(postback_url_with_fields.format(**querystring_values))
            # POST method
            #response = requests.get(postback_url_no_fields, params=querystring_values)

            logging.getLogger().info("Postback sent: {} Response: HTTP {} --- {}".format(response.url, response.status_code, response.text.replace('\n', '')))
       
    except (Exception, ValueError) as ex:
        logging.getLogger().error(str(ex))
        return
