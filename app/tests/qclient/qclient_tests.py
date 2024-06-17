'''Tests for QClient module'''

# Lib imports
import pytest
from allure import step

class TestCreateQueue:
	'''Tests for queue creation'''

	def test_new_queue(self, sqs, qclient):
		'''Test create new queue'''
		with step('Arrange: initialize queue name'):
			queue_name = 'test-queue'

		with step(f'Act: create queue {queue_name}'):
			created_queue = qclient.create_queue(queue_name)

		with step('Assert: queue creation succeded'):
			retrieved_queue = sqs.get_queue_by_name(QueueName=queue_name)
			assert created_queue.url == retrieved_queue.url

	def test_existing_queue(self, sqs, qclient):
		'''Test create on existing queue'''
		with step('Arrange: initialize queue name'):
			queue_name = 'test-queue'

		with step(f'Act: create queue {queue_name}'):
			created_queue = qclient.create_queue(queue_name)

		with step('Assert: queue creation on existing on succeded'):
			recreated_queue = qclient.create_queue(queue_name)
			assert created_queue.url == recreated_queue.url

class TestGetQueueByName:
	'''Tests get queue by name'''

	def test_get_queue_by_name_success(self, sqs, qclient):
		'''Test get valid queue'''
		with step('Arrange: initialize queue name'):
			queue_name = 'test-queue'

		with step(f'Act: create queue {queue_name}'):
			created_queue = sqs.create_queue(QueueName=queue_name)

		with step(f'Act: retrieve queue {queue_name}'):
			retrieved_queue = qclient.get_queue_by_name(queue_name)

		with step('Assert: getting queue by name succeded'):
			assert retrieved_queue.url == created_queue.url

	def test_get_queue_by_name_fail(self, qclient):
		'''Test get invalid queue'''
		with step('Assert: getting error when queue name does not exist'):
			with pytest.raises(Exception) as error:
				qclient.get_queue_by_name('test-queue')
				client_error = (getattr(error, 'response', {})).get('Error', {}).get('Code') in [
					'AWS.SimpleQueueService.NonExistentQueue'
				]
				assert client_error or isinstance(error, qclient.client.exceptions.QueueDoesNotExist)

class TestDoesQueueExist:
	'''Tests check if queue exists'''

	def test_existing_queue(self, sqs, qclient):
		'''Test queue exist'''
		with step('Arrange: initialize queue name'):
			queue_name = 'test-queue'

		with step(f'Act: create queue {queue_name}'):
			sqs.create_queue(QueueName=queue_name)

		with step('Assert: queue exist succeded'):
			assert qclient.does_queue_exist(queue_name)

	def test_non_existing_queue(self, qclient):
		'''Test queue does not exist'''
		with step('Assert: queue does not exist succeded'):
			assert not qclient.does_queue_exist('test-queue')

class TestSendMessageToQueue:
	'''Tests send message'''

	def test_success(self, qclient, queue_without_messages):
		'''Test send message'''
		with step('Arrange: get queue with no message'):
			queue, queue_name = queue_without_messages

		with step('Act: send message'):
			response = qclient.send_message_to_queue(queue_name, 'message')

		with step('Assert: message sent'):
			message_id = response.get('MessageId')
			retrieved_message = qclient.receive_message_from_queue(queue_name)
			assert retrieved_message.message_id == message_id
			assert retrieved_message.queue_url == queue.url

	def test_non_existing_queue(self, qclient):
		'''Test send message fail because no queue'''
		with step('Arrange: initialize queue name'):
			queue_name = 'test-queue'

		with step('Assert: getting error when queue name does not exist'):
			with pytest.raises(Exception) as error:
				qclient.send_message_to_queue(queue_name, 'message')
				client_error = (getattr(error, 'response', {})).get('Error', {}).get('Code') in [
					'AWS.SimpleQueueService.NonExistentQueue'
				]
				assert client_error or isinstance(error, qclient.client.exceptions.QueueDoesNotExist)

class TestReceiveMessagesFromQueue:
	'''Tests receive message'''

	def test_without_messages(self, qclient, queue_without_messages):
		'''Test request message from empty queue'''
		with step('Arrange: get queue with no message'):
			queue, queue_name = queue_without_messages

		with step('Act: get message'):
			message = qclient.receive_message_from_queue(queue_name)
			messages = qclient.receive_messages_from_queue(queue_name)

		with step('Assert: no message received'):
			assert message is None
			assert not messages

	def test_one_message(self, qclient, queue_with_one_message):
		'''Test request message from queue with just one'''
		with step('Arrange: get queue with one message'):
			queue, queue_name, message_id = queue_with_one_message

		with step('Act: get message'):
			message = qclient.receive_message_from_queue(queue_name, VisibilityTimeout=0)

		with step('Assert: only one message received'):
			assert message.message_id == message_id
			messages = qclient.receive_messages_from_queue(queue_name)
			assert messages[0].message_id == message_id
			assert len(messages) == 1

	def test_multiple_messages(self, qclient, queue_with_messages):
		'''Test request messages from queue with more than one'''
		with step('Arrange: get queue with more than one messages'):
			queue, queue_name, message_ids = queue_with_messages

		with step('Act: get messages'):
			messages = qclient.receive_messages_from_queue(queue_name, max_count=10)

		with step('Assert: multiple messages received'):
			for message in messages:
				assert message.message_id in message_ids
			message = qclient.receive_message_from_queue(queue_name)
			assert message.message_id in message_ids

class TestPurgeQueue:
	'''Tests purge queue'''

	def test_empty_queue(self, qclient, queue_without_messages):
		'''Test purge empty queue'''
		with step('Arrange: get queue with no message'):
			queue, queue_name = queue_without_messages

		with step('Act: purge queue'):
			qclient.purge_queue(queue_name)

		with step('Assert: queue purged'):
			messages = qclient.receive_messages_from_queue(queue_name)
			assert not messages

	def test_queue_with_messages(self, qclient, queue_with_messages):
		'''Test purge queue with messages'''
		with step('Arrange: get queue with more than one messages'):
			queue, queue_name, message_ids = queue_with_messages

		with step('Act: purge queue'):
			qclient.purge_queue(queue_name)

		with step('Assert: queue purged'):
			messages = qclient.receive_messages_from_queue(queue_name)
			assert not messages

