## Command Bot for Twitter

#### What's it for?

- Helps you or your community tweet repetitive content to users.
- Helps your brand's community contribute towards support and miscellaneous tasks.

#### Performance:

Twitter user [@MehowBrains](https://twitter.com/mehowbrains) commissioned his crew to get this bot developed, and deployed one for the [@THORChain_org](https://twitter.com/thorchain_org) community under the [@THORChainHammer](https://twitter.com/thorchainhammer) bot. He's used it religiously over several months, and in July 2020 it helped him amass over [812,000 impressions](https://twitter.com/mehowbrains/status/1290522595532722177?s=20) to his tweets.

#### Functions:

- You or your community can tweet a content command and get a tweet-back from the the bot with the requested content.
- You or your community can tweet a join role command to be assigned into that user group / role.
- You or your community can tweet a task command and get a tweet-back from the the bot with the requested tasks for the role.
- Admins can manage content, roles, tasks, users and admins by DM'ing the bot.

#### Use-case examples:

Here's some examples from the [@THORChainHammer](https://twitter.com/thorchainhammer) bot that [@MehowBrains](https://twitter.com/mehowbrains) deployed:

a) Users often tweet questions to one another "what's the link to the Google sheet which contains the emission schedule?". A bot command can help you or any other users reply to that tweet without actually looking for the link themselves. They'd just tweet something like: <b>[@THORChainHammer emissions](https://twitter.com/mehowbrains/status/1276806930166661120?s=20)</b> --- and the bot will reply with the link. You or other users were now able to join-in on supporting the request by simply learning the command. The bot is great for organizing content via custom commands that you name. You can set links to websites, tweets etc. Think of it like having a website at your fingertips. You no longer have to go look for the content, you just need to memorize commands and tweet them out.

b) Users often want to help a community, but don't know what to do or who to ask for directions. Teams are also busy developing stuff, and often the community is left with the role to shill and support. But many of these followers are in fact experts at something usually, whether it be marketing, engineering, design etc. So I wanted to develop an easier way to communicate tasks to followers, without necessarily having to interact with them directly one by one. With the bot, an admin can create a role for his Twitter community i.e. #THORChainMarketers, write a medium article or tweet about the on-going tasks for that role, and link the content to that role. A user would tweet <b>[@THORChainHammer tasks THORChainMarketer](https://twitter.com/mehowbrains/status/1293737792036642816?s=20)</b> -- and the bot would reply with the link to the medium post / tweet which highlights the tasks they can be working-on.
<br>

*****

### Bot internals:

The bot really functions as 2 separate bots

- bot.py - which handles all public commands.
- pm.py - which handles all administrative commands.

<b>bot.py</b> is pretty simple. It gets all mentions using standard API. Since this bot is coded in Python, there's a library, Tweepy, that does all behind scenes. Once it gets all mentions, it processes each one. To determine which command it has to execute, it compares based on some standard commands. If none of them matches, then it will look for content in DB. Content is the text that an admin user sets up. Finally, it saves every message ID into the database. When processing mentions it check whether it wasn't already processed or it wasn't generated more than a day ago. If this condition meets, it will process. Otherwise, it will ignore this mention.

<b>pm_bot.py</b> commands work in a similar way, but instead of getting mentions, it will get received private messages for the administrator's commands via DM (or as we call it: PM aka private message).

*****

### Running the bot:

1) In the tweets.db SQLite database:
	
	* Create a master admin user by: 
		* Creating a new row in the users_by_role table:

			* userid = the Twitter userid for the @handle that'll be the master administrator. That userid for the handle can be found via tools like [TwitterID.com](https://www.tweeterid.com).

			*  role_id = 1

2) In the bot.py file:

	* Set your [Twitter Developer](https://developer.twitter.com/en) API credentials:

		* `consumer_token = ''`
		* `consumer_secret = ''`
		* `access_token = ''`
		* `access_token_secret = ''`

    * Set the path where the tweets.db is stored. By default it's set to: `/root/command-bot/tweets.db`

    * Set the path where you'd like to log exceptions. By default it's set to: `/root/command-bot/log`

    * Set the link for your admin and public guides (i.e. if users tweet <b>[@THORChainHammer help](https://twitter.com/mehowbrains/status/1287492093737349120?s=20)</b>, they'll get a tweet back with the link to the [public guide](https://medium.com/@thorchaincommunity/thorchainhammer-bot-overview-6992a5b8de2d)):

		* `LINK_TO_ADMIN_HELP_LINK = 'link-to-the-admin-guide-between-the-quotes'`
		* `LINK_TO_PUBLIC_TWEET_HELP = 'link-to-the-public-guide-between-the-quotes'`

3) In the pm_bot.py file:

	* Set the path where you'd like to log exceptions for the pm bot. By default it's set to: `/root/command-bot/pm_log`

It's recommended that the bot be setup on a VPS for availability.

*****

### Using the bot:

#### Administrative commands:

If your handle was set as a master administrator in the tweets.db file, you can DM the bot the following commands to manage it:

- <b>Help:</b>
	- Command: `help`
	- Replies: `Link to the admin guide previous set in the bot.py`

- <b>Content:</b>
	- Command: `add-content command-name link`
	- Command: `edit-content command-name new-link`
	- Command: `remove-content command-name`
	- Command: `content`
 
- <b>Role:</b>
	- Command: `add-role role-name`
	- Command: `edit-role role-name new-role-name`
	- Command: `remove-role role-name`
	- Command: `recruit @handle role-name`
	- Command: `fire @user-handle role-name`
	- Command: `role @user-handle`

- <b>Tasks:</b>
	- Command: `add-task role-name link`
	- Command: `edit-task role-name new-link`
	- Command: `remove-task role-name`

#### Public commands:

These commands are available for anyone to tweet:

- <b>Help:</b>
	- Command: `@bot-handle-name help`
	- Replies: `Link to the public guide previous set in the bot.py`

- <b>Content:</b>
	- Command: `@bot-handle-name command-name`

- <b>Role:</b>
	- Command: `@bot-handle-name recruit` 
	- Command: `@bot-handle-name join role-name`
	- Command: `@bot-handle-name quit role-name` 
	- Command: `@bot-handle-name role`

- <b>Tasks:</b>
	- Command: `@bot-handle-name tasks role-name`

- <b>Stalk:</b>
	- Command: `@bot-handle-name stalk keyword`

<br>
