FROM python:3

WORKDIR /root
COPY fetch.py .
COPY fetch .
RUN chmod 755 fetch

RUN pip install bs4

CMD ["/bin/bash"]