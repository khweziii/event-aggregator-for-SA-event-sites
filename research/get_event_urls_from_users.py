

"""
Docstring for research.get_event_urls_from_users
This is designed to prompt a user to upload urls, until they are done

Everytime they press "Enter" they url gets appended to a list 
Once they click "Done" the prompt to upload urls will terminate and the final object returned will be a list called event_urls
"""

def get_event_urls_from_users():
    '''
    Prompt the user to enter as many event URLs as they'd like
    '''
    terminator = False 
    event_urls = []

    while terminator == False:

        user_input = input("Enter event URL: \n")

        if user_input == "stop":
            terminator = True

        else:
            event_urls.append(user_input)

    print(f"Found {len(event_urls)} event URLs")

    return event_urls



print(get_event_urls_from_users())

        
