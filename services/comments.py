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


# a in-memory cache to prevent spamming the same comments
# on startup, the last 30 stories are resent
seen_comments = set()


def comment_story_pairs(html: str):
    # use bs4 to create a list of (comment, story) tuples
    pairs = []

    soup = BeautifulSoup(html, 'html.parser')
    things = soup.find_all('tr', {'class': 'athing'})

    for thing in things:
        comment_id = int(thing['id'])
        on_story = thing.select('.onstory > a')[0]
        story_id = int(on_story['href'].split('=')[-1])
        pairs.append((comment_id, story_id))

    return pairs


def inflate_comment(id, story):
    print('inflating...', id)
    comment = requests.get(
        f'https://hacker-news.firebaseio.com/v0/item/{id}.json').json()
    if comment is not None:
        comment['story'] = int(story)
    return comment


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Numeric, primary_key=True)
    by = Column(String)
    parent = Column(Numeric)
    text = Column(String)
    time = Column(DateTime)
    story = Column(Numeric)


db = create_engine(config['db']['uri'])
Base.metadata.create_all(db)

with db.connect() as conn:
    sess = Session(db)

    while True:
        print('Fetching new comments...')
        html = requests.get(
            'https://news.ycombinator.com/newcomments').text
        new_comments = 0

        for (comment_id, story_id) in comment_story_pairs(html):
            if comment_id in seen_comments:
                continue

            comment = inflate_comment(comment_id, story_id)
            if comment is None:
                continue

            sess.merge(Comment(
                by=comment['by'],
                id=comment['id'],
                parent=comment['parent'],
                text=comment['text'],
                time=datetime.datetime.utcfromtimestamp(comment['time']),
                story=comment['story']
            ))
            sess.commit()

            seen_comments.add(comment_id)
            new_comments += 1

        print('Produced', new_comments, 'new comments')
        time.sleep(15)
