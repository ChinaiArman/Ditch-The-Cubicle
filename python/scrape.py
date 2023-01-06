# Imports
from bs4 import BeautifulSoup
import requests
import re
from csv import writer
from geopy.geocoders import Nominatim


# Initialize geolocator
geolocator = Nominatim(user_agent="my_request")

# Website information
url = "https://www.todocanada.ca/things-vancouver-weekend/"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
page = requests.get(url, headers= headers)

# Initialize Beautiful Soup
soup = BeautifulSoup(page.content, 'html.parser')
lists = soup.find_all('article')

# Open CSV to write
with open('event_data.csv', 'w', encoding='utf8', newline='') as file:
    writer = writer(file)
    header = ['Title', 'Link', 'Location', 'Cost', 'StartDate', 'EndDate', 'NumericalDate', 'Image', 'Poster', 'Description', "Preview", "Longitude", "Latitude"]
    writer.writerow(header)
    
    # Iterate over each article
    for list in lists:
        h2 = list.find('h2', class_ = "entry-title")
        if h2 != None:
            a = h2.find('a', attrs={'href': re.compile("^https://")})
            img = list.find('img', attrs={'data-lazy-src': re.compile("^https://")})

            title = h2.find('a').text
            link = a.get('href')
            image = img.get('data-lazy-src')
            location = "Not Specified"
            cost = "Not Specified"
            date = "Not Specified"
            for p in list.find_all('p', class_="address"):
                location = list.find('p', class_ = "address").text
            for p in list.find_all('p', class_="ampprice"):
                cost = list.find('p', class_ = "ampprice").text
            for p in list.find_all('p', class_="event_date"):
                date = list.find('p', class_ = "event_date").text.rstrip()


            if date != 'Not Specified':
                # Scrape each specific article
                url = link
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                page = requests.get(url, headers= headers)

                # Reinitialize Beautiful Soup
                soup = BeautifulSoup(page.content, 'html.parser')
                paragraphs = str(soup.find_all('div', class_ ="entry-content frontend-entry-content"))
                paragraphs.replace(',', '')
                paragraph_list = paragraphs.split('<p>')
                description = paragraph_list[1]
                try:
                    poster = str(soup.find_all('img', attrs={'src': re.compile("https://")})[2])
                except IndexError:
                    poster = "Not Specified"
                StartDate = soup.find('span', class_="frontend_st_date frontend_datepicker").text
                EndDate = soup.find('span', class_="frontend_end_date frontend_datepicker").text

                months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
                listdate = EndDate.split(" ")
                numericaldate = 0
                numericaldate += int(listdate[2]) * 10000 + months.get(listdate[0]) * 100 + int(listdate[1].replace(",", ""))

                # Coordinates
                geographicallocation = geolocator.geocode(location)
                if geographicallocation == None:
                    templocation = location
                    letter = True
                    while letter:
                        try: 
                            if templocation[0].isalpha() or templocation[0] == ' ' or templocation[0] == ',' or templocation[0] == '&' or templocation[0] == "'" or templocation[0] == "+" or templocation[0] == ".":
                                templocation = templocation[1:]
                            else:
                                letter = False
                                location = templocation
                        except IndexError:
                            letter = False
                geographicallocation = geolocator.geocode(location)
                print(location)
                if geographicallocation == None:
                    print("no specific address")
                    longitude = "null"
                    latitude = "null"
                    print(str(longitude) + ", " + str(latitude))
                else:
                    longitude = geographicallocation.longitude
                    latitude = geographicallocation.latitude
                    print(str(longitude) + ", " + str(latitude))
                print("---------------")
                    

                # Event Title
                title = str(title).replace(',',"")
                # Event Link
                link = str(link).replace(',',"")
                # Event Location
                location = str(location).replace(',',"")
                # Event Cost
                cost = str(cost).replace(',',"")
                # Event Start Date
                StartDate = str(StartDate).replace(',',"")
                # Event End Date
                EndDate = str(EndDate).replace(',',"")
                # Event Image
                image = str(image).replace(',',"")
                # Poster Image
                if poster == "Not Specified":
                    poster = image
                else:
                    poster = poster.replace('<img src="', '')
                    poster = poster.replace('"/>', '')
                # Description
                text = description.split('</p>')[0]
                text = text.replace('<span class=""TextRun SCXW197544240 BCX0"" data-contrast=""none"" lang=""EN-US"" xml:lang=""EN-US"">', '')
                text = text.replace('<span class=""NormalTextRun CommentStart SCXW197544240 BCX0"">', '')
                text = text.replace('</span>', '')
                text = text.replace('<span class=""NormalTextRun SCXW197544240 BCX0"">', '')
                text = text.replace('<br/>', '')
                text = text.replace(',', '')
                if 'span' in text or len(text) <= 1:
                    text = 'No Description Available'
                # Preview
                if len(text) > 80:
                    preview = text[:80] + "..."
                else:
                    preview = text

                # Write to CSV
                if date != 'Not Specified':
                    info = [title, link, location, cost, StartDate, EndDate, numericaldate, image, poster, text, preview, longitude, latitude]
                    writer.writerow(info)