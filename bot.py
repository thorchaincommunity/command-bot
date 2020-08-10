import re
import datetime
import tweepy
import sqlite3
import time
from dateutil.relativedelta import relativedelta

LINK_TO_ADMIN_HELP_LINK = ''
LINK_TO_PUBLIC_TWEET_HELP = ''
MAX_TWEET_LEN = 280
ADMIN_ROLE = ''


class BotException(Exception):
    pass


class CommandBot:

    def __init__(self):
        # Bot constants
        consumer_token = ''
        consumer_secret = ''
        access_token = ''
        access_token_secret = ''

        auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        self.api = tweepy.API(auth)
        self.available_commands = set()

        # account ID
        self.current_UID = self.api.me().id

        # account name
        self.account_name = self.api.me().screen_name.strip()

        # location of sqlite DB
        self.con_bd = sqlite3.connect('/path-to-tweetsdb_dir/tweets.db')
        self.cursor = self.con_bd.cursor()
        self.cursor.execute("SELECT tweet_id FROM processed_mentions")
        rows = self.cursor.fetchall()

    def tweet(self, message, tweet_id=None, remote_user=None):
        """Tweets the message given by message. tweet_id and remote_user are to mention"""
        try:
            if tweet_id and remote_user:
                self.api.update_status('@' + remote_user + ' ' + message, tweet_id)
            else:
                self.api.update_status(message)
        except Exception as e:
            print(str(e))


    def process_admin_command(self, userid, text):
        """Processes commands based on regular expressions. These commands arrive by PMs"""
        if (m := re.match('^ADD-ROLE\s*([\S]*)$', text, re.IGNORECASE)) is not None:
            role_name = m.group(1).strip()

            if len(role_name) == 0:
                raise BotException("There's a problem with your command, make sure to follow this guide: " +
                                   LINK_TO_ADMIN_HELP_LINK)
            self.add_role(role_name)
        elif (m := re.match('^REMOVE-ROLE\s*([\S]*)$', text, re.IGNORECASE)) is not None:
            role_name = m.group(1).strip()

            if len(role_name) == 0:
                raise BotException("There's a problem with your command, make sure to follow this guide: " +
                                   LINK_TO_ADMIN_HELP_LINK)
            self.remove_roles(role_name)
        elif (m := re.match('^EDIT-ROLE\s*([\S]*)\s*(.*)$', text, re.IGNORECASE)) is not None:
            old_name = m.group(1).strip()
            new_name = m.group(2).strip()

            if len(old_name) == 0 or len(new_name) == 0:
                raise BotException("There's a problem with your command, make sure to follow this guide: " +
                                   LINK_TO_ADMIN_HELP_LINK)
            self.modify_role(old_name, new_name)
        elif (m := re.match('^ADD-CONTENT\s*([\S]*)\s*(.*)$', text, re.IGNORECASE)) is not None:
            command = m.group(1).strip().upper()
            content = m.group(2).strip()

            if len(command) == 0 or len(content) == 0:
                raise BotException("There's a problem with your command, make sure to follow this guide: " +
                                   LINK_TO_ADMIN_HELP_LINK)
            if len(content) >= MAX_TWEET_LEN:
                raise BotException("Your content is too long, the limit is " + str(MAX_TWEET_LEN) +
                                   " characters. It wasn't saved, please try again.")
            self.add_content(command, content)
        elif (m := re.match('^EDIT-CONTENT\s*([\S]*)\s*(.*)$', text, re.IGNORECASE)) is not None:
            command = m.group(1).strip().upper()
            content = m.group(2).strip()

            if len(command) == 0 or len(content) == 0:
                raise BotException("There's a problem with your command, make sure to follow this guide: " +
                                   LINK_TO_ADMIN_HELP_LINK)

            if len(content) >= MAX_TWEET_LEN:
                raise BotException("Your content is too long, the limit is " + str(MAX_TWEET_LEN) +
                                   " characters. It wasn't saved, please try again.")

            self.modify_content(command, content)
        elif (m := re.match('^REMOVE-CONTENT\s*([\S]*)$', text, re.IGNORECASE)) is not None:
            command = m.group(1).strip().upper()

            if len(command) == 0:
                raise BotException("There's a problem with your command, make sure to follow this guide: " +
                                   LINK_TO_ADMIN_HELP_LINK)
            self.del_content(command)
        elif (m := re.match('^ADD-TASK\s*([\S]*)\s*(.*)$', text, re.IGNORECASE)) is not None:
            command = m.group(1).strip().upper()
            content = m.group(2).strip()
            if len(command) == 0 or len(content) == 0:
                raise BotException("There's a problem with your command, make sure to follow this guide: " +
                                   LINK_TO_ADMIN_HELP_LINK)
            self.add_task(command, content)
        elif (m := re.match('^EDIT-TASK\s*([\S]*)\s*(.*)$', text, re.IGNORECASE)) is not None:
            command = m.group(1).strip().upper()
            content = m.group(2).strip()
            if len(command) == 0 or len(content) == 0:
                raise BotException("There's a problem with your command, make sure to follow this guide: " +
                                   LINK_TO_ADMIN_HELP_LINK)
            self.modify_task(command, content)
        elif (m := re.match('^REMOVE-TASK\s*([\S]*)$', text, re.IGNORECASE)) is not None:
            command = m.group(1).strip().upper()
            if len(command) == 0:
                raise BotException("There's a problem with your command, make sure to follow this guide: " +
                                   LINK_TO_ADMIN_HELP_LINK)
            self.del_task(command)
        else:
            return False

        return True

    def pm_was_processed(self, message_id):
        """Checks if a received PM was processed or not"""
        self.cursor.execute("SELECT count(*) FROM processed_pms WHERE message_id = ?", (message_id,))
        row_count = self.cursor.fetchone()
        return row_count[0] != 0

    def tweet_was_processed(self, tweet_id):
        """Checks if a received tweet was processed or not"""
        self.cursor.execute("SELECT count(*) FROM processed_mentions WHERE tweet_id = ?", (tweet_id,))
        row_count = self.cursor.fetchone()
        return row_count[0] != 0

    def mark_pm_as_processed(self, message_id, timestamp):
        """Marks a PM as processed on db"""
        self.cursor.execute("INSERT INTO processed_pms (message_id, timestamp) VALUES (?,?)", (message_id, timestamp))
        self.con_bd.commit()

    def mark_tweet_as_processed(self, tweet_id, tweet_timestamp):
        """Marks a tweet as processed on db"""
        self.cursor.execute("INSERT INTO processed_mentions VALUES(?,?)", (tweet_id, tweet_timestamp))
        self.con_bd.commit()

    def check_task_exists(self, task_name):
        """Checks if a task exists"""
        self.cursor.execute("SELECT count(*) from tasks WHERE task_name = ?", (task_name,))
        row_count = self.cursor.fetchone()
        return row_count[0] != 0

    def add_task(self, task_name, text):
        """Adds a new task to DB"""
        if self.check_task_exists(task_name):
            raise BotException("Task already registered")
        self.cursor.execute("INSERT INTO tasks (task_name, text) VALUES (?, ?)", (task_name, text))
        self.con_bd.commit()

    def del_task(self, task_name):
        """Deletes a task from db"""
        if not self.check_task_exists(task_name):
            raise BotException("Task doesn't exist")
        self.cursor.execute("DELETE FROM tasks WHERE task_name = ?", (task_name,))
        self.con_bd.commit()

    def modify_task(self, task_name, new_text):
        """Modifies a task"""
        if not self.check_task_exists(task_name):
            raise BotException("Task doesn't exist")
        self.cursor.execute("UPDATE tasks SET text = ? WHERE task_name = ?", (new_text, task_name))
        self.con_bd.commit()

    def add_content(self, command, text):
        """Adds content to db"""
        self.cursor.execute("INSERT INTO content (command, text) VALUES (?, ?)", (command, text))
        self.con_bd.commit()

    def del_content(self, command):
        """Deletes content from db"""
        self.cursor.execute("DELETE FROM content WHERE command = ?", (command,))
        self.con_bd.commit()

    def modify_content(self, command, new_text):
        """Modifies content from db"""
        self.cursor.execute("UPDATE content SET text = ? WHERE command = ?", (new_text, command))
        self.con_bd.commit()

    def get_all_contents(self):
        """Gets all content"""
        self.cursor.execute("SELECT command FROM content ORDER BY command ASC")
        rows = self.cursor.fetchall()
        return rows

    def get_text_from_content(self, command):
        """Gets associated text from content"""
        self.cursor.execute("SELECT text FROM content WHERE command = ?", (command,))
        row = self.cursor.fetchone()
        if row is not None and len(row) > 0:
            return row[0]
        return None

    def get_text_from_task(self, task_name):
        """Gets associated text from task"""
        self.cursor.execute("SELECT text FROM tasks WHERE task_name = ?", (task_name,))
        row = self.cursor.fetchone()
        if row is not None and len(row) > 0:
            return row[0]
        return None

    def add_role(self, role_name):
        """Adds a role to db. Internal function"""
        self.cursor.execute("INSERT INTO roles (role_name, display_name, enabled) VALUES (?, ?, 1)",
                            (role_name.upper(), role_name))
        self.con_bd.commit()

    def remove_roles(self, role_name):
        """Removes a role to db. Internal function"""
        if re.match('^' + ADMIN_ROLE + '$', role_name, re.IGNORECASE):
            raise BotException("Admin role can't be deleted")
        self.cursor.execute("UPDATE roles set enabled = 0 WHERE role_name = ?", (role_name.upper(),))
        self.con_bd.commit()

    def modify_role(self, role_name, new_role_name):
        """Modifies a role to db. Internal function"""
        if re.match('^' + ADMIN_ROLE + '$', role_name, re.IGNORECASE):
            raise BotException("Admin role can't be modified")
        self.cursor.execute("UPDATE roles set role_name = ? WHERE role_name = ?",
                            (new_role_name.upper(), role_name.upper()))
        self.con_bd.commit()
        self.cursor.execute("UPDATE roles set display_name = ? WHERE role_name = ?",
                            (new_role_name, new_role_name.upper()))
        self.con_bd.commit()

    def is_admin_user(self, userid):
        """Returns if a user is admin or not based on its userid"""
        self.cursor.execute("SELECT count(*) FROM users_by_role u INNER JOIN roles r ON u.role_id = r.id" \
                            " WHERE u.userid = ? AND r.role_name = '" + ADMIN_ROLE + "'", (userid,))
        row_count = self.cursor.fetchone()
        return row_count[0] != 0

    def query_role_id(self, role_name):
        """Gets the ID of a role specified by role_name"""
        try:
            self.cursor.execute("SELECT id FROM roles WHERE role_name = ?", (role_name.upper(),))
            row = self.cursor.fetchone()
            return row[0]
        except:
            raise BotException("Specified role does not exist")

    def get_all_roles(self, from_public_source=False):
        """Gets all roles. If from_public_source is True, it doesn't return admin role"""
        query = "SELECT display_name FROM roles WHERE enabled = 1 ORDER BY display_name ASC"
        if from_public_source:
            query = "SELECT display_name FROM roles WHERE enabled = 1 AND role_name <> '" + ADMIN_ROLE + "' ORDER BY display_name ASC"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def add_role_to_user(self, role_name, userid, from_public_source=False):
        """Adds a new role. If from_public_source is True, it will throw an exception because only admin members can
         do it"""
        if re.match('^' + ADMIN_ROLE + '$', role_name, re.IGNORECASE) and from_public_source:
            raise BotException("You don't have permissions to join this role.")
        self.cursor.execute("SELECT id FROM roles WHERE enabled = 1 AND role_name = ?", (role_name.upper(),))
        row = self.cursor.fetchone()
        if row is not None and len(row) == 0:
            raise BotException(
                "This role doesn't exist.")
        role_id = row[0]
        self.cursor.execute("SELECT count(*) FROM users_by_role WHERE role_id = ? and userid = ?", (role_id, userid))
        row_count = self.cursor.fetchone()
        if row_count[0] == 0:
            self.cursor.execute("INSERT INTO users_by_role (userid, role_id) VALUES (?, ?)", (userid, role_id))
            self.con_bd.commit()

    def remove_role_from_user(self, role_name, userid, from_public_source=False):
        """Removes a role. If from_public_source is True, it will throw an exception because only admin members can
         do it"""
        if re.match('^' + ADMIN_ROLE + '$', role_name, re.IGNORECASE) and from_public_source:
            raise BotException("You don't have permissions to join this role.")
        role_id = self.query_role_id(role_name)
        self.cursor.execute("DELETE FROM users_by_role WHERE userid = ? and role_id = ?", (userid, role_id))
        self.con_bd.commit()

    def get_roles_by_userid(self, userid, from_public_source=False):
        """Gets all roles. If from_public_source is True, it will return all roles except admin ones"""
        query = "SELECT r.display_name FROM roles r INNER JOIN users_by_role u ON u.role_id = r.id WHERE r.enabled = 1" \
                " AND u.userid = ? ORDER BY r.display_name"
        if from_public_source:
            query = "SELECT r.display_name FROM roles r INNER JOIN users_by_role u ON u.role_id = r.id WHERE r.enabled = 1" \
                    " AND u.userid = ? AND r.role_name <> '" + ADMIN_ROLE + "' ORDER BY r.display_name"
        self.cursor.execute(query, (userid,))
        return self.cursor.fetchall()

    def get_private_messages(self):
        """Gets and processes all PMs for the current user (user who's running the bot)"""
        pms = self.api.list_direct_messages()
        pms = reversed(pms)

        for pm in pms:
            timestamp = pm.created_timestamp
            sender = int(pm.message_create.get('sender_id'))
            text = pm.message_create.get('message_data').get('text')
            message_id = int(pm.id)
            if not self.is_admin_user(sender) or sender == self.current_UID:
                self.api.destroy_direct_message(message_id)
                continue
            if self.pm_was_processed(message_id):
                continue
            try:
                if re.match('^HELP$', text, re.IGNORECASE):
                    # TODO: change HELP DATA
                    self.api.send_direct_message(sender, "HELP DATA")
                elif re.match('^CONTENT$', text, re.IGNORECASE):
                    all_contents = self.get_all_contents()
                    if len(all_contents) > 0:
                        roles = list(map(lambda x: x[0].lower(), list(all_contents)))
                        message = '\n'.join(list(roles))
                    else:
                        raise BotException("There's a problem with your command, make sure to follow this guide: " + \
                                           LINK_TO_ADMIN_HELP_LINK)
                    self.api.send_direct_message(sender, message)
                elif (m := re.match('^ROLE\s*@([\w]*)$', text, re.IGNORECASE)) is not None:
                    user = m.group(1)
                    userid = self.api.get_user(screen_name=user).id
                    roles = self.get_roles_by_userid(userid)
                    if len(roles) == 0:
                        message = '@' + user + " doesn't have a role"
                    else:
                        roles = list(map(lambda x: x[0], list(roles)))
                        message = '\n'.join(list(roles))
                    self.api.send_direct_message(sender, message)
                elif (m := re.match('^RECRUIT\s*@([\w]*)\s*([\w]*)$', text, re.IGNORECASE)) is not None:
                    user = m.group(1)
                    role = m.group(2)
                    message = 'Recruited successfully.'
                    try:
                        if len(role) == 0 or len(user) == 0:
                            raise BotException("There's a problem with your command, make sure to follow this guide: " +
                                               LINK_TO_ADMIN_HELP_LINK)
                        userid = self.api.get_user(screen_name=user).id
                        self.add_role_to_user(role, userid)
                    except:
                        message = "There's a problem with your command, make sure to follow this guide: " + \
                                  LINK_TO_ADMIN_HELP_LINK
                    self.api.send_direct_message(sender, message)
                elif (m := re.match('^FIRE\s*@([\w]*)\s*([\w]*)$', text, re.IGNORECASE)) is not None:
                    user = m.group(1)
                    role = m.group(2)
                    message = 'Fired successfully.'
                    try:
                        if len(role) == 0 or len(user) == 0:
                            raise BotException("There's a problem with your command, make sure to follow this guide: " +
                                               LINK_TO_ADMIN_HELP_LINK)
                        userid = self.api.get_user(screen_name=user).id
                        self.remove_role_from_user(role, userid)
                    except:
                        message = "There's a problem with your command, make sure to follow this guide: " + \
                                  LINK_TO_ADMIN_HELP_LINK
                    self.api.send_direct_message(sender, message)
                else:
                    if self.process_admin_command(sender, text):
                        self.api.send_direct_message(sender, "Your command was successfully processed.")
                    else:
                        self.api.send_direct_message(sender, "The command doesn't exist, try: HELP")
            except BotException as e:
                self.api.send_direct_message(sender, str(e))
            self.mark_pm_as_processed(message_id, timestamp)

    def get_mentions(self):
        mentions = self.api.mentions_timeline()
        for mention in mentions:

            mention.text = mention.text.replace('@' + self.account_name, '').strip()

            remote_user = mention.author.screen_name
            tweet_id = mention.id
            tweet_timestamp = int(mention.created_at.timestamp())
            userid = mention.author.id
            if self.tweet_was_processed(tweet_id):
                continue

            # discards old mentions with more than 1 day from now
            if datetime.datetime.fromtimestamp(tweet_timestamp) + relativedelta(days=+1) < datetime.datetime.now():
                continue

            if userid == self.current_UID:
                continue

            while re.match('^(@[\\w-]*)', mention.text, re.IGNORECASE):
                mention.text = re.sub('^(@[\w-]*)', '', mention.text, re.IGNORECASE).strip()

            message = ''

            if (m := re.match('^HELP$', mention.text, re.IGNORECASE)) is not None:
                message = LINK_TO_PUBLIC_TWEET_HELP
            elif (m := re.match('^RECRUIT$', mention.text, re.IGNORECASE)) is not None:
                roles = self.get_all_roles(from_public_source=True)
                if len(roles) > 0:
                    roles = list(map(lambda x: x[0], list(roles)))
                    message = '\n'.join(list(roles))
                else:
                    message = "There's no roles registered on system"
            elif (m := re.match('^JOIN\s*([\w]*)$', mention.text, re.IGNORECASE)) is not None:
                hashtag = m.group(1).strip()
                if len(hashtag) > 0:
                    try:
                        self.add_role_to_user(hashtag.upper(), userid, from_public_source=True)
                        message = 'Welcome to #' + hashtag + '. ' + \
                                  hashtag
                    except BotException as e:
                        message = str(e)
            elif (m := re.match('^QUIT\s*([\w]*)$', mention.text, re.IGNORECASE)) is not None:
                hashtag = m.group(1).strip()
                if len(hashtag) > 0:
                    try:
                        self.remove_role_from_user(hashtag.upper(), userid, from_public_source=True)
                        message = "Sad to see you leave #" + hashtag + ". We're always here if you wish to join again!"
                    except BotException as e:
                        message = str(e)
            elif (m := re.match('^ROLE$', mention.text, re.IGNORECASE)) is not None:
                roles = self.get_roles_by_userid(userid, from_public_source=True)
                if len(roles) == 0:
                    message = "You haven't assigned yourself a role."
                else:
                    roles = list(map(lambda x: x[0], list(roles)))
                    message = ', '.join(list(roles))
            elif (m := re.match('^TASKS\s*([\w]*)$', mention.text, re.IGNORECASE)) is not None:
                hashtag = m.group(1).strip()
                if len(hashtag) > 0:
                    message = self.get_text_from_task(hashtag.upper())
                    if message is None:
                        message = "The admin didn’t set any tasks yet, but I'll make sure to let all #" + hashtag + \
                                  " know when they do!"
            elif (m := re.match('STALK\s*([\w]*)$', mention.text, re.IGNORECASE)) is not None:
                hashtag = m.group(1).strip().lower()
                if len(hashtag) > 0:
                    message = 'https://twitter.com/search?q=' + hashtag + '&src=typed_query&f=live'
            elif (content := self.get_text_from_content(mention.text.upper())) is not None:
                message = content

            if len(message) > 0:
                # Tweets the message given by message variable
                self.tweet(message, tweet_id, remote_user)

            # Saves mentions onto db
            self.mark_tweet_as_processed(tweet_id, tweet_timestamp)

def main():
    bot = CommandBot()
    # Log file
    f = open('/path-to-log-dir/log', 'a+')
    while True:
        try:
            bot.get_mentions()
            time.sleep(15)
        except BotException as e:
            print("Bot exception: " + str(e))
        except Exception as e:
            print(str(e))
            f.write(str(e))


if __name__ == "__main__":
    main()
