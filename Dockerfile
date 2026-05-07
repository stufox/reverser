FROM public.ecr.aws/amazonlinux/amazonlinux:2023-minimal
RUN dnf -y update && dnf -y install python3.12 python3.12-pip
COPY ./requirements.txt /app/requirements.txt
COPY ./reverser-instrumentation.py /app/reverser.py
RUN pip3.12 install -r /app/requirements.txt
WORKDIR /app
CMD opentelemetry-instrument fastapi run /app/reverser.py
