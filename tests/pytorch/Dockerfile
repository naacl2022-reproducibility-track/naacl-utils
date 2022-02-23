ARG PYTHON
FROM danieldeutsch/python:${PYTHON}-cuda11.0.3-base

ARG PYTORCH
RUN pip install --no-cache-dir torch==${PYTORCH} -f https://download.pytorch.org/whl/torch_stable.html

ENV PYTHONUNBUFFERED=1

COPY run.py run.py
CMD python run.py