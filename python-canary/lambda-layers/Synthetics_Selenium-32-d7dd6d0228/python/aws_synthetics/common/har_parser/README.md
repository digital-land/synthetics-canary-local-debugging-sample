Generate HAR file with Puppeteer

This library is based on [puppeteer-har](https://github.com/Everettss/puppeteer-har).

### Usage

```
from har_parser import HarParser
from pyppeteer import launch

browser = await launch()
page = await browser.newPage()
har_region = "us-east-1"
har = HarParser(page, har_region, path="/tmp/har.html")

# start recording
await har.start_recording()
await page.goto("https://aws.amazon.com")

# stop recording
await har.stop_recording()
await browser.close()
```

### HarParser(page, region, path)
- `page` - Puppeteer page instance
- `region` - DNS region for HTML version
- `path` - Path where the har file is saved


### get_har_json()
Returns HAR as JSON

### get_har_html()
Returns HAR as HTML file 

