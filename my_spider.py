import re
import time
import random
import requests
from bs4 import BeautifulSoup


# list of User Agents
UA = ['Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
      # Chrome
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
      'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
      'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
      'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
      'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
      'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
      'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
      # Firefox
      'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
      'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
      'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
      'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
      'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
      'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
      'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
      'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
      'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
      'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
      'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
      'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
      'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)',
      ]
RETRY_COUNT = 5


# the main spider driver function
def the_spider(cat_urls):
    print('Starting our Spider...\n')
    products = []
    product_urls = []
    cookies = None
    for url in cat_urls:
        # getting the product URLs and cookies
        urls, cookies = get_product_urls(url)
        product_urls.extend(urls)

    print('\nProducts URLs:\n')
    [print(i) for i in product_urls]
    print('\n\nTotal products to be crawled: ', len(product_urls), '\n')

    for url in product_urls:
        result = None
        if cookies is not None:
            result = get_product_data(url[0], url[1], cookies)
        if result is not None:
            products.append(result)
        print('Products so far: ', len(products))
        print(products, '\n')

    print('Exiting the spider!')
    # returning the final list of JSON(product dictionary) objects
    return products


# crawls the category pages
def get_product_urls(cat_url):
    print('Crawling a category page...')
    user_agent = random.choice(UA)
    headers = {
        'User Agent': user_agent
    }
    response = requests.get(cat_url, headers=headers)
    cookies = response.cookies

    soup = BeautifulSoup(response.text, features='html.parser')
    products = []
    for product in soup.select('.view.grid-nosku .product .product-iWrap'):
        item_url = 'https:' + product.select_one('.productTitle > a').get('href')
        meta = {}
        monthly_sales = product.select_one('.productStatus > span > em')
        if monthly_sales:
            meta["Monthly Sales"] = monthly_sales.string
        reviews = product.select('.productStatus > span > a')
        if len(reviews):
            meta["Total Number of Reviews"] = reviews[0].string
        products.append([item_url, meta])

    # returning a list of product URLs along with data from the category page and the cookies received in the response
    return products, cookies


def get_product_data(product_url, meta, cookies):
    print('Crawling a product page...\n')
    response = None
    count = 0

    # sending requests to the product URL until a proper response is received
    while count < RETRY_COUNT:
        try:
            count += 1
            print('Attempt number: ', count, ' for ', product_url)
            # trying with a new random User Agent everytime
            user_agent = random.choice(UA)
            headers = {
                'User Agent': user_agent
            }
            response = requests.get(product_url, headers=headers, cookies=cookies)
        except Exception as e:
            print('Following exception occurred:\n', e)
            seconds = random.randrange(1, 3)
            print('Cooling for ', seconds, ' second(s)...')
            time.sleep(seconds)
            continue
        break

    if response is not None:
        soup = BeautifulSoup(response.text, features='html.parser')

        product = dict({
            "Product Link": response.url,
            "Currency": "Yen",
        })

        if 'Monthly Sales' in meta.keys():
            product["Monthly Sales"] = meta["Monthly Sales"]
        if 'Total Number of Reviews' in meta.keys():
            product["Total Number of Reviews"] = meta["Total Number of Reviews"]

        product_description = soup.select_one('.tb-detail-hd > h1')
        if product_description:
            product["Product Description"] = product_description.string.strip()

        price = re.search('defaultItemPrice":"([\d.,]+)', response.text)
        if price:
            product["Price"] = price.group(1)

        brand_name = re.search('brand":"(.*?)"', response.text)
        if brand_name:
            product["Brand Name"] = brand_name.group(1)

        product_name = [i for i in soup.select('#J_AttrUL > li') if '产品名称' in i.string]
        if len(product_name):
            product["Product Name"] = product_name[0].get('title')

        origin = [i for i in soup.select('#J_AttrUL > li') if '产地' in i.string]
        if len(origin):
            product["Origin"] = origin[0].get('title').strip()

        taste = [i for i in soup.select('#J_AttrUL > li') if '口味' in i.string]
        if len(taste):
            product["Taste"] = taste[0].get('title').strip()

        type_of_drink = [i for i in soup.select('#J_AttrUL > li') if '饮品种类' in i.string]
        if len(type_of_drink):
            product["Type of drink"] = type_of_drink[0].get('title').strip()

        sugar = [i for i in soup.select('#J_AttrUL > li') if '是否含糖' in i.string]
        if len(sugar):
            product["Whether it contains sugar"] = sugar[0].get('title').strip()

        net_content = [i for i in soup.select('#J_AttrUL > li') if '净含量' in i.string]
        if len(net_content):
            product["Net content"] = net_content[0].get('title').strip()

        product["Product Image"] = ['https:' + i.get('src').replace('//img.alicdn.com/imgextra/http', 'http').replace('60x60q90', '430x430q90') for i in soup.select('#J_UlThumb > li > a > img')]

        # returning product data in the form of a dictionary
        return product

    else:
        # giving up as the server is not responding
        print('\nTried enough!\n')
        return None


category_urls = ['https://list.tmall.com/search_product.htm?spm=a220m.1000858.1000723.1.283ac87fxoVMX5&&from=rs_1_key-top-s&q=%B9%FB%D6%AD',
                 'https://list.tmall.com/search_product.htm?spm=a220m.1000858.1000723.2.283ac87fxoVMX5&&from=rs_1_key-top-s&q=%BF%C9%C0%D6',
                 'https://list.tmall.com/search_product.htm?spm=a220m.1000858.1000723.3.283ac87fxoVMX5&&from=rs_1_key-top-s&q=%D1%A9%B1%CC',
                 'https://list.tmall.com/search_product.htm?spm=a220m.1000858.1000723.4.283ac87fxoVMX5&&from=rs_1_key-top-s&q=%B3%C8%D6%AD',
                 'https://list.tmall.com/search_product.htm?spm=a220m.1000858.1000723.5.283ac87fxoVMX5&&from=rs_1_key-top-s&q=%B1%F9%BA%EC%B2%E8',
                 'https://list.tmall.com/search_product.htm?spm=a220m.1000858.1000723.6.283ac87fxoVMX5&&from=rs_1_key-top-s&q=%B9%FB%C1%A3%B3%C8',
                 'https://list.tmall.com/search_product.htm?spm=a220m.1000858.1000723.7.283ac87fxoVMX5&&from=rs_1_key-top-s&q=%D2%AC%D6%AD',
                 'https://list.tmall.com/search_product.htm?spm=a220m.1000858.1000723.8.283ac87fxoVMX5&&from=rs_1_key-top-s&q=%B0%D9%CA%C2%BF%C9%C0%D6',
                 'https://list.tmall.com/search_product.htm?q=+%D2%FB%C1%CF&type=p&vmarket=&spm=875.7931836%2FB.a2227oh.d100&from=mallfp..pc_1_searchbutton',]

# Final list of JSON(product dictionary) objects
data = the_spider(category_urls)
