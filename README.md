To get the Tessel code working, you should do the following:

1. Install the climate module that is appropriate for your board:

	```
	npm install climate-si7005
	   --- or ---
	npm install climate-si7020
	```

2. Set up  wifi: 

	```
	tessel wifi -n [network name] -p [password]
	```

Check if you are connected with:

	```
	tessel wifi -l
	```

3. Run code: 
	
	```
	tessel run gatd_climate.js
	```

4. If satisfied, load code into flash to be run automatically upon startup: 

	```
	tessel push gatd_climate.js
	```

	After pushing, you can see output when connected by USB using `tessel listen`.