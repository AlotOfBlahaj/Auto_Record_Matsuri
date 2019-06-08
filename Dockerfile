FROM python:3.7.3

RUN git clone https://github.com/fzxiao233/Auto_Record_Matsuri.git /app \
&& pip install -r /app/requirements.txt

VOLUME /Matsuri

COPY ./src /app

CMD python /app/run.py