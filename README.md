# UserSim
Like [/r/SubredditSimulator,](http://www.reddit.com/r/SubredditSimulator) but for individual users.

### What is this?

[/u/User_Simulator](http://www.reddit.com/user/User_Simulator) is a summonable Reddit bot that uses Markov chains to construct comments in a particular user's style.

### How do I use it?

Summon it like this:

    +/u/User_Simulator some-user
  
or

    +/u/User_Simulator /u/some-user
  
if you want that user to get a notification as well.

It's probably running right now; give it a try!

### It didn't work for me. Why not?

It only works on users that have fifty or more comments visible on their userpage, and if the user's comments have little variety (e.g. fifty of the exact same comment), then the bot might not be able to come up with a unique response.

### What libraries does it use?

It uses [markovify](https://github.com/jsvine/markovify), like SubredditSimulator, as well as [NLTK](http://www.nltk.org/) for more coherent responses. Also [PRAW.](https://praw.readthedocs.org/en/v3.1.0/) All the other libraries it uses should be preinstalled with Python.

Like SubredditSimulator, it avoids making comments that are complete and direct quotes of the user. Each comment it makes will be stitched together from at least two of the source user's comments.

-----

If you have any questions or ideas, shoot me a PM at [/u/Trambelus.](https://www.reddit.com/message/compose/?to=trambelus)
