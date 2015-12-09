# UserSim
Like [/r/SubredditSimulator,](http://www.reddit.com/r/SubredditSimulator) but for individual users.

Check out the subreddit at [/r/User_Simulator](http://www.reddit.com/r/User_Simulator) for announcements, updates, or if you just want somewhere to test it to your heart's content.

### What is this?

[/u/User_Simulator](http://www.reddit.com/user/User_Simulator) is a summonable Reddit bot that reads a particular user's last 1000 comments and uses Markov chains to construct comments in that user's style.

Basically, it pretends to be you. It's what you would write if you were a robot with a nice vocabulary but no understanding of how words should fit together.

### How do I use it?

Summon it like this:

    +/u/User_Simulator some-user
  
or

    +/u/User_Simulator /u/some-user
  
if you want that user to get a notification as well.

It's probably running right now; give it a try!

### It didn't work for me. Why not?

It only works on users that have 25 or more comments visible on their userpage, and if the user's comments have little variety (e.g. 25 of the exact same comment), then the bot might not be able to come up with a unique response.

### What libraries does it use?

It uses [markovify](https://github.com/jsvine/markovify), like SubredditSimulator, as well as [NLTK](http://www.nltk.org/) for more coherent responses. Also [PRAW.](https://praw.readthedocs.org/en/v3.1.0/) All the other libraries it uses should be preinstalled with Python.

Like SubredditSimulator, it avoids making comments that are complete and direct quotes of the user. Each comment it makes will be stitched together from at least two of the source user's comments.


### I got a really unfunny reply. This is asenine.

Yeah, it's a bot and it generates its responses randomly; it doesn't know what's funny and what's not. Sometimes its responses are hilariously absurd; other times they're boring and weird and completely unfunny. You're welcome to page it again for a new response if you don't like the last one you got.

-----

If you have any questions or ideas, shoot me a PM at [/u/Trambelus.](https://www.reddit.com/message/compose/?to=trambelus)

-----

### Currently banned in 78 subreddits:

/r/AceAttorney, /r/AgainstGamerGate, /r/ApocalypseRising, /r/Art, /r/AskReddit, /r/CFB, /r/CadenMoranDiary, /r/Calgary, /r/Cardinals, /r/CasualConversation, /r/Civcraft, /r/Coffee, /r/Cricket, /r/DarkNetMarkets, /r/Denmark, /r/DestinyTheGame, /r/Eve, /r/GlobalOffensive, /r/HPMOR, /r/InternetIsBeautiful, /r/KCRoyals, /r/MLS, /r/NASCAR, /r/NoStupidQuestions, /r/Omnipotent_League, /r/Patriots, /r/RWBY, /r/SFGiants, /r/SammyClassicSonicFan, /r/ShitRedditSays, /r/SubredditDrama, /r/SubredditSimMeta, /r/TheWaterLew, /r/Weaselwarren, /r/Whatcouldgowrong, /r/Wishlist, /r/abc, /r/anime, /r/atheism, /r/australia, /r/badhistory, /r/blackladies, /r/cardsagainsthumanity, /r/cringepics, /r/fireemblem, /r/flicks, /r/formula1, /r/gameofthrones, /r/gaming, /r/gifs, /r/india, /r/leagueoflegends, /r/magicTCG, /r/mylittleandysonic1, /r/nba, /r/nbacirclejerk, /r/news, /r/offmychest, /r/paradoxplaza, /r/pcmasterrace, /r/politics, /r/quityourbullshit, /r/reactiongifs, /r/relationships, /r/roosterteeth, /r/rupaulsdragrace, /r/science, /r/smashbros, /r/soccer, /r/syriancivilwar, /r/tf2, /r/todayilearned, /r/unitedkingdom, /r/videos, /r/worldnews, /r/worldpowers, /r/wow, /r/wsgy

*List updated: 2015-10-12 1509 EDT*
