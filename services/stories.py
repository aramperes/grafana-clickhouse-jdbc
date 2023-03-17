import datetime
import requests
import json
import time
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, String, Numeric, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
Base = declarative_base()

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# a in-memory cache to prevent spamming the same stories
# on startup, the last 500 stories are resent, so the topic will still have dupes
seen_stories = set()


def inflate_story(id):
    print('inflating...', id)
    return requests.get(f'https://hacker-news.firebaseio.com/v0/item/{id}.json').json()

class Story(Base):
    __tablename__ = 'stories'

    id = Column(Numeric, primary_key=True)
    by = Column(String)
    score = Column(Numeric)
    title = Column(String)
    time = Column(DateTime)
    url = Column(String)


db = create_engine(config['db']['uri'])
Base.metadata.create_all(db)

with db.connect() as conn:
    sess = Session(db)
    while True:
        print('Fetching new stories...')
        stories = requests.get(
            'https://hacker-news.firebaseio.com/v0/newstories.json').json()
        new_stories = 0

        for story_id in stories:
            if story_id in seen_stories:
                continue

            story = inflate_story(story_id)
            if story is None:
                continue
            if 'url' not in story:
                continue

            sess.merge(Story(
                by=story['by'],
                id=story['id'],
                score=story['score'],
                title=story['title'],
                time=datetime.datetime.fromtimestamp(story['time']),
                url=story['url']
            ))
            sess.commit()

            seen_stories.add(story_id)
            new_stories += 1

        print('Produced', new_stories, 'new stories')
        time.sleep(15)
