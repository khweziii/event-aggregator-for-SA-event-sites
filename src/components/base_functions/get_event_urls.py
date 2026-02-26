from src.logger import logging 


def get_event_urls_from_users():
    '''
    Prompt the user to enter as many event URLs as they'd like
    '''
    logging.info("Getting events from users initialized")
    terminator = False 
    event_urls = []

    while terminator == False:

        user_input = input("Enter event URL: \n")

        if user_input == "stop":
            terminator = True

        else:
            event_urls.append(user_input)

    print(f"Found {len(event_urls)} event URLs")
    logging.info("Getting events from users completed")
    return event_urls
