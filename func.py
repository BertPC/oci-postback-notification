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

bounce_postback_url = "https://ascentwebs.com/dyn-http-handler.php?type=b&e={email}&br={bouncerule}&bt={bouncetype}&bc={bouncecode}&dc={diagnostic}&s={status}&c={XCampaignID}&sub={XSubscriberID}&q={XUserData3}&z={XMultipleDashes}&LIVE=1&data={logdata}"

def handler(ctx, data: io.BytesIO=None):

    # Input is one or more Log events; parse into JSON and loop through them
    try:
        logs = json.loads(data.getvalue())

        for item in logs: 

            headers = {'Content-type': 'application/json'}
            x = requests.get(bounce_postback_url.format(data=json.dumps(item)), headers=headers)
            logging.getLogger().info(x.text)

            return response.Response(ctx, response_data=json.dumps(
                {"message": "Log data: {}\nResponse: {}".format(json.dumps(item), x.text)}),
                headers={"Content-Type": "application/json"}
            )
       
    except (Exception, ValueError) as ex:
        logging.getLogger().info(str(ex))
        return


#    name = "World"
#    try:
#        body = json.loads(data.getvalue())
#        name = body.get("name")
#    except (Exception, ValueError) as ex:
#        logging.getLogger().info('Error parsing Logging event data payload into JSON: ' + str(ex))
#
#    logging.getLogger().info("Inside Python Hello World function")
#    return response.Response(
#        ctx, response_data=json.dumps(
#            {"message": "Hello {0}".format(name)}),
#        headers={"Content-Type": "application/json"}
#    )
