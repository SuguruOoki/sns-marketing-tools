import twint

c = twint.Config()
c.Search = "#駆け出しエンジニアと繋がりたい"
c.Min_likes = 3
c.Limit=100000
c.Lang="ja"
c.Output="kakedashi.csv"
c.Store_csv=True

twint.run.Search(c)
