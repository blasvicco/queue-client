'''Driver for AWS SQS Broker'''

# General imports
import json

# Lib imports
from pika import BlockingConnection, URLParameters

# App imports
from . import Abstract

class Instance(Abstract):
	'''
	A wrapper class around pika module

	Please see the official documentation for more detailed information:
	https://pika.readthedocs.io/en/stable/
	'''

	def __init__(self, cfg): # pylint: disable=super-init-not-called
		'''
			Set the AMQP Pika connection
		'''
		self.cfg = cfg
		credentials = cfg.get('credentials', {})
		user = f"{credentials.get('username')}:{credentials.get('password')}"
		parameters = URLParameters(
			f"amqp://{user}@{cfg.get('host')}:{cfg.get('port') or 5672}/"
		)
		self.connection = BlockingConnection(parameters=parameters)
		self.channel = self.connection.channel()
		self.channel.confirm_delivery()

	def __del__(self):
		'''
			Close connections
		'''
		if hasattr(self, 'connection'):
			self.connection.close()

	def create_queue(self, queue_name, attributes=None, tags=None):
		'''
			Create a queue named `queue_name` using the given `attributes` and `tags`.

			:param str queue_name: Name of the queue.
			:param dict attributes: Attributes that will be set for the queue.
			:param dict tags: Queue cost allocation tags that will be set for the queue.
		'''
		if attributes:
			raise ValueError('Argument attributes is not supported in this driver.')
		if tags:
			raise ValueError('Argument tags is not supported in this driver.')

		self.channel.queue_declare(
			queue=queue_name,
			durable=True,
			exclusive=False,
			auto_delete=False,
		)

	def does_queue_exist(self, queue_name):
		'''
			Return `True` if a queue named `queue_name` exists.

			:param str queue_name: Name of the queue.
			:return: Whether a queue named `queue_name` exists.
			:rtype: boolean
		'''
		# For AMQP there is no need to check for queue existence
		# so we just create it if does not exist and then return true
		self.create_queue(queue_name)
		return True

	def get_queue_by_name(self, queue_name, skip_cache=False):
		'''
			Return a queue named `queue_name`.

			:param str queue_name: Name of the queue.
			:param boolean skip_cache: Whether to skip the queue cache.
			:raise RuntimeError: Because it is not supported by the driver.
			:return: None.
		'''
		# For AMQP there is no need to check for queue existence
		raise RuntimeError('AMQP driver does not implement get_queue_by_name.')

	def purge_queue(self, queue_name):
		'''
			Delete all messages from a queue named `queue_name`.

			:param str queue_name: Name of the queue.
			:rtype: None
		'''
		return self.channel.queue_purge(queue_name)

	def receive_message_from_queue(self, queue_name, **receive_kwargs):
		'''
			Return a single message from a queue named `queue_name`.

			`receive_kwargs` are passed to the underlying receive_messages call.

			:param str queue_name: Name of the queue.
			:param receive_kwargs: Arguments that will be passed to the underlying `receive_messages` call.
			:return: `Message` object or None, when no message was received.
			:rtype: Message, None
		'''
		if receive_kwargs:
			raise ValueError('Argument receive_kwargs is not supported in this driver.')

		method_frame, _, body = self.channel.basic_get(queue_name)
		if method_frame:
			self.channel.basic_ack(method_frame.delivery_tag)
			return json.loads(body)
		return None

	def receive_messages_from_queue(self, queue_name, max_count=10, **receive_kwargs):
		'''
			Return maximum of `max_count` messages from a queue named `queue_name`.

			:param str queue_name: Name of the queue.
			:param int max_count: Maximum number of messages to receive (10 at most).
			:param receive_kwargs: Arguments that will be passed to the underlying `receive_messages` call.
			:return: List of `Message` objects.
			:rtype: list[Message`]
		'''
		if receive_kwargs:
			raise ValueError('Argument receive_kwargs is not supported in this driver.')

		messages = []
		while True:
			message = self.receive_message_from_queue(queue_name)
			if message:
				messages.append(message)
				if len(messages) < max_count:
					continue
			break
		return messages

	def send_message_to_queue(self, queue_name, message_body, **send_kwargs):
		'''
			Send a message `message_body` to a queue named `queue_name`.

			:param str queue_name: Name of the queue.
			:param str message_body: The body of the message that will be sent.
			:param send_kwargs: Arguments that will be passed to the underlying `send_message` call.
			:return: the message body.
			:rtype: dict
		'''
		if send_kwargs:
			raise ValueError('Argument send_kwargs is not supported in this driver.')

		self.channel.basic_publish(
			'',
			routing_key=queue_name,
			body=json.dumps(message_body),
			mandatory=True,
		)
		return message_body
