# -*- coding: utf-8 -*-
import mc
import rfc822
from datetime import datetime
from BeautifulSoup import BeautifulStoneSoup


RSS_FEED = 'http://forsvaret.no/aktuelt/publisert/forsvaret-i-dag/_layouts/listfeed.aspx?List=366E5F82-17CB-4CD0-86BA-9B4C2A750490'


def main():
	mc.ActivateWindow(14000)
	mc.ShowDialogWait()
	response_data = mc.Http().Get(RSS_FEED)
	soup = BeautifulStoneSoup(response_data)
	elems = soup.findAll('item')
	item_list = mc.ListItems()
	for i, elem in enumerate(elems):
		try:
			# Need to convert it to 'str' since SetImage doesn't support 'unicode'
			img = elem.find('enclosure')['url'].encode('utf-8')
			media = elem.find('media:content')
		except:
			# Skip posts without img
			continue
		# Since it's wrapped in CDATA we must get the contents
		# Strip the trailing dot and whitespace
		title = elem.find('title').contents[0].encode('utf-8').rstrip('. ')
		summary = elem.find('description').contents[0].replace('\n', ' ').encode('utf-8')
		pub_date = elem.find('pubdate').string
		updated = rfc822_to_datetime(pub_date)
		counter = '%s   %s/%s' % (days_ago(updated), i + 1, len(elems))
		item = mc.ListItem(mc.ListItem.MEDIA_PICTURE)
		item.SetImage(0, img)
		item.SetContentType('image/jpeg')
		item.SetLabel(title)
		item.SetDescription(summary, False)
		item.SetProperty('counter', counter)
		# Ugly workaround to scale only landscape images
		if media and is_landscape(media['width'], media['height']):
			item.SetProperty('ratio', 'scale')
		else:
			item.SetProperty('ratio', 'keep')
		item_list.append(item)
	mc.GetWindow(14000).GetList(140).SetItems(item_list)
	mc.HideDialogWait()


def is_landscape(width, height):
	return int(width) / int(height) > 0


def rfc822_to_datetime(date_string):
	utc_timestamp = rfc822.mktime_tz(rfc822.parsedate_tz(date_string))
	return datetime.fromtimestamp(utc_timestamp)


def days_ago(dt):
	now = datetime.now()
	delta = now - dt
	days = delta.days
	if days <= 0:
		return 'I dag'
	elif days == 1:
		return 'I går'
	else:
		return '%s dager siden' % days


main()