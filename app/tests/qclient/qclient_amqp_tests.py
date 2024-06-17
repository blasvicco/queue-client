'''Tests for QClient module'''

# General imports
import json

# Lib imports
import pytest
import requests
from allure import step
from pika.exceptions import UnroutableError

class TestCreateQueue:
	'''Tests for queue creation'''

	@pytest.mark.parametrize('qclient', [{'driver': 'amqp'}], indirect=True)
	def test_new_queue(self, qclient):
		'''Test create new queue'''
		with step('Arrange: initialize queue name'):
			queue_name = 'test-queue'

		with step(f'Act: create queue {queue_name}'):
			qclient.create_queue(queue_name)

		with step('Assert: queue creation succeded'):
			credentials = qclient.cfg.get('credentials')
			response = requests.get(
				f"http://{qclient.cfg.get('host')}:15672/api/queues",
				auth=(credentials.get('username'), credentials.get('password')),
			)
			res = json.loads(response.content)
			assert len(res) == 1
			assert res[0].get('name') == queue_name

	@pytest.mark.parametrize('qclient', [{'driver': 'amqp'}], indirect=True)
	def test_existing_queue(self, qclient):
		'''Test create on existing queue'''
		with step('Arrange: initialize queue name'):
			queue_name = 'test-queue'

		with step(f'Act: create queue {queue_name} and recreate'):
			qclient.create_queue(queue_name)
			qclient.create_queue(queue_name)

		with step('Assert: queue creation succeded'):
			credentials = qclient.cfg.get('credentials')
			response = requests.get(
				f"http://{qclient.cfg.get('host')}:15672/api/queues",
				auth=(credentials.get('username'), credentials.get('password')),
			)
			res = json.loads(response.content)
			assert len(res) == 1
			assert res[0].get('name') == queue_name

class TestGetQueueByName: # pylint: disable=too-few-public-methods
	'''Tests get queue by name'''

	@pytest.mark.parametrize('qclient', [{'driver': 'amqp'}], indirect=True)
	def test_get_queue_by_name_fail(self, qclient):
		'''Test get invalid queue'''
		with step('Assert: getting error when try to get queue by name because driver does not support it'):
			with pytest.raises(RuntimeError):
				qclient.get_queue_by_name('test-queue')

class TestDoesQueueExist: # pylint: disable=too-few-public-methods
	'''Tests check if queue exists'''

	@pytest.mark.parametrize('qclient', [{'driver': 'amqp'}], indirect=True)
	def test_existing_queue(self, sqs, qclient):
		'''Test queue exist'''
		with step('Arrange: initialize queue name'):
			queue_name = 'test-queue'

		with step(f'Act: create queue {queue_name}'):
			sqs.create_queue(QueueName=queue_name)

		with step('Assert: queue exist succeded'):
			assert qclient.does_queue_exist(queue_name)

class TestSendMessageToQueue:
	'''Tests send message'''

	@pytest.mark.parametrize('qclient', [{'driver': 'amqp'}], indirect=True)
	def test_success(self, qclient, queue_without_messages):
		'''Test send message'''
		with step('Arrange: get queue with no message'):
			queue_name = queue_without_messages

		with step('Act: send message'):
			sent_message = qclient.send_message_to_queue(queue_name, 'message')

		with step('Assert: message sent'):
			retrieved_message = qclient.receive_message_from_queue(queue_name)
			assert sent_message == retrieved_message

	@pytest.mark.parametrize('qclient', [{'driver': 'amqp'}], indirect=True)
	def test_non_existing_queue(self, qclient):
		'''Test send message fail because no queue'''
		with step('Arrange: initialize queue name'):
			queue_name = 'test-queue-fail'

		with step('Assert: getting error when queue name does not exist'):
			with pytest.raises(Exception) as error:
				qclient.send_message_to_queue(queue_name, 'message')
				assert isinstance(error, UnroutableError)

class TestReceiveMessagesFromQueue:
	'''Tests receive message'''

	@pytest.mark.parametrize('qclient', [{'driver': 'amqp'}], indirect=True)
	def test_without_messages(self, qclient, queue_without_messages):
		'''Test request message from empty queue'''
		with step('Arrange: get queue with no message'):
			queue_name = queue_without_messages

		with step('Act: get message'):
			message = qclient.receive_message_from_queue(queue_name)
			messages = qclient.receive_messages_from_queue(queue_name)

		with step('Assert: no message received'):
			assert message is None
			assert not messages

	@pytest.mark.parametrize('qclient', [{'driver': 'amqp'}], indirect=True)
	def test_one_message(self, qclient, queue_with_one_message):
		'''Test request message from queue with just one'''
		with step('Arrange: get queue with one message'):
			queue_name, message = queue_with_one_message

		with step('Act: get message'):
			received_message = qclient.receive_message_from_queue(queue_name)

		with step('Assert: only one message received'):
			assert received_message == message
			received_messages = qclient.receive_messages_from_queue(queue_name)
			assert len(received_messages) == 0

	@pytest.mark.parametrize('qclient', [{'driver': 'amqp'}], indirect=True)
	def test_multiple_messages(self, qclient, queue_with_messages):
		'''Test request messages from queue with more than one'''
		with step('Arrange: get queue with more than one messages'):
			queue_name, messages = queue_with_messages

		with step('Act: get messages'):
			received_messages = qclient.receive_messages_from_queue(queue_name, max_count=10)

		with step('Assert: multiple messages received'):
			for received_message in received_messages:
				assert received_message in messages
			received_message = qclient.receive_message_from_queue(queue_name)
			assert received_message in messages

		with step('Act: purge queue'):
			qclient.purge_queue(queue_name)

class TestPurgeQueue:
	'''Tests purge queue'''

	@pytest.mark.parametrize('qclient', [{'driver': 'amqp'}], indirect=True)
	def test_empty_queue(self, qclient, queue_without_messages):
		'''Test purge empty queue'''
		with step('Arrange: get queue with no message'):
			queue_name = queue_without_messages

		with step('Act: purge queue'):
			qclient.purge_queue(queue_name)

		with step('Assert: queue purged'):
			messages = qclient.receive_messages_from_queue(queue_name)
			assert not messages

	@pytest.mark.parametrize('qclient', [{'driver': 'amqp'}], indirect=True)
	def test_queue_with_messages(self, qclient, queue_with_messages):
		'''Test purge queue with messages'''
		with step('Arrange: get queue with more than one messages'):
			queue_name, _ = queue_with_messages

		with step('Act: purge queue'):
			qclient.purge_queue(queue_name)

		with step('Assert: queue purged'):
			messages = qclient.receive_messages_from_queue(queue_name)
			assert not messages
