from bot import CommandBot
import time

def main():
    bot = CommandBot()
    f = open('/path-to-pm_log-dir/pm_log', 'a+')
    while True:
        try:
            bot.get_private_messages()
            time.sleep(10*60)
        except Exception as e:
            print(str(e))
            f.write(str(e))

if __name__ == "__main__":
    main()
