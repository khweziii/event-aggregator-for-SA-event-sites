import requests
from .date_extractor import extract_date_components
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
from src.components.base_scrapers.places_function import get_place_id
from src.logger import logging
from bs4 import BeautifulSoup




def howler_event_extractor(event_link, email):

    # header = {
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
    #     "X-Amzn-Trace-Id": "Root=1-679df051-2daca5245a793cdb15e9d7e9"
    #   }
    logging.info("Starting howler extractor function")

    load_dotenv()
    # print("before request")
    # page = requests.get(event_link, headers=header)
    page = requests.get(event_link)

    # print("after request")


    soup = BeautifulSoup(page.content, "html.parser")

    # print("before event page div")
    ##-----------------------this div contains the other divs that have info we want
    event_page = soup.find("div", class_="page-wrapper")
    ##-----------------------this div contains the other divs that have info we want
    # print("after event page div")

    # print("before event hero")
    ##-----------------------traversing through div elements to get event name and event category
    event_hero = event_page.find("div", class_="event-hero")
    hero_one = event_hero.find("div", class_="inset-x--large-on-medium")
    hero_two = hero_one.find("div", class_="event-hero__content")
    hero_three = hero_two.find("div", class_="event-hero__category")
    hero_event_name = hero_two.find("h1", class_="t-display")
    hero_event_category = hero_three.find("div", class_="label label--inverse")
    try:
        hero_event_image = hero_two.find("img")
    except:
        hero_event_image = ""
    ##-----------------------traversing through div elements to get event name and event category
    # print("after event hero")

    # print(hero_event_name.getText()) # getting the event name
    # print(hero_event_category.getText()) # getting the event category
    # print(hero_event_image["src"]) # getting the event image

    # print("before event bar")
    ##-----------------------traversing through div elements to get event start/end date, location and link to get ticket prices
    event_bar = event_page.find("div", class_="event-bar")
    bar_one = event_bar.find("div", class_="event-bar__info")
    bar_two = bar_one.find("div", class_="event-detail event-detail__date flex flex--align-items--center")
    bar_three = bar_one.find("div", class_="event-detail event-detail__venue flex flex--align-items--center")
    bar_four = event_bar.find("div", class_="event-bar__action")
    # bar_three = event_bar.find("div", class_="event-detail event-detail__venue flex flex--align-items--center")
    # bar_four = bar_three.find("div", class_="event-detail__link")
    # bar_four = bar_ond.find("div", class_="event-detail__link")
    bar_event_dates = bar_two.find("a")
    bar_event_dates_alt = bar_two.find("h3")

    start, end = extract_date_components(date_string=bar_event_dates.getText(), alt_date=bar_event_dates_alt.getText())
    bar_venue_name = bar_three.find("h3")
    bar_venue_address = bar_three.find("a")
    bar_link_to_purchase = bar_four.find("a")

    places_api_key = os.environ.get("PLACES_API")
    place_info = get_place_id(bar_venue_name.getText(), api_key=places_api_key)
    #
    if place_info is not None:
        establishment_details = {
            "id": place_info["candidates"][0]['place_id'],
            "formattedAddress": place_info["candidates"][0]['formatted_address'],
            "location": place_info["candidates"][0]['geometry']['location'],
            "displayName": place_info["candidates"][0]['name'],
            "managerAccount": 'testAddEventEndpoint'

        }


    else:
        establishment_details = None
    ##-----------------------traversing through div elements to get event start/end date and location
    # print("after event bar")

    # print("before event description")
    ##-----------------------traversing through div elements to get event descriptions
    event_carousel = event_page.find("div", class_="event-carousel")
    carousel_one = event_carousel.find("div", class_="event-section__content")
    carousel_two = event_carousel.find("div", class_="event-line-up")

    carousel_event_description = carousel_one.find_all("p")
    list_of_descriptions = [par.getText() for par in carousel_event_description]

    try:
        carousel_event_lineups = carousel_two.find_all("a")
        list_of_artists = [artist.find("div", class_="event-line-up__name").getText() for artist in carousel_event_lineups]

    except:
        # print("No Lineups")
        list_of_artists = []
        # list_of_descriptions = []
    ##-----------------------traversing through div elements to get event descriptions
    # print("after event description")

    # print("before event prices")
    ##-----------------------traversing through div elements to get event prices
    # ticket_page_request = requests.get(f"https://ag.howler.co.za/{bar_link_to_purchase["href"]}", headers=header)
    try:
        ticket_page_request = requests.get(f"https://ag.howler.co.za/{bar_link_to_purchase["href"]}")


    # print("I'm at the ticket page")

        ticket_soup = BeautifulSoup(ticket_page_request.content, "html.parser")
        # print("I'm at the ticket page soup")

        ticket_page = ticket_soup.find("div", class_="purchase-process-wrapper")
        # print("I'm at the purchase process wrapper")

        ticket_one = ticket_page.find("div", class_="ticket-selection-layout__main")
        # print("I'm at the ticket selection layout main")

        ticket_two = ticket_one.find_all("form", id="ticket_order_form")
        # print("I'm at the ticket two section of page")

        ticket_form = None

        ticket_prices = []

        for form in ticket_two:

            if form.get("action") == "/ticket_order/tickets":
                ticket_form = form

        try:
            ticket_types = ticket_form.find("div", class_="accordion-content ticket-selection__accordion-content")

            # ticket_prices = []
            ticket_status = None

            for ticket in ticket_types:

                try:
                    ticket_status = ticket.find("div", class_="ticket-info__booking-status").getText()
                except:
                    ticket_status = None


                if ticket_status is None:
                    price = ticket.find("div", class_="ticket__price").getText()
                    result = ''.join(char for char in price if char.isdigit() or char == ".") # extracting price digits from price string
                    result_formatted = int(result.split('.')[0])
                    ticket_prices.append(result_formatted)

        except:
            try:
                ticket_types = ticket_form.find_all("div", class_="ticket-selection ticket-selection--loose-ticket")
                # print(ticket_types)
                # ticket_prices = []
                ticket_status = None

                for ticket in ticket_types:

                    try:
                        ticket_status = ticket.find("div", class_="ticket-info__booking-status").getText()
                    except:
                        ticket_status = None


                    if ticket_status is None:
                        price = ticket.find("div", class_="ticket__price").getText()
                        result = ''.join(char for char in price if char.isdigit() or char == ".") # extracting price digits from price string
                        result_formatted = int(result.split('.')[0])
                        ticket_prices.append(result_formatted)

            except:
                print("Price not found")
                ticket_prices.append(-1)

            # print("Error with price element")

    except:
            ticket_prices = []
            ticket_prices.append(0)
    ##-----------------------traversing through div elements to get event prices
    # print(f"this is {start}")
    # print(f"this is {end}")
    # print(bar_event_dates.getText())
    # print(bar_event_dates_alt.getText())
    # print(extract_date_components(bar_event_dates.getText(), bar_event_dates_alt.getText()))
    # print("after event description")


    # print(start) # event start date
    # print(bar_event_dates.getText())
    # print(end) # event start date
    # print(bar_venue_name.getText()) # event venue name
    # print(bar_venue_address.getText()) # event location (1) Street number (2) Street name (3) Suburb (4) City (5) Postal code
    # print(f"https://ag.howler.co.za/{bar_link_to_purchase["href"]}") # link to purchase ticket
    # print(list_of_descriptions[0]) # full event description
    # print(list_of_artists) # top 3 artists on the lineup
    # print(ticket_prices) # returnng a list of ticket prices (that aren't sold out)

    if ticket_prices == []:
        ticket_prices.append(-1)


    try:

        event_info = {
            "ageRestriction": "18 and older",
            "artistNames": [],
            "artists": [],
            "description": list_of_descriptions[0],
            "endDate": datetime(end['year'], end['month'], end['day'], end['hour'], end['minute'],
                                tzinfo=timezone(timedelta(hours=2))),
            "genres": [],
            "managerAccount": email,
            "name": hero_event_name.getText(),
            "paymentPortal": f"https://ag.howler.co.za{bar_link_to_purchase["href"]}",
            "price": ticket_prices[0],
            "startDate": datetime(start['year'], start['month'], start['day'], start['hour'], start['minute'],
                                  tzinfo=timezone(timedelta(hours=2))),
            "venue": "",  # use this as input for google places API to get venue id
            'venueId': "",
            'whatstheplace': "",
            "eventImageUrl": hero_event_image["src"]


            # "lineup": list_of_artists,

            }

    except:

        event_info = {
            "ageRestriction": "18 and older",
            "artistNames": [],
            "artists": [],
            "description": list_of_descriptions[0],
            "endDate": datetime(end['year'], end['month'], end['day'], end['hour'], end['minute'],
                                tzinfo=timezone(timedelta(hours=2))),
            "genres": [],
            "managerAccount": email,
            "name": hero_event_name.getText(),
            "paymentPortal": f"https://ag.howler.co.za{bar_link_to_purchase["href"]}",
            "price": ticket_prices[0],
            "startDate": datetime(start['year'], start['month'], start['day'], start['hour'], start['minute'],
                                  tzinfo=timezone(timedelta(hours=2))),
            # "venue": venue_id, # use this as input for google places API to get venue id
            "venue": "",  # use this as input for google places API to get venue id
            'venueId': "",
            'whatstheplace': "",
            "eventImageUrl": ""

            # "lineup": list_of_artists,

        }
    
    # venue_info = {
    #     "venueId": venue_id,
    #     "managerAccount": email
    # }
    # venue_info = {
    #     "venueId": "",
    #     "managerAccount": email
    # }
    logging.info("Successfully retrieved howler event information")

    return event_info, establishment_details
    # return ticket_prices

# # Example usage:
# string = "https://www.howler.co.za/events/joburg-freshers-c8f6?_gl=1%2Ay510md%2A_up%2AMQ..%2A_ga%2AMTM5MjA4MjM4OC4xNzM5NzIyMDkw%2A_ga_0X69KFQ5F8%2AMTczOTcyMjA4Ny4xLjEuMTczOTcyMjE5MS4wLjAuMA..&utm_campaign=Music+Category+Page&utm_medium=Web&utm_source=Howler+Listing+Pages"
# event_info = howler_event_extractor(string,email="kgalemakhwezi0@gmail.com")
# print(event_info)
# print("Start Date Components:", start['year'])
# print("End Date Components:", end)
