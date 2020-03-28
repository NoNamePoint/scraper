import requests
import bs4
import csv


def get_html(url):
	response = requests.get(url)
	return response.text

def get_total_pages(html):
	#получаем html разметку страницы
	soup = bs4.BeautifulSoup(html, 'lxml')
	#получаем список всех страниц со ссылками
	pages = soup.find("div", class_="pagination-root-2oCjZ").find_all("span", class_="pagination-item-1WyVp")
	#узнаем количество всех страниц с объявлениями
	total_page = pages[-2].text
	return int(total_page)


def get_flats(html):
	soup = bs4.BeautifulSoup(html, 'lxml')
	flats = soup.find_all('div', class_='snippet-horizontal item item_table clearfix js-catalog-item-enum item-with-contact js-item-extended')
	return flats

def write_to_csv(data):
	with open('avito_flats.txt', 'a', encoding='utf-8') as file:
		writer = csv.writer(file)
		writer.writerow((data['name'],
						 data['metro'],
						 data['price'],
						 data['link'],
						 data['pub_date']))

def main():
	url = "https://www.avito.ru/moskva/kvartiry/sdam/na_dlitelnyy_srok/2-komnatnye-ASgBAQICAkSSA8gQ8AeQUgFAzAgUkFk?p=1"
	base_url = 'https://www.avito.ru/moskva/kvartiry/sdam/na_dlitelnyy_srok/2-komnatnye-ASgBAQICAkSSA8gQ8AeQUgFAzAgUkFk?'
	avito_main_dns = 'https://www.avito.ru'
	page_part = 'p='

	list_of_links = []
	# ссылки на все квартиры
	total_pages = get_total_pages(get_html(url))
	for i in range(1, total_pages + 1):
		url_gen = base_url + page_part + str(i)
		list_of_links.append(url_gen)
	for link in list_of_links:
		flats_bloks_html = get_html(link)
		flats_bloks = get_flats(flats_bloks_html)
		for flat_blok in flats_bloks:
			try:
				name = flat_blok.find('h3').text.replace('"', '')
			except AttributeError:
				continue
			try:
				href = flat_blok.find('h3').find('a').get('href')
				link = avito_main_dns + href
			except AttributeError:
				continue
			try:
				metro = flat_blok.find('span', class_='item-address-georeferences-item__content').text.strip()
			except AttributeError:
				continue
			try:
				price_list_components = (flat_blok.find('span', class_='snippet-price').text.strip()).split()
				price = int(price_list_components[0] + price_list_components[1])
			except AttributeError:
				continue
			try:
				publication_date = flat_blok.find('div', class_='snippet-date-info').text.strip()
			except AttributeError:
				continue
			#оторать варианты не выше 40000 тысяч рулей и в заданном диапазоне метро
			if price > 40000:
				continue
			if metro not in ["Новокосино", "Лухмановская", "Улица Дмитриевского", "Новогиреево"]:
				continue

			dict_of_params = { 'name': name,
							   'metro': metro,
							   'link': link,
							   'price': price,
							   'pub_date': publication_date
							  }
			write_to_csv(dict_of_params)
	print('Готoво')

if __name__ == "__main__":

	main()
