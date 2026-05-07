from fastapi import FastAPI, Response, status
from pydantic import BaseModel
import time 
import hmac
import hashlib
import base64
import sys
from opentelemetry import trace 
import opentelemetry.instrumentation.fastapi 
from opentelemetry.metrics import CallbackOptions, Observation
import logging
from opentelemetry import _logs
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import StatusCode



STARTUPTIME = time.time()
GLOBAL_CACHE = []
HASH = 'THISISFINE'

class ReverserRequest(BaseModel):
    Message: str

class ReverserResponse(BaseModel):
    Message: str
    Signature: str

class GetResponse(BaseModel):
    Message: str = {"Status":"OK"}

app = FastAPI()
tracer = trace.get_tracer(__name__) 
logger = _logs.get_logger(__name__)
#logger = logging.getLogger()
#logger.setLevel(logging.INFO)

exporter = OTLPLogExporter(endpoint="http://localhost:4317",insecure=True)
resource = Resource.create({"service.name": "reverser"})
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
_logs.set_logger_provider(logger_provider)

handler = LoggingHandler(logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

logger = logging.getLogger()


def sign(key, message): #HMAC signing, sign with our teams secret hash
    message = bytes(message, 'utf-8')
    key = bytes(key, 'utf-8')
    sig = hmac.new(key, message, hashlib.sha256)
    return base64.b64encode(sig.digest()).decode()

def transform(message):
    return message[::-1]

@app.post("/reverser")
@app.post("/")
#@tracer.start_as_current_span("reverser_post_handler")
def post_handler(request: ReverserRequest, response: Response) -> ReverserResponse:
    global GLOBAL_CACHE
    with tracer.start_as_current_span("reverser_post_handler"):
        current_span = trace.get_current_span()
        logger.info(f"Received a message {request.Message}")
        current_span.add_event(f"Received a message {request.Message}")
        reversed = transform(request.Message)
        signature = sign(HASH, reversed)
        response = ReverserResponse(Message=reversed,Signature=signature)
        if time.time() - STARTUPTIME > 180.00: #After 3 mins use cache
            cachesize = 0
            GLOBAL_CACHE.append(response.Message * 2**20) #Cache part of the message received
            for i in GLOBAL_CACHE:
                cachesize = cachesize + int(sys.getsizeof(i))
                print(f"Cache size is {cachesize}")
            if cachesize > 370000000 : #if cache over 370MB log warning to use cacheless version :patched
                logger.error("cache is getting too big")
                #current_span.add_event("Warning. Large cache size. If containers crash with OutOfMemoryError try docker tag :patched")
                current_span.set_attribute("warning","Large cache size. If containers crash with OutOfMemoryError try docker tag :patched")
                current_span.set_status(StatusCode.ERROR, "Caching error")
    return response
    

# Handle GET - just return an OK message
@app.get("/{full_path:path}")
def get_handler():
    return {"Status":"OK"}