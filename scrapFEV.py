#! python

'''scrapFEV.py dowloands webpage https://www.upce.cz/en/foreign-education-verification
and creates a list containing countries and groups from the html code for further processing'''

import requests, bs4, openpyxl

fevUrl = 'https://www.upce.cz/uznavani-zahranicniho-vzdelavani'

sourcePage = requests.get(fevUrl)
sourceSoup = bs4.BeautifulSoup(sourcePage.text, 'html.parser')
allLines = sourceSoup.select('option')
allLines = allLines[1:len(allLines)-7]

#TODO get rid of none country items in the list
def mineLine(line):
    '''mineLine takes a line from scrapped page in from of a string, locates positions of name of the country and group it belongs to and returns a tupple of group and country'''
    quotesPosition = []
    angleBracketPos = []

    for position, character in enumerate(line):
        if character == '"':
            quotesPosition.append(position)
        if character in ['<', '>']:
            angleBracketPos.append(position)
    groupPositionStart = quotesPosition[2] + 1
    groupPositionEnd = quotesPosition[3]
    countryPositionStart = angleBracketPos[1] + 1
    countryPositionEnd = angleBracketPos[2]
    groupAndCountry = (line[groupPositionStart:groupPositionEnd], line[countryPositionStart:countryPositionEnd])
    return groupAndCountry

def uniqueGroups(list):
    '''uniqueGroups returns unique groups found in tupples of group and country. It's only a check to see what groups are in the code'''
    uniques = []
    for item in list:
        if item[0] not in uniques:
            uniques.append(item[0])
    return uniques

statesAndGroups = []
for line in allLines:
    #creates tuppple of country and group it belongs to
    line = str(line)
    statesAndGroups.append(mineLine(line))

#set up the workbook and worksheet
workbook = openpyxl.Workbook()
worksheet = workbook.active
worksheet.title = 'Seznam Zemí'
worksheet['A1'] = 'Země'
for column in ['A', 'F']:
    worksheet.column_dimensions[column].width = 40
for column in ['B', 'C', 'D', 'E']:
    worksheet.column_dimensions[column].width = 15
worksheet['B1'] = 'Způsob ověření'
worksheet['C1'] = 'Ověřená kopie'
worksheet['D1'] = 'Apostila'
worksheet['E1'] = 'Superlegalizace'
worksheet['F1'] = 'Poznámky'

for pair in statesAndGroups:
    curRow = statesAndGroups.index(pair) + 2
    worksheet.cell(row=curRow, column=1).value = pair[1]
    worksheet.cell(row=curRow, column=2).value = pair[0]

    if pair[0] == "gA":
        worksheet.cell(row=curRow, column=3).value = 'Ano'
    else:
        worksheet.cell(row=curRow, column=3).value = 'Ne'

    if pair[0] in ['gA', 'gB']:
        worksheet.cell(row=curRow, column=4).value = 'Ano'
    else:
        worksheet.cell(row=curRow, column=4).value = 'Ne'

    if pair[0] in ['gA', 'gB', 'gC']:
        worksheet.cell(row=curRow, column=5).value = 'Ano'
    else:
        worksheet.cell(row=curRow, column=5).value = 'Ne'

    if pair[0] == 'gD':
        worksheet.cell(row=curRow, column=3).value = 'Za podmínky*'
        worksheet.cell(row=curRow, column=4).value = 'Ano'
        worksheet.cell(row=curRow, column=5).value = 'Ano'
        worksheet.cell(row=curRow, column=6).value = '*Zahraniční škola potvrdí, že student je absolvent (emailem, zapečetěnou obálkou s transkriptem, ověření umožňují webové stránky školy)'

    if pair[0] == 'gE_Germany':
        worksheet.cell(row=curRow, column=3).value = 'Za podmínky*'
        worksheet.cell(row=curRow, column=4).value = 'Ano'
        worksheet.cell(row=curRow, column=5).value = 'Ano'
        worksheet.cell(row=curRow, column=6).value = '*Zahraniční škola potvrdí, že student je absolvent (emailem, zapečetěnou obálkou s transkriptem, ověření umožňují webové stránky školy)'

    if pair[0] == 'gE_Visegrad':
        worksheet.cell(row=curRow, column=3).value = 'Není třeba*'
        worksheet.cell(row=curRow, column=4).value = 'Není třeba*'
        worksheet.cell(row=curRow, column=5).value = 'Není třeba*'
        worksheet.cell(row=curRow, column=6).value = '*Uznání zahraničního vzdělání není vyžadováno'

    if pair[0] == 'gE_Canada':
        worksheet.cell(row=curRow, column=3).value = 'Za podmínky*'
        worksheet.cell(row=curRow, column=4).value = 'Ne'
        worksheet.cell(row=curRow, column=5).value = 'Ano'
        worksheet.cell(row=curRow, column=6).value = '*Zahraniční škola potvrdí, že student je absolvent (emailem, zapečetěnou obálkou s transkriptem, ověření umožňují webové stránky školy)'

    if pair[0] == 'gE_Slovenia':
        worksheet.cell(row=curRow, column=3).value = 'Ano*'
        worksheet.cell(row=curRow, column=4).value = 'Ano*'
        worksheet.cell(row=curRow, column=5).value = 'Ano*'
        worksheet.cell(row=curRow, column=6).value = '*U středoškolských a magisterských procesů, není uznání zahraničního vzdělání vyžadováno.'


#TODO make this pretty
bottomRight = str(openpyxl.utils.get_column_letter(worksheet.max_column)) + str(worksheet.max_row)
topLeft = "A1"
tableRange = '{}:{}'.format(topLeft ,bottomRight)
tabulka = openpyxl.worksheet.table.Table(displayName="tabulka1", ref=tableRange)
stylTabulky = openpyxl.worksheet.table.TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                       showLastColumn=False, showRowStripes=True, showColumnStripes=False)
tabulka.tableStyleInfo = stylTabulky
worksheet.add_table(tabulka)

worksheet.freeze_panes = worksheet['A2']
worksheet.column_dimensions['B'].hidden = True
workbook.save('Uznávání zahraničního vzdělávání.xlsx')
