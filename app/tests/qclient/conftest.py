'''Conf Tests for QClient module'''

# General imports
import os

# Lib imports
import boto3
import pytest
from moto import mock_aws

# App imports
from app.src.qclient import QClientFactory

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
def cfg():
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
def sqs(aws_credentials):
	'''Return an SQS resource from boto3'''
	with mock_aws():
		yield boto3.Session(**aws_credentials).resource('sqs')

@pytest.fixture
def qclient(cfg):
	'''Return an instance of QClient based on cfg.driver value'''
	with mock_aws():
		yield QClientFactory.get_instance(cfg)

@pytest.fixture
def queue_without_messages(qclient):
	'''Return an empty SQS queue'''
	queue_name = 'test-queue'
	queue = qclient.create_queue(queue_name)
	yield queue, queue_name

@pytest.fixture
def queue_with_one_message(qclient):
	'''Return an SQS queue which contains a single message'''
	queue_name = 'test-queue'
	queue = qclient.create_queue(queue_name)
	message = qclient.send_message_to_queue(queue_name, 'message')
	message_id = message.get('MessageId')
	yield queue, queue_name, message_id

@pytest.fixture
def queue_with_messages(qclient):
	'''Return an SQS queue which contains messages'''
	queue_name = 'test-queue'
	queue = qclient.create_queue(queue_name)
	messages = [
		qclient.send_message_to_queue(queue_name, 'message-' + str(i))
		for i in range(15)
	]
	message_ids = [message.get('MessageId') for message in messages]
	yield queue, queue_name, message_ids
