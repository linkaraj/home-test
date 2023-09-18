import argparse
import json
import os
import sys

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.request import urlopen, urlretrieve

#
# WebPage class to fetch and save web pages
#
class WebPage:
    def __init__(self, url):
        self.url = url

    #
    # Fetch the web page and store the content and object
    #
    def fetch(self):
        url_with_schema = self.get_url_with_schema()
        try:
            response = urlopen(url_with_schema)
            self.web_content = response.read().decode('UTF-8')
        except:
            raise Exception("Unable to fetch URL : " + self.url)

        metadata = {}
        metadata['fetch_date'] = response.info()['date']
        self.soup = BeautifulSoup(self.web_content, 'html.parser')
        metadata['links_count'] = len(self.soup.find_all('a'))
        metadata['images_count'] = len(self.soup.find_all('img'))
        self.metadata = metadata

    #
    # Add http schema if not provided
    #
    def get_url_with_schema(self):
        return 'http://' + self.url if not urlparse(self.url).scheme else self.url

    #
    # Sanitize the URL then construct the html file name
    #
    def html_file_name(self):
        file_name_wo_ext = self.file_name_without_extension()
        return file_name_wo_ext if file_name_wo_ext.endswith('.html') else file_name_wo_ext + '.html'

    #
    # Sanitize the URL then construct the metadata file name
    #
    def metadata_file_name(self):
        return self.html_file_name() + '.metadata'

    def file_name_without_extension(self):
        file_name = self.url
        parsed = urlparse(file_name)
        if parsed.scheme:
            file_name = parsed.geturl().replace(parsed.scheme + '://', '')

        file_name = file_name.replace('/', '_')
        return file_name

    #
    # Get the last metadata information from local metadata file
    #
    def get_last_metadata(self):
        metadata_file_name = self.metadata_file_name()
        if os.path.isfile(metadata_file_name):
            with open(metadata_file_name) as metadata_file:
                return json.load(metadata_file)
        else:
            return None

    #
    # Save html file locally
    #
    def save_html(self):
        html_file_name = self.html_file_name()
        with open(html_file_name, "w") as html_file:
            html_file.write(str(self.soup))

    #
    # Save metadata file locally
    #
    def save_metadata(self):
        metadata_file_name = self.metadata_file_name()
        with open(metadata_file_name, "w") as html_file:
            html_file.write(json.dumps(self.metadata, indent=4))


    #
    # Download all images from web page
    #
    def save_all_images(self):
        folder_name = self.html_file_name() + '.folder'
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        i = 1
        for img in self.soup.find_all('img'):
            if hasattr(img, 'src'):
                image_src = img['src']
                if image_src.startswith('http'):
                    pass
                elif image_src.startswith('/'):
                    image_src = self.base_url(self.get_url_with_schema(), False) + image_src
                    print(image_src)
                else:
                    image_src = self.base_url(self.get_url_with_schema(), True) + image_src

                urlretrieve(image_src, folder_name + '/' + str(i) + '.jpg')
                img['src'] = folder_name + '/' + str(i) + '.jpg'
                i = i + 1

    def base_url(self, url, relative=False):
        parsed = urlparse(url)        
        path   = '/'.join(parsed.path.split('/')[:-1]) if relative else ''
        parsed = parsed._replace(path=path)
        parsed = parsed._replace(params='')
        parsed = parsed._replace(query='')
        parsed = parsed._replace(fragment='')
        return parsed.geturl()

def fetch_web_pages(web_urls, metadata, deep):
    for web_url in web_urls:
        web_page = WebPage(web_url)
        try:
            web_page.fetch()

            #
            # Print metadata
            #
            if metadata :
                print('#############################################################')
                print('Web URL : ' + web_url)
                print('No of links : ' + str(web_page.metadata['links_count']))
                print('No of images : ' + str(web_page.metadata['images_count']))
                print('Fetch date : ' + web_page.metadata['fetch_date'])
                last_meta_data = web_page.get_last_metadata()
                if last_meta_data:
                    print("Last fetch date : " + last_meta_data['fetch_date'])
                    print('Last fetch No of links : ' + str(last_meta_data['links_count']))
                    print('Last fetch No of images : ' + str(last_meta_data['images_count']))
                print('#############################################################')

            #
            # Save html and metadata into disk
            #
            if deep:
                try:
                    web_page.save_all_images()
                except:
                    print('Failed to save all images for URL : ' + web_url)
            web_page.save_html()
            web_page.save_metadata()
            
        except Exception as error:
            print('Unable to fetch URL : ' + web_url)

def main():
    #
    # Parse command line arguments
    #
    parser = argparse.ArgumentParser('Fetch webpages and saves them do disk')
    parser.add_argument('--metadata', default=False, action='store_true', help='Print metadata information about the web url\'s')
    parser.add_argument('--deep', default=False, action='store_true', help='Download all the images from the web url\'s')
    parser.add_argument('web_urls', metavar='WEB-URL', nargs='+', help='Collection of web url\'s to fetch')

    args = parser.parse_args()
    fetch_web_pages(args.web_urls, args.metadata, args.deep)

if __name__ == "__main__":
    rv = main()
    sys.exit(rv)