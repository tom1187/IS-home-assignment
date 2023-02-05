FROM python:3.9
WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /code

ENV PYTHONPATH "${PYTHONPATH}:/code"

CMD ["uvicorn", "customer_manager_ws:app", "--host", "0.0.0.0", "--port", "8000"]
#ENTRYPOINT ["bash"]