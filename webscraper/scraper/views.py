from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from .forms import ScrapeForm
from .models import ScrapedResult
from textblob import TextBlob
from urllib.parse import urljoin
import re
from collections import Counter

def scrape_view(request):
    data = {}
    error = None

    if request.method == 'POST':
        form = ScrapeForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract data
                title = soup.title.string.strip() if soup.title else 'No title found'

                links = [link['href'] for link in soup.find_all('a', href=True)]
                images = [urljoin(url, img['src']) for img in soup.find_all('img', src=True)]

                meta_desc = soup.find('meta', attrs={'name': 'description'})
                meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
                description = meta_desc['content'] if meta_desc else 'No description'
                keywords = meta_keywords['content'] if meta_keywords else 'No keywords'

                # Enhanced Sentiment Analysis
                content = soup.get_text()
                blob = TextBlob(content)
                polarity = blob.sentiment.polarity

                if polarity >= 0.6:
                    sentiment = "Very Positive 😊"
                elif polarity >= 0.2:
                    sentiment = "Positive 🙂"
                elif polarity > -0.2:
                    sentiment = "Neutral 😐"
                elif polarity > -0.6:
                    sentiment = "Negative 🙁"
                else:
                    sentiment = "Very Negative 😠"

                # Basic keyword extraction from content
                words = re.findall(r'\b\w{5,}\b', content.lower())  # words with 5+ letters
                common_words = Counter(words).most_common(10)
                keywords_ai = [word for word, _ in common_words]


                # Save to database (sentiment not stored yet)
                ScrapedResult.objects.create(
                    url=url,
                    title=title,
                    meta_description=description,
                    meta_keywords=keywords,
                    links=",".join(links),
                    images=",".join(images)
                )

                # Pass to template
                data = {
                    'title': title,
                    'links': links,
                    'images': images,
                    'meta_description': description,
                    'meta_keywords': keywords,
                    'sentiment': sentiment,
                    'polarity_score': polarity,
                    'keywords_ai': keywords_ai,
                }

            except Exception as e:
                error = f"Error: {e}"
    else:
        form = ScrapeForm()

    return render(request, 'scraper/scrape.html', {'form': form, 'data': data, 'error': error})
