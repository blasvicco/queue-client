'''Conf Tests for QClient module'''

# General imports
import os

# Lib imports
import boto3
import pytest
from moto import mock_aws

# App imports
from app.src.qclient import QClientFactory

def cfg_amqp():
	'''Set the cfg for the QClient'''
	return {
		'credentials': {
			'username': 'my-broker',
			'password': 'my-pass',
		},
		'driver': 'amqp',
		'host': 'broker',
	}

def cfg_sqs():
	'''Set the cfg for the QClient'''
	return {
		'credentials': {
			'key_id': 'testing',
			'secret': 'testing',
		},
		'driver': 'aws_sqs',
		'region': 'eu-west-1',
	}

@pytest.fixture
def aws_credentials():
	'''Set AWS credentials for testing'''
	os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
	os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
	os.environ['AWS_SECURITY_TOKEN'] = 'testing'
	os.environ['AWS_SESSION_TOKEN'] = 'testing'
	os.environ['SQS_POLLER_AWS_ACCESS_KEY_ID'] = 'testing'
	os.environ['SQS_POLLER_AWS_SECRET_ACCESS_KEY'] = 'testing'
	return {
		'aws_access_key_id': 'testing',
		'aws_secret_access_key': 'testing',
		'region_name': 'eu-west-1',
	}

@pytest.fixture
def sqs(aws_credentials): # pylint: disable=redefined-outer-name
	'''Return an SQS resource from boto3'''
	with mock_aws():
		yield boto3.Session(**aws_credentials).resource('sqs')

@pytest.fixture
def qclient(request):
	'''Return an instance of QClient based on cfg.driver value'''
	driver = request.param.get('driver')
	if driver == 'aws_sqs':
		with mock_aws():
			yield QClientFactory.get_instance(cfg_sqs())
	elif driver == 'amqp':
		yield QClientFactory.get_instance(cfg_amqp())

@pytest.fixture
def queue_without_messages(qclient): # pylint: disable=redefined-outer-name
	'''Return an empty SQS queue'''
	queue_name = 'test-queue'
	qclient.create_queue(queue_name)
	queue = qclient.queue_cache[queue_name] if hasattr(qclient, 'queue_cache') else {}
	yield queue_name

@pytest.fixture
def queue_with_one_message(qclient): # pylint: disable=redefined-outer-name
	'''Return an SQS queue which contains a single message'''
	queue_name = 'test-queue'
	qclient.create_queue(queue_name)
	queue = qclient.queue_cache[queue_name] if hasattr(qclient, 'queue_cache') else {}
	message = qclient.send_message_to_queue(queue_name, 'message')
	yield queue_name, message

@pytest.fixture
def queue_with_messages(qclient): # pylint: disable=redefined-outer-name
	'''Return an SQS queue which contains messages'''
	queue_name = 'test-queue'
	qclient.create_queue(queue_name)
	queue = qclient.queue_cache[queue_name] if hasattr(qclient, 'queue_cache') else {}
	messages = [
		qclient.send_message_to_queue(queue_name, 'message-' + str(i))
		for i in range(15)
	]
	yield queue_name, messages
