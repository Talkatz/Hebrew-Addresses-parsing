"""
@author: Tal Katz
"""
import re #regex
import openpyxl #excel
import pandas as pd
from bs4 import BeautifulSoup

#A class to hold the functions of the addresses. 
class addresses:
    #A function that gets a client excel file, and takes the relevant address column with the delimiter,
    #and passes it directly to the function that separates the address string, in order to append them
    #to a list. That list transforms into a dataFrame, but only a full valid address is added. 
    #The delimiter is between the street (with house number) and the city, and cannot be a space
    def add_newAddresses(excelPath, sheetName, addressColNumber, delimiterAddress):
        if (delimiter == ' '): #space check
            return
        records = []
        wb = openpyxl.load_workbook(excelPath)
        ws = wb.get_sheet_by_name(sheetName)
        for col_cells in ws.iter_cols(min_col=addressColNumber, max_col=addressColNumber):
            for cell in col_cells:
                current_record =  addresses.parse_address(cell.value, delimiterAddress)
                #only if the address is a full and good one, it adds it. Thus also the headers of the excel are thrown out 
                if ((current_record[0] != "") and (current_record[1] != "") and (current_record[2] != 0)):
                    records.append(current_record)
        
        records = list(set(records)) #remove duplicates records
        df = pd.DataFrame(records) #turns the list into a dataFrame
        df.columns = ['City','Street','House_number']
        df.insert(3, "Street_code", "0") #new column for the dataFrame
        return df
    
    #A function that separates the full address string into City, Street and House number;
    #by identifying the relevant information, and ignoring other parts in the string
    def parse_address(fullAddress, delimiterChar):
        city = ""
        street = ""
        houseNumber = 0
        rawAddress = str(fullAddress).strip()
        firstDelimiterIndex = rawAddress.find(delimiterChar)
        if (firstDelimiterIndex == (-1)): #if there is no delimiter, we cannot separate the city and street
            return (city, street, houseNumber) #returns no empty data
        numExistsIndex = re.search(r"\d", rawAddress) #looks for the first number and returns index
        if (numExistsIndex is None): #if there are no numbers
            return (city, street, houseNumber)
        else:
            street_and_city = rawAddress.split(delimiterChar)
            if (len(street_and_city) != 2): #if there is not only a city part and street part, return empty data
                return (city, street, houseNumber)
            numberCheck_firstParth = re.search(r'\d', street_and_city[0])
            numberCheck_secondPart = re.search(r'\d', street_and_city[1])
            #if both parth have number, we can't know which one is the city and which one is the stree
            if ((numberCheck_firstParth is not None) and (numberCheck_secondPart is not None)):
                return (city, street, houseNumber)
            elif (numberCheck_firstParth is not None):
                city = re.sub('[^א-ת ]+', "", street_and_city[1].strip()) #keep alphabets only
                subStreet = str(street_and_city[0]).strip()
            else:
                city = re.sub('[^א-ת ]+', "", street_and_city[0].strip()) #keep alphabets only
                subStreet = str(street_and_city[1]).strip()
            firstSpaceIndex = subStreet.find(" ")
            if (firstSpaceIndex == (-1)): #if street is one word only, can be a number as some of Tel Aviv streets are
                return(city, street, houseNumber)
            else:
                numStartIndex = re.search(r"\d", subStreet)#because of the strip, there is a need to check again where the number starts
                street = re.sub('[^א-ת ]+', "", subStreet[0:numStartIndex.start()].strip())
                subHouseNum = subStreet[numStartIndex.start():].strip()
                firstSpaceIndexHouse = subHouseNum.find(" ")
                if (firstSpaceIndexHouse == (-1)): #if there is only a number
                    houseNumber = re.sub("[^0-9]", "", subHouseNum) #keep numbers only
                    return (city, street, houseNumber)
                else: #if there are more letters after the first number
                    houseNumber =  re.sub("[^0-9]", "", subHouseNum[0:firstSpaceIndexHouse])
                    return (city, street, houseNumber)
    
    #A function that receives the xml file of the streets data from the government data site,
    # and turns it into a dataFrame with relevant data. The xml parsing is with BeautifulSoup library                
    def streets_xml_into_df(xml_file_path):
        with open(xml_file_path, 'r', encoding='windows-1255') as f_in:
            f_in.readline()  #skipping the header
            xml_soup = BeautifulSoup(f_in.read(), 'xml')
            streets = []
            city = xml_soup.find_all('שם_ישוב') 
            street = xml_soup.find_all('שם_רחוב')
            street_code = xml_soup.find_all('סמל_רחוב')
            for i in range(0, len(city)):
                    currentRecord = []
                    currentRecord.append(str(city[i].get_text()).strip())
                    currentRecord.append(str(street[i].get_text()).strip())
                    currentRecord.append(str(street_code[i].get_text()).strip())
                    streets.append(currentRecord)
            df = pd.DataFrame(streets)
            df.columns =['City', 'Street', 'Street_code']
            return df
    
    #A function that updates the street code column in the addresses dataFrame. It does that by checking the city
    #and street by their name in the government dataFrame, and if it exists over there, it takes the
    #value of the street code and updates the row with it.
    def update_street_code(addresses_df, gov_streets_df):
        for index, row in addresses_df.iterrows():
            current_city = row['City']
            current_street = row['Street']
            result = gov_streets_df.loc[(gov_streets_df['City'] == current_city) & (gov_streets_df['Street'] == current_street)]
            if not result.empty:
                current_streetCode = result.iloc[0]['Street_code']
                addresses_df['Street_code'][index] = current_streetCode


#Example of using the functions
                
delimiter = "," #cannot be a space since some cities and streets are two words or more
exelPath = "excel file path"
addressesDf = addresses.add_newAddresses(exelPath, "Sheet1", 2, delimiter)

#The xml file was download from the Israeli goverment data site: data.gov.il
#It contains all the streets in Israel: https://data.gov.il/dataset/321/resource/9ad3862c-8391-4b2f-84a4-2d4c68625f4b
xmlPath = "xml file path"
streetsGovDf = addresses.streets_xml_into_df(xmlPath)

#if the dataFrame that was made from the client's file is good, then there is an update
if (addressesDf is not None):
    addresses.update_street_code(addressesDf, streetsGovDf)

print(addressesDf.head())

#examples of the parse_address function
print(addresses.parse_address("רוטשילד, ראשון לציון", delimiter))
print(addresses.parse_address("רוטשילד 112 תעודת דואר 11132, ראשון-לציון", delimiter))
print(addresses.parse_address("רוטשילד 5, ראשון לציון", delimiter))
print(addresses.parse_address("ראשון לציון, רוטשילד 5", delimiter))