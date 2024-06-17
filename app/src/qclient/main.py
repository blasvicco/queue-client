'''QClient factory'''

# General imports
import importlib

INSTANCES = {}

class QClientFactory(): # pylint: disable=too-few-public-methods
	'''QClient factory class'''

	@staticmethod
	def get_instance(cfg=None):
		'''QClient instantiation'''
		if cfg is None:
			cfg = {}
		driver = cfg.get('driver') or 'aws_sqs'
		driver_module = importlib.import_module(
			f'.driver.{driver}',
			__name__.replace('.main', '')
		)
		INSTANCES[driver] = INSTANCES.get(driver) or driver_module.Instance(cfg)
		return INSTANCES[driver]
