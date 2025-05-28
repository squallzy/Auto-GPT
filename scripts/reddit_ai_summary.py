import os
import datetime
from pathlib import Path
from typing import List

import openai
import praw


SUBREDDITS = ["Artificial", "MachineLearning", "singularity", "deeplearning"]
POST_LIMIT = 10
TARGET_CHARS = 2000


def fetch_top_posts(limit: int = POST_LIMIT) -> List[str]:
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "reddit_ai_summary_script"),
    )
    per_sub_limit = max(1, limit // len(SUBREDDITS))
    posts = []
    for sub in SUBREDDITS:
        for post in reddit.subreddit(sub).top(time_filter="day", limit=per_sub_limit):
            content = post.selftext or ""
            posts.append(f"Title: {post.title}\n{content}")
            if len(posts) >= limit:
                break
        if len(posts) >= limit:
            break
    return posts


def generate_summary(posts: List[str], target_chars: int = TARGET_CHARS) -> str:
    prompt = (
        "\n\n".join(posts)
        + "\n\n请基于以上内容用中文撰写约"
        + str(target_chars)
        + "字的摘要："
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message["content"].strip()


def main() -> None:
    posts = fetch_top_posts()
    summary = generate_summary(posts)
    today = datetime.date.today().isoformat()
    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"reddit_ai_summary_{today}.txt"
    out_file.write_text(summary, encoding="utf-8")
    print(f"Summary saved to {out_file}")


if __name__ == "__main__":
    main()
