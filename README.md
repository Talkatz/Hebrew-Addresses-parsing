# Hebrew-Addresses-parsing
Separation of addresses from an Excel file in order to retrieve a full proper address, and add a street code to it, by using an XML file with data on all the streets in Israel

When working on customers data, to know where they live and their surroundings can produce valuable information about them. 
Many companies have addresses table in their databases, and each one may save the data differently. 

The code presented here processes an excel file with a column of the full address, and separates it with a chosen delimiter
to city and street with house number. If the address is good, it adds it into a dataFrame. In real life cases we might just
send them directly into our database.

After it does so, I've added a function that adds the street code. It does that by first reading an xml file
with data on streets (in Israel) into a dataFrame. Afterwards it compares the two dataFrames, and if it finds the street
and the city, it adds the street code to the client's addresses dataFrame. 

It can be done also for the city code, and it is better afterwards to work with the city code and then street
name in order to find a match; so if in the xml file the city name is written a little bit differently, it doesn't
matter because we use the city code which is fixed. But of course we need to have a Cities table with synonyms and city codes, and use it before in order to give the city a city code.

I've added a data file with a column of address for example. The XML file of the streets can be download from: https://data.gov.il/
