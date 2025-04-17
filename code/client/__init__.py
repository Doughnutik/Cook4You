from model import model
from storage import mongodb
from logger import logger
from .client import Client

client = Client(model, mongodb, logger)