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


### I got a really dumb reply. This is dumb.

Yeah, it's a bot and it generates its responses randomly; it doesn't know what's funny and what's not. Sometimes its responses are hilariously absurd; other times they're boring and weird and completely unfunny. You're welcome to page it again for a new response if you don't like the last one you got.

-----

If you have any questions or ideas, shoot me a PM at [/u/Trambelus.](https://www.reddit.com/message/compose/?to=trambelus)

-----

### Currently banned in 109 subreddits:

[/r/AceAttorney](http://reddit.com/r/AceAttorney), [/r/AgainstGamerGate](http://reddit.com/r/AgainstGamerGate), [/r/ApocalypseRising](http://reddit.com/r/ApocalypseRising), [/r/Art](http://reddit.com/r/Art), [/r/AskReddit](http://reddit.com/r/AskReddit), [/r/BestOfReports](http://reddit.com/r/BestOfReports), [/r/BlackPeopleTwitter](http://reddit.com/r/BlackPeopleTwitter), [/r/Braveryjerk](http://reddit.com/r/Braveryjerk), [/r/CanadianForces](http://reddit.com/r/CanadianForces), [/r/CFB](http://reddit.com/r/CFB), [/r/CadenMoranDiary](http://reddit.com/r/CadenMoranDiary), [/r/Calgary](http://reddit.com/r/Calgary), [/r/Cardinals](http://reddit.com/r/Cardinals), [/r/CasualConversation](http://reddit.com/r/CasualConversation), [/r/Civcraft](http://reddit.com/r/Civcraft), [/r/Coffee](http://reddit.com/r/Coffee), [/r/Cricket](http://reddit.com/r/Cricket), [/r/DarkNetMarkets](http://reddit.com/r/DarkNetMarkets), [/r/Denmark](http://reddit.com/r/Denmark), [/r/DestinyTheGame](http://reddit.com/r/DestinyTheGame), [/r/Documentaries](http://reddit.com/r/Documentaries), [/r/Eve](http://reddit.com/r/Eve), [/r/EnoughTrumpSpam](http://reddit.com/r/EnoughTrumpSpam),  [/r/Futurology](http://reddit.com/r/Futurology), [/r/GlobalOffensive](http://reddit.com/r/GlobalOffensive), [/r/HPMOR](http://reddit.com/r/HPMOR), [/r/HighQualityGifs](http://reddit.com/r/HighQualityGifs), [/r/HillaryForPrison](http://reddit.com/r/HillaryForPrison), [/r/InternetIsBeautiful](http://reddit.com/r/InternetIsBeautiful), [/r/Jokes](http://reddit.com/r/Jokes), [/r/JonTron](http://reddit.com/r/JonTron), [/r/KCRoyals](http://reddit.com/r/KCRoyals), [/r/MLS](http://reddit.com/r/MLS), [/r/NASCAR](http://reddit.com/r/NASCAR), [/r/NoEntryToClub86](http://reddit.com/r/NoEntryToClub86), [/r/NoStupidQuestions](http://reddit.com/r/NoStupidQuestions), [/r/Omnipotent_League](http://reddit.com/r/Omnipotent_League), [/r/OutOfTheLoop](http://reddit.com/r/OutOfTheLoop), [/r/Patriots](http://reddit.com/r/Patriots), [/r/RWBY](http://reddit.com/r/RWBY), [/r/SFGiants](http://reddit.com/r/SFGiants), [/r/SammyClassicSonicFan](http://reddit.com/r/SammyClassicSonicFan), [/r/ShitRedditSays](http://reddit.com/r/ShitRedditSays), [/r/Skyremcoop](http://reddit.com/r/Skyremcoop), [/r/SubredditDrama](http://reddit.com/r/SubredditDrama), [/r/SubredditSimMeta](http://reddit.com/r/SubredditSimMeta), [/r/TheWaterLew](http://reddit.com/r/TheWaterLew), [/r/Unexpected](http://reddit.com/r/Unexpected), [/r/WTF](http://reddit.com/r/WTF), [/r/Weaselwarren](http://reddit.com/r/Weaselwarren), [/r/Whatcouldgowrong](http://reddit.com/r/Whatcouldgowrong), [/r/Wishlist](http://reddit.com/r/Wishlist), [/r/abc](http://reddit.com/r/abc), [/r/anime](http://reddit.com/r/anime), [/r/atheism](http://reddit.com/r/atheism), [/r/australia](http://reddit.com/r/australia), [/r/aww](http://reddit.com/r/aww), [/r/badhistory](http://reddit.com/r/badhistory), [/r/blackladies](http://reddit.com/r/blackladies), [/r/cardsagainsthumanity](http://reddit.com/r/cardsagainsthumanity), [/r/cringepics](http://reddit.com/r/cringepics), [/r/depression](http://reddit.com/r/depression), [/r/exmormon](http://reddit.com/r/exmormon), [/r/explainlikeimfive](http://reddit.com/r/explainlikeimfive), [/r/fireemblem](http://reddit.com/r/fireemblem), [/r/flicks](http://reddit.com/r/flicks), [/r/formula1](http://reddit.com/r/formula1), [/r/gameofthrones](http://reddit.com/r/gameofthrones), [/r/gaming](http://reddit.com/r/gaming), [/r/gifs](http://reddit.com/r/gifs), [/r/guns](http://reddit.com/r/guns), [/r/hockey](http://reddit.com/r/hockey), [/r/hoi4](http://reddit.com/r/hoi4),  [/r/india](http://reddit.com/r/india), [/r/leagueoflegends](http://reddit.com/r/leagueoflegends), [/r/magicTCG](http://reddit.com/r/magicTCG), [/r/mylittleandysonic1](http://reddit.com/r/mylittleandysonic1), [/r/nba](http://reddit.com/r/nba), [/r/nbacirclejerk](http://reddit.com/r/nbacirclejerk), [/r/news](http://reddit.com/r/news), [/r/nottheonion](http://reddit.com/r/nottheonion), [/r/offmychest](http://reddit.com/r/offmychest), [/r/paradoxplaza](http://reddit.com/r/paradoxplaza), [/r/pcmasterrace](http://reddit.com/r/pcmasterrace), [/r/politics](http://reddit.com/r/politics), [/r/quityourbullshit](http://reddit.com/r/quityourbullshit), [/r/rage](http://reddit.com/r/rage), [/r/rant](http://reddit.com/r/rant), [/r/reactiongifs](http://reddit.com/r/reactiongifs), [/r/relationships](http://reddit.com/r/relationships), [/r/roosterteeth](http://reddit.com/r/roosterteeth), [/r/rupaulsdragrace](http://reddit.com/r/rupaulsdragrace), [/r/science](http://reddit.com/r/science), [/r/smashbros](http://reddit.com/r/smashbros), [/r/soccer](http://reddit.com/r/soccer), [/r/syriancivilwar](http://reddit.com/r/syriancivilwar), [/r/tf2](http://reddit.com/r/tf2), [/r/thenetherlands](http://reddit.com/r/thenetherlands), [/r/tifu](http://reddit.com/r/tifu), [/r/todayilearned](http://reddit.com/r/todayilearned), [/r/toronto](http://reddit.com/r/toronto), [/r/ukpolitics](http://reddit.com/r/ukpolitics), [/r/unitedkingdom](http://reddit.com/r/unitedkingdom), [/r/videos](http://reddit.com/r/videos), [/r/worldnews](http://reddit.com/r/worldnews), [/r/worldpowers](http://reddit.com/r/worldpowers), [/r/wow](http://reddit.com/r/wow), [/r/wsgy](http://reddit.com/r/wsgy), [/r/yugioh](http://reddit.com/r/yugioh)

*List updated: 2016-07-25 1348 EDT*
