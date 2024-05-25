import re
import requests
from bs4 import BeautifulSoup

#Website
url = 'https://velvetwatches.com'


try:
    # Send a GET request to the website
    response = requests.get(url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all the article titles
        article_titles = soup.find_all('h2', class_='headline')

        # Print the article titles if found, otherwise print NA
        if article_titles:
            print("Article Titles:")
            for title in article_titles:
                print(title.text.strip())
        else:
            print("Article Titles: NA")

        # Section: Emails
        # Find all email addresses using regular expression
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, response.text)

        
        # Print the emails if found, otherwise print NA
        if emails:
            print("\nEmails:")
            for email in emails:
                print(email)
        else:
            print("\nEmails: NA")

            print("\nPhone Numbers: NA")

        # Section: Social Media Links
        social_media_links = []

        # Find social media links
        social_links = soup.find_all('a', href=True)
        social_patterns = [
            r'facebook.com',
            r'instagram.com',
            r'twitter.com',
            r'linkedin.com',
            r'youtube.com'
        ]

        for link in social_links:
            for pattern in social_patterns:
                if re.search(pattern, link['href'], re.IGNORECASE):
                    social_media_links.append(link['href'])
                    break

        # Print social media links if found, otherwise print NA
        if social_media_links:
            print("\nSocial Media Links:")
            for link in social_media_links:
                print(link)
        else:
            print("\nSocial Media Links: NA")

        # Section: Other Links
        # Find all the links
        other_links = [link['href'] for link in social_links if link['href'] not in social_media_links]

        # Print other links if found, otherwise print NA
        if other_links:
            print("\nOther Links:")
            for link in other_links:
                print(link)
        else:
            print("\nOther Links: NA")

    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

except Exception as e:
    print(f"An error occurred: {str(e)}")
