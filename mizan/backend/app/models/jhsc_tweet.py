import enum
from sqlalchemy import Column, BigInteger, Integer, Text, Enum
from app.database import Base


class JhscLabel(str, enum.Enum):
    negative = "negative"
    neutral = "neutral"
    positive = "positive"
    very_positive = "very positive"


class JhscTweet(Base):
    __tablename__ = "jhsc_tweets"

    id = Column(BigInteger, primary_key=True)
    text = Column(Text, nullable=True)
    label = Column(
        Enum(JhscLabel, name="jhsclabel", create_constraint=True),
        nullable=False,
    )
    tweet_year = Column(Integer, nullable=False)
    tweet_month = Column(Integer, nullable=False)
