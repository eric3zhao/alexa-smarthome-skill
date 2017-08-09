# -*- coding: utf-8 -*-
import logging, json, requests, uuid
from constant import error_message,device_type

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info('got event:{}'.format(event))
    logger.info('got context:{}'.format(context))
    # access_token = event['payload']['accessToken']
    # logger.info('access_token:{}'.format(access_token))

    eventtype = event['header']['namespace']

    # logger.info('event type:{}'.format(eventtype))
    if eventtype == 'Alexa.ConnectedHome.Discovery':
        return handleDiscovery(context, event)
    elif eventtype == 'Alexa.ConnectedHome.Control':
        return handleControl(context, event)


def handleDiscovery(context, event):
    message_id = event['header']['messageId']
    if event['header']['name'] == 'DiscoverAppliancesRequest':
        uid = str(uuid.uuid1())
        respone = {}
        try:

            access_token = event['payload']['accessToken']

            httppayload = {'access_token': access_token, 'message_id': message_id}
            headers = {'content-type': 'application/json'}
            url = 'https://example.com/alexa/devices'
            httpresponse = requests.post(url, data=json.dumps(httppayload), headers=headers)

            responseJson = httpresponse.json()

            # logger.info('http responses {}'.format(responseJson))

            appliances = []

            if (responseJson['success']):
                list = responseJson['list']

                for devie in list:
                    # logger.info('http response {}'.format(devie))
                    dtype = devie['type']
                    description = device_type.get(dtype,'ABC production')
                    appliance = {'actions': ['turnOn', 'turnOff'], 'additionalApplianceDetails': {},
                                 'applianceId': devie['id'],
                                 'friendlyDescription': description,
                                 'friendlyName': devie['name'],
                                 'isReachable': devie['online'], 'manufacturerName': 'ABC Electronics Inc.',
                                 'modelName': dtype, 'version': '1'}

                    appliances.append(appliance)
                # logger.info('appliances: {}'.format(appliances))

                payload = {
                    'discoveredAppliances': appliances
                }

                respone = {'header': {
                    'messageId': uid,
                    'namespace': 'Alexa.ConnectedHome.Discovery',
                    'name': 'DiscoverAppliancesResponse',
                    'payloadVersion': '2'
                }, 'payload': payload}
            else:
                code = responseJson['code']
                msg = responseJson['msg']

                error = error_message.get(code)

                respone = {
                    'header': {
                        'namespace': 'Alexa.ConnectedHome.Control',
                        'name': error,
                        'payloadVersion': '2',
                        'messageId': uid
                    },
                    'payload': {
                    }
                }
        except BaseException, e:
            logger.error(e)
            respone = {
                "header": {
                    "namespace": "Alexa.ConnectedHome.Control",
                    "name": "DependentServiceUnavailableError",
                    "payloadVersion": "2",
                    "messageId": uid
                },
                "payload": {
                    "dependentServiceName": "ABC Device Server"
                }
            }

        finally:
            logger.info('respone: {}'.format(respone))
            return respone
            # responeJson = json.dumps(respone)
            # return responeJson


def handleControl(context, event):
    logger.info('handle control {}'.format(event))
    device_id = event['payload']['appliance']['applianceId']
    message_id = event['header']['messageId']
    event_name = event['header']['name']

    respone = {}

    try:
        uid = str(uuid.uuid1())
        if event_name == 'TurnOnRequest':

            access_token = event['payload']['accessToken']

            httppayload = {'access_token': access_token, 'device_id': device_id, 'message_id': message_id,
                           'operation': event_name}
            headers = {'content-type': 'application/json'}
            url = 'https://example.com/alexa/controller'
            httpresponse = requests.post(url, data=json.dumps(httppayload), headers=headers)

            responseJson = httpresponse.json()
            # logger.info('http response {}'.format(responseJson))

            if (responseJson['success']):
                respone = {'header': {
                    'namespace': 'Alexa.ConnectedHome.Control',
                    'name': 'TurnOnConfirmation',
                    'payloadVersion': '2',
                    'messageId': uid
                }, 'payload': {}}
            else:
                code = responseJson['code']
                msg = responseJson['msg']

                error = error_message.get(code)

                respone = {
                    'header': {
                        'namespace': 'Alexa.ConnectedHome.Control',
                        'name': error,
                        'payloadVersion': '2',
                        'messageId': uid
                    },
                    'payload': {
                    }
                }

        elif event_name == 'TurnOffRequest':
            payload = {}
            header = {
                'namespace': 'Alexa.ConnectedHome.Control',
                'name': 'TurnOffConfirmation',
                'payloadVersion': '2',
                'messageId': uid
            }

            access_token = event['payload']['accessToken']

            httppayload = {'access_token': access_token, 'device_id': device_id, 'message_id': message_id,
                           'operation': event_name}
            headers = {'content-type': 'application/json'}
            url = 'https://example/alexa/controller'
            httpresponse = requests.post(url, data=json.dumps(httppayload), headers=headers)

            responseJson = httpresponse.json()
            # logger.info('http response {}'.format(responseJson))

            if (responseJson['success']):
                respone = {'header': header, 'payload': payload}
            else:
                code = responseJson['code']
                msg = responseJson['msg']

                error = error_message.get(code)

                respone = {
                    'header': {
                        'namespace': 'Alexa.ConnectedHome.Control',
                        'name': error,
                        'payloadVersion': '2',
                        'messageId': uid
                    },
                    'payload': {
                    }
                }
        else:
            respone = {
                "header": {
                    "namespace": "Alexa.ConnectedHome.Control",
                    "name": "UnsupportedOperationError",
                    "payloadVersion": "2",
                    "messageId": uid
                },
                "payload": {
                }
            }

    except BaseException,e:
        logger.error(e)
        respone = {
            "header": {
                "namespace": "Alexa.ConnectedHome.Control",
                "name": "DependentServiceUnavailableError",
                "payloadVersion": "2",
                "messageId": uid
            },
            "payload": {
                "dependentServiceName": "ABC Device Server"
            }
        }
    finally:
        return respone
