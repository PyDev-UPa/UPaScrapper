#! python

'''scrapFEV.py dowloands webpage https://www.upce.cz/en/foreign-education-verification
and creates a list containing countries and groups from the html code for further processing'''

import requests, bs4, openpyxl

fevUrl = 'https://www.upce.cz/uznavani-zahranicniho-vzdelavani'
groupKeys = {
'gA': ('Ano', 'Ano', 'Ano', ''),
'gB': ('Ne', 'Ano', 'Ano', ''),
'gC': ('Ne', 'Ne', 'Ano', ''),
'gD': ('Za podmínky*', 'Ano', 'Ano', '*Zahraniční škola potvrdí, že student je absolvent (emailem, zapečetěnou obálkou s transkriptem, ověření umožňují webové stránky školy'),
'gE_Germany': ('Za podmínky*', 'Ano', 'Ano', 'Řízení musí mít vždy kladný výsledek. *Zahraniční škola potvrdí, že student je absolvent (emailem, zapečetěnou obálkou s transkriptem, ověření umožňují webové stránky školy'),
'gE_Visegrad': ('Není třeba*', 'Není třeba*', 'Není třeba*', '*Uznání zahraničního vzdělání není vyžadováno'),
'gE_Canada': ('Za podmínky*', 'Ne', 'Ano', '*Zahraniční škola potvrdí, že student je absolvent (emailem, zapečetěnou obálkou s transkriptem, ověření umožňují webové stránky školy'),
'gE_Slovenia': ('Ano*', 'Ano*', 'Ano*', '*U středoškolských a magisterských procesů, není uznání zahraničního vzdělání vyžadováno.')
}

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

    if pair[0] in groupKeys.keys():
        worksheet.cell(row=curRow, column=3).value = groupKeys[pair[0]][0]
        worksheet.cell(row=curRow, column=4).value = groupKeys[pair[0]][1]
        worksheet.cell(row=curRow, column=5).value = groupKeys[pair[0]][2]
        worksheet.cell(row=curRow, column=6).value = groupKeys[pair[0]][3]

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
