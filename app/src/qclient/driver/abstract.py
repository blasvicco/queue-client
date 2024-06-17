'''QClient abstract class'''

def raise_no_implemented(msg='Abstract method require to be implemented.'):
	'''Helper to raise exception when call no implemented method'''
	raise RuntimeError(msg)

# pylint: disable=unused-argument
class Abstract:
	'''Abstract class for queue client drivers'''

	def __init__(self, cfg=None):
		'''Instance constructor'''
		raise RuntimeError('Abstract class cannot be instantiated.')

	def create_queue(self, queue_name, attributes=None, tags=None):
		'''
			Create a queue named `queue_name` using the given `attributes` and `tags`.

			:param str queue_name: Name of the queue.
			:param dict attributes: Attributes that will be set for the queue.
			:param dict tags: Queue cost allocation tags that will be set for the queue.
		'''
		raise_no_implemented()

	def does_queue_exist(self, queue_name):
		'''
			Return `True` if a queue named `queue_name` exists.

			:param str queue_name: Name of the queue.
			:return: Whether a queue named `queue_name` exists.
			:rtype: boolean
		'''
		raise_no_implemented()

	def get_queue_by_name(self, queue_name, skip_cache=False):
		'''
			Return a queue named `queue_name`.

			:param str queue_name: Name of the queue.
			:param boolean skip_cache: Whether to skip the queue cache.
			:raise QueueDoesNotExist: When the queue is not found, this exception is raised.
			:return: A `Queue` object.
		'''
		raise_no_implemented()

	def purge_queue(self, queue_name):
		'''
			Delete all messages from a queue named `queue_name`.

			:param str queue_name: Name of the queue.
			:raise QueueDoesNotExist: When the queue is not found, this exception is raised.
			:rtype: None
		'''
		raise_no_implemented()

	def receive_message_from_queue(self, queue_name, **receive_kwargs):
		'''
			Return a single message from a queue named `queue_name`.

			`receive_kwargs` are passed to the underlying receive_messages call.

			:param str queue_name: Name of the queue.
			:param receive_kwargs: Arguments that will be passed to the underlying `receive_messages` call.
			:raise QueueDoesNotExist: When the queue is not found, this exception is raised.
			:return: `Message` object or None, when no message was received.
			:rtype: Message, None
		'''
		raise_no_implemented()

	def receive_messages_from_queue(self, queue_name, max_count=10, **receive_kwargs):
		'''
			Return maximum of `max_count` messages from a queue named `queue_name`.

			:param str queue_name: Name of the queue.
			:param int max_count: Maximum number of messages to receive (10 at most).
			:param receive_kwargs: Arguments that will be passed to the underlying `receive_messages` call.
			:raise QueueDoesNotExist: When the queue is not found, this exception is raised.
			:return: List of `Message` objects.
			:rtype: list[Message`]
		'''
		raise_no_implemented()

	def send_message_to_queue(self, queue_name, message_body, **send_kwargs):
		'''
			Send a message `message_body` to a queue named `queue_name`.

			:param str queue_name: Name of the queue.
			:param str message_body: The body of the message that will be sent.
			:param send_kwargs: Arguments that will be passed to the underlying `send_message` call.
			:raise QueueDoesNotExist: When the queue is not found, this exception is raised.
			:return: The API response.
			:rtype: dict
		'''
		raise_no_implemented()
