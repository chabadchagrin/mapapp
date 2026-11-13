# Source inspection 2

## Links on realestate.geauga.oh.gov

- Map -> https://gcgis-apps.geauga.oh.gov/vertigisstudio/web/?app=6b75443a4f54426e8f91d4c07a44ca13
- NEW - Advanced Search Tool -> https://gcgis-apps.geauga.oh.gov/AdvancedSearch/advsearch.aspx
- 2024 Parcel Transfers -> https://realestate.geauga.oh.gov/api/Document/2024%20Complete%20Transfer%20Report.xlsx
- 2025 Parcel Transfers -> https://realestate.geauga.oh.gov/api/Document/2025%20Complete%20Transfer%20Report.xlsx
- Real Estate &amp; GIS Data Downloads -> https://realestate.geauga.oh.gov/
- Geauga County GIS - Data and Maps -> https://geauga-county-hub-geauga.hub.arcgis.com/search
- GIS Extract (Updated Daily) -> https://realestate.geauga.oh.gov/api/Document/GISExtract.zip
- Public Records Extract (Updated Daily) -> https://realestate.geauga.oh.gov/api/Document/PublicRecordsExtract.zip
- State of Ohio Parcel Viewer -> https://geohio.maps.arcgis.com/apps/instant/sidebar/index.html?appid=ca7fb8ae3c6f420890a6ebf6d4bd1468
- State of Ohio Rest Service Endpoints -> https://das.ohio.gov/technology-and-strategy/ogrip/data_services/rest_service_endpoints
- OGRIP Data Downloads -> https://gis1.oit.ohio.gov/geodatadownload/
- GIS Activities -> https://realestate.geauga.oh.gov/
- What is GIS? -> https://www.esri.com/en-us/what-is-gis/overview
- The History of GIS -> https://realestate.geauga.oh.gov/api/Document/History%20of%20GIS.pdf
- GCGIS HUB Site -> https://geauga-county-hub-geauga.hub.arcgis.com/
- Geauga County GIS Day 2026 -> https://storymaps.arcgis.com/stories/4a6163e0411d4d378e530de645441755
- gis@co.geauga.oh.us -> mailto:gis@co.geauga.oh.us
- Realink 2.0 GIS Mapping -> https://gcgis-apps.geauga.oh.gov/vertigisstudio/web/?app=6b75443a4f54426e8f91d4c07a44ca13
- Advanced Search -> https://gcgis-apps.geauga.oh.gov/AdvancedSearch/advsearch.aspx
- Board of Elections - Voting Precincts -> https://experience.arcgis.com/experience/ec316b758a2249dc80c5b29cb11ef07e
- Interactive Great Geauga County Fair App -> https://experience.arcgis.com/experience/d8c9d3b30f244bd0ba0a3e9ee6126ca3/page/Home?views=View
- Geauga County GIS HUB Site -> https://geauga-county-hub-geauga.hub.arcgis.com/
- GCE Historic Tax Maps -> https://gce-tax-map-research-geauga.hub.arcgis.com/

## Monthly parcel shapefile: None

## Geauga hub search
- 2006 - 2010 Parcel History | Map Service | https://gcgis.geauga.oh.gov/arcgis/rest/services/2010_2006/FeatureServer | id=0fe123b15b684b8680de25bb468afbcf
- 2021 - 2025 Parcel History | Map Service | https://gcgis.geauga.oh.gov/arcgis/rest/services/2025___2021/FeatureServer | id=6dd8b1993b214f8b9059d9be54127bfe
- 1998 - 2000 Parcel History | Map Service | https://gcgis.geauga.oh.gov/arcgis/rest/services/2000_1998/FeatureServer | id=d5f26fa24b2e438c9cf3cf45546b415a
- 2001 - 2005 Parcel History | Map Service | https://gcgis.geauga.oh.gov/arcgis/rest/services/2005_2001/FeatureServer | id=c50c5ce7aa4d403a9b10beea46b30ca5
- 2016 - 2020 Parcel History | Map Service | https://gcgis.geauga.oh.gov/arcgis/rest/services/2020_2016/FeatureServer | id=caba0ffd671d419c995be52c68a29259
- 2011 - 2015 Parcel History | Map Service | https://gcgis.geauga.oh.gov/arcgis/rest/services/2015_2011/FeatureServer | id=143fe5d74b034e62b368379f18a66b13
- 2026 - 2030 Parcel History | Map Service | https://gcgis.geauga.oh.gov/arcgis/rest/services/2030___2026/FeatureServer | id=60ef3fcf465042638714bcc5832021fc
- Tax Parcel Viewer Web Experience | Web Experience | https://experience.arcgis.com/experience/9eeb60de3b524a1595e822e1c4f28c91 | id=9eeb60de3b524a1595e822e1c4f28c91
- Parcels | Feature Service | https://gcgis.geauga.oh.gov/parcel/rest/services/AzureParcels/Parcels/FeatureServer/0 | id=c50ead8d7ba5432094888bac90093c13
- Geauga County Public Notification Application | Web Mapping Application | https://geauga.maps.arcgis.com/apps/instant/notification/index.html?appid=1fabef3aeeb04bfb925da21481cdf005 | id=1fabef3aeeb04bfb925da21481cdf005
- Polling Locations 2026 | Feature Service | https://gcgis.geauga.oh.gov/arcgis/rest/services/PollingLocations/FeatureServer/0 | id=90991b6328734f679224bc35d769f7fe

## GIS Extract spreadsheet

### File Layout.xlsx

sheet 'Sheet 1' header: ('File Name', 'Field Name', 'Field Type', 'Description')
   ('Parcel_GIS', 'Extract_ID', 'bigint', 'The unique identifier of the extract')
   ('Parcel_GIS', 'Property_ID', 'int', 'The unique identifier for the parcel')

### Parcel GIS.xlsx

sheet 'Sheet 1' header: ('Extract ID', 'Property ID', 'Parcel Number', 'Parcel Number U', 'Tax Year', 'District Code', 'District Name', 'District', 'Land Use Code', 'Land Use Name', 'Land Use', 'Class', 'School District', 'Acres', 'Listed Name', 'Deed Volume', 'Deed Page', 'Date Conveyed', 'Consideration', 'Valid Sale', 'Appraised Land 100', 'Appraised Improvement 100', 'Appraised Total 100', 'Taxable Land 100', 'Taxable Improvement 100', 'Taxable Total 100', 'Has CAUV', 'Has Exemption', 'Has Abatement', 'Current Tax', 'Prior Tax', 'Paid', 'Has Contract', 'Legal Description', 'Location Address', 'Location City State Zip', 'Owner Contact Name', 'Owner Contact Address', 'Owner Contact City', 'Owner Contact State', 'Owner Contact ZipCode', 'Owner Contact Country', 'Taxpayer Contact Name', 'Taxpayer Contact Address', 'Taxpayer Contact City', 'Taxpayer Contact State', 'Taxpayer Contact ZipCode', 'Taxpayer Contact Country', 'Neighborhood Code', 'Neighborhood Name', 'Neighborhood', 'Auditor Link', 'Treasurer Link')
   (1943, 1, '01-000050', '01000050', 2025, 1, 'AUBURN TWP-KENSTON LSD', '01-AUBURN TWP-KENSTON LSD', 499, 'OTHER COMMERCIAL STRUCTURES', '499-OTHER COMMERCIAL STRUCTURES', 'Commercial', '2804 - KENSTON LSD', 4.82, 'RYLYND PROPERTIES LLC', 1282, 824, '2/25/2000 12:00:00 AM', 210000, 'False', 154280, 159600, 313880, 154280, 159600, 313880, 'NO', 'NO', 'NO', 7946.66, 0, 7946.66, 'NO', 'SEC 1 TR 2', '9809 WASHINGTON ST', 'AUBURN TOWNSHIP OH 44023', 'RYLYND PROPERTIES LLC', 'PO BOX 23007', 'CHAGRIN FALLS', 'OH', 44023, '', 'RYLYND PROPERTIES LLC', 'PO BOX 23007', 'CHAGRIN FALLS', 'OH', 44023, '', 22000, 'BAINBRIDGE/AUBURN', '22000-BAINBRIDGE/AUBURN', 'https://realestate.geauga.oh.gov/RealEstate/Summary?Property_ID=1', '')
   (1943, 7, '01-000100', '01000100', 2025, 1, 'AUBURN TWP-KENSTON LSD', '01-AUBURN TWP-KENSTON LSD', 511, 'SINGLE FAMILY DWELLING - UNPLATTED 0 - 9.99 ACRES', '511-SINGLE FAMILY DWELLING - UNPLATTED 0 - 9.99 ACRES', 'Residential', '2804 - KENSTON LSD', 2, 'LARUE ANNE M TRUSTEE', 2045, 1140, '12/28/2017 12:00:00 AM', 0, 'False', 56900, 81400, 138300, 56900, 81400, 138300, 'NO', 'NO', 'NO', 2386.02, 0, 2386.02, 'NO', 'LOT 3 SEC 2 TR 2', '10114 WASHINGTON ST', 'AUBURN TOWNSHIP OH 44023', 'LARUE ANNE M TRUSTEE', '11749 WASHINGTON ST', 'AUBURN TWP', 'OH', 44023, '', 'LARUE ANNE M TRUSTEE', '11749 WASHINGTON ST', 'AUBURN TWP', 'OH', 44023, '', 22000, 'BAINBRIDGE/AUBURN', '22000-BAINBRIDGE/AUBURN', 'https://realestate.geauga.oh.gov/RealEstate/Summary?Property_ID=7', '')
   (1943, 3737, '01-109800', '01109800', 2025, 1, 'AUBURN TWP-KENSTON LSD', '01-AUBURN TWP-KENSTON LSD', 511, 'SINGLE FAMILY DWELLING - UNPLATTED 0 - 9.99 ACRES', '511-SINGLE FAMILY DWELLING - UNPLATTED 0 - 9.99 ACRES', 'Residential', '2804 - KENSTON LSD', 4.06, 'DAVIS GREGORY E', 1757, 2335, '3/22/2005 12:00:00 AM', 245000, 'False', 57900, 229400, 287300, 57900, 229400, 287300, 'NO', 'NO', 'NO', 4367.78, 0, 19689.18, 'NO', 'LOT 65 TR 3', '19120 FOX RD', 'AUBURN TOWNSHIP OH 44023', 'DAVIS GREGORY E', '11935 WASHINGTON ST', 'CHAGRIN FALLS', 'OH', 44023, '', 'DAVIS GREGORY E', '11935 WASHINGTON ST', 'CHAGRIN FALLS', 'OH', 44023, '', 22000, 'BAINBRIDGE/AUBURN', '22000-BAINBRIDGE/AUBURN', 'https://realestate.geauga.oh.gov/RealEstate/Summary?Property_ID=3737', '')
   (1943, 12942, '02-065110', '02065110', 2025, 2, 'BAINBRIDGE TWP-KENSTON LSD', '02-BAINBRIDGE TWP-KENSTON LSD', 511, 'SINGLE FAMILY DWELLING - UNPLATTED 0 - 9.99 ACRES', '511-SINGLE FAMILY DWELLING - UNPLATTED 0 - 9.99 ACRES', 'Residential', '2804 - KENSTON LSD', 5, 'KANAGARAJ GLADYS TOD & GLADYS LEELA TOD', 2190, 202, '9/5/2024 12:00:00 AM', 0, 'False', 114100, 195000, 309100, 114100, 195000, 309100, 'NO', 'NO', 'NO', 5292.18, 0, 5292.18, 'NO', 'LOT 4 TR 3', '9640 CRACKEL RD', 'AURORA OH 44202', 'KANAGARAJ GLADYS LEELA', '9640 CRACKEL RD', 'AURORA', 'OH', 44202, '', 'KANAGARAJ GLADYS LEELA', '9640 CRACKEL RD', 'AURORA', 'OH', 44202, '', 22000, 'BAINBRIDGE/AUBURN', '22000-BAINBRIDGE/AUBURN', 'https://realestate.geauga.oh.gov/RealEstate/Summary?Property_ID=12942', '')
   (1943, 44061, '11-019200', '11019200', 2025, 11, 'CHESTER TWP-WEST GEAUGA LSD', '11-CHESTER TWP-WEST GEAUGA LSD', 510, 'SINGLE FAMILY DWELLING', '510-SINGLE FAMILY DWELLING', 'Residential', '2807 - WEST GEAUGA LSD', 1.4, 'DEMARCO GODFREY L TOD & HENRIETTE TOD', 2071, 1993, '5/24/2019 12:00:00 AM', 159900, 'True', 60100, 207400, 267500, 60100, 207400, 267500, 'NO', 'NO', 'NO', 4008.92, 0, 4008.92, 'NO', 'S/L 43\nCHESTERLAND HILLS SUB', '12953 KENYON DR', 'CHESTERLAND OH 44026', 'DEMARCO GODFREY L & HENRIETTE', '12953 KENYON DR', 'CHESTERLAND', 'OH', 44026, 'USA', 'DEMARCO GODFREY L & HENRIETTE', '12953 KENYON DR', 'CHESTERLAND', 'OH', 44026, 'USA', 20004, 'CHESTER SUBS 1', '20004-CHESTER SUBS 1', 'https://realestate.geauga.oh.gov/RealEstate/Summary?Property_ID=44061', '')
   (1943, 28990, '21-001850', '21001850', 2025, 21, 'MUNSON TWP-CHARDON LSD', '21-MUNSON TWP-CHARDON LSD', 442, 'MEDICAL CLINICS AND OFFICES', '442-MEDICAL CLINICS AND OFFICES', 'Commercial', '2803 - CHARDON LSD', 12.67, 'DI BLASIO JOSEPH A & SUSAN A', 853, 1342, '6/25/1990 12:00:00 AM', 115000, 'False', 375600, 1994900, 2370500, 375600, 1994900, 2370500, 'NO', 'NO', 'NO', 58810.06, 0, 58810.06, 'NO', 'PARCEL A\nHEAD OF THE MEADOW SUB', '13170 RAVENNA RD', 'CHARDON OH 44024', 'DI BLASIO JOSEPH A & SUSAN A', '8315 BELLE VERNON DR', 'NOVELTY', 'OH', 44072, 'USA', 'DI BLASIO JOSEPH A DI BLASIO SUSAN A', '8315 BELLE VERNON DR', 'NOVELTY', 'OH', 44072, 'USA', 20100, 'MUNSON', '20100-MUNSON', 'https://realestate.geauga.oh.gov/RealEstate/Summary?Property_ID=28990', '')
   (1943, 8282, '27-000100', '27000100', 2025, 27, 'HUNTING VALLEY VILL-WEST GEAUGA LSD', '27-HUNTING VALLEY VILL-WEST GEAUGA LSD', 599, 'OTHER RESIDENTIAL STRUCTURES', '599-OTHER RESIDENTIAL STRUCTURES', 'Residential', '2807 - WEST GEAUGA LSD', 5.16, 'RRF ANNEX LLC', 2152, 269, '5/19/2022 12:00:00 AM', 300000, 'False', 236640, 14800, 251440, 236640, 14800, 251440, 'NO', 'NO', 'NO', 3987.06, 0, 3987.06, 'NO', 'LOT 5 SEC 11 TR 1', '14760 COUNTY LINE RD', 'CHAGRIN FALLS OH 44022', 'RRF ANNEX LLC', 'C/O JOHN F BURKE\n55 PUBLIC SQUARE, 21ST FLOOR', 'CLEVELAND', 'OH', 44113, 'USA', 'RRF ANNEX LLC', 'C/O JOHN F BURKE\n55 PUBLIC SQUARE, 21ST FLOOR', 'CLEVELAND', 'OH', 44113, 'USA', 30900, 'HUNTING VALLEY VILLAGE', '30900-HUNTING VALLEY VILLAGE', 'https://realestate.geauga.oh.gov/RealEstate/Summary?Property_ID=8282', '')

## Public Records Extract tables

### File Layout.xlsx
sheet 'Sheet 1': 1634 rows
   ('Parcel', 'Extract_ID', 'bigint', 'The unique identifier of the extract')
   ('Parcel', 'Property_ID', 'int', 'The unique identifier for the parcel')
   ('Parcel', 'Parcel_Number', 'nvarchar', 'The parcel number')
   ('Parcel', 'Parcel_Number_U', 'nvarchar', 'The unformatted parcel number')
   ('Parcel', 'Tax_Year', 'smallint', 'The tax year for the parcel')
   ('Parcel', 'District_Code', 'nvarchar', 'The district code of the parcel')
   ('Parcel', 'District', 'nvarchar', 'The district of the parcel')
   ('Parcel', 'Acres', 'decimal', 'The deeded acres')
   ('Parcel', 'Legal_Description', 'nvarchar', 'The legal description')
   ('Parcel', 'Deeded_Name', 'nvarchar', 'The name as listed on the deed')
   ('Parcel', 'Listed_Name', 'nvarchar', 'The shortened owner name')
   ('Parcel', 'Owner_Contact_Name', 'nvarchar', 'Owner Contact Name')
   ('Parcel', 'Owner_Contact_Address', 'nvarchar', 'Owner Contact Address')
   ('Parcel', 'Owner_Contact_City', 'nvarchar', 'Owner Contact City')
   ('Parcel', 'Owner_Contact_State', 'nvarchar', 'Owner Contact State')
   ('Parcel', 'Owner_Contact_ZipCode', 'nvarchar', 'Owner Contact ZIP Code')
   ('Parcel', 'Owner_Contact_Country', 'nvarchar', 'Owner Contact Country')
   ('Parcel', 'School_District', 'nvarchar', 'The school district of the parcel')
   ('Parcel', 'Subdivision', 'nvarchar', 'The subdivision of the parcel')
   ('Parcel', 'Map_Number', 'nvarchar', 'The map number')
   ('Parcel', 'Map_Link', 'nvarchar', 'A link to the map information provided by a third party. (If Available)')
   ('Parcel', 'Route_Number', 'nvarchar', 'The route number')
   ('Parcel', 'Taxpayer_Contact_Name', 'nvarchar', 'Taxpayer Contact Name')
   ('Parcel', 'Taxpayer_Contact_Address', 'nvarchar', 'Taxpayer Contact Address')
   ('Parcel', 'Taxpayer_Contact_City', 'nvarchar', 'Taxpayer Contact City')
   ('Parcel', 'Taxpayer_Contact_State', 'nvarchar', 'Taxpayer Contact State')
   ('Parcel', 'Taxpayer_Contact_ZipCode', 'nvarchar', 'Taxpayer Contact ZIP Code')
   ('Parcel', 'Taxpayer_Contact_Country', 'nvarchar', 'Taxpayer Contact Country')
   ('Parcel', 'Account_ID', 'int', 'Used by ISSG')
   ('Parcel', 'Account_Number', 'nvarchar', 'The parcel account number')
   ('Parcel', 'Account_Number_U', 'nvarchar', 'The parcel unformatted account number ')
   ('Parcel', 'Has_Escrow', 'nvarchar', "Y/N indicates whether the property is on treasurer's escrow")
   ('Parcel', 'Escrow_ID', 'int', 'Used by ISSG')
   ('Parcel', 'Escrow_Number', 'nvarchar', 'The escrow account number associated with the parcel')
   ('Parcel', 'Escrow_Number_U', 'nvarchar', 'The unformatted escrow account number associated with the parcel')
   ('Parcel', 'Escrow_Amount', 'decimal', 'The amount in the escrow account associated with the parcel')
   ('Parcel', 'Has_Contract', 'nvarchar', 'Y/N indicates whether the property has an active contract')
   ('Parcel', 'Contract_ID', 'int', 'Used by ISSG')
   ('Parcel', 'Contract_Number', 'nvarchar', 'The contract account number')
   ('Parcel', 'Contract_Number_U', 'nvarchar', 'The unformatted contract account number')
   ('Parcel', 'Contract_Amount', 'decimal', 'The principal left on the contract account')
   ('Parcel', 'Contract_Installment', 'decimal', 'The installment amount of the contract account')
   ('Parcel', 'CD_Year', 'varchar', 'The certified delinquent year')
   ('Parcel', 'Retired', 'nvarchar', "An indicator of a parcel's retired status")
   ('Parcel', 'Has_Foreclosure', 'nvarchar', 'Y/N indicates whether the property is in foreclosure')
   ('Parcel', 'Has_County_Foreclosure', 'nvarchar', 'Y/N indicates whether the property is in county foreclosure')
   ('Parcel', 'Has_Sheriff_Sale', 'nvarchar', 'Y/N indicates whether the property is in sheriff sale')
   ('Parcel', 'Has_Bankruptcy', 'nvarchar', 'Y/N indicates whether the property is in bankruptcy')
   ('Parcel', 'CAUV_Savings_Year_1', 'decimal', 'CAUV Savings 1st Year')
   ('Parcel', 'CAUV_Savings_Year_2', 'decimal', 'CAUV Savings 2nd Year')
   ('Parcel', 'CAUV_Savings_Year_3', 'decimal', 'CAUV Savings 3rd Year')
   ('Parcel', 'Lender', 'nvarchar', 'The lender for the parcel')
   ('Parcel', 'Lender_Code', 'nvarchar', 'The code for the lender for the parcel')
   ('Parcel', 'Retire_Date', 'datetime2', 'The date the parcel was retired')
   ('ManufacturedHome', 'Owner_Contact_Name', 'nvarchar', 'Owner Contact Name')
   ('ManufacturedHome', 'Owner_Contact_Address', 'nvarchar', 'Owner Contact Address')
   ('ManufacturedHome', 'Owner_Contact_City', 'nvarchar', 'Owner Contact City')
   ('ManufacturedHome', 'Owner_Contact_State', 'nvarchar', 'Owner Contact State')
   ('ManufacturedHome', 'Owner_Contact_ZipCode', 'nvarchar', 'Owner Contact ZIP Code')
   ('ManufacturedHome', 'Owner_Contact_Country', 'nvarchar', 'Owner Contact Country')
   ('ManufacturedHome_Appraisal', 'Has_Owner_Occupancy', 'varchar', 'Indicates an active owner occupancy application for the year')
   ('ManufacturedHome_Delinquent_List', 'Owner_Name', 'varchar', 'The manufactured home owner name')
   ('ManufacturedHome_Location', 'Extract_ID', 'bigint', 'The unique identifier of the extract')
   ('ManufacturedHome_Location', 'Property_ID', 'int', 'The unique identifier for the Manufactured Home')
   ('ManufacturedHome_Location', 'Registration_Number', 'varchar', 'Registration Number')
   ('ManufacturedHome_Location', 'Registration_Number_U', 'varchar', 'The unformatted Registration Number')
   ('ManufacturedHome_Location', 'Tax_Year', 'smallint', 'The tax year for the manufactured home')
   ('ManufacturedHome_Location', 'Principal', 'varchar', 'An indicator for the default location address')
   ('ManufacturedHome_Location', 'Number', 'varchar', 'The street number')
   ('ManufacturedHome_Location', 'Number_N', 'int', 'The street number (integer portion)')
   ('ManufacturedHome_Location', 'Number_C', 'varchar', 'The street number (alpha portion)')
   ('ManufacturedHome_Location', 'PreDirection', 'varchar', 'The street pre-direction')
   ('ManufacturedHome_Location', 'Street', 'varchar', 'The street name')
   ('ManufacturedHome_Location', 'StreetSuffix', 'varchar', 'The street suffix')
   ('ManufacturedHome_Location', 'PostDirection', 'varchar', 'The street post-direction')
   ('ManufacturedHome_Location', 'UnitDesignator', 'varchar', 'The unit designator')
   ('ManufacturedHome_Location', 'Unit', 'varchar', 'The unit number')
   ('ManufacturedHome_Location', 'City', 'varchar', 'The city')
   ('ManufacturedHome_Location', 'State', 'varchar', 'The state')
   ('ManufacturedHome_Location', 'ZipCode', 'varchar', 'The postal code')
   ('ManufacturedHome_Owner', 'Extract_ID', 'bigint', 'The unique identifier of the extract')
   ('ManufacturedHome_Owner', 'Property_ID', 'int', 'The unique identifier for the Manufactured Home')
   ('ManufacturedHome_Owner', 'Registration_Number', 'varchar', 'Registration Number')
   ('ManufacturedHome_Owner', 'Registration_Number_U', 'varchar', 'The unformatted Registration Number')
   ('ManufacturedHome_Owner', 'Tax_Year', 'smallint', 'The tax year for the manufactured home')
   ('ManufacturedHome_Owner', 'Title', 'varchar', 'The name title')
   ('ManufacturedHome_Owner', 'First', 'varchar', 'The first name')
   ('ManufacturedHome_Owner', 'Middle', 'varchar', 'The middle name')
   ('ManufacturedHome_Owner', 'Last', 'varchar', 'The last name')
   ('ManufacturedHome_Owner', 'Suffix', 'varchar', 'The name suffix')
   ('ManufacturedHome_Owner', 'Dividend', 'smallint', 'The dividend of owner interest')
   ('ManufacturedHome_Owner', 'Divisor', 'smallint', 'The divisor of owner interest')
   ('ManufacturedHome_Transfer', 'Extract_ID', 'bigint', 'The unique identifier of the extract')
   ('ManufacturedHome_Transfer', 'Property_ID', 'int', 'The unique identifier for the Manufactured Home')
   ('ManufacturedHome_Transfer', 'Registration_Number', 'varchar', 'Registration Number')
   ('ManufacturedHome_Transfer', 'Registration_Number_U', 'varchar', 'The unformatted Registration Number')
   ('ManufacturedHome_Transfer', 'Tax_Year', 'smallint', 'The tax year for the manufactured home')
   ('ManufacturedHome_Transfer', 'Conveyance_Number', 'varchar', 'The conveyance number')
   ('ManufacturedHome_Transfer', 'Date_Conveyed', 'datetime2', 'The date of the transfer')
   ('ManufacturedHome_Transfer', 'Number_Of_Registrations', 'smallint', 'The number of registrations on the transfer')
   ('ManufacturedHome_Transfer', 'Consideration', 'decimal', 'The sales amount of the transfer')
   ('ManufacturedHome_Transfer', 'Instrument', 'varchar', 'The instrument name')
   ('ManufacturedHome_Transfer', 'Exempt_Code', 'varchar', 'The exempt code of the transfer')
   ('ManufacturedHome_Transfer', 'Deeded_Name', 'varchar', "The buyer's deeded name")
   ('ManufacturedHome_Transfer', 'Listed_Name', 'varchar', "The buyer's listed name")
   ('ManufacturedHome_Transfer', 'Owner_Contact_Name', 'nvarchar', "The buyer's owner contact name")
   ('ManufacturedHome_Transfer', 'Owner_Contact_Address', 'nvarchar', "The buyer's owner contact address")
   ('ManufacturedHome_Transfer', 'Owner_Contact_City', 'nvarchar', "The buyer's owner contact city")
   ('ManufacturedHome_Transfer', 'Owner_Contact_State', 'nvarchar', "The buyer's owner contact state")
   ('ManufacturedHome_Transfer', 'Owner_Contact_ZipCode', 'nvarchar', "The buyer's owner contact ZIP code")
   ('ManufacturedHome_Transfer', 'Owner_Contact_Country', 'nvarchar', "The buyer's owner contact country")
   ('ManufacturedHome_Transfer', 'Valid_Sale', 'varchar', 'An indicator of the validity of the sale')
   ('ManufacturedHome_Transfer', 'Sequence', 'int', 'The order of the transfers for a manufactured home')
   ('ManufacturedHome_Transfer', 'Seller_Deeded_Name', 'nvarchar', "The seller's deeded name")
   ('ManufacturedHome_Transfer', 'Seller_Listed_Name', 'nvarchar', "The seller's listed name")
   ('ManufacturedHome_Transfer', 'Seller_Owner_Contact_Name', 'nvarchar', "The seller's owner contact name")
   ('ManufacturedHome_Transfer', 'Seller_Owner_Contact_Address', 'nvarchar', "The seller's owner contact address")
   ('ManufacturedHome_Transfer', 'Seller_Owner_Contact_City', 'nvarchar', "The seller's owner contact city")
   ('ManufacturedHome_Transfer', 'Seller_Owner_Contact_State', 'nvarchar', "The seller's owner contact state")
   ('ManufacturedHome_Transfer', 'Seller_Owner_Contact_ZipCode', 'nvarchar', "The seller's owner contact ZIP code")
   ('ManufacturedHome_Transfer', 'Seller_Owner_Contact_Country', 'nvarchar', "The seller's owner contact country")
   ('ManufacturedHome_Transfer', 'Conveyance_ID', 'int', 'The unique identifier of the conveyance')
   ('OilGas', 'Owner_Contact_Name', 'nvarchar', 'Owner Contact Name')
   ('OilGas', 'Owner_Contact_Address', 'nvarchar', 'Owner Contact Address')
   ('OilGas', 'Owner_Contact_City', 'nvarchar', 'Owner Contact City')
   ('OilGas', 'Owner_Contact_State', 'nvarchar', 'Owner Contact State')
   ('OilGas', 'Owner_Contact_ZipCode', 'nvarchar', 'Owner Contact ZIP Code')
   ('OilGas', 'Owner_Contact_Country', 'nvarchar', 'Owner Contact Country')
   ('OilGas', 'Owner_Number', 'nvarchar', 'Owner Number')
   ('OilGas', 'Owner_Number_U', 'nvarchar', 'Owner Number Unformatted')
   ('OilGas_Delinquent_List', 'Owner_Name', 'varchar', 'The name of the oil and gas company')
   ('OilGas_Delinquent_List', 'Owner_Number', 'nvarchar', 'Owner Number')
   ('OilGas_Delinquent_List', 'Owner_Number_U', 'nvarchar', 'Owner Number Unformatted')
   ('OilGas_Distribution', 'Owner_Number', 'nvarchar', 'Owner Number')
   ('OilGas_Distribution', 'Owner_Number_U', 'nvarchar', 'Owner Number Unformatted')
   ('OilGas_Filing', 'Owner_Number', 'nvarchar', 'Owner Number')
   ('OilGas_Filing', 'Owner_Number_U', 'nvarchar', 'Owner Number Unformatted')
   ('OilGas_Filing_District', 'Owner_Number', 'nvarchar', 'Owner Number')
   ('OilGas_Filing_District', 'Owner_Number_U', 'nvarchar', 'Owner Number Unformatted')
   ('OilGas_Payment', 'Owner_Number', 'nvarchar', 'Owner Number')
   ('OilGas_Payment', 'Owner_Number_U', 'nvarchar', 'Owner Number Unformatted')
   ('OilGas_Tax', 'Owner_Number', 'nvarchar', 'Owner Number')
   ('OilGas_Tax', 'Owner_Number_U', 'nvarchar', 'Owner Number Unformatted')
   ('OilGas_Value', 'Owner_Number', 'nvarchar', 'Owner Number')
   ('OilGas_Value', 'Owner_Number_U', 'nvarchar', 'Owner Number Unformatted')
   ('Parcel', 'Extract_ID', 'bigint', 'The unique identifier of the extract')
   ('Parcel', 'Property_ID', 'int', 'The unique identifier for the parcel')
   ('Parcel', 'Parcel_Number', 'nvarchar', 'The parcel number')
   ('Parcel', 'Parcel_Number_U', 'nvarchar', 'The unformatted parcel number')
   ('Parcel', 'Tax_Year', 'smallint', 'The tax year for the parcel')
   ('Parcel', 'District_Code', 'nvarchar', 'The district code of the parcel')
   ('Parcel', 'District', 'nvarchar', 'The district of the parcel')
   ('Parcel', 'Acres', 'decimal', 'The deeded acres')
   ('Parcel', 'Legal_Description', 'nvarchar', 'The legal description')
   ('Parcel', 'Deeded_Name', 'nvarchar', 'The name as listed on the deed')
   ('Parcel', 'Listed_Name', 'nvarchar', 'The shortened owner name')
   ('Parcel', 'Owner_Contact_Name', 'nvarchar', 'Owner Contact Name')
   ('Parcel', 'Owner_Contact_Address', 'nvarchar', 'Owner Contact Address')
   ('Parcel', 'Owner_Contact_City', 'nvarchar', 'Owner Contact City')
   ('Parcel', 'Owner_Contact_State', 'nvarchar', 'Owner Contact State')
   ('Parcel', 'Owner_Contact_ZipCode', 'nvarchar', 'Owner Contact ZIP Code')
   ('Parcel', 'Owner_Contact_Country', 'nvarchar', 'Owner Contact Country')
   ('Parcel', 'School_District', 'nvarchar', 'The school district of the parcel')
   ('Parcel', 'Subdivision', 'nvarchar', 'The subdivision of the parcel')
   ('Parcel', 'Map_Number', 'nvarchar', 'The map number')
   ('Parcel', 'Map_Link', 'nvarchar', 'A link to the map information provided by a third party. (If Available)')
   ('Parcel', 'Route_Number', 'nvarchar', 'The route number')
   ('Parcel', 'Taxpayer_Contact_Name', 'nvarchar', 'Taxpayer Contact Name')
   ('Parcel', 'Taxpayer_Contact_Address', 'nvarchar', 'Taxpayer Contact Address')
   ('Parcel', 'Taxpayer_Contact_City', 'nvarchar', 'Taxpayer Contact City')
   ('Parcel', 'Taxpayer_Contact_State', 'nvarchar', 'Taxpayer Contact State')
   ('Parcel', 'Taxpayer_Contact_ZipCode', 'nvarchar', 'Taxpayer Contact ZIP Code')
   ('Parcel', 'Taxpayer_Contact_Country', 'nvarchar', 'Taxpayer Contact Country')
   ('Parcel', 'Account_ID', 'int', 'Used by ISSG')

### Parcel Owner.xml
<Parcel_Owner> {}
<Parcel_Owner> {}
records scanned: 186089

### Parcel Transfer.xml
<Parcel_Transfer> {}
<Parcel_Transfer> {}
records scanned: 220852

### Parcel Location.xml
<Parcel_Location> {}
<Parcel_Location> {}
records scanned: 167263

### Parcel.xml
<Parcel> {}
<Parcel> {}
records scanned: 167241
