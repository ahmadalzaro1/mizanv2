Description of Jordanian Hate Speech Corpus (JHSC):

The folder consists of two CSV files: 

1. annotated-hatetweets-4-classes_train.csv

Which contains (302,766) labeled tweets

2. annotated-hatetweets-4-classes_test.csv

Which contains (100,923) labeled tweets



Each file contains three features: 
1. Tweet id: Unique ID given for each tweet (removed before training)
2. Text: The tweet text in Arabic, cleaned and pre-processed.
3. Label: the dataset has 4 labels:
        a. Negative: No hate speech is included in the tweet.
	b. Neutral: General tweet (add, prayer, no sentiment is included)
	c. Positive: A hate speech exists, bullying, sarcasm, racism, ...etc.
	d. Very positive: A severe hate speech exists; includes phrases that can cause fights, or very bad influence on people and society.

	