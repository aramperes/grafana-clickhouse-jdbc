CREATE TABLE comments_pg
(
    `id` Int32,
    `by` String,
    `parent` Int32,
    `text` Nullable(String),
    `time` DateTime64(6),
    `story` Int32
)
ENGINE = JDBC('jdbc:postgresql://postgres:5432/hn?user=hn&password=password', 'public', 'comments');

---

CREATE TABLE stories_pg
(
    `id` Int32,
    `by` String,
    `score` Int32,
    `title` Nullable(String),
    `time` DateTime64(6),
    `url` Nullable(String)
)
ENGINE = JDBC('jdbc:postgresql://postgres:5432/hn?user=hn&password=password', 'public', 'stories');

---

CREATE LIVE VIEW comments
WITH REFRESH 30
AS SELECT
  *
FROM comments_pg;

---

CREATE LIVE VIEW stories
WITH REFRESH 30
AS SELECT
  *
FROM stories_pg;